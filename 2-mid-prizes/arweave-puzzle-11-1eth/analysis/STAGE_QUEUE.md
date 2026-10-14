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


## 2026-10-13 — Stage 127 inconclusive; Stage 128 preregistered

- Stage 127 #38482080263 completed successfully and synthetic mixed vs neutral+decoy controls passed. All 5 real hulls failed the cross-detector/cross-format stable classification (0/5). Examination of hull-roi-contact.png shows the fixed narrow hull strips contain neighboring sail strokes and pier strokes. This is a source-separation failure, **not proof of no hull-slope encoding**. The inconclusive Stage 127 remains archived without promotion or negative extrapolation; no data-driven changes to cutoffs.
- The user requested a new stage. **One new, nonoverlapping visual question:** Stage 128 tests whether hand-drawn water ripples in four specified water regions form reproducible *closed loop* subdetails rather than open scribbles. Stage 104 tested roof/building topology, not water. Existing reflection-coupling stages tested orientation/correlation, not topological closure.
- Two fixed hole detectors (contour hierarchy and white-component floodfill); 3 grayscale thresholds (130/175/210); original/JPEG85/JPEG70/75%-resampled; 4 predeclared water ROIs.
- Positive control: 4 thick closed ellipses (>=3 detected across all settings); negative: 4 incomplete arcs (0 detected in all settings). If controls fail, repair **Stage 128**; otherwise positive promotion only if >=3/4 regions yield exactly repeatable counts across 2 methods x 3 thresholds x 4 formats, including >=2 with a nonzero loop count. In all outcomes do not infer keys, BIP39, semantic words or external references.
- Files: tools/stage128_water_ripple_loops.py, analysis/runs/stage128-water-ripple-loops/.


## 2026-10-13 — Stage128 audited; Stage129 precommitted

Stage128 run #38484785422 successfully completed. SHA matched, closed-vs-open synthetic controls passed (closed: 4/4 over all tests, open: 0). Real image 0/4 water ROIs had counts simultaneously stable across two enclosure detectors, three thresholds and four lossy formats; count ranges [0,10], [0,4], [2,18], [3,13]. Narrow valid non-promotion of the fixed closed-water-loop count hypothesis only.

Stage129 selected under documented anti-recycling implementation-error exception: Stage102 used a falsely identified sail near x~675 and omitted the true fifth sail x~1490; Stage112 proved the object association defect. Stage129 rechecks *internal diagonal pencil hatch direction* with five correct small sails. Excludes exterior sail outline base-offsets (Stages124-125), darkness-side asymmetry (Stage122), exact hatch counts (Stage121), size/width/copy tests (Stages112/120), and hull-waterline slopes (Stage127).
Precommitted fixed triangular masks, independent Sobel-gradient tangent and Hough diagonal-line sign checks, four image formats, five positive/negative/neutral synthetic controls per sail. Both algorithms must agree in all four variants on >=4/5 true sails, with both signs present, to promote merely a visual mixed-direction observation. Control failure: fix SAME Stage129; insufficient real coverage: inconclusive, not negative. No key, BIP39, wallet or Twitter operations.
Script: tools/stage129_corrected_sail_hatch_direction.py.


## 2026-10-13 — Stage129 repaired and validated; Stage130 preregistered

- Stage129 first run #38485119956 was INVALID: only 34/60 synthetic POS/NEG/neutral controls worked because narrow clipped masks disrupted short Hough-line estimates. Corrected this SAME stage under commit 06cf361c14193ff79b6c270ab032a110153d48da, replacing Hough with image-intensity *directional lag-autocorrelation* while holding original triangular masks, Sobel, signed threshold 0.23 and lossy variant set fixed.
- Stage129 repaired run #38485582635: all **60/60** synthetic controls passed, canonical hash verified, but real full-sail Sobel scores were near neutral and failed to agree in signed polarity with lag-correlation. **0/5** confidently classified. Decision INSUFFICIENT_REAL_HATCH_COVERAGE (not an absence-of-code claim). No further relaxation permitted.
- Stage130 is ONE follow-up on a newly observed source phenomenon: real full-sail orientation may cancel because the triangular sail comprises left/right penciled panels with opposing hatches. Fixed left/right masks split the same five true sail interiors; Sobel vs independent grayscale lag-autocorrelation; four original/lossy variants.
- Five synthetic source controls at each site (POS/NEG, NEG/POS, POS/POS, NEG/NEG, horizontal/horizontal) × four variants = 100 test cases; classification gate remains 0.23.
- Promotion requires >=4/5 sails individually classified in BOTH halves across BOTH methods/FOUR formats, with >=4 opposite-sided and BOTH swapped panel orders present. Ordinary same-order opposed hatching is not evidence of a message. If source coverage insufficient, label INCONCLUSIVE; if controls fail repair Stage130.
- Do not generate, map, enumerate, derive or verify any private keys, wallet addresses, or BIP39 words; image-only, no Twitter or social archive.
- Script: tools/stage130_sail_two_panel_direction.py; outputs: analysis/runs/stage130-two-panel-sail-hatching/.


## 2026-10-13 — Stage 130 reviewed; Stage 131 image-only experiment preregistered

- Stage 130 GitHub Actions #38485935539 completed; canonical hash verified, 100/100 precommitted left/right, both-sign and neutral synthetic panel controls passed. On real pencil strokes **0/5** sail panel pairs satisfied two-detector agreement across all four source/lossy formats. A few individual halves were reproducible, but opposing Sobel/lag signs in others cannot be interpreted as a code. Verdict **INSUFFICIENT_PANEL_COVERAGE**: not a negative about all sail markings. Do not relax Stage129–130 gates post hoc.
- Next Stage **131** changes visual region and observable rather than recycling sail angle questions: isolated deliberately drawn *short sky marks* vs single-pixel image speckles, only in four fixed blank sky windows outside roofs, boats and water, and below the top 0..48 strip previously counted in Stage12. Two independent segmentation outputs (8-connectivity components; contour boxes), three thresholds (90/140/190), original/JPEG85/JPEG70/downsample, location drift <=3px. Positive calibration: exactly three short synthetic dashes in each ROI; negative: random one-pixel speckle fields yield zero accepted marks. Promotion requires >=3/4 stable real ROIs including >=2 with nonzero marks, otherwise narrow negative or source limitation. Control failure => repair same Stage131. No OCR, secret, BIP39, wallet or external-site work.
- Tool: tools/stage131_sky_isolated_marks.py; outputs analysis/runs/stage131-isolated-sky-marks/ plus visual source contact.


## 2026-10-13 — Stage 131 reviewed, Stage 132 preregistered (image-only)

- Stage 131 Action run #38487611024 completed. Canonical image SHA256 correct. Synthetic three-dash controls in all four ROIs and 1px speckle negatives passed 192/192; 4/4 real empty-sky ROIs were stable but had zero qualifying short line marks across 3 thresholds, two detectors and all four renderings. Decision: NO_REPLICATED_ISOLATED_SKY_MARK_PATTERN. This retires only the specified sky ROIs/isolated-mark filter; does not rule out a clue elsewhere.
- **Concrete new image-geometry concern:** data/geometry.json describes the "large_sailboat" as bbox [44,320,359,599], but direct canonical image shows a large sail and vessel extending well below/right. Some Stage 36 / 94 measurements used this ROI; need a controlled coverage audit, not arbitrary new decoding.
- Stage 132 precommits manually annotated, approximate large-sail triangle [(242,398),(56,758),(512,760)] and hull quad [(25,783),(525,778),(480,931),(75,939)] before any outcome, compares the actual pencil ink inside these polygons against the legacy bbox.
- Sources: only canonical PNG plus repository geometry.json. Three cutoffs (110,170,210) × four variants (original/JPEG85/JPEG70/down75_up); require sail ink >=1500, hull ink >=1500, ink density >=8% and >4× blank-sky noise, and >=65% of sail plus >=96% of hull ink outside legacy box in **all** 12 cases.
- Synthetic full-object positive must show substantial missing ink; synthetic cropped-to-legacy negative must show near-zero missing ink/no hull ink. If controls fail, repair Stage132 under SAME number. Any positive is only a SOURCE ROI defect; previous ROI-dependent negatives need reevaluation but are not automatically reversed. Never generate secret material.
- Files: tools/stage132_large_sail_legacy_bbox_audit.py; outputs analysis/runs/stage132-large-sail-roi-coverage/ with colored overlay.


## 2026-10-13 — Stage132 VALID SOURCE DEFECT; Stage133 preregistered

- Stage132 GitHub run #38488910201 completed; canonical SHA confirmed. 24/24 synthetic full-shape-vs-truncated controls passed. Across the full fixed family of 3 thresholds x 4 source/lossy variants (12/12), the former `data/geometry.json` `large_sailboat` bbox (44,320)-(359,599) omitted >=65% of the ink in the manually fixed triangle and >=96% of the hull. At original threshold 170, omitted **66.7162%** of in-triangle ink and **100%** of in-hull ink. This is a demonstrated ROI implementation defect. It does not prove a hidden message or invalidate every unrelated earlier result.
- Stage133 selected, NOT random reopening: rerun the nonsecret Stage94 diagonal-stroke *capacity counts only* with the same detector and thresholds on both legacy truncated ROI and the corrected Stage132 triangle polygon, keeping all four real-image re-encoding variants.
- Precommitted controls: a blank sail must yield zero tracks; synthetic short drawn 16-stroke and 64-stroke examples must yield >=6 and >=15 detected tracks respectively, with >=10 count separation. Also require corrected fixed-mask source ink >=1200 and >=65% outside the old source bbox. Control failure => repair **Stage133**, not progress. All old/new stroke signs remain unordered; nothing is generated/derived/checked as a key.
- Any count difference is descriptive. Stage94's prior negative can no longer be generalized to the full visible large sail without checking corrected ROI. Neither 64 nor 256 marks are promoted as a cipher absent independent evidence.
- User asked for probability the image itself matters over raw file format. The archive's source-author hint "format does not matter" and image-level invariance favor visual/semantic carriers over fragile PNG-specific bit patterns. This is a qualitative prior, NOT a frequency-based posterior probability, and visible geometry might still require arithmetic.
- Tool: `tools/stage133_corrected_full_sail_strokes.py`, result `analysis/runs/stage133-corrected-large-sail-strokes/`.


## 2026-10-13 — Stage 133 completed; Stage 134 preregistered

- Stage133 Actions #38489793473 completed successfully (verified status and saved REPORT/result.json). Corrected full-sail source mask valid, ink outside the Stage94 legacy ROI **84.9%** for this eroded mask; Stage132 original larger-polygon comparison was 66.7% sail and 100% hull missed. Synthetic blank=0 tracks, 16 visible strokes -> min 15, 64 strokes -> min 42; controls pass.
- **Old Stage94 measured 10–14 classifiable strokes across 4 formats; full Stage132 sail geometry yields 76–90 with exactly the same Stage94 algorithm.** Old negative for that truncated source cannot be generalized to entire large sail. Counts neither prove 64 nor 256 encoded symbols, and no ordered target sequence was stored.
- Precommit exactly ONE next experiment: Stage134 re-audits another concrete ROI-dependent earlier negative, Stage36's visual glyph-line-reveal heuristic. Reuse the exact fixed 19 Stage36 transforms/connected-component alignment metric, replace its truncated large-sail box with the immutable Stage132 triangle, and compare against 3 equal-sized *same-aperture* scene controls, over original/JPEG85/JPEG70/75%-resampling.
- Positive synthetic fixture: aligned visible non-secret demo "ABCD" inside the aperture versus independent scribbles; negative: scribble target and text comparator. Both must separate under the exact predeclared Stage134 rank/margin family rule (>=3 transform candidates replicated in 4 renderings, from >=2 transform families, score margin >=0.15 and >=3 aligned components). If control failure, repair **Stage134**, not a new Stage. Real positive would mean only **manual visual review warranted**, not valid glyphs, text extraction, secret or key. Real negative retires only the fixed transform family for the **correct source ROI**.
- No OCR, BIP39, private key, wallet, Twitter or external site operations. Script: tools/stage134_corrected_full_sail_visual_reveal.py.


## 2026-10-13 — Stage134 repaired, reviewed; Stage135 preregistered

- Stage134 first run #38490289635 concluded CONTROL_FAILURE despite successful workflow: the synthetic ABCD source-control width covered only ~14.2% of the corrected sail crop, less than the fixed 15% x-coverage cutoff. This was a *fixture* defect; kept unchanged detector, 19 transforms, rank, gate, source-mask and all real-image inputs. Corrected SAME Stage134 fixture to ABCDEFGH spanning the supported aperture.
- Stage134 repaired run #38490532439: positive synthetic 9 fully reproduced transforms across 4 independent families; negative synthetic 0; controls PASS. Real full sail: 3/19 original qualifying transforms, only 2 replicated across formats, both DoG (single family). Decision NO_REPLICATED_CORRECTED_SAIL_GLYPH_ALIGNMENT. Retires only Stage36 family of generic glyph-line alignment in corrected sail polygon. No OCR, word or key was found.
- Stage135 is a distinct image-only structural question supported by Stage133's 76–90 **full sail** detectable diagonal tracks, including + and -: are these stroke directions strongly organized into 2×2 visible geometry sectors (upper/lower x left/right) rather than spatially exchangeable?
- Same fixed Stage132 triangle/Stage94 stroke detector; no ordered stroke sequence persisted. Divide using triangle apex and base-midpoint spine, exclude +/-8px seam and +/-12px horizontal midline. Analyze exactly 4 regions, conditional permutation n=20,000 per JPEG/original variant, within-format p<=.01 and Cramer's V>=.35, min >=40 classifiable and >=4 tracks per sector. Require ALL FOUR variants strong with same four majority signs, both sign categories, at least 10% majority margin.
- Precommit synthetic 80 track positive with clear alternating quadrant majority (p<.01/V>.35), and matched balanced-per-quadrant negative (p>.05/V<.1). This calibrates the *statistical test*, while the pixel detector/source is separately calibrated by Stage133. If control failure repair Stage135; inadequate real-sector source coverage is INCONCLUSIVE. A positive would be a structural lead requiring independent human confirmation, not a private-key encoding; no BIP39/ETH/Twitter/other external operations.
- Script `tools/stage135_full_sail_quadrant_orientation.py`, reports `analysis/runs/stage135-full-sail-quadrant-orientation/`.


## 2026-10-13 — Stage135 POSITIVE aggregate, Stage136 follow-up registered

- Stage135 run #38490812973 succeeded. Synthetic structured-vs-balanced controls PASS, canonical SHA matched, all four source variants adequate, and all four show very strong **side-dependent** full-sail line directions (Cramer's V .819..902; 20k permutation p floor 0.00005). In every variant quadrants are **upper-left NEG, upper-right POS, lower-left NEG, lower-right POS**. This supports a stable left/right V-hatch symmetry, but is **not** evidence of an intentional encoded private key. The prior fully random-label permutation null fails to model the ordinary drafting convention of alternating hatch lean on triangle sides.
- Stage136 is the ONE precommitted follow-up: test extra top/bottom structure **conditional on LEFT/RIGHT side** using exact two-sided-like Pearson statistics and within-side hypergeometric enumeration over fixed 2x2 sign tables, rather than Stage135's globally exchangeable sign null. Recompute Stage135 aggregate counts from canonical source to verify source and avoid relying on archived output alone.
- Synthetic negative control: natural mirrored V left NEG/right POS same at both heights => conditioned p>.05. Synthetic positive: top vs bottom signs invert within both sides => p<=.01 and fraction difference >=.25. Balanced null also must not classify. Real promotion requires all 4 formats adequate (>=40 tracks, >=4 per quadrant), conditioned p<=.01, >=.25 upper/lower difference in >=1 side, consistent direction across formats. Otherwise the Stage135 signal can be explained by ordinary V-style shading; no evidence for extra vertical layer.
- Four lossy variants are correlated, and quoted p-values are NOT familywise significance over the wider historical project. Do not treat visual hatching as cryptographic decoding or generate key candidates.
- Script: tools/stage136_sail_side_conditioned_null.py; outputs analysis/runs/stage136-side-conditioned-sail-null/.


## 2026-10-13 — Stage136 side-conditioned VALID NEGATIVE, Stage137 registered

- Stage136 GitHub Actions #38491300004 completed successfully; canonical SHA and exact Stage135 aggregate reproduction passed, synthetic natural-V/vertical-reversal/balanced controls passed, source coverage 4/4. After conditioning on left/right side, **0/4** image renderings showed additional top/bottom sign differences; exact conditional p were 0.758, 0.630, 1.000, 0.271. Stage135's striking global pattern is consistent with ordinary opposing hatch angles on the left and right triangular sail surfaces. Do not treat Stage135's unconditioned p-values as support for hidden code. Retire only the proposed *extra upper/lower structure*.
- Stage137 now targets a separate, newly source-accessible visual cue: direct full LARGE HULL ↔ its LOWER WATER WAKE mirrored ink/edge pattern. Stage132 proved the earlier shared "large_sailboat" box entirely missed the hull. Stages35 and 47–54 addressed skyline/building-water reflection elsewhere, not this full large hull/wake. This is a calibrated IMAGE-only direct reflection question, not encoded-bit search.
- Fixed source apertures: x=15..535; hull y=818..938 and wake y=942..1062, 520×120 each. Compare vertical-flipped hull ink and blurred Canny edges against wake over source/JPEG85/JPEG70/resampled. Fixed null lateral shifts ±80/130px. Gate: hull ink >=8%, wake >=4%; mirrored ink correlation >=0.73, mirrored edge >=0.57, each >=0.19 above shifted-reference max, replicated across four renderings.
- Controls: 130 synthetic strokes with exact vertical mirror positive, independently generated water-strokes negative; negative must remain ink/edge corr <=0.42 and not pass mirror gate. Control failure => repair Stage137 SAME number; real source low coverage => inconclusive, otherwise only fixed-template reflection claim closed or flagged for manual review.
- No Twitter, wallet, private key, mnemonic, BIP39 or other secret operation.
- Script: tools/stage137_large_hull_wake_reflection.py; artifacts: analysis/runs/stage137-large-hull-wake-reflection/.


## 2026-10-13 — Stage137 closed; Stage138 source-corrected re-audit preregistered

Stage137 Actions #38492279979 completed successfully. Canonical SHA matched, positive reflected vs independent-wake controls 8/8 passed, real hull+lower-wake both covered all 4 JPEG/source variants. Actual large-hull/wake mirror correlations: ink 0.023..0.039 and edge 0.226..0.234; all worse than shifted-water controls; verdict NO_EXACT_LARGE_HULL_WAKE_MIRROR. Retire only those matched fixed windows and two exact mirrored texture metrics.

**One defect-justified new test: Stage138** revisits old Stage35's direct H/V building-facade versus underlying water-reflection orientation. Stage35 excluded first two buildings *because the incorrect large-sailboat bbox* allegedly overlapped their water y330..360; Stage132 instead verified the actual large sail begins y398, outside that reflection band. This is a demonstrable OBJECT GEOMETRY/REGION ASSOCIATION defect, not recycling an exhausted experiment.

- Same Stage35 building x ranges, inner 10% margin, y330..360, Sobel/Fourier orientation estimators and original H/V labels HHVVHHVHHHHV; now all 12 buildings, four V, exact C(12,4)=495 permutations. 4 source/JPEG85/JPEG70/resample variants.
- Independent controls: the original Stage35 ten crop measurements must reproduce within 1e-6; synthetic V-vertical/H-horizontal positive reflections and inverted negative orientations for all four variants; old excluded-source overlap invalid because real sail begins y398. All calibrations must pass before interpreting image.
- Added buildings 1 and 2 must each show mean darkness >=2.0 in the fixed reflection aperture across all formats; otherwise INCONCLUSIVE coverage rather than negative.
- Promotion needs **both** original Stage35 methods V-minus-H positive and one-sided exact p<=.025 each (two-test Bonferroni), surviving all four lossy/original variants. No retuning to get a positive.
- Never derive keys, mnemonic words, account access or external Twitter content. Source canonical image only.
- Script tools/stage138_corrected_all_building_reflections.py, outputs analysis/runs/stage138-all-building-reflection-recheck/.


## 2026-10-13 — Stage138 calibrated negative; Stage139 quality audit preregistered

- Stage138 Actions #38492878610 completed SUCCESS and canonical SHA matched. Reproduced the original Stage35 data at all ten legacy retained sites with exact zero numerical drift; synthetic V-vertical/H-horizontal and inverted negative passed on 4 variants. Newly restored buildings #1 and #2 both show strong water-band ink. Full 12-building result: Sobel V-minus-H is NEGATIVE -0.032..-0.023 (p=.556..582); Fourier V-minus-H +.085..+.113 but p=.327..370. NO_REPLICATED_ALL_12_REFLECTION_ASSOCIATION. Do not treat this as general failure of visible H/V facade sequence.
- A NEW SOURCE-COVERAGE defect is apparent in the Stage138 original rows: building #6 water-band brightness darkness=0.400 and #11 darkness=0.832, well below the **2.0 mean darkness** already predeclared for #1 and #2 in Stage138. Stage138 never required source adequacy across its original ten sites, so near-empty patches contributed meaningless Sobel/Fourier orientations.
- Stage139 is exactly one non-arbitrary re-audit: reproduce Stage138 measurements verbatim, apply the SAME fixed 2.0 darkness minimum uniformly across all 12 building-water apertures in original/JPEG85/JPEG70/resampled, precommit per-class and total coverage >=8 good / >=3 V / >=4 H, and require stable excluded IDs. Then retain the same Stage35/138 two-method exact V-vs-H permutation gate (each one-sided p<=.025), without retuning.
- Calibrations: exact Stage138 original 12-row replay <=1e-7, synthetic V/H positive plus H/V inversion negative with Stage138-observed near-empty #6/#11 artificially blanked in source, all 4 variants; require exactly those two exclusions and 4 V/6 H synthetic. Control failure => repair Stage139. Real source low coverage => inconclusive; positive => independent adversarial review, not code. Any p is exploratory because this check was initiated after Stage138 diagnostics; no claims of fresh independent confirmation.
- Strictly image-only; no BIP39, mnemonic, key, wallet or Twitter.
- Script tools/stage139_reflection_coverage_audit.py; artifacts analysis/runs/stage139-reflection-coverage-audit/.


## 2026-10-13 — Stage139 final; Stage140 preregistered

- Stage139 GitHub Actions #38494403165 succeeded, 100% identical Stage138 12-site measurements and positive V/H + reversed negative controls passed all four formats. Uniformly applied the already-fixed darkness>=2.0 across all twelve reflection apertures; only nearly empty buildings #6 and #11 excluded in every format. Remaining 10 include 4 V/6 H. Both original Stage35 orientation tests remain NON-significant (Sobel exact p .20–.2095, Fourier p .3286–.3524). Verdict NO_COVERAGE_GATED_REFLECTION_RELATION. Retire this narrow direct facade/reflection coupling, not H/V visual geometry.
- **Exactly one new, non-recycled test:** Stage140 examines whether interior pencil strokes in the *large actual sail* (Stage132 corrected triangle) were copied and resized into any of the five small true sail triangles. Stage120 tested reuse AMONG the five small sails only; Stage123 searched cross-region equal-scale 64px patches, not giant-to-small affine normalization.
- All six triangle apex/feet are fixed in tools/stage140_cross_scale_sail_motif.py. Affine normalize into 128×128, compare only the inner two side panels y=.26..79 and |x|=.17..76 in two descriptors (low-frequency ink correlation >=.65 AND high-pass pencil-detail correlation >=.28, separately for both sides). Four original/JPEG85/JPEG70/75%-resample source renderings; zero free search over rotation, crop, alignment, or thresholds.
- 20 synthetic exact cross-scale copied sail positives and 20 same-silhouette independent redraw negatives, with fixed source density >=.10 at all sites. Controls must pass 20/20 both families. Any control failure => repair Stage140 before interpreting; if any real region source coverage insufficient => INCONCLUSIVE. Real promotion only for a full template fingerprint passing both sectors and all four image variants. Neither copied templates nor negative outcomes constitute a private key.
- Image-only. No wallet, BIP39, key, public-address checks or Twitter.
- Script: tools/stage140_cross_scale_sail_motif.py. Results: analysis/runs/stage140-cross-scale-sail-motif/.


## 2026-10-13 — Stage140 reviewed, Stage141 preregistered

- Stage140 Actions #38495397342 completed SUCCESS with original-image SHA check; 20/20 copied and 20/20 independently redrawn synthetic affine-rescaled sail controls passed, all 5 real small-sail interiors adequately sampled. None of the five reproduced both-panel complete-large-sail stroke texture under original/JPEG85/JPEG70/down75_up with fixed normalized geometry (0/5); verdict NO_LARGE_TO_SMALL_STROKE_TEMPLATE_COPY. This retires only exact affine normalized copied pen-stroke fingerprints, not other sail meanings.
- Stage141 tests a DIFFERENT, newly accessible source region: bilateral *pencil stroke fingerprint* inside the actual large **hull**, whereas historical Stage40's boat x-symmetry audit was over the old incorrect large-sailboat ROI that Stage132 proved omitted 100% of hull pixels. This is a concrete source-ROI defect, not revisiting old validated hypotheses.
- Same immutable Stage132 hull quadrilateral [(25,783),(525,778),(480,931),(75,939)] with eroded mask; center x=275 chosen from visible geometric hull center BEFORE comparisons, horizontal offsets 12..180; fixed bands upper y803..855, lower y859..921. Compare each x-mirrored left/right source band on smooth ink (correlation >=0.72) AND high-pass pencil details (>=0.56), requiring >=550 matched interior pixels and ink density >=.075 on both sides; four source/JPEG85/JPEG70/resample variants. No fitting axis/translation to source outcomes.
- Synthetic copied-mirror positive and independent pen-redraw same-shaped negative across each of two bands and four image variants, 16 checks total; both control families must PASS before interpreting original. Source failure => INCONCLUSIVE, positive requires all bands × formats and independent visual review, negative retires only exact mirrored hull-pen texture, NOT natural hull-shape symmetry.
- No private key, BIP39, seed word, address, wallet, Twitter or other off-image investigation.
- Script: tools/stage141_corrected_hull_bilateral_strokes.py; output analysis/runs/stage141-corrected-hull-bilateral-strokes/.


## 2026-10-13 — Stage141 validated; Stage142 preregistered (image only)

- Stage141 GitHub Actions #38495806304 completed SUCCESS with canonical SHA, full source coverage and 16/16 synthetic exact mirror versus redraw controls passing. Original hull upper band interior pencil correlations L/R: smooth ink -0.060 and detail -0.036, lower band smooth +0.333 and detail +0.017, with all four variants similarly weak. Decision NO_EXACT_MIRRORED_HULL_STROKE_FINGERPRINT. This retires only exact horizontal-axis copied pen texture in corrected hull, not approximate shape symbolism.
- Stage142 tests the OTHER genuinely unmeasured symmetry direction in the corrected hull: original Stage41 sought top-vs-bottom large-boat symmetry but relied on the old ROI that Stage132 proved contained 0 actual hull pixels; Stage141 only checked L/R. Now test UPPER ↔ LOWER pencil stroke copying around predetermined y=860.5, NOT reusing Stage141 x-reflection and NOT interpreting any digits.
- Immutable Stage132 hull polygon and 7px erosion, two fore/aft windows x95..235 and x315..455; fixed upper y798..847 and lower y875..924, no optimization over axes, formats original/JPEG85/JPEG70/down75_up.
- Two independent scores for BOTH windows: low-frequency reflected-ink correlation >=.72 and high-pass reflected pencil details >=.56; >=1200 paired mask pixels and ink density >=.075 in both surfaces. Positives are synthetic exact upper-to-lower pixel mirror, negatives are independently sketched lower strokes, 4 formats x 2 windows x 2 families =16 cases. ALL 16 controls must pass; otherwise repair SAME Stage142. Real low coverage => inconclusive; replica in all formats => only manual visual review, not decoded code.
- Remain image-only: no BIP39, private keys, wallet access or off-image research.
- Script tools/stage142_corrected_hull_vertical_mirror.py; reports analysis/runs/stage142-true-hull-vertical-mirror/.


## 2026-10-13 — Stage142 completed; Stage143 preregistered on user chess observation

- Stage142 GitHub run #38496317157 succeeded. Canonical hash and full corrected hull source coverage passed, 4/4 synthetic positive and 4/4 independent-redraw negative over 2 fore/aft strips passed. Real vertical top↔bottom hull fingerprint comparison: original fore ink corr 0.155/detail 0.0095; aft ink 0.251/detail 0.0054, invariantly low over 4 formats. Decision NO_UPPER_LOWER_HULL_PENCIL_TEMPLATE_MIRROR. Retires exact registered upper/lower hull-pen copying only.
- The user supplied a rotated+duplicated mirrored canonical-image montage and personally outlined **two white voids**; perceived upper as king and lower as queen. These screenshots are transformed user-selected views, NOT independent source image marks. Avoid claiming an actual chess code merely because human-drawn tracing emphasizes a symmetrical silhouette.
- **Stage143** is the sole new image-only investigation: reconstruct source 90°-rotation plus bilateral mirror and the building ROOFLINE-only silhouette from canonical PNG and the already registered 12 building roofs/positions (not invented puzzle digits). Test whether 2 distinct x-mirrored generic pedestal profiles arise from the original 2 skyline clusters: right x884–1592 (7 buildings) maps to the upper profile, left x234–782 (5 buildings) to the lower profile.
- Precommitted source control: each roof has an independently confirmed line within ±25px of its recorded y, with >=11/12 adequate across each of four lossy formats; artificial source mirror must have pixel equality 1.0 by construction. Positive synthetic stepped profile with base/head >=1.30 and >=3 unique tiers, negative flat-roof rectangle must NOT pass.
- Conditional exact **descriptive** null: permute rooftop heights among existing building-width positions within each cluster; count frequency that both paired source gaps are generic stepped flared pedestals (base/head >=1.30). This is NOT a king or queen classifier and is post-hoc after seeing user-selected montage; do NOT treat its permutation frequency as familywise support for intent. Generate original mirrored image, roofline-only geometric paired contours and six fixed seeded null image pairs for adversarial visual review.
- Critical chess specificity: a true king normally has an unambiguous cross finial, queen a multi-pointed crown; neither can be asserted from a manually traced pair of skyline-based negative voids without independent visible crown evidence in original.
- No BIP39/key/secret/wallet operations or Twitter/off-image investigation. Script tools/stage143_mirrored_skyline_chess_shapes.py; results analysis/runs/stage143-mirrored-skyline-chess/.


## 2026-10-13 — Stage143 user-supplied chess silhouette investigation completed

Stage143 GitHub Action #38498657551 completed successfully. Canonical SHA verified, roof-line sources 12/12 buildings in all 4 source/lossy formats, synthetic stepped-pedestal versus flat-rectangle controls PASS. The reconstructed 90° source rotation and two mirror-facing copies visually reproduce the user's two white outlines (excluding their manual red tracing). The bilateral symmetry is ARTIFICIALLY FORCED by reflection, rather than two independently drawn symbols.

Top void follows 7 right-city building roof heights (IDs 12–6); lower void follows 5 left-city building roof heights (IDs 5–1). Their mirrored roofline gap widths widen base/head by 2.716× and 8.05×. An exact within-cluster endpoint permutation null gives 17.14286% occurrence of merely GENERIC pairs of widening pedestal profiles using the fixed 1.30× ratio criterion. This is a POST-HOC illustrative null, not a calibrated chess-classification p-value or chance of author intent.

Verdict MIRROR_GENERATES_GENERIC_PIECE_LIKE_NEGATIVE_SPACE. No unambiguously identifiable king cross finial or queen multi-pointed crown independently documented in the original canonical picture. Do NOT infer coded king/queen identities or force a connection with H/V 321 absent independent, source-visible distinguishing features. Investigation is archived pending the user's further rotations; do not initiate more speculative image transformations without a new observed difference.

Source file tools/stage143_mirrored_skyline_chess_shapes.py; artifacts analysis/runs/stage143-mirrored-skyline-chess/ include canonical-rotated-mirror-pair.png, geometry-only-stepped-voids.png, six-randomized-skyline-mirror-controls.png. No secret or off-image operations.


## 2026-10-13 — Stage143 reviewed; Stage144 new user-observed vertical spire preregistered

- Stage143 GitHub run #38498657551 completed SUCCESS, original SHA, roof-source confirmations 12/12 in 4 formats, reflected-pair symmetry 1.0 by construction, synthetic stepped-vs-flat profiles PASS. The upper/lower chess-piece-like central WHITE voids were reproduced from 7/5 city buildings facing their roofs; the 17.14% generic flared-pedestal null is post-hoc descriptive and does not establish king/queen identities. Closed pending new visible unique source clues.
- User subsequently supplied a SECOND distinct configuration: when mirroring the skyline the opposite way, building facades appear as stacked horizontal blocks around one long, narrow central BLACK pointed 'spire' or tower silhouette. The canonical city skyline has a dark horizontal waterfront baseline, which 90-degree rotation turns into a vertical line. New question: is the apparent spire just that real HORIZONTAL source line, rather than an independently encoded tower/needle?
- Stage144 precommitted: no unknown crop optimization. Source x180..1595 and y225..292, 12 equal x-blocks. Detect source horizontal runs using 35-px morphological opening at grayscale<175, select highest-supported row with fixed ±3px search. Require >=9/12 x-blocks and ablating ONLY those detected horizontal-ink pixels in that row to remove >=6 blocks; require chosen source y stable ±3 across canonical, JPEG85, JPEG70 and 75%-resample.
- Synthetic controls: an independently hatching skyline PLUS long thin horizontal waterfront line must pass all four formats; the same independent building hatches WITHOUT a long shared waterfront line must remain <=4 covered blocks and not trigger. If controls fail, repair SAME Stage144; no weak-source positive or uncalibrated inference. Save 2 human-inspectable contacts: source horizon-location markup, roof-facing vs BASE-facing rotated/mirrored skyline before/after source-line ablation. This is a representative montage, not claimed pixel-exact reconstruction of the user's unknown crop.
- A positive would only establish ordinary source-line provenance for the new vertical spear. It is not a chess, steganographic or mathematical symbol and not proof of author intention. No keys, BIP39, wallet activity or off-image sources.
- Tool: tools/stage144_rotated_skyline_spire.py, results analysis/runs/stage144-rotated-skyline-spire/.


## 2026-10-13 — Stage144 repaired, Stage145 precommitted

- Stage144 initial run #38500113800 was INVALID: positive artificial native horizontal line was found in all 12/12 x-bins but clipping only the top ±3px band left the lower anti-aliased rows, so all four positives erroneously survived ablation. Repaired SAME Stage144 without changing x/y source aperture, 35px morphological opening, gray threshold 175 or source acceptance gates. Instead erase each COMPLETE already-detected connected long-horizontal stroke component touching the same ±3px seed row. Run #38500725098 passed 4/4 synthetic horizon positives (12→0 x-bins) and 4/4 independent facade-only negatives (0 x-bins). Canonical hash unchanged. Real source y258–260 long horizontal marks robustly cover 11–12/12 x-bins, but after removing one selected stroke 8/12 x-bins remain. Source does not satisfy predeclared ≥6-bin-drop in 4 formats (real drop 3–4 bins). Decision SPIRE_SOURCE_HORIZON_NOT_CONFIRMED: single source line cannot explain the entire mirrored apparent vertical spike under tested method. This is NOT evidence of an intentional tower.
- Stage145 tests exactly the reported new limitation: are there TWO OR MORE separate vertically spaced NATIVE horizontal shoreline pen bands, rather than one, generating the visual black spine when rotated and reflected? It keeps Stage144 immutable x180..1595, y225..292, original 35px filter and 12 x-bins, original/JPEG85/JPEG70/down75_up. Compute row support with same original ±3px and group rows with 0–2 missing y-rows. Require at least two bands EACH covering ≥6/12 x-bins, centers separated ≥15px, and ≥6 x-bins of long ink remaining after Stage144's single-component ablation. No y/threshold/rotation fitting to the original outcome.
- Three independent source controls ×4 renderings = 12: two parallel long source lines at fixed y239/281, one single source line y260, and facade-only source with no long shared line. Two-line control must classify multi; both other controls must not. Exact reproduction of archived Stage144 4× source measurements required. Any control failure => repair Stage145. Positive identifies ordinary source multiple native horizontal marks, not chess, tower, 321 or hidden code. Output contact compares rotated mirror before removal, after Stage144 single-line removal and after **all detected** long native horizontal source marks removed.
- Absolutely no key, BIP39, wallet, outside-site or social research.
- Source: tools/stage145_skyline_multiple_lines.py; reports: analysis/runs/stage145-skyline-multi-horizontal/.


## 2026-10-13 — Stage145 audited; Stage146 registered for downsampling merge

- Stage145 Actions #38501094776 finished SUCCESS, canonical source SHA, 12/12 synthetic multiple-line vs single-line vs no-line controls and exact replay of fixed Stage144 4-format measurements all PASS. Native original, JPEG85 and JPEG70 have TWO connected y source-line groups centered y237 and y257–258, each with ≥6 of 12 skyline x-bins long horizontal lines. After 75% down/up resampling these two groups MERGE into one morphological component y232..268 (center y250), although source after single selected component ablation still retains 8/12 x-bins. Decision NO_REPLICATED_MULTIPLE_HORIZONTAL_RULES under strict across-format separate-component rule. Do not misinterpret the failure as absence of any horizontal strokes; it is a topology/source-transform limitation of this exact detector.
- Stage146 is the single next experiment *repairing that observed connected-component merge*, not retuning Stage145 thresholds. Predeclare two fixed, nonoverlapping native source y windows directly from already observed Stage145 first three source renderings: UPPER y232..242 and LOWER y252..267, keep same Stage144 original x180..1595, 35px morphological horizontal opening, dark threshold 175, twelve x-bins, same ±3px Stage144 single-component removal. Ask whether the two fixed windows each retain ≥6/12 source long-hatch x-bin support AND at least one window retains ≥6/12 after one other stroke is removed, across all four image source/lossy variants.
- Synthetic 4 fixtures x 4 variants=16 calibrations: two native horizontals y237 and y260 positive; single line at y237 only, y260 only, and no line negatives. Controls must distinguish all 16. Exact Stage145 source diagnostics must reproduce or no inference. No new axis, ROI fitting, score threshold relaxation or hidden-image guesses. A positive only establishes two robust preexisting drawing band signatures explaining artificial vertical montage structure, not author-intent/chess/steganography.
- Strictly canonical-image only, no keys, BIP39, mnemonic, wallet/address or external research.
- Script tools/stage146_fixed_skyline_bands.py, artifact analysis/runs/stage146-fixed-skyline-bands/.


## 2026-10-13 — Stage146 valid positive source observation; Stage147 independent measurement

- Stage146 GitHub run #38501412862 succeeded. Canonical source hash, 16/16 two-line/upper-only/lower-only/no-line synthetic controls and exact replay of Stage145 image metrics PASS. Unlike Stage145's fragile connected-component grouping, two *pre-fixed source y windows* y232..242 and y252..267 both have long horizontal native ink in EVERY original/JPEG85/JPEG70/downsample rendering. Upper 8/8/8/7 of 12 x-bins, lower 11/12/12/11; after deleting one selected native horizontal component at least 8/8/8/7 blocks of another native source band remain. Decision FIXED_NATIVE_SKYLINE_BANDS_REPRODUCIBLE. This is image-geometry provenance, not a recovered symbol/word/key: windows were selected after native-image Stage145 results and are not independent evidence of author intent.
- Stage147 now tests the one remaining measurement uncertainty *independently of Stage144/146 morphology*: in the identical Stage146 registered two source apertures and 12 x-bins, check whether Sobel horizontal edge-energy anisotropy AND Canny/Hough line segments also distinguish both source bands from single-upper, single-lower, none synthetic controls. Require >=6/12 supported x-bins per detector per band under each of original/JPEG85/JPEG70/down75_up. Fixed source coordinates, no threshold tuning on original. Independently re-run Stage146 per-format raw source measurements exactly to prevent dataset/provenance drift. Controls must succeed 16/16 cases or repair Stage147. Real positive only confirms natural, visible skyline horizontal drawing structure, never chess, tower glyph, data bits or secret material.
- Source tools/stage147_skyline_independent_orientation.py, results analysis/runs/stage147-independent-skyline-line-detectors/. User requested only brief stage updates; no further off-image speculation.


## 2026-10-13 — Stage147 independent source line confirmation; Stage148 new original-image clue control

Stage147 GitHub run #38501723077 completed SUCCESS. 16/16 artificial two-band/single-band/no-line source controls PASS; exact replay of Stage146 source values PASS, SHA matches. Two *independent* detectors that did not use Stage144/146 morphology each find BOTH native source-line bands in ALL four original/JPEG85/JPEG70/resampled copies: upper fixed y232..242 Sobel 7/12 and Hough 11/12 x-bins, lower y252..267 Sobel 10/12 and Hough 12/12 in every source version. Decision TWO_HORIZONTAL_SOURCE_BANDS_CONFIRMED_INDEPENDENTLY. This establishes ordinary source pencil-line geometry in the user's artificially mirrored/rotated vertical 'spire' but NOT author-intended chess/tower coding. Skyline-spire source provenance branch now closed absent an independently new unique feature.
- **One new visual issue of higher value:** The ORIGINAL, unmirrored H/V fill sequence of 12 buildings `HHVVHHVHHHHV` / `001100100001` / `0x321` is demonstrably stable (Stage10/31), but might reflect ordinary illustrator habit: tall, wide, slender or large buildings get horizontal vs vertical strokes. This *shape-H/V relationship* was not the Stage63–70 building width/aspect ALTERNATION/TREND tests, and was not evaluated in Stage10 robustness. Stage148 tests **whether the H/V labels depend on basic facade geometry** (width, height, aspect ratio, area) rather than encoded instruction, using only canonical image and already measured building boxes.
- Precommitted exactly 4 shape predictors, 12 buildings with 4 V, 495 exact conditional permutations. Compare mean V minus mean H with a two-sided standardized max-test across 4 predictors (familywise p<=.05), not post-hoc 321 discovery. Source SHA, Stage10 `baseline_sequence` / hex 321 verified; independently recompute Stage10 fixed-inner-box Sobel orientations and Stage143 roofline source-pixel confirmations in all four image formats. Synthetic positive: much wider V facades; synthetic positive: much taller V facades; negative: equal shapes regardless H/V. Control failure => repair Stage148, no real conclusion; source non-reproduction => inconclusive. Significant association is an ordinary shape-art confound, and NON-significant association does NOT prove an intentional code.
- Never derive keys, mnemonic/BIP39 phrases, wallets, addresses or off-image information. Script tools/stage148_hv_building_aspect_confounds.py, artifacts analysis/runs/stage148-hv-building-shape-confound/.


## 2026-10-14 — Stage148 complete, Stage149 independent facade-height consistency preregistered

- Stage148 run #38502142003 completed SUCCESS, verified SHA256 and four-format 12/12 source H/V markers HHVVHHVHHHHV, 12/12 source roof checks. Synthetic wide-V/tall-V permutation positives p=0.0020202 and equal-shape null p=1 PASS. Four mundane building geometric predictors (width, height, aspect, area) did **not** explain V versus H under 495 exact four-V label assignments and joint max-standardized-test adjustment (FWER two-sided p=0.2989899; individual p=0.1273/.5980/.5374/.1798). This leaves the visual 321 mapping as a *possibility* not evidence of author intent.
- Stage149 is one new IMAGE-ONLY source falsification, not another re-encoding or key experiment: check whether H/V facade orientation is a whole-building homogeneous drawing property or a pixel-average hiding mixed TOP/MIDDLE/BOTTOM hatches. Stage10 tested whole-facade margin/jitter, Stage121 exact integer line counts, Stage148 width/height predictor; none classified 3 independently segmented tiers per building.
- Precommit 12 original facades ×3 disjoint inner-y strips (building original roof/bottom after 14% top margin/10% bottom, each band trimmed ±3px; x margin 12%), 4 source/JPEG85/JPEG70/75%-resampled variants, two independent measures of predominant H/V orientation: Sobel ex-ey signed score, and oriented ±4px shifted grayscale autocorrelation. Both must agree, with min ink density 0.065 and fixed Sobel±0.14 / correlation±0.10 gates.
- Calibration BEFORE source interpretation: four synthetic regimes (all H; all V; three-tier H/V/H mixed; entirely blank) drawn inside the 12×3 registered regions, ×4 variants, full **576 independently scored** H/V/blank cases. ALL must pass, or repair SAME Stage149. Reproduce Stage148's whole original sequence on all source/format variants. Real >=30/36 fully replicated three-tier labels required; mixed-layer lead iff >=4 facades show >=2 stably opposing H/V tiers; homogeneity lead iff >=10 buildings each have all three tiers stably equal to whole source H/V; otherwise inconclusive/partially mixed. Never decode key/word or assume H0/V1 321 intentional.
- Source: tools/stage149_hv_within_facade_layers.py. Outputs analysis/runs/stage149-hv-facade-layers/.


## 2026-10-14 — Stage149 three facade heights measured, Stage150 targeted source-jitter audit preregistered

Stage149 GitHub workflow #38576395527 completed successfully. Original SHA and 12-building H/V labels match Stage148 across 4 original/lossy formats. **All 576/576** synthetic horizontal, vertical, H/V/H layered and empty-facade controls passed. Real source subfacade labels stably classified 35/36; 9/12 facades have all three tiers identical to overall source H/V. Notably original V-labelled facades #3,#4,#7 have LOWER H tiers, while source V-labelled facade #12 remains V throughout; #3's middle tier is ambiguous. This did NOT meet the precommitted mixed building threshold of four, so decision FACADES_PARTIALLY_MIXED_OR_SOURCE_AMBIGUOUS. This is evidence of more layered painting than whole-facade binary view, not proof of encoded bits.
Stage150 is a focused, image-only replication of the newly observed lower-tier split: test exactly the 4 V-labelled facades #3/#4/#7/#12 with Stage149's unchanged independent Sobel+4px-ink-lag estimators on UPPER and LOWER fixed interiors, 3×3 grid of x offsets {-4,0,+4} and y offsets {-3,0,+3}, 4 source/JPEG formats =36 crops per band per facade. Require >=31/36 predicted UPPER V on all four, >=31/36 LOWER H on #3/#4/#7 and >=31/36 LOWER V on #12. Do not promote arbitrary crop recalibration.
Positive synthetic V/V/H painting (lower H) vs two negatives V/V/V and V/V/V with external horizontal baseline adjacent but outside tested crop; all four geometries ×2 bands ×36 jitter-format combinations. Synthetic fixtures must pass per-facade >=31/36 correct, false basal H in full-V <=5/36 before interpreting source. Archive original Stage149 result integrity. A positive would establish a locally robust mixed painting detail, NOT automatically intentional 321 coding. Failed controls => repair SAME Stage150, no Stage151.
Tools: tools/stage150_v_facade_lower_h_perturb.py; artifacts analysis/runs/stage150-v-base-layer-perturb/. No secret derivation, BIP39, wallet, address or external research.


## 2026-10-14 — Stage150 crop-sensitivity result; Stage151 new under-pier visual object registered

- Stage150 Action run #38577281719 completed successfully, canonical original and Stage149 aggregate reproduced exactly; all synthetic V/V/H, V/V/V, exterior-H controls passed 3/3 regimes × four known V building geometries on fixed 3x3 jitter grid. UPPER H/V on all four V buildings remains V 36/36 each. Basal #3 is H 36/36, but #4/#7 only H 24/36 (12 ambiguous each), and #12 only V 24/36 (12 ambiguous). None showed an opposite stable basal sign under jitter. The preregistered >=31/36 per-building gate fails, decision V_BUILDING_BASAL_HATCH_CHANGE_NOT_REPLICATED_UNDER_JITTER. Thus do not claim a novel stable split-bit sequence or automatic 321 confirmation; Stage149 facades retain local drawing boundary sensitivity.
- **Stage151 is an independently observable source-image object** not previously among the six recognized sail masks: an open triangular region under the right-hand pier/jetty around (1052,633),(1052,778),(1280,714). This might be an additional hatched sail, an inverted sail or simply dock rigging. Prior Stage120 compared five true small sails with each other; Stage140 compared the large sail against those same five. No experiment compared this one source region against the known five.
- Precommit one triangle per object (five known small sails plus the single under-pier candidate) with fixed apex/base vertices from source; all affinely normalized to 128x128, a shared eroded interior mask excluding mast/outer lines, original/JPEG85/JPEG70/75%-resample. Compare only density of source dark pencil pixels >=0.18 AND highpass pencil detail >=0.030; no source ROI or threshold search. Positive synthetic dense triangular sail vs negative synthetic hollow outlined triangle at all six sites ×4 formats = 48 calibrations. ALL controls must pass, and at least 4/5 genuine source sails must pass across all four variants, before interpreting candidate. A source target positive merits only human picture review, not a sixth ship or key; a negative excludes only this fixed densely hatched panel reading.
- Tools: tools/stage151_under_pier_triangle.py, artifacts analysis/runs/stage151-under-pier-triangle/ plus contact sheet. No secrets, wallets, key generation or off-image research.


## 2026-10-14 — Stage151 calibrated unfilled under-pier region, Stage152 perimeter audit registered

- Stage151 Actions #38578665223 completed SUCCESS; canonical SHA and **48/48** known hatched-vs-empty outlined triangular synthetic controls passed. Source texture of 5/5 true sails passes in 4/4 images, density .764–.846 and high-frequency detail .129–.167. A visually nominated under-right-pier triangular aperture at source vertices (1052,633),(1052,778),(1280,714) has dark interior density .154/detail .082; fails fixed dense-sail criterion on source/JPEG/resample. Decision NO_HATCHED_SIXTH_SAIL_UNDER_PIER. This excludes only a normal filled sail in that one chosen region, NOT every drawn geometric meaning.
- Stage152 asks one independently measurable OUTLINE-only question not tested by Stage151 interior density: does that under-pier triangle have three physically inked sides like five positively localized true sail triangles, or merely an unclosed dock rope/brace crossing? Same six vertex sets, affine normalization, 45 fixed local edge samples per side, ±4px detection aperture, grayscale<185, per-side support ≥.58, source/JPEG85/JPEG70/down75_up. No source ROI fit or threshold adjustments.
- Synthetic full three-side positive vs V-shaped missing-base negative vs isolated mast-only negative, all six triangle sites ×4 renderings = 72 calibration checks must pass. Require at least 4/5 known positive actual sail outlines stably detected in all 4 images before interpreting candidate. If control/source issue, repair SAME Stage152; real full outlined candidate merits visual review only, not extra vessel, crypto symbol or decoded key.
- Script tools/stage152_under_pier_triangle_outline.py, artifacts analysis/runs/stage152-under-pier-closed-outline/. No BIP39, mnemonic, private key, wallet, address or outside sources.

## 2026-10-14 — Stage153 source diagnostic complete, Stage154 outward continuation preregistered BEFORE test

- Stage153 originally ran #38614668825 and yielded 48/48 simulated controls, only 2/5 stable known-sail closed-three-corner recovery; decision INSUFFICIENT_KNOWN_SAIL_JUNCTION_RECOVERY. It must not be called a negative on candidate closure. Follow-on source-only diagnosis #38620890513 (SUCCESS) verified canonical PNG SHA and left the Stage153 classifier, 48/48 controls and 2/5 recovery unchanged. Four missed actual known-sail corners included three with median nominal-arm ink offset about 3–4 px; a fourth had two nominal arm contacts but distinct components. Two under-pier corners likewise failed. This documents idealized ray/hand-drawn source mismatch; it does NOT prove how to repair physical junction identification. Do not tune Stage153 to the target or call its triangle open.
- Stage154 is a genuinely separate image-only observable, not another closure/vertex sensitivity trial: a pier brace or rigging line may extend well BEYOND BOTH LOWER annotated corners of a triangular negative-space opening, unlike two bounded sloping sail sides. Test four outward rays per site (two incident edges × vertices #2/#3) at EXACT existing Stage153 polygons, six sites (five true sails and one under-pier), and four image variants. Only long-range EXTERIOR continuations, t=20..56 pixels outward at 2-pixel steps, are tested; do not include top apex where sail masts naturally extend. Fixed ray corridor ±4px cross-section, flank control corridors at ±12px, gray<185, at least 0.68 along-ray detection, ≥0.35 contrast over flank mean, at least 8 consecutive dark-supported samples. A site is "paired extension" only if at least one ray at EACH base corner passes and all four variants do so.
- Calibrate on white synthetic isolated triangle (negative), one outward slope (negative), crossing transverse bars (negative), flanking parallel-line distractors (negative), both exterior slopes extended (positive), both exterior base rays extended (positive); ×six source geometries ×four formats = 144 labelled fixtures, ALL must pass. Real-source interpretation additionally requires at least FOUR of the five known true sails to be negative for paired extension in all four variants. If not, INCONCLUSIVE, repair this SAME Stage154 only if a reproducible defect is found. If all gates pass and under-pier paired extension is positive: evidence of continuing drawing strokes compatible with dock structure, NOT semantic proof or message. If negative: only the exact four fixed outward rays at the fixed gate lack positive continuation; does not turn it into a sail or key.
- Script tools/stage154_under_pier_outward_continuations.py; report/json and source overview under analysis/runs/stage154-under-pier-outward-continuations/. Use original SHA only, no social/source archaeology, OCR, keys, BIP39, address checks or wallets. One workflow only. Do not adjust gates after reading target.
