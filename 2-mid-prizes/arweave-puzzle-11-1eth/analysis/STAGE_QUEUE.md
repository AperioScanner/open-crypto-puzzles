# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-12

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 108

Stage 108 completed successfully, but the tri-modal density hypothesis **failed its predeclared stability gate**.

### Stage-108 result

- synthetic light/medium/dark controls: **PASS**
- k=3 beats k=2: **171/180 = 95%**
- dominant sequence: **DDLLMMLLDMLM**
- class counts: **L=5, M=4, D=3**
- buildings stable >=90%: **9/12**
- unstable: buildings **3, 5, 12**
- promotion required >=10/12 stable: **FAIL**

### Hypothesis decision

**Building density coding = RETIRED.**

Although a 3-level model often fits better statistically, its labels are too crop-sensitive to treat as an intentional discrete code. Do not continue density clustering.

## Next stage

**Stage 109 — central skyline gap / 5|7 delimiter audit.**

Motivation:
- Stage 91 marked the historical **5/7 skyline split** as PARTIAL, not covered or retired.
- Geometry shows the twelve buildings may be separated after building 5 by a conspicuously wide central gap.
- This is a distinct visible structural hypothesis, independent of H/V, density, roof and topology tests.

Bounded design:
1. Use the fixed 12 building x-ranges from `geometry.json`.
2. Measure all 11 inter-building gaps and the largest-gap/second-largest ratio.
3. Independently detect empty vertical runs from the lower skyline band (y=240..295) after thresholding and horizontal closing.
4. Repeat on original, JPEG85, JPEG70 and resize at thresholds 100/140/180.
5. Require the independently detected dominant gap to overlap the geometry gap after building 5 in every condition.
6. Require dominant gap width >=5× the second-largest inter-building gap and midpoint within 10% of image center.
7. Calibrate concentration of empty-space into one gap against an exchangeable Dirichlet null conditioned on 11 gaps.

A positive result promotes only **5|7 as a robust visible delimiter**, not any numeric/key interpretation.

## Status

- Stages 1–108: completed.
- Stage 108: COMPLETED + REVIEWED — density coding retired.
- Stage 109: selected for launch.
