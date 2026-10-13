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


## 2026-10-13 — reviewed image-only Stages 120 and 121

### Stage 120 — REPLICATED CONTROL PASS, NEGATIVE WITH NARROW SCOPE
- Run: https://github.com/AperioScanner/open-crypto-puzzles/actions/runs/38424534898
- Canonical SHA256 verified; ORB exact-duplication and mirror positives pass with 205 inliers / 0.3198 fraction; 24 independent redraw negatives max 0.0514.
- All five sail centers stable (<=2 px); ten pair comparisons each have 0/4 transformed variants crossing the required calibrated threshold (>=25 RANSAC inliers and >=0.18 fraction).
- Decision: retire *identical reused interior pen-stroke template among five small sails*, not all common triangular symbolism or sail meanings.

### Stage 121 — CALIBRATION PASS, NEGATIVE / MEASUREMENT AMBIGUITY
- Run: https://github.com/AperioScanner/open-crypto-puzzles/actions/runs/38425779620
- Synthetic line-count controls pass 82/82 (two orientations, 5 known stroke counts, four variants, plus dot controls).
- Real facades: 0/12 stable integer hatch-line counts across the two independently predeclared counting estimators and lossy variants.
- Decision: no supported *precise, individual long-hatch count* sequence. Manual re-interpretation or looser thresholds must not be presented as evidence. This is not a negative for arbitrary semantic or BIP39 mappings.

**Next:** no more Twitter. Before the next Stage, propose one genuinely new image-only hypothesis with independent evidence, positive/negative controls and a precommitted stopping rule. Do not recycle exact sail duplication, precise facade hatch counts, density, tone, roofs, Braille, or previous covered image carriers. Never generate or test secret keys/mnemonics.


## 2026-10-13 — Stage 122 preregistered (image-only)

**Stage 121 reviewed:** run #38425779620 completed. Canonical image SHA-256 matched; 82/82 synthetic line-count checks passed within their ±1 calibration tolerance. Zero of twelve real building facades produced an exact jointly stable count across the two methods and four variants. This retires only the direct per-building *precise long-hatch-count* interpretation, not arbitrary building symbolism.

**One new experiment:** Stage 122 — six-sail left/right shading polarity, including the large sail and five smaller ones. This compares the shading of symmetric, fixed triangular interior wedges, subtracting matched left/right outside-wedge ink, across original, JPEG85, JPEG70 and 75%-resample. The visible fact motivating the test is that the sail triangles have visibly hatched and unhatched sectors; no binary symbolism is assumed in advance.

**Fixed controls/gates before execution:**
- Canonical SHA-256 must match `c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1`.
- Six manually anchored sites, unchanged between original and lossy images, specified in `tools/stage122_sail_side_shading.py`.
- Synthetic right-dark, left-dark and neutral patches, all four variants. Controls must correctly resolve sign and not treat neutral as a clue.
- Require absolute corrected contrast >=0.14, raw contrast >=0.13, adequate ink/sample coverage, and agreement of all four variants.
- A nontrivial *visual* pattern needs >=5/6 valid sites and both left-dark and right-dark cases. All-one-side is consistent with natural drawing/shading, not a 6-bit message.
- Control failures: repair **Stage 122**; low source coverage/unstable signs: narrow negative or inconclusive as applicable; any apparent positive requires independent confirmation and cannot be interpreted as a key or mnemonic.

**Restrictions:** no Twitter or off-image reference, no private keys, no BIP39 candidates, no wallet access, no new search over retired widths/roof/hatch counts. Do not promote an image-only contrast as a secret encoding.

Script: `tools/stage122_sail_side_shading.py`; results: `analysis/runs/stage122-sail-side-shading/`.
