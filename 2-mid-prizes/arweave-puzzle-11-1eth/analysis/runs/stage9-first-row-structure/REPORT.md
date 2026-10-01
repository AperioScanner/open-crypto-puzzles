# Stage 9 — first-row position/run structure

- Canonical non-white pixels (<255): 147
- Canonical non-white runs: 10
- Distinct non-white grayscale values: 38
- Unique 32-byte candidates generated: 60423
- Valid secp256k1 scalars checked: 56300
- ff21 prefix near-misses: 1
- Exact target match: false

## Canonical <255 non-white runs (start:length)

1013:2 1026:4 1031:3 1038:2 1044:2 1053:1 1111:113 1271:7 1362:8 1396:5

## Threshold summary

| threshold | ones | total runs | nonwhite runs |
|---:|---:|---:|---:|
| <255 | 147 | 21 | 10 |
| <254 | 103 | 27 | 13 |
| <253 | 89 | 23 | 11 |
| <252 | 71 | 17 | 8 |
| <251 | 66 | 17 | 8 |
| <250 | 60 | 17 | 8 |
| <248 | 54 | 15 | 7 |
| <245 | 50 | 13 | 6 |
| <240 | 42 | 13 | 6 |
| <235 | 26 | 13 | 6 |
| <230 | 18 | 5 | 2 |
| <220 | 11 | 5 | 2 |
| <200 | 0 | 1 | 0 |

This closes a gap left by the earlier first-row value scan: it tests where anomalous pixels occur, not only their grayscale bit values.
