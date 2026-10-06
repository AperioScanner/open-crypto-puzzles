# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-06

## Review through Stage 89

Stage 89 is now technically valid enough to review after two implementation fixes.

### Confirmed facts

- CryptoCanvas contract: `0x0b0b70905137786cf705102c194a1b4916d8c4d0`
- token #5 first mint/Transfer: **2020-07-24 16:19:20 UTC**
- Puzzle #11 public announcement: **2020-04-22**
- therefore the CryptoCanvas token is on-chain **~3 months after** the puzzle publication
- all five CryptoCanvas tokens were minted in July 2020
- current `tokenURI` values point to dead `https://cryptocanvas.xyz/api/token/<id>` endpoints
- no archived token JSON was recovered in Stage 89
- the Stage-89 media comparison used OpenSea's generated **opengraph image**, not proven original NFT media; its mismatch therefore does **not** establish that the reverse-image-search report was false

### Hypothesis decision

**CryptoCanvas is retired as a possible pre-publication source.** The mint dates make that impossible.

However, the weaker hypothesis remains unresolved:

> CryptoCanvas may be a post-publication derivative/mirror whose cached NFT metadata or original media could identify who mirrored the puzzle, preserve historical asset URLs, or validate the 2021 reverse-image-search report.

That distinction matters. We should close the provenance branch correctly rather than infer from an OpenSea social-preview card.

## Next stage

**Stage 90 — CryptoCanvas closure audit: cached NFT media + deployer provenance.**

Bounded goals:

1. Query Blockscout's indexed token-instance endpoint for tokens 1–5, looking for cached metadata, image URLs and external URLs no longer available at `cryptocanvas.xyz`.
2. Query Blockscout contract/address records for creator/deployment transaction and verified-source metadata.
3. Resolve transaction senders for the deployment and the five mint transactions.
4. Parse the current OpenSea token #5 HTML for embedded original-asset candidates, not only the opengraph card.
5. Query the Internet Archive wildcard index for historical `cryptocanvas.xyz/*` URLs from 2020–2021 and look specifically for token #5 metadata/media candidates.
6. Download bounded image candidates and rank them against the canonical puzzle PNG using image-level perceptual similarity.
7. Classify the lead as:
   - **CONFIRMED_POSTPUBLICATION_MIRROR** if actual/cached token #5 media strongly matches the puzzle;
   - **POSTPUBLICATION_COLLECTION_NO_MEDIA_PROOF** if provenance is later but original media cannot be recovered;
   - **MISIDENTIFIED_REVERSE_IMAGE_LEAD** if recovered token #5 media clearly does not match.

No identity attribution is inferred from an address without independent public evidence.

## Status

- Stages 1–89: completed.
- Stage 89: COMPLETED + REVIEWED.
- CryptoCanvas as pre-publication source: RETIRED.
- Stage 90: selected for launch.
