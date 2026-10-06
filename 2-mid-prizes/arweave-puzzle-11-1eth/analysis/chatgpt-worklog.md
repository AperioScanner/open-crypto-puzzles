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
