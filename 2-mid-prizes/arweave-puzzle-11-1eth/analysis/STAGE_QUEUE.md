# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-12

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 111

Stage 111 completed successfully but did **not** promote sail↔skyline alignment.

- same best skyline block across all variants: buildings 7–11
- direct RMS: 29.72 px
- sail-center drift: 2 px
- translation-preserving familywise p: **0.41334**
- spacing-constrained familywise p: **0.05970**
- promotion: **False**

### Hypothesis decision

**Direct five-sail ↔ five-building x-alignment = RETIRED.**

The spacing-constrained result is close but still above the predeclared 0.05 threshold, while the translation-preserving null is clearly non-significant.

## New implementation finding

Stage 105 and Stage 111 independently corrected the true right-hand five-sail centers to approximately:

`[1042, 1148, 1282, 1372, 1490]`

The earlier Stage-19 "remeasurement" that rejected Stage 18 instead tracked:

`[675.5, 1046.5, 1144.5, 1269.5, 1361.0]`

That Stage-19 object set contains a spurious non-sail track near x≈675 and omits the real rightmost sail near x≈1490.

Therefore Stage 19 did **not** validly replicate the five true sails. This is a concrete implementation defect and satisfies the anti-recycling exception.

Stage 18's original width sequence was:
`[27, 53, 79, 83, 51]`

Its first three widths form the exact progression:
`27, 53, 79` → **+26, +26**.

## Next stage

**Stage 112 — corrected five-sail width-progression replication.**

Bounded confirmatory design:
1. Re-detect the five true right-hand sail centers on original/JPEG85/JPEG70/resize.
2. Build non-overlapping boxes from those centers.
3. Measure sail width with two independent estimators:
   - dark-mask row-envelope width;
   - Canny-edge row-envelope width.
4. Use multiple fixed thresholds for the mask estimator.
5. Positive synthetic controls contain widths `27,53,79,83,51`; negative controls deliberately break the first-three arithmetic progression.
6. Confirm only if:
   - both control families behave correctly;
   - both real estimators reproduce a first-three AP error <=4 px across all four image variants;
   - the AP step remains positive and near the prior ~26 px scale;
   - the five-width profile broadly agrees with the original Stage-18 measurements.

No modulo/alphabet/key interpretation is allowed in this stage.

## Status

- Stages 1–111: completed.
- Stage 111: COMPLETED + REVIEWED — direct cross-object alignment retired.
- Stage 112: selected for launch.
