# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 103

Stage 103 completed successfully.

### Stage-103 result

- synthetic roof controls: PASS
- stable buildings: **2/12**
- roof sequence: **?????-?-????**
- only category represented: flat (`-`)
- promotion: **False**

### Hypothesis decision

**Building roof-profile coding = RETIRED.**

The two estimators disagree on most real buildings, especially after lossy transforms.

## Next stage

**Stage 104 — enclosed-white-space / window-topology audit across 12 buildings.**

Why:
- solved siblings favor secondary visible details/counting;
- Stage 12 counted dark connected components/perimeter occupancy, but did **not** count enclosed white holes/windows;
- topology is format-invariant and distinct from H/V texture, roof slope, height/width and prior component-density tests.

Bounded design:
1. Reuse the 12 fixed building interiors from Stage 12.
2. Threshold at 100/130/160/190.
3. Flood-fill exterior white; count only enclosed white components.
4. Exclude tiny antialias holes (<9 px) and very large openings (>15% crop area).
5. Repeat on original, JPEG85, JPEG70 and 0.75x resize.
6. Require stable count per building across thresholds and variants.
7. Synthetic 0/1/2/3-hole building controls validate the detector.
8. Promote only if >=9/12 buildings yield stable counts and at least 3 distinct count values are represented.

No mapping from counts to secret material is attempted.

## Status

- Stages 1–103: completed.
- Stage 103: COMPLETED + REVIEWED — roof-profile coding retired.
- Stage 104: selected for launch.
