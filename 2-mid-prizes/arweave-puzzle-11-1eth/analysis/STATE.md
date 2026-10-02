# Research state — Arweave Puzzle #11

Last updated: 2026-10-01

## Objective

Find a 32-byte secp256k1 private key whose standard Ethereum address is exactly:

`0xFF2142E98E09b5344994F9bEB9C56C95506B9F17`

Success requires an exact address match. Prefix or partial matches are not evidence of success.

## Safety / handling

- Never broadcast a transaction.
- Never publish a discovered private key.
- If an exact match is found, stop the search and record only that an exact cryptographic match was found plus non-secret verification metadata.


## Current assistant research boundary

The active ChatGPT work on this branch is limited to non-secret research: public-clue recovery, visual semantics, image/steganography diagnostics, statistical structure, historical comparison, and reproducible code/tests that do **not** generate, derive, enumerate, or verify candidate private keys against the funded wallet. Historical experiments already present in this branch may contain address-verification counts; they are retained as prior work but are not extended by the active assistant scope.

## Canonical artifact

- Image: `clues/arweave-puzzle-11.png`
- Expected SHA-256: `c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1`
- Arweave tx: `CzITHnEIlkQw9SbaX5futCzFrKk1qe_NwvWnIBmP2fY`

## Existing knowledge

Read before adding experiments:

1. `README.md`
2. `analysis/tested.md`
3. `analysis/leads.md`
4. `clues/author-posts.md`
5. `puzzle.json`

The existing fork already includes substantial negative work: geometry and metadata families, alpha inspection, 7,168 pixel bitstreams for ASCII/compressed payloads, 79,863 unique valid scalars from first-row 256-bit windows, barcode scans, and 1,488 HD derivations from one skyline transcription.

## Research protocol

Every new experiment must record:

| Field | Requirement |
|---|---|
| ID | Stable identifier, e.g. A11-EXP-001 |
| Hypothesis | What encoding is being tested |
| Evidence | Why the hypothesis is plausible |
| Scope | Exact search space |
| Method | Reproducible decoding procedure |
| Controls | Synthetic/known-good checks |
| Result | Exact-match count and candidate count |
| Coverage limit | What remains untested |
| Artifacts | Script/report paths |
| Date | UTC or local date |

Do not rerun an exhausted scope unless the previous experiment is shown to be incomplete or incorrect.

## Current priority

### P1 — seek an independent visual confirmation of the robust `0x321` marker

Stages 10 and 13 now establish two separate facts: the 12-building H/V sequence is geometrically robust, and the exact `0x321` pattern is uncommon under simple random-orientation nulls (1/4096 unconditioned; 1/495 conditional on exactly four V buildings). This strengthens `321` as a lead but does not prove intent because the segmentation/coding were not pre-registered.

Stage 14 reconstructed the complete mirrored author launch window (2020-04-20 through 2020-05-01): there is **no direct textual 3-2-1 clue and no ordering/direction wording**. Therefore a second confirmation, if it exists, is more likely visual/semantic than textual.

Next bounded work: search the image for a second robust 3-2-1 / countdown / ordering / selection structure using object groups, secondary marks, perimeter/context cues, and spatial relationships. Reject unstable threshold artifacts.

### P2 — use the solved-puzzle design grammar, not arbitrary transforms

Stage 11 (A11-EXP-011) reconstructed 18 public solved-token mechanisms from #5/#7/#8. Fourteen are broadly semantic/contextual and four are counting/sequence/numeric-extraction mechanisms. Recurrent design habits include tiny secondary details, counting, cross-domain references, visual + technical context, and ordered interpretation.

This is now the main prior for deciding which visual hypotheses deserve tests.

### P3 — inspect Stage 12 promoted regions without over-reading raster artifacts

Stage 12 ranked regions by stable small-component counts, perimeter occupancy, and projection periodicity. The common best lag of 3 across very different regions is likely influenced by stroke width/raster structure, so it is **not** independent support for 321 by itself. Use the diagnostic atlas to identify human-visible deliberate marks; require threshold/crop robustness before promotion.

### P4 — recover missing first-hand context around #9 and early community discussion

The complete mirrored #11 launch window is exhausted. Remaining archival value is in sources outside that mirror: early Telegram/Discord/Weavemail, deleted replies, or a real #9 solve-method account. #9 remains the strongest sibling-control lead.

## Stop conditions

Stop and request review if:

1. an exact target address match is found;
2. the planned scope would become computationally unreasonable without a justified reduction;
3. a new clue materially changes the hypothesis space;
4. a test would duplicate an already-exhausted scope.
