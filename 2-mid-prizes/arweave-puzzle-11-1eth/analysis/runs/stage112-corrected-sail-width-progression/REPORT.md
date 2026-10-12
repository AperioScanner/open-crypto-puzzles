# Stage 112 — corrected five-sail width-progression replication

- five-sail detector stable: **True**
- max center drift: **2.0 px**
- centers original: **[1042, 1148, 1282, 1372, 1490]**
- synthetic controls pass: **False**
- median mask widths: **[np.float64(nan), np.float64(nan), np.float64(54.2), np.float64(45.13), np.float64(86.3)]**
- median edge widths: **[np.float64(nan), np.float64(nan), np.float64(71.44), np.float64(45.9), np.float64(84.45)]**
- mask first-three AP: **{'d1': nan, 'd2': nan, 'error': nan, 'mean_step': nan}**
- edge first-three AP: **{'d1': nan, 'd2': nan, 'error': nan, 'mean_step': nan}**
- permutation p (mask/edge): **0.00000 / 0.00000**
- cross-method profile correlation: **0.000**
- Stage-18 qualitative profile reproduced: **False**
- all real variant/method AP gates pass: **False**
- promoted: **False**

| variant | mask widths | mask AP err | edge widths | edge AP err |
|:---|:---|---:|:---|---:|
| original | [None, None, 54.2, 45.0, 85.6] | nan | [None, None, 72.6, 46.3, 84.5] | nan |
| jpeg85 | [None, None, 54.2, 45.0, 86.2] | nan | [None, 17.9, 73.1, 46.4, 84.4] | nan |
| jpeg70 | [None, None, 54.2, 45.3, 86.4] | nan | [None, None, 70.3, 45.5, 84.0] | nan |
| down75_up | [None, None, 53.4, 45.2, 86.4] | nan | [None, None, 58.5, 44.0, 85.0] | nan |

## Interpretation

The corrected true five-sail measurement does not robustly reproduce Stage 18's arithmetic progression under the confirmatory gates. Retire the +26/+26 sail-width lead.

No private-key material was generated or tested.
