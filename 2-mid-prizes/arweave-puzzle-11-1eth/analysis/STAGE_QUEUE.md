# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-06

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through corrected Stage 93

Stage 93 required two implementation repairs under the same stage number:
- OpenCV 5 returns HoughLinesP output as (N,4) in this runner, not always (N,1,4);
- the first X/IX/XI scorer mathematically prevented IX/XI composites from outranking bare X, and its synthetic IX/XI controls failed.

Both defects were fixed before interpretation.

### Valid Stage-93 result

- all synthetic X / IX / XI controls: **PASS**
- original dominant template: **IX**, 4/5 detector configurations
- lossy dominant template: **IX**, 3/5 configurations
- target family-best score: **0.8741**
- matched-window median: **0.8534**
- matched-window maximum: **0.9857**
- familywise empirical p: **0.4107**
- promotion: **False**

The pier really can look Roman-like, and that appearance survives lossy conversion, but it is **not unusual** relative to other line-rich regions of the same drawing.

### Hypothesis decision

**Pier X / IX / XI = RETIRED.**

This closes the last genuinely untested historical visual claim identified in corrected Stage 91.

## New mechanism family

With the historical clue backlog exhausted, move back to mechanism discovery rather than recycling old solver ideas.

The strongest surviving constraints are:
- author: **format does not matter**;
- author: the **private key is hidden in the image**;
- Stage 31: macroscopic line/orientation structure survives JPEG/resampling while exact low bits collapse;
- the artwork is explicitly a hand-drawn stroke image;
- Stage 3 exhausted exact alpha-marked grayscale/bitstream/crop-hash candidates;
- Stage 36 rejected hidden readable text in the large sailboat;
- neither stage tested a **format-invariant discrete stroke-orientation carrier**.

## Next stage

**Stage 94 — large-sail stroke-orientation carrier-capacity audit.**

Question:
> Does the large sail contain a robust, naturally discrete set of visible strokes whose count and binary orientation structure are compatible with storing a 64-hex / 256-bit key, without relying on exact pixels?

Bounded design:
1. Fixed triangular sail-interior mask derived from the existing large-sailboat bbox; hull excluded.
2. Skeletonize visible ink at several fixed grayscale thresholds.
3. Detect/deduplicate long stroke centerlines and track them across thresholds.
4. Repeat on original, JPEG85, JPEG70, and 0.75x down/up variants.
5. Measure only non-secret carrier properties:
   - number of stable stroke tracks;
   - robustness of the count;
   - two-orientation separability/balance;
   - cross-variant stroke agreement.
6. Compare stable count against the only two canonical representation sizes justified in advance: **64 visible hex symbols** or **256 binary symbols**.
7. Use a synthetic 64-stroke two-orientation sail as a positive detector control.
8. Do **not** persist or print the target sail's ordered binary orientation sequence.

Promotion requires a stable count close to 64 or 256 across variants plus strong two-class orientation structure. Otherwise retire this carrier family.

## Status

- Stages 1–93: completed.
- Corrected Stage 93: COMPLETED + REVIEWED — Roman hypothesis retired.
- Historical solver-clue backlog: exhausted.
- Stage 94: selected for launch.
