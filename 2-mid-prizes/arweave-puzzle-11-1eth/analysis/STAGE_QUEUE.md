# Arweave Puzzle #11 — stage queue

Last updated: 2026-10-03

This queue is the coordination plan for the safe research scope on `research/arweave11-chatgpt`.
GitHub Actions only shows a run after that stage has actually been dispatched; planned stages below
are therefore visible here before they appear in the Actions run list.

## Current

| Stage | Status | Purpose |
|---|---|---|
| 21 | QUEUED/RUNNING | Independently replicate the 12-building H/V texture sequence with Fourier anisotropy and morphological line-response classifiers, without reusing the Stage-5 Sobel decision rule. |

## Exhaust the visual `321` family first

| Stage | Status | Purpose |
|---|---|---|
| 22 | NEXT | Final evidence synthesis + stop rule for the specific `0x321` interpretation. Combine Stages 10, 13, 15, 16, 17, 20 and 21. Keep the H/V texture lead separate from the post-hoc hexadecimal interpretation. If no independent 321 corroboration remains, retire `0x321` as the primary visual hypothesis. |

## Then pivot to bit-level steganalysis

| Stage | Status | Purpose |
|---|---|---|
| 23 | PLANNED | LSB/MSB statistical steganalysis: per-bitplane entropy, balance, pair-of-values / chi-square style tests, grayscale-vs-alpha comparisons and region controls. No key derivation. |
| 24 | PLANNED | RS-style LSB steganalysis and local embedding-rate diagnostics on grayscale regions, with synthetic controls. |
| 25 | PLANNED | Local entropy / anomaly maps by bitplane and residual channel; identify spatially localized carriers rather than brute-force bitstreams. |
| 26 | PLANNED | 2-D autocorrelation and Fourier/spectral analysis of bitplanes/residuals; test periodic, tiled, row/column and serpentine structure. |
| 27 | PLANNED | Traversal-order diagnostics (row-major, column-major, serpentine, rotations/reflections) using compressibility, byte statistics, printable-text rates and file-signature evidence only; no private-key reconstruction or wallet verification. |

## Decision rule

Stages 21–22 finish the visual `321` route. Unless Stage 21 produces a materially new independent
visual confirmation that survives the Stage-22 stop rule, Stage 23 begins the statistical
bit-level steganalysis route.

The queue may be refined when a stage produces evidence that materially changes the next best test.
