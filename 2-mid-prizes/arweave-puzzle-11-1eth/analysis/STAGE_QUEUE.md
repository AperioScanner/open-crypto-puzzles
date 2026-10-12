# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-12

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through corrected Stage 109

Stage 109 tested the historical 5|7 skyline split.

Geometry alone is striking:
- dominant inter-building gap: after building 5
- width: **102 px**
- second-largest gap: **4 px**
- ratio: **25.5×**
- midpoint only **2.1%** of image width from canvas center
- exchangeable-gap null p ≈ **5e-6**

However, independent image detectors could not be calibrated cleanly:
- literal-blank detector failed because horizon strokes cross the gap;
- full-height relative occupancy detector failed its synthetic negative control because building height itself creates low-occupancy corridors;
- lower-band relative detector still failed its synthetic control and only matched the target at thresholds 140/180, not 100.

### Hypothesis decision

**5|7 delimiter = NOT PROMOTED.**

Retain the 102 px geometry fact, but do not treat it as an intentional delimiter without a validated independent detector. Do not spend further cycles tuning this family absent new evidence.

## Next stage

**Stage 110 — building stroke-tone / pencil-pressure audit.**

Motivation:
- density amount was tested and retired, but conditional stroke darkness/tone is a distinct feature;
- the drawing visibly contains darker and lighter pencil strokes;
- stroke tone should survive ordinary JPEG/resampling if deliberate;
- no prior stage tested per-building ink tone as a discrete channel.

Bounded design:
1. Reuse the 12 fixed Stage-12 building interiors.
2. Perturb crop margins (8/14/20%) and x/y by ±4 px across original/JPEG85/JPEG70/resize.
3. Two independent tone measures:
   - median darkness of Otsu-selected ink pixels;
   - median darkness sampled on Canny edge pixels.
4. For every condition, compare k=2 vs k=3 one-dimensional cluster models using BIC.
5. Synthetic binary-tone and ternary-tone hatch controls validate model selection independently of hatch orientation/density.
6. Promote only if:
   - synthetic controls recover the correct model and labels;
   - one model (k=2 or k=3) wins in >=80% of real conditions for both metrics;
   - >=10/12 buildings retain the same ordered tone class in >=90% of conditions;
   - each class has >=2 members;
   - labels are not nearly identical to H/V or the retired density labels.

A positive result establishes only a robust visible stroke-tone channel. No secret/key mapping is attempted.

## Status

- Stages 1–109: completed.
- Stage 109: COMPLETED + REVIEWED — 5|7 geometry notable but delimiter not validated.
- Stage 110: selected for launch.
