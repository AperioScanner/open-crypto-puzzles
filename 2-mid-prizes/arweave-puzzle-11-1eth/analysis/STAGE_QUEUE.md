# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 102

Stage 102 completed successfully.

### Stage-102 result

Synthetic left/right sail controls passed, but only **3/5** real small sails were stable across both independent estimators and all lossy variants.

Observed sequence:
- sail 1: R — stable
- sail 2: ? — Hough/Sobel disagree
- sail 3: L — stable
- sail 4: ? — Sobel too weak for consensus
- sail 5: L — stable

Visible sequence: **R?L?L**

Promotion required >=4/5 stable sails. It failed.

### Hypothesis decision

**Small-sail L/R direction coding = RETIRED.**

Do not try to fill the two unknowns post hoc.

## Next stage

**Stage 103 — 12-building roof-profile category audit.**

Motivation:
- the 12 buildings are the strongest repeated object family in the image;
- H/V interior hatching has already been exhausted as an organizing clue;
- roof/silhouette shape is a separate, human-visible and format-invariant feature family;
- prior geometry stages used roof y/height/width numerically but did not classify roof-profile direction.

Bounded design:
1. Reuse the 12 fixed building x-ranges and roof_y values from `geometry.json`.
2. For each building, analyze only a narrow roof band around the recorded roof_y.
3. Two independent estimators:
   - robust top-envelope slope from the uppermost dark pixels;
   - near-horizontal Hough roof-line slope.
4. Predeclared categories:
   - `/` = rises to the right
   - `-` = approximately flat
   - `\\` = falls to the right
5. Repeat on original, JPEG85, JPEG70 and 0.75x resize roundtrip.
6. Synthetic flat/rising/falling roof controls validate both estimators.
7. Promote only if >=10/12 buildings receive the same category across both estimators and all four variants, with at least two categories represented.

A positive result establishes only a robust visible roof-category sequence. No key mapping is attempted.

## Status

- Stages 1–102: completed.
- Stage 102: COMPLETED + REVIEWED — small-sail direction retired.
- Stage 103: selected for launch.
