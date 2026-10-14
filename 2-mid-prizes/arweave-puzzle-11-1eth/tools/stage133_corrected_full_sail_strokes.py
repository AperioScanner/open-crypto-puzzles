#!/usr/bin/env python3
"""Stage 133 — provenance-corrected full large-sail stroke measurement.

Stage 132 has independently demonstrated an implementation defect in the
large_sailboat ROI shared by earlier structural tests: the box misses ~2/3 of
the visible triangular sail ink. This is a FIXED-ROI replication of Stage 94's
nonsecret stroke-count measurement, not a search for keys or candidate payloads.

Reuses exact Stage-94 detector, thresholds, track deduplication and positive
control mechanism; only the source-image ROI changes to the already fixed
Stage-132 manual large-sail polygon. Records counts and agreement only.
No ordered stroke signs, mnemonics, keys, addresses or wallet operations.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from stage112_corrected_sail_width_progression import variants
from stage132_large_sail_legacy_bbox_audit import POLYGONS
from stage94_large_sail_stroke_carrier import (
    sail_roi, track_across_thresholds, summarize,
    cross_agreement, synthetic_calibration,
)

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage133-corrected-large-sail-strokes"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")

# Same Stage132 source polygon, no new points. Erode boundary to prevent
# object outline from being counted as interior strokes.
SAIL_POLYGON=tuple(map(tuple,POLYGONS["large_sail"]))
EDGE_ERODE=5
SOURCE_THR=170
MAX_BLANK_TRACKS=0
MIN_SYNTH_16=6
MIN_SYNTH_64=15
MIN_SYNTH_64_ABOVE_16=10
MIN_REAL_PIXELS=1200
MIN_LEGACY_MISSING=.65

def full_sail_roi(gray):
    points=np.asarray(SAIL_POLYGON,dtype=np.int32)
    x0,y0=np.min(points,axis=0)-4
    x1,y1=np.max(points,axis=0)+5
    x0,y0,x1,y1=map(int,(x0,y0,x1,y1))
    patch=gray[y0:y1,x0:x1]
    mask=np.zeros_like(patch,dtype=np.uint8)
    cv2.fillPoly(mask,[points-np.array([x0,y0])],1)
    mask=cv2.erode(mask,np.ones((EDGE_ERODE,EDGE_ERODE),np.uint8),iterations=1)
    return patch,mask,{"box":[x0,y0,x1,y1],"mask_pixels":int(mask.sum()),
                       "full_polygon_points":list(map(list,SAIL_POLYGON))}

def run_detector(gray,full):
    outputs={}
    tracks={}
    geometry={}
    for name,arr in variants(gray).items():
        if name not in FORMATS:continue
        patch,mask,g=full_sail_roi(arr) if full else sail_roi(arr)
        geometry=g
        candidates=track_across_thresholds(patch,mask)
        tracks[name]=candidates
        outputs[name]=summarize(candidates)
    baseline=tracks["original"]
    agreement={n:cross_agreement(baseline,t) for n,t in tracks.items()
               if n!="original"}
    counts=[outputs[n]["classifiable_tracks"] for n in FORMATS]
    return {
        "geometry":geometry,
        "variant_summaries":outputs,
        "agreement":agreement,
        "min_classifiable":int(min(counts)),
        "max_classifiable":int(max(counts)),
        "classifiable_cv":round(float(np.std(counts)/np.mean(counts)),6)
        if np.mean(counts)>0 else None,
    }

def synthetic_checks(gray):
    patch,mask,geom=full_sail_roi(gray)
    empty=np.full(patch.shape,255,dtype=np.uint8)
    blank_count=summarize(track_across_thresholds(empty,mask))["classifiable_tracks"]
    calibration=synthetic_calibration(patch.shape,mask)
    c=calibration["controls"]
    ctl16=c["16"]["min_detected"]
    ctl64=c["64"]["min_detected"]
    passed=bool(
        blank_count<=MAX_BLANK_TRACKS
        and ctl16>=MIN_SYNTH_16
        and ctl64>=MIN_SYNTH_64
        and ctl64>=ctl16+MIN_SYNTH_64_ABOVE_16
    )
    return {
        "pass":passed,
        "blank_tracks":int(blank_count),
        "synthetic_16_min":int(ctl16),
        "synthetic_64_min":int(ctl64),
        "synthetic_256_min":int(c["256"]["min_detected"]),
        "controls_calibrated":c,
        "drawn_detected_correlation":float(calibration["detected_vs_drawn_pearson"]),
    }

def roi_integrity(gray):
    c,mask,_=full_sail_roi(gray)
    mask_bool=mask>0
    dark=(c<SOURCE_THR)
    original_count=int((dark&mask_bool).sum())
    old_patch,old_mask,geom=sail_roi(gray)
    # Source-geometry provenance: the full visible sail polygon is mostly
    # outside the rectangle used by Stage94.
    x0,y0,x1,y1=geom["box"]
    pts=np.asarray(SAIL_POLYGON,np.int32)
    gx0,gy0=np.min(pts,axis=0)-4
    ref=np.zeros(c.shape,np.uint8)
    l=max(0,x0-int(gx0));t=max(0,y0-int(gy0))
    r=min(c.shape[1],x1-int(gx0))
    b=min(c.shape[0],y1-int(gy0))
    if r>l and b>t:
        ref[t:b,l:r]=1
    outside=int((dark&mask_bool&(ref==0)).sum())
    return {
        "visible_sail_ink":original_count,
        "outside_legacy_box":outside,
        "fraction_outside":round(outside/max(1,original_count),6),
        "source_pass":bool(original_count>=MIN_REAL_PIXELS
                           and outside/max(1,original_count)>=MIN_LEGACY_MISSING)
    }

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=SHA:raise SystemExit("Unexpected canonical PNG checksum")
    arr=np.asarray(Image.open(PNG).convert("L"))
    if arr.shape!=(1105,1600):raise SystemExit("Unexpected image shape")
    source=roi_integrity(arr)
    controls=synthetic_checks(arr)
    old=run_detector(arr,full=False)
    corrected=run_detector(arr,full=True)
    old_max=old["max_classifiable"]
    new_max=corrected["max_classifiable"]

    # Decisive claim is merely that Stage94's data coverage was incomplete.
    # If counts differ, quantify direction; a larger raw count is not evidence
    # of 64/256 symbols and a smaller count would not validate old negatives.
    decision=("CONTROL_FAILURE" if not controls["pass"] else
              "ROI_SOURCE_FAILURE" if not source["source_pass"] else
              "STAGE94_CARRIER_NEGATIVE_REQUIRES_REAUDIT")
    result={
        "experiment_id":"A11-EXP-133",
        "date":"2026-10-13",
        "hypothesis":"Stage94 inherited a source-geometry defect and its short-patch count-negative must not be extrapolated to the full, visible large sail",
        "cause":"Stage132 verified the old bounding-box omission; this is a proven implementation defect, not a recycled arbitrary encoding search.",
        "scope":"reproduce Stage94's nonsecret structural tracking in old ROI and corrected Stage132 full-sail triangle; 4 image variants; synthetic 16/32/64/128/256 controls and blank control",
        "sha256":digest,
        "polygon_from_stage132":list(map(list,SAIL_POLYGON)),
        "eroded_edge_px":EDGE_ERODE,
        "real_source_control":source,
        "detector_calibration":controls,
        "old":old,
        "corrected":corrected,
        "max_count_difference_new_minus_old":int(new_max-old_max),
        "decision":decision,
        "interpretation_guard":"Regardless of sign of count differences, this is solely an ROI-provenance and visible-stroke diagnostic; no hidden sequence or key can be inferred. Old Stage94 numerical negative only covered its truncated ROI.",
        "safety_guard":"Canonical visible image only, no private keys, word lists, seeds, wallet operations, external references or candidate verifications."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=[
        "# Stage 133 — corrected full-sail stroke audit",
        "",
        f"- Canonical image hash: **{digest==SHA}**",
        f"- Fixed Stage132 ROI source control: **{source['source_pass']}** (sail ink missed {source['fraction_outside']:.3f})",
        f"- Synthetic count + blank controls: **{controls['pass']}** (16 → {controls['synthetic_16_min']}, 64 → {controls['synthetic_64_min']}, blank → {controls['blank_tracks']})",
        f"- Old ROI classifiable count range (4 variants): **{old['min_classifiable']}–{old['max_classifiable']}**",
        f"- Complete sail classifiable count range: **{corrected['min_classifiable']}–{corrected['max_classifiable']}**",
        f"- Decision: **{decision}**",
        "",
        "| format | legacy truncated classifiable | full-sail classifiable |",
        "|---|---:|---:|",
    ]
    for name in FORMATS:
        md.append(f"| {name} | {old['variant_summaries'][name]['classifiable_tracks']} | {corrected['variant_summaries'][name]['classifiable_tracks']} |")
    md+=["","## Interpretation",""]
    if not controls["pass"]:
        md.append("Detection control failure. Repair Stage133; do not interpret real image counts.")
    elif not source["source_pass"]:
        md.append("Corrected ROI not independently verified. Do not claim the source defect is measured in this run.")
    else:
        md.append("Earlier Stage94 detector measured a truncated piece of the object. Its negative cannot be generalized to the entire visible sail; the corrected counts are descriptive, not evidence for any key-size coding.")
    md+=["","No ordered strokes, keys or wallet activity.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"stage":133,"controls":controls["pass"],
                      "source":source["source_pass"],
                      "old_range":[old["min_classifiable"],old["max_classifiable"]],
                      "new_range":[corrected["min_classifiable"],corrected["max_classifiable"]],
                      "decision":decision}))

if __name__=="__main__":
    main()
