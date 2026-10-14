# ChatGPT research worklog

This file is the append-only coordination log for the `research/arweave11-chatgpt` branch.

## 2026-09-30 — initialization

- Fork verified: `AperioScanner/open-crypto-puzzles`.
- Write/admin access verified through the connected AperioScanner GitHub account.
- Dedicated branch created: `research/arweave11-chatgpt`.
- Existing puzzle documentation reviewed.
- Existing negative ledger reviewed before planning new work.
- Immediate next technical target: full-image continuous-channel bitstream search without duplicating the already-recorded first-row and ASCII/compression scans.

## 2026-10-01 — safe-scope continuation

- Active scope narrowed to public clues, visual semantics, steganography/image diagnostics, and statistical structure; no generation/derivation/verification of candidate private keys.
- Reviewed completed branch runs through stage 9 and the recovered 2020-04-23 author clues.
- Reviewed surviving solved-puzzle write-ups (#5, #7, #8) because the author explicitly told #11 solvers to look at solved puzzles.
- Added and ran A11-EXP-010 (`stage10_marker_robustness.py`) through GitHub Actions.
- Result: `HHVVHHVHHHHV = 0x321` survives all tested inner margins; exact full-sequence preservation is 100% through ±8 px jitter, 94.25% at ±12 px and 85% at ±16 px; mean per-building class stability under ±24 px shifts is 97.9%.
- Interpretation: `321` is now treated as a robust visual clue candidate, not as proof of intent. Next safe target is solved-puzzle grammar + non-key visual interpretation of 3-2-1.

## 2026-10-01 — stage 11 through stage 14

- **Stage 11 / A11-EXP-011:** reconstructed solved-puzzle design grammar from public #5/#7/#8 write-ups and the author archive. Catalogued 18 solved-token mechanisms; 14 are semantic/contextual and 4 are counting/sequence/numeric-extraction. Result materially favors human-readable semantic clues and secondary details over arbitrary pixel transforms.
- **Stage 12 / A11-EXP-012:** ran counting/perimeter/secondary-detail diagnostics across 16 image regions. Produced a diagnostic contact sheet. Common lag-3 projection periodicity occurs in several unrelated regions and is therefore treated as likely raster/stroke structure, not independent 321 evidence.
- **Stage 13 / A11-EXP-013:** quantified the 321 marker under exact null models. Exact 0x321 is 1/4096 under a uniform 12-bit null and 1/495 conditioned on four V buildings. This strengthens the lead but is not a formal discovery p-value because of look-elsewhere effects.
- **Stage 14 / A11-EXP-014:** reconstructed every mirrored @ArweaveP post/reply from 2020-04-20 through 2020-05-01. Seven deduplicated rows; no direct 3-2-1 pattern, no ordering/direction clue, and no geometry/object wording. The known public hints are confirmed, but 321 has no independent textual corroboration in this source.
- Next stage: seek an independent **visual** 3-2-1/countdown/order/selection structure, using the solved-puzzle grammar and rejecting unstable raster artifacts.


## 2026-10-03 — adaptive review of batch 22–27

- The fixed 22–27 multi-stage pipeline was recognized as the wrong orchestration model for this project. It completed successfully, but those stages are treated as one exploratory evidence batch, not as adaptive reasoning between stages.
- Removed the fixed multi-stage workflow so it cannot be reused.
- Stage 22 retained the robust H/V texture but retired the specific hexadecimal `0x321` interpretation as primary.
- Stage 24 weakened simple global LSB replacement: the original RS-style statistics are far from the stronger synthetic replacement controls.
- Stage 27 tested 768 traversal/bit-selection streams. The best printable fraction was only about 0.109 and the longest printable run was 8. The previous magic-signature count is not trustworthy because one-byte JSON markers (`{` and `[`) created many chance hits.
- Adaptive decision for Stage 28: null-calibrate Stage-27 traversal anomalies with matched spatial surrogate images and use only sufficiently specific multi-byte file signatures. This tests whether the apparent text/compressibility anomalies are actually exceptional before inventing a new carrier hypothesis.


## 2026-10-03 — adaptive review of stage 28

- Stage 28 completed successfully with 100 block-shuffled surrogate images.
- Stage-27 one-byte magic hits were eliminated from consideration; no specific multi-byte file signature remained.
- Two global traversal metrics survived null calibration: max printable fraction p=0.0099 and min zlib ratio p=0.0099. Longest printable run was not unusual (p=0.8416).
- Interpretation: this is not evidence of readable plaintext, but the promoted L-bit0 traversal family is statistically structured relative to matched surrogates and deserves localization.
- Adaptive decision: Stage 29 was designed only after reading Stage 28. It localizes the canonical traversal anomaly in fixed byte windows and compares the same traversal across grayscale bitplanes 0–7 to test LSB specificity versus ordinary image structure.
- The hourly controller was disabled while the user is actively steering the research; it can be re-enabled when requested.


## 2026-10-03 — adaptive review of stages 29–30

- Stage 29 localized the Stage-28 traversal anomaly and showed that the canonical effect is not unique to grayscale bit 0; similar structure persists through higher bitplanes.
- Stage 30 then decomposed the fixed source-x clusters by semantic y-band and foreground/background class. The apparent printability sits in drawn foreground pixels (~0.36–0.38 printable), while the extreme compressibility sits in blank background strips (zlib as low as ~0.012).
- The same source-cluster behavior persists across grayscale bits 0–3. This explains why the Stage-28 block-shuffled null looked significant: block shuffling destroyed the large-scale foreground/background layout.
- Adaptive conclusion: retire generic traversal-text/compressibility hunting as a primary carrier hypothesis. The earlier Stage-28 significance is retained as a useful null-model lesson, not as payload evidence.
- Hypothesis ranking changed: format-invariant visual/semantic structure is now highest priority; raw exact-pixel low-bit steganography is strongly downgraded; the robust H/V building texture is retained without reviving the post-hoc hexadecimal 0x321 reading.
- Adaptive decision: Stage 31 directly tests format invariance by comparing independent H/V classifiers against lossy JPEG/resampling variants while measuring exact low-bit destruction on the same transformed images.


## 2026-10-03 — adaptive review of Stage 31

- Stage 31 tested the competing route hypotheses directly under lossy format conversion and resampling.
- The visual H/V sequence remained **12/12 under both independent classifiers for every tested variant** (JPEG 95/85/70, down/up, up/down, and JPEG85+resampling).
- Exact foreground grayscale bit-0 agreement simultaneously fell to roughly **0.52–0.55**, near chance.
- Adaptive conclusion: format-invariant visual/semantic structure is now the primary research route; fragile exact-pixel LSB explanations are strongly downgraded.
- The H/V pattern itself remains an unresolved clue, not a proven payload; the prior post-hoc hexadecimal `0x321` interpretation stays retired.
- New strategic leverage: the author said the known public escrow address is also present somewhere in the image. Use that known public 160-bit value as a safe positive probe for the visual carrier mechanism.
- Stage 32 was chosen because the source width is exactly 1600 px = 160 address bits × 10 px. It tests a bounded coarse vertical-stripe encoding family, requires lossy-format reproduction, and familywise-calibrates the best match against random balanced 160-bit controls.


## 2026-10-03 — adaptive review of Stage 32

- Stage 32 tested the exact dimensional hypothesis `1600 px = 160 public-address bits × 10 px`.
- Best candidate matched 94/160 bits (Hamming 66), with familywise empirical **p=0.40953** against 20,000 same-balance null targets.
- The same coarse feature survived JPEG/resampling, confirming the feature itself is format-stable, but its address match is unexceptional.
- Adaptive conclusion: retire the simple 160 vertical × 10px bit-stripe representation.
- The public address remains useful as a safe known-answer probe because the author explicitly said it is present in the image.
- Stage 33 was chosen from a separate exact dimensional relationship: the published address has 40 hex digits and the source width is 1600 px = **40×40 px**. Test this bounded coarse hex-cell family with predeclared quantizers, familywise null calibration, and lossy reproduction.


## 2026-10-03 — adaptive review of Stage 33

- Stage 33 tested the exact coarse mapping `1600 px = 40 public-address hex digits × 40 px`.
- Best candidate matched **9/40** hex digits, with familywise p(exact)=**0.08519** and nibble-bit Hamming **67/160** with p=**0.95830**.
- The selected coarse visual feature itself was stable after JPEG/resampling (38/40 extracted digits unchanged), but its match to the known address was not statistically exceptional.
- Adaptive conclusion: retire uniform-width address partitions; Stage 32 and Stage 33 together provide no support for direct equal-cell encoding of the public address across image width.
- Strategy pivots to object-level visual grammar: secondary details, counts, selectors and ordering.
- Stage 34 was chosen to test whether the robust H/V building labels organize the independent Stage-12 secondary-detail measurements. It uses exact enumeration of all 495 four-V label assignments and excludes projection metrics that are circular with hatch orientation.


## 2026-10-03 — adaptive review of Stage 34

- Stage 34 tested whether the robust H/V labels organize independent secondary-detail statistics already measured in Stage 12.
- No feature was close to significant after exact permutation: raw p-values ranged from 0.3475 to 0.9071; the multivariate exact p-value was 0.7010.
- Adaptive conclusion: keep H/V as a real format-stable visual clue, but downgrade the specific idea that it selects a second channel of building-detail counts.
- Strategy shifts one level outward, from within-building statistics to explicit scene semantics.
- Stage 35 was chosen to test a direct building↔water-reflection relation. Buildings 3–12 use a fixed clean reflection strip (y=330..360); buildings 1–2 are excluded in advance because the large sailboat overlaps their below-skyline region. Two independent orientation measures and exact 4-of-10 permutation tests are used, with lossy-format replication.


## 2026-10-03 — adaptive review of Stage 35

- Stage 35 tested whether the fixed H/V building labels align with the orientation of directly underlying water-reflection strokes.
- Sobel and Fourier did not agree on association direction, and exact permutation p-values were non-significant (0.6762 and 0.3571 respectively). JPEG/resampling reproduced the same weak pattern rather than strengthening it.
- Adaptive conclusion: stop forcing H/V into secondary selector/reflection roles. Retain H/V as a real visible feature, but downgrade it to a secondary clue until independent corroboration appears.
- Re-read the early HomelessPhD PZL11 dossier. It confirms the parent question behind “format does not matter” was “What's the photo format. It's not JPG!?”, so the file-format context is real.
- The same dossier records an old unresolved hypothesis that the **large sailboat may hide plain text or another readable pattern inside its dense shading**; the prior work used manual histogram/filter experiments but did not establish a reproducible result.
- Adaptive decision: Stage 36 performs a bounded, reproducible multiscale visual-reveal audit of the large sailboat against matched scene controls, with no OCR and no private-key candidate construction.


## 2026-10-05 — Stage 36 review and orchestration correction

- Stage 36 had already completed successfully on 2026-10-04, but the ChatGPT research automation was disabled and therefore did not perform its hourly review.
- Stage 36 result is negative: 0/19 target rank-1 transforms on the original image and 0 transforms that remained rank-1 before/after lossy conversion.
- The large-sailboat hidden-text hypothesis is therefore downgraded rather than extended serially.
- The hourly controller has been re-enabled.
- Per user request, the next phase is a one-shot **50-experiment superbatch (A11-EXP-037 through A11-EXP-086)** plus aggregate **A11-EXP-087**. The batch is restricted to safe visual/semantic/steganalysis diagnostics and uses multiple-testing correction in the aggregate report.


## 2026-10-05 — adaptive review of Superbatch 37–87

- The 50-experiment superbatch completed successfully with no implementation errors.
- Aggregate A11-EXP-087: 0 PROMOTED, 3 INTERESTING, 39 NULL, 7 CONTROL_PASS, 1 CONTROL_FAIL.
- The three nominal survivors were A11-EXP-050 (reflection, p=0.03106), A11-EXP-043 (large-boat vertical projection, p=0.03315), and A11-EXP-061 (small-sail width/following-gap, p=0.03998). All had BH q≈0.425, so none survived multiple-testing correction.
- Adaptive conclusion: do not branch into three new interpretation trees. First falsify/replicate exactly these three under stronger independent controls.
- Stage 88 was designed accordingly:
  - 043: nuisance-matched same-size window null, with lossy replication;
  - 050: high-pass + edge representations, fixed spatial halves, and lossy replication;
  - 061: both independent Stage-19 segmentation families with exact 5! permutation tests.
- The three primary confirmation p-values are Holm-adjusted; a lead survives only with both a family-specific replication gate and adjusted p<=0.05.


## 2026-10-05 — adaptive review of Stage 88

- All three nominal superbatch survivors failed confirmatory replication.
- A11-EXP-043 fell to nuisance-matched p=0.0717 (lossy 0.0518; Holm 0.2151).
- A11-EXP-050 disappeared after high-pass and edge representations (p=0.6211 and 0.3222); its rightmost-band grayscale effect was localized to only one of two fixed halves.
- A11-EXP-061 did not reproduce under either independent Stage-19 segmentation family (exact p=0.5333 and 0.5667); the superbatch detector aligned with only 3/5 stable Stage-19 centers.
- Decision: retire all three and pivot to a genuinely independent evidence family rather than mining the same image statistics further.
- Public web review surfaced a 2021 Puzzling StackExchange reverse-image-search report linking the puzzle image to the five-item OpenSea collection `cryptocanvas.xyz - CANVAS`. Current OpenSea indexing dates the collection to Jul 2020 and exposes contract `0x0b0b70905137786cf705102c194a1b4916d8c4d0`; token #5 is the reported puzzle item.
- Stage 89 will audit public on-chain tokenURI/mint provenance and compare token #5 media to the canonical puzzle image. The collection postdates the puzzle, so derivative/mirror is the default hypothesis unless provenance says otherwise.


## 2026-10-06 — adaptive review of Stage 89

- The hardened Stage-89 rerun completed successfully.
- Blockscout indexed the first mint/Transfer for token #5 at 2020-07-24 16:19:20 UTC, about three months after the 2020-04-22 Puzzle #11 announcement. Tokens 1–5 were all minted in July 2020.
- This decisively retires CryptoCanvas as a possible pre-publication source for the puzzle image.
- Current tokenURI endpoints at cryptocanvas.xyz are dead and Stage 89 did not recover archived JSON.
- Important correction: the downloaded OpenSea media was the generated opengraph preview card, not proven original token media. Its poor correlation with the puzzle cannot be used to reject the 2021 reverse-image-search report.
- Adaptive decision: Stage 90 closes this branch by querying indexed NFT metadata/media and contract/deployer provenance, parsing embedded original-asset URLs from OpenSea, searching Internet Archive wildcard records, and perceptually comparing only actual candidate images against the canonical puzzle.


## 2026-10-06 — adaptive review of corrected Stage 90

- The corrected Stage-90 rerun invalidated the first Stage-90 implementation's false “misidentified reverse-image” conclusion.
- The exact token #5 OpenSea route renders the Puzzle #11 artwork inside its OpenGraph card. After isolating the artwork rectangle, ORB produced 266 good matches and RANSAC retained 239 homography inliers (89.85% inlier fraction) against the canonical puzzle image.
- Combined with the 2020-07-24 token #5 mint, CryptoCanvas is a confirmed **post-publication mirror**, not a pre-publication source and not evidence for the puzzle's encoding mechanism.
- Adaptive conclusion: close the CryptoCanvas branch.
- Next direction: reconcile the complete 2020–2021 public solver discussion against the current tested ledger. Several observations in the Puzzling thread—5/7 skyline split, pier X/IX/XI reading, source-photo possibility and filename-to-32-byte observation—do not appear in repository search, while alpha/first-row/H/V ideas are already heavily covered.
- Stage 91 will perform this archival delta audit before selecting another image experiment.


## 2026-10-06 — corrected Stage 91 review

- The first Stage-91 reconciliation was invalid because its coverage scan counted the controller/leads/worklog and Stage-91's own script as prior evidence. This made newly mentioned historical claims falsely appear COVERED.
- Fixed the same stage number to exclude self-referential planning material and reran it.
- Corrected result: 3 RETIRED_BY_LATER_EVIDENCE, 4 COVERED, 1 PARTIAL, 2 genuinely UNTESTED.
- The genuinely untested claims are (1) source-photo provenance and (2) pier/support Roman-numeral interpretation. The source-photo hypothesis receives higher priority because it is tied to the series' external-context puzzle grammar, while the Roman-numeral comment was explicitly speculative.
- The 5/7 skyline split is only PARTIAL: the counts appeared in the broad historical object-count sweep, but no independent evidence promotes them as a semantic instruction.
- Added a durable anti-recycling rule: exhausted/falsified hypotheses are not reopened without a demonstrated implementation defect or new independent evidence.
- Stage 92 selected: bounded source-photo candidate audit of the exact Courageous Sailing lead, its 2019–2021 archived page images, and a small public Boston/sailing/skyline image pool using photo-to-sketch geometric matching.


## 2026-10-06 — adaptive review of corrected Stage 92

- Stage 92's first run accidentally produced zero scored null images because the global URL cap was consumed by candidates before nulls were appended. Fixed and reran the same stage with separate candidate/null caps.
- Corrected run: 110 candidate URLs, 74 successfully scored candidates, 14 null URLs but only 1 successfully fetched null image, positive control PASS.
- No candidate met even the weaker “interesting” geometry gate; strong=0, interesting=0. The transformed-canonical control produced ~2291 SIFT homography inliers and ~524 ORB inliers, showing the matcher can detect a true geometric derivative.
- Best real candidate (Courageous Sailing CASD5.jpg) produced only 6 SIFT and 7 ORB homography inliers. Therefore the specific Courageous Sailing/Boston candidate pool is retired.
- The thin null pool prevents strong false-positive calibration, but is immaterial to the observed negative because there were no candidate positives to calibrate.
- Do not broaden arbitrary photo search without new provenance evidence.
- Stage 93 selected: one bounded test of the last genuinely untested historical visual claim, the pier/support X/IX/XI Roman-numeral interpretation.


## 2026-10-06 — adaptive review of corrected Stage 93

- Initial Stage 93 failed on OpenCV 5 Hough output shape; fixed under the same stage number.
- The next run exposed a deeper control defect: the composite IX/XI score was mathematically constrained below X, so synthetic IX/XI controls failed. Redesigned the scorer to combine independent X and adjacent-vertical evidence; all three synthetic controls then passed.
- Valid result: target is visually IX-like (4/5 configs original, 3/5 lossy), but this is not unusual among matched line-rich windows: familywise p=0.4107, matched-null max 0.9857 versus target 0.8741.
- Roman X/IX/XI hypothesis retired. This closes the corrected Stage-91 historical visual backlog.
- Next mechanism family is genuinely new: a format-invariant discrete stroke-orientation carrier inside the large sail. Earlier boat stages covered exact pixels/hashes and hidden text, not the capacity/robustness of individual visible line orientations.
- Stage 94 will measure only count/separability/robustness and explicitly will not persist or print an ordered target bit sequence.


## 2026-10-06 — calibrated Stage 94 review

- The initial Stage-94 count inference was not sufficiently calibrated because a synthetic 64-stroke carrier produced only 48 detected classifiable tracks.
- Repaired Stage 94 with synthetic controls at 16/32/64/128/256 strokes and wide detector-output compatibility bands.
- Detector saturation is visible at high density, but the real sail remains far below canonical carriers: target 10–14 detected tracks vs 45–52 for 64 drawn and 53–70 for 256 drawn.
- Both 64-hex-symbol and 256-binary-symbol one-stroke-per-symbol sail carriers are rejected conservatively.
- The sail still has stable two-orientation structure, but there are too few robust individual tracks for the tested direct carrier sizes.
- Stage 95 selected as a genuinely different mechanism: a 16-level foreground grayscale alphabet, motivated by the native grayscale image and the hexadecimal target representation. It will compare #11 against lossy variants, synthetic 16-shade controls, and solved Puzzle #5 as an author-style hand-drawn raster control.


## 2026-10-06 — corrected Stage 95 review and new Puzzle #9 evidence

- First Stage-95 run failed its synthetic-control validation and was not interpreted.
- Corrected detector cleanly separates a 16-mode positive from a continuous negative and uses solved Puzzle #5 as an author-style drawing control.
- All four Puzzle #11 regions are far from the validated positive control in every variant; direct 16-gray-mode / one-tone-per-hex-symbol encoding is retired.
- Fresh public-source research surfaced a directly relevant author statement about solved sibling Puzzle #9: on 2020-06-14 Tiamat wrote that the puzzle “required 4 steps” and guessed the anonymous solver found 3 and brute-forced one.
- This exact clue is absent from the current #11 branch, so it is genuinely new evidence rather than recycled community speculation.
- Stage 96 will fetch the original #9 permaweb page and assets, recover the author tweet context where possible, and compare #9/#11 mechanism-level construction to infer reusable steps without generating any candidate secret material.


## 2026-10-10 — adaptive review of Stage 96

- Stage 96 recovered the original Puzzle #9 image and page successfully.
- #9 is PNG P-mode indexed color, 900x635, no alpha; #11 is LA grayscale+alpha, 1600x1105. This weakens any attempt to transfer #11 alpha/channel-specific mechanisms from #9.
- The two images do share a broad PNG production family and the create-before-modify tEXt timestamp pattern, supporting production lineage rather than payload significance.
- Stage 96's Wayback call timed out, so its direct primary verification of the "required 4 steps" tweet failed.
- Follow-up public-source validation found the same status ID, timestamp, exact wording and Puzzle #9 context preserved independently in two public crypto-puzzle research pages. The official Arweave December newsletter independently confirms that everything needed for #9 was hidden in the image.
- The #9 image visibly contains a strong literary quote (Orwell/1984), a literal numeric stamp (12:05.04), and five distinct colored birds. These are obvious semantic/numeric anchors, but their role in the four steps is not yet established.
- Stage 97 selected to audit anchor robustness and source hierarchy before transferring any mechanism prior to #11.


## 2026-10-10 — adaptive review of corrected Stage 97

- Initial Stage 97 failed on an undefined variant constant; fixed under the same stage.
- Wayback then successfully recovered the original 2020-06-14 Twitter snapshot for status 1272111084867129344. The archived page title contains the author's exact “required 4 steps ... figured out 3 and brute forced one” statement. This upgrades the four-step clue from secondary corroboration to PRIMARY_VERIFIED.
- The green-bird “instability” was a categorical hue-boundary artifact: dominant hue moved only 38→36 after lossy transforms. Corrected stability uses circular hue drift; all five color anchors are stable (0–2 hue units).
- The official Arweave newsletter could not be fetched by the GitHub runner because Medium returns 403, but the public indexed official article independently confirms that everything needed for #9 was hidden in the image.
- Promoted prior: #9 was an image-only multi-step puzzle with multiple robust visible anchors. Guardrail: four steps do not imply four visible objects.
- Stage 98 selected to reconstruct the primary Twitter conversation around the #9 solve and look for explicit step/mechanism language before inventing any transfer to #11.


## 2026-10-11 — adaptive review of Stage 98

- Stage 98 recovered 10 primary archived status pages but no concrete Puzzle #9 solve step.
- Its automatic classifier promoted the term `order` from a tweet saying the unsolved puzzles were "ordered by difficulty" (3,9,8,5,7). Manual contextual review rejects this as a mechanism clue.
- Corrected Stage-98 decision: NO_NEW_MECHANISM.
- The useful primary evidence remains broad: Puzzle #9 required four steps; Puzzle #11's author says format does not matter, the private key is hidden in the image, and the public address is also included somewhere in the image.
- Since #9 visibly uses robust text/numeric anchors and Stage 36 explicitly avoided OCR, Stage 99 is a bounded whole-image visible alphanumeric audit over fixed #11 regions, transforms and cardinal rotations, with Puzzle #9 positive controls and shuffled negatives.
- The hourly adaptive controller was found disabled again and was re-enabled.


## 2026-10-11 — adaptive review of corrected Stage 99

- Initial Stage 99 was an implementation failure because the APRIL control looked for a standalone token even though Tesseract correctly recovered merged strings such as `APRILANDTHECLOCKSWER`.
- Fixed the same stage to count APRIL as a substring within the known quote OCR output. Both Puzzle #9 controls then pass across original and lossy transforms.
- Valid Stage-99 survivors: SSS (11 original, 9 lossy, 0 shuffled), EAE (7/9/3), BEE (2/3/6), IES (2/3/2).
- Interpretation is intentionally conservative: Stage 99 only establishes region-level OCR repetition. It does not show that different transforms read the same physical location.
- SSS is the only strong lead before localization because it is absent from shuffled controls; BEE and IES are especially suspect because shuffled controls produce them frequently.
- Stage 100 selected to require canonical-coordinate co-localization across preprocessing and lossy variants, with Puzzle #9 anchor boxes as positive controls.


## 2026-10-11 — adaptive review of Stage 100

- Both Puzzle #9 spatial-localization controls passed.
- SSS, EAE and IES fail original/lossy physical co-localization and are retired as OCR hallucinations.
- BEE alone survives at canonical box ~[803,520.5,883,545], with gray+Otsu support in original and lossy variants, mean OCR confidence 54.6, crop correlation 0.969, and zero qualifying shuffled clusters.
- Direct inspection of the saved BEE crop shows dense mostly-horizontal line hatching, not obvious human-readable B/E/E glyphs. This is critical: spatially stable OCR is still not proof of text.
- Stage 101 selected as an adversarial literal-text test: crop jitter, six Tesseract PSM modes, four image variants, matched line-art controls, rendered BEE positives and independent stroke-orientation balance.
- No semantic interpretation of BEE is permitted unless Stage 101 survives.


## 2026-10-12 — adaptive review of corrected Stage 110

- Initial Stage 110 failed synthetic controls due model-selection precision/criterion mismatch; repaired under the same stage number.
- Valid controls now pass: binary model selection 96.7% with minimum per-patch stability 96.7%; ternary 100% with minimum per-patch stability 93.3%.
- Both real tone metrics prefer three classes in every tested condition, producing modal sequence DDLLMMLLDMLM, but only 7/12 buildings retain their class in >=90% of perturbations.
- Decision: retire stroke-tone/pencil-pressure as a deliberate discrete carrier; the clustering exists but lacks per-building robustness.
- Stage 111 selected as a genuinely different cross-object semantic test: direct x alignment between the five right-hand sailboats and consecutive five-building skyline blocks, with no fitted translation/scale and two familywise null models.


## 2026-10-12 — adaptive review of Stage 111

- Stage 111 finds the same best skyline block (buildings 7–11) across all lossy variants, but the correspondence is not exceptional under both predeclared nulls: p=0.41334 translation-preserving and p=0.05970 spacing-constrained. Direct sail↔skyline alignment is retired.
- Important implementation correction discovered during review: the corrected Stage-105/111 right-hand sail centers are [1042,1148,1282,1372,1490], while Stage 19 used [675.5,1046.5,1144.5,1269.5,1361.0]. Stage 19 therefore included a non-sail x≈675 track and omitted the true rightmost sail.
- This invalidates Stage 19 as a replication of Stage 18's five-sail width sequence. The anti-recycling exception is satisfied by a concrete object-association defect.
- Stage 112 selected to remeasure the true five sails with two independent width estimators and synthetic positive/negative controls. It tests only whether Stage 18's +26,+26 first-three progression is genuinely visible and robust; no alphabet/modulo/key interpretation is attempted.


## 2026-10-12 — corrected Stage 112 review

- The first Stage-112 result was not interpretable: synthetic controls failed and the first two real sails were unmeasurable.
- Repaired the same stage rather than advancing. The final estimator uses center-anchored vertical-support projections for mask and Canny-edge representations and validates on synthetic positive/negative sail-width profiles.
- Final controls pass. True sail centers are [1042,1148,1282,1372,1490] with <=2 px drift under lossy transforms.
- Real median widths are mask [24,49,65,60,64] and edge [31,53,64,54.5,75.5].
- First-three AP errors are 9 and 11 px; permutation p=0.20 for both methods; the Stage-18 qualitative profile is not reproduced.
- Decision: retire the +26,+26 sail-width lead as a measurement/object-association artifact.
- Stage 113 selected from an exact untested dimensional relation: 1600 px image width = 64 private-key hex characters × 25 px. It tests only whether 64 fixed visual cells support a stable 16-state carrier, with all 25 phase offsets, synthetic controls, lossy replication and no ordered secret sequence persisted.


## 2026-10-12 — corrected Stage 113 review and new Reddit evidence

- Stage 113 was repaired until both synthetic controls passed. Final target result is negative: phase 0 ranks only 21/25; best cluster count is k=8; k=16 ranks 14/19 and is not tied with the best model.
- Decision: retire simple 64×25 vertical-cell / one-hex-symbol-per-cell encoding.
- Fresh public research surfaced the original 2020-01-21 r/ethtrader Puzzle #9 thread, which was not covered by the prior Twitter reconstruction.
- The indexed comments include several contemporaneous concrete hypotheses, especially a date/time path (05/04/2012 and 13:00), bird/color/direction observations, Orwell/1984, “invisible 9 lines”, and LSB suggestions; a 2020-06-09 comment notes the challenge was solved.
- Stage 114 selected to reconstruct the primary Reddit thread and distinguish OP/author replies, pre-solve hypotheses, and post-solve evidence. Community speculation is not promoted without corroboration.


## 2026-10-12 — corrected Stage 114 review and Stage 115 rationale

- Initial Stage 114 could not access Reddit JSON or Wayback from the GitHub runner, so it was correctly treated as source-recovery failure rather than a negative.
- Repaired Stage 114 under the same number using a bounded public snapshot independently verified against the canonical Reddit thread. Source controls then passed.
- Valid result: 8 mechanism-relevant comments, 7 pre-solve and 1 post-solve; zero mechanism-specific OP replies and zero independently corroborated community paths. Decision: NO_CORROBORATED_MECHANISM.
- The Reddit date/time, bird, Orwell, angle/line and LSB comments remain community hypotheses only.
- Fresh primary author evidence from the official 2019-10-10 "Community Spotlight: Meeting Tiamat" interview says Tiamat saw a Bitcoin puzzle on Reddit and then recognized the permaweb as a good immutable home for puzzles.
- Chronology is powerful: since Tiamat's series already existed by late May 2019, later 2019 Reddit puzzles cannot be the inspiration.
- Two May-2018 Reddit image puzzles are the strongest pre-launch candidates identified so far: 8kk0pa (1 BTC image treasure hunt) and 8krbd3 (2.5mBTC private key encoded in a visible custom character system).
- Stage 115 selected to score the fixed pre-launch candidates, require a direct Tiamat link for exact identification, and otherwise extract only shared construction traits as a family prior.


## 2026-10-12 — Stage 115 review and Stage 116 rationale

- Stage 115 completed cleanly. Chronology leaves two top pre-launch Reddit image puzzles, 8kk0pa and 8krbd3, tied at 6/6 broad construction traits.
- No direct Tiamat link identifies either candidate as the exact inspiration. Decision: EXACT_IDENTITY_UNRESOLVED_FAMILY_PRIOR_ONLY.
- Safe broad common traits are image-based, funded crypto reward, direct wallet/key unlock, multi-step, visible-semantic construction and availability of public hints/solution material.
- Candidate-specific tricks must not be transferred.
- Public-source mechanism evidence for both candidates was distilled into a fixed 11-operation vocabulary in clues/tiamat-inspiration-solution-grammar.json. No secret/key strings are stored.
- Stage 116 selected to compute only the strict intersection of confirmed mechanism operations across the two independent candidates. This is intended to sharpen the author-inspiration prior without inventing a solution for Puzzle #11.


## 2026-10-12 — Stage 116 review and Stage 117 rationale

- Stage 116 passed its synthetic intersection and source/schema controls.
- Strict intersection across both plausible pre-launch inspiration puzzles contains exactly three confirmed operations: visible_text_or_symbol_reading, ordering_or_traversal, and cross_domain_conversion.
- Selection/filtering, pairing, known-text reference and geometry are specific to 8kk0pa; custom alphabet, numeral-system mapping and final brute-force ambiguity are specific to 8krbd3. These remain blocked from transfer.
- Decision: NARROW_SHARED_GRAMMAR.
- Before applying those operations to Puzzle #11, Stage 117 will check whether they recur in Tiamat's own solved Arweave puzzle mechanisms from Stage 11.
- The mapping is deliberately conservative: ordering/traversal receives support only from an explicit sequence-pattern class, while visible-symbol reading and cross-domain conversion use fixed Stage-11 class allowlists.
- Promotion requires >=2 supporting mechanisms across >=2 solved puzzles, preventing one isolated solved clue from defining the author-wide prior.


## 2026-10-13 — switch to image-only Stage 120

- User explicitly prohibited further Twitter directions; Stage 119 source-limited research is shelved without an unjustified negative inference.
- Reviewed Stages 18/102/105/111/112 and superbatch to avoid repetition. Exact pairwise geometric reuse of *interior sail strokes* had not been audited; the prior experiments addressed widths, directions, spokes or x-alignments, not internal template identity.
- Created `tools/stage120_sail_motif_reuse.py` and GitHub Actions workflow `arweave11-stage120-sail-motif-reuse.yml` on `research/arweave11-chatgpt`.
- Stage 120 uses canonical PNG only, synthetic copy/mirror positives, independent hand-drawn silhouette-matched negatives, ORB/RANSAC and 4 lossy variants. No secret data operations.
- Run: https://github.com/AperioScanner/open-crypto-puzzles/actions/runs/38424534898. Await final result and audit controls before interpretation or choosing a later stage.


## 2026-10-13 — image-only Stages 120 and 121 result reviews

- Stage120 Actions run #38424534898 completed successfully; canonical hash and all controls passed. Original 5 sail centers [1042,1148,1282,1372,1490] drift <=2px across original/JPEG85/JPEG70/down75_up. All ten pairs of small sails had 0/4 variants meeting >=25 inliers, >=0.18 fraction; zero replicated internal-stroke templates. Closed narrow copy/paste hypothesis.
- Stage121 Actions run #38425779620 completed successfully; exact source hash; synthetic controls 82/82 passed; zero of twelve real building facades produced a robust two-estimator, four-variant count of long hatch strokes. No image-supported exact facade stroke-count sequence.
- Both tests were strictly visual and recorded reproducible JSON+REPORT; no secret candidates, BIP39 word lists, key derivations, or wallet access.
- Further investigation must remain image-only by user directive; do not repeat retired visual scopes or resume Twitter.


## 2026-10-13 — Stage 121 audit and Stage 122 selection

- Direct GitHub Actions check: Stage 121 #38425779620 completed with success.
- Read complete JSON and REPORT: true canonical hash, 82 synthetic pass cases with tolerance ±1 (some V16 synthetic estimates were 15), 0/12 real facades yielded an exact stable cross-estimator/cross-image integer count. This is a valid negative for the predeclared exact counting method, not a negative for arbitrary image codes.
- Read current STAGE_QUEUE, STATE, tested ledger, leads, stage120 result, and Stages 36/94/102/105/112 and 37–86 manifest; geometric sail heights, widths, x order and direct duplication had already been tested. Therefore Stage 122 changes the observable rather than recycling them: six-sail *signed side-shading* after correction by outside ink.
- Fixed image-specific ROI geometry, exact gates and positive, negative and neutral synthetic controls were recorded in Stage 122 script before launching workflow.
- Experiment is strictly image-only: no key, mnemonic, wallet or other secret processing. User-directed abandonment of Twitter remains in force.


### Stage 122 source-region audit and reproducible repair

Initial Stage 122 #38458484692 returned controls 72/72 PASS, 3/6 stable side classifications, but contact sheet from follow-up #38458745501 showed the exterior left/right masks intersected multiple neighboring sails and the pier. The "corrected" differences were dominated by that irrelevant background (up to ~0.70 absolute), sometimes reversing the within-sail sign. No valid inference may be drawn from that background subtraction.

Actual triangle interiors were visually located correctly; repaired *same* Stage 122 in commit 1deef3d7c33689d47cdc36650efe3ee49c709987 to drop exterior subtraction while preserving all six masks and predeclared gates. Verification run #38458971789 was launched. It remains image-only and carries no secret/key functionality.


## 2026-10-13 — Stage 122 final review and Stage 123 handoff

- Stage 122 final repaired run #38458971789: 72/72 synthetic controls passed; 3/6 six-sail shading polarities stable (large, small_3 and small_5 right-darker). Other three undecidable under unchanged raw contrast gates. No usable mixed-side pattern and no key material.
- Pivoted from direct object measurements to a new, bounded pixel-template question: do pencil strokes directly repeat between distinct foreground/background illustration regions? Stage 123 searches cross-region fixed-grid local 64px patches, with identical-patch vs independently drawn synthetic controls, lossy re-encoding, coverage check and strict correlation/IoU.
- This does not reopen Stage 120's within-five-sail copy tests; exactly one novel image-only experiment selected and preregistered.


## 2026-10-13 — Stage 123 review / Stage 124 selected
Confirmed GitHub Actions Stage123 run #38459664096 successful, canonical digest correct. Positive synthetic cloned patches produced 5 replicates; independent synthetic redraws produced 0; region coverage 228/265/230 patches; 0 of 180 top pairwise candidates passed the strict original/JPEG85/JPEG70/downsample correlation and IoU gates. Narrow valid negative.
Selected exactly one follow-up based on a concrete unresolved object-association defect: Stage 102 measured L/R on one spurious x~675 track and omitted rightmost x~1490 sail. Stage124 tests a *distinct* geometry (five corrected apex-to-outline-base-center lateral offsets) with fixed visible sail sites, two detectors, four lossy variants, strong positive/neutral synthetic controls. No secret interpretation.


## 2026-10-13 — Stage 124 result and Stage 125 plan
- Stage124 #38478839142 finished; 120/120 synthetic controls, original hash verified. Correctly localized five sails after fixing old Stage-102/19 object defect. Real lean classes N,?,N,N,L, with only rightmost sailor showing a reliable signed left offset; no mixed-sign coding pattern.
- Stage125 selected based solely on that newly observed single silhouette outlier: 216 fixed jitter/threshold/detector/format configs, positive fifth-left vs all-neutral synthetic controls, strong gap/offset gates, no key/mnemonic/address operations. Launch as workflow and audit controls before classifying.


## 2026-10-13 — Stage 125 audited, Stage 126 prepared
- Run #38479304077 completed successfully; recorded canonical hash verified; 216/216 artificial-left positive controls, 0/216 all-neutral positives; all 216 real source configs usable.
- Rightmost is lowest measured outline offset in 209/216 configs, but never achieves *both* preregistered offset <= -0.28 and runner-up gap >= 0.16. Result UNREPLICATED_RIGHTMOST_OUTLIER; do not retune.
- Selected exactly one independent visual-detail question: are narrow mast tips explicitly extended above some of the five true sail apices? Stage126 uses fixed windows, four lossy renderings, ±2px lateral jitter, binarized-ink and Canny continuity, and mast/no-mast/side-decoy synthetic controls. No secret or off-image operations.


## 2026-10-13 — Stage 126 validated, Stage 127 selected

- Stage126 Actions #38480951073 verified completed; SHA and 180/180 synthetic mast-present/absent/off-axis line controls passed. Real results 4 stable EXTENDED and 1 unknown; no mixed pattern; uniform masthead extensions not an encoded binary sequence by this test.
- One new bounded feature from the drawing itself: five small hull waterline slopes (below sail tips), not sail triangle orientation or ray counts. Predetermined hull strips, independent Canny/binary Hough slope estimators, four image variants, positive signed/neutral+decoy synthetic controls and conservative coverage gate; image-only and no secret reconstruction.


## 2026-10-13 — Stage 127 scientific audit and Stage 128 handoff

GitHub confirmed Stage 127 run #38482080263 success. Verified canonical hash, positive mixed-slope control and level+decoy negative both pass. Real hulls: 0/5 receive a stable classification, with contradictory Hough median slopes under lossy transforms and two detectors. The stored hull ROI contact image visibly overlaps sails/pier, invalidating strong per-hull waterline attribution. Verdict INSUFFICIENT_HULL_ISOLATION, do not retire hull semantics or claim negative results.

Stage 128 selected as a distinct image-only test: explicit closed-water-ripple topology across four fixed water ROIs, not the previously tested closed building topology, reflection directions, boat widths, or image-text OCR. Fixed thresholds, two detectors, lossy variants and calibrated closed ellipse/open arc synthetic controls. No secret/key/wallet/source-history operations.


## 2026-10-13 — Stage128 result and Stage129 handoff

Stage128 #38484785422 completed successfully while being checked. Synthetic closed/open control families passed; the four actual fixed ripple regions yielded 0 stable closed-loop counts across two methods x three thresholds x four lossies. Conclusion narrow negative for this closure topology, not for all image semantics.

Stage129 selected to correct Stage102's proved object association defect (not general recycled search): five actual sail interiors, diagonal line orientation only. Predeclared Sobel/Hough two-measure method, neutral/positive/negative controls, four image variants, >=4/5 reproducible classes and both signs required. Research remains restricted to public canonical image; no secrets or social media.


## 2026-10-13 — Stage129 repair and Stage130 selection
- GitHub Stage129 initial completion was technically successful but CONTROL_FAILURE 34/60; found unstable Hough fragments inside clipped synthetic sail panels. Replaced with raw-ink signed diagonal lag autocorrelation in SAME Stage129, with no shift to decision gate or mask geometry.
- GitHub Stage129 repaired run #38485582635, controls 60/60 PASS; all five real whole-sail Sobel scores were between -0.042 and +0.086 despite signed lag-correlation of variable direction. Zero cross-method full-sail classifications: INSUFFICIENT_REAL_HATCH_COVERAGE; no generalized negative.
- Stage130 selected: explicitly test whether cancellation occurs between LEFT/RIGHT subpanels with reversed pencil hatch angles; distinct from prior whole-sail signs (Stage129) and left/right darkness levels (Stage122). Two detectors, four lossies, five synthetic control patterns × five real-site sizes. No cryptographic or off-image operations.


## 2026-10-13 — Stage130 interpretation and Stage131 handoff
- GitHub run #38485935539 completed successfully, canonical image verified, 100/100 synthetic two-panel controls passed; 0 of five real sails showed stable dual-estimator left/right orientation in every format. Some individual panel signs were robust but no fully resolved pairs. INSUFFICIENT_PANEL_COVERAGE, do not claim no hidden meaning.
- The isolated sky was comparatively under-reviewed outside Stage12's 0..48px first-row, while stage130 remained inconclusive. Selected one different, bounded visual observable: true short isolated pencil dashes vs random speckles in four source-fixed blank-sky ROIs (not objects/boats/water), using two component algorithms, 3 thresholds and 4 renderings. Predefined positive/negative control images and reject/promotion rules. No secret candidates, external social research or wallet operations.


## 2026-10-13 — Stage 131 results and Stage 132 selection

GitHub Stage131 #38487611024 completed: 192/192 synthetic controls; all four real fixed sky ROIs empty of qualifying 12..250 pixel isolated short ink marks in original/JPEG85/JPEG70/resampled across 90/140/190. Negative only for four surveyed locations. Shifted to a newly seen implementation-quality issue in canonical image geometry: data/geometry.json claims "large_sailboat" bbox [44,320,359,599], whereas the visibly drawn triangle and hull extend to about x~525 and y~940. Stages36/94 use old box. Stage132 preregisters old-vs-fixed-polygon ink coverage with positive full/cropped negative synthetic controls, thresholds and lossy tests, and saves actual source overlay; may reveal undercoverage without posthoc key search. No external/sensitive operations.
