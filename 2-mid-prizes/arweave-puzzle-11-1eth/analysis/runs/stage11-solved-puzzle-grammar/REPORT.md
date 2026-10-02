# Stage 11 — solved-puzzle design grammar

**Experiment:** A11-EXP-011

This is public-source, non-cryptographic research. It does not generate, derive, reconstruct, enumerate, or verify private-key candidates.

## Why this stage exists

While discussing Puzzle #11 on 2020-04-23, the author explicitly told a solver to look at the solved puzzles. The same public archive also preserves the #11 hints that format does not matter and that the image demonstrates an alternative way of storing a private key. The goal here is therefore to learn the author's clue-design habits rather than continue treating every pixel transform as equally likely.

## Recovered solved-puzzle grammar

| puzzle | public solved token | mechanism | design lesson |
|---:|:---|:---|:---|
| #5 | * | medium-translation | translate a familiar mark between physical and technical contexts |
| #5 | 48 | small-detail-counting | count small visual sub-elements rather than naming the main object |
| #5 | GCE | cultural-reference | a picture can point to an external cultural reference and then a compact token |
| #5 | Eris | symbol-identification | identify an exact symbol rather than use a generic visual label |
| #5 | Umber | franchise-reference | external fictional context can disambiguate an otherwise generic drawing |
| #5 | Castle | secondary-detail-rebus | the intended clue can be a secondary drawn detail, not the dominant object |
| #5 | Picasso | art-reference | visual resemblance can encode the creator/title, not the literal object |
| #7 | Vivaldi | cultural-reference | combine image semantics with a small textual constraint |
| #7 | 227 | reference-to-number | semantic identification can terminate in a number rather than a word |
| #7 | Permanent | technical-context | overall platform/environment can be part of the clue |
| #7 | Arnheim | literature-reference | literature and named works are recurring disambiguators |
| #7 | Bulgakov | literature-reference | the final token can be one semantic hop away from the pictured/hinted entity |
| #7 | 1157 | sequence-pattern | a visible numeric sequence can encode a rule and demand continuation |
| #7 | Ulysses | cross-domain-reference | apparently unrelated visual details can point to a named cultural object |
| #7 | 143176176209 | visual-number-extraction | literal numeric extraction is used when the image supplies a structured numeric cue |
| #8 | Rasputin | biographical-rebus | identify the famous person implied by a narrative scene |
| #8 | Wilhelm | biographical-rebus | historical biography may supply the intended compact name |
| #8 | Alekhine | biographical-rebus | recognition of a person from contextual facts can be the entire mechanism |

## Mechanism counts

- biographical-rebus: 3
- cultural-reference: 2
- literature-reference: 2
- art-reference: 1
- cross-domain-reference: 1
- franchise-reference: 1
- medium-translation: 1
- reference-to-number: 1
- secondary-detail-rebus: 1
- sequence-pattern: 1
- small-detail-counting: 1
- symbol-identification: 1
- technical-context: 1
- visual-number-extraction: 1

- Broadly semantic/contextual examples: **14**
- Counting/sequence/numeric-extraction examples: **4**

## Implications for Puzzle #11

1. **Treat 321 first as a human-readable instruction/semantic clue, not as raw payload.** — Solved examples are dominated by semantic rebuses, contextual interpretation, and tiny deliberate visual details.
2. **Inspect secondary details around buildings and boats, not only dominant skyline shapes.** — Puzzle #5 Castle came from tiny O-O marks on a log; #5 also used grass-blade counting.
3. **Test order, count, perimeter, and environment readings of 3-2-1.** — The author repeatedly used ordering, counting, perimeter, visual context, and overall-environment hints in the series.
4. **Prefer clues that survive re-encoding and remain human-visible.** — For #11 the author said format does not matter; the stable hatch-direction marker survives ordinary visual perturbation.

## Working conclusion

The solved-sibling evidence materially shifts the research priority toward human-readable semantics and deliberate secondary details. The robust skyline 0x321 marker should therefore be treated first as an instruction such as ordering, counting, or selection rather than as raw secret material. This does not prove that 321 is intentional; it defines the next bounded visual tests.

## Source checks

- PZL5: https://raw.githubusercontent.com/HomelessPhD/AR_Puzzles/main/PZL5/README.md — 7 explicit solved-value markers parsed.
- PZL7: https://raw.githubusercontent.com/HomelessPhD/AR_Puzzles/main/PZL7/README.md — 8 explicit solved-value markers parsed.
- PZL8: https://raw.githubusercontent.com/HomelessPhD/AR_Puzzles/main/PZL8/README.md — 0 explicit solved-value markers parsed.