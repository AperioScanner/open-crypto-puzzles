#!/usr/bin/env python3
"""Bounded alpha-anomaly sweep for Arweave Puzzle #11.

The public report never persists candidate private keys. If an exact target
address is detected, the script emits only a generic MATCH_DETECTED marker and
exits nonzero so the derivation can be reproduced later in a private context.
"""
from __future__ import annotations

import hashlib
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image
from eth_keys import keys
from Crypto.Hash import keccak

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "clues" / "arweave-puzzle-11.png"
OUT = ROOT / "analysis" / "runs" / "stage2-alpha"
EXPECTED_SHA256 = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
TARGET = "ff2142e98e09b5344994f9beb9c56c95506b9f17"
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
KNOWN = bytes([1]) * 32
KNOWN_ADDR = "1a642f0e3c3af545e7acbd38b07251b3990914f1"


def address(raw: bytes) -> str | None:
    if len(raw) != 32:
        return None
    scalar = int.from_bytes(raw, "big")
    if not 0 < scalar < ORDER:
        return None
    return keys.PrivateKey(raw).public_key.to_canonical_address().hex()


def connected_components(mask: np.ndarray) -> list[dict]:
    coords = set(map(tuple, np.argwhere(mask)))
    comps = []
    while coords:
        seed = coords.pop()
        q = deque([seed])
        pts = [seed]
        while q:
            y, x = q.popleft()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if not (dx or dy):
                        continue
                    p = (y + dy, x + dx)
                    if p in coords:
                        coords.remove(p)
                        q.append(p)
                        pts.append(p)
        ys = [p[0] for p in pts]
        xs = [p[1] for p in pts]
        comps.append({
            "size": len(pts),
            "bbox": [min(xs), min(ys), max(xs), max(ys)],
            "points": pts,
        })
    comps.sort(key=lambda c: c["size"], reverse=True)
    return comps


def ordered_records(A: np.ndarray) -> dict[str, list[tuple[int,int,int,int]]]:
    ys, xs = np.where(A < 255)
    rec = [(int(x), int(y), int(A[y, x]), int(255 - A[y, x])) for y, x in zip(ys, xs)]
    by_row = sorted(rec, key=lambda r: (r[1], r[0]))
    by_col = sorted(rec, key=lambda r: (r[0], r[1]))

    # Sparse serpentine traversals: alternate direction within occupied rows/columns.
    rows = {}
    for r in rec:
        rows.setdefault(r[1], []).append(r)
    serp_row = []
    for i, y in enumerate(sorted(rows)):
        rr = sorted(rows[y], key=lambda r: r[0], reverse=bool(i & 1))
        serp_row.extend(rr)

    cols = {}
    for r in rec:
        cols.setdefault(r[0], []).append(r)
    serp_col = []
    for i, x in enumerate(sorted(cols)):
        rr = sorted(cols[x], key=lambda r: r[1], reverse=bool(i & 1))
        serp_col.extend(rr)

    return {
        "row": by_row,
        "row_rev": list(reversed(by_row)),
        "col": by_col,
        "col_rev": list(reversed(by_col)),
        "serp_row": serp_row,
        "serp_row_rev": list(reversed(serp_row)),
        "serp_col": serp_col,
        "serp_col_rev": list(reversed(serp_col)),
    }


def symbols_to_bits(values: list[int], width: int, bit_order: str) -> np.ndarray:
    bits = np.empty(len(values) * width, dtype=np.uint8)
    k = 0
    for v in values:
        rng = range(width - 1, -1, -1) if bit_order == "msb" else range(width)
        for b in rng:
            bits[k] = (v >> b) & 1
            k += 1
    return bits


def bits_to_bytes(bits: np.ndarray) -> bytes:
    usable = (len(bits) // 8) * 8
    if usable <= 0:
        return b""
    return np.packbits(bits[:usable], bitorder="big").tobytes()


def iter_bit_windows(bits: np.ndarray):
    # Every possible bit start, not merely byte aligned.
    n = len(bits)
    for start in range(0, n - 255):
        raw = np.packbits(bits[start:start+256], bitorder="big").tobytes()
        yield start, raw


def iter_byte_windows(data: bytes):
    for start in range(0, len(data) - 31):
        yield start * 8, data[start:start+32]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA256:
        raise SystemExit(f"wrong source sha256: {sha}")

    a = np.array(Image.open(SOURCE))
    if a.shape != (1105, 1600, 2):
        raise SystemExit(f"unexpected image shape: {a.shape}")
    A = a[:, :, 1].astype(np.uint8)
    mask = A < 255

    # Cryptographic positive control.
    assert address(KNOWN) == KNOWN_ADDR

    comps = connected_components(mask)
    orders = ordered_records(A)
    seen: set[bytes] = set()
    checked = 0
    near_ff21 = 0
    family_counts: dict[str, int] = {}
    exact_match = False

    def check(raw: bytes, family: str):
        nonlocal checked, near_ff21, exact_match
        if raw in seen:
            return
        seen.add(raw)
        addr = address(raw)
        if addr is None:
            return
        checked += 1
        family_counts[family] = family_counts.get(family, 0) + 1
        if addr.startswith("ff21"):
            near_ff21 += 1
        if addr == TARGET:
            exact_match = True
            # Do not record candidate or transform details in a public artifact.

    for order_name, recs in orders.items():
        alpha = [r[2] for r in recs]
        deficit = [r[3] for r in recs]
        alpha5 = [v & 31 for v in alpha]          # observed 1..30
        deficit5 = [v & 31 for v in deficit]      # complementary 1..30
        deficit0 = [(v - 1) & 31 for v in deficit]  # 0..29 normalization

        # Direct byte windows.
        for label, vals in [
            ("alpha8", alpha),
            ("deficit8", deficit),
            ("alpha5_as_byte", alpha5),
            ("deficit5_as_byte", deficit5),
            ("deficit0_as_byte", deficit0),
        ]:
            data = bytes(vals)
            for _, raw in iter_byte_windows(data):
                check(raw, f"{order_name}:{label}:bytewin")
                check(raw[::-1], f"{order_name}:{label}:bytewin:scalar-rev")
                if exact_match:
                    break
            if exact_match:
                break
        if exact_match:
            break

        # Packed symbol streams, widths 1..5. For widths <5 use low bits.
        reps = [
            ("alpha_low", alpha5),
            ("deficit", deficit5),
            ("deficit0", deficit0),
        ]
        for rep_name, vals in reps:
            for width in range(1, 6):
                maskv = (1 << width) - 1
                clipped = [v & maskv for v in vals]
                for bit_order in ("msb", "lsb"):
                    bits = symbols_to_bits(clipped, width, bit_order)
                    for _, raw in iter_bit_windows(bits):
                        check(raw, f"{order_name}:{rep_name}:w{width}:{bit_order}:bitwin")
                        check(raw[::-1], f"{order_name}:{rep_name}:w{width}:{bit_order}:bitwin:scalar-rev")
                        if exact_match:
                            break
                    if exact_match:
                        break
                if exact_match:
                    break
            if exact_match:
                break
        if exact_match:
            break

        # Whole-sequence hashes under several byte representations.
        for label, vals in [
            ("alpha8", alpha), ("deficit8", deficit),
            ("alpha5", alpha5), ("deficit5", deficit5), ("deficit0", deficit0)
        ]:
            data = bytes(vals)
            for hname, raw in [
                ("sha256", hashlib.sha256(data).digest()),
                ("sha256-rev", hashlib.sha256(data[::-1]).digest()),
                ("keccak256", keccak.new(digest_bits=256, data=data).digest()),
                ("keccak256-rev", keccak.new(digest_bits=256, data=data[::-1]).digest()),
            ]:
                check(raw, f"{order_name}:{label}:{hname}")
                if exact_match:
                    break
            if exact_match:
                break
        if exact_match:
            break

    comp_public = [
        {"size": c["size"], "bbox": c["bbox"]}
        for c in comps
    ]

    result = {
        "source_sha256": sha,
        "alpha_non255_count": int(mask.sum()),
        "alpha_min": int(A.min()),
        "alpha_max": int(A.max()),
        "deficit_min": int((255-A[mask]).min()),
        "deficit_max": int((255-A[mask]).max()),
        "component_count": len(comps),
        "components": comp_public,
        "orders_tested": list(orders),
        "unique_candidate_scalars_seen": len(seen),
        "valid_scalars_checked": checked,
        "near_ff21_addresses": near_ff21,
        "family_counts": family_counts,
        "exact_match_detected": exact_match,
        "scope": [
            "all 434 alpha!=255 pixels",
            "8 spatial orders including reverse and sparse serpentine variants",
            "direct 8-bit and low-5-bit byte windows",
            "packed low-bit symbol widths 1..5, MSB/LSB symbol order",
            "every 256-bit start position in packed streams",
            "normal and reversed 32-byte scalar order",
            "SHA-256 and Keccak-256 of whole ordered symbol sequences",
        ],
        "security_note": "No candidate private key or winning transform is persisted.",
    }

    if exact_match:
        # Do not write the normal report: even a family breakdown after a hit can
        # materially narrow reproduction in a public repository.
        print("MATCH_DETECTED")
        raise SystemExit(78)

    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Stage 2 alpha-anomaly sweep",
        "",
        f"- Alpha pixels below 255: {result['alpha_non255_count']}",
        f"- Deficit range (255-alpha): {result['deficit_min']}..{result['deficit_max']}",
        f"- Connected components: {result['component_count']}",
        f"- Unique 32-byte candidates generated: {result['unique_candidate_scalars_seen']}",
        f"- Valid secp256k1 scalars checked: {result['valid_scalars_checked']}",
        f"- Addresses beginning ff21: {result['near_ff21_addresses']}",
        f"- Exact target match: **{result['exact_match_detected']}**",
        "",
        "## Largest alpha components",
        "",
        "| size | bbox x0,y0,x1,y1 |",
        "|---:|---|",
    ]
    for c in comp_public[:20]:
        lines.append(f"| {c['size']} | {','.join(map(str,c['bbox']))} |")
    lines += [
        "",
        "No private-key candidate is stored in this public report.",
        "",
    ]
    (OUT / "REPORT.md").write_text("\n".join(lines))
    print(json.dumps({
        "status": "exhausted-no-match",
        "valid_scalars_checked": checked,
        "unique_candidates": len(seen),
        "components": len(comps),
    }))


if __name__ == "__main__":
    main()
