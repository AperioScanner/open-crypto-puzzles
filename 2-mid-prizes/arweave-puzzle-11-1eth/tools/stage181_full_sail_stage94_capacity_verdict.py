#!/usr/bin/env python3
"""A11-EXP-181: correct the ORIGINAL Stage94 capacity decision with Stage133
full giant sail data. Pure archived counting/geometry QA, no image pixel reads.
It does NOT extract an ordered stroke sequence, key, address or secret.
All conditions preregistered in analysis/STAGE_QUEUE.md.
"""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"clues/arweave-puzzle-11.png"
OLD=ROOT/"analysis/runs/stage94-large-sail-stroke-carrier/result.json"
CORRECTED=ROOT/"analysis/runs/stage133-corrected-large-sail-strokes/result.json"
SOURCE_ROI=ROOT/"analysis/runs/stage132-large-sail-roi-coverage/result.json"
CODE94=ROOT/"tools/stage94_large_sail_stroke_carrier.py"
OUT=ROOT/"analysis/runs/stage181-full-sail-capacity"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
TARGET_COUNTS=((64,8),(256,16))
MINORITY=.20
SEPARATION=35.
MIN_AGREEMENT=.55
MIN_SAME_SIGN=.90
MAX_CV=.15

def evaluate(summaries,agreements,calibration):
    counts=[int(summaries[k]["classifiable_tracks"]) for k in FORMATS]
    mean=sum(counts)/4
    cv=(math.sqrt(sum((x-mean)**2 for x in counts)/4)/mean) if mean else math.inf
    low,high=min(counts),max(counts)
    carrier={}
    countcompatible=[]
    for n,reported_tol in TARGET_COUNTS:
        calib=calibration[str(n)]
        nmin=int(calib["min_detected"]);nmax=int(calib["max_detected"])
        bound=(max(1,math.floor(nmin*.5)),math.ceil(nmax*1.5))
        reject=high < .5*nmin
        compat=all(bound[0]<=x<=bound[1] for x in counts)
        carrier[str(n)]={"synthetic_min":nmin,"synthetic_max":nmax,
            "source_min":low,"source_max":high,
            "compatibility_band":list(bound),
            "compatible":bool(compat),"rejected_by_count":bool(reject)}
        if compat:countcompatible.append(n)
    minority_ok=all(summaries[k]["minority_fraction"]>=MINORITY
                    and summaries[k]["orientation_median_separation_deg"]>=SEPARATION
                    for k in FORMATS)
    agreement_ok=all(agreements[k]["matched_fraction"]>=MIN_AGREEMENT and
                     agreements[k]["same_sign_fraction"]>=MIN_SAME_SIGN
                     for k in FORMATS if k!="original")
    all_rejected=all(c["rejected_by_count"] for c in carrier.values())
    promoted=bool(not all_rejected and bool(countcompatible)
                  and cv<=MAX_CV and minority_ok and agreement_ok)
    return {"counts_by_format":dict(zip(FORMATS,counts)),
        "cv":cv,"minority_orientation_gate":minority_ok,
        "cross_variant_agreement_gate":agreement_ok,
        "all_count_carriers_rejected":all_rejected,
        "carrier_by_size":carrier,"compatible_target_counts":countcompatible,
        "promoted":promoted}

def numeric_controls():
    sample={"classifiable_tracks":0,"minority_fraction":.40,
             "orientation_median_separation_deg":115.}
    ag={name:{"matched_fraction":.8,"same_sign_fraction":1.} for name in FORMATS[1:]}
    calibr={"64":{"min_detected":42,"max_detected":51},
            "256":{"min_detected":64,"max_detected":97}}
    def case(counts,alter=None):
        ss={fmt:{**sample,"classifiable_tracks":count}
            for fmt,count in zip(FORMATS,counts)}
        gg={k:v.copy() for k,v in ag.items()}
        if alter is not None:gg["down75_up"]["matched_fraction"]=alter
        return evaluate(ss,gg,calibr)
    positive=case((72,78,81,75))
    negative=case((2,3,4,3))
    weak=case((72,78,81,75),.54)
    checks={
       "positive_mock_composite_promotes":positive["promoted"],
       "negative_mock_two_sizes_rejected":negative["all_count_carriers_rejected"] and not negative["promoted"],
       "one_weak_format_blocks_promotion":not weak["promoted"] and not weak["cross_variant_agreement_gate"],
    }
    return {"pass":all(checks.values()),"passed":sum(checks.values()),
            "cases":len(checks),"checks":checks}

def main():
    sha=hashlib.sha256(SRC.read_bytes()).hexdigest()
    old=json.loads(OLD.read_text())
    fixed=json.loads(CORRECTED.read_text())
    roi=json.loads(SOURCE_ROI.read_text())
    source=CODE94.read_text().replace(" ","")
    cal=fixed["detector_calibration"]["controls_calibrated"]
    checks={
      "canonical_sha_provenance":sha==SHA==fixed["sha256"],
      "prior_Stage132_confirmed_defect":roi["decision"]=="LEGACY_LARGE_SAILBOAT_BBOX_INCOMPLETE",
      "Stage133_valid_corrected_ROI":fixed["decision"]=="STAGE94_CARRIER_NEGATIVE_REQUIRES_REAUDIT"
           and fixed["real_source_control"]["source_pass"]
           and fixed["real_source_control"]["fraction_outside"]>=.65,
      "Stage133_known_count_controls":fixed["detector_calibration"]["pass"]
           and fixed["detector_calibration"]["blank_tracks"]==0
           and fixed["detector_calibration"]["synthetic_16_min"]>=6
           and fixed["detector_calibration"]["synthetic_64_min"]>=15
           and fixed["detector_calibration"]["synthetic_256_min"]>=64,
      "Stage94_original_target_constants":"TARGET_COUNTS=((64,8),(256,16))" in source
          and "THRESHOLDS=(110,135,160,185,210)" in source,
      "Stage94_original_promotion_gates":
          "matched_fraction" in source and "same_sign_fraction" in source
          and "cv<=0.15" in source and "minority_fraction" in source
          and "0.55" in source and "0.90" in source,
      "Stage133_old_summary_matches_Stage94_raw":all(
          fixed["old"]["variant_summaries"][k]==old["variants"][k] for k in FORMATS),
      "Stage133_old_agreement_matches_Stage94_raw":
          fixed["old"]["agreement"]==old["cross_variant_agreement"],
      "Stage133_corrected_full_sail_count_all_variants":
          [fixed["corrected"]["variant_summaries"][x]["classifiable_tracks"] for x in FORMATS]
          ==[80,76,90,77],
      "calibration_records_both_original_carrier_sizes":all(str(n) in cal for n,_ in TARGET_COUNTS)
    }
    numeric=numeric_controls()
    old_eval=evaluate(old["variants"],old["cross_variant_agreement"],
                      old["synthetic_calibration"]["controls"])
    checks["exact_archived_old_carrier_gate_replay"]=bool(
        old_eval["promoted"]==old["promoted"]
        and old_eval["carrier_by_size"]=={
          k:{"synthetic_min":v["control_min_detected"],
             "synthetic_max":v["control_max_detected"],
             "source_min":v["target_detected_min"],
             "source_max":v["target_detected_max"],
             "compatibility_band":v["compatibility_band"],
             "compatible":v["compatible"],
             "rejected_by_count":v["rejected_by_count"]}
          for k,v in old["carrier_count_decisions"].items()}
        and old_eval["all_count_carriers_rejected"]==
          old["all_canonical_one_stroke_carriers_rejected"]
        and old_eval["compatible_target_counts"]==old["compatible_target_counts"]
        and old_eval["minority_orientation_gate"]==old["orientation_structure_ok"]
        and old_eval["cross_variant_agreement_gate"]==old["cross_variant_agreement_ok"]
        and abs(old_eval["cv"]-old["classifiable_count_cv"])<=1e-8
    )
    checks["three_pure_numeric_positive_negative_cases"]=numeric["pass"]
    if all(checks.values()):
        result=evaluate(fixed["corrected"]["variant_summaries"],
                        fixed["corrected"]["agreement"],cal)
        if result["promoted"]:
            decision="FULL_SAIL_CARRIER_GATE_PASSES_REQUIRES_INDEPENDENT_REVIEW"
        elif result["compatible_target_counts"]:
            decision="FULL_SAIL_COUNT_COMPATIBLE_BUT_ROBUSTNESS_GATE_FAILS"
        elif not result["compatible_target_counts"]:
            decision="CORRECTED_FULL_SAIL_CARRIERS_NOT_COUNT_COMPATIBLE"
        else:
            decision="INCONCLUSIVE"
    else:
        result={}
        decision="CONTROL_FAILURE"
    data={"experiment_id":"A11-EXP-181",
          "original_SHA256_provenance_only":sha,
          "original_artwork_pixels_reanalyzed":False,
          "hypothesis":"Stage94's old 64/256 capacity exclusion was specific to a wrong small ROI, but the source-corrected full-sail capacity GATES were never re-evaluated as a whole.",
          "source_code_and_archived_provenance_checks":checks,
          "checks_passed":sum(checks.values()),"checks_total":len(checks),
          "numeric_gate_controls":numeric,"original_Stage94_gate_replay":old_eval,
          "corrected_full_sail_original_Stage94_gate":result,
          "decision":decision,
          "scope_limit":"Only detection-capacity and repeatability of two previously REGISTERED count families is assessed, NOT a 256-bit extraction. A 256-drawn synthetic often collapses to fewer detected graphite tracks; compatibility is not proof of a natural or encoded 256-stroke arrangement. JPEGs are one artwork, not independent replicates.",
          "safety":"No private key, mnemonic, BIP39 word, Ethereum address, wallet or external/social work."}
    (OUT/"result.json").write_text(json.dumps(data,indent=2)+"\n")
    lines=["# Stage181 — original Stage94 capacity gate re-audited on COMPLETE genuine sail","",
       f"- Canonical source checksum provenance: **{sha==SHA}**",
       f"- Source/code/archived historic replay checks: **{sum(checks.values())}/{len(checks)}**",
       f"- Synthetic pure numeric gates: **{numeric['passed']}/{numeric['cases']}**",
       f"- Scientific decision: **{decision}**",""]
    if result:
        lines +=[
            f"- Full sail counts (original/JPEG85/JPEG70/resize): **{list(result['counts_by_format'].values())}**",
            f"- Full sail count-compatible old target sizes: **{result['compatible_target_counts']}**",
            f"- Minority orientation gate: **{result['minority_orientation_gate']}**",
            f"- JPEG positional same-sign agreement gate: **{result['cross_variant_agreement_gate']}**",
            f"- Full unmodified Stage94 promotion: **{result['promoted']}**","",
            "| Fixed old target size | Full-sail count band | Count compatible | Conservative count-rejected |",
            "|---:|---|---|---|"
        ]
        for target,_ in TARGET_COUNTS:
            v=result["carrier_by_size"][str(target)]
            lines.append(f"| {target} | {v['compatibility_band']} | {v['compatible']} | {v['rejected_by_count']} |")
        lines+=["","The weakness is the unchanged Stage94 resized/original positional agreement gate. A 256-carrier synthetic SOURCE-BLIND full-gate calibration is required before this can be interpreted as a reliable exclusion of such a carrier. Do not decode any target-orientation sequence.",""]
    lines+=["","Archived Stage94 negative and Stage133 corrected-source evidence are unchanged. No secret data or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":181,"checks":f"{sum(checks.values())}/{len(checks)}",
          "numeric":f"{numeric['passed']}/{numeric['cases']}",
          "compatible":result.get("compatible_target_counts"),
          "agreement":result.get("cross_variant_agreement_gate"),
          "decision":decision}))
if __name__=="__main__":main()
