#!/usr/bin/env python3
"""A11-EXP-128: closed-loop topology of four visible water-ripple groups.

Image-only. Different from prior building topology, reflection correlations,
text/OCR, repeated raster patches and boat/hull slope tests. The question is
whether water ripples contain stable, bounded, closed oval marks that could
serve as reproducible *visible* subdetails rather than incidental open curves.

All windows, methods, thresholds, controls and decision rules are fixed.
No key, seed, BIP39, wallet, social, or off-image operations.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage128-water-ripple-loops"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
VARIANTS=("original","jpeg85","jpeg70","down75_up")
THRESHOLDS=(130,175,210)
ROIS={
  "skyline_reflection":(180,275,730,378),
  "central_open_water":(495,555,855,850),
  "largeboat_lower_wake":(10,925,420,1090),
  "right_lower_water":(1010,815,1530,1060),
}
MIN_HOLE_AREA=24
MAX_HOLE_AREA=4000
MIN_DIAMETER=7
BORDER=5
MIN_STABLE_REGIONS=3
MIN_DISTINCT_POSITIVE_REGIONS=2

def counted_hole(contour,shape):
    area=float(cv2.contourArea(contour))
    if not MIN_HOLE_AREA<=area<=MAX_HOLE_AREA:
        return False
    x,y,w,h=cv2.boundingRect(contour)
    H,W=shape
    if min(w,h)<MIN_DIAMETER:
        return False
    if x<BORDER or y<BORDER or x+w>=W-BORDER or y+h>=H-BORDER:
        return False
    return True

def contour_holes(gray,cutoff):
    mask=(gray<cutoff).astype(np.uint8)*255
    contours,hier=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hier is None:return 0
    h=hier[0]
    return sum(1 for i,c in enumerate(contours) if h[i][3]>=0
               and counted_hole(c,gray.shape))

def floodfill_holes(gray,cutoff):
    """Independent background-connectivity model of white enclosed islands."""
    ink=(gray<cutoff)
    outside=np.zeros(ink.shape,np.uint8)
    # Connected white component touching any border is not a closed loop.
    passable=(~ink).astype(np.uint8)
    n,labels,stats,_=cv2.connectedComponentsWithStats(passable,connectivity=4)
    H,W=gray.shape
    holes=0
    for k in range(1,n):
        x,y,w,h,area=map(int,stats[k])
        if x<BORDER or y<BORDER or x+w>=W-BORDER or y+h>=H-BORDER:
            continue
        if area<MIN_HOLE_AREA or area>MAX_HOLE_AREA or min(w,h)<MIN_DIAMETER:
            continue
        # Check that the connected white island is fully bounded by ink
        # rather than merely by image/window edge.
        if not np.any(labels[y:y+h,x:x+w]==k):continue
        holes+=1
    return holes

def count_pair(gray,cutoff):
    return {
        "contours":int(contour_holes(gray,cutoff)),
        "floodfill":int(floodfill_holes(gray,cutoff)),
    }

def synthetic(closed):
    h,w=155,245
    a=np.full((h,w),255,np.uint8)
    for x in (32,92,152,212):
        if closed:
            cv2.ellipse(a,(x,77),(15,24),0,0,360,0,3,cv2.LINE_AA)
        else:
            cv2.ellipse(a,(x,77),(15,24),0,22,318,0,3,cv2.LINE_AA)
    # Open, incomplete scribbles of the sort present in the drawing.
    for i in range(3):
        cv2.line(a,(27+i*66,124),(55+i*66,134),0,1,cv2.LINE_AA)
    return a

def analyze_variants(gray):
    transformed=variants(gray)
    per={}
    for name in VARIANTS:
        per[name]={str(t):count_pair(transformed[name],t) for t in THRESHOLDS}
    counts=[x for family in per.values() for x in family.values()]
    values=[v for row in counts for v in row.values()]
    unanimous=len(set(values))==1
    stable_count=int(values[0]) if unanimous else None
    return {"by_variant":per,"stable":unanimous,"stable_count":stable_count,
            "count_range":[min(values),max(values)]}

def control_suite():
    pos=analyze_variants(synthetic(True))
    neg=analyze_variants(synthetic(False))
    # Re-encoding can cause one tiny gap; allow at most one missed oval,
    # while both independent algorithms must reject all open arcs.
    pos_vals=[v for fam in pos["by_variant"].values() for pair in fam.values()
              for v in pair.values()]
    neg_vals=[v for fam in neg["by_variant"].values() for pair in fam.values()
              for v in pair.values()]
    passed=min(pos_vals)>=3 and max(pos_vals)<=4 and max(neg_vals)==0
    return {
        "passed":bool(passed),
        "positive_closed_range":[int(min(pos_vals)),int(max(pos_vals))],
        "negative_open_range":[int(min(neg_vals)),int(max(neg_vals))],
        "cases":len(pos_vals)+len(neg_vals),
        "positive":pos,"negative":neg,
    }

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:raise SystemExit("canonical SHA256 mismatch")
    im=np.asarray(Image.open(SOURCE).convert("L"))
    if im.shape!=(1105,1600):
        raise SystemExit("canonical dimension mismatch")
    controls=control_suite()
    regions={}
    for name,(x0,y0,x1,y1) in ROIS.items():
        roi=im[y0:y1,x0:x1]
        regions[name]={"box":[x0,y0,x1,y1],"pixels":int(roi.size),
                       **analyze_variants(roi)}
    stable=[x["stable_count"] for x in regions.values() if x["stable"]]
    eligible=len(stable)
    positive=sum(x>0 for x in stable)
    promoted=(eligible>=MIN_STABLE_REGIONS
              and positive>=MIN_DISTINCT_POSITIVE_REGIONS)
    decision=(
      "CONTROL_FAILURE" if not controls["passed"] else
      "STABLE_WATER_LOOP_SUBDETAILS" if promoted else
      "UNSTABLE_OR_ABSENT_CLOSED_WATER_LOOPS"
    )
    result={
        "experiment_id":"A11-EXP-128",
        "hypothesis":"closed, elliptical pencil ripples are a consistent distinct visible subdetail across multiple water groups, not just open freehand strokes",
        "evidence":"the canonical picture visibly contains curved/loop-shaped water marks outside sails and buildings; previous closed-contour experiment focused on building facades rather than water",
        "scope":"four fixed water ROIs; two independently implemented enclosure detectors; JPEG85/JPEG70/resampling and three fixed thresholds, no secret material",
        "sha256":digest,
        "rois":ROIS,"thresholds":THRESHOLDS,
        "controls":controls,
        "regions":regions,
        "stable_regions":eligible,
        "regions_with_stable_loops":positive,
        "promoted":bool(controls["passed"] and promoted),
        "decision":decision,
        "stopping_rule":"synthetic controls must recover 3..4 closed ovals and zero open arcs; require >=3/4 stable ROIs and >=2 with stable nonzero loop count to promote as a visible secondary mark; otherwise narrow non-promotion",
        "scope_limit":"Does not test implicit open wave symbolism, transformations that close gaps, or outlines elsewhere. A stable loop count is visual evidence only, never an encoded word, number or secret.",
        "safety_guard":"No keys, word lists, wallet, transaction or social-reference work.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    report=[
       "# Stage 128 — water ripple closed-loop topology audit","",
       f"- Original image SHA verified: **{digest==SHA}**",
       f"- Synthetic closed/open controls: **{controls['passed']}** ({controls['cases']} readings)",
       f"- Stable water ROIs: **{eligible}/4**",
       f"- Stable, nonzero-loop ROIs: **{positive}/4**",
       f"- Decision: **{decision}**","",
       "| region | counts min/max | stable loop count |",
       "|:---|:---|---:|",
    ]
    for name,x in regions.items():
        report.append(f"| {name} | {x['count_range']} | {x['stable_count'] if x['stable'] else '?'} |")
    report+=["","## Interpretation",""]
    if not controls["passed"]:
        report.append("Synthetic controls failed. Do not interpret the real result; repair Stage 128.")
    elif promoted:
        report.append("Stable visible water-loop subdetails warrant independent manual inspection; this alone is not evidence of an encoding.")
    else:
        report.append("No sufficient reproducible closed-loop count pattern in the four fixed water ROIs. Retire only this exact method and region family.")
    report+=["","No secret material generated, derived or checked.",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"experiment":"A11-EXP-128","controls":controls["passed"],
       "stable":eligible,"nonzero":positive,"decision":decision}))

if __name__=="__main__":
    main()
