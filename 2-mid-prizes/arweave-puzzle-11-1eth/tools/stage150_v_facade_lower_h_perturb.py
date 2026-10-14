#!/usr/bin/env python3
"""A11-EXP-150 — test whether Stage149's V→H base-layer phenomenon is crop-stable.

Stage149 found 3 of 4 V-labelled buildings (#3/#4/#7) have lower-facade H
hatches (fully format-stable), while #12 retains V in all 3 strips. This
could be ordinary facade/base pencil treatment OR an artifact from exact
trim locations. The present stage tests a fixed, predeclared 3x3 crop jitter
grid plus original/JPEG85/JPEG70/75% resample, never optimizing source bounds.

Calibration before interpreting original:
* positive V-upper/V-middle/H-lower synthetic facades,
* negative full-V facades,
* full-V facades with an unrelated H stroke outside the lower crop.
All 4 V-labelled building geometries use these controls.

This is **not** a BIP39, key, 321 or wallet test. It measures painted source
directions only; the result cannot determine whether the painter intended bits.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image,ImageDraw

from stage112_corrected_sail_width_progression import variants
from stage149_hv_within_facade_layers import (
    SHA,EXPECTED,ZONES,estimate,boxes,
    MIN_DARK_FRACTION,STROKE_SPACING
)

ROOT=Path(__file__).resolve().parents[1]
IMAGE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOMETRY=ROOT/"data"/"geometry.json"
PREVIOUS=ROOT/"analysis"/"runs"/"stage149-hv-facade-layers"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage150-v-base-layer-perturb"
OUT.mkdir(parents=True,exist_ok=True)
FORMATS=("original","jpeg85","jpeg70","down75_up")
V_IDS=(3,4,7,12)
MIXED_KNOWN_IDS=(3,4,7)
ALL_V_KNOWN_ID=12
X_JITTER=(-4,0,4)
Y_JITTER=(-3,0,3)
N_PER_BUILDING=36
MIN_STABLE=31   # 31/36 or 86%, no a-posteriori relaxation.
MAX_FALSE=5
KINDS=("upper_V_lower_H","all_V","V_with_outside_H")

def shifts():
    return [(dx,dy) for dx in X_JITTER for dy in Y_JITTER]

def jiggle(box,dx,dy):
    x0,y0,x1,y1=box
    return (x0+dx,y0+dy,x1+dx,y1+dy)

def synthetic_fixture(buildings,kind):
    image=np.full((1105,1600),255,np.uint8)
    regions=boxes(buildings)
    for bid in V_IDS:
        for zone in ZONES:
            xa,ya,xb,yb=regions[(bid,zone)]
            # Build 6px outer guard so a ±4x/±3y jitter still measures
            # pencil marks rather than newly introduced blank edges.
            xa-=6;xb+=6;ya-=4;yb+=4
            mode=("H" if zone=="lower" and kind=="upper_V_lower_H"
                  else "V")
            if mode=="V":
                for x in range(xa+3,xb-3,STROKE_SPACING):
                    cv2.line(image,(x,ya+1),(x,yb-2),0,2,cv2.LINE_AA)
            else:
                for y in range(ya+2,yb-2,STROKE_SPACING):
                    cv2.line(image,(xa+2,y),(xb-3,y),0,2,cv2.LINE_AA)
        if kind=="V_with_outside_H":
            x0,y0,x1,y1=regions[(bid,"lower")]
            # Deliberately OUTSIDE even the widest ±3px perturbation.
            cv2.line(image,(x0-5,y1+13),(x1+5,y1+13),
                     0,3,cv2.LINE_AA)
    return image

def examine(frames,regions):
    result={}
    for bid in V_IDS:
        obs={"upper":[],"lower":[]}
        for name in FORMATS:
            frame=frames[name]
            for dx,dy in shifts():
                for zone in ("upper","lower"):
                    test=estimate(frame,jiggle(regions[(bid,zone)],dx,dy))
                    obs[zone].append(test["class"])
        result[str(bid)]={
           "upper_counts":{c:obs["upper"].count(c) for c in ("V","H",None)},
           "lower_counts":{c:obs["lower"].count(c) for c in ("V","H",None)},
           "upper_v_fraction":round(obs["upper"].count("V")/N_PER_BUILDING,6),
           "lower_h_fraction":round(obs["lower"].count("H")/N_PER_BUILDING,6),
           "lower_v_fraction":round(obs["lower"].count("V")/N_PER_BUILDING,6)
        }
    return result

def calibrate(buildings,regions):
    controls={}
    all_pass=True
    for kind in KINDS:
        z=examine(variants(synthetic_fixture(buildings,kind)),regions)
        passes={}
        for bid in V_IDS:
            x=z[str(bid)]
            positive=kind=="upper_V_lower_H"
            ok=bool(
                x["upper_counts"]["V"]>=MIN_STABLE
                and x["lower_counts"]["H" if positive else "V"]>=MIN_STABLE
                and (positive or x["lower_counts"]["H"]<=MAX_FALSE)
            )
            passes[str(bid)]=ok
        correct=all(passes.values())
        controls[kind]={"pass":correct,"by_building_pass":passes,
                        "by_building":z}
        all_pass=all_pass and correct
    return {
       "pass":bool(all_pass),
       "cases":len(KINDS)*len(V_IDS)*N_PER_BUILDING*2,
       "case_definition":"three synthetic fixture types × four V facade sites × 4 source formats × 3x3 jitters × two facade zones",
       "regime_checks_passed":sum(z["pass"] for z in controls.values()),
       "regime_checks_total":len(KINDS),
       "details":controls
    }

def original_source_provenance(old):
    if not(old["controls"]["pass"] and old["whole_source_HV_reproduction_pass"]
           and old["sha256"]==SHA):return False
    for bid in V_IDS:
        entry=old["building_summary"][str(bid)]
        if entry["whole_facade_stage10"]!="V":return False
        if entry["upper_middle_lower"]["upper"]!="V":return False
        if bid in MIXED_KNOWN_IDS and entry["upper_middle_lower"]["lower"]!="H":
            return False
        if bid==ALL_V_KNOWN_ID and entry["upper_middle_lower"]["lower"]!="V":
            return False
    return True

def main():
    digest=hashlib.sha256(IMAGE.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("canonical source hash mismatch")
    gray=np.asarray(Image.open(IMAGE).convert("L"))
    if gray.shape!=(1105,1600):raise RuntimeError("canonical dimensions mismatch")
    buildings=json.loads(GEOMETRY.read_text())["buildings"]
    region=boxes(buildings)
    prior=json.loads(PREVIOUS.read_text())
    source_chain=original_source_provenance(prior)
    controls=calibrate(buildings,region)
    source=examine(variants(gray),region)

    all_uppers=all(source[str(bid)]["upper_counts"]["V"]>=MIN_STABLE
                   for bid in V_IDS)
    three_mixed=all(source[str(bid)]["lower_counts"]["H"]>=MIN_STABLE
                    for bid in MIXED_KNOWN_IDS)
    one_uniform=source[str(ALL_V_KNOWN_ID)]["lower_counts"]["V"]>=MIN_STABLE
    physical_pattern=bool(all_uppers and three_mixed and one_uniform)

    decision=(
        "CONTROL_FAILURE" if not controls["pass"] else
        "STAGE149_SOURCE_PROVENANCE_FAILURE" if not source_chain else
        "V_BUILDING_BASAL_HATCH_CHANGE_SOURCE_ROBUST"
        if physical_pattern else
        "V_BUILDING_BASAL_HATCH_CHANGE_NOT_REPLICATED_UNDER_JITTER"
    )
    payload={
       "experiment_id":"A11-EXP-150",
       "hypothesis":"three of the four V-painted buildings have stable H-painted basal zones independent of moderate user-selected cropping, while the fourth is V throughout",
       "motivation":"Stage149 classified 35/36 facade 3-tier regions across 4 formats and identified lower H at #3/#4/#7 vs lower V at #12, but did not perturb crop boxes",
       "scope":"known V source buildings 3,4,7,12, their fixed Stage149 upper and lower zones; 3 x jitters × 3 y jitters × 4 re-encodings; same two-estimator Stage149 rule unchanged",
       "sha256":digest,
       "source_original_HV":EXPECTED,
       "predeclared_shifts":{"x":list(X_JITTER),"y":list(Y_JITTER)},
       "thresholds":{"min_V_upper_cases":MIN_STABLE,
                     "min_lower_expected_cases":MIN_STABLE,
                     "max_false_negative_H_cases":MAX_FALSE,
                     "cases_per_zone_per_building":N_PER_BUILDING},
       "controls":controls,
       "stage149_original_provenance_reproduced":source_chain,
       "source_by_building":source,
       "all_four_upper_V_robust":all_uppers,
       "three_lower_H_robust":three_mixed,
       "building_12_lower_V_robust":one_uniform,
       "full_observed_pattern_replicated":physical_pattern,
       "decision":decision,
       "interpretation_limit":"This is a post-Stage149 crop-perturbation stability audit of the SAME pixels, not independent evidence of encoded bits. Basal H hatching may be conventional artist shading; original H0 V1 321 remains interpretationally unproven.",
       "safety_guard":"No private key, BIP39, mnemonic, wallet, address, transactions or off-image/social research."
    }
    (OUT/"result.json").write_text(json.dumps(payload,indent=2)+"\n")
    report=[
       "# Stage 150 — are three V-building H base layers source-robust?",
       "",
       f"- Canonical PNG hash: **{digest==SHA}**",
       f"- Known V/V/H vs V/V/V vs exterior-H synthetic controls: **{controls['regime_checks_passed']}/{controls['regime_checks_total']} regimes**",
       f"- Original Stage149 source pattern reproduced: **{source_chain}**",
       f"- Three H bases remain robust under 36 observations each: **{three_mixed}**",
       f"- Remaining V building 12 stays V through bottom: **{one_uniform}**",
       f"- Decision: **{decision}**","",
       "| facade | top V /36 | basal H /36 | basal V /36 |",
       "|---|---:|---:|---:|"
    ]
    for bid in V_IDS:
        a=source[str(bid)]
        report.append(f"| {bid} | {a['upper_counts']['V']} | {a['lower_counts']['H']} | {a['lower_counts']['V']} |")
    report+=["","## Interpretation",""]
    if not controls["pass"] or not source_chain:
        report.append("Synthetic controls or source provenance failed. Repair Stage150; no inference about original.")
    elif physical_pattern:
        report.append("The 3-of-4 V façade lower-zone H shift survives fixed window jitter and lossy transformations; this is a real mixed painting style, NOT evidence for a 12-bit cryptogram.")
    else:
        report.append("The Stage149 3-of-4 lower H observation fails some of the fixed crop perturbations; treat bottom hatching as boundary-sensitive.")
    report+=["","No secret, key, mnemonic or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":150,"controls":controls["pass"],
        "source":source_chain,"all_uppers":all_uppers,
        "3H":three_mixed,"1V":one_uniform,"decision":decision}))

if __name__=="__main__":
    main()
