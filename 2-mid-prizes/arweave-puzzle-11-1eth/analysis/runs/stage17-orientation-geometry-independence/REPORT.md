# Stage 17 — is hatch orientation explained by building geometry?

**Experiment:** A11-EXP-017

Fixed skyline sequence: HHVVHHVHHHHV; vertical-hatched buildings: [3, 4, 7, 12].
All p-values are exact over the 495 possible placements of four V labels among 12 buildings.

| feature | abs mean difference (V-H) | exact two-sided p | best-direction AUC |
|:---|---:|---:|---:|
| width | 32.2500 | 0.1273 | 0.562 |
| area | 8783.7500 | 0.1798 | 0.719 |
| aspect_width_over_height | 0.0761 | 0.5192 | 0.594 |
| height | 18.1250 | 0.5980 | 0.641 |
| roof_y | 16.6250 | 0.6444 | 0.594 |
| x_center | 46.8750 | 0.8727 | 0.500 |

- Smallest raw p: **0.1273** (width)
- Bonferroni correction across 6 pre-defined features: **0.7636**

## Interpretation

No tested simple geometric feature predicts H/V orientation at corrected 5% significance. This argues against the easiest shape/position explanation, while still not proving intentional encoding.

This test addresses the H/V structure itself, not whether the post-hoc hexadecimal reading 0x321 is correct.
