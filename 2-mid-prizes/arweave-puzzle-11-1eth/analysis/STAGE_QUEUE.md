# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-12

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through Stage 117

Stage 117 completed successfully. Both source/schema and synthetic controls passed.

### Stage-117 result

The strict Stage-116 inspiration grammar had three operations:
- visible_text_or_symbol_reading
- ordering_or_traversal
- cross_domain_conversion

Testing those against Tiamat's own solved Arweave puzzles leaves only two recurrent author-series operations:

1. **cross_domain_conversion**
   - 15 supporting mechanisms
   - appears in solved puzzles 5, 7 and 8
2. **visible_text_or_symbol_reading**
   - 6 supporting mechanisms
   - appears in solved puzzles 5 and 7

`ordering_or_traversal` appears in only one solved puzzle and is not promoted.

Decision: **AUTHOR_SERIES_INTERSECTION**.

### Hypothesis decision

This is genuinely new independent evidence. It permits one narrowly predeclared revisit of a previously observed visible symbol family, but not generic H/V mining.

The 12 building interiors form the stable visible binary sequence `HHVVHHVHHHHV`. Twelve binary symbols have an exact, standard human-readable cross-domain fit to **two 6-dot Braille cells**. Braille has not previously been tested in the repository.

This exact dimensional fit plus Stage-117's recurrent visible-symbol + cross-domain prior satisfies the anti-recycling exception for one bounded test.

## Next stage

**Stage 118 — exact two-cell Braille audit of the 12 building H/V sequence.**

Bounded design:
1. Fixed sequence: `HHVVHHVHHHHV`; do not alter/re-segment buildings.
2. Standard Braille dot numbering only (1,2,3,4,5,6).
3. Exactly four predeclared readings:
   - left→right, H=raised
   - left→right, V=raised
   - right→left, H=raised
   - right→left, V=raised
4. Split only as 6+6; no sliding windows.
5. Positive control encodes/decodes two known Braille letters.
6. Null calibration enumerates all 12-bit strings with the same H/V counts as the observed sequence.
7. Promotion requires:
   - both cells decode to standard alphabetic Braille letters in a predeclared reading;
   - the all-letter outcome is familywise exceptional under the count-matched null (p<=0.05).

If no reading produces two letters, or the result is not exceptional, retire standard two-cell Braille. Do not expand to arbitrary binary alphabets after a negative.

No private-key material is generated or tested.

## Status

- Stages 1–117: completed and reviewed.
- Stage 117: VALID AUTHOR-SERIES PRIOR — cross-domain conversion + visible symbol reading.
- Stage 118: selected for launch.
