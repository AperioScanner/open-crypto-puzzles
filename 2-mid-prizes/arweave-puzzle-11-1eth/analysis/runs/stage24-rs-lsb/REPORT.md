# Stage 24 — RS-style LSB diagnostics

**Experiment:** A11-EXP-024

The statistic compares regular/singular group asymmetry under positive and negative LSB flips. Synthetic LSB-replacement controls calibrate direction and scale.

## L channel

- original symmetry gap: **0.156190**
- original R-S positive: 0.673932
- original R-S negative: 0.830122

| synthetic LSB replacement | symmetry gap | R-S pos | R-S neg |
|---:|---:|---:|---:|
| 0.10 | 0.283810 | 0.540624 | 0.824434 |
| 0.25 | 0.445715 | 0.368557 | 0.814271 |
| 0.50 | 0.646086 | 0.153032 | 0.799118 |
| 1.00 | 0.766045 | 0.001471 | 0.767516 |

## A channel

- original symmetry gap: **0.000326**
- original R-S positive: 0.999656
- original R-S negative: 0.999982

| synthetic LSB replacement | symmetry gap | R-S pos | R-S neg |
|---:|---:|---:|---:|
| 0.10 | 0.189661 | 0.810312 | 0.999973 |
| 0.25 | 0.437176 | 0.562783 | 0.999959 |
| 0.50 | 0.749434 | 0.250498 | 0.999932 |
| 1.00 | 1.003167 | -0.003271 | 0.999896 |

## Interpretation

Similarity to a synthetic replacement control is evidence only of LSB statistical behavior, not proof of an embedded message. Strong differences from all controls weaken simple global LSB replacement as a carrier model.
