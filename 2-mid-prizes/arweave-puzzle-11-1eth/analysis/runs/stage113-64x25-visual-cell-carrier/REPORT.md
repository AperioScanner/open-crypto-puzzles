# Stage 113 — 64 × 25 px visual-cell carrier audit

**Experiment:** A11-EXP-113

- exact relation: **1600 = 64 × 25**
- positive control pass: **False**
- negative control pass: **True**
- controls pass: **False**
- real phase-0 rank: **23/25**
- real k=16 silhouette: **0.3046**
- real k=16 cross-variant stability: **0.9896**
- occupied k=16 states: **16/16**
- singleton states: **2**
- best k by silhouette: **8**
- k=16 silhouette rank: **18/19**
- k=16 effectively tied with best: **False**
- real structural gate: **False**
- promoted: **False**

## Top phase scores

| rank | phase | score | silhouette16 | stability | occupied | singletons |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 9 | 0.34345 | 0.3434 | 1.0000 | 16 | 0 |
| 2 | 2 | 0.32988 | 0.3369 | 0.9792 | 16 | 0 |
| 3 | 8 | 0.31238 | 0.3444 | 0.9896 | 16 | 1 |
| 4 | 1 | 0.31093 | 0.3428 | 0.9896 | 16 | 1 |
| 5 | 10 | 0.30402 | 0.3072 | 0.9896 | 16 | 0 |

## Interpretation

The carrier-structure harness failed its synthetic controls. Stage 113 is an implementation failure and must be repaired under the same stage number before interpreting Puzzle #11.

No ordered 64-cell symbol sequence is stored or printed.
No private-key material was generated, reconstructed or tested.
