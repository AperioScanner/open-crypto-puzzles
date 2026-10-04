# Arweave Puzzle #11 — adaptive stage controller

Last updated: 2026-10-03

This file defines the one-stage-at-a-time adaptive research loop on `research/arweave11-chatgpt`.

## Required control loop

1. GitHub Actions executes exactly one experimental stage.
2. The stage writes non-secret `REPORT.md` + `result.json` and commits them.
3. ChatGPT reads the actual result before choosing any later stage.
4. ChatGPT updates the hypothesis tree, records the decision, and designs exactly one next bounded experiment.
5. The new workflow is pushed and GitHub Actions executes it.
6. Implementation failures are fixed and rerun under the same stage number before advancing.

No fixed multi-stage pipeline should replace the reasoning step between experiments.

## Adaptive review through Stage 30

### Stage 28
The Stage-27 L-bit0 traversal family looked significant against 100 block-shuffled surrogates:
- printable fraction p = 0.0099
- zlib ratio p = 0.0099
- printable-run length was not significant
- no specific multi-byte file signature survived

### Stage 29
The effect localized strongly in source-space columns. The same general behavior was also visible in higher grayscale bitplanes, already arguing against a bit-0-specific payload.

### Stage 30 — decisive source decomposition
Stage 30 split the fixed Stage-29 source clusters by semantic y-band and foreground/background pixels.

The apparent anomalies decompose almost completely into ordinary image structure:

- In the “printable” cluster, foreground-only streams are consistently about 0.36–0.38 printable, while background-only streams are about 0.000–0.016 printable.
- In the “compressible” cluster, foreground streams have zlib ratios around 1.0, while blank-background streams become extremely compressible (down to about 0.012).
- The same cluster behavior persists across grayscale bits 0–3 instead of being unique to bit 0.
- Therefore the Stage-28 p-values were driven by a null model that destroyed the image’s large-scale foreground/background layout. They are not evidence for a hidden traversal payload.

**Decision:** retire generic traversal-text/compressibility hunting as a primary carrier hypothesis. Stages 28–30 remain useful as a negative result explaining the earlier statistical anomaly.

## Current hypothesis ranking

1. **Format-invariant visual/semantic carrier — promoted.**
   The author explicitly said image format does not matter. This is difficult to reconcile with fragile exact-pixel LSB encoding. The robust 12-building H/V texture remains reproducible, although its former hexadecimal `0x321` reading stays retired.

2. **Raw low-bit / generic traversal carrier — downgraded strongly.**
   Global random-LSB replacement was already weakened by Stages 23–24, and the Stage-28/29 anomaly is now explained by ordinary spatial image structure in Stage 30.

3. **Alpha channel carrier — already exhausted / low priority.**
   Prior inspection found 434 non-opaque pixels localized to the large sailboat anti-aliasing halo, consistent with compositing rather than structured data.

4. **Human-readable visual semantics / solved-puzzle grammar — active.**
   The author’s solved puzzles favor visible secondary details, counting, rebuses, semantic references and ordered interpretation.

## Next stage

**Stage 31 — format-invariance audit of competing signal families.**

Question:
> Under lossy format conversion and resampling, does the robust H/V visual texture survive while exact low-bit structure collapses?

Pre-declared interpretation:
- If H/V classification remains stable across JPEG/resampling while foreground bit-0 agreement falls sharply, promote the visual-semantic route and further downgrade exact-pixel steganography.
- If a low-bit signature survives lossy transformations comparably well, revisit the assumption that the carrier requires exact source pixels.

## Status

- Stages 1–30: completed.
- Stage 30: COMPLETED + ADAPTIVELY REVIEWED.
- Generic traversal anomaly: RETIRED AS PRIMARY.
- Adaptive controller: manual while user is active.
- Next stage: 31.
