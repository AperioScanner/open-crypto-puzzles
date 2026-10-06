# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-06

## Review through corrected Stage 90

The corrected Stage 90 completed successfully.

### CryptoCanvas conclusion

- Token #5 mint: **2020-07-24 16:19:20 UTC**
- Puzzle #11 publication: **2020-04-22**
- the NFT therefore postdates the puzzle by roughly three months
- token-specific OpenSea OpenGraph artwork was segmented from the social card and matched against the canonical puzzle image with ORB + RANSAC:
  - **266** good feature matches
  - **239** homography inliers
  - inlier fraction **0.8985**
- verdict: **CONFIRMED_POSTPUBLICATION_MIRROR**

The first Stage-90 run that said “misidentified reverse-image lead” is explicitly invalidated: it accidentally treated unrelated OpenSea recommendation images as token-specific media. The corrected rerun uses only evidence tied to the exact contract/token route.

### Hypothesis decision

- CryptoCanvas as a pre-publication source: **RETIRED**
- CryptoCanvas as a later mirror of Puzzle #11: **CONFIRMED**
- CryptoCanvas as a clue to the encoding mechanism: **NOT SUPPORTED**

This archival branch is closed unless new author-linked evidence appears.

## Next stage

**Stage 91 — historical solver-clue reconciliation audit.**

Reason:
- after closing CryptoCanvas, the best remaining path is external archival / semantic evidence;
- the public Puzzling StackExchange discussion contains several concrete observations that were never systematically reconciled against the branch's tested ledger;
- some are already exhausted (alpha, first row, H/V), while others may be genuinely untested (the objective 5/7 skyline split, pier Roman-numeral interpretation, possible source-photo hypothesis, and the filename/32-byte observation).

Bounded goals:
1. Fetch the complete public Puzzling question, answers and comments through the Stack Exchange API / StackPrinter fallback.
2. Fetch the HomelessPhD PZL11 public dossier.
3. Inventory a predeclared set of historical clue claims.
4. Search the current repository ledger/reports/scripts for direct evidence that each claim has already been tested.
5. Classify each claim as:
   - **COVERED**
   - **PARTIAL**
   - **UNTESTED**
   - **RETIRED_BY_LATER_EVIDENCE**
6. Rank only genuinely untested visible/semantic claims for the next adaptive stage.

Stage 91 does not interpret any candidate as private-key material and performs no wallet/key operations.

## Status

- Stages 1–90: completed.
- Corrected Stage 90: COMPLETED + REVIEWED.
- CryptoCanvas branch: CLOSED.
- Stage 91: selected for launch.
