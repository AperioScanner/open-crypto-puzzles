# Stage 94 — large-sail stroke-orientation carrier-capacity audit

**Experiment:** A11-EXP-094

- synthetic count controls tested: **[16, 32, 64, 128, 256]**
- detector count correlation (descriptive): **0.8415**
- count-compatible canonical carriers: **[]**
- all 64/256 one-stroke carriers rejected by conservative count gate: **True**
- classifiable-count CV: **0.1207**
- orientation structure gate: **True**
- cross-variant agreement gate: **True**
- promotion rule satisfied: **False**

## Detector calibration

| drawn strokes | mean detected | min | max | CV |
|---:|---:|---:|---:|---:|
| 16 | 13.25 | 12 | 14 | 0.063 |
| 32 | 25.25 | 22 | 27 | 0.081 |
| 64 | 48.50 | 45 | 52 | 0.056 |
| 128 | 61.25 | 49 | 68 | 0.119 |
| 256 | 64.75 | 53 | 70 | 0.106 |

## Variant summaries

| variant | stable tracks | classifiable | + | - | minority frac | angle separation | nearest canonical count |
|:---|---:|---:|---:|---:|---:|---:|:---|
| original | 13 | 10 | 6 | 4 | 0.400 | 111.9 | 64 (delta 54) |
| jpeg85 | 16 | 13 | 8 | 5 | 0.385 | 112.4 | 64 (delta 51) |
| jpeg70 | 13 | 12 | 7 | 5 | 0.417 | 111.1 | 64 (delta 52) |
| down75_up | 16 | 14 | 7 | 7 | 0.500 | 111.3 | 64 (delta 50) |

## Cross-format agreement

| variant vs original | matched fraction | same-sign among matches |
|:---|---:|---:|
| jpeg85 | 0.600 | 1.000 |
| jpeg70 | 0.800 | 1.000 |
| down75_up | 0.700 | 1.000 |

## Interpretation

Both canonical one-stroke-per-symbol carrier sizes (64 visible hex symbols and 256 binary symbols) produce substantially larger detector responses in synthetic controls than the real sail. Retire this specific one-stroke-per-symbol carrier family.

The ordered target stroke-orientation sequence is deliberately not stored or printed.
No private-key material was generated, reconstructed or tested.
