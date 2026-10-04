# Stage 29 — localize and reproduce Stage-28 traversal anomaly

**Experiment:** A11-EXP-029

Canonical fixed traversal: {'rot90': 1, 'flip_lr': True, 'traversal': 'row_serp', 'bitorder': 'big'}.
Window size: 4096 bytes; block-shuffled surrogates: 100.

## Familywise localization calibration

- observed max window printable fraction: **0.217773** (p=0.0099)
- observed min window zlib ratio: **0.114008** (p=0.0099)
- observed max printable run: **8** (p=0.4752)

## Top printable windows

| start byte | printable | run | zlib | source bbox |
|---:|---:|---:|---:|:---|
| 172032 | 0.2178 | 8 | 0.7952 | [324, 0, 355, 1105] |
| 167936 | 0.2126 | 5 | 0.7551 | [354, 0, 385, 1105] |
| 184320 | 0.2080 | 6 | 0.7817 | [235, 0, 266, 1105] |
| 176128 | 0.2075 | 5 | 0.7959 | [295, 0, 325, 1105] |
| 180224 | 0.2065 | 5 | 0.7991 | [265, 0, 296, 1105] |
| 188416 | 0.1965 | 8 | 0.7297 | [206, 0, 236, 1105] |
| 192512 | 0.1707 | 6 | 0.6626 | [176, 0, 207, 1105] |
| 28672 | 0.1584 | 6 | 0.6892 | [1362, 0, 1393, 1105] |
| 73728 | 0.1572 | 6 | 0.6470 | [1036, 0, 1067, 1105] |
| 163840 | 0.1555 | 7 | 0.6421 | [384, 0, 414, 1105] |

## Top compressible windows

| start byte | printable | run | zlib | source bbox |
|---:|---:|---:|---:|:---|
| 217088 | 0.0146 | 3 | 0.1140 | [0, 0, 29, 1105] |
| 106496 | 0.0151 | 4 | 0.1208 | [799, 0, 829, 1105] |
| 102400 | 0.0193 | 4 | 0.1372 | [828, 0, 859, 1105] |
| 110592 | 0.0173 | 3 | 0.1418 | [769, 0, 800, 1105] |
| 98304 | 0.0181 | 3 | 0.1467 | [858, 0, 889, 1105] |
| 94208 | 0.0300 | 5 | 0.1543 | [888, 0, 918, 1105] |
| 90112 | 0.0408 | 6 | 0.2046 | [917, 0, 948, 1105] |
| 212992 | 0.0435 | 3 | 0.2412 | [28, 0, 58, 1105] |
| 86016 | 0.0593 | 4 | 0.2839 | [947, 0, 978, 1105] |
| 143360 | 0.0559 | 6 | 0.3022 | [532, 0, 563, 1105] |

## Same traversal across grayscale bitplanes

| bit | printable | run | zlib |
|---:|---:|---:|---:|
| 0 | 0.1091 | 8 | 0.4655 |
| 1 | 0.1056 | 9 | 0.4592 |
| 2 | 0.1042 | 9 | 0.4569 |
| 3 | 0.1006 | 8 | 0.4526 |
| 4 | 0.0991 | 8 | 0.4482 |
| 5 | 0.0948 | 8 | 0.4419 |
| 6 | 0.0840 | 8 | 0.4213 |
| 7 | 0.0705 | 8 | 0.3897 |

## Interpretation

If the familywise window anomaly remains significant and is spatially concentrated, the next stage should inspect those source regions with matched local controls. If the same behavior appears equally or more strongly in higher bitplanes, that favors ordinary image structure over an LSB-specific carrier.
