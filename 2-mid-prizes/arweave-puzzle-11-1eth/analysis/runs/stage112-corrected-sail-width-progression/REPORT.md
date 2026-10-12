# Stage 112 — corrected five-sail width-progression replication

- five-sail detector stable: **True**
- max center drift: **2.0 px**
- centers original: **[1042, 1148, 1282, 1372, 1490]**
- synthetic controls pass: **True**
- median mask widths: **[np.float64(24.0), np.float64(49.0), np.float64(65.0), np.float64(60.0), np.float64(64.0)]**
- median edge widths: **[np.float64(31.0), np.float64(53.0), np.float64(64.0), np.float64(54.5), np.float64(75.5)]**
- mask first-three AP: **{'d1': 25.0, 'd2': 16.0, 'error': 9.0, 'mean_step': 20.5}**
- edge first-three AP: **{'d1': 22.0, 'd2': 11.0, 'error': 11.0, 'mean_step': 16.5}**
- permutation p (mask/edge): **0.20000 / 0.20000**
- cross-method profile correlation: **0.922**
- Stage-18 qualitative profile reproduced: **False**
- all real variant/method AP gates pass: **False**
- promoted: **False**

| variant | mask widths | mask AP err | edge widths | edge AP err |
|:---|:---|---:|:---|---:|
| original | [24.0, 49.0, 65.0, 60.0, 64.0] | 9.00 | [31.0, 53.0, 64.0, 54.0, 75.0] | 11.00 |
| jpeg85 | [24.0, 49.0, 65.0, 60.0, 64.0] | 9.00 | [32.0, 53.0, 64.0, 55.0, 75.0] | 10.00 |
| jpeg70 | [23.0, 49.0, 65.0, 60.0, 64.0] | 10.00 | [31.0, 53.0, 64.0, 54.0, 76.0] | 11.00 |
| down75_up | [25.0, 49.0, 65.0, 60.0, 64.0] | 8.00 | [31.0, 53.0, 64.0, 55.0, 76.0] | 11.00 |

## Interpretation

The corrected true five-sail measurement does not robustly reproduce Stage 18's arithmetic progression under the confirmatory gates. Retire the +26/+26 sail-width lead.

No private-key material was generated or tested.
