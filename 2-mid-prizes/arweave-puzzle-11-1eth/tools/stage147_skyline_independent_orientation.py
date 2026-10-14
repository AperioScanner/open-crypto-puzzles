#!/usr/bin/env python3
"""A11-EXP-147 — independent detectors for source skyline horizontal bands.

Stage146 established two visually strong source band apertures in all four
renderings using Stage144's long-horizontal morphological opening. This
confirmation tests the SAME fixed upper/lower source bands using TWO OTHER
detection methods: (1) independent Canny/Hough horizontal line segments,
(2) Sobel horizontal-versus-vertical stroke energy per building-width x-bin.
It does NOT change source coordinates to optimize for a positive finding.

Calibration reuses Stage146's synthetic two-line, upper-only, lower-only and
no-horizontal-line images under all four source/JPEG/rendering variants.
The stage cannot infer a tower, chess piece, key, intended cipher or mnemonic.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from stage112_corrected_sail_width_progression import variants
from stage144_rotated_skyline_spire import SHA,X0,X1,N_BLOCKS,FORMATS
from stage146_fixed_skyline_bands import (
    UPPER_Y,LOWER_Y,synthetic as stage146_synthetic,
    measure as stage146_measure
)

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE146=ROOT/"analysis"/"runs"/"stage146-fixed-skyline-bands"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage147-independent-skyline-line-detectors"
OUT.mkdir(parents=True,exist_ok=True)

# All source-bounds and thresholds fixed before independent detector analysis;
# Hough and Sobel have no access to Stage144's morphology output.
SOBEL_HORIZONTAL_MIN=.18
INK_DENSITY_MIN=.015
HOUGH_MAX_SLOPE_DEGREES=13.0
HOUGH_SEGMENT_MIN=19
HOUGH_MIN_PASSES=6
SOBEL_MIN_PASSES=6
CANNY_LOW=60
CANNY_HIGH=145
CONTROL_TYPES=("two","upper_only","lower_only","none")
MIN_SOURCE_CROSS_METHOD_PAIRS=2
BANDS=(("upper",UPPER_Y),("lower",LOWER_Y))

def score_one_bin(patch):
    ink_density=float(np.mean(patch<175))
    f=patch.astype(np.float32)
    gx=cv2.Sobel(f,cv2.CV_32F,1,0,ksize=3)
    gy=cv2.Sobel(f,cv2.CV_32F,0,1,ksize=3)
    ex=float(np.mean(gx*gx))
    ey=float(np.mean(gy*gy))
    horizontal_sobel=(ey-ex)/(ey+ex+1e-9)
    sobel=ink_density>=INK_DENSITY_MIN and horizontal_sobel>=SOBEL_HORIZONTAL_MIN
    edges=cv2.Canny(patch,CANNY_LOW,CANNY_HIGH)
    lines=cv2.HoughLinesP(edges,1,np.pi/180,threshold=6,
                          minLineLength=HOUGH_SEGMENT_MIN,maxLineGap=7)
    horizontal=0
    if lines is not None:
        for x1,y1,x2,y2 in np.asarray(lines).reshape(-1,4):
            dx=x2-x1;dy=y2-y1
            length=math.hypot(dx,dy)
            if length<HOUGH_SEGMENT_MIN:continue
            if abs(math.degrees(math.atan2(dy,dx)))<=HOUGH_MAX_SLOPE_DEGREES:
                horizontal+=1
    hough=ink_density>=INK_DENSITY_MIN and horizontal>=1
    return {
       "sobel_horizontal":bool(sobel),
       "hough_horizontal":bool(hough),
       "sobel_horizontal_energy_score":round(horizontal_sobel,6),
       "ink_density":round(ink_density,6),
       "hough_horizontal_segments":horizontal
    }

def evaluate(frame):
    output={}
    h,w=frame.shape
    if h!=1105 or w!=1600:raise RuntimeError("Wrong frame shape")
    for band,(y0,y1) in BANDS:
        roi=frame[y0:y1+1,X0:X1]
        n,width=roi.shape
        cells=[]
        for k in range(N_BLOCKS):
            xa=k*width//N_BLOCKS
            xb=(k+1)*width//N_BLOCKS
            cell=score_one_bin(roi[:,xa:xb])
            cells.append(cell)
        sobel_blocks=sum(x["sobel_horizontal"] for x in cells)
        hough_blocks=sum(x["hough_horizontal"] for x in cells)
        output[band]={
           "source_rows":[y0,y1],
           "sobel_support_blocks":sobel_blocks,
           "hough_support_blocks":hough_blocks,
           "both_estimators_support":bool(
               sobel_blocks>=SOBEL_MIN_PASSES and
               hough_blocks>=HOUGH_MIN_PASSES
           ),
           "per_bin_readings":cells
        }
    output["both_bands_agree_independently"]=all(
       output[band]["both_estimators_support"] for band,_ in BANDS
    )
    return output

def calibrate():
    all_results={}
    pass_count=0
    cases=0
    for kind in CONTROL_TYPES:
        fake=stage146_synthetic(kind)
        all_results[kind]={}
        for name,a in variants(fake).items():
            if name not in FORMATS:continue
            z=evaluate(a)
            upper=z["upper"]["both_estimators_support"]
            lower=z["lower"]["both_estimators_support"]
            expected_upper=kind in ("two","upper_only")
            expected_lower=kind in ("two","lower_only")
            ok=(upper==expected_upper and lower==expected_lower)
            all_results[kind][name]={
               "pass":ok,
               "upper_sobel_blocks":z["upper"]["sobel_support_blocks"],
               "upper_hough_blocks":z["upper"]["hough_support_blocks"],
               "lower_sobel_blocks":z["lower"]["sobel_support_blocks"],
               "lower_hough_blocks":z["lower"]["hough_support_blocks"]
            }
            pass_count+=int(ok)
            cases+=1
    return {
        "pass":cases==16 and pass_count==16,
        "cases":cases,
        "passed":pass_count,
        "fixtures":all_results
    }

def original_chain_replay(original,old):
    if not old["controls"]["pass"] or not old["reproduced_stage145_source"]:
        return False
    for name,a in variants(original).items():
        if name not in FORMATS:continue
        if stage146_measure(a)!=old["source_results"][name]:return False
    return True

def save_source_comparison(gray,z):
    copy=Image.fromarray(gray).convert("RGB")
    mark=ImageDraw.Draw(copy)
    mark.rectangle((X0,UPPER_Y[0],X1,UPPER_Y[1]),outline=(50,100,215),width=3)
    mark.rectangle((X0,LOWER_Y[0],X1,LOWER_Y[1]),outline=(230,75,55),width=3)
    copy.save(OUT/"independent-skyline-source-apertures.png")

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if sha!=SHA:raise RuntimeError("Canonical image mismatch")
    gray=np.asarray(Image.open(PNG).convert("L"))
    if gray.shape!=(1105,1600):raise RuntimeError("Unexpected image size")
    prior=json.loads(STAGE146.read_text())
    controls=calibrate()
    chain=original_chain_replay(gray,prior)
    output={fmt:evaluate(a) for fmt,a in variants(gray).items()
            if fmt in FORMATS}
    adequate=all(output[v]["both_bands_agree_independently"] for v in FORMATS)
    decision=(
       "CONTROL_FAILURE" if not controls["pass"] else
       "STAGE146_SOURCE_REPRODUCTION_FAILURE" if not chain else
       "TWO_HORIZONTAL_SOURCE_BANDS_CONFIRMED_INDEPENDENTLY"
       if adequate else
       "NO_CROSS_METHOD_CONFIRMATION_OF_BOTH_SOURCE_BANDS"
    )
    report={
      "experiment_id":"A11-EXP-147",
      "hypothesis":"two native horizontal skyline stroke bands confirmed by Stage146's morphology also survive an independent Canny/Hough line and Sobel orientation audit at fixed source y windows",
      "evidence":"Stage146 found source horizontal support in 4/4 renderings; source band y230..275 morphology merging after resampling required not conflating connected-component counts with real source line presence.",
      "scope":"Stage146 fixed y232..242 and y252..267 x180..1595 in original/JPEG85/JPEG70/down75_up, 12 x-bins, independent Sobel and Canny/Hough metrics",
      "sha256":sha,
      "criteria":{"sobel_horizontal_energy_gate":SOBEL_HORIZONTAL_MIN,
                  "minimum_ink_density":INK_DENSITY_MIN,
                  "maximum_hough_line_tilt_deg":HOUGH_MAX_SLOPE_DEGREES,
                  "minimum_hough_segment_px":HOUGH_SEGMENT_MIN,
                  "minimum_bins_per_detector_per_band":6},
      "controls":controls,
      "stage146_image_measurement_reproduced_exactly":chain,
      "by_variant":output,
      "independent_two_band_confirmation":adequate,
      "decision":decision,
      "interpretation_limits":"Source windows selected after Stage145 original inspection, not prospectively independent: even confirmed horizontal source lines explain only ordinary pixel geometry and cannot establish a unique spire/chess symbol, encoding or author intent. JPEG variants reuse the same source and are statistically correlated.",
      "safety":"No secret candidate enumeration, private key, BIP39, mnemonic, wallet, Ethereum address check or off-image research."
    }
    save_source_comparison(gray,output["original"])
    (OUT/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    md=[
       "# Stage147 — independent stroke detectors for source skyline bands","",
       f"- Original PNG hash verified: **{sha==SHA}**",
       f"- Independent-detector positive/single/no-band controls: **{controls['passed']}/{controls['cases']}**",
       f"- Stage146 source replay exact: **{chain}**",
       f"- Both native horizontal source bands supported by BOTH methods in all formats: **{adequate}**",
       f"- Decision: **{decision}**","",
       "| format | upper Sobel/Hough supported x-bins | lower Sobel/Hough |",
       "|---|---:|---:|"
    ]
    for v in FORMATS:
        t=output[v]["upper"]
        b=output[v]["lower"]
        md.append(f"| {v} | {t['sobel_support_blocks']}/{t['hough_support_blocks']} | {b['sobel_support_blocks']}/{b['hough_support_blocks']} |")
    md+=["","## Interpretation",""]
    if not controls["pass"] or not chain:
        md.append("Control/calibration failed; repair SAME Stage147 before real image conclusions.")
    elif adequate:
        md.append("Two source-band horizontal stroke signatures survive an independent line-segment/gradient audit. The black central spike of a rotated+mirrored montage remains explainable by ordinary original skyline pencil work, not a verified special symbol.")
    else:
        md.append("An independent horizontal-stroke method did not corroborate both fixed source bands in every format. Stage146's morphology-only finding should not be overinterpreted.")
    md+=["","No key/phrase/wallet activity.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"stage":147,"controls":controls["pass"],"chain":chain,
                      "adequate":adequate,"decision":decision}))

if __name__=="__main__":main()
