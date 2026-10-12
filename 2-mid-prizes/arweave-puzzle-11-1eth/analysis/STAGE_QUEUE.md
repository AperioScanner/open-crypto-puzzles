# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through Stage 100

Stage 100 completed with both spatial-localization controls passing.

### Stage-100 result

Retired as region-level OCR hallucinations:
- **SSS** — no original/lossy co-localized box.
- **EAE** — no original/lossy co-localized box.
- **IES** — no original/lossy co-localized box.

One token survived the predeclared spatial rule:

**BEE**
- canonical box: approximately **x=803..883, y=520.5..545**
- 2 original preprocessing transforms: gray + Otsu
- 2 lossy preprocessing transforms: gray + Otsu
- mean OCR confidence: **54.6**
- original/lossy crop correlation: **0.969**
- qualifying shuffled co-localized clusters: **0**

### Direct visual validation

The saved Stage-100 diagnostic crop was inspected directly. It does **not** look like obvious printed/handwritten `BEE`; it looks like a compact patch of dense, mostly horizontal line hatching.

Therefore Stage 100 establishes a reproducible **OCR phenomenon**, not readable plaintext.

### Hypothesis decision

- SSS / EAE / IES: **RETIRED**
- literal `BEE` text: **UNCONFIRMED and visually suspect**
- exact BEE location: deserves one adversarial glyph-validity test before semantic interpretation

## Next stage

**Stage 101 — BEE adversarial glyph-validity and perturbation audit.**

Question:
> Is the Stage-100 BEE location behaving like genuine text, or is Tesseract consistently hallucinating letters from hatching?

Bounded design:
1. Fixed target box from Stage 100, with small predeclared crop jitters/padding.
2. Variants: original, JPEG85, JPEG70, 0.75x resize roundtrip.
3. Transforms: gray, Otsu, adaptive.
4. Tesseract PSM modes: 6, 7, 8, 10, 11, 13.
5. Measure exact `BEE` recovery rate across PSM/transform/variant/crop perturbations.
6. Positive controls: rendered `BEE` using several ordinary system font families, subjected to the same lossy transformations.
7. Negative controls: same-size line-art windows selected by similar ink density and horizontal/vertical edge-energy balance, excluding the target.
8. Independently measure vertical/horizontal stroke-energy balance. Standard B/E glyphs require both vertical stems and horizontal arms; pure horizontal hatching should separate from rendered BEE controls.
9. Save a target-only contact sheet for direct review.

Promotion requires:
- recovery under multiple independent PSM modes;
- persistence across at least 3 image variants;
- recovery materially above matched line-art controls;
- glyph-orientation balance within the calibrated positive-control range.

A failure retires literal `BEE` as an OCR hallucination. No semantic use of the word is allowed before this test.

## Status

- Stages 1–100: completed.
- Stage 100: COMPLETED + REVIEWED — BEE is the only localized OCR survivor.
- Stage 101: selected for launch.
