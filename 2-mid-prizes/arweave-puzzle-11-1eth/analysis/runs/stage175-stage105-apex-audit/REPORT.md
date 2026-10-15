# Stage175 — Stage105 old source apex and synthetic-control defect

- Canonical PNG SHA provenance: **True**
- Exact source/result guards: **18/18**
- Stage105 false apex positions ≥8 px from Stage153 true reference: **3/5**
- Stage105 original synthetic 3..7 spoke annulus counts: **[3, 4, 3, 3, 2]** (NOT monotonic)
- Stage105 original synthetic 3..7 scanline counts: **[3, 4, 5, 6, 2]** (NOT monotonic)
- Stage164 independently verified ≥20% real source ink omitted by old boxes: **3/5**
- Decision: **CONFIRMED_STAGE105_UNCALIBRATED_AND_WRONG_APEX_SOURCE**

| Sail | True tip | Stage105 inferred tip | Distance (px) | Missing cropped area |
|---|---|---|---:|---:|
| 1 | [1042, 448] | [1021.0, 347.0] | 103.2 | 74.8% |
| 2 | [1148, 433] | [1164.0, 347.0] | 87.5 | 56.2% |
| 3 | [1282, 411] | [1279.0, 407.0] | 5.0 | 25.2% |
| 4 | [1372, 397] | [1370.0, 347.0] | 50.0 | 0.0% |
| 5 | [1490, 357] | [1491.0, 360.0] | 3.2 | 0.0% |

Stage105 had failed its OWN synthetic controls; no source-confirmed counted spoke pattern was ever established by that stage. This is a metadata/geometry QA, not a new spoke count or cryptographic clue.
