# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through Stage 98

Stage 98 completed successfully, but its automatic term classifier produced one false semantic promotion:

- it promoted **"order"** from the archived tweet:
  > "The list of unsolved #Arweave puzzles ordered by difficulty probably looks like: 3, 9, 8, 5, 7"

That tweet is plainly about **ranking puzzles by difficulty**, not a solve instruction for Puzzle #9.

### Corrected Stage-98 conclusion

- primary statuses parsed: **10**
- four-step / brute-force context: independently confirmed
- concrete Puzzle #9 mechanism terms recovered from the surrounding primary thread: **0**
- automatic `order` promotion: **REJECTED AS CONTEXTUAL FALSE POSITIVE**
- decision: **NO_NEW_MECHANISM**

Therefore do not invent a Puzzle #9 solution from the birds, quote, timestamp, or the word "order".

### Important side result

Stage 98 also re-confirmed several primary Puzzle #11 statements in archived Twitter:
- "format does not matter"
- "the private key is hidden in the image"
- the public escrow address is also included somewhere in the image
- the "weird image in your email account" storage analogy

These are already known and remain active constraints, not new hypotheses.

## Next stage

**Stage 99 — whole-image visible alphanumeric/rebus audit.**

Motivation:
- Puzzle #9 contains overt robust text/numeric anchors.
- Solved siblings and Stage 11 favor human-readable semantic anchors and secondary details.
- Puzzle #11 has never had a systematic whole-image OCR-style audit across the major semantic regions and simple cardinal rotations.
- Stage 36 only audited visual reveal structure in the large sailboat and deliberately did **not** perform OCR.

Bounded design:
1. Fixed Puzzle #11 regions:
   - full image
   - skyline
   - large sailboat
   - small-sails/jetty
   - lower water
2. Fixed transforms:
   - grayscale original
   - Otsu threshold
   - adaptive threshold
3. Fixed rotations: **0°, 90°, 180°, 270°** only.
4. Run Tesseract sparse-text OCR on:
   - canonical PNG
   - JPEG85 + resize roundtrip
5. Positive controls:
   - Puzzle #9 quote crop must recover `APRIL`
   - Puzzle #9 numeric stamp must recover at least two of `12`, `05`, `04`
6. Negative control:
   - deterministic block-shuffled versions of the same Puzzle #11 regions.
7. Promotion requires a token/instruction fragment:
   - length 3–20;
   - repeated in at least 2 independent transform paths;
   - replicated after lossy conversion at the same region+rotation;
   - absent from matched shuffled controls.
8. Any 64-hex-like output is discarded and never persisted or treated as a key candidate.

A null result retires straightforward visible alphanumeric/OCR-readable anchors, not visual rebuses or non-text semantics.

## Status

- Stages 1–98: completed.
- Stage 98: COMPLETED + REVIEWED — no mechanism-specific primary thread clue.
- Stage 99: selected for launch.
- Hourly controller: re-enabled.
