# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 105

Stage 105 did **not** produce a valid hypothesis result.

Two independently implemented spoke-count detectors both failed their synthetic controls:
- first Hough/radial detector: controls non-monotonic
- corrected skeleton-annulus/scanline detector: controls still non-monotonic at higher spoke counts

The corrected run did improve object localization: the five actual right-hand sail centers were recovered at approximately **[1042, 1148, 1282, 1372, 1490]**, confirming the earlier Stage-19 x=675 track was not a real small sail.

### Hypothesis decision

**Small-sail spoke-count coding = UNRESOLVED / ABANDONED FOR NOW.**

Do not interpret the real counts because the detector is unvalidated. Do not spend further cycles repairing this family without new evidence.

## Next stage

**Stage 106 — building fill-density bimodality audit.**

Motivation:
- the 12 buildings remain the strongest repeated object family;
- roof/topology/count families have failed;
- H/V interior orientation is real but its tested meanings failed;
- mean fill density / darkness is a separate visible feature and has not been tested as a discrete second channel.

Bounded design:
1. Reuse the 12 fixed Stage-12 building interiors.
2. Two independent visible-density measures:
   - mean darkness
   - threshold-140 ink fraction
3. Fit two 1D clusters per metric on each of four image variants.
4. Require:
   - >=10/12 agreement between the two metrics;
   - stable labels across original/JPEG85/JPEG70/resize;
   - balanced clusters (3..9 members);
   - strong separation (>=1.5 pooled SD).
5. Synthetic sparse/dense hatch buildings validate the detector.
6. Compare the final density labels against the known H/V sequence; if nearly identical to H/V or its inverse, classify as redundant rather than a new channel.

No mapping to secret material is attempted.

## Status

- Stages 1–105: completed.
- Stage 105: detector family unresolved after repeated control failure; no real-sail inference accepted.
- Stage 106: selected for launch.
