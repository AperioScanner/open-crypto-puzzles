# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-10

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through Stage 96

Stage 96 completed successfully and recovered the original Puzzle #9 page/image.

### What Stage 96 established directly

Puzzle #9 primary image:
- PNG, **indexed-color P mode**
- **900 × 635**
- **no alpha channel**
- 159 grayscale values after grayscale conversion
- visible image contains an Orwell/1984 quote, five colored birds on a tree, and a visible `12:05.04` stamp
- same PNG production family as #11 at the container level: gAMA, cHRM, bKGD, pHYs and tEXt chunks
- #9 has the same create-before-modify timestamp pattern as #11

Puzzle #11 differs materially:
- LA grayscale+alpha, 1600 × 1105
- 256 grayscale values
- 434 nonopaque alpha pixels
- public escrow address in a tEXt comment

### Four-step author statement: source validation

Stage 96 itself **did not recover the original tweet from Wayback** because the archive request timed out. Therefore the run's own field `author four-step Wayback verification = False` must not be read as a primary-source verification.

A fresh public-source check after Stage 96 found two independent public research pages carrying the same tweet ID, timestamp, wording and #9 context:
- `itsnex1s/crypto-puzzle-list/unsolved/arweave-puzzle-11-1eth.md`
- `itsnex1s/crypto-puzzle-list/unsolved/arweave-puzzle-3-1000ar.md`

Both attribute status **1272111084867129344**, 2020-06-14 10:18:11 UTC, to Puzzle #9 and reproduce:
> "The puzzle required 4 steps. My guess is the solver figured out 3 and brute forced one, that's why he is silent"

The official Arweave December newsletter independently confirms that Puzzle #9's format was different and that **everything needed to crack the code is hidden in the image**.

### Hypothesis decision

- Shared create/modify timestamps: production lineage, not payload evidence.
- #9 alpha-carrier analogy: invalid because #9 has no alpha.
- The exact four-step tweet is **strongly corroborated by public secondary archival research but not yet re-captured from a primary Twitter/Wayback endpoint in this branch**.
- The visible #9 image clearly supplies several robust semantic/numeric anchors; whether these correspond to the four steps remains unproven.

## Next stage

**Stage 97 — Puzzle #9 semantic-anchor + four-step source corroboration audit.**

Goals:
1. Re-fetch the original #9 image from the committed Stage-96 artifact.
2. Preserve fixed crops for:
   - Orwell/1984 quote
   - visible `12:05.04` stamp
   - each of the five colored birds
3. Measure whether those visible anchors survive JPEG/resampling and whether the five bird color classes remain distinct.
4. Fetch the official Arweave newsletter / announcement pages and record the "everything needed ... hidden in the image" statement.
5. Fetch the two independent public crypto-puzzle dossiers that preserve the exact four-step quote and thread context.
6. Attempt direct recovery through Twitter syndication and Internet Archive again, but classify evidence honestly if primary recovery fails.
7. Produce an evidence hierarchy:
   - PRIMARY_VERIFIED
   - OFFICIAL_CONTEXT_ONLY
   - MULTI_SOURCE_SECONDARY_CORROBORATED
   - UNVERIFIED
8. Decide whether #9 provides a defensible **semantic multi-anchor prior** for #11 or only a generic "image contains everything" prior.

No private-key candidates, hashes-to-key pipelines, or wallet checks are performed.

## Status

- Stages 1–96: completed.
- Stage 96: COMPLETED + REVIEWED.
- Puzzle #9 four-step statement: secondary corroboration strong; primary recapture pending.
- Stage 97: selected for launch.
