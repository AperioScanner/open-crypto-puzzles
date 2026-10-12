# Stage 101 — BEE adversarial glyph-validity audit

**Experiment:** A11-EXP-101

- rendered BEE controls valid: **True**
- target OCR hit rate: **0.011** (4/360)
- positive-control median hit rate: **1.000**
- max matched line-art control hit rate: **0.000**
- target variants with BEE hit: **3/4**
- target PSM modes with hit: **2/6**
- target crop jitters with hit: **2/5**
- target vertical-stem fraction: **0.115**
- weakest positive vertical-stem fraction: **0.359**
- target gradient balance: **0.181**
- weakest positive gradient balance: **0.647**
- rate gate: **False**
- diversity gate: **False**
- glyph gate: **False**
- stage promoted: **False**

## Rendered BEE controls

| font | hit rate | variants | PSM modes | vertical stem | gradient balance |
|:---|---:|---:|---:|---:|---:|
| DejaVuSans.ttf | 1.000 | 4/4 | 6/6 | 0.359 | 0.684 |
| DejaVuSerif.ttf | 1.000 | 4/4 | 6/6 | 0.359 | 0.689 |
| DejaVuSansMono.ttf | 1.000 | 4/4 | 6/6 | 0.359 | 0.728 |
| DejaVuSans-Bold.ttf | 1.000 | 4/4 | 6/6 | 0.359 | 0.647 |

## Matched line-art controls

| idx | box | BEE hit rate | vertical stem | gradient balance |
|---:|:---|---:|---:|---:|
| 0 | [560, 350, 676, 411] | 0.000 | 0.131 | 0.187 |
| 1 | [70, 980, 186, 1041] | 0.000 | 0.115 | 0.169 |
| 2 | [140, 980, 256, 1041] | 0.000 | 0.131 | 0.160 |
| 3 | [490, 350, 606, 411] | 0.000 | 0.115 | 0.153 |
| 4 | [140, 280, 256, 341] | 0.000 | 0.115 | 0.152 |
| 5 | [280, 350, 396, 411] | 0.000 | 0.131 | 0.228 |
| 6 | [1120, 280, 1236, 341] | 0.000 | 0.098 | 0.237 |
| 7 | [0, 980, 116, 1041] | 0.000 | 0.115 | 0.141 |

## Interpretation

The localized Stage-100 BEE reading fails the adversarial literal-glyph test. Retire BEE as a Tesseract hallucination caused by stable line hatching; do not interpret the word semantically.

Artifacts: `bee-target-window.png`, `bee-target-contact-sheet.png`.
No private-key material was generated, reconstructed or tested.
