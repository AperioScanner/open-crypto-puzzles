# Stage 93 — pier Roman-numeral structure audit

**Experiment:** A11-EXP-093

- ROI: **(900, 510, 1320, 830)**
- original dominant template: **X** (5/5 configs)
- lossy dominant template: **X** (5/5 configs)
- original family-best score: **0.927937**
- matched-null median: **0.900541**
- matched-null max: **0.985737**
- familywise empirical p: **0.392857**
- synthetic controls all pass: **False**
- promotion rule satisfied: **False**

## Synthetic controls

| control | passed | mean X | mean IX | mean XI |
|:---|:---:|---:|---:|---:|
| X | True | 0.7990 | 0.0000 | 0.0000 |
| IX | False | 0.8826 | 0.6336 | 0.0000 |
| XI | False | 0.7465 | 0.0000 | 0.5257 |

## Per-config target results

| config | winner | score | X | IX | XI | lines |
|:---|:---:|---:|---:|---:|---:|---:|
| c50_150_h35 | X | 0.9195 | 0.9195 | 0.7112 | 0.6980 | 182 |
| c65_165_h40 | X | 0.8413 | 0.8413 | 0.6806 | 0.6442 | 188 |
| c80_180_h45 | X | 0.9279 | 0.9279 | 0.7524 | 0.5769 | 145 |
| c95_195_h50 | X | 0.9035 | 0.9035 | 0.6405 | 0.6083 | 148 |
| c110_210_h55 | X | 0.8735 | 0.8735 | 0.6290 | 0.6151 | 96 |

## Interpretation

The historical X/IX/XI reading does not meet the predeclared uniqueness/stability gate. Retire this Roman-numeral hypothesis rather than building further interpretations from it.

No private-key material was generated, reconstructed or tested.
