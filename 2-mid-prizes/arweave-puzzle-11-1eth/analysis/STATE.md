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

### P1 — interpret the robust skyline `0x321` marker as a human-readable clue/instruction

Stage 5 recovered the 12-building hatch sequence `HHVVHHVHHHHV`, which maps to `001100100001 = 0x321` under H=0/V=1. Stage 10 (A11-EXP-010) established that this sequence is not sensitive to the exact building crop: all nine tested inner margins preserved it; bounded jitter preserved the full sequence in 100% of trials through ±8 px, 94.25% at ±12 px, and 85% at ±16 px; mean per-building class stability under ±24 px local shifts was 97.9%.

Treat `321` as a clue lead, not a solution. The next work should ask what a human solver would do with that marker, especially in light of the author's 2020-04-23 instruction to "Look at the solved puzzles."

### P2 — reconstruct the author's solved-puzzle design grammar

Document the mechanisms of solved siblings (#1, #2, #5, #7, #8) from author posts and surviving solution write-ups. Known solved examples rely heavily on robust visual/semantic rebuses, ordered concatenation, small drawn details, cultural references, and sometimes technical/page context rather than fragile container metadata. Test only analogous **visual or semantic** structures in #11.

### P3 — non-key image diagnostics guided by `3-2-1`

Inspect bit planes / residual views / spatial masks for human-readable text, shapes, ordering marks, or other robust structure. Do not convert those observations into private-key candidates and do not compare candidates to the funded address.

### P4 — recover missing first-hand context

Search surviving author/community archives for puzzle #11 and puzzle #9 method clues, prioritizing primary or contemporaneous sources. The real #9 solve method would be especially valuable because the author described the puzzles as related.

## Stop conditions

Stop and request review if:

1. an exact target address match is found;
2. the planned scope would become computationally unreasonable without a justified reduction;
3. a new clue materially changes the hypothesis space;
4. a test would duplicate an already-exhausted scope.
