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

**Stage 28 must be chosen from the combined Stage 23–27 evidence, not from an old fixed roadmap.**

Current best justified question:
> Are the Stage-27 traversal anomalies (printability/compressibility/signature hits) actually exceptional relative to matched null/surrogate streams, or are they expected from the highly biased and spatially correlated image bitplanes?

A good Stage 28 should null-calibrate those anomalies using shuffled or block-shuffled surrogate streams that preserve relevant marginal statistics, and should replace one-byte “magic” signatures with sufficiently specific multi-byte signatures.

## Status

- Stages 1–27: completed or superseded as recorded in their run folders.
- Adaptive controller: ACTIVE.
- Next stage: 28, to be designed only after explicit reasoning over Stage 22–27.
