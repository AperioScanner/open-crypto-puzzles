# Arweave Puzzle #11 — adaptive stage controller

Last updated: 2026-10-03

## Control loop

1. GitHub Actions executes exactly one experiment.
2. The stage commits non-secret `REPORT.md` + `result.json`.
3. ChatGPT reads the actual result before choosing the next experiment.
4. ChatGPT updates the hypothesis tree and designs exactly one next bounded stage.
5. Implementation failures are fixed under the same stage number before advancing.

## Adaptive review through Stage 34

### Stage 31 — route selection
Visible H/V texture survives lossy conversion/resampling at 12/12 under two independent classifiers while exact low-bit identity collapses near chance.

### Stages 32–33 — uniform public-address tilings: negative
Both natural equal-width address mappings were rejected after familywise calibration:
- 160 address bits × 10 px
- 40 address hex digits × 40 px

### Stage 34 — H/V selector × secondary building details: negative
The fixed H/V labels were tested against pre-existing Stage-12 detail measurements using all 495 possible four-V assignments.

- small-component density p = **0.4101**
- component-instability p = **0.4465**
- mid-component density p = **0.9071**
- perimeter occupancy p = **0.3475**
- multivariate exact p = **0.7010**

**Decision:** H/V remains a real, format-stable visual pattern, but the hypothesis that it selects a second counted/detail channel inside the buildings is downgraded.

## Current hypothesis ranking

1. **Format-invariant scene/object semantics — highest priority.**
2. **Robust H/V building texture — active as a standalone clue/instruction; not supported as a selector of building-detail counts.**
3. **Scene context: water/reflection/mirroring — promoted for direct testing.**
4. **Solved-puzzle grammar: rebuses, secondary details, selection, ordering and environment — active prior.**
5. **Known public address as positive probe — active, but equal-cell mappings retired.**
6. **Raw low-bit / generic traversal / alpha — downgraded or exhausted.**

## Next stage

**Stage 35 — building ↔ water-reflection orientation coupling audit.**

Motivation:
- the drawing is explicitly organized as a skyline above water with visible reflection strokes directly beneath it;
- mirroring/reflection is human-readable and format-invariant;
- Stage 11 shows that overall scene context/environment can participate in the author's clue grammar;
- Stage 34 says H/V does not simply select counted details inside buildings, so a scene-level relation is the next justified use of the H/V clue.

Bounded test:
- use buildings **3–12 only**; buildings 1–2 are excluded before analysis because the known large-sailboat bbox overlaps their below-skyline region;
- fixed reflection band: **y=330..360**, ending before the small-sails band begins at y=360;
- use inner 10% of each building x-span to reduce cross-building contamination;
- measure reflection orientation continuously with two independent methods: Sobel gradient anisotropy and Fourier anisotropy;
- test whether V buildings have more vertical-oriented reflection signal than H buildings using exact enumeration of all **210** four-V assignments among 10 eligible buildings;
- Bonferroni-correct the two methods;
- repeat the fixed test after JPEG85 + resize roundtrip and require the sign/order of the association to reproduce.

A positive result would promote H/V as a scene-level relation. A negative result would keep H/V as a standalone clue but retire the straightforward building-to-reflection coupling hypothesis.

## Status

- Stages 1–34: completed.
- Stage 34: COMPLETED + ADAPTIVELY REVIEWED — NEGATIVE.
- H/V-as-detail-selector: DOWNGRADED.
- Adaptive controller: manual while user is active.
- Next stage: 35.
