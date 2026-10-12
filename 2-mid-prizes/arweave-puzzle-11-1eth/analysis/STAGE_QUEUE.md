# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-11

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through corrected Stage 99

Stage 99 initially failed its Puzzle #9 APRIL control for a parsing reason: OCR recovered strings such as `APRILANDTHECLOCKSWER`, but the harness required `APRIL` as a standalone token. The control logic was fixed under the same stage number to accept the known anchor as a substring inside a recovered OCR word.

### Valid Stage-99 result

Positive controls:
- Puzzle #9 APRIL: **PASS** in all 3 original and all 3 lossy preprocessing paths.
- Puzzle #9 numeric `12:05.04`: **PASS** in all 3 original and all 3 lossy paths.

Puzzle #11 short OCR candidates meeting the Stage-99 region-level replication rule:
- **SSS** — strongest: 11 original paths, 9 lossy paths, 0 shuffled occurrences.
- **EAE** — 7 original, 9 lossy, 3 shuffled.
- **BEE** — 2 original, 3 lossy, 6 shuffled.
- **IES** — 2 original, 3 lossy, 2 shuffled.

### Hypothesis decision

Stage 99 **promotes only a localization question**, not readable plaintext.

The current rule proves that a token can recur within the same semantic region/rotation, but it does **not** prove that independent OCR paths are reading the **same physical glyph location**. Line art can generate repeated OCR hallucinations at different places.

Therefore:
- `SSS` is the strongest candidate because it has zero shuffled occurrences.
- `EAE` is weaker.
- `BEE` and `IES` are weak because the same tokens are common in shuffled controls.
- none is accepted as intended text until spatial co-localization is demonstrated.

## Next stage

**Stage 100 — spatial localization and glyph-consistency audit of Stage-99 OCR survivors.**

Bounded scope:
1. Candidate set fixed in advance: `SSS`, `EAE`, `BEE`, `IES`.
2. Re-run Tesseract in TSV/bounding-box mode on the exact Stage-99 region+rotation paths only.
3. Map every occurrence back to canonical Puzzle #11 coordinates.
4. Cluster occurrences by physical location.
5. Require a candidate to have:
   - the **same physical box/location** in at least 2 original preprocessing transforms;
   - a matching lossy occurrence at the same location;
   - center displacement <= 18 px after canonical mapping;
   - substantial box overlap or size agreement;
   - no equally persistent co-localized occurrence in matched shuffled controls.
6. Validate localization using Puzzle #9 APRIL and `12:05.04` crops.
7. Save only small diagnostic crops around co-localized short tokens; never save long OCR strings or key-shaped output.
8. Rank survivors by spatial replication + OCR confidence + crop correlation.

A candidate that fails co-localization is retired as OCR hallucination. A candidate that survives becomes eligible for direct visual inspection/rebus interpretation in the next adaptive stage.

## Status

- Stages 1–99: completed.
- Corrected Stage 99: COMPLETED + REVIEWED — four short OCR localization leads, no plaintext conclusion.
- Stage 100: selected for launch.
