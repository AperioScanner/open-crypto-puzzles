# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 107

Stage 107 completed successfully and **did not confirm the binary density channel as originally defined**.

### Stage-107 result

- synthetic perturbation controls: PASS
- conditions tested: **180**
- buildings reproducing Stage-106 label >=90%: **9/12**
- median Hamming distance vs Stage 106: **3**
- exactly the unstable buildings are **5, 6, 12**
- their Stage-106 darkness values were tightly grouped around **0.436–0.440**
- the clearly dense buildings (1,2,9) were much darker, while the sparse group was much lighter
- density vs H/V exact association p: **0.5455**
- therefore density is not redundant with H/V, but the forced binary split is unstable

### Hypothesis decision

**Binary sparse/dense channel = DOWNGRADED / NOT VALIDATED.**

However, Stage 107 reveals a new, specific pattern: the three unstable buildings form a coherent **intermediate-density group**, suggesting that the real structure may be tri-modal rather than binary.

This is new evidence produced by the adversarial failure itself, so testing it does not violate the anti-recycling rule.

## Next stage

**Stage 108 — three-level building density audit.**

Predeclared model:
- light
- medium
- dark

Bounded design:
1. Reuse the 12 fixed building interiors.
2. Metrics: mean darkness, ink<140, ink<160.
3. Fit k=2 and k=3 1D clusters under:
   - original/JPEG85/JPEG70/resize;
   - margins 8%, 14%, 20%;
   - jitters ±4 px.
4. Synthetic light/medium/dark hatch controls validate k=3 recovery.
5. Require:
   - >=10/12 buildings stable in one of 3 labels across >=90% conditions;
   - all three classes present with >=2 members each;
   - k=3 materially better than k=2 by silhouette/BIC-like score in most conditions;
   - labels not reducible to H/V.
6. Expected failure-driven pattern to test, without forcing it: buildings 5/6/12 may form the medium class.

A positive result establishes only a robust three-level visual density channel. No secret mapping is attempted.

## Status

- Stages 1–107: completed.
- Stage 107: COMPLETED + REVIEWED — binary density not validated; tri-modal density promoted as the next hypothesis.
- Stage 108: selected for launch.
