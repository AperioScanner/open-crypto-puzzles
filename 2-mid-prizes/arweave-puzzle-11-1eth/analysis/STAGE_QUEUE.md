# Arweave Puzzle #11 — adaptive stage controller

Last updated: 2026-10-03

## Control loop

1. GitHub Actions executes exactly one experiment.
2. The stage commits non-secret `REPORT.md` + `result.json`.
3. ChatGPT reads the actual result before choosing the next experiment.
4. ChatGPT updates the hypothesis tree and designs exactly one next bounded stage.
5. Implementation failures are fixed under the same stage number before advancing.

## Adaptive review through Stage 32

### Stage 31 — route selection
The robust 12-building H/V texture stayed **12/12** under both independent classifiers across every tested JPEG/resampling variant, while foreground bit-0 agreement collapsed to about **0.52–0.55**.

**Decision:** prioritize format-invariant visible/semantic mechanisms; strongly downgrade fragile exact-pixel LSB explanations.

### Stage 32 — 160 vertical bit stripes: negative
The exact dimensional coincidence `1600 px = 160 address bits × 10 px` was tested with a predeclared family of coarse visible features and two natural reading directions.

Best result:
- Hamming distance: **66/160** (94 matches)
- familywise empirical p: **0.40953**
- same family survives lossy transform, but the target match is completely unexceptional

**Decision:** retire the simple 160×10px bit-stripe representation. Keep the known public address as a useful positive probe because the author explicitly said it is present somewhere in the image.

## Current hypothesis ranking

1. **Format-invariant visible/semantic encoding — highest priority.**
2. **Known public escrow address as a positive probe — active, but Stage-32 bit stripes retired.**
3. **Robust H/V building texture — active clue; interpretation unresolved.**
4. **Solved-puzzle visual grammar — active prior.**
5. **Raw low-bit / generic traversal / alpha — downgraded or exhausted.**

## Next stage

**Stage 33 — 40-hex-digit coarse-cell probe.**

Motivation:
- the public Ethereum address has exactly **40 hexadecimal digits**;
- image width is **1600 px = 40 × 40 px**, another exact and more semantically natural dimensional correspondence;
- hexadecimal digits are the human-visible representation in which the address was published;
- a coarse 40px feature is compatible with Stage-31 format invariance.

Bounded test:
- divide width into exactly 40 cells of 40 px;
- use a small predeclared family of visible aggregate features over fixed semantic y-bands;
- quantize each 40-cell feature vector into hexadecimal values using only predeclared min-max and rank-based 16-level quantizers;
- test polarity and the two natural reading directions;
- compare to the known public 40-digit address;
- familywise-calibrate exact-digit matches and nibble-bit Hamming distance against random permutations of the same public-address digits;
- require the same selected family member to reproduce after JPEG85 + resampling.

A negative result retires this simple 40×40px hex-cell family, not other visual/semantic representations of the address.

## Status

- Stages 1–32: completed.
- Stage 32: COMPLETED + ADAPTIVELY REVIEWED — NEGATIVE.
- Visual/semantic route: PROMOTED.
- Simple 160-bit vertical-stripe address encoding: RETIRED.
- Adaptive controller: manual while user is active.
- Next stage: 33.
