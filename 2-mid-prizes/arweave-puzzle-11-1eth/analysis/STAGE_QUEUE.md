# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 104

Stage 104 completed successfully.

### Stage-104 result

- synthetic 0/1/2/3-hole controls: PASS
- stable buildings: **0/12**
- stable count sequence: all unknown
- promotion: **False**

### Hypothesis decision

**Building enclosed-space/window topology = RETIRED.**

Counts vary strongly with threshold and lossy transforms, so they are not a robust visual code.

## Next stage

**Stage 105 — five-small-sail radial-spoke count audit.**

Motivation:
- the five small sails are repeated semantic objects;
- their internal lines visibly radiate from the apex toward the base;
- prior sail stages tested widths, gaps and overall lean, but not internal ray/spoke counts;
- spoke count is human-visible and format-invariant, fitting the active semantic/counting prior.

Bounded design:
1. Reuse the five fixed Stage-19 sail x-ranges and y=360..480.
2. Estimate each sail apex from the uppermost dark pixels.
3. Two independent count estimators:
   - Hough long-line angle clusters passing near the apex;
   - polar/radial angular ink-profile peaks from the apex into the sail body.
4. Repeat on original, JPEG85, JPEG70 and 0.75x resize roundtrip.
5. Synthetic sails with 3,4,5,6,7 radial spokes validate both estimators.
6. Promote only if >=4/5 real sails have the same count across all image variants with estimator agreement (±1 at most), and at least two distinct stable counts occur.

A positive result establishes only a robust visible spoke-count sequence. No secret mapping is attempted.

## Status

- Stages 1–104: completed.
- Stage 104: COMPLETED + REVIEWED — topology coding retired.
- Stage 105: selected for launch.
