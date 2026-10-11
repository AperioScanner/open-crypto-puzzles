# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-10

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through corrected Stage 97

Stage 97 first failed on an undefined variant-name constant; fixed under the same stage number.

A second review found two measurement/source issues:
- the green bird's dominant hue shifted only **2 / 180 hue units** after lossy transforms but crossed an arbitrary categorical green/yellow boundary;
- Medium returned HTTP 403 to the GitHub runner, so the official newsletter phrase could not be captured inside the Action artifact.

The bird stability test was corrected to use circular dominant-hue drift rather than brittle category boundaries. The official newsletter statement was separately verified from the public indexed article outside the runner.

### Valid Stage-97 evidence

**Primary author quote: VERIFIED.**

Wayback recovered the 2020-06-14 Twitter page for status `1272111084867129344`. Its archived HTML title contains:

> "The puzzle required 4 steps. My guess is the solver figured out 3 and brute forced one, that's why he is silent."

The exact statement is also independently preserved in two public crypto-puzzle dossiers with the same status ID and #9 context.

**Official Puzzle #9 context: VERIFIED externally.**

Arweave's January 2020 newsletter states that Puzzle #9 was different from earlier puzzles and that **everything needed to crack the code is hidden in the image**. The GitHub runner received 403 from Medium, but the public indexed page remains available and matches the official Arweave announcement context.

**Visible #9 anchors: robust.**
- Orwell/1984 quote crop: JPEG85 edge corr 0.974, JPEG70 0.967, resize 0.827.
- numeric `12:05.04` crop: 0.954 / 0.935 / 0.873.
- five bird colors are distinct in the source image and their dominant hues move by only 0–2 units after the tested re-encodings.

### Hypothesis decision

Promote only the following prior:

> **Puzzle #9 was an image-only, multi-step puzzle with multiple robust visible semantic/numeric anchors.**

Do **not** infer that:
- the four solve steps equal four visible objects;
- every visible anchor participated in the solve;
- Puzzle #11 uses the same concrete objects/colors.

This is mechanism-level evidence, not a recovered #9 solution.

## Next stage

**Stage 98 — Puzzle #9 primary Twitter thread reconstruction.**

Reason:
The four-step statement is now primary-verified. The highest-value next question is whether the surrounding contemporaneous author/solver thread reveals *what any of the four steps were*, rather than inventing a four-step mapping ourselves.

Bounded goals:
1. Use the verified Wayback snapshot of status `1272111084867129344` as seed.
2. Parse old-Twitter HTML for conversation ID, in-reply-to status, quoted status and neighboring status links.
3. Query Wayback CDX for @ArweaveP status pages during **2020-06-08..2020-06-15**, the week around the #9 sweep.
4. Fetch a bounded set of archived status snapshots and extract:
   - status ID
   - author handle
   - timestamp where present
   - page title / tweet text
   - reply-parent relationships
5. Follow only status links reachable from the seed or matching mechanism terms (`puzzle`, `solver`, `brute`, `step`, `bird`, `color`, `clock`, `April`, `1984`, `12:05.04`), max 40 statuses.
6. Cross-check the two public dossiers for quoted neighboring statuses/participants.
7. Classify recovered evidence:
   - **MECHANISM_SPECIFIC_PRIMARY**
   - **SOLVE_CONTEXT_PRIMARY**
   - **SECONDARY_CONTEXT**
   - **NO_NEW_MECHANISM**
8. Promote a mechanism term only if it appears in primary archived author/solver material, not merely in our interpretation of the image.

No private-key candidates or wallet operations are performed.

## Status

- Stages 1–97: completed.
- Corrected Stage 97: COMPLETED + REVIEWED.
- Puzzle #9 four-step statement: PRIMARY_VERIFIED.
- Puzzle #9 multi-step/image-only prior: PROMOTED.
- Stage 98: selected for launch.
