# Stage 10 — skyline 0x321 marker robustness

**Experiment:** A11-EXP-010

This is a visual-only experiment. It does not generate, derive, or verify any private-key material.

- Baseline H/V sequence: `HHVVHHVHHHHV`
- H=0, V=1: `001100100001` = `0x321`
- All tested inner-margin choices preserved the exact sequence: **True**
- Worst exact-sequence preservation across bounded box jitter radii: **0.850**
- Mean per-building baseline-class fraction under ±24 px local shifts: **0.979**

## Margin robustness

| inner margin | sequence | exact baseline |
|---:|:---:|:---:|
| 0.06 | HHVVHHVHHHHV | True |
| 0.08 | HHVVHHVHHHHV | True |
| 0.10 | HHVVHHVHHHHV | True |
| 0.12 | HHVVHHVHHHHV | True |
| 0.14 | HHVVHHVHHHHV | True |
| 0.16 | HHVVHHVHHHHV | True |
| 0.18 | HHVVHHVHHHHV | True |
| 0.20 | HHVVHHVHHHHV | True |
| 0.22 | HHVVHHVHHHHV | True |

## Bounding-box jitter robustness

| jitter radius | trials | exact sequence fraction | mean Hamming distance | mixed-class runs |
|---:|---:|---:|---:|---:|
| ±1 px | 400 | 1.000 | 0.000 | 0 |
| ±2 px | 400 | 1.000 | 0.000 | 0 |
| ±4 px | 400 | 1.000 | 0.000 | 0 |
| ±8 px | 400 | 1.000 | 0.000 | 0 |
| ±12 px | 400 | 0.943 | 0.058 | 23 |
| ±16 px | 400 | 0.850 | 0.150 | 60 |

## Interpretation

The purpose of this run is to test whether the visually recovered `0x321` marker is an artifact of exact crop coordinates.
High stability would support treating `321` as a genuine image-level clue or instruction; it would **not** prove what the clue means or establish that it is intentional.
The author explicitly pointed solvers toward solved puzzles, whose documented solutions rely heavily on robust human-readable visual semantics rather than fragile file-format details. That makes crop-invariant visual structure more relevant than container-specific noise.
