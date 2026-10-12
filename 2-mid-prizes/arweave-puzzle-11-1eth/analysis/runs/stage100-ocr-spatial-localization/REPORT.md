# Stage 100 — spatial localization of Stage-99 OCR survivors

**Experiment:** A11-EXP-100

- APRIL localization control: **True**
- 12:05.04 localization control: **True**
- all controls pass: **True**
- survivors: **['BEE']**
- stage promoted: **True**

## Candidate results

| token | target occurrences | qualifying target clusters | shuffled occurrences | qualifying shuffled clusters | survived | best box/conf/corr |
|:---|---:|---:|---:|---:|:---:|:---|
| SSS | 5 | 0 | 1 | 0 | False |  |
| EAE | 3 | 0 | 0 | 0 | False |  |
| BEE | 5 | 1 | 2 | 0 | True | [803.0, 520.5, 883.0, 545.0] / 54.6 / 0.969 |
| IES | 4 | 0 | 0 | 0 | False |  |

## Interpretation

At least one Stage-99 short OCR candidate is repeatedly read from the same physical image location across preprocessing and lossy re-encoding while lacking an equally persistent shuffled-control location. Only those survivors warrant direct visual/rebus follow-up.

Only small diagnostic crops for surviving short tokens are saved.
No private-key material was generated, reconstructed or tested.
