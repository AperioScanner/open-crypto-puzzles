# Stage 94 — large-sail stroke-orientation carrier-capacity audit

**Experiment:** A11-EXP-094

- synthetic 64-stroke detector control: **True**
- compatible representation counts across every variant: **[]**
- classifiable-count CV: **0.1207**
- orientation structure gate: **True**
- cross-variant agreement gate: **False**
- promotion rule satisfied: **False**

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

The large sail does not satisfy the predeclared count + binary-orientation + cross-format robustness requirements for a natural 64-symbol or 256-symbol visible stroke carrier. Retire this carrier family rather than decoding an unstable stroke sequence.

The ordered target stroke-orientation sequence is deliberately not stored or printed.
No private-key material was generated, reconstructed or tested.
