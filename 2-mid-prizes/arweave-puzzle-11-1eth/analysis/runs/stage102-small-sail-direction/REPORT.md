# Stage 102 — five-small-sail directional-orientation audit

**Experiment:** A11-EXP-102

- synthetic controls pass: **True**
- stable sails: **3/5**
- visible sequence: **R?L?L**
- both direction classes present: **True**
- promoted: **False**

| sail | direction | stable | original Hough | original Sobel |
|---:|:---:|:---:|---:|---:|
| 1 | R | True | 1.000 | 0.328 |
| 2 | ? | False | -0.164 | 0.130 |
| 3 | L | True | -0.622 | -0.303 |
| 4 | ? | False | -0.457 | -0.072 |
| 5 | L | True | -0.570 | -0.246 |

## Interpretation

The small sailboats do not provide a sufficiently stable, nontrivial L/R sequence. Retire sail-direction coding.

No private-key material was generated or tested.
