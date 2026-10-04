# Stage 30 — semantic source decomposition of traversal anomaly

**Experiment:** A11-EXP-030

Foreground threshold: gray < 250. Fixed source-x clusters come from Stage 29; no new region was selected after seeing Stage-30 values.

| cluster | band | fg fraction | all printable | all zlib | fg printable | fg zlib | bg printable | bg zlib |
|:---|:---|---:|---:|---:|---:|---:|---:|---:|
| printable_cluster | upper_skyline | 0.337 | 0.1240 | 0.4922 | 0.3637 | 0.9436 | 0.0036 | 0.1098 |
| printable_cluster | boats_mid | 0.541 | 0.1980 | 0.7258 | 0.3584 | 0.9576 | 0.0106 | 0.2086 |
| printable_cluster | lower_water | 0.643 | 0.2485 | 0.9203 | 0.3764 | 0.9698 | 0.0159 | 0.3346 |
| printable_cluster | full_height | 0.527 | 0.2032 | 0.7480 | 0.3598 | 0.9531 | 0.0082 | 0.2054 |
| compressible_cluster | upper_skyline | 0.141 | 0.0479 | 0.2655 | 0.3772 | 1.0109 | 0.0007 | 0.0623 |
| compressible_cluster | boats_mid | 0.063 | 0.0246 | 0.1663 | 0.4452 | 1.0262 | 0.0006 | 0.0448 |
| compressible_cluster | lower_water | 0.009 | 0.0025 | 0.0381 | 0.3684 | 1.1158 | 0.0001 | 0.0120 |
| compressible_cluster | full_height | 0.062 | 0.0225 | 0.1398 | 0.3801 | 1.0072 | 0.0003 | 0.0338 |
| left_margin_control | upper_skyline | 0.039 | 0.0159 | 0.1241 | 0.4505 | 1.1209 | 0.0009 | 0.0364 |
| left_margin_control | boats_mid | 0.000 | 0.0000 | 0.0143 | 0.0000 | NA | 0.0000 | 0.0133 |
| left_margin_control | lower_water | 0.141 | 0.0532 | 0.3097 | 0.3669 | 1.0222 | 0.0013 | 0.0712 |
| left_margin_control | full_height | 0.073 | 0.0295 | 0.1719 | 0.3895 | 1.0187 | 0.0005 | 0.0373 |

## Full-height cross-bitplane comparison

| cluster | bit | printable | run | zlib |
|:---|---:|---:|---:|---:|
| printable_cluster | 0 | 0.2032 | 9 | 0.7480 |
| printable_cluster | 1 | 0.1933 | 8 | 0.7406 |
| printable_cluster | 2 | 0.1905 | 9 | 0.7374 |
| printable_cluster | 3 | 0.1879 | 8 | 0.7353 |
| compressible_cluster | 0 | 0.0225 | 6 | 0.1398 |
| compressible_cluster | 1 | 0.0238 | 4 | 0.1357 |
| compressible_cluster | 2 | 0.0226 | 5 | 0.1345 |
| compressible_cluster | 3 | 0.0232 | 5 | 0.1345 |
| left_margin_control | 0 | 0.0295 | 4 | 0.1719 |
| left_margin_control | 1 | 0.0295 | 4 | 0.1713 |
| left_margin_control | 2 | 0.0275 | 3 | 0.1704 |
| left_margin_control | 3 | 0.0251 | 3 | 0.1648 |

## Interpretation

If the Stage-29 anomaly follows specific drawn-object bands or blank-background strips, it is more parsimoniously explained by natural image structure. Persistence across semantic bands, foreground/background classes, and uniquely in bit 0 would strengthen a carrier hypothesis.
