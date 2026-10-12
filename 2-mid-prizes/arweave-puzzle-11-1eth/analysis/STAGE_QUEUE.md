# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 101

Stage 101 completed successfully.

### Stage-101 result

The localized `BEE` OCR reading from Stage 100 fails every adversarial literal-text gate:

- target BEE hit rate: **4 / 360 = 1.1%**
- rendered BEE controls: **100%**
- target PSM support: **2 / 6**
- target crop-jitter support: **2 / 5**
- target vertical-stem fraction: **0.115** vs weakest real-BEE control **0.359**
- target gradient balance: **0.181** vs weakest real-BEE control **0.647**
- rate gate: FAIL
- diversity gate: FAIL
- glyph gate: FAIL

### Hypothesis decision

**Literal BEE = RETIRED as stable-hatching OCR hallucination.**

This closes the Stage-99/100 OCR branch:
- SSS / EAE / IES: retired by spatial localization
- BEE: retired by adversarial glyph validation

## Next stage

**Stage 102 — five-small-sail directional-orientation audit.**

Motivation:
- Puzzle #9 supports a visible, multi-step semantic prior.
- #11's five small sailboats are a distinct repeated object class.
- Prior small-sail stages tested width/area/gap relationships, but **not sail lean/direction**.
- Direction is human-visible and format-invariant, fitting the active route without recycling prior negatives.

Bounded design:
1. Reuse the five independently measured Stage-19 sail x-ranges.
2. Fixed y band: **360..480**.
3. Two independent direction estimators:
   - signed diagonal Hough-line energy
   - Sobel tangent-orientation signed energy
4. Fixed grayscale thresholds for Hough: 100, 140, 180.
5. Repeat on original, JPEG85, JPEG70 and 0.75x resize roundtrip.
6. Synthetic left-lean / right-lean sail controls validate both estimators.
7. Promote only if:
   - >=4/5 sails have a stable direction across all variants;
   - the two estimators agree;
   - both direction classes are present, yielding a nontrivial visible sequence.

This stage only establishes a robust L/R visual sequence. It does not map that sequence to secret material.

## Status

- Stages 1–101: completed.
- Stage 101: COMPLETED + REVIEWED — OCR text branch closed.
- Stage 102: selected for launch.
