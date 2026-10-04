# Stage 35 — building ↔ water-reflection orientation coupling

**Experiment:** A11-EXP-035

- Eligible buildings: **[3, 4, 5, 6, 7, 8, 9, 10, 11, 12]**
- Buildings 1–2 excluded a priori because the large sailboat overlaps their below-skyline region.
- Fixed reflection band: **y=330..360**
- Exact four-V assignments among 10 buildings: **210**

## Original image

| method | H mean | V mean | V-H | one-sided exact p | Bonferroni p | two-sided p |
|:---|---:|---:|---:|---:|---:|---:|
| sobel | -0.385651 | -0.466536 | -0.080885 | 0.6762 | 1.0000 | 0.6476 |
| fourier | 0.095571 | 0.198532 | 0.102960 | 0.3571 | 0.7143 | 0.7095 |

## JPEG85 + resampling replication

| method | H mean | V mean | V-H | one-sided exact p |
|:---|---:|---:|---:|---:|
| sobel | -0.381490 | -0.452965 | -0.071475 | 0.6762 |
| fourier | 0.210599 | 0.297322 | 0.086723 | 0.3714 |

- promotion rule satisfied: **False**

## Interpretation

The fixed H/V labels do not show a sufficiently strong, replicated same-orientation coupling to the directly underlying water-reflection strokes. Keep H/V as a real standalone visual clue, but retire this straightforward building↔reflection orientation hypothesis.

This test does not evaluate arbitrary mirrored crops, offsets, or pixel-level transforms; it only evaluates the predeclared human-visible scene relation.
