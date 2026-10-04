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
