# Stage157 — source-vs-silhouette control of old Stage12 projection lag

- Original PNG SHA verified: **True**
- Old Stage12 projection (x and y lag/score) exact replay: **True**
- Synthetic flat-vs-period12 controls: **24/24**
- Corrected ROI: x=1000..1545, y=350..554 (only 5 true sail polygon interiors)
- Original old-band x-lag: **3**; old score **0.970**
- Corrected source lag3 compatible with silhouette across 12: **True**
- Decision: **SOURCE_LAG3_COMPATIBLE_WITH_SILHOUETTE**

| Source/threshold | corrected lag/score | flat geometry lag/score | abs difference |
|---|---|---|---|
| original t110 | 3 / 0.861 | 3 / 0.981 | 0.120 |
| original t140 | 3 / 0.877 | 3 / 0.981 | 0.103 |
| original t170 | 3 / 0.898 | 3 / 0.981 | 0.083 |
| jpeg85 t110 | 3 / 0.861 | 3 / 0.981 | 0.120 |
| jpeg85 t140 | 3 / 0.879 | 3 / 0.981 | 0.102 |
| jpeg85 t170 | 3 / 0.898 | 3 / 0.981 | 0.082 |
| jpeg70 t110 | 3 / 0.860 | 3 / 0.981 | 0.120 |
| jpeg70 t140 | 3 / 0.878 | 3 / 0.981 | 0.102 |
| jpeg70 t170 | 3 / 0.898 | 3 / 0.981 | 0.083 |
| down75_up t110 | 3 / 0.857 | 3 / 0.981 | 0.124 |
| down75_up t140 | 3 / 0.882 | 3 / 0.981 | 0.099 |
| down75_up t170 | 3 / 0.901 | 3 / 0.981 | 0.079 |

The old y=[360,480) measurement was not a full five-sail inspection. A close match of corrected source lag3 to filled polygon silhouettes is mundane geometry, not an encoded three or an instruction.

This analysis does not derive, reconstruct or test any secret; no additional Stage is implied by a null result.
