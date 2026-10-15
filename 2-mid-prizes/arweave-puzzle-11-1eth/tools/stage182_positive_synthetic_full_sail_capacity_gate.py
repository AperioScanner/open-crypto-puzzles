#!/usr/bin/env python3
"""A11-EXP-182: Full composite Stage94 gate on an actual KNOWN-256 synthetic sail.

The Stage94 original negative was based on a known false giant-sail ROI.
Stage181 reapplied its original numerical gate to corrected Stage133 source,
revealing a count-compatible 256 scenario blocked by JPEG/resize positional
agreement. Original Stage94 had NEVER demonstrated that a true 256-stroke
synthetic POSITIVE can satisfy that WHOLE gate, rather than count alone.

Only draws frozen Stage94 source-BLIND known 16/64/256 stroke fixtures on
Stage133 fixed sail polygon, uses Stage94 tracker and Stage181 gate unchanged.
Canonical PNG is SHA checked only; NO natural source pixels or secret sequence.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np

from stage94_large_sail_stroke_carrier import (
    synthetic_image,roi_variants,track_across_thresholds,summarize,cross_agreement)
from stage133_corrected_full_sail_strokes import full_sail_roi,SAIL_POLYGON
from stage181_full_sail_stage94_capacity_verdict import evaluate,FORMATS

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
A133=ROOT/"analysis"/"runs"/"stage133-corrected-large-sail-strokes"/"result.json"
A181=ROOT/"analysis"/"runs"/"stage181-full-sail-capacity"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage182-known-256-capacity"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
DRAWS=(16,64,256)

def measure_synthetic(image,mask,reference):
    tracks={}
    values={}
    for name,variant in roi_variants(image).items():
        if name not in FORMATS:continue
        seg=track_across_thresholds(variant,mask)
        tracks[name]=seg
        values[name]=summarize(seg)
    original=tracks["original"]
    matches={name:cross_agreement(original,tracks[name])
             for name in FORMATS if name!="original"}
    return {"by_variant":values,"agreements":matches,
            "full_original_gate":evaluate(values,matches,reference)}

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    stage133=json.loads(A133.read_text())
    stage181=json.loads(A181.read_text())
    source_pixels_reexamined=False
    fake_full=np.full((1105,1600),255,np.uint8)
    patch,mask,roi=full_sail_roi(fake_full)
    calibr=stage133["detector_calibration"]["controls_calibrated"]
    checks={
       "canonical_source_sha_provenance":digest==SHA,
       "Stage181_scientifically_completed":
           stage181["checks_passed"]==stage181["checks_total"]==12
           and stage181["numeric_gate_controls"]["passed"]==3,
       "Stage181_corrected_256_count_compat_but_agreement_fail":
           stage181["decision"]=="FULL_SAIL_COUNT_COMPATIBLE_BUT_ROBUSTNESS_GATE_FAILS"
           and stage181["corrected_full_sail_original_Stage94_gate"]["compatible_target_counts"]==[256],
       "Stage133_known_source_ROI_correction":
           stage133["sha256"]==SHA
           and stage133["decision"]=="STAGE94_CARRIER_NEGATIVE_REQUIRES_REAUDIT"
           and stage133["real_source_control"]["fraction_outside"]>=.65
           and stage133["detector_calibration"]["pass"],
       "Stage133_same_fixed_large_sail_polygon":
           [list(p) for p in SAIL_POLYGON]==stage133["polygon_from_stage132"]
           and roi["mask_pixels"]==stage133["corrected"]["geometry"]["mask_pixels"],
       "source_blind_white_base":int(patch.min())==255 and int(patch.max())==255,
    }
    generated={}
    checks["blank_zero_all_renderings"]=all(
       summarize(track_across_thresholds(v,mask))["classifiable_tracks"]==0
       for fmt,v in roi_variants(np.full(patch.shape,255,np.uint8)).items()
       if fmt in FORMATS)
    for n in DRAWS:
        fixture,drawn=synthetic_image(patch.shape,mask,n)
        measurements=measure_synthetic(fixture,mask,calibr)
        expected={name:calibr[str(n)]["variants"][name]["classifiable_tracks"] for name in FORMATS}
        found={name:measurements["by_variant"][name]["classifiable_tracks"] for name in FORMATS}
        checks[f"known_{n}_drawn_exactly"]=drawn==n
        checks[f"known_{n}_calibration_count_exact_replay"]=expected==found
        generated[str(n)]={"known_drawn_strokes":drawn,
             "synthetic_source_count_replay_expected":expected,
             "synthetic_source_count_replay_found":found,
             "by_variant":measurements["by_variant"],
             "cross_reencoding_agreement":measurements["agreements"],
             "full_original_Stage94_capacity_gate":measurements["full_original_gate"]}
    negative16=generated["16"]["full_original_Stage94_capacity_gate"]
    checks["16_known_negative_rejected_for_both_targets"]=(negative16["all_count_carriers_rejected"]
         and not negative16["compatible_target_counts"] and not negative16["promoted"])
    valid=all(checks.values())
    pos256=generated["256"]["full_original_Stage94_capacity_gate"]
    if not valid:verdict="CONTROL_FAILURE"
    elif pos256["promoted"]:verdict="FULL_STAGE94_GATE_ACCEPTS_KNOWN_TRUE_256_STROKE_FIXTURE"
    else:verdict="FULL_STAGE94_GATE_REJECTS_KNOWN_TRUE_256_STROKE_FIXTURE"
    controls={"pass":valid,"passed":sum(checks.values()),
              "cases":len(checks),"checks":checks}
    result={"experiment_id":"A11-EXP-182",
      "canonical_SHA_provenance_only":digest,
      "original_artwork_pixels_reanalyzed":source_pixels_reexamined,
      "objective":"Check whether Stage94 complete pre-existing binary carrier-capacity/robustness gate can classify TRUE 256 drawn synthetic source, rather than only count-calibrate its detector.",
      "immutable_geometry":"Stage133 eroded Stage132 true full large sail polygon",
      "immutable_stage94_detector":"synthetic_image / roi_variants / track_across_thresholds / summarize / cross_agreement",
      "immutable_stage181_gates":"full original Stage94 evaluate",
      "source_and_generator_checks":controls,
      "frozen_synthetic_families":generated,
      "known_true_64_is_count_compatible_with_256_scenario":
          generated["64"]["full_original_Stage94_capacity_gate"]["carrier_by_size"]["256"]["compatible"],
      "known_true_256_full_gate_promoted":pos256["promoted"],
      "decision":verdict,
      "interpretation_limit":"This measures one stylized synthetic generator and one fixed SOURCE-INDEPENDENT full-sail geometry. Even known 256 stroke calibration success does not certify that a natural pencil drawing encodes 256 bits. If this known-positive fails, the Stage181 real-image cross-format negative is NOT a calibrated exclusion of the 256 target.",
      "safety":"No ordered true image angles, numeric secret candidate, key, BIP39 mnemonic, wallet, Ethereum address compare or external/social search."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage182 — can the OLD full Stage94 gate accept a KNOWN TRUE 256-stroke sail?","",
       f"- Canonical original PNG SHA (no original pixel read): **{digest==SHA}**",
       f"- Unchanged source/positive generator replay and negative checks: **{controls['passed']}/{controls['cases']}**",
       f"- Known true 64-stroke fixture ALSO count-compatible with 256-carrier band: **{result['known_true_64_is_count_compatible_with_256_scenario']}**",
       f"- Known true 256-stroke fixture passes original FULL Stage94 decision: **{pos256['promoted']}**",
       f"- Decision: **{verdict}**","",
       "| Known source-blind fixture | Detector counts by format | Old carrier-compatible sizes | CV | JPEG positional gate | Overall full gate |",
       "|---:|---|---|---:|---|---|"]
    for n in DRAWS:
        a=generated[str(n)]["full_original_Stage94_capacity_gate"]
        lines.append(f"| {n} | {list(a['counts_by_format'].values())} | {a['compatible_target_counts']} | {a['cv']:.5f} | {a['cross_variant_agreement_gate']} | {a['promoted']} |")
    lines+=["","This is an independent POSITIVE-CONTROL sensitivity check of the same full Stage94 numeric rule that Stage181 applied to the corrected natural drawing. It does not infer any original artwork sequence, code or private material. One original synthetic fixture per row; four re-encodings are not independent artwork.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":182,"checks":f"{controls['passed']}/{controls['cases']}",
      "known256_full_promotion":pos256["promoted"],
      "known64_also_256_countcompatible":result["known_true_64_is_count_compatible_with_256_scenario"],
      "decision":verdict}))
if __name__=="__main__":main()
