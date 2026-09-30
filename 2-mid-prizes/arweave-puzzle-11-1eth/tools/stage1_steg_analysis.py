#!/usr/bin/env python3
"""Stage 1 structural steganalysis for Arweave Puzzle #11.

This stage deliberately does NOT emit or persist any private-key candidate.
It measures carrier structure, ranks alternate reshape widths, and creates
non-secret diagnostic images/reports that can guide bounded key searches.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "clues" / "arweave-puzzle-11.png"
OUT = ROOT / "analysis" / "runs" / "stage1-steg"
EXPECTED_SHA256 = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"


def entropy01(bits: np.ndarray) -> float:
    p = float(np.mean(bits))
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def serial_flip_rate(bits: np.ndarray) -> float:
    flat = bits.ravel()
    if flat.size < 2:
        return 0.0
    return float(np.mean(flat[1:] != flat[:-1]))


def pair_chi_square(values: np.ndarray) -> float:
    """Westfeld-style even/odd pair imbalance statistic (lower can mean LSB replacement)."""
    hist = np.bincount(values.ravel(), minlength=256).astype(np.float64)
    even = hist[0::2]
    odd = hist[1::2]
    den = even + odd
    keep = den > 0
    if not np.any(keep):
        return 0.0
    return float(np.sum(((even[keep] - odd[keep]) ** 2) / den[keep]))


def neighbor_stats(bits: np.ndarray) -> dict:
    h = float(np.mean(bits[:, 1:] != bits[:, :-1])) if bits.shape[1] > 1 else 0.0
    v = float(np.mean(bits[1:, :] != bits[:-1, :])) if bits.shape[0] > 1 else 0.0
    return {"horizontal_flip": h, "vertical_flip": v, "anisotropy": abs(h - v)}


def divisors(n: int, lo: int = 32, hi: int = 8192) -> list[int]:
    out = set()
    r = int(math.isqrt(n))
    for d in range(1, r + 1):
        if n % d == 0:
            q = n // d
            if lo <= d <= hi:
                out.add(d)
            if lo <= q <= hi:
                out.add(q)
    return sorted(out)


def lag_agreement(signal: np.ndarray, lag: int) -> float:
    a = signal[:-lag]
    b = signal[lag:]
    if a.size == 0:
        return 0.0
    return float(np.mean(a == b))


def lag_corr(values: np.ndarray, lag: int) -> float:
    a = values[:-lag].astype(np.float64)
    b = values[lag:].astype(np.float64)
    if a.size == 0:
        return 0.0
    a -= a.mean()
    b -= b.mean()
    den = float(np.sqrt(np.dot(a, a) * np.dot(b, b)))
    if den == 0:
        return 0.0
    return float(np.dot(a, b) / den)


def save_mask(mask: np.ndarray, width: int, name: str) -> str:
    h = mask.size // width
    arr = mask[: h * width].reshape(h, width)
    im = Image.fromarray(np.where(arr, 0, 255).astype(np.uint8), mode="L")
    # Keep previews manageable while preserving geometry.
    if im.width > 2400 or im.height > 2400:
        im.thumbnail((2400, 2400))
    dest = OUT / "previews" / f"{name}-w{width}-h{h}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, optimize=True)
    return str(dest.relative_to(ROOT))


def block_anomalies(channel: np.ndarray, bit: int, block: int = 32, topk: int = 40) -> list[dict]:
    bits = ((channel >> bit) & 1).astype(np.uint8)
    global_p = float(bits.mean())
    rows = []
    for y in range(0, bits.shape[0], block):
        for x in range(0, bits.shape[1], block):
            tile = bits[y:y+block, x:x+block]
            if tile.size < 64:
                continue
            p = float(tile.mean())
            # Binomial-style standardized deviation from global p.
            var = max(global_p * (1-global_p) / tile.size, 1e-12)
            z = abs(p - global_p) / math.sqrt(var)
            ns = neighbor_stats(tile)
            rows.append({
                "x": x, "y": y, "w": int(tile.shape[1]), "h": int(tile.shape[0]),
                "ones_ratio": p, "z_from_global": z,
                "hflip": ns["horizontal_flip"], "vflip": ns["vertical_flip"],
                "anisotropy": ns["anisotropy"],
            })
    rows.sort(key=lambda r: (r["z_from_global"], r["anisotropy"]), reverse=True)
    return rows[:topk]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw = SOURCE.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_SHA256:
        raise SystemExit(f"wrong source sha256: {sha}")

    a = np.array(Image.open(SOURCE))
    if a.shape != (1105, 1600, 2):
        raise SystemExit(f"unexpected image shape: {a.shape}")
    L = a[:, :, 0].astype(np.uint8)
    A = a[:, :, 1].astype(np.uint8)
    n = L.size
    widths = divisors(n)

    report: dict = {
        "source": {
            "sha256": sha,
            "shape": list(a.shape),
            "pixels": int(n),
            "candidate_reshape_widths": widths,
        },
        "channels": {},
        "alpha": {},
        "reshape_rankings": {},
        "block_anomalies": {},
        "notes": [
            "No private-key candidate is printed or stored by this stage.",
            "Reshape rankings scan every exact divisor width 32..8192, not only a hand-picked subset.",
            "High rank is a lead generator, not evidence of a hidden key."
        ],
    }

    for name, ch in [("L", L), ("A", A)]:
        chrep = {
            "min": int(ch.min()), "max": int(ch.max()),
            "mean": float(ch.mean()), "std": float(ch.std()),
            "pair_chi_square": pair_chi_square(ch),
            "bitplanes": [],
        }
        for bit in range(8):
            bp = ((ch >> bit) & 1).astype(np.uint8)
            ns = neighbor_stats(bp)
            chrep["bitplanes"].append({
                "bit": bit,
                "ones_ratio": float(bp.mean()),
                "entropy": entropy01(bp),
                "serial_flip_rate": serial_flip_rate(bp),
                **ns,
            })
        report["channels"][name] = chrep

    ys, xs = np.where(A < 255)
    report["alpha"] = {
        "non255_count": int(xs.size),
        "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if xs.size else None,
        "distinct_non255": sorted(int(x) for x in np.unique(A[A < 255])),
    }

    # Block-local anomalies for the low four grayscale planes and alpha LSB.
    for bit in range(4):
        report["block_anomalies"][f"L_bit{bit}"] = block_anomalies(L, bit)
    report["block_anomalies"]["A_bit0"] = block_anomalies(A, 0)

    flatL = L.ravel()
    flatA = A.ravel()
    masks = {
        "L_240_245": ((flatL >= 240) & (flatL <= 245)),
        "L_235_254": ((flatL >= 235) & (flatL <= 254)),
        "L_248_254": ((flatL >= 248) & (flatL <= 254)),
        "L_dark_110": (flatL <= 110),
        "A_non255": (flatA < 255),
        "L_bit0": ((flatL & 1) != 0),
        "L_bit1": (((flatL >> 1) & 1) != 0),
        "L_bit2": (((flatL >> 2) & 1) != 0),
        "L_bit3": (((flatL >> 3) & 1) != 0),
    }

    # Rank exact reshapes by vertical agreement at the implied row width.
    # A true prior row width can produce unusually strong lag structure.
    preview_candidates = []
    for name, sig in masks.items():
        rows = []
        baseline = float(np.mean(sig))
        for w in widths:
            agree = lag_agreement(sig, w)
            # Remove trivial agreement expected purely from class imbalance.
            expected = baseline * baseline + (1-baseline) * (1-baseline)
            lift = agree - expected
            rows.append({
                "width": int(w), "height": int(n // w),
                "agreement": agree, "expected_random": expected, "lift": lift,
            })
        rows.sort(key=lambda r: abs(r["lift"]), reverse=True)
        report["reshape_rankings"][name] = rows[:20]
        for row in rows[:3]:
            if row["height"] >= 16:
                preview_candidates.append((abs(row["lift"]), name, sig, row["width"]))

    # Continuous grayscale autocorrelation at every exact reshape width.
    gray_rows = []
    for w in widths:
        gray_rows.append({"width": int(w), "height": int(n // w), "corr": lag_corr(flatL, w)})
    gray_rows.sort(key=lambda r: abs(r["corr"]), reverse=True)
    report["reshape_rankings"]["L_continuous_corr"] = gray_rows[:30]

    # Save only the strongest unique diagnostic previews.
    previews = []
    used = set()
    for score, name, sig, w in sorted(preview_candidates, reverse=True):
        key = (name, w)
        if key in used:
            continue
        used.add(key)
        previews.append({"mask": name, "width": int(w), "score": float(score),
                         "path": save_mask(sig, w, name)})
        if len(previews) >= 18:
            break
    report["previews"] = previews

    (OUT / "stage1.json").write_text(json.dumps(report, indent=2) + "\n")

    md = [
        "# Stage 1 steganalysis report",
        "",
        f"- Source SHA-256: `{sha}`",
        f"- Image: {a.shape[1]}×{a.shape[0]}, grayscale + alpha",
        f"- Exact reshape widths scanned: {len(widths)}",
        f"- Alpha pixels <255: {xs.size}",
        "",
        "## Strongest alternate-reshape leads",
        "",
    ]
    for key in ["L_240_245", "L_235_254", "L_248_254", "L_dark_110", "L_bit0", "L_bit1", "L_bit2", "L_bit3", "A_non255"]:
        md.append(f"### {key}")
        md.append("")
        md.append("| width | height | agreement lift |")
        md.append("|---:|---:|---:|")
        for row in report["reshape_rankings"][key][:8]:
            md.append(f"| {row['width']} | {row['height']} | {row['lift']:.8f} |")
        md.append("")
    md += [
        "## Continuous grayscale lag correlation",
        "",
        "| width | height | correlation |",
        "|---:|---:|---:|",
    ]
    for row in gray_rows[:15]:
        md.append(f"| {row['width']} | {row['height']} | {row['corr']:.8f} |")
    md += [
        "",
        "## Interpretation",
        "",
        "These are anomaly rankings only. A width or bitplane is not considered a solution unless a later bounded decoder yields a 32-byte scalar whose Ethereum address exactly matches the target.",
        "",
        "No private key or private-key candidate is stored by this stage.",
        "",
    ]
    (OUT / "REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status": "ok",
        "report": str((OUT / "REPORT.md").relative_to(ROOT)),
        "json": str((OUT / "stage1.json").relative_to(ROOT)),
        "previews": len(previews),
        "widths_scanned": len(widths),
    }))


if __name__ == "__main__":
    main()

# Workflow trigger marker: 2026-09-30
