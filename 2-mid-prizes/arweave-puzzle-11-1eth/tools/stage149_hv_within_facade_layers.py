#!/usr/bin/env python3
"""A11-EXP-149 — are original building H/V strokes uniform through facade height?

Stage148 ruled out strong ordinary BUILDING SHAPE prediction for the robust
12-building H/V label vector (FWER exact p=.299), but H/V labels had always
been measured over each whole facade. The original sketch often has visible
shading LAYERS. An H/V label is less like 1 intrinsic bit per building if its
upper/middle/lower layers point different ways.

This experiment is NOT stroke counts (Stage121), overall stability (Stage10),
area/roof-size predictors (Stage148), cross-facade reflection (Stage139) or
invented 0x321/key decoding. It measures original vs JPEG85/JPEG70/0.75
resampled image in THREE strictly registered disjoint facade-height bands,
with two independent local H/V estimators (Sobel and grayscale shift corr).
Four synthetic positive/negative building patterns and 576 tests calibrate
this test before interpreting the real source.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from stage112_corrected_sail_width_progression import variants
from stage148_hv_building_aspect_confounds import bitmap_labels,EXPECTED,SHA

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOMETRY=ROOT/"data"/"geometry.json"
STAGE148=ROOT/"analysis"/"runs"/"stage148-hv-building-shape-confound"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage149-hv-facade-layers"
OUT.mkdir(parents=True,exist_ok=True)

FORMATS=("original","jpeg85","jpeg70","down75_up")
ZONES=("upper","middle","lower")
FIXTURES=("all_horizontal","all_vertical","mixed_HVH","blank")
FACADE_X_MARGIN=.12
FACADE_TOP_MARGIN=.14
FACADE_BOTTOM_MARGIN=.10
LOCAL_Y_GUARD=3
STROKE_SPACING=8
MAX_SOURCE_Y=1105
MIN_CROP_HEIGHT=10
MIN_CROP_WIDTH=15
MIN_DARK_FRACTION=.065
SOBEL_GATE=.14
CORR_GATE=.10
LAG_PIXELS=4
MIN_REPLICATED_REGIONS=30
MIN_FULL_LABEL_MATCH_BUILDINGS=10
MIXED_SOURCE_BUILDING_GATE=4

def boxes(buildings):
    """Source coordinates only; equal proportions within each facade."""
    out={}
    for b in buildings:
        bid=int(b["id"])
        x0,x1,y0,y1=map(int,(b["x0"],b["x1"],b["roof_y"],b["bottom_y"]))
        w=x1-x0;h=y1-y0
        inner=max(5,int(round(w*FACADE_X_MARGIN)))
        start=y0+int(round(FACADE_TOP_MARGIN*h))
        stop=y1-int(round(FACADE_BOTTOM_MARGIN*h))
        edges=np.linspace(start,stop,4).round().astype(int)
        for i,zone in enumerate(ZONES):
            xa=x0+inner;xb=x1-inner
            ya=int(edges[i])+LOCAL_Y_GUARD
            yb=int(edges[i+1])-LOCAL_Y_GUARD
            if yb-ya<MIN_CROP_HEIGHT or xb-xa<MIN_CROP_WIDTH:
                raise RuntimeError(f"Insufficient fixed facade zone {bid}:{zone}")
            out[(bid,zone)]=(xa,ya,xb,yb)
    if len(out)!=36:raise RuntimeError("Need 12×3 facade zones")
    return out

def pearson(x,y):
    a=x.astype(np.float64).ravel()
    b=y.astype(np.float64).ravel()
    a-=a.mean();b-=b.mean()
    denom=float(np.linalg.norm(a)*np.linalg.norm(b))
    return float(a.dot(b)/denom) if denom>1e-9 else 0.

def estimate(gray,bbox):
    x0,y0,x1,y1=bbox
    patch=gray[y0:y1,x0:x1]
    if patch.size==0:raise RuntimeError("Empty facade crop")
    dark=float(np.mean(patch<175))
    blur=cv2.GaussianBlur(patch,(3,3),0)
    gx=cv2.Sobel(blur,cv2.CV_32F,1,0,ksize=3)
    gy=cv2.Sobel(blur,cv2.CV_32F,0,1,ksize=3)
    ex=float(np.mean(np.abs(gx)));ey=float(np.mean(np.abs(gy)))
    score=float((ex-ey)/(ex+ey+1e-9))
    f=(255-patch.astype(np.float32))/255.0
    lag=LAG_PIXELS
    cx=pearson(f[:,:-lag],f[:,lag:])
    cy=pearson(f[:-lag,:],f[lag:,:])
    corr_score=(cy-cx)/(abs(cx)+abs(cy)+1e-9)
    adequate=dark>=MIN_DARK_FRACTION and min(patch.shape)>=MIN_CROP_HEIGHT
    if adequate and score>=SOBEL_GATE and corr_score>=CORR_GATE:
        label="V"
    elif adequate and score<=-SOBEL_GATE and corr_score<=-CORR_GATE:
        label="H"
    else:
        label=None
    return {"class":label,
            "dark_fraction":round(dark,6),
            "adequate":adequate,
            "sobel_score":round(score,6),
            "lag_orientation_score":round(float(corr_score),6)}

def simulate(buildings,pattern):
    result=np.full((1105,1600),255,np.uint8)
    for (bid,zone),(x0,y0,x1,y1) in boxes(buildings).items():
        target=(
            "H" if pattern=="all_horizontal" else
            "V" if pattern=="all_vertical" else
            {"upper":"H","middle":"V","lower":"H"}[zone]
            if pattern=="mixed_HVH" else
            None
        )
        if target=="H":
            for y in range(y0+2,y1-2,STROKE_SPACING):
                cv2.line(result,(x0+2,y),(x1-3,y),0,2,cv2.LINE_AA)
        elif target=="V":
            for x in range(x0+3,x1-3,STROKE_SPACING):
                cv2.line(result,(x,y0+1),(x,y1-2),0,2,cv2.LINE_AA)
    return result

def expected_fixture_label(name,zone):
    if name=="all_horizontal":return "H"
    if name=="all_vertical":return "V"
    if name=="mixed_HVH":return "V" if zone=="middle" else "H"
    return None

def check_controls(buildings):
    box=boxes(buildings)
    summaries={}
    passed=0
    total=0
    failures=[]
    for name in FIXTURES:
        observations={}
        for fmt,im in variants(simulate(buildings,name)).items():
            if fmt not in FORMATS:continue
            matches=0
            for (bid,zone),coords in box.items():
                v=estimate(im,coords)
                predicted=expected_fixture_label(name,zone)
                valid=(v["class"]==predicted)
                matches+=int(valid)
                total+=1
                passed+=int(valid)
                if not valid and len(failures)<25:
                    failures.append({
                        "fixture":name,"format":fmt,
                        "building":bid,"zone":zone,
                        "expected":predicted,
                        "got":v["class"],
                        "sobel":v["sobel_score"],
                        "corr":v["lag_orientation_score"],
                        "ink":v["dark_fraction"]
                    })
            observations[fmt]=matches
        summaries[name]=observations
    return {"pass":passed==total and total==4*4*36,
            "passed_cases":passed,"cases":total,
            "fixture_scores":summaries,
            "failures":failures}

def actual_facade_test(gray,buildings):
    registered=boxes(buildings)
    outputs={}
    frames=variants(gray)
    for fmt in FORMATS:
        im=frames[fmt]
        readings={}
        for (bid,zone),coords in registered.items():
            readings.setdefault(str(bid),{})[zone]=estimate(im,coords)
        outputs[fmt]=readings
    per_building={}
    fully_replicated=0
    matches_full=0
    mixed=0
    for bid in range(1,13):
        zones={}
        for zone in ZONES:
            outcomes=[outputs[fmt][str(bid)][zone]["class"] for fmt in FORMATS]
            stable=outcomes[0] if outcomes[0] is not None and len(set(outcomes))==1 else None
            zones[zone]=stable
            fully_replicated+=int(stable is not None)
        stable_values=[v for v in zones.values() if v is not None]
        full=EXPECTED[bid-1]
        full_match=len(stable_values)==3 and all(x==full for x in stable_values)
        is_mixed=len(set(stable_values))>=2 and len(stable_values)>=2
        matches_full+=int(full_match)
        mixed+=int(is_mixed)
        per_building[str(bid)]={
            "whole_facade_stage10":full,
            "upper_middle_lower":zones,
            "all_3_stable_and_same_as_original":full_match,
            "contains_two_stable_opposite_directions":is_mixed
        }
    return outputs,per_building,fully_replicated,matches_full,mixed,registered

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Canonical image SHA changed")
    raw=np.asarray(Image.open(SOURCE).convert("L"))
    if raw.shape!=(1105,1600):raise RuntimeError("Wrong source dimensions")
    prior=json.loads(STAGE148.read_text())
    if not(prior["controls"]["pass"]
           and prior["source_replicated_in_four_formats"]
           and prior["sha256"]==digest):
        raise RuntimeError("Stage148 source chain mismatch")
    geom=json.loads(GEOMETRY.read_text())
    buildings=geom["buildings"]
    ctl=check_controls(buildings)
    all_data,per_building,coverage,full_matches,mixed,registered=actual_facade_test(raw,buildings)
    source_labels=all(bitmap_labels(frame,buildings)[0]==EXPECTED
                      for fmt,frame in variants(raw).items() if fmt in FORMATS)
    if coverage<MIN_REPLICATED_REGIONS:
        outcome="INSUFFICIENT_REAL_FACADE_ZONE_COVERAGE"
    elif mixed>=MIXED_SOURCE_BUILDING_GATE:
        outcome="MULTIPLE_FACADE_HATCH_DIRECTIONS_REPLICATED"
    elif full_matches>=MIN_FULL_LABEL_MATCH_BUILDINGS:
        outcome="BINARY_HV_DIRECTION_HOMOGENEOUS_THROUGH_FACADES"
    else:
        outcome="FACADES_PARTIALLY_MIXED_OR_SOURCE_AMBIGUOUS"
    decision=("CONTROL_FAILURE" if not ctl["pass"] else
              "WHOLE_FACADE_HV_SOURCE_DRIFT" if not source_labels else
              outcome)
    result={
        "experiment_id":"A11-EXP-149",
        "hypothesis":"the stable H/V label of each whole source building might mask internally mixed hatch angles in upper/middle/lower subregions, challenging a simple one-symbol-per-building visual reading",
        "why_new":"Stage10/31 measured aggregate per-building H/V; Stage121 counted exact hatch LINES; Stage148 tested building DIMENSIONS, but no prior test independently classified three disjoint height layers in each source facade.",
        "scope":"12 fixed native facade boxes x three disjoint interior vertical tiers, original/JPEG85/JPEG70/down75_up, Sobel and directional pixel-lag independent estimators",
        "sha256":digest,"original_labels":EXPECTED,
        "fixed_gates":{
           "x_inner_fraction":FACADE_X_MARGIN,
           "source_top_fraction":FACADE_TOP_MARGIN,
           "source_bottom_fraction":FACADE_BOTTOM_MARGIN,
           "y_inner_zone_guard_px":LOCAL_Y_GUARD,
           "min_source_dark_fraction":MIN_DARK_FRACTION,
           "sobel_orientation_gate":SOBEL_GATE,
           "pixel_lag_orientation_gate":CORR_GATE,
           "pixels_per_lag":LAG_PIXELS,
           "min_covered_facade_zones":MIN_REPLICATED_REGIONS,
           "mixed_buildings_gate":MIXED_SOURCE_BUILDING_GATE,
           "whole_hv_matching_buildings_gate":MIN_FULL_LABEL_MATCH_BUILDINGS},
        "controls":ctl,
        "whole_source_HV_reproduction_pass":source_labels,
        "fully_replicated_zone_count":coverage,
        "all_three_zones_same_as_whole_HV_count":full_matches,
        "buildings_with_stably_opposed_zone_directions":mixed,
        "building_summary":per_building,
        "by_format":all_data,
        "registered_boxes":{str(k[0])+":"+k[1]:list(v) for k,v in registered.items()},
        "decision":decision,
        "scope_guard":"Tests only two angle estimators in 3 facades zones; not an exact stroke-count or 0x321 decoding. Uniform H/V does not imply author intended a binary key, mixed zones do not falsify all possible visual symbols. Multiple prior hypotheses mean any surprise is exploratory.",
        "safety":"Only pixels and public building geometry. No private keys, wallet, addresses, mnemonics, BIP39, derived key or external source."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
        "# Stage149 — are H/V facade strokes genuinely uniform from top to bottom?","",
        f"- Canonical image SHA verified: **{digest==SHA}**",
        f"- Horizontal/vertical/mixed/blank synthetic 3-band controls: **{ctl['passed_cases']}/{ctl['cases']}**",
        f"- Whole-facade original H/V labels confirmed: **{source_labels}**",
        f"- Independent zone direction stable across four formats: **{coverage}/36**",
        f"- 3/3 zones agree with original building H/V: **{full_matches}/12**",
        f"- Buildings with at least two opposed stable zones: **{mixed}/12**",
        f"- Decision: **{decision}**","",
        "| building | original | upper | middle | lower |",
        "|---|:---:|:---:|:---:|:---:|"
    ]
    for bid in range(1,13):
        z=per_building[str(bid)]
        q=z["upper_middle_lower"]
        lines.append(f"| {bid} | {z['whole_facade_stage10']} | {q['upper'] or '?'} | {q['middle'] or '?'} | {q['lower'] or '?'} |")
    lines+=["","## Interpretation",""]
    if not ctl["pass"]:
        lines.append("Positive/negative controls failed. Repair Stage149; do not interpret source.")
    elif not source_labels or coverage<MIN_REPLICATED_REGIONS:
        lines.append("Insufficient reliable source and/or subregion extraction; no source-level H/V inference.")
    elif mixed>=MIXED_SOURCE_BUILDING_GATE:
        lines.append("Several facades have stably opposed orientations within their height, complicating a simplistic 12-bit reading; not proof of absent semantic symbols.")
    elif full_matches>=MIN_FULL_LABEL_MATCH_BUILDINGS:
        lines.append("The 12 H/V labels are locally coherent in most buildings under both independent estimators; this is still not proof of a deliberately encoded number.")
    else:
        lines.append("Some facades lack exact 3-band uniformity, but no robust widespread two-direction mixture; treat each whole-facade H/V label as an aggregate observation only.")
    lines+=["","No secret material or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":149,"controls":ctl["pass"],
        "reproduced_HV":source_labels,"valid_zones":coverage,
        "fully_uniform":full_matches,"mixed_buildings":mixed,
        "decision":decision}))

if __name__=="__main__":
    main()
