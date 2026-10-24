#!/usr/bin/env python3
"""Stage184: frozen synthetic source-blind full-scene versus ROI-only transform calibration."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from stage94_large_sail_stroke_carrier import synthetic_image,roi_variants,track_across_thresholds,summarize,cross_agreement
from stage133_corrected_full_sail_strokes import full_sail_roi
from stage112_corrected_sail_width_progression import variants as full_variants
from stage181_full_sail_stage94_capacity_verdict import evaluate,FORMATS
from stage183_known256_maximum_match_audit import max_agreement
ROOT=Path(__file__).resolve().parents[1]
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
OUT=ROOT/"analysis/runs/stage184-full-canvas-transform-calibration"
OUT.mkdir(parents=True,exist_ok=True)
def measure(views,mask,reference):
    tracks={k:track_across_thresholds(views[k],mask) for k in FORMATS}
    summaries={k:summarize(tracks[k]) for k in FORMATS}
    greedy={k:cross_agreement(tracks["original"],tracks[k]) for k in FORMATS[1:]}
    optimal={k:max_agreement(tracks["original"],tracks[k]) for k in FORMATS[1:]}
    return {"counts":{k:summaries[k]["classifiable_tracks"] for k in FORMATS},
      "greedy_matches":{k:{"n":greedy[k]["matched"],"fraction":greedy[k]["matched_fraction"]} for k in FORMATS[1:]},
      "optimal_matches":{k:{"n":optimal[k]["matched"],"fraction":optimal[k]["matched_fraction"]} for k in FORMATS[1:]},
      "greedy_gate":evaluate(summaries,greedy,reference),
      "optimal_gate":evaluate(summaries,optimal,reference)}
def main():
    sha=hashlib.sha256((ROOT/"clues/arweave-puzzle-11.png").read_bytes()).hexdigest()
    prev182=json.loads((ROOT/"analysis/runs/stage182-known-256-capacity/result.json").read_text())
    prev183=json.loads((ROOT/"analysis/runs/stage183-known256-maxmatching/result.json").read_text())
    prev133=json.loads((ROOT/"analysis/runs/stage133-corrected-large-sail-strokes/result.json").read_text())
    blank=np.full((1105,1600),255,np.uint8)
    patch,mask,geom=full_sail_roi(blank)
    x0,y0,x1,y1=geom["box"]
    reference=prev133["detector_calibration"]["controls_calibrated"]
    checks={
      "canonical_sha":sha==SHA,
      "stage182_source_blind_known_controls":prev182["source_and_generator_checks"]["passed"]==prev182["source_and_generator_checks"]["cases"]==14 and prev182["decision"]=="FULL_STAGE94_GATE_REJECTS_KNOWN_TRUE_256_STROKE_FIXTURE",
      "stage183_optimal_controls":prev183["guards_passed"]==prev183["guards_total"]==15 and prev183["known_answer_matching_controls"]["passed"]==4 and prev183["decision"]=="KNOWN_256_FAILS_FULL_GATE_EVEN_WITH_MAXIMUM_MATCHING",
      "stage133_geometry":geom["mask_pixels"]==prev133["corrected"]["geometry"]["mask_pixels"] and prev133["sha256"]==SHA,
      "whole_scene_blank":bool(np.all(blank==255)),
      "full_scene_blank_zero":all(summarize(track_across_thresholds(full_sail_roi(v)[0],mask))["classifiable_tracks"]==0 for v in full_variants(blank).values())
    }
    outputs={}
    for count in (16,64,256):
        art,made=synthetic_image(patch.shape,mask,count)
        scene=blank.copy()
        scene[y0:y1,x0:x1]=art
        views_local=roi_variants(art)
        views_global={k:full_sail_roi(v)[0] for k,v in full_variants(scene).items()}
        checks[f"{count}_drawn_exact"]=made==count
        checks[f"{count}_original_patches_identical"]=bool(np.array_equal(views_local["original"],views_global["original"]))
        lo=measure(views_local,mask,reference)
        gl=measure(views_global,mask,reference)
        old=prev182["frozen_synthetic_families"][str(count)]
        checks[f"{count}_local_counts_replay"]=lo["counts"]==old["synthetic_source_count_replay_found"]
        checks[f"{count}_local_gate_replay"]=lo["greedy_gate"]["promoted"]==old["full_original_Stage94_capacity_gate"]["promoted"]
        if count in (64,256):
            checks[f"{count}_local_matching_replay"]=all(
              lo["greedy_matches"][k]["n"]==old["cross_reencoding_agreement"][k]["matched"]
              and lo["optimal_matches"][k]["n"]==prev183["known_synthetic_64_and_256_results"][str(count)]["maximum_matches"][k]["matched"]
              for k in FORMATS[1:])
        outputs[str(count)]={"known_drawn":made,"local":lo,"full_canvas":gl,
          "frame_effect":{k:gl["greedy_matches"][k]["n"]-lo["greedy_matches"][k]["n"] for k in FORMATS[1:]}}
    valid=all(checks.values())
    n16=outputs["16"]["full_canvas"]["greedy_gate"]
    n64=outputs["64"]["full_canvas"]["greedy_gate"]
    n256=outputs["256"]["full_canvas"]["greedy_gate"]
    neg16=not n16["compatible_target_counts"] and not n16["promoted"]
    if not valid: decision="CONTROL_FAILURE"
    elif not neg16:decision="CALIBRATION_FAILURE"
    elif not n64["promoted"]:decision="INSUFFICIENT_GLOBAL_KNOWN64_CONTROL"
    elif n256["promoted"] and not outputs["256"]["local"]["greedy_gate"]["promoted"]:
        decision="FULL_FRAME_CALIBRATION_FIXES_KNOWN256_FALSE_NEGATIVE"
    elif outputs["256"]["full_canvas"]["optimal_gate"]["promoted"]:
        decision="MAX_MATCH_ONLY_NOT_ORIGINAL_GATE"
    else:decision="GLOBAL_FRAME_DOES_NOT_FIX_KNOWN256_FALSE_NEGATIVE"
    result={"experiment_id":"A11-EXP-184","source_sha_provenance_only":sha,
      "source_artwork_pixels_reexamined":False,
      "hypothesis":"Synthetic full-canvas transform frame is necessary to reproduce source image full-frame treatment",
      "full_canvas_geometry":geom,"controls":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),
      "known16_global_count_negative":neg16,"known64_global_positive":n64["promoted"],"known256_global_positive":n256["promoted"],
      "fixtures":outputs,"decision":decision,
      "scope":"Identical artificial image content; transform frame only; no code, keys, addresses, wallets or source image stroke sequence."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage184 — fixed synthetic full-canvas transform frame check","",
      f"- Checks: **{sum(checks.values())}/{len(checks)}**",
      f"- Global n16 valid negative: **{neg16}**",
      f"- Global n64 positive full gate: **{n64['promoted']}**",
      f"- Global n256 positive full gate: **{n256['promoted']}**",
      f"- Decision: **{decision}**","",
      "| Known marks | Mode | Original | JPEG85 | JPEG70 | Resize | Resize matched original | Full old gate |",
      "|---:|---|---:|---:|---:|---:|---:|---|"]
    for count in (16,64,256):
        for label,key in (("ROI-local","local"),("Full-canvas","full_canvas")):
            v=outputs[str(count)][key]; c=v["counts"]; m=v["greedy_matches"]["down75_up"]
            lines.append(f"| {count} | {label} | {c['original']} | {c['jpeg85']} | {c['jpeg70']} | {c['down75_up']} | {m['n']}/{c['original']} ({m['fraction']:.4f}) | {v['greedy_gate']['promoted']} |")
    lines+=["","No natural image pixels or ordered strokes were examined. Four encodings derive from the same artificial image. A successful positive fixture is not evidence of an intentional message in the real puzzle."]
    (OUT/"REPORT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"stage":184,"controls":f"{sum(checks.values())}/{len(checks)}","known64_global_pass":n64["promoted"],"known256_global_pass":n256["promoted"],"decision":decision}))
    if not valid:raise SystemExit("Stage184 QA controls failed")
if __name__=="__main__":main()
