#!/usr/bin/env python3
"""A11-EXP-183: max-cardinality vs Stage94 GREEDY cross-format stroke matching.

TRUE 256 drawn source-blind synthetic giant sail is already known to FAIL the
complete Stage94 promotion while known64 passes. Test whether the actual
greedy assignment procedure is causal using the EXACT same Stage94 track
sets, 16px distance eligibility, 14deg angle eligibility, no sign filtering,
and one-to-one assignment. No original natural artwork pixels are used.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
import numpy as np

from stage94_large_sail_stroke_carrier import (
    synthetic_image, roi_variants, track_across_thresholds, summarize,
    cross_agreement,angle_diff)
from stage133_corrected_full_sail_strokes import full_sail_roi
from stage181_full_sail_stage94_capacity_verdict import evaluate, FORMATS

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OLD182=ROOT/"analysis"/"runs"/"stage182-known-256-capacity"/"result.json"
OLD133=ROOT/"analysis"/"runs"/"stage133-corrected-large-sail-strokes"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage183-known256-maxmatching"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
DIST_MAX=16.
ANGLE_MAX=14.
PREFERENCE_ANGLE_WEIGHT=1.2
MIN_ANGLE=18.
MAX_ANGLE=86.

def keep_classifiable(tracks):
    return [t for t in tracks if MIN_ANGLE<=abs(t["angle"])<=MAX_ANGLE]

def max_agreement(base_raw,other_raw):
    base=keep_classifiable(base_raw)
    other=keep_classifiable(other_raw)
    if not base:
        return {"matched":0,"matched_fraction":0.,"same_sign_fraction":0.,
                "n_original_tracks":0,"n_other_tracks":len(other),
                "matched_original_indices":[],"matched_other_indices":[]}
    edges=[]
    for source in base:
        choices=[]
        for j,neighbor in enumerate(other):
            distance=math.hypot(source["mx"]-neighbor["mx"],
                                source["my"]-neighbor["my"])
            theta=angle_diff(source["angle"],neighbor["angle"])
            if distance<=DIST_MAX and theta<=ANGLE_MAX:
                score=distance+PREFERENCE_ANGLE_WEIGHT*theta
                choices.append((score,j))
        edges.append([j for _,j in sorted(choices,key=lambda z:(z[0],z[1]))])
    # Exact max cardinality augmenting-path assignment, deterministic
    # favoring same original cost order and candidate ordering.
    owner=[-1]*len(other)
    def augment(i,seen):
        for j in edges[i]:
            if j in seen:continue
            seen.add(j)
            if owner[j]==-1 or augment(owner[j],seen):
                owner[j]=i
                return True
        return False
    for i in range(len(base)):
        augment(i,set())
    assigned=[(i,j) for j,i in enumerate(owner) if i!=-1]
    n=len(assigned)
    signs=sum((base[i]["angle"]>0)==(other[j]["angle"]>0) for i,j in assigned)
    return {"matched":n,"matched_fraction":float(n/len(base)),
            "same_sign_fraction":float(signs/max(1,n)),
            "n_original_tracks":len(base),"n_other_tracks":len(other),
            "matched_original_indices":[i for i,j in assigned],
            "matched_other_indices":[j for i,j in assigned]}

def miniature_controls():
    def obj(x,y,ang):
        return {"mx":x,"my":y,"angle":ang}
    original=[obj(0,0,30),obj(26,0,30)]
    shifted=[obj(12,0,30),obj(-14,0,30)]
    greedy=cross_agreement(original,shifted)
    exact=max_agreement(original,shifted)
    empty=max_agreement([obj(0,0,30)],[obj(100,100,30)])
    checks={
      "greedy_conflict_matched_one_of_two":greedy["matched"]==1,
      "global_reassigns_to_match_two_of_two":exact["matched"]==2
              and exact["same_sign_fraction"]==1,
      "separate_lines_not_force_matched":empty["matched"]==0,
      "global_assignment_not_reusing_other_track_indices":
          len(set(exact["matched_other_indices"]))==exact["matched"]
          and len(set(exact["matched_original_indices"]))==exact["matched"]
    }
    return {"pass":all(checks.values()),"passed":sum(checks.values()),
            "cases":len(checks),"checks":checks}

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    saved=json.loads(OLD182.read_text())
    prev133=json.loads(OLD133.read_text())
    white=np.full((1105,1600),255,np.uint8)
    patch,mask,box=full_sail_roi(white)
    reference=prev133["detector_calibration"]["controls_calibrated"]
    controls=miniature_controls()
    guards={
       "source_sha_provenance_only":sha==SHA,
       "Stage182_known256_real_positive_failure":
          saved["decision"]=="FULL_STAGE94_GATE_REJECTS_KNOWN_TRUE_256_STROKE_FIXTURE"
          and saved["source_and_generator_checks"]["pass"]
          and saved["source_and_generator_checks"]["passed"]==14,
       "Stage133_correct_geometry":box["mask_pixels"]==
          prev133["corrected"]["geometry"]["mask_pixels"]
          and prev133["sha256"]==SHA,
       "known_bipartite_math_controls":controls["pass"],
       "original_matching_constraints_frozen":
          (DIST_MAX,ANGLE_MAX,PREFERENCE_ANGLE_WEIGHT,MIN_ANGLE,MAX_ANGLE)
          ==(16.,14.,1.2,18.,86.)
    }
    outputs={}
    for n in (64,256):
        art,made=synthetic_image(patch.shape,mask,n)
        tracks={}
        readings={}
        for fmt,frame in roi_variants(art).items():
            if fmt not in FORMATS:continue
            tracks[fmt]=track_across_thresholds(frame,mask)
            readings[fmt]=summarize(tracks[fmt])
        compare_greedy={}
        compare_opt={}
        for fmt in FORMATS[1:]:
            compare_greedy[fmt]=cross_agreement(tracks["original"],tracks[fmt])
            compare_opt[fmt]=max_agreement(tracks["original"],tracks[fmt])
        old=saved["frozen_synthetic_families"][str(n)]
        guards[f"known_{n}_drawn_and_counts_unchanged"]=(
            made==n and all(
            readings[fmt]["classifiable_tracks"]==
            old["synthetic_source_count_replay_found"][fmt]
            for fmt in FORMATS))
        guards[f"known_{n}_exact_original_greedy_match_replay"]=all(
            compare_greedy[fmt]["matched"]==
            old["cross_reencoding_agreement"][fmt]["matched"]
            and abs(compare_greedy[fmt]["matched_fraction"]-
                    old["cross_reencoding_agreement"][fmt]["matched_fraction"])<1e-12
            and abs(compare_greedy[fmt]["same_sign_fraction"]-
                    old["cross_reencoding_agreement"][fmt]["same_sign_fraction"])<1e-12
            for fmt in FORMATS[1:])
        guards[f"known_{n}_max_cardinality_at_least_greedy"]=all(
            compare_opt[fmt]["matched"]>=compare_greedy[fmt]["matched"]
            for fmt in FORMATS[1:])
        guards[f"known_{n}_unique_global_matches"]=all(
            len(set(compare_opt[fmt]["matched_original_indices"]))==
            len(set(compare_opt[fmt]["matched_other_indices"]))==
            compare_opt[fmt]["matched"] for fmt in FORMATS[1:])
        gate_greedy=evaluate(readings,compare_greedy,reference)
        gate_global=evaluate(readings,compare_opt,reference)
        outputs[str(n)]={"drawn_known":made,
            "synthetic_gate_greedy":gate_greedy,
            "synthetic_gate_globally_maximal":gate_global,
            "greedy_matches":compare_greedy,
            "maximum_matches":compare_opt}
        guards[f"known_{n}_source_blind_full_gate_original_replay"]=(
          gate_greedy["promoted"]==
          old["full_original_Stage94_capacity_gate"]["promoted"]
        )
    valid=all(guards.values())
    positive=outputs["256"]["synthetic_gate_globally_maximal"]["promoted"]
    old_positive=outputs["256"]["synthetic_gate_greedy"]["promoted"]
    if not valid:decision="CONTROL_FAILURE"
    elif positive and not old_positive:
        decision="GREEDY_MATCHING_WAS_CAUSAL_LIMIT_FOR_KNOWN_256"
    else:
        decision="KNOWN_256_FAILS_FULL_GATE_EVEN_WITH_MAXIMUM_MATCHING"
    report={
       "experiment_id":"A11-EXP-183","source_sha256_provenance_only":sha,
       "original_artwork_pixels_reexamined":False,
       "question":"Could greedy candidate allocation rather than true image transformation loss explain why the Stage94 original full-gate rejects a known true256-stroke synthetic sail?",
       "fixed_track_eligibility":{"distance_px":DIST_MAX,
          "angle_deg":ANGLE_MAX,"preference_d_plus_w_angle":PREFERENCE_ANGLE_WEIGHT,
          "angle_magnitude_min":MIN_ANGLE,"angle_magnitude_max":MAX_ANGLE},
       "known_answer_matching_controls":controls,
       "precommitted_source_and_math_guards":guards,
       "guards_passed":sum(guards.values()),"guards_total":len(guards),
       "known_synthetic_64_and_256_results":outputs,
       "decision":decision,
       "scope_limit":"This tests only an assignment-algorithm defect using unaltered known positive synthetic source. Max matching can increase pair counts but does not imply source art carries 256 coded symbols, and cannot be used on natural image without precommitted separate study and true-positive gate.",
       "safety":"No private key, address, mnemonic, wallet, EVM verification, OCR or outside/social research."}
    (OUT/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    lines=["# Stage183 — greedy vs mathematically maximal matching for known 256 artificial sail","",
       f"- Canonical PNG SHA provenance only: **{sha==SHA}**",
       f"- Structural/positive fixture exact replay: **{sum(guards.values())}/{len(guards)}**",
       f"- Known two-to-two reassignment controls: **{controls['passed']}/{controls['cases']}**",
       f"- Known 256 full gate passes with old greedy: **{old_positive}**",
       f"- Known 256 full gate passes with globally maximum pairing: **{positive}**",
       f"- Decision: **{decision}**","",
       "| Fixture | Image transform | Old greedy matches | Maximum strict matches | Max fraction | Original min fraction .55 |",
       "|---:|---|---:|---:|---:|---|"]
    for n in (64,256):
        for fmt in FORMATS[1:]:
            g=outputs[str(n)]["greedy_matches"][fmt]
            m=outputs[str(n)]["maximum_matches"][fmt]
            lines.append(f"| {n} | {fmt} | {g['matched']} | {m['matched']} | {m['matched_fraction']:.4f} | {m['matched_fraction']>=.55} |")
    lines+=["","No source natural-image segments were matched or re-labeled in this stage. All thresholds, geometry and 256-drawn positive source strokes remain fixed, and the original Stage181 source negative is NOT reinterpreted unless a separately justified calibration and original-image study exists.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":183,"controls":f"{sum(guards.values())}/{len(guards)}",
       "known256_greedy_pass":old_positive,
       "known256_max_pass":positive,"decision":decision}))
if __name__=="__main__":main()
