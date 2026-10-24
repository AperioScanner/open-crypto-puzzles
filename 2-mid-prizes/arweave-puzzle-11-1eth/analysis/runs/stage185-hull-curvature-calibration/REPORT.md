# Stage185 — Stage127 curved/broken hull source-blind calibration

- Original PNG SHA provenance correct: **True**
- QA: **44/44**
- New synthetic source-like fixture scenes: **9** (5 hulls per scene)
- Instrument recovery all nine scenes >=4/5: **False**
- Decision: **STAGE127_SOURCE_LIKE_POSITIVE_RECOVERY_INADEQUATE**

| Controlled hull stroke style | True hull line sign | Correct stable / 5 | Wrong / 5 | Abstained / 5 |
|---|---|---:|---:|---:|
| curved | UP_RIGHT | 5 | 0 | 0 |
| curved | LEVEL | 1 | 0 | 4 |
| curved | DOWN_RIGHT | 3 | 0 | 2 |
| broken | UP_RIGHT | 5 | 0 | 0 |
| broken | LEVEL | 5 | 0 | 0 |
| broken | DOWN_RIGHT | 5 | 0 | 0 |
| curved_broken | UP_RIGHT | 2 | 0 | 3 |
| curved_broken | LEVEL | 0 | 0 | 5 |
| curved_broken | DOWN_RIGHT | 2 | 0 | 3 |

The test runs on invented white synthetic scenes only. A detector failure means its old real-source abstention cannot exclude true hull-slope variation. A positive source-like control would still NOT establish author intent or any code. Unmodified original Stage127 files remain archived.
