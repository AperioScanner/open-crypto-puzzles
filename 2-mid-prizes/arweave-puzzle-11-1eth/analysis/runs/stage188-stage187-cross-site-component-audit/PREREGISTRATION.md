# A11-EXP-188 — preregistered audit of cross-site contamination in Stage187 component counts

Date: 2026-10-28 UTC. Repository: AperioScanner/open-crypto-puzzles, branch `research/arweave11-chatgpt`.

## Independent methodological defect and historical contrast

Stage187 correctly implemented its *literal* preregistered procedure: count connected foreground components within an unaltered Stage127 cropped ROI of a fully composited Stage185 synthetic scene. However, its REPORT/STATE interpret these ROI counts as though they were connected components *of the single nominated hull*. The five Stage127 crop rectangles are not object-isolated: fixed coordinates for neighboring sail sites intersect in x/y, and their synthetic hull strokes can enter a neighbor's crop. This creates a specific **object-attribution / measurement-contamination mismatch** in Stage187, distinct from Stage187's already-proven Stage185 per-layer vs composite QA mismatch.

Stage127's historical original-image analysis *already cautioned* that fixed hull crops intersect neighboring boats/pier. This is not a newly discovered original-image feature; the new point to test is whether Stage187's **source-blind synthetic 10/45 count** is numerically inflated/deflated by strokes from *other generated boats* that do not belong to its nominal target.

A pre-preregistration local exploratory reproduction of the exact original Stage185 renderer reproduced the published Stage187 full-scene component histograms and suggested 19/45 site ROIs contain foreground absent from the corresponding target-only render, and 5 sites marked as >=2 components in Stage187 have <2 components in a target-only render (10/45 full-ROI deficits vs approximately 15/45 object-isolated deficits). These are **post-hoc inspected legacy cases**, NOT held-out evidence; the numbers are provisional until independently replayed in GitHub Actions. The goal is reproducible QA/attribution, NOT new detector optimization or clue inference.

## Frozen protocol, controls, and scope (before Stage188 execution)

1. Reuse the original, unmodified `stage185_hull_curve_fragment_positive_audit.source_blind_scene` for 3 families (`curved`, `broken`, `curved_broken`) x 3 labels (`UP_RIGHT`, `LEVEL`, `DOWN_RIGHT`), each with exactly the same frozen Stage127 five sites. Total 9 scenes / 45 site observations. Use unchanged `stage127_hull_waterline_slope.crop` and unchanged `stage187_stage185_component_qa_audit.components` (gray<245, 8-connectivity). Do not modify prior generator/detector/script/workflows or stage outputs.

2. Create one **single-site-only** 1105x1600 white canvas per nominated site: draw **exactly** its Stage185 three sail outline lines, four hull strokes and frozen coordinates/curvature/fragmentation using the **existing imported** `stage185.a_stroke_points` and `stage185.draw_one_stroke`, with `SITES`, `SLOPES`, `OFFSETS` and thickness exactly as Stage185. No unrelated site is drawn on this site-only canvas.

3. For each of the 9 scenes: before interpretation, require that the pixelwise OR of the gray<245 foreground masks of the five single-site-only canvases **exactly equals** the gray<245 foreground mask of the original unchanged full `source_blind_scene` canvas. If any pixel disagrees, CONTROL_FAILURE: do not compare component counts. This guards the isolated renderer against geometric/line reconstruction drift without altering the original renderer. Confirm Stage187 archived **per-site** full-ROI component counts equal the freshly calculated full-scene counts on all 45 records (not just summary totals). Require all 45 names/classes/families to match.

4. For each site: report `full_components` from the full synthetic scene cropped by Stage127, `isolated_components` from the nominated site-only canvas with the identical crop, and `foreign_pixels` = number of foreground pixels in the full crop absent in the isolated crop. Compute old Stage187 flag discrepancy `full_components<2` and target-only discrepancy `isolated_components<2`. Define **cross-site false sufficiency** precisely as `full_components>=2 AND isolated_components<2 AND foreign_pixels>0`; record all 45 rows. No pre- or post-result choice of threshold, crop or neighborhood radius.

5. Fresh independent source-blind component-counter controls on a 41x65 patch under identical gray<245/connectivity8: blank gives 0; isolated one-line target gives 1; a second **unrelated, non-touching** neighboring line crossing the same ROI gives 2 (not falsely attributed to target); a neighboring line drawn completely outside a fixed patch does not change its 1 target component; joining the target and foreign line by a bridge yields 1. These fixtures validate expected attribution hazards. Any unexpected control result = CONTROL_FAILURE.

6. Provenance/archive guards: canonical original PNG byte SHA-256 is `c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1`, checked **by bytes only**; Stage186 archived QA18/18 and `STAGE186_HELDOUT_CALIBRATION_INADEQUATE`, Stage187 archived QA13/13, `mismatch_count=10`, and decision `STAGE185_COMPOSITE_COMPONENT_QA_MISMATCH_CONFIRMED`. Never read canonical PNG pixels. Reencoded variants and old Stage185/186 scientific decisions are not retested or tuned.

## Frozen decision and stop conditions

If any controls/archive/source-blind scene identity/row count checks fail -> `CONTROL_FAILURE`; stop, do not infer mismatch, repair only Stage188 without changing preregistered decision gates. Else if >=1 cross-site false-sufficiency row -> `STAGE187_CROSS_SITE_ATTRIBUTION_BIAS_CONFIRMED`; otherwise -> `STAGE187_CROSS_SITE_ATTRIBUTION_NO_CHANGE`. Report full vs isolated mismatch counts and site-level effects, including any cases of more/less than 2 components where numbers differ without changing the criterion.

All 45 legacy objects are **in-sample historical fixtures**. Passing this technical audit does not validate any puzzle-image code, direction, message, or prize; it does not correct or overwrite Stage187's literal ROI count (10/45) but qualifies whether that quantity can represent per-hull connected-component counts. A Stage188 result is not an independent scientific holdout. Stop after one Stage188 run and verified report. No post-hoc cutoff changes, no repeated Stages, no cryptographic keys, BIP39, mnemomics, wallets, public-address checks, OCR or external/social research.

## Deliverables

New `tools/stage188_stage187_cross_site_component_audit.py`; new `.github/workflows/arweave11-stage188-cross-site-component-audit.yml`; new `analysis/runs/stage188-stage187-cross-site-component-audit/REPORT.md` and `result.json` from GitHub Actions. All Stages1–187 remain untouched. Update state/queue only **after** verified Actions result.
