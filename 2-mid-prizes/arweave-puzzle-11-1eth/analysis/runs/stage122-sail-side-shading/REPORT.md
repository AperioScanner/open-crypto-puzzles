# Stage 122 — image-only six-sail signed shading asymmetry

- Input: canonical 1600x1105 image; SHA256 verified.
- Repair: external reference zones intersect other objects and were excluded from scoring.
- Synthetic paired dark-side / neutral controls: **72**, pass=**True**
- Stable, image-supported signed sides: **3/6**
- Nontrivial mixed sides: **False**
- Decision: **NO_STABLE_SIX_SAIL_SIDE_PATTERN**

| sail | right−left INNER contrast (original) | coverage | stable side |
|---|---:|:---:|:---:|
| large | +0.194 | True | R |
| small_1 | +0.076 | True | ? |
| small_2 | -0.151 | True | ? |
| small_3 | +0.211 | True | R |
| small_4 | +0.088 | True | ? |
| small_5 | +0.144 | True | R |

## Interpretation

No reproducible multistate left/right shading pattern meets the predeclared gate. Retire only this fixed wedge/contrast mechanism.

No private keys, mnemonics, secret candidates or address checks were performed.
