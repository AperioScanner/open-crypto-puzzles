#!/usr/bin/env python3
"""A11-EXP-132 — verify legacy bounding box covers the full *large sailboat*.

An implementation-quality question motivated by direct canonical-image viewing:
the legacy geometry file labels (44,320)-(359,599) the "large_sailboat".
The visibly drawn large triangular sail and its boat/hull extend substantially
below/right of that rectangle. Multiple older experiments imported the same
box (e.g. stages 36/94), potentially sampling only a fragment.

This stage preregisters two approximate manual polygons covering the obvious
large SAIL and its HULL, and measures how much of each polygon's actual
grayscale ink lies outside the legacy box. It does NOT alter previous results,
decode any symbol, generate any key, or infer author intent.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage132-large-sail-roi-coverage"
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
SHAPE=(1105,1600)
# Two fixed, conservative human-annotated silhouette regions, NOT masks
# derived by optimizing any match statistic. Approximate sail and hull only.
POLYGONS={
    "large_sail": [(242,398),(56,758),(512,760)],
    "large_hull": [(25,783),(525,778),(480,931),(75,939)]
}
# Blank upper-left sky is an independent local noise-density control.
SKY_CONTROL=(20,55,190,220)
THRESHOLDS=(110,170,210)
FORMATS=("original","jpeg85","jpeg70","down75_up")
SAIL_MISSING_MIN=.65
HULL_MISSING_MIN=.96
MIN_SAIL_INK_PIXELS=1500
MIN_HULL_INK_PIXELS=1500
MIN_SCENE_INK_DENSITY=.08
MAX_TRUNCATED_OUTSIDE_FRACTION=.025
MAX_TRUNCATED_HULL_PIXELS=20

def masks(geom):
    box=geom["large_sailboat"]
    old=np.zeros(SHAPE,np.uint8)
    x0,x1=int(box["x0"]),int(box["x1"])
    y0,y1=int(box["y0"]),int(box["y1"])
    old[y0:y1,x0:x1]=1
    polys={}
    for name,pts in POLYGONS.items():
        m=np.zeros(SHAPE,np.uint8)
        cv2.fillPoly(m,[np.asarray(pts,np.int32)],1)
        polys[name]=m>0
    return old>0,polys,[x0,y0,x1,y1]

def inspect(arr,old,regions,thr):
    dark=arr<thr
    obs={}
    for name,mask in regions.items():
        total=int(np.count_nonzero(dark & mask))
        missed=int(np.count_nonzero(dark & mask & ~old))
        coverage=(total-missed)/total if total else None
        density=total/int(mask.sum())
        obs[name]={
            "ink":total,"outside_legacy_ink":missed,
            "fraction_outside":round(missed/total,6) if total else None,
            "fraction_covered":round(coverage,6) if coverage is not None else None,
            "ink_density":round(density,6)
        }
    x0,y0,x1,y1=SKY_CONTROL
    obs["sky_background_density"]=round(float((arr[y0:y1,x0:x1]<thr).mean()),6)
    return obs

def synthetic(regions,old,truncate):
    img=np.full(SHAPE,255,np.uint8)
    for mask in regions.values():
        ink=np.zeros(SHAPE,np.uint8)
        ink[mask]=255
        # Thick stylized silhouettes model an indisputable large visible object.
        img[ink>0]=0
    if truncate:
        img[~old]=255
    return img

def assess_one(results,compare_bg):
    passed=[]
    for v in FORMATS:
        for thr in THRESHOLDS:
            result=results[v][str(thr)]
            sail=result["large_sail"]
            hull=result["large_hull"]
            ok=bool(
                sail["fraction_outside"] is not None
                and hull["fraction_outside"] is not None
                and sail["fraction_outside"]>=SAIL_MISSING_MIN
                and hull["fraction_outside"]>=HULL_MISSING_MIN
                and (not compare_bg or (
                    sail["ink"]>=MIN_SAIL_INK_PIXELS and
                    hull["ink"]>=MIN_HULL_INK_PIXELS and
                    sail["ink_density"]>=MIN_SCENE_INK_DENSITY and
                    hull["ink_density"]>=MIN_SCENE_INK_DENSITY and
                    sail["ink_density"]>4*result["sky_background_density"] and
                    hull["ink_density"]>4*result["sky_background_density"]
                ))
            )
            passed.append(ok)
    return all(passed),sum(passed),len(passed)

def run_set(img,old,regs):
    vv=variants(img)
    return {v:{str(t):inspect(vv[v],old,regs,t) for t in THRESHOLDS}
            for v in FORMATS}

def run_controls(old,regs):
    pos=run_set(synthetic(regs,old,False),old,regs)
    neg=run_set(synthetic(regs,old,True),old,regs)
    pos_ok,pos_n,pos_total=assess_one(pos,False)
    neg_checks=[]
    for v in FORMATS:
        for thr in THRESHOLDS:
            obs=neg[v][str(thr)]
            sail=obs["large_sail"]
            hull=obs["large_hull"]
            # Synthetic image intentionally cut at the historical rectangle.
            neg_checks.append(
                sail["fraction_outside"] is not None
                and sail["fraction_outside"]<=MAX_TRUNCATED_OUTSIDE_FRACTION
                and hull["ink"]<=MAX_TRUNCATED_HULL_PIXELS
            )
    return {
        "passed":bool(pos_ok and all(neg_checks)),
        "cases":pos_total+len(neg_checks),
        "positive_full_shape_passes":pos_n,
        "negative_truncated_shape_passes":sum(neg_checks),
        "synthetic_full_example":pos["original"]["170"],
        "synthetic_truncated_example":neg["original"]["170"]
    }

def save_overlay(gray,old,regs,box):
    canvas=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    overlay=canvas.copy()
    colors={"large_sail":(250,178,20),"large_hull":(70,210,110)}
    for name,pts in POLYGONS.items():
        cv2.polylines(overlay,[np.asarray(pts,np.int32)],True,colors[name],3)
    x0,y0,x1,y1=box
    cv2.rectangle(overlay,(x0,y0),(x1,y1),(10,10,240),3)
    cv2.putText(overlay,"LEGACY bbox",(x0,max(25,y0-12)),
                cv2.FONT_HERSHEY_SIMPLEX,.9,(10,10,240),2)
    cv2.putText(overlay,"fixed sail polygon",(540,690),
                cv2.FONT_HERSHEY_SIMPLEX,.8,colors["large_sail"],2)
    cv2.putText(overlay,"fixed hull polygon",(540,750),
                cv2.FONT_HERSHEY_SIMPLEX,.8,colors["large_hull"],2)
    # Fixed display only; no image search or OCR.
    vis=cv2.addWeighted(overlay,.87,canvas,.13,0)
    cv2.imwrite(str(OUT/"large-sail-legacy-bbox-overlay.png"),vis)

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=EXPECTED_SHA:
        raise SystemExit("Canonical image SHA256 mismatch")
    gray=np.array(Image.open(SOURCE).convert("L"))
    if gray.shape!=SHAPE:
        raise SystemExit("Wrong image dimensions")
    geom=json.loads(GEOM.read_text())
    old,regs,box=masks(geom)
    controls=run_controls(old,regs)
    real=run_set(gray,old,regs)
    real_ok,real_passes,real_n=assess_one(real,True)
    decision=(
        "CONTROL_FAILURE" if not controls["passed"] else
        "LEGACY_LARGE_SAILBOAT_BBOX_INCOMPLETE" if real_ok else
        "INSUFFICIENT_PROOF_OF_LEGACY_BBOX_INCOMPLETENESS"
    )
    save_overlay(gray,old,regs,box)
    report={
        "experiment_id":"A11-EXP-132",
        "question":"Does the legacy large_sailboat rectangular ROI omit most ink from its sail and hull?",
        "evidence":"Visual source review shows the legacy geometry bbox seems to end halfway down/right of the large ship; prior analysis repeatedly used that box.",
        "scope":"manual fixed large sail and hull silhouettes + old data/geometry.json ROI, 3 thresholds, original/JPEG85/JPEG70/resampling",
        "canonical_sha256":digest,"legacy_box":box,
        "precommitted_polygon_vertices":POLYGONS,
        "thresholds":THRESHOLDS,
        "min_fraction_outside":{"sail":SAIL_MISSING_MIN,"hull":HULL_MISSING_MIN},
        "min_ink_pixels":{"sail":MIN_SAIL_INK_PIXELS,"hull":MIN_HULL_INK_PIXELS},
        "controls":controls,
        "real_pass_cases":real_passes,
        "real_total_cases":real_n,
        "real_measurements":real,
        "decision":decision,
        "scope_guard":"A positive flags a potentially truncated legacy measurement ROI; it does NOT retroactively refute every negative or establish a new encoding.",
        "safety_guard":"No private keys, mnemonic words, wallet or external site access."
    }
    (OUT/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    md=[
        "# Stage 132 — audit legacy large sailboat bounding-box coverage","",
        f"- Canonical SHA verified: **{digest==EXPECTED_SHA}**",
        f"- Legacy bounding box: **{box}**",
        f"- Synthetic full vs truncated controls: **{controls['passed']}** ({controls['positive_full_shape_passes']} + {controls['negative_truncated_shape_passes']}/{controls['cases']})",
        f"- Real threshold×reencoding cases meeting fixed incomplete-ROI gate: **{real_passes}/{real_n}**",
        f"- Decision: **{decision}**","",
        "| fixed region | original source ink outside legacy bbox (thr=170) | density |",
        "|---|---:|---:|",
    ]
    for name in ("large_sail","large_hull"):
        row=real["original"]["170"][name]
        md.append(f"| {name} | {row['fraction_outside']:.3f} | {row['ink_density']:.3f} |")
    md+=["","## Interpretation",""]
    if not controls["passed"]:
        md.append("Control failure. Repair this SAME Stage132 before interpreting real data.")
    elif real_ok:
        md.append("The old ROI excludes most visible pencil ink in fixed large-sail/hull polygons. Review earlier ROI-dependent measurements with accurate bounds; this is an image-geometry defect, NOT a discovered code.")
    else:
        md.append("Predeclared real coverage tests did not demonstrate severe undercoverage. Keep earlier bounds' limitations explicitly documented; do not force an interpretation.")
    md+=["","Source overlay: large-sail-legacy-bbox-overlay.png.",
         "No keys or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"stage":132,"controls":controls["passed"],
        "real_pass":real_passes,"real_total":real_n,"decision":decision}))

if __name__=="__main__":
    main()
