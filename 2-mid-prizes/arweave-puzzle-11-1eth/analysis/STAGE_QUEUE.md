# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-12

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 118

Stage 118 completed successfully and its positive control passed.

### Stage-118 result

Fixed stable building sequence:
`HHVVHHVHHHHV`

Exactly four predeclared standard-Braille readings were tested:
- LTR, H raised → `?T`
- LTR, V raised → `??`
- RTL, H raised → `T?`
- RTL, V raised → `??`

No reading produced two Braille letters.

Count-matched exact null:
- 495 sequences with the same 8H/4V balance
- 242/495 produce at least one two-letter reading under the same four mappings
- familywise probability = **0.488889**

Decision: **standard two-cell Braille RETIRED**.

Do not expand this negative into arbitrary binary alphabets.

## Active prior after Stage 118

Stage 117 remains the strongest mechanism-family evidence:
- recurrent **visible text/symbol reading**
- recurrent **cross-domain conversion**
- generic ordering/traversal was not recurrent

A literal visible cross-domain pointer exists in Puzzle #11 itself: the watermark `twitter.com/ArweaveP`.

Prior archive work reconstructed posts and replies, but did not test whether the watermark points to contemporaneous **profile/header visual context** that could act as a cross-domain clue.

## Next stage

**Stage 119 — watermark-directed @ArweaveP profile/header archive audit.**

Question:
> Did the visible `twitter.com/ArweaveP` watermark point, at publication time, to profile/header imagery or profile metadata that reused or materially referenced the Puzzle #11 scene?

Bounded design:
1. Query archived snapshots of the exact @ArweaveP profile around 2020-04-20 through 2020-05-02.
2. Recover only profile-level metadata and referenced profile/header/OG images.
3. Source control requires at least one timestamped archive snapshot tied to the exact handle.
4. Compare recovered profile/header images to canonical Puzzle #11 using perceptual similarity + ORB/RANSAC geometry.
5. Record only short public profile metadata and image-similarity statistics.
6. Promotion requires either:
   - a strong geometric visual derivative of Puzzle #11 in contemporaneous profile/header imagery, or
   - an explicit profile-level puzzle-specific reference independently tied to the image scene.
7. If archive recovery fails, classify SOURCE_FAILURE and repair Stage 119; do not interpret as a negative.

No private-key material is generated or tested.

## Status

- Stages 1–118: completed and reviewed.
- Stage 118: VALID NEGATIVE — standard Braille retired.
- Stage 119: selected for launch.


## 2026-10-13 — image-only user scope directive (supersedes older Stage 119 priority)

**No new Twitter, profile, header, social-archive, or external biography experiments.** The user redirected this research explicitly to the canonical puzzle image. Stage 119 is an archived, source-limited result and NOT a validated negative on missing historical profile/header material. It is shelved by scope, not completed as a scientific negative.

**Current experiment: Stage 120 — small-sail exact stroke-template reuse.**

- Input: canonical puzzle PNG, SHA256 `c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1`.
- Scope: five correctly detected right-hand sails, comparing entire normalized visible motifs by ORB/RANSAC, including horizontal reflection and JPEG/resampling replication.
- Tests whether the drawn internal strokes originate from a replicated image template. Different from retired sail widths, L/R, spoke-count, and sail-skyline alignments.
- Positive controls: repeated template under affine transform, JPG70 and mirror; negative controls: independently drawn synthetic sails with matched outer silhouettes.
- A matching pair must pass fixed minimum 25 inliers, calibrated fraction gate, all four transforms and mirror consistency.
- If controls fail: fix Stage 120 without advancing; if source/recovery fails: keep INCONCLUSIVE; if valid negative: retire *exact duplicated stroke template* only.
- Do not infer BIP39 words, keys or any secret from visible silhouettes.
- After Stage 120 result is audited, select exactly **one** further novel image-only experiment under the anti-recycling rule.

Run: https://github.com/AperioScanner/open-crypto-puzzles/actions/runs/38424534898
