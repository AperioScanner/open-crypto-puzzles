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
