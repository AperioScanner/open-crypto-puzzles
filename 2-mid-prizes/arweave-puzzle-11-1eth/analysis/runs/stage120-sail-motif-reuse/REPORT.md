# Stage 120 — five-sail interior motif-reuse test

- Scope: image-only; checks repeated interior pen strokes, not widths/directions or cryptographic values.
- Canonical PNG SHA256 verified: **True**
- Synthetic duplicate/redraw controls: **True**
- Detector stable across image variants: **True**, drift **2px**
- Independent-redraw maximum: **0.0514**
- Pair matching cutoff: **0.1800** plus **25** RANSAC inliers
- Replicated repeated-stroke pairs: **0**
- Decision: **NO_EXACT_STROKE_TEMPLATE_REUSE**

| sails | original inliers | original fraction | passing variants/4 |
|:---|---:|---:|---:|
| 1–2 | 3 | 0.010 | 0/4 |
| 1–3 | 0 | 0.000 | 0/4 |
| 1–4 | 2 | 0.007 | 0/4 |
| 1–5 | 4 | 0.013 | 0/4 |
| 2–3 | 7 | 0.013 | 0/4 |
| 2–4 | 4 | 0.008 | 0/4 |
| 2–5 | 3 | 0.006 | 0/4 |
| 3–4 | 3 | 0.005 | 0/4 |
| 3–5 | 3 | 0.005 | 0/4 |
| 4–5 | 4 | 0.006 | 0/4 |

## Interpretation

No replicated, affine-compatible identical pen-stroke template among the five sails under calibrated controls. Retire *direct graphic duplication only*; do not infer that sail symbols are meaningless.

No keys, mnemonic words, secret candidates, or wallet operations were generated or evaluated.
