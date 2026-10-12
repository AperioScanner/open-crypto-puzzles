# Stage 105 — five-small-sail radial-spoke count audit

**Experiment:** A11-EXP-105

- synthetic controls pass: **False**
- synthetic detected sequence for drawn 3..7 spokes: **[None, None, None, 4, 4]**
- stable real sails: **3/5**
- stable spoke sequence: **0 0 0 ? ?**
- distinct stable counts: **[0]**
- promoted: **False**

| sail | stable count | stable | orig Hough | orig radial |
|---:|---:|:---:|---:|---:|
| 1 | 0 | True | 0 | 0 |
| 2 | 0 | True | 0 | 0 |
| 3 | 0 | True | 0 | 0 |
| 4 |  | False | 3 | 0 |
| 5 |  | False | 4 | 0 |

## Interpretation

The synthetic spoke-count controls do not validate the detector. This is an implementation failure and must be fixed under Stage 105.

No private-key material was generated or tested.
