# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-05

## Review through Stage 88

Superbatch 37–86 produced three nominal p<=0.05 results, but none survived FDR. Stage 88 subjected exactly those three to stronger independent replication.

### Stage 88 result — all three retired

- **A11-EXP-043 large-boat vertical projection**
  - nuisance-matched p = 0.0717
  - lossy nuisance-matched p = 0.0518
  - Holm p = 0.2151
  - not confirmed

- **A11-EXP-050 rightmost reflection**
  - high-pass p = 0.6211
  - edge p = 0.3222
  - one fixed half replicates weakly, the other does not
  - Holm p = 1.0
  - not confirmed

- **A11-EXP-061 small-sail width/gap correlation**
  - independent Stage-19 method p-values = 0.5333 and 0.5667
  - only 3/5 Stage-61 components align with Stage-19 stable centers
  - Holm p = 1.0
  - not confirmed

**Decision:** retire all three nominal superbatch hits. Do not continue localizing them.

## New independent clue family

A public Puzzling StackExchange thread from 2020–2021 contains a reverse-image-search lead that has not been audited in this branch:

- a commenter reported that the puzzle image appeared in an OpenSea collection named **cryptocanvas.xyz - CANVAS**;
- current OpenSea indexing shows the collection contract `0x0b0b70905137786cf705102c194a1b4916d8c4d0`, five items, dated **Jul 2020**;
- token #5 is owned by `0xfdae2f991a521f54bbef89048922dff9bac2d96b`;
- the collection postdates Puzzle #11 (April 2020), so it may be a derivative mirror rather than a source—but its on-chain metadata/provenance could still preserve descriptions or source material no longer indexed elsewhere.

This is genuinely independent of the exhausted visual-statistical families.

## Next stage

**Stage 89 — CryptoCanvas provenance and metadata audit.**

Goals:
1. Query the public ERC-721 contract for `tokenURI(1..5)` and `ownerOf(1..5)` using public Ethereum RPC.
2. Fetch any public token metadata and media URIs without credentials.
3. Identify the first Transfer/mint log for each token and record block timestamp, recipient and transaction sender where available.
4. Compare token #5 media against the canonical puzzle image using hashes, dimensions and image-level similarity.
5. Determine whether the collection is:
   - an exact post-publication mirror;
   - a modified derivative carrying additional visual/metadata information;
   - or unrelated/misidentified.
6. Record descriptions/names/attributes that could constitute an independent clue, without treating later third-party text as author evidence unless provenance links it to Tiamat.

No secret/key extraction is performed.

## Status

- Stages 1–88: completed.
- Stage 88: reviewed — 0 confirmed survivors.
- Stage 89: selected for launch.
- Hourly controller: enabled.
