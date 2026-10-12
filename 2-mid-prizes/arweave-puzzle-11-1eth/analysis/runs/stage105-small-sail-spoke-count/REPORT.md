# Stage 105 — corrected small-sail radial-spoke audit

- detected sail centers: **[1042, 1148, 1282, 1372, 1490]**
- synthetic annulus counts 3..7: **[3, 4, 3, 3, 2]**
- synthetic scanline counts 3..7: **[3, 4, 5, 6, 2]**
- controls pass: **False**
- stable real sails: **2/5**
- stable sequence: **0 ? ? 0 ?**
- distinct counts: **[0]**
- promoted: **False**

| sail | box | count | stable | original annulus | original scanline |
|---:|:---|---:|:---:|---:|---:|
| 1 | [987, 345, 1095, 500] | 0 | True | 1 | 0 |
| 2 | [1095, 345, 1215, 500] |  | False | 2 | 0 |
| 3 | [1215, 345, 1327, 500] |  | False | 2 | 4 |
| 4 | [1327, 345, 1431, 500] | 0 | True | 0 | 0 |
| 5 | [1431, 345, 1550, 500] |  | False | 1 | 5 |

## Interpretation

The corrected detector still fails synthetic controls. Stage 105 remains an implementation failure; do not interpret real-sail counts.

No private-key material was generated or tested.
