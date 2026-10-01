# Stage 5 — robust visual structure

The 12 building interiors were classified independently with Sobel orientation energy and five Hough-line parameter sets.

| id | class | confidence | Sobel V-H score | Hough classes |
|---:|:---:|---:|---:|:---|
| 1 | V | 0.833 | -0.4673 | VVVVV |
| 2 | V | 0.833 | -0.4297 | VVVVV |
| 3 | V | 1.000 | 0.1915 | VVVVV |
| 4 | V | 1.000 | 0.4231 | VVVVV |
| 5 | V | 0.833 | -0.5201 | VVVVV |
| 6 | H | 1.000 | -0.4714 | HHHHH |
| 7 | V | 1.000 | 0.3278 | VVVVV |
| 8 | V | 0.833 | -0.5005 | VVVVV |
| 9 | V | 0.833 | -0.3924 | VVVVV |
| 10 | V | 0.833 | -0.4696 | VVVVV |
| 11 | V | 0.833 | -0.4056 | VVVVV |
| 12 | V | 1.000 | 0.4788 | VVVVV |

Stable orientation sequence: VVVVVHVVVVVV
H=0, V=1: {"bits": "111110111111", "hex": "fbf", "int": 4031}
H=1, V=0: {"bits": "000001000000", "hex": "040", "int": 64}

## Threshold robustness

- threshold 80: HHVVHHVHHHHV
- threshold 100: HHVVHHVHHHHV
- threshold 120: HHVVHHVHHHHV
- threshold 140: HHVVHHVHHHHV
- threshold 160: HHVVHHVHHHHV
- threshold 180: HHVVHHVHHHHV
- threshold 200: HHVVHHVHHHHV
- threshold 220: HHVVHHVHHHHV

A pattern stable across independent estimators and thresholds is worth following because it is visually preserved by ordinary re-encoding, consistent with the author's 'format does not matter' hint. It is not a solution by itself.
