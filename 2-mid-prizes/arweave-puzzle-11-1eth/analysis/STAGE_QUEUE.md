# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 106

Stage 106 produced the strongest new direct image result in several stages.

### Stage-106 result

- synthetic sparse/dense controls: **PASS**
- all four real-image variant gates: **PASS**
- metric agreement: **12/12** in every variant
- stable buildings: **12/12**
- cluster sizes: **6 sparse / 6 dense**
- separation: about **3.2–3.4 pooled SD**
- density sequence: **DDSSDDSSDSSD**
- nearly identical to H/V or inverse: **False**
- promotion: **True**

### Hypothesis decision

**A robust building fill-density binary channel is promoted.**

This is not yet evidence of author intent. Stage 106 used fixed building crops, so the next step must test whether the same binary labels survive crop/margin perturbations and whether the split is independent of the already-known H/V channel rather than a crop artifact.

## Next stage

**Stage 107 — adversarial replication + independence audit of building density channel.**

Bounded design:
1. Fixed reference labels from Stage 106: `DDSSDDSSDSSD`.
2. Recompute labels across:
   - original / JPEG85 / JPEG70 / resize;
   - inner margins 8%, 14%, 20%;
   - crop jitters ±4 px in x/y;
   - three density measures: mean darkness, ink<140, ink<160.
3. Align every two-cluster split as sparse/dense by cluster center.
4. Require >=10/12 buildings to reproduce the Stage-106 label in >=90% of all perturbation conditions.
5. Synthetic sparse/dense hatch controls validate the perturbation harness.
6. Exact 6-of-12 permutation test against fixed H/V labels quantifies association; classify the new channel as:
   - redundant,
   - associated-but-distinct,
   - or statistically independent.
7. Report the four-state H/V×density sequence only if the density channel replicates; do not interpret the states as secret symbols.

No private-key mapping is attempted.

## Status

- Stages 1–106: completed.
- Stage 106: COMPLETED + REVIEWED — density channel promoted provisionally.
- Stage 107: selected for launch.
