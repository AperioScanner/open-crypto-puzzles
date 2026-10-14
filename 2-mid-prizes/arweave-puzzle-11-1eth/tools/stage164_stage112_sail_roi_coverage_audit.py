#!/usr/bin/env python3
"""A11-EXP-164 — audit coverage of *actual* true sails in Stage112's y345:500 boxes.

Stage112 correctly re-identified 5 sail centers, but its width input strips
terminate at y500. True source-corrected Stage153 sail bases reach y546,
532 and514 for the first three. This audit does not infer true widths, code,
symbols, keys, phrases or wallet access. The experiment was preregistered.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import (
    variants,boxes_from_centers,MASK_THRESHOLDS,SEARCH)
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OLD_CODE=ROOT/"tools"/"stage112_corrected_sail_width_progression.py"
STAGE112=ROOT/"analysis"/"runs"/"stage112-corrected-sail-width-progression"/"result.json"
STAGE163=ROOT/"analysis"/"runs"/"stage163-superbatch-source-provenance"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage164-stage112-sail-coverage"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
SITES={name:pts for name,pts in TRIANGLES.items() if name.startswith("sail")}
THRESHOLDS=(120,150,180)
OMISSION_THRESHOLD=0.20
MIN_MATERIAL_SAILS=3
SOURCE_PIXELS_MIN=200
INNER_NEGATIVE_MARGIN=8
EROSION=np.ones((5,5),np.uint8)

def masks(shape):
    result={}
    for name,points in SITES.items():
        raw=np.zeros(shape,np.uint8)
        cv2.fillPoly(raw,[np.asarray(points,np.int32)],255)
        result[name]=cv2.erode(raw,EROSION,iterations=1)>0
    return result

def boxmask(shape,box,inset=0):
    x0,y0,x1,y1=box
    m=np.zeros(shape,np.bool_)
    if y1-y0>2*inset and x1-x0>2*inset:
        m[y0+inset:y1-inset,x0+inset:x1-inset]=True
    return m

def geometry(mask,box):
    inside=boxmask(mask.shape,box)
    total=int(mask.sum())
    outside=int(np.count_nonzero(mask & (~inside)))
    return {"polygon_area":total,"omitted_area":outside,
            "omitted_area_fraction":outside/total if total else None}

def ink_measure(gray,polygon,box,threshold):
    dark=(gray<threshold)&polygon
    within=boxmask(gray.shape,box)
    total=int(dark.sum())
    lost=int(np.count_nonzero(dark&~within))
    return {"dark_ink":total,"outside_box_ink":lost,
            "fraction_lost":round(float(lost/total),6) if total else None}

def scene(masks,kind,archived):
    raw=np.full((1105,1600),255,np.uint8)
    if kind=="full":
        for mask in masks.values():raw[mask]=0
    elif kind=="inside":
        for i,name in enumerate(SITES):
            orig_box=archived["variants"]["original"]["boxes"][i]
            # Strictly inside original boxes, padded to avoid JPEG border spill.
            inner=boxmask(raw.shape,orig_box,INNER_NEGATIVE_MARGIN)
            raw[masks[name]&inner]=0
    else:raise ValueError(kind)
    return raw

def controls(ms,archived):
    cases=[]
    for kind in ("full","inside"):
        images=variants(scene(ms,kind,archived))
        for fmt in FORMATS:
            for i,name in enumerate(SITES):
                poly=ms[name]
                box=archived["variants"][fmt]["boxes"][i]
                measured=ink_measure(images[fmt],poly,box,150)
                g=geometry(poly,box)
                ratio=measured["fraction_lost"]
                if kind=="full":
                    ok=measured["dark_ink"]>20 and ratio is not None and abs(ratio-g["omitted_area_fraction"])<=.035
                else:
                    ok=measured["dark_ink"]>20 and ratio is not None and ratio<=.03
                cases.append({"type":kind,"format":fmt,"site":name,
                   "pass":bool(ok),"dark_px":measured["dark_ink"],
                   "lost_fraction":ratio,
                   "geometric_reference":round(g["omitted_area_fraction"],6)})
    return {"pass":len(cases)==40 and all(z["pass"] for z in cases),
            "passed":sum(z["pass"] for z in cases),"cases":len(cases),
            "failures":[z for z in cases if not z["pass"]]}

def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=SHA:raise RuntimeError("Canonical SHA changed")
    old=json.loads(STAGE112.read_text())
    prev=json.loads(STAGE163.read_text())
    if prev["decision"]!="VERIFIED_LEGACY_SUPERBATCH_OBJECT_CROP_SCOPE_DEFECT":
        raise RuntimeError("Stage163 unverified")
    if tuple(SEARCH)!=(900,345,1585,500) or tuple(MASK_THRESHOLDS)!=THRESHOLDS:
        raise RuntimeError("Stage112 registration changed")
    if "SEARCH=(900,345,1585,500)" not in OLD_CODE.read_text():
        raise RuntimeError("Stage112 script text no longer matches")
    if old["detected_centers"]["original"]!=[1042,1148,1282,1372,1490]:
        raise RuntimeError("Stage112 five genuine identifiers changed")
    original=np.asarray(Image.open(SOURCE).convert("L"))
    if original.shape!=(1105,1600):raise RuntimeError("source dimensions")
    expected={}
    for fmt in FORMATS:
        cent=old["detected_centers"][fmt]
        exact=boxes_from_centers(cent,1600)
        saved=old["variants"][fmt]["boxes"]
        expected[fmt]=bool([list(b) for b in exact]==saved and
                           all(b[1]==345 and b[3]==500 for b in exact))
    mask=masks(original.shape)
    ctr=controls(mask,old)
    data={}
    available=True
    for fmt,im in variants(original).items():
        if fmt not in FORMATS:continue
        data[fmt]={}
        for t in THRESHOLDS:
            tr={}
            for i,name in enumerate(SITES):
                tr[name]=ink_measure(im,mask[name],old["variants"][fmt]["boxes"][i],t)
                available &= tr[name]["dark_ink"]>=SOURCE_PIXELS_MIN
            data[fmt][str(t)]=tr
    stable={}
    for name in SITES:
        stable[name]=all(data[fmt][str(t)][name]["fraction_lost"] is not None
            and data[fmt][str(t)][name]["fraction_lost"]>=OMISSION_THRESHOLD
            for fmt in FORMATS for t in THRESHOLDS)
    count=sum(stable.values())
    archived_valid=all(expected.values())
    decision=("CONTROL_FAILURE" if not ctr["pass"] or not archived_valid else
          "INSUFFICIENT_REAL_SAIL_INK_SAMPLE" if not available else
          "STAGE112_UPPER_SAIL_CROPS_MATERIALLY_INCOMPLETE"
              if count>=MIN_MATERIAL_SAILS else
          "STAGE112_COMPLETE_SAIL_MATERIAL_TRUNCATION_NOT_ESTABLISHED")
    result={
       "experiment_id":"A11-EXP-164","canonical_sha256":sha,
       "source_original":"Stage153 fixed 5 genuine small sail polygons",
       "Stage112_boxes_reproduced":expected,
       "Stage112_code_search":SEARCH,"Stage112_thresholds":THRESHOLDS,
       "synthetic_controls":ctr,"source_ink_sufficient_all_conditions":bool(available),
       "fixed_geometry":{name:{"polygon":SITES[name],
                      "original_stage112_crop":old["variants"]["original"]["boxes"][i],
                      "geometric_omission":geometry(mask[name],old["variants"]["original"]["boxes"][i])}
                      for i,name in enumerate(SITES)},
       "ink_omission_by_variant":data,
       "material_loss_stable_by_sail":stable,
       "materially_incomplete_true_sails":count,"decision":decision,
       "scope_limit":"Stage112 detection of which five sail apexes is distinct from its measured widths in an upper-only y345..500 crop; this coverage audit does not determine corrected full-object widths or invalidate all Stage112 observations.",
       "safety":"Canonical source and fixed polygons only; no key, BIP39, wallet, address or external research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    report=["# Stage164 — Stage112 true-five-sail width input window source adequacy","",
        f"- Canonical SHA: **{sha==SHA}**",
        f"- Stage112 exact archived 5-box replay: **{sum(expected.values())}/4 variants**",
        f"- Positive/negative synthetic source-box controls: **{ctr['passed']}/{ctr['cases']}**",
        f"- Source five sails x 12 variant/threshold settings ink >=200: **{bool(available)}**",
        f"- >=20% real sail ink excluded in all 12 settings: **{count}/5**",
        f"- Decision: **{decision}**","",
        "| Sail | Stage112 base y limit | Actual reference base y | Original t150 ink omitted | Geometric area omitted |",
        "|---|---:|---:|---:|---:|"]
    for i,name in enumerate(SITES):
        t=data["original"]["150"][name]["fraction_lost"]
        g=geometry(mask[name],old["variants"]["original"]["boxes"][i])
        y=max(p[1] for p in SITES[name])
        report.append(f"| {name} | 500 | {y} | {t:.1%} | {g['omitted_area_fraction']:.1%} |")
    report+=["","Stage112's x-center localization could still be correct, while its y345..500 width crops do not cover complete pencil sail shapes. This is a source-coverage fact, not confirmation of an intentional width sequence or cryptographic message.","",
              "No private key, wallet or text extraction performed.",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":164,"controls":f"{ctr['passed']}/{ctr['cases']}",
         "old_boxes":sum(expected.values()),"incomplete":count,"decision":decision}))
if __name__=="__main__":
    main()
