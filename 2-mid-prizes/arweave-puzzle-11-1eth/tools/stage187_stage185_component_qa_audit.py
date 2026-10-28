#!/usr/bin/env python3
"""A11-EXP-187: preregistered source-blind audit of Stage185 component QA.

Only reads the canonical PNG bytes for SHA identity. No original image pixels,
wallet/secret/address tests, source-code tuning or external searches.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

from stage127_hull_waterline_slope import SITES, crop as old_crop
from stage185_hull_curve_fragment_positive_audit import (
    NUISANCES, CLASSES, source_blind_scene,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/runs/stage187-stage185-component-qa-audit"
OUT.mkdir(parents=True, exist_ok=True)
OLD185 = ROOT / "analysis/runs/stage185-hull-curvature-calibration/result.json"
OLD186 = ROOT / "analysis/runs/stage186-hull-column-center-holdout/result.json"
PNG = ROOT / "clues/arweave-puzzle-11.png"
EXPECTED_SHA = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
PRE = "analysis/runs/stage187-stage185-component-qa-audit/PREREGISTRATION.md"


def components(roi: np.ndarray) -> int:
    """Frozen Stage185 intensity test and 8-connected foreground components."""
    assert roi.ndim == 2 and roi.dtype == np.uint8
    fg = (roi < 245).astype(np.uint8)
    return int(cv2.connectedComponents(fg, connectivity=8)[0] - 1)


def fresh_fixture_controls() -> dict[str, int]:
    blank = np.full((41, 65), 255, np.uint8)
    one = blank.copy()
    cv2.line(one, (5, 10), (59, 10), 0, 2, cv2.LINE_AA)
    two = one.copy()
    cv2.line(two, (5, 30), (59, 30), 0, 2, cv2.LINE_AA)
    joined = two.copy()
    cv2.line(joined, (32, 10), (32, 30), 0, 2, cv2.LINE_AA)
    return {n: components(x) for n, x in (
        ("blank", blank), ("one", one), ("two", two), ("joined", joined)
    )}


def main() -> None:
    digest = hashlib.sha256(PNG.read_bytes()).hexdigest()
    old185 = json.loads(OLD185.read_text())
    old186 = json.loads(OLD186.read_text())

    sanity = fresh_fixture_controls()
    qa = {
        "source_identity_bytes_only": digest == EXPECTED_SHA,
        "stage185_archived_44_of_44": (
            old185.get("qa_passed") == old185.get("qa_total") == 44
            and old185.get("decision") ==
            "STAGE127_SOURCE_LIKE_POSITIVE_RECOVERY_INADEQUATE"
        ),
        "stage186_archived_18_of_18": (
            old186.get("qa_passed") == old186.get("qa_total") == 18
            and old186.get("decision") == "STAGE186_HELDOUT_CALIBRATION_INADEQUATE"
        ),
        "frozen_five_sites": len(SITES) == 5
            and len({x[0] for x in SITES}) == 5,
        "frozen_three_families": tuple(NUISANCES) ==
            ("curved", "broken", "curved_broken"),
        "frozen_three_classes": tuple(CLASSES) ==
            ("UP_RIGHT", "LEVEL", "DOWN_RIGHT"),
        "fresh_blank_is_zero": sanity["blank"] == 0,
        "fresh_one_line_is_one": sanity["one"] == 1,
        "fresh_two_separated_lines_are_two": sanity["two"] == 2,
        "fresh_two_joined_lines_are_one": sanity["joined"] == 1,
    }
    qa = {key: bool(value) for key, value in qa.items()}
    rows = []
    if all(qa.values()):
        for family in NUISANCES:
            for truth in CLASSES:
                image, metadata = source_blind_scene(truth, family)
                assert image.shape == (1105, 1600)
                mapping = {x["site"]: x for x in metadata}
                for site in SITES:
                    name = site[0]
                    m = mapping[name]
                    old_flag = bool(m[">=two_nonempty_stroke_components_or_contours"])
                    actual = components(old_crop(image, site))
                    rows.append({
                        "family": family,
                        "known_truth": truth,
                        "site": name,
                        "archived_individual_strokes": int(
                            m["four_individually_rendered_hull_strokes"]
                        ),
                        "archived_claim_two_contours": old_flag,
                        "actual_composite_components": actual,
                        "precommitted_qa_discrepancy":
                            old_flag and actual < 2,
                    })
    qa["exactly_45_existing_fixture_sites"] = len(rows) == 45
    qa["archived_individual_strokes_4_each"] = (
        bool(rows) and all(x["archived_individual_strokes"] == 4 for x in rows)
    )
    qa["archived_composite_claims_true"] = (
        bool(rows) and all(x["archived_claim_two_contours"] for x in rows)
    )
    qa = {key: bool(value) for key, value in qa.items()}
    good = all(qa.values())
    bad = [x for x in rows if x["precommitted_qa_discrepancy"]]
    decision = (
        "CONTROL_FAILURE" if not good else
        "STAGE185_COMPOSITE_COMPONENT_QA_MISMATCH_CONFIRMED" if bad else
        "STAGE185_COMPOSITE_COMPONENT_QA_MATCHES"
    )
    per_family = {
        family: {
            "total_sites": sum(x["family"] == family for x in rows),
            "mismatches": sum(x["family"] == family
                              and x["precommitted_qa_discrepancy"] for x in rows),
            "component_histogram": dict(Counter(
                str(x["actual_composite_components"])
                for x in rows if x["family"] == family
            )),
        }
        for family in NUISANCES
    }
    result = {
        "experiment_id": "A11-EXP-187",
        "preregistration": PRE,
        "canonical_sha256_provenance_only": digest,
        "original_artwork_pixels_read": False,
        "scope": "Stage185 QA protocol compliance on old synthetic fixtures only",
        "reused_old_fixtures_not_independent_holdouts": True,
        "fixed_component_counter": {
            "input": "unchanged Stage127.crop scene/site",
            "foreground_gray_below": 245,
            "connectivity": 8,
        },
        "fresh_known_component_controls": sanity,
        "qa": qa,
        "qa_passed": sum(qa.values()),
        "qa_total": len(qa),
        "audited_sites": len(rows),
        "mismatch_count": len(bad),
        "per_family": per_family,
        "site_results": rows,
        "decision": decision,
        "scientific_limit":
            "Old QA protocol mismatch cannot validate a source-image code. "
            "Stage185/186 negative scientific conclusions unchanged.",
        "safety":
            "No canonical pixel read, keys, BIP39, wallets, addresses, "
            "OCR or outside-image research.",
    }
    (OUT / "result.json").write_text(json.dumps(
        result, indent=2, sort_keys=True, allow_nan=False
    ) + "\n")
    lines = [
        "# Stage187 — Stage185 composite-component QA protocol audit",
        "",
        f"- Archive/provenance/fresh-counter checks: **{sum(qa.values())}/{len(qa)}**",
        f"- Previously archived Stage185 sites reviewed: **{len(rows)}**",
        f"- False Stage185 multi-component QA assertions: **{len(bad)}**",
        f"- Decision: **{decision}**",
        "",
        "| Old fixture family | Sites | Composite-flag mismatches |",
        "|---|---:|---:|",
    ]
    for family, v in per_family.items():
        lines.append(f"| {family} | {v['total_sites']} | {v['mismatches']} |")
    lines += [
        "",
        "The Stage185 code checks separate line supports and then labels their",
        "count as a composite >=2 connected-component/contour guard. Its",
        "preregistered condition concerned connected features in the composed",
        "object. Passing Stage185's 44/44 QA therefore does **not** verify that",
        "specific preregistered composite condition. It does not invalidate the",
        "prior finding that positive recovery was inadequate; no Stage185",
        "criterion, report, code, or source-derived claim was revised.",
        "",
        "The 45 old synthetic cases are in-sample protocol audits, NOT",
        "independent scientific holdouts. No natural-image pixels were read.",
        "No clue, message, cryptographic or wallet inference is supported.",
    ]
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({
        "stage": 187,
        "qa": f"{sum(qa.values())}/{len(qa)}",
        "mismatch": len(bad),
        "decision": decision,
    }))
    if decision == "CONTROL_FAILURE":
        raise SystemExit("CONTROL_FAILURE: do not interpret mismatches")


if __name__ == "__main__":
    main()
