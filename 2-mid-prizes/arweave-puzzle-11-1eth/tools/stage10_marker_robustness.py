#!/usr/bin/env python3
"""Stage 10: test whether the 12-building H/V skyline marker is robust to crop choices.

This experiment is intentionally non-cryptographic. It does not generate, derive, or
verify private keys. It only measures visual orientation structure in the published image.
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "clues" / "arweave-puzzle-11.png"
GEOM = ROOT / "data" / "geometry.json"
OUT = ROOT / "analysis" / "runs" / "stage10-marker-robustness"
OUT.mkdir(parents=True, exist_ok=True)

EXPERIMENT_VERSION = 1\nEXPECTED = "HHVVHHVHHHHV"


def clamp_box(box, w, h):
    x0, y0, x1, y1 = map(int, box)
    x0 = max(0, min(w - 2, x0))
    x1 = max(x0 + 2, min(w, x1))
    y0 = max(0, min(h - 2, y0))
    y1 = max(y0 + 2, min(h, y1))
    return x0, y0, x1, y1


def inner_box(b, frac=0.12):
    x0, x1, y0, y1 = b["x0"], b["x1"], b["roof_y"], b["bottom_y"]
    w = x1 - x0
    h = y1 - y0
    mx = max(5, int(w * frac))
    my = max(6, int(h * frac))
    return x0 + mx, y0 + my, x1 - mx, y1 - my


def classify(gray, box):
    x0, y0, x1, y1 = clamp_box(box, gray.shape[1], gray.shape[0])
    crop = gray[y0:y1, x0:x1]
    if crop.size < 16:
        return "M", 0.0
    x = cv2.GaussianBlur(crop, (3, 3), 0)
    gx = cv2.Sobel(x, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(x, cv2.CV_64F, 0, 1, ksize=3)
    ex = float(np.mean(np.abs(gx)))
    ey = float(np.mean(np.abs(gy)))
    score = (ex - ey) / (ex + ey + 1e-12)
    cls = "V" if score > 0.06 else ("H" if score < -0.06 else "M")
    return cls, score


def seq_for_boxes(gray, boxes):
    cs, scores = [], []
    for box in boxes:
        c, s = classify(gray, box)
        cs.append(c)
        scores.append(s)
    return "".join(cs), scores


def as_hex(seq):
    if any(c not in "HV" for c in seq):
        return None
    bits = "".join("0" if c == "H" else "1" for c in seq)
    return {"bits": bits, "hex": format(int(bits, 2), "03x"), "int": int(bits, 2)}


def main():
    geom = json.loads(GEOM.read_text())
    img = cv2.imread(str(SOURCE), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise SystemExit("image load failed")
    gray = img[:, :, 0] if img.ndim == 3 else img

    buildings = geom["buildings"]
    baseline_boxes = [inner_box(b, 0.12) for b in buildings]
    baseline, baseline_scores = seq_for_boxes(gray, baseline_boxes)
    if baseline != EXPECTED:
        raise SystemExit(f"baseline drift: {baseline} != {EXPECTED}")

    # 1) Margin robustness: change how much of each building boundary is excluded.
    margin_results = []
    for frac in (0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.22):
        boxes = [inner_box(b, frac) for b in buildings]
        seq, scores = seq_for_boxes(gray, boxes)
        margin_results.append({
            "inner_margin_fraction": frac,
            "sequence": seq,
            "matches_baseline": seq == baseline,
            "mapping": as_hex(seq),
            "scores": scores,
        })

    # 2) Deterministic jitter around each independently measured building box.
    # Shift and lightly resize each inner box. This asks whether the marker depends on
    # exact hand-picked coordinates.
    rng = np.random.default_rng(20261001)
    jitter_results = []
    per_building = {
        str(i + 1): {"H": 0, "V": 0, "M": 0, "trials": 0}
        for i in range(len(buildings))
    }
    for radius in (1, 2, 4, 8, 12, 16):
        trials = 400
        exact = 0
        total_hamming = 0
        mixed = 0
        for _ in range(trials):
            boxes = []
            for box in baseline_boxes:
                x0, y0, x1, y1 = box
                dx = int(rng.integers(-radius, radius + 1))
                dy = int(rng.integers(-radius, radius + 1))
                edge = max(1, radius // 3)
                dl = int(rng.integers(-edge, edge + 1))
                dr = int(rng.integers(-edge, edge + 1))
                dt = int(rng.integers(-edge, edge + 1))
                db = int(rng.integers(-edge, edge + 1))
                boxes.append((x0 + dx + dl, y0 + dy + dt, x1 + dx + dr, y1 + dy + db))
            seq, _ = seq_for_boxes(gray, boxes)
            if seq == baseline:
                exact += 1
            if "M" in seq:
                mixed += 1
            hamming = sum(a != b for a, b in zip(seq, baseline))
            total_hamming += hamming
            for i, c in enumerate(seq):
                per_building[str(i + 1)][c] += 1
                per_building[str(i + 1)]["trials"] += 1
        jitter_results.append({
            "radius_px": radius,
            "trials": trials,
            "exact_sequence_count": exact,
            "exact_sequence_fraction": exact / trials,
            "mixed_sequence_count": mixed,
            "mean_hamming_distance": total_hamming / trials,
        })

    # 3) Local single-building stability, with larger shifts but no resizing.
    local_stability = []
    rng2 = np.random.default_rng(321)
    for i, box in enumerate(baseline_boxes):
        counts = {"H": 0, "V": 0, "M": 0}
        samples = 2000
        for _ in range(samples):
            dx = int(rng2.integers(-24, 25))
            dy = int(rng2.integers(-24, 25))
            x0, y0, x1, y1 = box
            c, _ = classify(gray, (x0 + dx, y0 + dy, x1 + dx, y1 + dy))
            counts[c] += 1
        local_stability.append({
            "building_id": i + 1,
            "baseline_class": baseline[i],
            "samples": samples,
            "counts": counts,
            "baseline_class_fraction": counts[baseline[i]] / samples,
        })

    result = {
        "experiment_id": "A11-EXP-010",
        "scope": "visual-only skyline orientation marker robustness; no key generation or address verification",
        "baseline_sequence": baseline,
        "baseline_scores": baseline_scores,
        "baseline_mapping_H0_V1": as_hex(baseline),
        "margin_robustness": margin_results,
        "jitter_robustness": jitter_results,
        "per_building_jitter_counts": per_building,
        "local_shift_stability": local_stability,
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n")

    all_margins = all(r["matches_baseline"] for r in margin_results)
    min_jitter = min(r["exact_sequence_fraction"] for r in jitter_results)
    mean_local = float(np.mean([r["baseline_class_fraction"] for r in local_stability]))

    md = [
        "# Stage 10 — skyline 0x321 marker robustness",
        "",
        "**Experiment:** A11-EXP-010",
        "",
        "This is a visual-only experiment. It does not generate, derive, or verify any private-key material.",
        "",
        f"- Baseline H/V sequence: `{baseline}`",
        f"- H=0, V=1: `{as_hex(baseline)['bits']}` = `0x{as_hex(baseline)['hex']}`",
        f"- All tested inner-margin choices preserved the exact sequence: **{all_margins}**",
        f"- Worst exact-sequence preservation across bounded box jitter radii: **{min_jitter:.3f}**",
        f"- Mean per-building baseline-class fraction under ±24 px local shifts: **{mean_local:.3f}**",
        "",
        "## Margin robustness",
        "",
        "| inner margin | sequence | exact baseline |",
        "|---:|:---:|:---:|",
    ]
    for r in margin_results:
        md.append(f"| {r['inner_margin_fraction']:.2f} | {r['sequence']} | {r['matches_baseline']} |")

    md += [
        "",
        "## Bounding-box jitter robustness",
        "",
        "| jitter radius | trials | exact sequence fraction | mean Hamming distance | mixed-class runs |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in jitter_results:
        md.append(
            f"| ±{r['radius_px']} px | {r['trials']} | {r['exact_sequence_fraction']:.3f} | "
            f"{r['mean_hamming_distance']:.3f} | {r['mixed_sequence_count']} |"
        )

    md += [
        "",
        "## Interpretation",
        "",
        "The purpose of this run is to test whether the visually recovered `0x321` marker is an artifact of exact crop coordinates.",
        "High stability would support treating `321` as a genuine image-level clue or instruction; it would **not** prove what the clue means or establish that it is intentional.",
        "The author explicitly pointed solvers toward solved puzzles, whose documented solutions rely heavily on robust human-readable visual semantics rather than fragile file-format details. That makes crop-invariant visual structure more relevant than container-specific noise.",
        "",
    ]
    (OUT / "REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status": "ok",
        "experiment_id": "A11-EXP-010",
        "baseline": baseline,
        "mapping": as_hex(baseline),
        "all_margin_variants_preserved": all_margins,
        "worst_jitter_exact_fraction": min_jitter,
        "mean_local_stability": mean_local,
    }))


if __name__ == "__main__":
    main()
