# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-12

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through corrected Stage 112

Stage 112 required repair before interpretation.

The first Stage-112 implementation was invalid because:
- the synthetic positive edge control failed;
- the first two real sails returned no width.

The estimator was repaired under the **same stage number**:
- real widths now come from center-anchored vertical-support projections;
- thin Canny traces are joined before the edge projection;
- positive and negative synthetic controls now behave correctly.

### Valid Stage-112 result

True right-hand sail centers are stable:
`[1042, 1148, 1282, 1372, 1490]`, max lossy drift **2 px**.

Synthetic controls: **PASS**.

Real median profiles:
- mask: **[24, 49, 65, 60, 64]**
- edge: **[31, 53, 64, 54.5, 75.5]**

First-three arithmetic-progression test:
- mask steps: **+25, +16**, AP error **9**
- edge steps: **+22, +11**, AP error **11**
- fixed-order permutation p: **0.20 / 0.20**
- Stage-18 qualitative profile: **not reproduced**
- promotion: **False**

### Hypothesis decision

**Stage-18 +26,+26 five-sail width progression = RETIRED.**

The earlier exact progression came from an unreliable object/measurement association and does not reproduce on the corrected true five-sail set with validated independent estimators.

## Next stage

**Stage 113 — 64 × 25 px full-width visual-cell carrier audit.**

Motivation:
- the target raw private key is conventionally represented as **64 hexadecimal characters**;
- the source image width is exactly **1600 px = 64 × 25 px**;
- Stage 32 tested 160 public-address bits × 10 px and Stage 33 tested 40 public-address hex digits × 40 px;
- no prior stage tests the exact private-key dimensional relation **64 cells × 25 px**;
- this is compatible with the author's format-invariant visual-storage hint.

Safe bounded design:
1. Partition the image into 64 vertical cells of exactly 25 px at phase 0.
2. Extract only coarse format-invariant per-cell visual features: ink fractions, edge density, horizontal/vertical gradient balance, low-frequency vertical centroid and connected-component density.
3. Test whether the 64 cells behave like a discrete **16-state alphabet** without outputting any ordered symbol sequence.
4. Compare original, JPEG85, JPEG70 and 0.75× resize roundtrip.
5. Phase control: repeat the exact analysis for all 25 possible x phases (0..24) using circular wrapping. If 25-px cells are intended, phase 0 should be exceptional.
6. Positive synthetic control: aligned 64-cell image built from 16 repeated visual states; phase 0 must rank first and k=16 assignments must be stable under lossy variants.
7. Negative synthetic control: 64 continuous/random visual states must not spuriously promote k=16.
8. Promotion requires:
   - both control families pass;
   - k=16 cross-variant cluster stability >=0.90;
   - >=12/16 states occupied with no pathological singleton domination;
   - phase 0 ranks #1 among 25 phases for the predeclared score;
   - k=16 is preferred or effectively tied for best over k=2..20.

**Safety guard:** do not persist, print, reconstruct or verify the ordered 64-symbol class sequence. This stage tests carrier structure/capacity only.

## Status

- Stages 1–112: completed and reviewed.
- Stage 112: VALID NEGATIVE — corrected five-sail width progression retired.
- Stage 113: selected for launch.
