# Stage 99 — whole-image visible alphanumeric/rebus audit

**Experiment:** A11-EXP-099

- Puzzle #9 positive controls all pass: **True**
- target OCR jobs: **120**
- shuffled negative jobs: **60**
- promoted short tokens: **4**
- stage promoted: **True**

## Positive controls

- APRIL quote control: **True** — {'original_april_paths': 3, 'lossy_april_paths': 3}
- 12:05.04 numeric control: **True** — {'original_numeric_paths': 3, 'lossy_numeric_paths': 3}

## Promoted Puzzle #11 tokens

| token | region/rotation replications | original paths | lossy paths | shuffled |
|:---|:---|---:|---:|---:|
| SSS | full@0° | 11 | 9 | 0 |
| EAE | lower_water@0° | 7 | 9 | 3 |
| BEE | full@0° | 2 | 3 | 6 |
| IES | full@0° | 2 | 3 | 2 |

## Interpretation

At least one short visible token survives independent preprocessing and lossy re-encoding while disappearing under matched block shuffling. These are candidates for direct visual localization in the next stage; they are not secret/key material.

Raw OCR text is intentionally not saved. No long/key-shaped strings are persisted.
No private-key material was generated, reconstructed or tested.
