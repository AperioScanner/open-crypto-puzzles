# Stage186 — independent source-blind hull-centroid slope calibration

- Canonical SHA bytes (never pixels): **True**
- Fixture/source controls: **18/18**
- Final decision: **STAGE186_HELDOUT_CALIBRATION_INADEQUATE**

| Holdout | Truth | Correct /5 | Wrong /5 | Abstained /5 |
|---|---|---:|---:|---:|
| holdout_A | UP_RIGHT | 1 | 0 | 4 |
| holdout_A | LEVEL | 5 | 0 | 0 |
| holdout_A | DOWN_RIGHT | 0 | 0 | 5 |
| holdout_B | UP_RIGHT | 2 | 0 | 3 |
| holdout_B | LEVEL | 5 | 0 | 0 |
| holdout_B | DOWN_RIGHT | 2 | 0 | 3 |

| Negative | False classifications /5 |
|---|---:|
| blank | 0 |
| single_diagonal | 0 |
| opposing_two_diagonals | 0 |

## Reused Stage185 synthetic scenes (diagnostic only)
These were seen by the project before Stage186; not independent holdouts.

| Family | Truth | Correct /5 | Wrong /5 | Abstained /5 |
|---|---|---:|---:|---:|
| curved | UP_RIGHT | 0 | 0 | 5 |
| curved | LEVEL | 5 | 0 | 0 |
| curved | DOWN_RIGHT | 0 | 0 | 5 |
| broken | UP_RIGHT | 0 | 0 | 5 |
| broken | LEVEL | 4 | 0 | 1 |
| broken | DOWN_RIGHT | 0 | 0 | 5 |
| curved_broken | UP_RIGHT | 1 | 0 | 4 |
| curved_broken | LEVEL | 5 | 0 | 0 |
| curved_broken | DOWN_RIGHT | 0 | 0 | 5 |

A successful GitHub Actions status means the code ran, not that
the detector's scientific validation passed. Fixed holdout rule:
each of six positives >=4/5, zero confidently wrong among 30,
and at most one false confident label across 15 negatives.
No natural original puzzle-image pixels were read; no recovered
message, author intent, symbol count, or cryptographic inference.
