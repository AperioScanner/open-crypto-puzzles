#!/usr/bin/env python3
"""A11-EXP-158: Stage15 large-sailboat region, corrected after proven Stage132 ROI defect.

Replays original Stage15 five counts on its wrong bbox, then uses ONLY the
pre-registered source sail+boat hull polygons from Stage132. Original counting
thresholds, component bins and known positive/negative fixtures stay fixed.
No keys, BIP39, wallet, address checks, socials, or inferred secret code.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from stage112_corrected_sail_width_progression import variants
from stage132_large_sail_legacy_bbox_audit import POLYGONS
from stage15_semantic_321_counts import band_counts, THRESHOLDS, TARGETS

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE15=ROOT/"analysis"/"runs"/"stage15-semantic-321-counts"/"result.json"
STAGE132=ROOT/"analysis"/"runs"/"stage132-large-sail-roi-coverage"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage158-corrected-large-boat-counts"
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
EXPECTED_BOX=(44,320,359,599)
EROSION=np.ones((5,5),np.uint8)

def source_masks(shape):
    pieces={}
    union=np.zeros(shape,np.uint8)
    for key in ("large_sail","large_hull"):
        if key not in POLYGONS:raise RuntimeError("Missing Stage132 polygon")
        layer=np.zeros(shape,np.uint8)
        cv2.fillPoly(layer,[np.array(POLYGONS[key],np.int32)],255)
        layer=cv2.erode(layer,EROSION,iterations=1)
        pieces[key]=layer>0
        union=np.maximum(union,layer)
    return union>0,pieces

def whiten_outside(a,union):
    x=a.copy()
    x[~union]=255
    return x

def synthetic(kind,union,pieces):
    z=np.full(union.shape,255,np.uint8)
    def dot(x,y,r):
        cv2.circle(z,(x,y),r,0,-1,cv2.LINE_8)
    if kind=="321":
        for x,y in ((230,460),(165,595),(310,630)):dot(x,y,4)
        for x,y in ((220,575),(390,700)):dot(x,y,11)
        z[pieces["large_hull"]]=0
    elif kind=="123":
        dot(230,460,4)
        for x,y in ((220,575),(390,700)):dot(x,y,11)
        for x,y in ((160,670),(350,670),(290,840)):dot(x,y,28)
    elif kind=="negative_two_large":
        z[union]=0
    else:raise ValueError(kind)
    return whiten_outside(z,union)

def calibration(union,pieces):
    results=[]
    for kind in ("321","123","negative_two_large"):
        for fmt,frame in variants(synthetic(kind,union,pieces)).items():
            if fmt not in FORMATS:continue
            z=whiten_outside(frame,union)
            for thr in THRESHOLDS:
                actual=tuple(band_counts(z,thr))
                expect=next((tpl for tpl,label in TARGETS.items() if label==kind),None)
                passed=(actual==expect) if expect else (actual not in TARGETS)
                results.append({"kind":kind,"format":fmt,"threshold":int(thr),
                                "measured":list(actual),"passed":bool(passed)})
    return {"pass":len(results)==60 and all(x["passed"] for x in results),
            "passed":sum(x["passed"] for x in results),
            "cases":len(results),"failures":[x for x in results if not x["passed"]]}

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=EXPECTED_SHA:raise RuntimeError("Canonical PNG changed")
    src=np.asarray(Image.open(SOURCE).convert("L"))
    if src.shape!=(1105,1600):raise RuntimeError("Dimensions changed")
    if tuple(THRESHOLDS)!=(80,110,140,170,200):raise RuntimeError("Stage15 thresholds drifted")
    legacy=json.loads(STAGE15.read_text())
    prior132=json.loads(STAGE132.read_text())
    if prior132.get("decision")!="LEGACY_LARGE_SAILBOAT_BBOX_INCOMPLETE":
        raise RuntimeError("Stage132 defect not verified")
    if list(prior132["legacy_box"])!=list(EXPECTED_BOX):
        raise RuntimeError("Stage132 bbox mismatch")
    original_row=next(x for x in legacy["regions"] if x["region"]=="large_sailboat")
    old_box=list(original_row["bbox"])
    if old_box!=list(EXPECTED_BOX):raise RuntimeError("Stage15 recorded bbox differs")
    x0,y0,x1,y1=old_box
    actual_old=[list(band_counts(src[y0:y1,x0:x1],t)) for t in THRESHOLDS]
    expected_old=[x["small_mid_large"] for x in original_row["counts_by_threshold"]]
    historic_count=sum(int(x==y) for x,y in zip(actual_old,expected_old))
    union,pieces=source_masks(src.shape)
    controls=calibration(union,pieces)
    by_format={}
    for fmt,frame in variants(src).items():
        if fmt not in FORMATS:continue
        filtered=whiten_outside(frame,union)
        rows=[list(band_counts(filtered,t)) for t in THRESHOLDS]
        counts={v:sum(tuple(row)==k for row in rows)
                for k,v in TARGETS.items()}
        by_format[fmt]={"counts_by_threshold":dict(zip(map(str,THRESHOLDS),rows)),
                        "exact_matches":counts,
                        "promoted":max(counts.values())>=4}
    stable=all(x["promoted"] for x in by_format.values())
    verdict=("CONTROL_FAILURE" if not controls["pass"] else
             "HISTORICAL_REPLAY_FAILURE" if historic_count!=5 else
             "CORRECTED_FULL_BOAT_321_OR_123_NEEDS_VISUAL_REVIEW" if stable else
             "NO_STABLE_FULL_LARGE_BOAT_COUNT_CORROBORATION")
    result={"experiment_id":"A11-EXP-158","canonical_sha256":digest,
        "source_polygon_origins":"Stage132 immutable large sail and hull hand annotations",
        "old_stage15_bbox":old_box,"historical_exact_replay":historic_count,
        "historical_replay_total":5,"old_counts":actual_old,
        "fixed_mask_erosion":5,
        "sail_polygon":POLYGONS["large_sail"],"hull_polygon":POLYGONS["large_hull"],
        "sail_ink_mask_area":int(pieces["large_sail"].sum()),
        "hull_ink_mask_area":int(pieces["large_hull"].sum()),
        "thresholds":THRESHOLDS,
        "component_bins":{"small":[3,200],"medium":[201,2000],"large":[2001,None]},
        "synthetic_controls":controls,"results_by_format":by_format,
        "source_promoted_all_four_formats":stable,"decision":verdict,
        "scope_limit":"Only historical Stage15 truncated large-sailboat ROI repaired. Negative cannot prove absence of any arbitrary image encoding. A 321/123 count positive would only warrant source review, not author intent.",
        "safety":"No key, BIP39, wallet, address or external research."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage158 — Full original large boat counts, repairing Stage15 source ROI","",
      f"- Canonical SHA256 verified: **{digest==EXPECTED_SHA}**",
      f"- Old Stage15 large-boat 5-threshold exact replay: **{historic_count}/5**",
      f"- Fixed 321/123/negative synthetic controls: **{controls['passed']}/{controls['cases']}**",
      f"- Source stable 321/123 signature in all 4 formats: **{stable}**",
      f"- Decision: **{verdict}**","",
      "| Threshold | old truncated Stage15 bbox count | corrected source sail+hull count |",
      "|---:|---|---|"]
    for i,t in enumerate(THRESHOLDS):
        lines.append(f"| {t} | {actual_old[i]} | {by_format['original']['counts_by_threshold'][str(t)]} |")
    lines+=["","Full true ship polygons are reused unchanged from Stage132 and do not overlap the missing old right/bottom content. No other Stage15 region was retested; no private keys or messages decoded.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":158,"controls":f"{controls['passed']}/{controls['cases']}",
                      "old_replay":historic_count,"positive":stable,"decision":verdict}))
if __name__=="__main__":main()
