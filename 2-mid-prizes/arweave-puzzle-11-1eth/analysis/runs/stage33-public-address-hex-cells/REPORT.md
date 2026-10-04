# Stage 33 — public-address 40×40px hex-cell probe

**Experiment:** A11-EXP-033

- Image width: **1600 px = 40 hex digits × 40 px**
- Candidate sequences: **96**, evaluated with directions: **192**
- Null permutations preserving address digit multiset: **10000**

## Best result

- band: **full**
- feature: **ink220**
- quantizer: **minmax16**
- polarity: **inverted**
- direction: **left_to_right**
- exact hex-digit matches: **9/40**
- nibble-bit Hamming: **67/160**
- familywise p(exact): **0.085191**
- familywise p(bit-Hamming): **0.958304**
- transformed exact matches: **9/40**
- same-family extracted digits stable after lossy transform: **38/40**
- promotion rule: **False**

## Top candidates

| rank | band | feature | quantizer | polarity | direction | exact | bit-H | lossy exact | stable |
|---:|:---|:---|:---|:---|:---|---:|---:|---:|---:|
| 1 | full | ink220 | minmax16 | inverted | left_to_right | 9 | 67 | 9 | 38 |
| 2 | boats_mid | ink250 | rank16 | inverted | right_to_left | 8 | 57 | 5 | 31 |
| 3 | boats_mid | mean_darkness | rank16 | inverted | right_to_left | 8 | 63 | 6 | 36 |
| 4 | boats_mid | ink220 | rank16 | inverted | right_to_left | 7 | 59 | 6 | 36 |
| 5 | full | ink180 | minmax16 | inverted | left_to_right | 7 | 59 | 8 | 37 |
| 6 | boats_mid | ink180 | rank16 | inverted | right_to_left | 7 | 63 | 7 | 40 |
| 7 | lower_water | mean_darkness | rank16 | inverted | left_to_right | 7 | 67 | 5 | 34 |
| 8 | full | ink250 | minmax16 | inverted | left_to_right | 7 | 71 | 6 | 25 |
| 9 | boats_mid | ink250 | minmax16 | inverted | right_to_left | 6 | 67 | 8 | 23 |
| 10 | full | horizontal_change | minmax16 | inverted | left_to_right | 6 | 68 | 5 | 37 |

## Interpretation

A positive result would identify a coarse format-robust mapping to the already-public address. A negative result retires only the exact 40 vertical × 40px hex-cell family; it does not rule out object-based, symbolic, textual, or other semantic encodings of the public address.
