# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-06

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through corrected Stage 95

The first Stage-95 implementation failed its own control validation because the synthetic 16-level positive control did not score above the Puzzle #5 drawing control. That run was not interpreted.

Stage 95 was repaired under the same number with a general 16-mode detector and three control classes:
- exact 16-shade synthetic positive;
- continuous-tone synthetic negative;
- solved Puzzle #5 as an author-style drawing control.

### Valid Stage-95 result

Control validation: **PASS**

Scores:
- synthetic positive: **0.838–1.000**
- continuous negative: **~0.468**
- Puzzle #5: **0.491–0.669**

All four fixed Puzzle #11 regions are rejected:
- whole foreground
- large sail
- skyline
- small-sails / jetty

No region was close to the positive control in any of the four image variants.

### Hypothesis decision

**Direct 16-gray-mode / one-tone-per-hex-symbol alphabet = RETIRED.**

## New independent evidence

A fresh public-source sweep surfaced an author statement about **Puzzle #9**, the closest solved sibling to #11:

- #9 was also a puzzle where everything needed was hidden in an image and the prize was Ethereum-side (100 DAI);
- #9 shared the same create-before-modify metadata anomaly already noted in #11;
- #9 was solved anonymously;
- on 2020-06-14, Tiamat wrote that **“The puzzle required 4 steps. My guess is the solver figured out 3 and brute forced one, that's why he is silent.”**

This exact 4-step statement is not present anywhere in the current #11 branch. It is therefore genuinely new independent evidence and satisfies the anti-recycling exception.

## Next stage

**Stage 96 — Puzzle #9 four-step sibling reconstruction audit.**

Goals:
1. Fetch the original #9 permaweb page at `1--NRFY3naNwTlxBSRjzDPNUq-Cn1yLG2RmgGHZem9c`.
2. Extract all embedded/linked image assets and identify the primary puzzle image(s).
3. Save only bounded diagnostic thumbnails/metadata needed for reproducible review.
4. Recover the 2020-06-14 author tweet through Internet Archive CDX/Wayback if possible and verify the exact “4 steps / brute forced one” wording and thread context.
5. Characterize #9's page/image construction and compare mechanism-level traits with #11:
   - image mode/channels/dimensions;
   - PNG chunks / date metadata;
   - alpha behavior;
   - first-row anomalies;
   - grayscale quantization / bitplane statistics;
   - visible line/region organization.
6. Identify which of the four conceptual steps can be inferred from #9 **without** generating or checking any private-key candidate.
7. Produce a ranked set of **new mechanism constraints** for #11, explicitly separating:
   - shared production artifacts;
   - likely selection/ordering steps;
   - the one step that may have been brute-forced.

No private-key derivation or wallet access is performed.

## Status

- Stages 1–95: completed.
- Corrected Stage 95: COMPLETED + REVIEWED — 16-level grayscale alphabet retired.
- New Puzzle #9 author evidence: PROMOTED.
- Stage 96: selected for launch.
