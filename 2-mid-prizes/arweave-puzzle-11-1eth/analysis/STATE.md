# Research state — Arweave Puzzle #11

Last updated: 2026-09-30

## Objective

Find a 32-byte secp256k1 private key whose standard Ethereum address is exactly:

`0xFF2142E98E09b5344994F9bEB9C56C95506B9F17`

Success requires an exact address match. Prefix or partial matches are not evidence of success.

## Safety / handling

- Never broadcast a transaction.
- Never publish a discovered private key.
- If an exact match is found, stop the search and record only that an exact cryptographic match was found plus non-secret verification metadata.

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

### P1 — exhaustive continuous-channel bit extraction

The highest-priority unresolved family is a systematic scan of grayscale and alpha pixel streams beyond the bounded scopes already recorded.

Required dimensions include, where meaningful:

- grayscale and alpha independently;
- raster orientations and reversals;
- row-major / column-major;
- serpentine row / serpentine column;
- rotations / reflections represented as traversal transforms;
- individual bit planes 0..7;
- low/high 2, 3, and 4-bit symbol extraction;
- MSB-first / LSB-first within symbols and bytes;
- raw 256-bit windows over the full stream, not only the first row;
- structured 64-hex extraction when text-like encodings are plausible;
- candidate deduplication before secp256k1 verification.

Prior bounded scans in `analysis/tested.md` must be treated as exclusions.

## Stop conditions

Stop and request review if:

1. an exact target address match is found;
2. the planned scope would become computationally unreasonable without a justified reduction;
3. a new clue materially changes the hypothesis space;
4. a test would duplicate an already-exhausted scope.
