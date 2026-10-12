# Stage 107 — adversarial replication of building density channel

- synthetic perturbation controls pass: **True**
- perturbation conditions tested: **180**
- buildings reproducing reference >=90%: **9/12**
- buildings reproducing reference >=95%: **9/12**
- median condition Hamming distance: **3.0**
- maximum condition Hamming distance: **3**
- reference density sequence: **DDSSDDSSDSSD**
- abs(phi) vs H/V: **0.3536**
- exact association p: **0.5455** (924 balanced assignments)
- relation to H/V: **STATISTICALLY_INDEPENDENT_AT_THIS_SAMPLE_SIZE**
- promoted: **False**

## Per-building robustness

| building | reference | match rate |
|---:|:---:|---:|
| 1 | D | 1.000 |
| 2 | D | 1.000 |
| 3 | S | 1.000 |
| 4 | S | 1.000 |
| 5 | D | 0.378 |
| 6 | D | 0.350 |
| 7 | S | 1.000 |
| 8 | S | 1.000 |
| 9 | D | 1.000 |
| 10 | S | 0.994 |
| 11 | S | 1.000 |
| 12 | D | 0.467 |

## Interpretation

The apparent Stage-106 density split does not survive adversarial crop/metric perturbations strongly enough, or collapses to the H/V channel. Downgrade/retire it.

No private-key material was generated or tested.
