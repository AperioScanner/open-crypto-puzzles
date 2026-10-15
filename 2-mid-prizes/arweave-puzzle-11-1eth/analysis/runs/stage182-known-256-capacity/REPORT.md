# Stage182 — can the OLD full Stage94 gate accept a KNOWN TRUE 256-stroke sail?

- Canonical original PNG SHA (no original pixel read): **True**
- Unchanged source/positive generator replay and negative checks: **14/14**
- Known true 64-stroke fixture ALSO count-compatible with 256-carrier band: **True**
- Known true 256-stroke fixture passes original FULL Stage94 decision: **False**
- Decision: **FULL_STAGE94_GATE_REJECTS_KNOWN_TRUE_256_STROKE_FIXTURE**

| Known source-blind fixture | Detector counts by format | Old carrier-compatible sizes | CV | JPEG positional gate | Overall full gate |
|---:|---|---|---:|---|---|
| 16 | [15, 16, 15, 15] | [] | 0.02839 | True | False |
| 64 | [48, 46, 51, 42] | [64, 256] | 0.06993 | True | True |
| 256 | [89, 97, 79, 64] | [256] | 0.14974 | False | False |

This is an independent POSITIVE-CONTROL sensitivity check of the same full Stage94 numeric rule that Stage181 applied to the corrected natural drawing. It does not infer any original artwork sequence, code or private material. One original synthetic fixture per row; four re-encodings are not independent artwork.
