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


## 2026-10-13 — Stage132 confirmation and Stage133 re-audit

Verified GitHub Stage132 run #38488910201 completed with success, canonical image hash, full/truncated positive and negative calibration 24/24. All 12 source/lossy×threshold checks meet incompleteness criterion. Original threshold 170 source polygon ink outside legacy geometry.json bbox: sail 0.667162, hull 1.000000. This exposes ROI-truncation in previous structural work, including Stage94. Prohibited inference: a defective source ROI does not magically establish secret code.

Selected exactly one next experiment, Stage133: preserve Stage94 segmentation/skeleton/Hough code and its fixed thresholds, but compare counts under its original ROI and Stage132 corrected sail polygon, with explicit blank and synthetic 16/64 count controls. Do not extract ordered stroke signs, words, private keys or wallet material. The author's historical "format does not matter" note strongly favors a visually persistent clue, but no statistically defensible posterior percentage exists.


## 2026-10-13 — Stage133 reviewed, Stage134 prepared

- Stage133 GitHub run #38489793473 finished successfully. SHA256 canonical verified, full large-sail source control passed: 84.9331% of ink in the eroded Stage133 triangular ROI lies outside Stage94 partial rectangle. Synthetic positive 16-stroke detected minimum 15, 64-stroke minimum 42, blank 0. Stage94 old classifiable count min/max across 4 variants 10/14, new full sail 76/90; JPEG/resampling matching rates ~0.51–0.60 with preserved matched signs. The old count-negative cannot represent the full sail. **No cipher or secret scheme inferred.**
- Stage134 chosen as exactly one ROI-defect justified extension. Stage36 visual-transformation/glyph-component heuristics also used the defective box. Reuse its 19 transformations and non-OCR alignment diagnostics on the Stage132 complete triangle and three equally cropped scene controls, synthetic demonstration word/neutral scribble controls, 4 source formats, strict cross-family replicated rank gate. A positive requires manual inspection, never secret/key generation.


## 2026-10-13 — Stage134 repaired and Stage135 launched

Stage134 #38490289635 was CONTROL_FAILURE: fixture ABCD word covered just ~14.2% horizontal extent against a fixed 15% gate. Repaired SAME Stage134 by drawing a longer positive-only fixture ABCDEFGH; real data, 19 Stage36 transforms and thresholds unchanged. Run #38490532439 positive synthetic control replicated 9 transforms across four families, negative synthetic 0; real source had only 2/19 replicated signals, both DoG same family. Decision NO_REPLICATED_CORRECTED_SAIL_GLYPH_ALIGNMENT. Thus no validated generic glyph alignment in full sail; not a global no-hidden-message claim.

Stage135 selected based on independently established real 76–90 corrected full-sail stroke measurements (Stage133). Tests only aggregate orientation sign versus four fixed anatomical sail quadrants, with synthetic structured/balanced controls, exact group null via 20k conditional permutations, four lossy variants, precommitted p/effect and replication gates. Does not persist per-stroke ordered signs or construct any secret, key, mnemonic or wallet actions.


## 2026-10-13 — Stage135 review and Stage136 preregistration

Stage135 run #38490812973 completed success, source SHA passed, synthetic patterned and balanced control passed; 4/4 real variant tables show V-shaped x-side association, original p floor 1/20001, V=.819, all formats p<=.00005 and V~.82-.90. Crucially majority direction is LEFT NEG, RIGHT POS at both top and bottom. A normal illustration with mirrored hatching violates global permutation's assumption. No decoded message.
Selected Stage136 to condition on left/right side and ask for *new vertical variation* beyond normal V shading; uses exact conditional enumeration of 2x2 counts on each side and source-reproduction audit; precommitted natural-V negative, top-bottom inversion positive, balanced negative. No keys, mnemonic phrases, wallet operation, Twitter or external sources.


## 2026-10-13 — Stage136 reviewed, Stage137 launched

Stage136 #38491300004 finished success; canonical SHA and source table reproduction PASS, all natural-V/reversal/balanced null synthetic controls PASS. All four formats show no vertical sign effect after conditioning on left/right shading: p=.75769/.62998/1.0/.27117, vertical delta <=.1154. Stage135's p floor 0.00005 had an unrealistic global exchangeability null for illustrated triangular hatching and cannot support encoded meaning.

Stage137 chosen as one image-only, ROI-defect-justified question: compare reflection of large boat's fully visible hull with directly below wake. Earlier skyline reflection studies do not specifically cover this hull, entirely outside the old ROI. Predeclared matched 520x120 source windows, ink and edge metrics and four variant replication, full/independent synthetic controls, lateral shift negatives. No ordered codes/secrets/wallet or social sources.


## 2026-10-13 — Stage137 result and Stage138 handoff

Stage137 GitHub #38492279979 SUCCESS. SHA/control/source passed; two independent metrics across four image formats show near-zero direct mirrored hull/wake pencil template correlations, worse than all shifted-null baselines. Clear, scope-limited negative, not a global claim about reflections or the image.

Noticed a concrete, unaddressed consequence of Stage132's verified incorrect boat box: Stage35's building↔reflection test omitted buildings 1 and 2 due to claimed overlapping old boat bbox in reflection band y330..360, but Stage132's real sail top y398 does not intersect this band. Selected Stage138 as calibrated repair of Stage35 cohort without changing its statistic or H/V labels; exact 4-of-12 test, source-coverage gate, four format replication and positive/negative synthetic orientation patterns. No cryptographic material produced.


## 2026-10-13 — Stage138 all-building result; Stage139 ink-coverage gate

Stage138 GitHub #38492878610 completed SUCCESS; SHA, original Stage35 ten exact values reproduced, 8/8 positive/reversed synthetic controls PASS; first-two new reflection crops show mean darkness 63.31 and 38.13. Full 12-building Sobel V-H negative -0.032 to -0.023, exact p .556..582, Fourier p .327..370, so no confirmed direct facade H/V vs underlying-reflection orientation.

Audit noticed **existing Stage138 cohort had near-empty reflection ROI** in building #6 (0.4) and #11 (0.832), while Stage138 applied min mean-darkness 2.0 only to newly included #1/#2. Those blank areas cannot yield trustworthy orientation estimates. Stage139 precommits uniformly applying Stage138's own 2.0 coverage gate to every building; exact permutation comparison only if >=8 usable, >=3 V, >=4 H and exclusions replicate across all 4 source formats. Synthetic strongly directional positive/inverted negative controls have exact blank #6/#11. Do not re-label original H/V or update any p gate. No external source or private key operation.


## 2026-10-13 — Stage139 verified and Stage140 handoff

Stage139 Actions run #38494403165 completed successful. Full synthetic V/H and reversal controls pass, Stage138 12 rows reproduce exactly, real mean-darkness gate 2.0 excludes only buildings 6 and 11 on all four image formats. Both estimator exact p values fail (Sobel .20–.21; Fourier .329–.352). Conclusion negative strictly for direct H/V building-to-water orientation, even after fixing source exclusion and ink quality.

Next Stage140 selected to test previously unmeasured large-sail-to-five-small-sail cross-scale copy-paste of internal pencil marks, not comparable to Stage120's small-sail-to-small-sail repeat or Stage123's exact fixed-grid same-scale patch reuse. Fixed six true triangle anchors, affine rectification, both left/right interior panels, two complementary image estimators and lossiness replication. Synthetic same-template positives and independent same-silhouette negatives in advance. No key, seed, wallet or outside-image research.


## 2026-10-13 — Stage140 result; Stage141 handoff

Stage140 #38495397342 completed successfully; 20/20 true-copy and 20/20 independent same-outline controls passed, actual 5/5 interiors sampled adequately, 0/5 meeting copy criterion across smooth/detail channels on left and right in all four images. This is narrow evidence against literal large-to-small resized template cloning, not against visible geometric coding.

Stage141 selected to repair a *distinct historical image localization defect*: Stage40 did left/right symmetry on old large boat ROI whose hull coverage was zero (confirmed Stage132). Stage141 checks true large HULL interior bilateral pencil stroke copying (not mirrored hull shape), with predeclared axis x275, symmetric paired masks eroded from Stage132 polygon, two vertical bands, positive exact-mirror vs independent stroke redraw controls on all 4 image formats; image-only and no secret operations.


## 2026-10-13 — Stage141 reviewed; Stage142 started

Stage141 Actions #38495806304 completed SUCCESS. SHA and real source coverage confirmed; synthetic true horizontal mirror positive and independent-redraw negative passed 4/4 formats each (16 band cases). Real corrected hull mirrored left/right highpass detail -0.036/+0.017 original and similar JPEG/resample, no exact interior pencil copy; does not address hull silhouette or metaphoric meaning.

Selected Stage142 because Stage41 top/bottom "large boat" symmetry relied on old erroneous ROI with no hull ink, and Stage141 only repaired L/R. Fixed true hull Stage132 polygon eroded and axis y860.5, two anatomical fore/aft x-bands and precommitted upper/lower y-pairs; smooth ink/detail controls for mirrored vs fresh redraw strokes. All image-only; no secret, key, BIP39 or wallet operation.


## 2026-10-13 — Stage142 validated, user's chess silhouettes, Stage143 selected

GitHub Stage142 #38496317157 finished SUCCESS. Corrected full hull source coverage valid and 8 mirrored/independent redraw format-level controls passed across two x-strips. The real top/bottom ink correlations and pencil-detail correlations were low (<.26 smooth, <.015 high-pass); no replicated vertical mirror of hull strokes.

User uploaded an image they created by duplicating and rotating the original and tracing its central white negative spaces red, perceiving a king in the upper and a queen in the lower half. The source scene has two skyline groups, left 5 and right 7 buildings. Rotating then mirroring **necessarily manufactures symmetric blank shapes**; perceptual resemblance alone, especially hand outlined, is not independently established author intent. Selected Stage143 source-only comparison: faithfully recreate mirror+rotation, roofline-only silhouette and exact rooftop reordering controls; compare purely generic base/head flaring (posthoc descriptive, not chess significance), evaluate original roof source evidence across 4 variants, flag absence of unambiguous crown/cross specific features. Neither download/interpret any external chess puzzle hints nor generate codes/wallet keys.


## 2026-10-13 — Stage143 source-only chess negative-space audit

Action #38498657551 completed SUCCESS. Source mirror reproduction visually agrees with user's duplicated, rotated photograph minus their red marker tracing. Canonical rooftop ink across 12 buildings validated all four lossy/source renderings. Top void from right 7 buildings, lower void from left 5, with base/head flare ratios 2.716 and 8.05. Symmetry guaranteed by mirror transform, not an independent author-drawn element. Generic paired pedestal flares were possible in 17.14% of exact within-cluster roof-endpoint permutations. This figure is posthoc and cannot be used as a chess probability. No original unambiguous king cross or queen crown found, and no decoding attempted. Save findings; wait for another distinct source-visible clue from user's further rotations. Strict image-only, no wallets or key material.


## 2026-10-13 — Stage143 checked, Stage144 reversed-spire follow-up

Stage143 GitHub Action #38498657551 completed with canonical/roof provenance confirmed, synthetic 1.30x stepped pedestal controls passed, mirror equality 1.0. It reproduced user's hand-traced paired white central voids, but found no independently drawn chess crown/cross; generic stepped neck/base pair possible in 17.14% of descriptive rooftop permutations. Keep chess analogy unconfirmed.

Following user supplied a different mirror/rotation screenshot, with a single vertically pointed black spike and stacked horizontal building tiers. Stage144 asks a distinct, grounded visual provenance question: can an ordinary native HORIZONTAL shoreline/horizon pen stroke generate that VERTICAL spike after rotating and flipping the skyline? Source band fixed y225..292, long-run source detection across 12 x-bins, removal counterfactual, 4 lossy variants, synthetic horizon-on vs building-hatches-only off controls. Results remain image-only, not code/words/private keys or wallet access.


## 2026-10-13 — Stage144 scientific repair and Stage145 selected

Stage144 original Actions #38500113800 failed its positive calibration: all 12 x-bins remained after erasing *part of the same* 2px anti-aliased synthetic source line, since selected score row y256 and line center y260. Repaired algorithm to ablate entire morphological connected source horizontal line components intersecting same ±3px source row without relaxing any image/classification threshold. Repaired run #38500725098 controls 4/4 true horizon, 4/4 independent facade negatives. Real source line at y258..260 covers 11–12 x-bins, but ablation of one selected component drops just 3–4 x-bins, leaving 8/12 horizontally inked x-bins. Stage144 decision SPIRE_SOURCE_HORIZON_NOT_CONFIRMED. Do not claim this refutes all source geometry, only one-line provenance.

Stage145 selected as directly falsifiable follow-up from this residual structure: test whether multiple y-separated horizontal pen line bands in the canonical skyline are responsible for the user's reverse mirror central spike, preserving Stage144 geometry and morphological estimator; two-line positive, one-line negative and building-only negative controls, 4 lossy variants, exact Stage144 replay, contact sheets of component ablation. Image only, no code candidate or wallet activity.


## 2026-10-13 — Stage145 interpreted; Stage146 fixed native-source band follow-up

Stage145 run #38501094776 completed SUCCESS. Original SHA, all 12 synthetic two-line/single-line/none controls and exact Stage144 source reproduction PASS. Real native original, JPEG85 and JPEG70 each yield 2 source-connected horizontal bands (upper y232..242 centered ~237, lower y246..268 centered ~257); 75% resample joins them into one y232..268 component even though 8/12 source x-bins remain after the Stage144 selected stroke is removed. Outcome 3/4; strict decision NO_REPLICATED_MULTIPLE_HORIZONTAL_RULES. The missing downsample separation is now a documented segmentation sensitivity, not a global negative about native horizontal line structure.

Stage146 preregistered: compare fixed actual-source upper/lower horizontal band apertures in four JPEG/PNG variants, preserving Stage144 filter and threshold; synthetic double-line vs each single-line vs no-line controls 4x4 cases; must reproduce Stage145 exactly. Result is only image provenance for user's artificially rotated/mirrored city-spire silhouette and cannot identify intended symbol or secrets.


## 2026-10-13 — Stage146 reviewed; Stage147 independent skyline support started

Stage146 Actions #38501412862 completed SUCCESS. Canonical hash, all 16 artificial source two-line/single-line/no-line controls, and exact Stage145 source-metric replay PASS. Registered native-source top skyline y232..242: long horizontal mask spans 8/8/8/7 of 12 x-bins; lower y252..267 spans 11/12/12/11, under original/JPEG85/JPEG70/75%-resampling. At least 7 or 8 blocks of another band remain after ablating one. This resolves Stage145's 3/4 source component-connectivity result as a resampling merge, but no source-specific chess/tower icon is established. Stage147 preregisters *independent* pixel orientation/line-segment confirmation using Sobel and Canny-Hough, with 16 known two/one/zero native lines fixture checks. No key or wallet ops.


## 2026-10-13 — Stage147 validated; Stage148 targeted original H/V marker

Stage147 Actions #38501723077 completed successfully: synthetic four-case source fixtures x four lossy formats 16/16; Stage146 image-source replay exact. Independent Canny/Hough native y232..242 line support 11/12 x-bins, y252..267 12/12; Sobel 7/12 and 10/12, identical across PNG/JPEG/resample. This corroborates two native horizontal shoreline source bands without implying rotated/mirrored 'spire' is an authored code. Archive user mirror-specific branch unless new source-specific evidence.

Stage148 pivots to unmirrored original H/V building fill already robust since Stage10/31: test specific *ordinary building proportions as a confound* for H/V visual directions, NOT repeat coding or original bit-stream search. Fixed width, height, ratio, area extracted from existing geometry.json, exact C(12,4) assignment calibration and FWER max statistic, Stage10 source classifier and Stage143 roof corroboration 4 lossy copies, synthetic large/wide/tall H/V positives and invariant negative. No secret derivations, key candidates, addresses, wallets or Twitter.


## 2026-10-14 — Stage148 verified, Stage149 preregistered

Stage148 GitHub Actions #38502142003 completed successfully; SHA verified and 12×4 original H/V facade labels HHVVHHVHHHHV and all rooflines independently confirmed. Geometry null controls success; width, height, ratio and area exact permutation p values 0.1273,0.5980,0.5374,0.1798, joint corrected p=.29899, no simple shape explanation. Visual mapping H0 V1 yields 0x321 but intentional encoding remains unverified and Stage22 grouping caveat holds.

One new Stage149 assesses cross-facade vertical texture consistency, not previous overall orientation or line counts. Three fixed source tier windows per building and two genuinely different classifiers (Sobel direction energy and directional 4px-pair grayscale correlation), four original/lossy images, positive full H and V and alternating H/V/H plus white-negative fixtures, all 576 registered classification checks must pass before evaluating original. No secret/mnemonic/address/wallet work.


## 2026-10-14 — Stage149 concluded; Stage150 source jitter selected

Stage149 run #38576395527 successful and saved result/REPORT. SHA, whole 12-building H/V labels and 576/576 synthetic all-H/all-V/HVH/blank 3-tier source fixture readings PASS. Source real tier orientation stable 35/36, 9/12 facades 3/3 match whole building; mixed vertical-H changes observed in V facades #3/#4/#7 at lower tier, V facade #12 remains V. Threshold for promoting broad facade layer mixture was 4 buildings, so verdict FACADES_PARTIALLY_MIXED_OR_SOURCE_AMBIGUOUS, not decoded 321.

Exactly one Stage150 follow-up: verify lower-H of #3,#4,#7 and all-V of #12 under nine predeclared x/y source crop shifts and four renderings, keeping same Stage149 independent Sobel/lag classifiers and no thresholds fit to source. Positive V/V/H and two V/V/V null fixtures (with/without outside horizontal line); >=31/36 per-site per-band stability, 3 case families, source provenance gate; image-only. No mnemonics, private keys, wallets or external research.


## 2026-10-14 — Stage150 finished; Stage151 new source image triangle selected

Stage150 source jitter run #38577281719 completed: all 3 artificial V/V/H, V/V/V, V/V/V-with-external-H synthetic patterns passed at 4 V building geometries; source upper V remains V 36/36 all sites, lower H #3 36/36, #4/#7 24/36 and lower V #12 24/36 with no opposite labels. Preregistered 31/36 per-building gate fails, resulting in boundary-sensitive basal zone pattern. Do not promote 321 intentional coding.

The canonical drawing contains a distinct hollow triangular construction beneath the right pier, roughly vertices (1052,633),(1052,778),(1280,714), not included in 5 annotated small sails or big left sail. One new Stage151 source-only test evaluates whether it has dense pencil hatching like any of five known sails vs unhatched outline/rigging, with affine rectification, 2 fixed interior features, four formats, 48 hatched/empty object fixtures, positive source recovery gate 4/5. No wallet, key, mnemonic or outside source work.


## 2026-10-14 — Stage151 completed, Stage152 outline follow-up

Stage151 Actions #38578665223 finished. Canonical image source control and 48/48 synthetic filled/unfilled triangle calibrations passed; 5/5 known sail interiors full-source recovered, while under-pier triangular region at fixed (1052,633),(1052,778),(1280,714) has low interior shading density .154 and detail .082 and fails normal filled sail criterion. No sixth sail established under this test.

Stage152 preregistered: a sparsely shaded triangle can still be genuinely CLOSED or simply crossing dock ropes; test three fixed boundaries by affine normalizing exact prior six ROI triplets. Synthetic full triangle vs 2-edge V vs mast-only ×4 formats ×6 known sites; source positive control requires ≥4/5 true sail outlines. No keys, mnemonic, wallets or external research.

## 2026-10-14 — Stage152, Stage153 and source audit reconciled; Stage154 completed

Stage152 #38579548232 passed 72/72 artificial controls, and recovered ink on three interpolated sides in 5/5 bona fide sails plus the under-pier region across original/JPEG/resampling. It sampled interior side points excluding vertices, so “closed triangle” was only an outline-support label, NOT a physical corner-join proof.

Stage153 #38614668825 passed 48/48 idealized synthetic corner fixtures but only 2/5 bona fide sail shapes had all three true-source corners connected under the fixed detector. Decision INSUFFICIENT_KNOWN_SAIL_JUNCTION_RECOVERY; the negative candidate corner result is not interpretable as proof of openness. Source audit #38620890513 SUCCESS retained 48/48 and 2/5 unchanged. At three of four failed known sail corners, idealized inward rays were offset from ink by approximately 3–4 source pixels; remaining case had individually inked arms but different connected components. It confirms mismatch between idealized control and source drawing, NOT a repaired reliable detector. No Stage153 retrospective threshold tuning.

Stage154 precommitted a distinct long-range exterior-ray geometry test after the Stage153 audit: 20–56px outward projections beyond TWO lower corners, four rays per object ×six existing triangles, fixed thin on-line corridor plus flank control, four source formats, 144 synthetic positive/negative fixtures and ≥4/5 real sails negative source comparator. Run #38622499517 COMPLETED SUCCESS: **144/144 fixtures pass, 5/5 real sails are negative for double exterior continuation**, and candidate under pier is negative in 4/4 variants, resulting in NO_STABLE_PAIRED_OUTWARD_CONTINUATION_AT_FIXED_RAYS. Ink density alone was misleading: source candidate exterior rays include 1.000 raw dark support accompanied by 0.868 or 1.000 adjacent flanking support, insufficient geometric contrast. Negative is narrowly about distinct extended outward rays, not pier structure itself. No source-validated code or six-sail claim. The Stage151–154 family is now low priority absent an independent canonical visual feature. No Stage155 opened and no cryptographic key/phrase/wallet operations.

## 2026-10-14 — Stage155 legacy small-sail ROI band audit completed

A fresh reproducible provenance concern was identified in the immutable data/geometry.json: small_sails_band_y=[360,480] excludes the lower portion of four of the five true small sail polygons already localized by Stage112/151/153. This is distinct from Stage132's giant-sail erroneous bbox and from Stage112's mistaken sail object identity. Stage155 preregistered immutable polygons, eroded interior masks, 3 thresholds x4 source formats, a >=25% omitted-ink gate for >=3/5 sails, and 40 full-ink vs within-band synthetic fixtures. Code and one workflow were committed to branch research/arweave11-chatgpt before execution.

Actions #38625119115 COMPLETED SUCCESS, canonical SHA matched, 40/40 fixture readings calibrated. True original sail drawing missing below/above the legacy band at dark threshold170: **sail1 91.8%, sail2 77.0%, sail3 55.3%, sail4 31.5%, sail5 0.0%**. All first four exceed 25% omission across 12 lossiness/threshold settings; decision LEGACY_SMALL_SAIL_BAND_MATERIALLY_TRUNCATES_TRUE_SAILS. This validates a historical ROI description defect, not a steganographic signal.

Static scan of 212 tool/workflow files found exact direct consumers Stage12, Stage15, Stage19, Stage23. Manual reading of their relevant code confirms this y field determines the small-sails-band portions: Stage12 image connected-component/perimeter/projection statistics, Stage15 3-2-1/1-2-3 regional component count, Stage19 formerly incorrect sail-track remeasurement (subsequently corrected by Stage112), Stage23 descriptive bitplane statistics. No basis to invalidate unrelated building, water or skyline ROIs, infer hidden patterns, or relaunch exhausted Stage19 width progression. The historical metadata and reports were not modified; new results are isolated in analysis/runs/stage155-small-sail-band-audit. No Stage156 launched.

## 2026-10-14 — Two sequential calibrated follow-ups Stage156 and Stage157

Stage155 documented a substantive obsolete true-small-sail y-band that excludes 31–92% real ink in four genuine sail polygons. Stage156 targeted only the direct Stage15 dependence: exact historical 5/5 y-band count replay, 60/60 precommitted synthetic 321/123/negative controls, then five true sail polygon masks with the original five dark thresholds and connected-component class bins. Workflow #38626316298 succeeded, but no corrected full-sail region gives a reproducible 321 or 123 signature. Stage15's original old-band negative lacked full-sail coverage, while the new corrected limited test is negative too. Neither provides proof of a coded hex321 instruction.

Stage157 independently audited the Stage12 *projection* lag=3 feature using the five same true sail masks, fixed 7px padded bbox, and flat-silhouette vs x-period12 synthetic source references. Workflow #38626858986 succeeded: original Stage12 lag/scores replay exactly and 24/24 synthetic fixtures distinguish lag3 from lag12. Real corrected source has x lag=3 across 12 format/threshold settings, the very same x lag3 as uniform flat polygon silhouettes; differences between x scores only 0.079..0.124. Source lag3 therefore has an ordinary geometry explanation at this precommitted resolution. No Stage158 created; no key/wallet work.

## 2026-10-14 — Stages158 and 159 final corrected full-boat audit

Follow-up after verified Stage157 was justified by a DIFFERENT specifically demonstrated historical source defect: old data/geometry.json large_sailboat rectangle excludes 66.7% of main sail and all hull (Stage132). Stage15 and Stage12 had directly measured that *incorrect* region, independent of the newly corrected small sail y-band. Stage158 locked the same Stage132 fixed sail and hull polygons, old Stage15 thresholds and component bins and the source replay before testing any corrected real image; Actions #38628765657 finished with 5/5 exact prior measurements, 60/60 positive/negative synthetic controls, and no corrected 321/123 count signature (original source [445,4,2] at t80, [323,1,2] t110, [208,2,2] t140, [147,1,2] t170, [98,1,2] t200). No author-intent claim.

Stage159 tested Stage12's separately unverified high x projection lag3 in the full large ship, rather than running another count. Its first run #38629049228 had CONTROL_FAILURE (12/24) since a synthetically injected source period12 with 3px-wide stripes gave a strongest third-harmonic at lag36. This is a calibration defect: external synthetic-only tests with the fixed Stage12 statistic showed 5px-wide period12 stripes yield exact lag12 across all re-encoded formats and three thresholds, with no target-source tuning. Fixture width alone changed; the method and interpretation gate stayed fixed. Repaired Stage159 #38629357345 passed 24/24 controls, exact old x/y lag/score replay, original SHA; corrected real source is lag3 in all 12 settings, which is also produced by uniformly filled ordinary sail/hull silhouette, real-minus-shape autocorrelation score differences only 0.001–0.007. Decision SOURCE_LAG3_COMPATIBLE_WITH_FULL_BOAT_SILHOUETTE, not encoded numeral or key.

Both source-region corrections are now exhausted in Stage12/15 family. No Stage160 created merely for numerical progression. Prior Stage153 triangulation remains inconclusive; no secret/seed/wallet address checking.

## 2026-10-14 — Stage160 original perimeter metric completed with scientific guard

From the Stage132 and Stage155 verified geometry ROI defects, Stage160 preregistered the last different Stage12 descriptive statistic, perimeter_fraction_t140(width1/2/4), on its two known bad original rectangle regions. Historical original-image values replayed exactly 6/6, synthetic black-rim versus white-rim controls passed 48/48. But the corrected real ROIs used already precommitted polygons each eroded 5x5 then bounded by original polygons; this makes the primary width2 ring geometrically entirely OUTSIDE permitted source mask. First run #38631390911's real=flat zeros therefore did not establish shape similarity or absence of pen-edge marks.

Repaired SAME Stage160 by explicitly computing eligible mask pixels in the fixed ring, without changing the test itself. Repaired workflow #38631617863 SUCCESS: 0 eligible source pixels at width2 for BOTH large-boat and five-small-sails ROIs. Decision MASKED_RECTANGLE_EDGE_NONINFORMATIVE_BY_CONSTRUCTION. Result explicitly a limitation of metric design, NOT a source visual/crypto negative. Preserve legacy data and reports and record invalid first interpretation. No Stage161 without independent new image observation; stopped rather than retuning geometric choices after results. No secrets/keys/wallet or social search.

## 2026-10-14 — Stage161 synthetic-only harmonic audit

After Stage160's physically ineligible corrected crop perimeter (0 permitted pixels at width2), no new source candidate was promoted. One methodological issue remained independently documented by Stage159's known-positive synthetic period12 stripes returning best lag36 until the fixture stroke width changed. Stage161 registered a SYNTHETIC-ONLY test of Stage12's overlap-normalized global-variance autocovariance on both fixed pre-existing polygon masks and stripe widths2,3,4,5 at true period12 across original/JPEG85/JPEG70/resampling and 3 thresholds. No actual source pixel observations, new codes, or crypto operations.

Actions #38636500115 finished SUCCESS. Synthetic source-mask/generator integrity 120/120, filled-shape x-lag3 references 24/24. Across 96 known period12 synthetic controls, detected best x-lag exactly12 in 60; selected harmonics 24/36/48 in 36 and never an unrelated lag. Thus shortest/fundamental period is not identified by the old maximum rule. Some 48/120 source-blind synthetic score values exceeded 1, establishing that original Stage12 output must not be represented as bounded Pearson correlation. Any earlier visual association with lag3 remains an ordinary short-lag shape comparison, not intentional encoded digit proof. No Stage162 queued without independent original-image evidence.

## 2026-10-14 — Four sequential source-audited Stages162–165

Stage161 had verified a short-lag period estimator's harmonic ambiguity but no original-image clue. A further independent established source BUG was located in Stage95: its large_sail tonal input was constructed from the broken legacy bbox already disproven by Stage132. Stage162 kept Stage95's exact tonal kmeans/scoring, frozen original author-style reference and original/JPEG image variants but replaced ONLY the input ROI with the full Stage132 large sail polygon. First run #38646301508 was CONTROL_FAILURE (21/22) due synthetic 16-tone positive at 24px checker patch failing only 75%-resize gate by 0.0068. Prior source-blind synthetic-only tests supported changing positive fixture block width from24 to32, no source/method/gate edits. SAME Stage162 rerun #38646502592 reached 22/22 and found 0/4 positive-tone/source resemblance, decision NO_ROBUST_FULL_SAIL_16_TONE_ALPHABET.

Stage163 audited old superbatch_stage37_87.py and Stage87 manifest/result against Stage112/132/155 confirmed source footprints. Workflow #38647052691 passed 7/7 structural controls and classified 24/50 direct bad-crop dependencies: 20/42 analytic rows and 4/8 controls. Old nominal Stage43/61 directly affected, Stage50 unaffected by these exact dependencies. Archived FDR adjusted q and raw p were not silently recalculated. Historical negatives cannot be called exhaustive full-boat or true-five-sail coverage.

Inspecting Stage112's own box construction independently revealed upper-only y345:500 crop retained after it fixed the mistaken sail identities. Stage164 registered true Stage153 sail polygons and original Stage112 4x5 boxes; GitHub #38647330833 succeeded with 40/40 synthetic controls and source showing omission in 3/5 real sails (70.1/51.4/22.7% gray<150 original, 12/12 variants/threshold checks >=20% for all three). Stage112 apex x-center localization remains valid but the old widths should not be represented as full sail measures.

Based on this actual implementation/coverage defect and the old Stage61 nominal width-to-gap hit, Stage165 tested only Stage61's identical absolute Pearson plus exact 5! permutation formula with five correct TRUE annotated full BASE outline widths [70,76,88,84,94] and corrected x centers from Stage112. Actions #38647720314 passed 13/13 source and 7/7 numerical controls, yielding exact p 0.616667 original and 0.566667 resized, not significant. This was annotation-based visible base geometry, not an independent raster width measurement; not a decoded message. Stage166 NOT launched in absence of new original-image cue. No secrets/keys/wallets/public address candidate checks.

## 2026-10-14 — Sequential Stages166,167,168 audit annotated endpoint uncertainty

Stage165 used hand-annotated five true sail base widths, giving exact original p=.616667 on width-to-next-sail-center-gap. Stage166 #38648679111 verified unchanged Stage165 source/numerical result, then exhaustively modelled ten independent LEFT/RIGHT x-footpoint uncertainties {-4,0,+4}px each. 59,049 synthetic ordered choices => 3125 unique widths, 16/16 controls PASS, and 33 distinct artificial width vectors would pass the old Stage165 joint all-four-format gate. This shows purely mathematical FRAGILITY, not new source-grounded significant widths.

Stage167 initially #38649137689 CONTROL_FAILURE (40/160), because 3x3 any-dark patch scorer could not distinguish clean lines only 4px apart. A source-blind synthetic calibration of continuous center-pixel darkness passed 120/120 shifted pencil lines; exact same Stage167 repair #38649376400 passed 160/160 fixtures and 6/6 provenance checks. With unchanged 5 true sail shapes and four re-encodings, only sail2_right original0 aligned clearly; three others preferred nonzero displacement (sail3_left +8, sail4_right -8, sail5_right -8), six unresolved. This is a SCORE preference in heavily hatched artwork, not an independently measured true outer foot.

Stage168 #38649693254 compiled and SHA/readback validated a contact sheet with ORIGINAL RAW grayscale versus original0 and Stage167 ±8 overlays, 12/12 structure controls. Assistant descriptive visual inspection found the alternate lines follow dark interior pencil hatching of sails more closely than the exterior silhouette (see VISUAL_REVIEW.md), but it is not certified independent human re-annotation. NO new source-corrected endpoints or decoded message; Stage165 numeric result not rerun on selected pixels. Stop; no Stage169 without independent new original-image evidence. No wallets, BIP39, key guesses or external social research.
