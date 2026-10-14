# Stage139 — uniform ink-coverage audit of all-building reflection test

- Canonical SHA256 verified: **True**
- Stage138 exact numerical reproduction: **True**
- Synthetic V/H and reversed negative calibration: **True / True**
- Source-adequate image variants: **4/4**
- Excluded near-blank buildings are consistent across formats: **True**
- Both methods pass 4/4: **False**
- Decision: **NO_COVERAGE_GATED_REFLECTION_RELATION**

| variant | excluded for low ink | Sobel p | Fourier p |
|---|---|---:|---:|
| original | [6, 11] | 0.2 | 0.33333333 |
| jpeg85 | [6, 11] | 0.2 | 0.32857143 |
| jpeg70 | [6, 11] | 0.2 | 0.33333333 |
| down75_up | [6, 11] | 0.20952381 | 0.35238095 |

## Interpretation

No replicated direct building H/V-to-reflection orientation relation after applying the SAME minimum source ink threshold to all 12 apertures. The facade H/V observation itself is unaffected.

No key, mnemonic, address or wallet operations.
