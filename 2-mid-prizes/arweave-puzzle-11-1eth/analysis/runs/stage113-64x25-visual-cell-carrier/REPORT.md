# Stage 113 — 64 × 25 px visual-cell carrier audit

**Experiment:** A11-EXP-113

- exact relation: **1600 = 64 × 25**
- positive control pass: **True**
- negative control pass: **True**
- controls pass: **True**
- real phase-0 rank: **21/25**
- real k=16 silhouette: **0.3499**
- real k=16 cross-variant stability: **0.9948**
- occupied k=16 states: **16/16**
- singleton states: **3**
- best k by silhouette: **8**
- k=16 silhouette rank: **14/19**
- k=16 effectively tied with best: **False**
- real structural gate: **False**
- promoted: **False**

## Top phase scores

| rank | phase | score | silhouette16 | stability | occupied | singletons |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | 0.33106 | 0.3650 | 0.9896 | 16 | 1 |
| 2 | 8 | 0.32737 | 0.3609 | 0.9896 | 16 | 1 |
| 3 | 4 | 0.32060 | 0.3516 | 0.9948 | 16 | 1 |
| 4 | 2 | 0.30863 | 0.3119 | 0.9896 | 16 | 0 |
| 5 | 10 | 0.30699 | 0.3366 | 0.9948 | 16 | 1 |

## Interpretation

The exact 64×25 partition does not satisfy the predeclared carrier-structure gates. Retire simple one-hex-symbol-per-25px vertical-cell encoding.

No ordered 64-cell symbol sequence is stored or printed.
No private-key material was generated, reconstructed or tested.
