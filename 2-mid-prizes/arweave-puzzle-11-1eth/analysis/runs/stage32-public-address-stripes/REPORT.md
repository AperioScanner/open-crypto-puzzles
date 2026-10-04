# Stage 32 — public-address coarse-stripe known-answer probe

**Experiment:** A11-EXP-032

- Public address bits: **160**, ones: **83**
- Image width: **1600 px = 160 × 10 px**
- Predeclared candidate sequences: **40**; with two reading directions: **80**
- Same-balance null targets: **20000**

## Best result

- band: **full**
- feature: **ink180**
- polarity: **low_is_1**
- direction: **right_to_left**
- Hamming distance: **66/160** (94 matches)
- familywise empirical p: **0.409530**
- same-family transformed Hamming: **66/160**
- lossy replication rule: **True**
- promotion rule satisfied: **False**

## Top candidates

| rank | band | feature | polarity | direction | Hamming | lossy Hamming |
|---:|:---|:---|:---|:---|---:|---:|
| 1 | full | ink180 | low_is_1 | right_to_left | 66 | 66 |
| 2 | full | ink250 | low_is_1 | right_to_left | 66 | 68 |
| 3 | full | ink220 | low_is_1 | right_to_left | 68 | 68 |
| 4 | full | mean_darkness | low_is_1 | right_to_left | 68 | 66 |
| 5 | full | vertical_change | low_is_1 | left_to_right | 68 | 70 |
| 6 | lower_water | ink250 | low_is_1 | left_to_right | 68 | 68 |
| 7 | lower_water | vertical_change | low_is_1 | left_to_right | 68 | 68 |
| 8 | boats_mid | ink180 | low_is_1 | right_to_left | 70 | 70 |
| 9 | boats_mid | ink220 | low_is_1 | right_to_left | 70 | 72 |
| 10 | boats_mid | mean_darkness | low_is_1 | right_to_left | 70 | 68 |

## Interpretation

A positive result would identify a simple, format-robust visual mechanism that reproduces a known public value already stated by the author to be present in the image. A negative result retires only this exact 160 vertical × 10px family; it does not rule out other visual encodings of the public address.
