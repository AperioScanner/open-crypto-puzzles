# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-06

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through calibrated Stage 94

The first Stage-94 result exposed a calibration issue: its 64-stroke synthetic control was detected as only 48 strokes, while the target-count gate assumed near-perfect recovery. That made a direct 64-vs-target count conclusion too strong.

Stage 94 was therefore repaired under the same number with high-density synthetic controls at **16, 32, 64, 128 and 256** strokes and wide detector-calibrated compatibility bounds.

### Valid Stage-94 result

Target large-sail detector response across original/lossy variants:
- **10, 13, 12, 14** classifiable stable tracks.

Synthetic controls:
- 16 drawn → **12–14** detected
- 32 drawn → **22–27**
- 64 drawn → **45–52**
- 128 drawn → **49–68**
- 256 drawn → **53–70**

The detector saturates at high density, but this does not rescue the target: even under deliberately wide calibrated bounds, the real sail's 10–14 tracks are far below both canonical carrier families.

Other target properties:
- two-orientation structure: PASS
- cross-format matched-sign stability: PASS
- 64 one-stroke-per-symbol count compatibility: **REJECTED**
- 256 one-stroke-per-symbol count compatibility: **REJECTED**

### Hypothesis decision

**Large-sail one-stroke-per-symbol carrier (64 hex symbols or 256 binary symbols) = RETIRED.**

This does not reject every grayscale/stroke encoding. It rejects the specific hypothesis that each visible stable sail stroke is one key symbol/bit.

## Next stage

**Stage 95 — 16-level grayscale-alphabet audit.**

Motivation:
- Puzzle #11 is natively **8-bit grayscale+alpha**, unlike the more ordinary color/photo presentation of several solved siblings.
- A 64-character hexadecimal private key has a natural **16-symbol alphabet**.
- Prior stages tested bitplanes, alpha-marked grayscale sequences, crop hashes, hidden text and stroke orientation; they did **not** test whether visible foreground tone itself forms a robust 16-level symbol alphabet.

Bounded design:
1. Fixed regions:
   - whole-image foreground
   - large-sail interior
   - skyline/building band
   - small-sails/jetty band
2. Evaluate only foreground grayscale samples (`gray < 245`).
3. Fit a predeclared 16-level affine intensity lattice and measure normalized residual, level occupancy and per-level support.
4. Independently fit 16 one-dimensional clusters and measure separation/within-cluster compactness.
5. Repeat after JPEG85, JPEG70 and 0.75x resize roundtrip.
6. Use synthetic 16-shade line-art controls.
7. Use the solved hand-drawn Puzzle #5 image as an author-style drawing control so ordinary antialiasing/pencil-like rasterization is not mistaken for an encoded alphabet.
8. Do not map levels to hex digits or construct a key candidate.

Promotion requires a strong 16-level structure in Puzzle #11 that survives lossy transforms, passes synthetic controls, and is materially stronger than the sibling-drawing control.

## Status

- Stages 1–94: completed.
- Calibrated Stage 94: COMPLETED + REVIEWED — negative for one-stroke-per-symbol sail carrier.
- Stage 95: selected for launch.
