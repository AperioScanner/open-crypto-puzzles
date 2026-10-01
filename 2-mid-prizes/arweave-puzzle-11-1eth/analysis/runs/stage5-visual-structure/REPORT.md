# Stage 5 — robust visual structure

The 12 building interiors were classified independently with Sobel orientation energy and five Hough-line parameter sets.

| id | visual class | Sobel V-H score | Hough diagnostic |
|---:|:---:|---:|:---|
| 1 | H | -0.4673 | VVVVV |
| 2 | H | -0.4297 | VVVVV |
| 3 | V | 0.1915 | VVVVV |
| 4 | V | 0.4231 | VVVVV |
| 5 | H | -0.5201 | VVVVV |
| 6 | H | -0.4714 | HHHHH |
| 7 | V | 0.3278 | VVVVV |
| 8 | H | -0.5005 | VVVVV |
| 9 | H | -0.3924 | VVVVV |
| 10 | H | -0.4696 | VVVVV |
| 11 | H | -0.4056 | VVVVV |
| 12 | V | 0.4788 | VVVVV |

Stable orientation sequence: HHVVHHVHHHHV
H=0, V=1: {"bits": "001100100001", "hex": "321", "int": 801}
H=1, V=0: {"bits": "110011011110", "hex": "cde", "int": 3294}

## Threshold robustness

- threshold 80: HHVVHHVHHHHV
- threshold 100: HHVVHHVHHHHV
- threshold 120: HHVVHHVHHHHV
- threshold 140: HHVVHHVHHHHV
- threshold 160: HHVVHHVHHHHV
- threshold 180: HHVVHHVHHHHV
- threshold 200: HHVVHHVHHHHV
- threshold 220: HHVVHHVHHHHV

The signed Sobel texture classifier is stable under all eight tested binarization thresholds. Hough is retained only as a diagnostic because dense freehand stroke edges bias it toward long edge/boundary segments.
The resulting 12-bit skyline pattern is visually preserved by ordinary re-encoding, consistent with the author's 'format does not matter' hint. It is a lead, not a solution.
