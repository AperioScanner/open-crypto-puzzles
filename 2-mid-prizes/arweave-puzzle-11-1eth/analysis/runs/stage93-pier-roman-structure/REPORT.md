# Stage 93 — pier Roman-numeral structure audit

**Experiment:** A11-EXP-093

- ROI: **(900, 510, 1320, 830)**
- original dominant template: **IX** (4/5 configs)
- lossy dominant template: **IX** (3/5 configs)
- original family-best score: **0.874056**
- matched-null median: **0.853438**
- matched-null max: **0.985737**
- familywise empirical p: **0.410714**
- synthetic controls all pass: **True**
- promotion rule satisfied: **False**

## Synthetic controls

| control | passed | winner support | mean X | mean IX | mean XI |
|:---|:---:|---:|---:|---:|---:|
| X | True | 5/5 | 0.7990 | 0.0000 | 0.0000 |
| IX | True | 5/5 | 0.6808 | 0.7589 | 0.0000 |
| XI | True | 5/5 | 0.5810 | 0.0000 | 0.6823 |

## Per-config target results

| config | winner | score | X | IX | XI | lines |
|:---|:---:|---:|---:|---:|---:|---:|
| c50_150_h35 | IX | 0.8384 | 0.7107 | 0.8384 | 0.8372 | 182 |
| c65_165_h40 | IX | 0.8326 | 0.6038 | 0.8326 | 0.8070 | 188 |
| c80_180_h45 | IX | 0.8741 | 0.6869 | 0.8741 | 0.7292 | 145 |
| c95_195_h50 | IX | 0.8110 | 0.6894 | 0.8110 | 0.7808 | 148 |
| c110_210_h55 | XI | 0.7833 | 0.7220 | 0.7767 | 0.7833 | 96 |

## Interpretation

The historical X/IX/XI reading does not meet the predeclared uniqueness/stability gate. Retire this Roman-numeral hypothesis rather than building further interpretations from it.

No private-key material was generated, reconstructed or tested.
