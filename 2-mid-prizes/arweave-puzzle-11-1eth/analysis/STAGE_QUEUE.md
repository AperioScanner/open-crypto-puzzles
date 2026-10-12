# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-12

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through corrected Stage 113

Stage 113 initially failed its positive control and was repaired under the same stage number. The final synthetic positive and negative controls both pass.

### Valid Stage-113 result

Exact dimensional hypothesis:
`1600 px = 64 private-key hex positions × 25 px`.

Validated harness:
- positive control: **PASS**
- negative control: **PASS**

Puzzle #11:
- phase-0 rank: **21 / 25**
- k=16 silhouette: **0.3499**
- cross-variant k=16 stability: **0.9948**
- occupied states: **16/16**
- singleton states: **3**
- best k by silhouette: **8**
- k=16 rank among k=2..20: **14 / 19**
- k=16 effectively tied with best: **False**
- structural promotion gate: **False**

### Hypothesis decision

**Simple one-hex-symbol-per-25px vertical-cell encoding = RETIRED.**

The exact 25-px boundary is not exceptional and a 16-state alphabet is not the preferred discrete structure.

## New external evidence

A fresh primary public source was identified outside the prior Twitter-focused Puzzle #9 audit:

**Original Reddit thread:** r/ethtrader, 2020-01-21, “100 DAI hidden in this image”
`https://www.reddit.com/r/ethtrader/comments/ersf73`

The indexed thread contains pre-solve mechanism discussion absent from the current branch, including:
- green-leaf/bird angle + “thirteen” speculation;
- “invisible 9 lines” observation;
- a concrete comment interpreting the image as **05/04/2012 and 13:00**, followed by “there's some more ... going on”;
- orange bird facing left + Orwell/1984 discussion;
- LSB suggestion;
- a post-solve comment on 2020-06-09 noting the challenge had been solved.

These are community comments, not yet author-confirmed clues. Their value is that they are contemporaneous and may preserve the missing Puzzle #9 solving path.

## Next stage

**Stage 114 — original Puzzle #9 Reddit-thread reconstruction.**

Bounded archival design:
1. Recover the Reddit thread via public Reddit JSON/HTML and Internet Archive snapshots where available.
2. Preserve comment hierarchy, timestamps, authors when public, and OP/author identity.
3. Separate:
   - OP/author replies;
   - pre-solve community hypotheses;
   - post-solve comments after the 2020-06-08 prize sweep.
4. Search a fixed mechanism vocabulary: date/time, 05/04/2012, 13:00/thirteen, birds/colors/direction, angles, lines, Orwell/1984, LSB/steganography.
5. Compare any concrete multi-step claim against the primary-verified author statement that Puzzle #9 required four steps.
6. Promotion requires either:
   - a mechanism-specific OP/author reply; or
   - a concrete pre-solve multi-step path independently corroborated by a post-solve/author source.
7. Community speculation alone is recorded but **not promoted**.

No secret/key candidates are constructed or verified.

## Status

- Stages 1–113: completed and reviewed.
- Stage 113: VALID NEGATIVE — 64×25 equal-cell carrier retired.
- Stage 114: selected for launch.
