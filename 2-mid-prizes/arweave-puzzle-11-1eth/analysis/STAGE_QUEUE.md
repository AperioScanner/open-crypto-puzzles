# Arweave Puzzle #11 — adaptive stage controller

Last updated: 2026-10-03

## Control loop

1. GitHub Actions executes exactly one experiment.
2. The stage commits non-secret `REPORT.md` + `result.json`.
3. ChatGPT reads the actual result before choosing the next experiment.
4. ChatGPT updates the hypothesis tree and designs exactly one next bounded stage.
5. Implementation failures are fixed under the same stage number before advancing.

## Adaptive review through Stage 35

### Stage 31 — route selection
The visible H/V structure remained 12/12 under two independent classifiers after JPEG/resampling while exact low-bit identity collapsed near chance. Visible/semantic mechanisms remain the preferred route.

### Stages 32–33 — equal-width public-address mappings: negative
Both natural uniform-width mappings were rejected after familywise calibration:
- 160 bits × 10 px
- 40 hexadecimal digits × 40 px

### Stage 34 — H/V as selector of building details: negative
All exact permutation tests were non-significant; multivariate p = 0.7010.

### Stage 35 — H/V ↔ reflection orientation coupling: negative
The direct scene-level relation also failed:
- Sobel V-H = **-0.0809**, one-sided p = **0.6762**
- Fourier V-H = **+0.1030**, one-sided p = **0.3571**
- the two methods do not even agree on direction
- lossy-format replication preserves the same weak/non-significant pattern

**Decision:** stop spending stages trying to make H/V explain another property. H/V remains a conspicuous, format-stable visual feature, but without independent corroboration it is now **secondary**, not the organizing hypothesis.

## New evidence review

The original community PZL11 dossier was re-read after the H/V branch stalled. It confirms the parent question behind the author's reply:
> “What's the photo format. It's not JPG!?” → “format does not matter”

So the format-invariance premise is correctly contextualized.

The same early dossier records a long-standing but never systematically resolved visual hypothesis: the **large sailboat may contain plain text / a hidden readable pattern inside its dense shading**. The community author experimented manually with histogram slices and wrote that zooming out made the boat look text-like, but did not establish a reproducible extraction.

This hypothesis fits:
- the author's “weird image” / steganography framing;
- file-format irrelevance better than PNG-only metadata tricks;
- the solved-puzzle grammar's emphasis on visible secondary details;
- the image composition, where the large sailboat is an unusually dense isolated object.

## Current hypothesis ranking

1. **Format-invariant hidden visual text / secondary pattern in a dense object — promoted.**
2. **Large sailboat as the highest-value region for a visual reveal audit — active.**
3. **General scene/object semantics — active.**
4. **H/V skyline texture — retained as secondary; stop forcing relations without new corroboration.**
5. **Known public address as positive probe — active but equal-width mappings retired.**
6. **Raw low-bit / generic traversal / alpha — downgraded or exhausted.**

## Next stage

**Stage 36 — large-sailboat multiscale visual-reveal audit.**

Bounded design:
- target region: the measured large-sailboat bbox from `geometry.json`;
- fixed controls of the same size from dense skyline, right-side boats/jetty, and water/line-art regions;
- predeclared visual transforms only: grayscale threshold sweep, narrow intensity-band masks, local-contrast enhancement, Difference-of-Gaussian residuals, and long-line suppression;
- generate a diagnostic contact sheet for direct visual review;
- compute a conservative “glyph-line” diagnostic from connected components (counts/alignment only) to rank transforms, not to decode text;
- repeat the same transform family after JPEG85 + resize roundtrip to distinguish visible structure from source-pixel accidents.

Stage 36 does **not** OCR, derive a key, or turn arbitrary pixel windows into private-key candidates. Its purpose is to determine whether the old “plain text/noised on the big boat” hypothesis deserves a narrower visual follow-up.

## Status

- Stages 1–35: completed.
- Stage 35: COMPLETED + ADAPTIVELY REVIEWED — NEGATIVE.
- H/V relational hypotheses: PAUSED.
- Adaptive controller: manual while user is active.
- Next stage: 36.
