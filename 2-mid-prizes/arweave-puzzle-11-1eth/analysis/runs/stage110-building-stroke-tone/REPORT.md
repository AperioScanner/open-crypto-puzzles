# Stage 110 — building stroke-tone / pencil-pressure audit

- synthetic binary control pass: **True**
- synthetic ternary control pass: **True**
- real dominant models: **{'otsu_ink_median_darkness': {'k': 3, 'win_fraction': 1.0, 'counts': {'2': 0, '3': 60}}, 'edge_median_darkness': {'k': 3, 'win_fraction': 1.0, 'counts': {'2': 0, '3': 60}}}**
- same dominant k across both metrics: **True**
- buildings stable >=90%: **7/12**
- tone sequence: **DDLLMMLLDMLM**
- class counts: **{'0': 5, '1': 4, '2': 3}**
- redundant with H/V or retired density: **False**
- promoted: **False**

## Synthetic controls

- binary correct-model fraction: 0.967, label accuracy: 0.997, min patch stability: 0.967
- ternary correct-model fraction: 1.000, label accuracy: 0.974, min patch stability: 0.933

## Per-building stability

| building | class | stability |
|---:|:---:|---:|
| 1 | D | 1.000 |
| 2 | D | 1.000 |
| 3 | L | 0.992 |
| 4 | L | 0.625 |
| 5 | M | 0.875 |
| 6 | M | 0.617 |
| 7 | L | 1.000 |
| 8 | L | 1.000 |
| 9 | D | 0.858 |
| 10 | M | 0.958 |
| 11 | L | 1.000 |
| 12 | M | 0.583 |

## Interpretation

Per-building stroke tone does not form a sufficiently stable, independently validated discrete channel. Retire stroke-tone coding.

No private-key material was generated or tested.
