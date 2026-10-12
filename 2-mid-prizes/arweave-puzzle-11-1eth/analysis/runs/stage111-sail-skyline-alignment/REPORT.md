# Stage 111 — small-sail ↔ skyline vertical-alignment audit

- synthetic aligned control pass: **True**
- original sail centers: **[1042, 1148, 1282, 1372, 1490]**
- best building block: **7–11**
- direct alignment RMS: **29.72 px**
- same best block across all image variants: **True**
- max sail-center drift: **2.0 px**
- translation-preserving familywise p: **0.41334**
- spacing-constrained familywise p: **0.05970**
- promoted: **False**

| variant | sail centers | best block | RMS px |
|:---|:---|:---:|---:|
| original | [1042, 1148, 1282, 1372, 1490] | 7–11 | 29.72 |
| jpeg85 | [1042, 1148, 1282, 1372, 1490] | 7–11 | 29.72 |
| jpeg70 | [1042, 1148, 1282, 1372, 1490] | 7–11 | 29.72 |
| down75_up | [1042, 1150, 1280, 1372, 1490] | 7–11 | 29.34 |

## Interpretation

The apparent sail-to-building alignment is not exceptional under the predeclared familywise nulls and/or is not stable enough across variants. Retire direct vertical correspondence.

No private-key material was generated or tested.
