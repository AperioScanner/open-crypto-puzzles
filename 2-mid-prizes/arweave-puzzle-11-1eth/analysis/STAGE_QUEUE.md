# Arweave Puzzle #11 — adaptive stage controller

Last updated: 2026-10-03

This file replaces the fixed multi-stage queue. The research must now advance **adaptively, one stage at a time**.

## Required control loop

1. GitHub Actions executes exactly one experimental stage.
2. That stage writes its non-secret `REPORT.md` and `result.json` and commits them.
3. The ChatGPT research automation detects the newest completed, unreviewed stage.
4. ChatGPT reads the actual results, re-evaluates the hypothesis tree, records a reasoning/decision entry, and only then designs the next stage.
5. Pushing the new stage workflow starts GitHub Actions immediately.
6. Repeat.

A future stage must **not** be pre-scripted merely because it was once listed in a roadmap. The next experiment is chosen from the evidence produced by the previous one.

## Current evidence handoff

The one-off accelerated batch 22–27 completed before this controller correction. Treat those stages as a **single exploratory evidence batch**, not as proof that adaptive reasoning occurred between each of them.

Important results from that batch:

- Stage 22: retain the robust H/V texture as a visual lead, but **retire hexadecimal `0x321` as the primary interpretation**.
- Stage 23: low grayscale bitplanes remain strongly image-correlated; descriptive statistics alone do not show an obvious global random LSB payload.
- Stage 24: simple global LSB replacement is weakened; original RS-style behavior is far from the stronger synthetic replacement controls.
- Stage 25: low-bit anomalies are mostly localized in image-texture regions; alpha anomalies are dominated by the sparse alpha channel and need caution.
- Stage 26: strong low-frequency/spatial correlation is present across low grayscale planes; it may reflect drawing/render structure rather than payload.
- Stage 27: no traversal is strongly text-like (best printable fraction about 0.109, longest printable run 8). The previous one-byte JSON magic test creates many false-positive “magic” hits and must be recalibrated before using those hits as evidence.

## Next adaptive decision

**Stage 28 completed successfully and was adaptively reviewed.**

Observed against 100 matched 32×32 block-shuffled surrogates:
- max printable fraction = 0.109059, empirical p = **0.0099**
- min zlib ratio = 0.464995, empirical p = **0.0099**
- longest printable run = 8, p = 0.8416
- specific multi-byte magic signatures = 0

The anomaly is therefore not “obvious text,” but two independent global traversal metrics are unusually extreme relative to the matched surrogate family.

**Adaptive decision:** Stage 29 localizes the fixed promoted L-bit0 traversal anomaly in byte windows and compares the same canonical traversal across grayscale bitplanes 0–7. This distinguishes a localized/LSB-specific effect from ordinary multiscale image structure.

## Status

- Stages 1–27: completed or superseded as recorded in their run folders.
- Adaptive controller: ACTIVE.
- Stage 28: COMPLETED + ADAPTIVELY REVIEWED.
- Stage 29: QUEUED/RUNNING — localization + cross-bitplane reproduction.
