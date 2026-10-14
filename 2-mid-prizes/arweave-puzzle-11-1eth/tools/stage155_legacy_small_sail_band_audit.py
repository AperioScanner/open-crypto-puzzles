#!/usr/bin/env python3
"""A11-EXP-155 — audit obsolete small-sails y band vs verified source masks.

A purely non-secret geometry/provenance test. The historical file describes
small_sails_band_y=[360,480], whereas the true five sail polygons were corrected
in Stages 112, 151 and 153. Stage132 audited a different incorrect large-sail
bbox. Gates and fixtures here are preregistered in analysis/STAGE_QUEUE.md.
This test does not derive any symbol, numeric code, private key, address,
BIP39 phrase or candidate, and does not reinterpret past test results.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
PNG = ROOT / "clues" / "arweave-puzzle-11.png"
GEOMETRY = ROOT / "data" / "geometry.json"
OUT = ROOT / "analysis" / "runs" / "stage155-small-sail-band-audit"
OUT.mkdir(parents=True,exist_ok=True)
SHA = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
SITES={k:v for k,v in TRIANGLES.items() if k.startswith("sail")}
FORMATS=("original","jpeg85","jpeg70","down75_up")
THRESHOLDS=(110,170,210)
MIN_SOURCE_DARK=200
MATERIAL_OMISSION=0.25
MIN_MATERIAL_SAILS=3
THRESHOLD_CONTROL=170
FULL_CONTROL_TOLERANCE=0.035
BAND_CONTROL_MAX_OMISSION=0.03
CONTROL_INSIDE_MARGIN=(368,472)
MASK_EROSION=np.ones((5,5),np.uint8)

def source_masks(shape,band):
    ylo,yhi=band
    out={}
    for name,triangle in SITES.items():
        mask=np.zeros(shape,np.uint8)
        cv2.fillPoly(mask,[np.array(triangle,np.int32)],255)
        mask=cv2.erode(mask,MASK_EROSION,iterations=1)>0
        area=int(mask.sum())
        excluded=int(mask[:ylo,:].sum()+mask[yhi:,:].sum())
        inside=area-excluded
        out[name]={"mask":mask,"area":area,"omitted_area":excluded,
                   "inside_area":inside,"geom_omission":excluded/area}
    return out

def summarize_ink(frame,site_mask,band,threshold):
    ylo,yhi=band
    ink=site_mask & (frame<threshold)
    n=int(np.count_nonzero(ink))
    outside=int(np.count_nonzero(ink[:ylo,:])+np.count_nonzero(ink[yhi:,:]))
    return {"ink_px":n,"outside_band_ink_px":outside,
            "inside_band_ink_px":n-outside,
            "omitted_ink_fraction":round(float(outside/n),6) if n else None}

def synthetic_image(kind):
    canvas=np.full((1105,1600),255,np.uint8)
    for triangle in SITES.values():
        cv2.fillPoly(canvas,[np.array(triangle,np.int32)],0)
    if kind=="band_ink_only":
        lo,hi=CONTROL_INSIDE_MARGIN
        canvas[:lo,:]=255
        canvas[hi:,:]=255
    elif kind!="full_triangles":
        raise ValueError(kind)
    return canvas

def synthetic_controls(masks,band):
    rows=[]
    ok=0
    for kind in ("full_triangles","band_ink_only"):
        scenes=variants(synthetic_image(kind))
        for fmt in FORMATS:
            for name,entry in masks.items():
                measure=summarize_ink(scenes[fmt],entry["mask"],band,THRESHOLD_CONTROL)
                m=measure["omitted_ink_fraction"]
                if kind=="full_triangles":
                    passed=bool(measure["ink_px"]>20 and m is not None
                        and abs(m-entry["geom_omission"])<=FULL_CONTROL_TOLERANCE)
                else:
                    passed=bool(measure["ink_px"]>20 and m is not None
                                and m<=BAND_CONTROL_MAX_OMISSION)
                ok+=int(passed)
                rows.append({"kind":kind,"format":fmt,"site":name,"passed":passed,
                    "ratio":m,"expected_geometry":round(entry["geom_omission"],6),
                    "dark_pixels":measure["ink_px"]})
    return {"pass":ok==len(rows)==40,"passed":ok,"cases":len(rows),
            "failures":[r for r in rows if not r["passed"]],
            "full_results":rows}

def find_script_references():
    roots=list((ROOT/"tools").glob("*.py"))+list((REPO_ROOT/".github"/"workflows").glob("*.yml"))
    direct=[]; broad=[]
    for p in roots:
        if p.name=="stage155_legacy_small_sail_band_audit.py":
            continue
        try:
            content=p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for n,txt in enumerate(content.splitlines(),1):
            record={"path":str(p.relative_to(REPO_ROOT)),
                    "line":n,"text":txt.strip()[:200]}
            if "small_sails_band_y" in txt:
                direct.append(record)
            elif "geometry.json" in txt:
                broad.append(record)
    return {"total_scripts_scanned":len(roots)-1,
            "direct_field_references":direct,
            "generic_geometry_file_references":broad,
            "meaning":"Lexical matches only: a match does not prove runtime use, and absence of exact field literal does not rule out indirect dynamic access."}

def create_visual(gray,band):
    ylo,yhi=band
    x0,y0,x1,y1=935,333,1585,564
    crop=gray[y0:y1,x0:x1]
    raw=cv2.cvtColor(crop,cv2.COLOR_GRAY2BGR)
    marks=raw.copy()
    for name,triangle in SITES.items():
        pts=np.array([[x-x0,y-y0] for x,y in triangle],np.int32)
        cv2.polylines(marks,[pts],True,(0,70,245),2,cv2.LINE_AA)
        v=triangle[0]
        cv2.putText(marks,name,(v[0]-x0-10,v[1]-y0-17),
                cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1,cv2.LINE_AA)
    for y in (ylo,yhi):
        cv2.line(marks,(0,y-y0),(x1-x0,y-y0),(20,185,20),1)
    h,w=raw.shape[:2]
    combined=np.full((h+35,w*2,3),255,np.uint8)
    combined[35:,:w]=raw
    combined[35:,w:]=marks
    cv2.putText(combined,"CANONICAL CROP (UNMODIFIED)",(8,23),
            cv2.FONT_HERSHEY_SIMPLEX,.52,(0,0,0),1,cv2.LINE_AA)
    cv2.putText(combined,"ANNOTATIONS ONLY: POLYGONS + BAND",(w+8,23),
            cv2.FONT_HERSHEY_SIMPLEX,.49,(0,0,0),1,cv2.LINE_AA)
    if not cv2.imwrite(str(OUT/"five-sails-versus-legacy-band.png"),combined):
        raise RuntimeError("Could not write contact image")

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Canonical image mismatch")
    gray=np.asarray(Image.open(PNG).convert("L"))
    if gray.shape!=(1105,1600):raise RuntimeError("Image dimensions changed")
    old=json.loads(GEOMETRY.read_text(encoding="utf-8"))
    band=list(old["small_sails_band_y"])
    if band!=[360,480]: raise RuntimeError("Legacy band changed — audit invalid")
    masks=source_masks(gray.shape,band)
    controls=synthetic_controls(masks,band)
    images=variants(gray)
    measurements={
      fmt:{
        str(t):{
          name:summarize_ink(images[fmt],entry["mask"],band,t)
          for name,entry in masks.items()
        } for t in THRESHOLDS
      } for fmt in FORMATS
    }
    has_source=all(
        measurements[fmt][str(t)][site]["ink_px"]>=MIN_SOURCE_DARK
        for fmt in FORMATS for t in THRESHOLDS for site in SITES
    )
    stable_material={
      site:all(
          measurements[fmt][str(t)][site]["omitted_ink_fraction"] is not None
          and measurements[fmt][str(t)][site]["omitted_ink_fraction"]>=MATERIAL_OMISSION
          for fmt in FORMATS for t in THRESHOLDS
      ) for site in SITES
    }
    known=sum(stable_material.values())
    decision=(
      "CONTROL_FAILURE" if not controls["pass"] else
      "INSUFFICIENT_REAL_SAIL_INK_SAMPLE" if not has_source else
      "LEGACY_SMALL_SAIL_BAND_MATERIALLY_TRUNCATES_TRUE_SAILS"
        if known>=MIN_MATERIAL_SAILS else
      "LEGACY_BAND_MATERIAL_TRUNCATION_NOT_ESTABLISHED"
    )
    static_refs=find_script_references()
    result={
      "experiment_id":"A11-EXP-155",
      "source_sha256":digest,
      "hypothesis":"An obsolete [360,480) y-only metadata band clips a material amount of the actual drawn five small sail panels.",
      "legacy_file":"data/geometry.json",
      "legacy_small_sails_band_y":band,
      "immutable_reference":"Stage153 five genuine sail polygons",
      "reference_triangles":SITES,
      "source_polygon_masks":{name:{
         "area":m["area"],"area_outside_legacy_band":m["omitted_area"],
         "geometric_missing_fraction":round(m["geom_omission"],6)}
        for name,m in masks.items()},
      "fixed_gates":{
         "dark_thresholds":THRESHOLDS,"formats":FORMATS,
         "interior_mask_erosion":"5x5 once",
         "min_real_sail_ink_px":MIN_SOURCE_DARK,
         "material_ink_omission_fraction":MATERIAL_OMISSION,
         "min_sails_with_material_loss_all_12_settings":MIN_MATERIAL_SAILS,
         "synthetic_controls":"filled full triangles expected geometric fraction +/-0.035; inside-band cropped triangles outside ink <=0.03, all 40 pass"
      },
      "synthetic_controls":controls,"source_ink_sufficient":has_source,
      "actual_source_by_format_threshold":measurements,
      "material_ink_loss_stable_by_sail":stable_material,
      "materially_truncated_sails":known,
      "static_code_provenance":static_refs,
      "decision":decision,
      "limits":"A legacy file's poor geometric coverage is not proof any historical workflow used the field. It does not invalidate past results without direct code/report linkage; it is not evidence of a code or hidden key.",
      "safety":"Image geometry and repository static metadata only. No key generation, BIP39, addresses, wallets, social or off-source research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    create_visual(gray,band)
    report=[
      "# Stage155 — old small-sail band source coverage and code provenance","",
      f"- Canonical PNG SHA verified: **{digest==SHA}**",
      f"- Literal obsolete small-sails y band: **{band}**",
      f"- Synthetic controls: **{controls['passed']}/{controls['cases']}**.",
      f"- Original + lossy variants: 3 thresholds x 4 renderings = **12** measured conditions per sail.",
      f"- All real source sails have >=200 dark ink px in every setting: **{has_source}**.",
      f"- Material ink omission (>=25% excluded in ALL 12 settings): **{known}/5**.",
      f"- Decision: **{decision}**.","",
      "| True sail | Fixed apex/base y | Geometric area excluded | Ink excluded (original, threshold 110) | Ink excluded (original, threshold 170) | Ink excluded (original, threshold 210) | Stable across 12 |",
      "|---|---|---:|---:|---:|---:|---|"
    ]
    for name,tri in SITES.items():
        y=[int(x[1]) for x in tri]
        vals=[measurements["original"][str(t)][name]["omitted_ink_fraction"] for t in THRESHOLDS]
        report.append(
            f"| {name} | {min(y)}–{max(y)} | {masks[name]['geom_omission']:.1%} | "
            + " | ".join("N/A" if z is None else f"{z:.1%}" for z in vals)
            + f" | {stable_material[name]} |")
    report+=["","## Static dependency search (read-only)","",
        f"- Tool/workflow files scanned: **{static_refs['total_scripts_scanned']}**.",
        f"- Exact small_sails_band_y field references outside this audit script: **{len(static_refs['direct_field_references'])}**.",
        f"- Generic geometry.json references outside this audit script: **{len(static_refs['generic_geometry_file_references'])}**.",
        "- These are TEXT matches only; do not infer that a recorded workflow used the obsolete band.",
        ""]
    for label,key in (
        ("Exact field usages","direct_field_references"),
        ("Generic file usages (investigation only)","generic_geometry_file_references")):
        report.append(f"### {label}")
        entries=static_refs[key]
        if not entries:
            report.append("- None found within scanned tool/workflow scope.")
        for x in entries[:25]:
            report.append(f"- {x['path']}:{x['line']}: {x['text']}")
        report.append("")
    report+=["## Interpretation limits","",
       "The five sail polygons were fixed by past verified source work. A confirmed stale geometric description should be kept as historical provenance and not silently overwritten.",
       "Four of five known sail bases are BELOW the old band; the Stage155 dark-ink measurement independently quantifies how much of the original pencil drawing was omitted.",
       "The old small sail widths and wrong source object from Stage112 are separate earlier corrections; Stage132's large-sail bbox defect is also separate.",
       "No statement about secret encoding, wallet access or solver progress is justified by this audit.",
       "Source crop comparison: five-sails-versus-legacy-band.png (raw crop at left, guides at right).",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":155,"sha_ok":True,"controls":str(controls["passed"])+"/"+str(controls["cases"]),
          "material_sails":known,"direct_field_references":len(static_refs["direct_field_references"]),
          "decision":decision}))
if __name__=="__main__":main()
