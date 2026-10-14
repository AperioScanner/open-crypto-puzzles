# Stage 138 — source-corrected all-12-building reflection audit

- Image SHA256 correct: **True**
- Legacy Stage35 original 10-row reproduction: **True**
- Synthetic positive/reversal negative controls: **True / True**
- Two newly included reflection crops have adequate ink: **True**
- Reproduced V/H orientation association 4/4 formats: **False**
- Decision: **NO_REPLICATED_ALL_12_REFLECTION_ASSOCIATION**

| variant | Sobel V-H | Sobel p | Fourier V-H | Fourier p |
|---|---:|---:|---:|---:|
| original | -0.0324 | 0.5818 | +0.0995 | 0.3455 |
| jpeg85 | -0.0291 | 0.5697 | +0.1126 | 0.3273 |
| jpeg70 | -0.0304 | 0.5758 | +0.0855 | 0.3697 |
| down75_up | -0.0235 | 0.5556 | +0.0975 | 0.3394 |

## Interpretation

The previously excluded first two buildings were restored, but no robust positive coupling across all twelve was found. Retire only this direct reflection-orientation criterion.

No key, mnemonic or wallet operations.
