# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-06

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless one of these is true:

1. a concrete implementation defect is demonstrated in the earlier test; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through corrected Stage 92

Stage 92 initially had a control-sampling defect: the candidate list exhausted the global URL cap before the unrelated-photo null pool was appended. The same stage number was fixed and rerun with independent candidate/null caps.

Corrected Stage-92 result:

- candidate URLs: **110**
- candidate images successfully scored: **74**
- null URLs: **14**
- null images successfully scored: **1** (many external Commons assets failed to fetch in the runner)
- transformed-canonical positive control: **PASS**
- strong candidate matches: **0**
- interesting candidate matches: **0**
- promotion: **False**

The weak null-pool recovery limits calibration of hypothetical false positives, but it does **not** weaken the main negative result here: no source-photo candidate crossed even the weaker “interesting” geometry gate, while the positive control was detected extremely strongly.

### Hypothesis decision

- exact Courageous Sailing candidate page: **RETIRED**
- bounded Boston/sailing/skyline photo pool tested in Stage 92: **RETIRED**
- global unknown-source-photo hypothesis: **UNRESOLVED but deprioritized**; do not broaden image search without new evidence

The best candidate, `CASD5.jpg`, had only 6 SIFT homography inliers and 7 ORB inliers, far below the predeclared strong gate.

## Next stage

**Stage 93 — pier Roman-numeral structure audit.**

This is the only remaining genuinely untested historical visual claim identified by corrected Stage 91.

Historical claim:
> the pier/support structure might visually form **X**, **IX**, or **XI**.

Bounded test:
1. Use one predeclared pier-support ROI: **x=900..1320, y=510..830**.
2. Detect only long straight strokes using multiple fixed Canny/Hough settings.
3. Score three predeclared templates:
   - X = two long opposite-slope segments crossing internally
   - IX = stable X with an adjacent near-vertical stroke on the left
   - XI = stable X with an adjacent near-vertical stroke on the right
4. Require the same structural template to persist across thresholds and JPEG85+resampling.
5. Compare the pier template score against matched same-size image windows with similar ink/long-line density.
6. Include synthetic X / IX / XI positive controls.

Promotion means only “the Roman-like structure is unusually explicit and stable”; it does **not** assign a numeric/private-key interpretation.

A null result retires this historical pier/Roman claim.

## Status

- Stages 1–92: completed.
- Corrected Stage 92: COMPLETED + REVIEWED — negative for tested source-photo pool.
- Stage 93: selected for launch.
