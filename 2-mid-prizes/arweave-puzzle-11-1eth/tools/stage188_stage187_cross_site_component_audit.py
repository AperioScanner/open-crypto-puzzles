#!/usr/bin/env python3
"""A11-EXP-188: frozen synthetic cross-site component-attribution audit.

This ONLY replays previously archived synthetic drawings using unchanged
Stage185/Stage187 functions; original puzzle image is read as SHA bytes only.
Prereg: analysis/runs/stage188-stage187-cross-site-component-audit/PREREGISTRATION.md.
No sensitive, wallet, address, mnemonic, or off-image operations.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

from stage127_hull_waterline_slope import SITES, crop as old_crop
import stage185_hull_curve_fragment_positive_audit as s185
from stage187_stage185_component_qa_audit import components

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/runs/stage188-stage187-cross-site-component-audit"
OUT.mkdir(parents=True, exist_ok=True)
PNG = ROOT / "clues/arweave-puzzle-11.png"
EXPECTED_SHA = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
OLD186 = ROOT / "analysis/runs/stage186-hull-column-center-holdout/result.json"
OLD187 = ROOT / "analysis/runs/stage187-stage185-component-qa-audit/result.json"
PRE = "analysis/runs/stage188-stage187-cross-site-component-audit/PREREGISTRATION.md"

def draw_single_site(site: tuple, known_class: str, family: str) -> np.ndarray:
    """Exactly the existing Stage185 drawing instructions, for ONE site."""
    image = np.full((1105, 1600), 255, np.uint8)
    name, cx, top, h, half = site
    by = top + h
    sail = [(cx, top + 8), (cx - half, by - 9), (cx + half, by - 9)]
    cv2.line(image, sail[0], sail[1], 0, 2, cv2.LINE_AA)
    cv2.line(image, sail[0], sail[2], 0, 2, cv2.LINE_AA)
    cv2.line(image, sail[1], sail[2], 0, 1, cv2.LINE_AA)
    left, right = cx - half - 11, cx + half + 11
    mid = (left + right) / 2
    for offset in s185.OFFSETS:
        points = s185.a_stroke_points(
            left, right, mid, by, offset, s185.SLOPES[known_class], family
        )
        made, inside = s185.draw_one_stroke(image, points, family)
        if made < 1 or not inside:
            raise AssertionError(f"single-site drawing failed: {name} {known_class} {family}")
    return image

def isolated_source_controls() -> dict[str, int]:
    """Known truth of target vs non-target line attribution (all <245, 8conn)."""
    blank = np.full((41, 65), 255, np.uint8)
    target = blank.copy()
    cv2.line(target, (5, 9), (59, 9), 0, 2, cv2.LINE_AA)
    inside = target.copy()
    cv2.line(inside, (5, 29), (59, 29), 0, 2, cv2.LINE_AA)
    joined = inside.copy()
    cv2.line(joined, (32, 9), (32, 29), 0, 2, cv2.LINE_AA)
    outside_canvas = np.full((60, 65), 255, np.uint8)
    cv2.line(outside_canvas, (5, 9), (59, 9), 0, 2, cv2.LINE_AA)
    cv2.line(outside_canvas, (5, 52), (59, 52), 0, 2, cv2.LINE_AA)
    return {
        "blank": components(blank),
        "target_only": components(target),
        "target_plus_non_touching_neighbor_inside_roi": components(inside),
        "target_plus_neighbor_outside_roi": components(outside_canvas[:41, :].copy()),
        "target_plus_joined_neighbor": components(joined),
    }

def main() -> None:
    digest = hashlib.sha256(PNG.read_bytes()).hexdigest()
    a186 = json.loads(OLD186.read_text())
    a187 = json.loads(OLD187.read_text())
    old_rows = a187.get("site_results", [])
    prior = {
        (r["family"], r["known_truth"], r["site"]): r
        for r in old_rows
    }
    basic = isolated_source_controls()
    qa = {
        "original_png_provenance_bytes_only": digest == EXPECTED_SHA,
        "archived_stage186_scientific_failure": (
            a186.get("qa_passed") == a186.get("qa_total") == 18
            and a186.get("decision") == "STAGE186_HELDOUT_CALIBRATION_INADEQUATE"
        ),
        "archived_stage187_qa_and_decision": (
            a187.get("qa_passed") == a187.get("qa_total") == 13
            and a187.get("mismatch_count") == 10
            and a187.get("decision") == "STAGE185_COMPOSITE_COMPONENT_QA_MISMATCH_CONFIRMED"
        ),
        "frozen_five_sites": len(SITES) == 5 and len({x[0] for x in SITES}) == 5,
        "frozen_three_families": tuple(s185.NUISANCES) == ("curved","broken","curved_broken"),
        "frozen_three_classes": tuple(s185.CLASSES) == ("UP_RIGHT","LEVEL","DOWN_RIGHT"),
        "archived_45_unique_composite_rows": len(old_rows) == len(prior) == 45,
        "known_blank_components_0": basic["blank"] == 0,
        "known_target_only_components_1": basic["target_only"] == 1,
        "known_unrelated_neighbor_inside_components_2":
            basic["target_plus_non_touching_neighbor_inside_roi"] == 2,
        "known_neighbor_outside_components_1":
            basic["target_plus_neighbor_outside_roi"] == 1,
        "known_joined_neighbor_components_1":
            basic["target_plus_joined_neighbor"] == 1,
    }
    qa = {k: bool(v) for k,v in qa.items()}
    records: list[dict] = []
    all_scene_masks_equal = True
    archived_full_replay_exact = True
    all_scene_shapes = True
    if all(qa.values()):
        for family in s185.NUISANCES:
            for known in s185.CLASSES:
                full, _metadata = s185.source_blind_scene(known, family)
                all_scene_shapes &= full.shape == (1105, 1600)
                isolated = {site[0]: draw_single_site(site, known, family) for site in SITES}
                union = np.zeros((1105,1600), dtype=bool)
                for separate in isolated.values():
                    union |= separate < 245
                all_scene_masks_equal &= bool(np.array_equal(union, full < 245))
                for site in SITES:
                    name = site[0]
                    key = (family, known, name)
                    full_roi = old_crop(full,site)
                    own_roi = old_crop(isolated[name],site)
                    full_count = components(full_roi)
                    own_count = components(own_roi)
                    foreign_pixels = int(np.count_nonzero(
                        (full_roi < 245) & ~(own_roi < 245)
                    ))
                    archived = prior.get(key)
                    old_match = archived is not None and full_count == archived.get(
                        "actual_composite_components"
                    ) and archived.get("archived_claim_two_contours") is True
                    archived_full_replay_exact &= bool(old_match)
                    records.append({
                        "family": family,
                        "known_truth": known,
                        "site": name,
                        "full_roi_components": full_count,
                        "isolated_target_components": own_count,
                        "foreign_foreground_pixels_in_full_roi": foreign_pixels,
                        "full_roi_fails_min_two": full_count < 2,
                        "target_only_fails_min_two": own_count < 2,
                        "cross_site_false_sufficiency":
                            full_count >= 2 and own_count < 2 and foreign_pixels > 0,
                        "component_count_changed": full_count != own_count,
                    })
    qa["all_nine_full_scenes_valid_shapes"] = bool(all_scene_shapes and records)
    qa["all_nine_binary_full_masks_exact_union_of_isolated"] = bool(all_scene_masks_equal and records)
    qa["all_45_full_roi_counts_reproduce_stage187_by_site"] = bool(archived_full_replay_exact and len(records)==45)
    qa["all_45_observations_generated"] = len(records) == 45
    qa = {k:bool(v) for k,v in qa.items()}
    correct_controls = all(qa.values())
    false_suff = [r for r in records if r["cross_site_false_sufficiency"]]
    full_deficits = sum(r["full_roi_fails_min_two"] for r in records)
    target_deficits = sum(r["target_only_fails_min_two"] for r in records)
    changed = sum(r["component_count_changed"] for r in records)
    foreign = sum(r["foreign_foreground_pixels_in_full_roi"]>0 for r in records)
    decision = (
        "CONTROL_FAILURE" if not correct_controls else
        "STAGE187_CROSS_SITE_ATTRIBUTION_BIAS_CONFIRMED" if false_suff else
        "STAGE187_CROSS_SITE_ATTRIBUTION_NO_CHANGE"
    )
    per_family = {}
    for family in s185.NUISANCES:
        rows=[r for r in records if r["family"]==family]
        per_family[family]={
            "total":len(rows),
            "foreign_roi_count":sum(r["foreign_foreground_pixels_in_full_roi"]>0 for r in rows),
            "full_roi_lt2":sum(r["full_roi_fails_min_two"] for r in rows),
            "isolated_target_lt2":sum(r["target_only_fails_min_two"] for r in rows),
            "false_sufficiency":sum(r["cross_site_false_sufficiency"] for r in rows),
            "count_changed":sum(r["component_count_changed"] for r in rows),
            "isolated_component_histogram":dict(Counter(str(r["isolated_target_components"]) for r in rows)),
        }
    data={
        "experiment_id":"A11-EXP-188",
        "preregistration":PRE,
        "canonical_sha256_provenance_only":digest,
        "original_artwork_pixels_read":False,
        "qa":qa,"qa_passed":sum(qa.values()),"qa_total":len(qa),
        "fresh_controls":basic,
        "site_results":records,
        "total_audited_sites":len(records),
        "foreign_site_roi_count":foreign,
        "component_count_changed_site_count":changed,
        "stage187_literal_full_roi_lt2":full_deficits,
        "target_isolated_lt2":target_deficits,
        "cross_site_false_sufficiency_count":len(false_suff),
        "per_family":per_family,
        "decision":decision,
        "source_isolation_limit":"All observations are existing synthetic sites; NOT independent holdout. Stage127 already noted real-source overlap.",
        "interpretation":"Stage187's ROI counts remain literal measurements, but cannot be attributed entirely to each nominal target hull where other site ink enters. No scientific image-source code claim.",
        "safety":"No original PNG pixels, private keys, BIP39, wallets, addresses, OCR or external/social research.",
    }
    (OUT/"result.json").write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    md=[
        "# Stage188 — source-blind Stage187 crop attribution audit", "",
        f"- Integrity / fresh controls: **{sum(qa.values())}/{len(qa)}**",
        f"- Full-ROI Stage187 site counts reproduced: **{archived_full_replay_exact and len(records)==45}**",
        f"- Number of synthetic site ROIs containing non-target foreground: **{foreign}/45**",
        f"- Site component counts changed by excluding non-target boats: **{changed}/45**",
        f"- Full-ROI sites with <2 components: **{full_deficits}/45** (Stage187 literal figure)",
        f"- Object-isolated sites with <2 components: **{target_deficits}/45**",
        f"- Apparent full-ROI passes that are target-only failures: **{len(false_suff)}/45**",
        f"- Frozen decision: **{decision}**","",
        "| Family | Sites | Foreign ink | Full-ROI <2 | Target-only <2 | False sufficiency |",
        "|---|---:|---:|---:|---:|---:|"
    ]
    for k,v in per_family.items():
        md.append(f"| {k} | {v['total']} | {v['foreign_roi_count']} | {v['full_roi_lt2']} | {v['isolated_target_lt2']} | {v['false_sufficiency']} |")
    md+=["","Stage187's 10/45 is an exact count of <2 **components inside fixed full-scene ROIs**.",
         "It is not, without object isolation, an exact count of <2 components of each **named hull**.",
         "The previous Stage127 original-source overlap warning is historical, not a new visual clue.",
         "This measurement audits already-used synthetic drawings, NOT independent holdouts.",
         "All historical Stage185–187 files, preregistration criteria and scientific failures are unchanged.",
         "No natural original image pixels, solution, code, key or wallet-related data were evaluated.",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md)+"\n")
    print(json.dumps({"stage":188,"qa":f"{sum(qa.values())}/{len(qa)}",
        "source_foreign_rois":foreign,"full_deficits":full_deficits,
        "isolated_deficits":target_deficits,"false_sufficiency":len(false_suff),
        "decision":decision}))
    if decision=="CONTROL_FAILURE":
        raise SystemExit("CONTROL_FAILURE — repair this stage only; do not interpret counts")

if __name__=="__main__":
    main()
