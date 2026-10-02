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
