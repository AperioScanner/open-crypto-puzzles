# Arweave Puzzle #11 — adaptive stage controller

Last updated: 2026-10-03

This file defines the one-stage-at-a-time adaptive research loop on `research/arweave11-chatgpt`.

## Control loop

1. GitHub Actions executes exactly one experiment.
2. The stage commits non-secret `REPORT.md` + `result.json`.
3. ChatGPT reads the actual result before choosing the next experiment.
4. ChatGPT updates the hypothesis tree and designs exactly one next bounded stage.
5. Implementation failures are fixed under the same stage number before advancing.

## Adaptive review through Stage 31

### Stages 28–30 — traversal anomaly resolved
Stage 28 initially promoted a grayscale bit-0 traversal anomaly against block-shuffled surrogates. Stage 29 localized it. Stage 30 showed that the effect decomposes into ordinary large-scale image structure: foreground pixels generate the apparent printability, blank background strips generate extreme zlib compressibility, and the same behavior persists across bits 0–3.

**Decision:** generic traversal / exact low-bit hunting is retired as a primary route.

### Stage 31 — format invariance strongly favors the visual route
The 12-building H/V sequence survived every lossy transformation with **12/12 agreement under both independent classifiers**:

- JPEG quality 95 / 85 / 70
- downsample 0.75× then restore
- upsample 1.25× then restore
- JPEG85 + downsample/restore

At the same time, exact foreground bit-0 agreement fell to roughly **0.52–0.55**, close to chance.

**Decision:** promote a format-invariant visual/semantic carrier and strongly downgrade exact-pixel LSB explanations. This is route-selection evidence; it does not prove that H/V itself is the payload.

## Current hypothesis ranking

1. **Format-invariant visible/semantic encoding — highest priority.**
   Consistent with the author's statement that image format does not matter and with Stage 31.

2. **Known public escrow address as a positive probe — promoted.**
   The author said the public `0xFF2142...` address is also included somewhere in the image. Because the address is known, it can be used safely as a known-answer probe to discover the visual carrier mechanism without touching private-key material.

3. **Robust H/V building texture — active clue, interpretation unresolved.**
   The sequence is real and format-stable. The former hexadecimal `0x321` interpretation remains retired.

4. **Solved-puzzle visual grammar — active prior.**
   Prefer visible secondary details, counting, selection, rebuses, ordered interpretation and other human-readable mechanisms over arbitrary transforms.

5. **Raw low-bit / generic traversal / alpha carriers — downgraded or exhausted.**

## Next stage

**Stage 32 — public-address coarse-stripe known-answer probe.**

Motivation:
- the known Ethereum address contains exactly **160 bits**;
- the image width is exactly **1600 px**, giving a natural **10 px per address bit** partition;
- the author explicitly said the address is included somewhere in the image;
- a 10-pixel coarse visual encoding is compatible with Stage-31 format invariance in a way that exact LSBs are not.

Bounded test:
- partition the image into exactly 160 vertical cells of 10 px;
- derive binary sequences only from a small pre-declared family of visible features and semantic y-bands;
- compare against the known public address under standard ordering/inversion conventions;
- require replication after JPEG/resampling;
- familywise-calibrate the best Hamming match against random 160-bit controls with the same bit balance.

A negative result retires this simple 160-stripe address representation, not all visual address encodings.

## Status

- Stages 1–31: completed.
- Stage 31: COMPLETED + ADAPTIVELY REVIEWED.
- Visual/semantic route: PROMOTED.
- Exact-pixel low-bit route: STRONGLY DOWNGRADED.
- Adaptive controller: manual while user is active.
- Next stage: 32.
