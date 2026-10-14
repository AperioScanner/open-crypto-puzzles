#!/usr/bin/env python3
"""A11-EXP-165: Stage61 original width-vs-next-gap formula on corrected true sail bases.

This does not invent a new width detector. It substitutes the fixed hand-
annotated original FULL SAIL OUTLINE foot widths from Stage153 for the bad
legacy component widths and uses the independently established 5 true sail
centers from Stage112. Exactly 120 width permutations, unaltered Stage88
Pearson absolute-correlation function. No keys or wallet access.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path

import numpy as np

from stage153_under_pier_triangle_junctions import TRIANGLES
from stage88_superbatch_survivor_replication import exact_width_gap,safe_corr

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE112=ROOT/"analysis"/"runs"/"stage112-corrected-sail-width-progression"/"result.json"
STAGE152=ROOT/"analysis"/"runs"/"stage152-under-pier-closed-outline"/"result.json"
STAGE163=ROOT/"analysis"/"runs"/"stage163-superbatch-source-provenance"/"result.json"
STAGE164=ROOT/"analysis"/"runs"/"stage164-stage112-sail-coverage"/"result.json"
STAGE61=ROOT/"analysis"/"runs"/"superbatch-37-87"/"exp_061"/"result.json"
STAGE88=ROOT/"analysis"/"runs"/"stage88-superbatch-survivor-replication"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage165-corrected-sail-width-gap"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
SITES={k:v for k,v in TRIANGLES.items() if k.startswith("sail")}
FIXED_FULL_BASE_WIDTHS=(70,76,88,84,94)
SIGNED_CORRELATION_MIN_ABS=0.85

def fixed_base_widths():
    widths=[]
    for points in SITES.values():
        apex,left,right=points
        widths.append(abs(int(right[0])-int(left[0])))
    return widths

def controls(original_centers):
    gaps=np.diff(original_centers)
    positives=[106.,134.,90.,118.,50.]
    negatives=[30.,30.,30.,30.,30.]
    positive=exact_width_gap(positives,original_centers)
    negative=exact_width_gap(negatives,original_centers)
    expected_gap=list(map(float,[106,134,90,118]))
    checks={
       "centers_independent_known_gaps":list(map(float,gaps))==expected_gap,
       "positive_120_permutations":positive["exact_permutations"]==120,
       "positive_high_r":positive["abs_correlation"]>=.999,
       "positive_significant":positive["exact_p"]<=.05,
       "constant_null_120_permutations":negative["exact_permutations"]==120,
       "constant_null_zero_r":negative["abs_correlation"]==0,
       "constant_null_exact_p_one":negative["exact_p"]==1.0
    }
    return {"pass":all(checks.values()),"passed":sum(checks.values()),
            "cases":len(checks),"checks":checks,
            "positive":positive,"negative":negative}

def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=SHA:raise RuntimeError("Canonical source hash changed")
    s112=json.loads(STAGE112.read_text())
    s152=json.loads(STAGE152.read_text())
    s163=json.loads(STAGE163.read_text())
    s164=json.loads(STAGE164.read_text())
    s61=json.loads(STAGE61.read_text())
    s88=json.loads(STAGE88.read_text())
    source_checks={
       "canonical_SHA":sha==SHA,
       "Stage152_true_five_outlines":s152["real_sail_outlines_stable"]==5,
       "Stage152_72_calibration":s152["control"]["pass"] and s152["control"]["passed_cases"]==72,
       "Stage163_legacy_superbatch_scope":s163["controls_pass"] and s163["decision"]=="VERIFIED_LEGACY_SUPERBATCH_OBJECT_CROP_SCOPE_DEFECT",
       "Stage164_width_roi_defect":s164["decision"]=="STAGE112_UPPER_SAIL_CROPS_MATERIALLY_INCOMPLETE"
                   and s164["materially_incomplete_true_sails"]>=3,
       "Stage164_synthetic_controls":s164["synthetic_controls"]["pass"] and s164["synthetic_controls"]["passed"]==40,
       "Stage61_past_nominal":s61["stage"]==61 and s61["method"]=="small_sails_permutation:width_gapcorr",
       "Stage88_historical_rejected":s88["confirmed_count"]==0,
       "Stage112_five_correct_centers":s112["detected_centers"]["original"]==[1042,1148,1282,1372,1490]
    }
    widths=fixed_base_widths()
    if widths!=list(FIXED_FULL_BASE_WIDTHS):raise RuntimeError("Frozen source polygon widths changed")
    center_ref=s112["detected_centers"]["original"]
    control=controls(center_ref)
    signed=[]
    per={}
    for fmt in FORMATS:
        centers=s112["detected_centers"][fmt]
        if len(centers)!=5:raise RuntimeError("Missing sail reference centers")
        drift=max(abs(float(a)-float(b)) for a,b in zip(centers,center_ref))
        res=exact_width_gap(widths,centers)
        sg=float(safe_corr(widths[:4],np.diff(centers)))
        signed.append(sg)
        per[fmt]={**res,"signed_correlation":sg,"max_center_drift_vs_original":drift}
        source_checks["Stage112_center_drift_"+fmt]=(drift<=8)
    enough=all(source_checks.values()) and control["pass"]
    allp=[per[fmt]["exact_p"] for fmt in FORMATS]
    positive=all(p<=.05 and per[fmt]["abs_correlation"]>=SIGNED_CORRELATION_MIN_ABS
                 for fmt,p in zip(FORMATS,allp))
    same_sign=all(s>0 for s in signed) or all(s<0 for s in signed)
    if not enough:
        verdict="CONTROL_FAILURE"
    elif positive and same_sign:
        verdict="CORRECTED_FULL_SAIL_BASE_WIDTH_GAP_REQUIRES_VISUAL_REVIEW"
    elif all(p>.05 for p in allp):
        verdict="NO_SIGNIFICANT_TRUE_SAIL_BASE_WIDTH_GAP_RELATION"
    else:
        verdict="CORRECTED_BASE_WIDTH_GAP_INCONCLUSIVE"
    result={
      "experiment_id":"A11-EXP-165","canonical_SHA":sha,
      "hypothesis":"Full annotated genuine sail BASE outline widths may retain prior Stage61 correlation with the distance to the next true sail center.",
      "width_data_type":"Stage153 existing manually annotated full-sail base x endpoints, NOT remeasured raster widths",
      "fixed_true_sail_widths":widths,
      "source_guards":source_checks,
      "synthetic_and_permutation_controls":control,
      "old_superbatch_stage61_nominal_p":s61["p_value"],
      "Stage88_old_identity_replication":next(z for z in s88["candidates"] if z["candidate"]=="A11-EXP-061"),
      "per_variant":per,
      "decision":verdict,
      "scope_limit":"An exact p for this particular five pre-annotated sail base-width vector does not imply author intention. JPEG variants reuse the same frozen base polygon widths (not independent samples). No other width estimate or sail-gap code has been tested here.",
      "safety":"Original image content only via previously archived visual geometry and SHA; no mnemonic, key, wallet or address verification."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
      "# Stage165 — Stage61 fixed true-sail full BASE outline width/gap retest","",
      f"- Canonical image hash: **{sha==SHA}**",
      f"- Prior known-source and geometry guards: **{sum(source_checks.values())}/{len(source_checks)}**",
      f"- Positive/negative permutation controls: **{control['passed']}/{control['cases']}**",
      f"- Corrected annotated five full-sail BASE widths: **{widths}**",
      f"- Stage61 old incomplete sail-set nominal p: **{s61['p_value']:.6f}**",
      f"- Corrected true-base width/gap joint result: **{verdict}**","",
      "| Variant | Correct real centers | Width-gap abs Pearson | Exact 5! p |",
      "|---|---|---:|---:|"]
    for fmt in FORMATS:
        v=per[fmt]
        lines.append(f"| {fmt} | {v['centers']} | {v['abs_correlation']:.4f} | {v['exact_p']:.6f} |")
    lines+=["","This exact permutation statistic tests only one preregistered visible base-width correlation. The Stage153 endpoints are fixed prior annotations; source re-encodings do not validate independent new outlines. No 321 interpretation, decoded symbol, secret key or wallet operation.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":165,"source_guards":f"{sum(source_checks.values())}/{len(source_checks)}",
           "fixture_controls":f"{control['passed']}/{control['cases']}",
           "p_original":per["original"]["exact_p"],"decision":verdict}))
if __name__=="__main__":
    main()
