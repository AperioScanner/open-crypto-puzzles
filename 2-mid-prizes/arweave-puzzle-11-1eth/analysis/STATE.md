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

### P1 — identify a format-invariant visual carrier using known public information

Stage 31 decisively favors the visual/semantic route: the robust 12-building H/V texture survives all tested lossy JPEG/resampling variants at 12/12 under two independent classifiers, while exact foreground bit-0 agreement collapses to ~0.52–0.55.

The author also said the **public escrow address** is present somewhere in the image. Because that 160-bit value is already known and public, it can be used as a known-answer probe to discover the carrier mechanism without generating or verifying private-key material.

Stage 32 tests the simplest dimension-motivated visual hypothesis: image width 1600 px = 160 address bits × 10 px, using only coarse visible features, lossy-reproduction requirements, and familywise null calibration.

### P2 — retain the H/V texture without forcing `0x321`

The sequence `HHVVHHVHHHHV` remains a strong reproducible visual feature. The hexadecimal `0x321` interpretation was retired in Stage 22 due to grouping/representation look-elsewhere effects. H/V may still act as a selector, ordering clue, or semantic signal.

### P3 — solved-puzzle visual grammar

Use human-readable semantics, tiny secondary details, counting, rebuses, selection, and ordered interpretation as the main prior for future visual hypotheses.

### P4 — archival context

The mirrored #11 launch window is exhausted. Remaining archival value is in external early discussion or a first-hand account of Puzzle #9's solve method.

## Stop conditions

Stop and request review if:

1. a new clue materially changes the safe hypothesis space;
2. a planned scope becomes computationally unreasonable without justified reduction;
3. a proposed experiment would duplicate an exhausted scope;
4. the next step would require generating, deriving, reconstructing, enumerating, or verifying candidate private keys or attempting wallet access.
