#!/usr/bin/env python3
"""Stage184-R: source-blind out-of-sample replication of Stage184 combined instrument.

All criteria, count classes, families and seeds are preregistered in STAGE_QUEUE.
No natural artwork pixels are inspected; only SHA256 of original file is read.
No ordered sign data, address comparisons, wallet access or secret material.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np

from stage94_large_sail_stroke_carrier import synthetic_image, track_across_thresholds, summarize
from stage133_corrected_full_sail_strokes import full_sail_roi
from stage112_corrected_sail_width_progression import variants as full_variants
from stage181_full_sail_stage94_capacity_verdict import FORMATS
from stage184_full_canvas_transform_calibration import measure

ROOT = Path(__file__).resolve().parents[1]
SHA = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
OUT = ROOT / "analysis/runs/stage184r-synthetic-holdout"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = (184101,184102,184103,184104)
FAMILIES = ("uniform","pencil")
# Explicitly frozen line-center sampling grid and safe endpoints.
GRID_STEP = 12
SAFE_KERNEL = (25,19)  # rows x columns
MIN_256_POSITIVE = 7
MAX_256_FALSE_POSITIVE = 1

def family_fixture(mask, count, family, seed):
    """Return new 1px-AA known-drawn scene using no original pixels."""
    if family not in FAMILIES or count not in (16,64,128,256):
        raise ValueError("unregistered fixture")
    h,w = mask.shape
    safe = cv2.erode(mask.astype(np.uint8),
                     np.ones(SAFE_KERNEL, np.uint8), iterations=1)
    rng = np.random.default_rng(seed + count*997 + (0 if family == "uniform" else 100000))
    x_offset = int(seed % 4)
    y_offset = int((seed//7) % 4)
    positions = []
    for row, y in enumerate(range(12+y_offset, h-12, GRID_STEP)):
        stagger = 6 if family == "pencil" and row % 2 == 1 else 0
        for x in range(10+x_offset, w-10-stagger, GRID_STEP):
            xx=x+stagger
            if safe[y,xx]>0:
                positions.append((xx,y))
    if len(positions)<count:
        raise RuntimeError("insufficient predeclared eligible grid positions")
    order = rng.permutation(len(positions))[:count]
    im = np.full(mask.shape,255,np.uint8)
    endpoints_valid = True
    for i, j in enumerate(order):
        x,y = positions[int(j)]
        if family=="uniform":
            dx,dy = 5,7
            sign = 1 if i%2==0 else -1
            ink = 0
        else:
            dx=int(rng.integers(5,8))
            dy=int(rng.integers(7,11))
            sign=1 if int(rng.integers(0,2))==1 else -1
            ink=int((0,35,70)[int(rng.integers(0,3))])
        p1=(x-dx,y-sign*dy)
        p2=(x+dx,y+sign*dy)
        valid = (0<=p1[0]<w and 0<=p1[1]<h
                 and 0<=p2[0]<w and 0<=p2[1]<h
                 and mask[p1[1],p1[0]]>0 and mask[p2[1],p2[0]]>0)
        endpoints_valid = endpoints_valid and valid
        if not valid:
            raise RuntimeError("synthetic endpoint outside preregistered mask")
        cv2.line(im,p1,p2,ink,1,cv2.LINE_AA)
    centers=[positions[int(j)] for j in order]
    return im, {
        "commanded_count":len(centers),
        "unique_centers":len(set(centers))==count,
        "endpoints_inside_mask":endpoints_valid,
        "eligible_positions":len(positions),
        "nonwhite_ink_pixels":int(np.count_nonzero(im<255))
    }

def whole_views(art, blank, box):
    x0,y0,x1,y1 = box
    scene=blank.copy()
    scene[y0:y1,x0:x1] = art
    views={k:full_sail_roi(v)[0] for k,v in full_variants(scene).items() if k in FORMATS}
    return views

def main():
    digest=hashlib.sha256((ROOT/"clues/arweave-puzzle-11.png").read_bytes()).hexdigest()
    a133=json.loads((ROOT/"analysis/runs/stage133-corrected-large-sail-strokes/result.json").read_text())
    a184=json.loads((ROOT/"analysis/runs/stage184-full-canvas-transform-calibration/result.json").read_text())
    blank=np.full((1105,1600),255,np.uint8)
    patch,mask,geometry=full_sail_roi(blank)
    reference=a133["detector_calibration"]["controls_calibrated"]
    box=geometry["box"]
    checks={
        "canonical_sha256_provenance_only":digest==SHA,
        "stage184_frozen_valid":a184["decision"]=="MAX_MATCH_ONLY_NOT_ORIGINAL_GATE" and a184["checks_passed"]==a184["checks_total"]==20,
        "stage133_mask_matches_archive":geometry["mask_pixels"]==a133["corrected"]["geometry"]["mask_pixels"] and box==a133["corrected"]["geometry"]["box"],
        "white_scene_unmodified":bool(np.all(blank==255)),
        "blank_zero_all_4_full_canvas_formats":all(
            summarize(track_across_thresholds(full_sail_roi(v)[0],mask))["classifiable_tracks"]==0
            for k,v in full_variants(blank).items() if k in FORMATS),
    }
    baseline={}
    for n in (16,64,256):
        known,made=synthetic_image(patch.shape,mask,n)
        views=whole_views(known,blank,box)
        res=measure(views,mask,reference)
        saved=a184["fixtures"][str(n)]["full_canvas"]
        checks[f"frozen_{n}_drawn_exact"]=made==n
        checks[f"frozen_{n}_original_crop_identical"]=bool(np.array_equal(known,views["original"]))
        checks[f"frozen_{n}_classifiable_counts_exact"]=res["counts"]==saved["counts"]
        checks[f"frozen_{n}_matching_exact"]=all(
            res["greedy_matches"][k]["n"]==saved["greedy_matches"][k]["n"]
            and res["optimal_matches"][k]["n"]==saved["optimal_matches"][k]["n"]
            for k in FORMATS[1:])
        checks[f"frozen_{n}_old_and_corrected_gate_replay"]=(
            res["greedy_gate"]["promoted"]==saved["greedy_gate"]["promoted"]
            and res["optimal_gate"]["promoted"]==saved["optimal_gate"]["promoted"])
        baseline[str(n)]={
            "counts":res["counts"],
            "max_resize_matches":res["optimal_matches"]["down75_up"],
            "max_gate_promoted":res["optimal_gate"]["promoted"],
            "greedy_gate_promoted":res["greedy_gate"]["promoted"]
        }
    checks["frozen_stage184_49_of_89_exact"]=(
        baseline["256"]["max_resize_matches"]["n"]==49
        and baseline["256"]["counts"]["original"]==89
        and baseline["256"]["max_gate_promoted"]
        and not baseline["256"]["greedy_gate_promoted"])
    checks["frozen_n16_negative_n64_positive"]=(
        not baseline["16"]["max_gate_promoted"] and baseline["64"]["max_gate_promoted"])
    observations=[]
    for family in FAMILIES:
        samples=[(256,s) for s in SEEDS]
        samples += [(64,s) for s in SEEDS[:2]]
        samples += [(128,s) for s in SEEDS[2:]]
        samples += [(16,SEEDS[0])]
        for n,seed in samples:
            art,draw=family_fixture(mask,n,family,seed)
            views=whole_views(art,blank,box)
            checks[f"{family}_{n}_{seed}_exact_draw"]=draw["commanded_count"]==n and draw["unique_centers"]
            checks[f"{family}_{n}_{seed}_endpoints_safe"]=draw["endpoints_inside_mask"]
            checks[f"{family}_{n}_{seed}_original_crop_equal"]=bool(np.array_equal(views["original"],art))
            res=measure(views,mask,reference)
            original=res["counts"]["original"]
            strict=res["optimal_matches"]["down75_up"]["n"]
            gate=res["optimal_gate"]
            candidate=bool(gate["promoted"] and 256 in gate["compatible_target_counts"])
            observations.append({
                "family":family,"seed":seed,"known_drawn":n,
                "eligible_grid_positions":draw["eligible_positions"],
                "nonwhite_ink_pixels":draw["nonwhite_ink_pixels"],
                "detected_counts_by_format":res["counts"],
                "resized_strict_optimal_matched":strict,
                "resized_strict_optimal_fraction":res["optimal_matches"]["down75_up"]["fraction"],
                "resized_original_greedy_fraction":res["greedy_matches"]["down75_up"]["fraction"],
                "original_greedy_gate_promoted":res["greedy_gate"]["promoted"],
                "strict_optimal_gate_promoted":gate["promoted"],
                "compatible_target_count_sizes":gate["compatible_target_counts"],
                "promoted_as_256_compatible":candidate,
                "count_cv":gate["cv"],
                "minority_orientation_gate":gate["minority_orientation_gate"],
                "all_variant_matching_gate":gate["cross_variant_agreement_gate"],
            })
    valid=all(checks.values())
    positives=[v for v in observations if v["known_drawn"]==256]
    decoys=[v for v in observations if v["known_drawn"] in (64,128)]
    negatives=[v for v in observations if v["known_drawn"]==16]
    n256_pass=sum(v["promoted_as_256_compatible"] for v in positives)
    nfalse=sum(v["promoted_as_256_compatible"] for v in decoys)
    neg16_ok=all(not v["strict_optimal_gate_promoted"] for v in negatives)
    if not valid:
        decision="CONTROL_FAILURE"
    elif n256_pass>=MIN_256_POSITIVE and nfalse<=MAX_256_FALSE_POSITIVE and neg16_ok:
        decision="STAGE184_COMBINED_GATE_PRELIMINARILY_REPLICATES"
    else:
        decision="STAGE184_COMBINED_GATE_NOT_DISCRIMINATIVE"
    report={
        "experiment_id":"A11-EXP-184-R",
        "source_sha256_provenance_only":digest,
        "original_artwork_pixels_examined":False,
        "prespecified_family_names":list(FAMILIES),
        "prespecified_seeds":list(SEEDS),
        "thresholds_unchanged":True,
        "frozen_qa_checks":checks,
        "checks_passed":sum(checks.values()),"checks_total":len(checks),
        "baseline_reproductions":baseline,
        "out_of_sample_fixtures":observations,
        "known_256_positive_passed":n256_pass,"known_256_positive_total":len(positives),
        "non256_false_256_compatible":nfalse,"non256_decoy_total":len(decoys),
        "known16_new_negative_pass":neg16_ok,
        "prespecified_min_positive":MIN_256_POSITIVE,
        "prespecified_max_false_positive":MAX_256_FALSE_POSITIVE,
        "decision":decision,
        "scope_limit":"Source-blind synthetic instrument discrimination only. No reliable 256-symbol decoding or evidence of an intentional natural-image code follows, even if synthetic results pass.",
        "safety":"No natural image stroke read, sign stream, address comparison, private key, wallet, mnemonic or outside-image research."
    }
    (OUT/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    lines=[
        "# Stage184-R — frozen source-blind synthetic holdout",
        "",
        f"- QA: **{sum(checks.values())}/{len(checks)}**",
        f"- KNOWN 256 drawn correctly promoted as 256-compatible: **{n256_pass}/{len(positives)}**",
        f"- KNOWN 64/128 falsely promoted as 256-compatible: **{nfalse}/{len(decoys)}**",
        f"- Two new known16 controls unpromoted: **{neg16_ok}**",
        f"- Fixed screening requirement: >= {MIN_256_POSITIVE}/8 sensitivity, <= {MAX_256_FALSE_POSITIVE}/8 false 256-compatible, known16 negative and QA passing",
        f"- Decision: **{decision}**","","| Family | Drawn | Seed | Detected original | Resized strict match | Full optimal gate | 256-compatible promoted |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for v in observations:
        m=v["resized_strict_optimal_matched"]; den=v["detected_counts_by_format"]["original"]
        lines.append(f"| {v['family']} | {v['known_drawn']} | {v['seed']} | {den} | {m}/{den} | {v['strict_optimal_gate_promoted']} | {v['promoted_as_256_compatible']} |")
    lines +=["","## Scientific limitation","",
        "These are artificial images generated by two specified mechanisms, not independent examples of an unknown authored 256-symbol encoding. Known64/128 false 256-compatibility demonstrates nonspecificity of count bands, not a real decoded symbol. Four image variants of each fixture are transformations of one fixture, not independent replicates. No original source artwork pixels or secret material were read."]
    (OUT/"REPORT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({
        "stage":"184-R",
        "qa":f"{sum(checks.values())}/{len(checks)}",
        "true256":f"{n256_pass}/{len(positives)}",
        "false256":f"{nfalse}/{len(decoys)}",
        "negative16":neg16_ok,"decision":decision}))
    if not valid:
        raise SystemExit("Stage184-R QA failure; do not interpret or claim success")

if __name__=="__main__":
    main()
