# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-12

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through corrected Stage 110

Stage 110 was repaired twice under the same stage number:
- quantization-aware BIC removed binary-control overfitting;
- synthetic control evaluation was aligned with the real per-object stability criterion.

### Valid Stage-110 result

Controls:
- binary tone control: **PASS**
- ternary tone control: **PASS**

Real image:
- both independent tone metrics choose **k=3 in 60/60 conditions each**
- modal tone sequence: **DDLLMMLLDMLM**
- class sizes: 5 / 4 / 3
- not redundant with H/V or retired density labels
- but only **7/12 buildings** retain the same tone class in >=90% of perturbations

Promotion required >=10/12 stable buildings.

### Hypothesis decision

**Building stroke-tone / pencil-pressure coding = RETIRED.**

The apparent 3-class structure is real enough to cluster, but not stable enough per building to support a deliberate discrete carrier.

## Next stage

**Stage 111 — small-sail ↔ skyline vertical-alignment audit.**

Motivation:
- the five right-hand sailboats form a repeated semantic object class;
- visually they sit below the right-hand skyline and may correspond to five consecutive buildings;
- no prior stage tested cross-object vertical alignment/correspondence;
- this is format-invariant and independent of width, direction, spoke count, density, tone and H/V texture.

Bounded design:
1. Re-detect the five sail centers inside the fixed right-hand band x=900..1585 on original/JPEG85/JPEG70/resize using the corrected Stage-105 detector.
2. Use the 12 fixed skyline building centers from `geometry.json`.
3. Test all **8 consecutive blocks of five buildings**.
4. Statistic: direct same-canvas x-alignment RMS; **no fitted translation or scale**.
5. Require the same best building block across all image variants and sail-center drift <=8 px.
6. Two familywise nulls:
   - translation-preserving null: shift the observed five-sail pattern within the allowed band, preserving all internal gaps;
   - spacing-constrained null: draw five sorted centers uniformly in the band with minimum 70 px spacing.
7. Synthetic aligned coordinate control must identify its known five-building block.
8. Promote only if both null p-values <=0.05 and the same block survives all variants.

A positive result would establish only a visible cross-object correspondence. No key/secret mapping is attempted.

## Status

- Stages 1–110: completed.
- Stage 110: COMPLETED + REVIEWED — stroke-tone coding retired.
- Stage 111: selected for launch.
