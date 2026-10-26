#!/usr/bin/env python3
"""A11-EXP-186: preregistered SOURCE-BLIND hull-slope detector validation.

Read original puzzle PNG BYTES ONLY for SHA-256 identity, never pixel arrays.
The candidate detector, holdouts, decision thresholds and stop criteria are
frozen in analysis/runs/stage186-hull-column-center-holdout/PREREGISTRATION.md.
No cryptographic, wallet, phrase, address or off-image operations.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

from stage112_corrected_sail_width_progression import variants
from stage127_hull_waterline_slope import (
    SITES, FORMATS, synthetic as old_synthetic
)
from stage185_hull_curve_fragment_positive_audit import (
    source_blind_scene as stage185_source_blind_scene
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/runs/stage186-hull-column-center-holdout"
OUT.mkdir(parents=True, exist_ok=True)
PNG = ROOT / "clues/arweave-puzzle-11.png"
SHA = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
OLD127 = ROOT / "analysis/runs/stage127-hull-waterline-slope/result.json"
OLD185 = ROOT / "analysis/runs/stage185-hull-curvature-calibration/result.json"

NATURAL_PIXELS_READ = False
CLASSES = ("UP_RIGHT", "LEVEL", "DOWN_RIGHT")
SLOPES = {"UP_RIGHT": -0.26, "LEVEL": 0.0, "DOWN_RIGHT": +0.26}
THRESHOLDS = (155, 185)
OFFSETS = (6, 10, 15, 20)
STYLE_SPECS = {
    "holdout_A": (4.0, 16, 7, 3),
    "holdout_B": (8.0, 12, 9, 5),
}
W = 1600
H = 1105


def estimator(image: np.ndarray, site: tuple, threshold: int) -> dict:
    """Median pairwise y-centroid slope; only columns with >=3 dark runs."""
    name, cx, top, h, _half = site
    by = top + h
    cut = image[by-5:by+35, cx-26:cx+27]
    assert cut.shape == (40, 53), (name, cut.shape)
    ink = cut < threshold
    prev_white = np.vstack((np.ones((1, 53), dtype=bool), ~ink[:-1]))
    run_count = np.sum(ink & prev_white, axis=0)
    xs_local = np.flatnonzero(run_count >= 3)
    count = int(len(xs_local))
    if count < 16 or int(np.ptp(xs_local)) < 32:
        return {"label": None, "slope": None, "columns": count,
                "span": int(np.ptp(xs_local)) if count else 0,
                "pairs": 0}

    ink_weight = (255.0 - cut.astype(np.float64)) / 255.0
    ink_weight *= ink
    weight = ink_weight[:, xs_local]
    denom = weight.sum(axis=0)
    if np.any(denom <= 0):
        raise AssertionError("Qualified columns must contain ink")
    ys = (weight * np.arange(by-5, by+35, dtype=np.float64)[:, None]).sum(axis=0) / denom
    xs = xs_local.astype(np.float64)
    i, j = np.triu_indices(count, 1)
    spaced = (xs[j] - xs[i]) >= 14
    if not np.any(spaced):
        return {"label": None, "slope": None,
                "columns": count, "span": int(np.ptp(xs_local)), "pairs": 0}
    slopes = (ys[j[spaced]]-ys[i[spaced]])/(xs[j[spaced]]-xs[i[spaced]])
    slope = float(np.median(slopes))
    if slope >= .12:
        label = "DOWN_RIGHT"
    elif slope <= -.12:
        label = "UP_RIGHT"
    elif abs(slope) <= .055:
        label = "LEVEL"
    else:
        label = None
    return {"label": label, "slope": round(slope, 6), "columns": count,
            "span": int(np.ptp(xs_local)), "pairs": int(len(slopes))}


def classify_scene(image: np.ndarray) -> list[dict]:
    trans = variants(image)
    outputs = []
    for site in SITES:
        measures = []
        for variant in FORMATS:
            for threshold in THRESHOLDS:
                values = estimator(trans[variant], site, threshold)
                measures.append({"variant": variant, "threshold": threshold, **values})
        labels = [v["label"] for v in measures]
        agreed = labels[0] if labels[0] is not None and all(
            v == labels[0] for v in labels
        ) else None
        outputs.append({"site": site[0], "stable_class": agreed,
                        "readings": measures})
    return outputs


def outline(image: np.ndarray, site: tuple) -> None:
    _name, cx, top, height, half = site
    by = top + height
    p0 = (cx, top + 8)
    p1 = (cx - half, by - 9)
    p2 = (cx + half, by - 9)
    cv2.line(image, p0, p1, 0, 2, cv2.LINE_AA)
    cv2.line(image, p0, p2, 0, 2, cv2.LINE_AA)
    cv2.line(image, p1, p2, 0, 1, cv2.LINE_AA)


def draw_fragments(image: np.ndarray, points: list[tuple[int, int]],
                   on: int, off: int, phase: int) -> int:
    """One frozen on/off pattern, applied to each of four stroked layers."""
    period = on + off
    mask = [((k + phase) % period) < on for k in range(len(points))]
    start = None
    pieces = 0
    for idx in range(len(points) + 1):
        active = idx < len(points) and mask[idx]
        if active and start is None:
            start = idx
        if start is not None and (not active):
            if idx-start >= 2:
                part = np.asarray(points[start:idx], dtype=np.int32)
                cv2.polylines(image, [part], False, 0, 2, cv2.LINE_AA)
                pieces += 1
            start = None
    return pieces


def make_holdout(label: str, family: str) -> tuple[np.ndarray, list[dict]]:
    bow, on, off, phase = STYLE_SPECS[family]
    canvas = np.full((H, W), 255, dtype=np.uint8)
    diagnostic = []
    for site in SITES:
        _name, cx, top, height, half = site
        by = top + height
        outline(canvas, site)
        left, right = cx-half-11, cx+half+11
        mid = (left + right)/2.0
        layers = []
        for offset in OFFSETS:
            pts = []
            for x in range(left, right+1):
                position = 2*(x-mid)/(right-left)
                y = int(round(by + offset + SLOPES[label]*(x-mid) + bow*position**2))
                pts.append((x, y))
            in_frame = all(0 <= x < W and 0 <= y < H for x,y in pts)
            individual = np.full((H,W),255,dtype=np.uint8)
            fragments = draw_fragments(individual, pts, on, off, phase)
            draw_fragments(canvas, pts, on, off, phase)
            layers.append({"pixels": int(np.count_nonzero(individual < 245)),
                           "total_points": len(pts),
                           "fragments": fragments,
                           "in_frame": bool(in_frame)})
        diagnostic.append({"site":site[0],"layers":layers})
    return canvas, diagnostic


def make_negative(kind: str) -> tuple[np.ndarray, list[dict]]:
    canvas = np.full((H,W),255,np.uint8)
    counts=[]
    for site in SITES:
        name,cx,top,h,half=site
        by=top+h
        if kind != "blank":
            outline(canvas,site)
        n=0
        if kind in ("single_diagonal","opposing_two_diagonals"):
            left,right=cx-half-11,cx+half+11
            mid=(left+right)/2.0
            lines=[(10,+.26)] if kind=="single_diagonal" else [(8,+.26),(19,-.26)]
            for offset,slope in lines:
                p0=(left,int(round(by+offset+slope*(left-mid))))
                p1=(right,int(round(by+offset+slope*(right-mid))))
                cv2.line(canvas,p0,p1,0,2,cv2.LINE_AA)
                n+=1
        counts.append({"site":name,"explicit_decoy_lines":n})
    return canvas, counts


def outcome(rows: list[dict], known: str | None) -> dict:
    correct=sum(q["stable_class"]==known for q in rows) if known is not None else 0
    wrong=sum(q["stable_class"] is not None and q["stable_class"]!=known
              for q in rows) if known is not None else 0
    false=sum(q["stable_class"] is not None for q in rows) if known is None else 0
    # Output all eight threshold/format readings for independent review.
    return {"correct_stable":int(correct), "wrong_stable":int(wrong),
            "abstained":int(5-correct-wrong) if known is not None else int(5-false),
            "false_positive":int(false),
            "site_results":rows}


def main() -> None:
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    old127=json.loads(OLD127.read_text())
    old185=json.loads(OLD185.read_text())
    qa={
        "source_sha_bytes_only":digest==SHA,
        "original_artwork_pixels_not_read":NATURAL_PIXELS_READ is False,
        "stage127_archived_abstention":
            old127["decision"]=="INSUFFICIENT_HULL_ISOLATION" and old127["stable_sites"]==0,
        "stage127_original_controls":
            old127["controls"]["positive_mixed_pass"] and
            old127["controls"]["negative_level_with_decoy_pass"],
        "stage185_archived_44_of_44":
            old185["qa_passed"]==old185["qa_total"]==44 and
            old185["decision"]=="STAGE127_SOURCE_LIKE_POSITIVE_RECOVERY_INADEQUATE",
        "frozen_sites":
            old127["hull_sites"]==[list(site) for site in SITES] and len(SITES)==5,
        "frozen_formats":
            tuple(FORMATS)==("original","jpeg85","jpeg70","down75_up"),
        "frozen_thresholds":THRESHOLDS==(155,185),
        "different_frozen_holdout_styles":
            all((b,on,off)!=(6.0,20,8) for b,on,off,_phase in STYLE_SPECS.values()),
    }

    # Validate new fixture construction before classifying any scene.
    positives=[]
    for family in STYLE_SPECS:
        for cls in CLASSES:
            arr,layers=make_holdout(cls,family)
            valid=all(
                len(site["layers"])==4 and all(
                    ln["pixels"]>=10 and ln["total_points"]>80 and
                    ln["fragments"]>=1 and ln["in_frame"]
                    for ln in site["layers"])
                for site in layers
            )
            qa[f"draw_{family}_{cls}"]=len(layers)==5 and valid
            positives.append((family,cls,arr))
    negatives=[]
    for kind,number in [("blank",0),("single_diagonal",1),
                        ("opposing_two_diagonals",2)]:
        arr,counts=make_negative(kind)
        good=len(counts)==5 and all(row["explicit_decoy_lines"]==number for row in counts)
        if kind=="blank":
            good=good and int(np.count_nonzero(arr<245))==0
        qa[f"negative_fixture_{kind}"]=good
        negatives.append((kind,arr))

    qa={k:bool(v) for k,v in qa.items()}
    if not all(qa.values()):
        results=[]
        negative_results=[]
        diagnostics=[]
        decision="CONTROL_FAILURE"
    else:
        results=[]
        for family,cls,arr in positives:
            measured=outcome(classify_scene(arr),cls)
            results.append({"family":family,"known_truth":cls,**measured})
        negative_results=[]
        for kind,arr in negatives:
            measured=outcome(classify_scene(arr),None)
            negative_results.append({"kind":kind,**measured})

        # Old fixtures are in-sample, diagnostic-only; never decide via them.
        diagnostics=[]
        for family in ("curved","broken","curved_broken"):
            for cls in CLASSES:
                art,_meta=stage185_source_blind_scene(cls,family)
                diagnostic=outcome(classify_scene(art),cls)
                diagnostics.append({"family":family,"known_truth":cls,
                                    "correct_stable":diagnostic["correct_stable"],
                                    "wrong_stable":diagnostic["wrong_stable"],
                                    "abstained":diagnostic["abstained"]})

        wrong=sum(row["wrong_stable"] for row in results)
        false=sum(row["false_positive"] for row in negative_results)
        passed=all(row["correct_stable"]>=4 for row in results) and wrong==0 and false<=1
        decision=("STAGE186_HELDOUT_CALIBRATION_PRELIMINARILY_DISCRIMINATIVE"
                  if passed else "STAGE186_HELDOUT_CALIBRATION_INADEQUATE")

    output={
        "experiment_id":"A11-EXP-186",
        "pre_registration":"analysis/runs/stage186-hull-column-center-holdout/PREREGISTRATION.md",
        "canonical_sha256_provenance_only":digest,
        "original_artwork_pixels_read":NATURAL_PIXELS_READ,
        "frozen_detector":{"x_from_center_inclusive":[-26,+26],
                           "y_from_by_inclusive":[-5,+34],
                           "thresholds":list(THRESHOLDS),
                           "min_vertical_runs":3,"min_columns":16,
                           "min_column_span":32,"min_pair_x_separation":14,
                           "slope_sign":.12,"slope_level":.055,
                           "unanimous_8_readings":True},
        "synthetic_holdouts":{k:list(v) for k,v in STYLE_SPECS.items()},
        "qa":qa,"qa_passed":sum(qa.values()),"qa_total":len(qa),
        "known_holdout_results":results,"negative_holdout_results":negative_results,
        "stage185_in_sample_diagnostics_only":diagnostics,
        "decision":decision,
        "scope":"Source-blind synthetic detector validation only. No natural-image slope inference.",
        "safety":"No source pixels, keys, BIP39, wallets, addresses or off-image research."
    }
    (OUT/"result.json").write_text(json.dumps(output,indent=2,allow_nan=False)+"\n")
    lines=[
        "# Stage186 — independent source-blind hull-centroid slope calibration","",
        f"- Canonical SHA bytes (never pixels): **{digest==SHA}**",
        f"- Fixture/source controls: **{sum(qa.values())}/{len(qa)}**",
        f"- Final decision: **{decision}**","",
        "| Holdout | Truth | Correct /5 | Wrong /5 | Abstained /5 |",
        "|---|---|---:|---:|---:|"
    ]
    for r in results:
        lines.append(
            f"| {r['family']} | {r['known_truth']} | {r['correct_stable']} "
            f"| {r['wrong_stable']} | {r['abstained']} |")
    lines+=["","| Negative | False classifications /5 |",
            "|---|---:|"]
    for r in negative_results:
        lines.append(f"| {r['kind']} | {r['false_positive']} |")
    lines+=["","## Reused Stage185 synthetic scenes (diagnostic only)",
            "These were seen by the project before Stage186; not independent holdouts.",
            "", "| Family | Truth | Correct /5 | Wrong /5 | Abstained /5 |",
            "|---|---|---:|---:|---:|"]
    for r in diagnostics:
        lines.append(f"| {r['family']} | {r['known_truth']} | "
                     f"{r['correct_stable']} | {r['wrong_stable']} | {r['abstained']} |")
    lines+=["","A successful GitHub Actions status means the code ran, not that",
            "the detector's scientific validation passed. Fixed holdout rule:",
            "each of six positives >=4/5, zero confidently wrong among 30,",
            "and at most one false confident label across 15 negatives.",
            "No natural original puzzle-image pixels were read; no recovered",
            "message, author intent, symbol count, or cryptographic inference."]
    (OUT/"REPORT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"stage":186,"qa":f"{sum(qa.values())}/{len(qa)}",
                      "decision":decision,
                      "positive_correct":[(x["family"],x["known_truth"],x["correct_stable"])
                                          for x in results],
                      "negative_false":[(x["kind"],x["false_positive"])
                                         for x in negative_results]}))
    if decision=="CONTROL_FAILURE":
        raise SystemExit("CONTROL_FAILURE - repair Stage186 only; do not interpret scientific result")


if __name__=="__main__":
    main()
