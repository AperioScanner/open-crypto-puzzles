# Stage186 preregistration — independent source-blind hull-slope calibration

Date: 2026-10-26. Repository branch: `research/arweave11-chatgpt`.

## Evidence and question

Stage185 GitHub Actions run 40104994829 completed successfully and its 44/44 integrity checks passed, but the **unchanged Stage127 Hough classifier** detected only 2/5 up, 0/5 level and 2/5 down on bowed+fragmented known-positive hull drawings. This is a specific, independently recorded **measurement sensitivity defect**, not evidence for a message. Stage127 original natural-scene result remains 0/5 stable and scientifically inconclusive; Stage184-R 256-stroke decoding is retired.

Can a **new, source-blind column-centroid robust slope estimator** recover *known* bowed and fragmented hull directions on previously unseen synthetic scenes without confusing lone unrelated lines for four hull strokes? No original puzzle pixel may be inspected, only SHA-256 provenance `c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1`.

## Frozen method before running any held-out case

Use the five immutable original Stage127 site tuples (name,cx,top,h,half). Put `by=top+h`. At each site, sample **only** x columns in [cx-26,cx+26], inclusive, and y rows [by-5,by+34], inclusive, of original full 1600x1105 canvas. For each **fixed** gray threshold 155 and 185 in each of the **four original Stage112 variants** (original/JPEG85/JPEG70/down75_up):
1. Retain dark pixels `gray < threshold`. Consider a column valid only if it has at least THREE separated contiguous vertical dark-pixel runs (four hull strokes were drawn), to reject single-line/dual-line decoys.
2. Compute that column's darkness-weighted y centroid using weight `(255-gray)/255` on its qualifying dark pixels.
3. Require at least 16 valid x columns whose overall x-span is >=32 pixels.
4. Take the median of ALL pairwise centroid slopes `(yj-yi)/(xj-xi)` for valid pairs with horizontal separation >=14 pixels. This is a deterministic robust median slope, with no fitted polynomial or tuning to any target.
5. Preserve the original Stage127 numeric sign gates: >=+0.12 DOWN_RIGHT, <=-0.12 UP_RIGHT, abs<=0.055 LEVEL; otherwise abstain.
6. A site receives a stable label only when ALL EIGHT threshold/format responses return the same non-null label. Report per-format support and slopes.

No image threshold, crop, minimum support, sign tolerance, or outcome gate may be altered after the frozen holdout data is evaluated. Never use old Stage185 scenarios for threshold selection: they are diagnostic only.

## Synthetic scenes and independent holdout

All scenes use a 1105x1600 white uint8 canvas; for each of five registered hull sites, draw the original Stage127 3-line triangular sail outline, then FOUR black antialiased 2px hull strokes at offsets [6,10,15,20], original Stage127 full left/right hull span `cx +/- (half+11)`, and known slopes -0.26/0/+0.26. For each x, base row is `by+offset+slope*(x-mid)+bow_amp*(2*(x-mid)/(right-left))**2`, rounded to nearest integer.

The **independent holdout** has exactly SIX scenes (30 labelled positive hull sites), one for each class UP/LEVEL/DOWN for each **new** fixed nuisance:
- A: bow amplitude 4px, *16 pixels ink / 7 pixels gap*, repeating from x=left with phase 3px.
- B: bow amplitude 8px, *12 pixels ink / 9 pixels gap*, repeating from x=left with phase 5px.
- The original Stage185 scene (bow6, 20 ink/8 gap) is NOT a holdout; reproduce its nine fixed scenes only after QA and report separately as diagnostics.

Negative decoys (15 sites total) on white source-blind canvases:
1. Five blank, no sail or hull pixels.
2. Original sail outlines with EXACTLY one unrelated 2px line in the hull band/site, slope +0.26, at y offset 10.
3. Same sail outlines with EXACTLY two unrelated 2px lines per site at y offsets 8 and 19, slopes +0.26 and -0.26. Decoy lines have the same original hull x endpoints. These are specifically NOT four-layer hulls.

In all cases use only original Stage112 image transforms, nothing from the original drawing's actual pixels.

## QA and precommitted statistical decision

Before treating output as a scientific result verify: original image SHA bytes match, Stage127 archival decision `INSUFFICIENT_HULL_ISOLATION`/0 stable and both original positives pass, Stage185 archival QA44/44 and decision `STAGE127_SOURCE_LIKE_POSITIVE_RECOVERY_INADEQUATE`, unchanged five tuples and four transform names, blank 0 dark pixels, every new known-positive site contains exactly 4 constructed hull layers with >=10 raster dark pixels EACH and all coordinates in-bounds, negative decoys have exactly 0/1/2 explicitly constructed lines, two holdout styles differ from Stage185 bow6/on20-off8, and full result serialization works. If these structural guards fail: **CONTROL_FAILURE**, repair only Stage186, do not interpret calibration.

Scientific pass requires **at least 4/5 correct stable site labels in EACH of the SIX independent positive scenes**, **zero confidently wrong labels among 30 positives**, and **at most 1 confidently classified negative among 15 decoy sites** (specificity >=14/15). If all QA succeeds but any of these fails: `STAGE186_HELDOUT_CALIBRATION_INADEQUATE`; if all pass: `STAGE186_HELDOUT_CALIBRATION_PRELIMINARILY_DISCRIMINATIVE`. Report exact per-family, per-class recovery, abstentions, false positive counts, as well as original Stage185 performance of the *new* estimator separately, with no claim of an independent source clue.

A successful detector would merely justify **a separately preregistered real-source retest** if independent image evidence also warrants one. No Stage187 in this run. A failure requires scientific pause or a genuinely new proven defect, not repeated post-result parameter fitting.

## Engineering & safety

One script `tools/stage186_hull_column_center_holdout.py`, one GitHub Actions workflow `.github/workflows/arweave11-stage186-hull-centroid-holdout.yml`; write generated `analysis/runs/stage186-hull-column-center-holdout/result.json` and `REPORT.md`. Preserve Stage127/185 and branch. No BIP39, private keys, wallet/address tests, social sources, OCR or off-image research.
