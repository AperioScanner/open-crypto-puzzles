# Arweave Puzzle #11 — adaptive stage controller

Last updated: 2026-10-03

## Control loop

1. GitHub Actions executes exactly one experiment.
2. The stage commits non-secret `REPORT.md` + `result.json`.
3. ChatGPT reads the actual result before choosing the next experiment.
4. ChatGPT updates the hypothesis tree and designs exactly one next bounded stage.
5. Implementation failures are fixed under the same stage number before advancing.

## Adaptive review through Stage 33

### Stage 31 — route selection
The visible H/V structure remained **12/12** under two independent classifiers through JPEG/resampling while exact foreground bit-0 identity collapsed to ~0.52–0.55.

**Decision:** prioritize format-invariant visible/semantic mechanisms.

### Stage 32 — 160×10px address-bit stripes: negative
Best Hamming distance was 66/160 with familywise p=0.40953.

### Stage 33 — 40×40px address-hex cells: negative
The more human-readable dimensional mapping `1600 px = 40 address hex digits × 40 px` also failed:

- best exact hex-digit matches: **9/40**
- familywise p(exact): **0.08519**
- nibble-bit Hamming: **67/160**
- familywise p(bit-Hamming): **0.95830**
- extracted coarse digits were format-stable (38/40) but their match to the public address was not exceptional

**Decision:** retire uniform-width address tilings as a primary visual hypothesis. The known public address remains a useful positive probe, but there is no evidence that the image width is partitioned directly into its bits or hex digits.

## Current hypothesis ranking

1. **Format-invariant object/semantic encoding — highest priority.**
2. **Robust H/V building texture — strongest specific visual clue; interpretation unresolved.**
3. **Solved-puzzle grammar: secondary details, counts, selection and ordering — promoted.**
4. **Known public address as positive probe — active, but uniform width mappings retired.**
5. **Raw low-bit / generic traversal / alpha — downgraded or exhausted.**

## Next stage

**Stage 34 — H/V selector × secondary-detail association audit.**

Motivation:
- Stage 11 showed that the author's solved puzzles frequently use small secondary details and counting;
- Stage 12 already measured secondary-detail counts and perimeter statistics for all 12 buildings;
- Stage 21 proved the H/V label sequence is robust and classifier-independent;
- Stage 17 showed simple building geometry does not explain the H/V labels.

Question:
> Do the four V-labeled buildings and eight H-labeled buildings also separate on independent secondary-detail measurements, as would be expected if H/V acts as a deliberate selector/class label rather than merely decorative hatching?

Bounded test:
- reuse Stage-12 measurements only; do not invent new visual features after seeing results;
- exclude projection-periodicity metrics because they are directly entangled with H/V texture orientation;
- normalize component counts by crop area;
- test small-component density, mid-component density, threshold stability and perimeter occupancy;
- enumerate all 495 possible placements of four V labels among 12 buildings for exact permutation p-values;
- compute both per-feature tests and one multivariate within-class clustering statistic;
- Bonferroni-correct the per-feature family.

A strong, multi-feature association would promote H/V as a selector that should guide object-level decoding. A null result would keep H/V as a real visual pattern but downgrade the idea that it organizes secondary-detail content.

## Status

- Stages 1–33: completed.
- Stage 33: COMPLETED + ADAPTIVELY REVIEWED — NEGATIVE.
- Uniform bit/hex width partitions: RETIRED.
- Adaptive controller: manual while user is active.
- Next stage: 34.
