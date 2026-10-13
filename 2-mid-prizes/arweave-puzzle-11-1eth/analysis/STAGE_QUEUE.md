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


### Stage 122 repair — source-region contamination (same stage number)

The first run passed 72 synthetic controls but the real-data diagnostic exposed large, sign-reversing exterior baselines for small sails; color-marked mask-contact.png confirms exterior reference masks cross *other sailboats and the pier*. Those regions are not valid matched-background controls. Therefore the initial "corrected-contrast" interpretation was **not a valid finding** about sail coding.

Repaired within Stage 122: preserve the exact original 6 interior masks, four image variants and 0.14/0.13 thresholds. Classify ONLY directly observed right-minus-left *within-sail* contrast; keep exterior measurements as contamination diagnostics, not subtraction. No after-the-fact retuning of sensitivity. Repair run: https://github.com/AperioScanner/open-crypto-puzzles/actions/runs/38458971789. Verify controls and real coverage before any conclusion.


## 2026-10-13 — final Stage 122 audit; image-only Stage 123 preregistered

Stage 122 run #38458971789 completed with canonical image check and all 72 synthetic controls PASS. The initial external-background subtraction was rejected after an actual mask-contact audit because outside wedges crossed other boats and the pier. The corrected, unchanged-threshold inside-wedge method found only **3/6** stable right-side-shaded sail regions; one negative-signed region did not survive all variants and two more were too weak. Decision: **NO_STABLE_SIX_SAIL_SIDE_PATTERN**, retiring only this precommitted within-wedge six-sail shading scheme. Do not broaden to general sail meanings.

**New Stage 123, one experiment only:** inspect 64×64 pencil-stroke fragments on a precommitted 32px grid for near-exact *cross-region* duplication between (1) skyline, (2) left water/large boat, (3) right pier/small boats. Unlike Stage 120, which compared only the five small sails against each other, Stage 123 explicitly excludes within-region sail-to-sail comparisons and seeks direct copied raster motifs crossing different drawn object categories.

- Precommit static masks / grid and restrict ink-occupancy to 0.07..0.80. Select top 60 descriptor pairs per cross-region pair.
- Thresholds: full-resolution correlation >=0.95 original, >=0.91 each lossy variant; ink-mask IoU >=0.82 in all four; >=15 eligible patches in each region.
- Positive control: same synthetic stroke patch stamped in two distant region grids, retaining match after JPEG/resampling. Negative: independently drawn similar patches on the same sites must not match.
- If control fails: repair Stage 123 under same number; if coverage fails: INCONCLUSIVE, not a negative; if match appears: independently confirm before claiming significance. If no match: retire only these fixed-grid translational clones.
- No external references, no wallet/key/mnemonic operations. Do not reuse Stages 120–122 interpretations.

Script: `tools/stage123_cross_region_stroke_reuse.py`


## 2026-10-13 — Stage 123 audited; Stage 124 preregistered

- Stage 123 run #38459664096 completed, controls PASS (5 copied-patch hits, 0 independently drawn negatives); canonical image checked; 180 top cross-region patch pairs evaluated across four formats and **0 reproduced**. Coverage valid (228/265/230 eligible patches across skyline/left boat-water/right pier). Retire only *exact, unrotated, same-scale, fixed-grid 64×64 duplicated raster motifs across these three regions*. Do not expand into arbitrary transformed copies without new evidence.
- Stage 124 now selected under the anti-recycling *implementation defect* exception: previous Stage 102 tested sail directions based on Stage 19 boxes at x~675,1046,1144,1269,1361, thus including one non-sail and omitting the real fifth rightmost sail at ~1490. Stage 112 independently documented the error.
- Different observable: fixed true-five-sail apex-to-base outline midpoint offset, not Hough/Sobel hatch direction, widths, ray counts, shade darkness, or cryptographic values.
- Exactly five immutable apex sites inherited from Stage 122; two image methods (binary ink and Canny edges); original/JPEG85/JPEG70/75% resize; preregistered support and sign thresholds; synthetic L/N/R controls at all five sites. Require >=4 resolvable objects and strongly signed BOTH directions for promotion. Control failure => repair Stage 124, insufficient outlines => INCONCLUSIVE, else negative only for this explicit silhouette criterion.
- Image only. No off-image research or secrets/wallet activity. Script: tools/stage124_true_sail_outline_offset.py


## 2026-10-13 — Stage 124 validated / Stage 125 selected

Stage124 GitHub run #38478839142 completed with success and canonical image hash matched. **120/120 synthetic L/N/R contour controls** passed on five true sail sites, two estimators and four lossy variants. On real pixels, four of five were stably classified: three neutral and one left-offset (rightmost x~1490); small #2 was a stable but borderline -0.25, unclassified under precommitted thresholds. No 4/5 mixed-sign pattern: negative ONLY for that geometry-as-multistate-signal gate.

The sole rightmost left-offset is an actual new empirical lead requiring adversarial replication, not an encoding. Stage125 preregistered: independently test whether rightmost sail is an outlier of all five under source anchor jitter ±4px x / ±3px y, ink threshold 155/175/195, binary and localized Canny, 4 lossy variants. Positive synthetic: fifth offset left, other four centered; negative: all centered. Need >=90% coverage and >=90% source-independent ranked lead fraction with gap >=0.16 and offset <=-0.28. Control failure: repair Stage125 same number; otherwise note limited observation only. No secret operations or Twitter.


## 2026-10-13 — Stage 125 reviewed; Stage 126 preregistered

Stage 125 run #38479304077 finished. Canonical image SHA matched. Synthetic controls succeeded: artificially unique fifth-left outlier in 216/216 configurations, all-neutral false positives 0/216. All 216 real configurations were usable. The fifth sail was numerically most left-offset in 209/216, **but ZERO of 216** satisfied the previously fixed minimum isolation gap and offset together; verdict UNREPLICATED_RIGHTMOST_OUTLIER. Do NOT promote a distinct rightmost marker or loosen criteria after seeing results. Retire the narrow strong-isolated-lean hypothesis.

**Exactly one next image-only test: Stage 126 — small-sail masthead tiny protrusions.** Solved-series studies supported deliberate tiny secondary drawn marks; the image contains 5 triangular sail tips. This test is unlike former interior spoke counts, signed side shading, hull/outline offsets, roof profiles, or raster template duplication. It checks a predeclared short zone immediately above each of the five corrected sail apex sites for the presence or absence of a thin vertical mast protrusion, across original/JPEG85/JPEG70/resampled variants and fixed x jitters {-2,0,2}.
Controls: synthetic mast extension, no extension, and distracting nearby off-axis line, at all five sites in four formats and three x jitters. Require all synthetic outcomes correct before interpreting real data. A candidate multistate clue needs >=4/5 stable classified apices with BOTH states present; uniform and ambiguous results cannot be promoted. Only source ROI behavior assessed; a failure of synthetic controls requires repair under the same Stage 126, not Stage 127.
No social sources, words, keys or wallet activity.
Script: tools/stage126_masthead_protrusion.py


## 2026-10-13 — Stage 126 reviewed; Stage 127 preregistered

Stage 126 GitHub Actions run #38480951073 succeeded and canonical PNG matched. 180/180 mast-extended, mast-absent and off-axis decoy controls passed. Real tiny masthead-extension classes were EXTENDED, EXTENDED, ?, EXTENDED, EXTENDED. All four stable labels are alike; no observed mixed present/absent marker. Retire ONLY this five-sail tip-extension binary-code hypothesis.

Stage 127 now selected: genuine different, image-only hull **waterline signed slope**, measured BELOW the five boats, not Stage102 sail lean or Stage124 triangular outline. Five hull bands fixed from the same known sail positions. Two image methods (Canny edges vs thresholded contours), original/JPEG85/JPEG70/75%-resampled. Gate: >=2 detected Hough line segments, >=48px total segment lengths; DOWN_RIGHT slope >=+0.12, UP_RIGHT <=-0.12, LEVEL <=0.055. Require >=4/5 fully stable across both detectors/four variants and BOTH slopes for a nontrivial mixed visual pattern.

Predeclared synthetic controls: opposite-sloped hulls (R,L,R,L,level) and all level hulls with an unrelated diagonal decoy below, both 5/5; fail either => CONTROL_FAILURE, do not interpret real data, repair Stage127 under same number. Real <4/5 classified => INCONCLUSIVE; otherwise absent opposite slopes is a narrow negative. Image-only. No BIP39, private-key, wallet, Twitter or external research.

Script: tools/stage127_hull_waterline_slope.py. Artifacts: analysis/runs/stage127-hull-waterline-slope/ including ROI contact PNG.
