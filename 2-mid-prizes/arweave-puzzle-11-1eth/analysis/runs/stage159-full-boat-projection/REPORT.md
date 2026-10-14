# Stage159 — audit Stage12 old large-boat projection with full source

- PNG SHA correct: **True**
- Stage12 old x/y projection exact replay: **True**
- Flat shape / x-period12 controls: **24/24**
- Five-source? No: true FULL LARGE sail + hull mask with 7px box pad.
- Corrected x lag3 shape explanation stable 12/12: **True**
- Decision: **SOURCE_LAG3_COMPATIBLE_WITH_FULL_BOAT_SILHOUETTE**

| Format/threshold | real x lag/score | flat x lag/score | score difference |
|---|---|---|---|
| original t110 | 3 / 0.976 | 3 / 0.981 | 0.006 |
| original t140 | 3 / 0.978 | 3 / 0.981 | 0.004 |
| original t170 | 3 / 0.980 | 3 / 0.981 | 0.001 |
| jpeg85 t110 | 3 / 0.976 | 3 / 0.981 | 0.006 |
| jpeg85 t140 | 3 / 0.977 | 3 / 0.981 | 0.004 |
| jpeg85 t170 | 3 / 0.980 | 3 / 0.981 | 0.001 |
| jpeg70 t110 | 3 / 0.976 | 3 / 0.981 | 0.006 |
| jpeg70 t140 | 3 / 0.978 | 3 / 0.981 | 0.004 |
| jpeg70 t170 | 3 / 0.980 | 3 / 0.981 | 0.002 |
| down75_up t110 | 3 / 0.975 | 3 / 0.981 | 0.007 |
| down75_up t140 | 3 / 0.978 | 3 / 0.981 | 0.004 |
| down75_up t170 | 3 / 0.980 | 3 / 0.981 | 0.001 |

The source ROI was defective in Stage12, but recovering the complete source does not by itself indicate a hidden digit. No keys, wallets or off-image material involved.
