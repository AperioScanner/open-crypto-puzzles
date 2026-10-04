# Stage 36 — large-sailboat multiscale visual-reveal audit

**Experiment:** A11-EXP-036

- Fixed transforms: **19**
- Target rank-1 transforms, original: **0**
- Target rank-1 transforms, lossy: **3**
- Rank-1 transforms replicated before/after lossy conversion: **0**
- Manual-review priority rule: **False**

## Family summary

| family | transforms | original rank1 | replicated rank1 |
|:---|---:|---:|---:|
| clahe | 1 | 0 | 0 |
| dog | 3 | 0 | 0 |
| intensity_band | 7 | 0 | 0 |
| line_suppression | 1 | 0 | 0 |
| threshold | 7 | 0 | 0 |

## Strongest target-vs-control rankings

| transform | target rank | target score | max control | difference | lossy rank |
|:---|---:|---:|---:|---:|---:|
| band_240_247 | 3 | 0.0000 | 0.0000 | -0.0000 | 3 |
| band_248_254 | 2 | 0.2619 | 0.3737 | -0.1119 | 4 |
| band_224_239 | 2 | 0.0000 | 0.1972 | -0.1972 | 3 |
| band_192_223 | 4 | 0.5768 | 0.8483 | -0.2715 | 1 |
| band_0_63 | 2 | 1.1029 | 1.5386 | -0.4357 | 3 |
| band_128_191 | 4 | 1.2118 | 1.6528 | -0.4411 | 4 |
| dog_4_12 | 4 | 0.6674 | 1.1691 | -0.5017 | 4 |
| dog_1_3 | 2 | 1.4543 | 1.9658 | -0.5115 | 2 |
| thr_80 | 4 | 0.7616 | 1.3020 | -0.5405 | 4 |
| thr_110 | 4 | 1.0193 | 1.5815 | -0.5622 | 4 |
| thr_140 | 4 | 0.4737 | 1.0989 | -0.6252 | 4 |
| band_64_127 | 3 | 1.2687 | 1.9185 | -0.6498 | 3 |

## Interpretation

This is a reveal-and-ranking stage, not a text decoder. Connected-component alignment can be produced by ordinary drawing strokes, so the decisive next step—if the target is consistently unusual—is direct visual review of the generated contact sheets and only then a narrower predeclared follow-up.

Artifacts:
- `large-boat-contact-original.png`
- `large-boat-contact-lossy.png`
- `top-comparison-original.png`
- `top-comparison-lossy.png`
