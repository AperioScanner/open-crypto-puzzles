# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-12

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless:
1. a concrete implementation defect is demonstrated; or
2. genuinely new independent evidence changes the hypothesis.

## Review through corrected Stage 114

The first Stage-114 run failed source recovery because GitHub-hosted runners received HTTP 403 from Reddit and no Wayback CDX rows. That was an implementation/source-access failure, not a negative result.

Stage 114 was repaired under the **same stage number** using a bounded, controller-verified snapshot of the canonical Reddit page. The snapshot stores only public mechanism-relevant comments with stable Reddit comment IDs and the canonical post metadata.

### Valid Stage-114 result

Source controls:
- canonical Reddit thread recovered: **PASS**
- title: **"100 DAI hidden in this image"**
- OP: **webgene**
- Arweave Puzzle #9 link: **PASS**
- mechanism-relevant public comments recovered: **8**
- pre-solve / post-solve: **7 / 1**

Evidence classification:
- mechanism-specific OP/author replies: **0**
- independently corroborated community solve paths: **0**
- decision: **NO_CORROBORATED_MECHANISM**
- promotion: **False**

The thread preserves useful contemporaneous speculation (date/time, birds, Orwell, angles/lines, LSB), but none may be treated as a Puzzle #9 step.

## New author-specific evidence family

The 2019-10-10 official Arweave interview **Community Spotlight: Meeting Tiamat** contains a primary statement from Tiamat that he liked tangible puzzles (e.g. Hanayama), then **saw a Bitcoin puzzle on Reddit** and realized the permaweb was a good immutable place to store puzzles.

Because Tiamat's Arweave puzzle series had already started by late May 2019, the inspiring Reddit Bitcoin puzzle must predate the series launch.

A bounded candidate audit found two especially relevant pre-launch Reddit image puzzles from May 2018:
1. r/Bitcoin `8kk0pa` — **"1 BTC is hidden in this puzzle. Good luck!"**
2. r/Bitcoin `8krbd3` — **"*Prize inside* 2.5mBTC. Private key in puzzle."**

Later 2019 image/private-key puzzles are chronologically incapable of being the original inspiration.

## Next stage

**Stage 115 — Tiamat Reddit-inspiration candidate audit.**

Question:
> Can primary chronology and puzzle-construction features narrow the unnamed Bitcoin Reddit puzzle that inspired Tiamat, and if not, what mechanism traits are safe to transfer as a family prior?

Bounded design:
1. Validate the official interview date and wording from a checked public-source snapshot.
2. Use the first Arweave-puzzle publication date as a hard chronology cutoff.
3. Evaluate the fixed candidate set in `clues/tiamat-reddit-inspiration-candidates.json`.
4. Score only pre-cutoff candidates on predeclared construction traits:
   - image-based;
   - funded crypto reward;
   - direct key/wallet unlock;
   - multi-step;
   - visible semantic encoding;
   - brute-force ambiguity;
   - public hints/solution.
5. Post-launch candidates are excluded before scoring.
6. Promotion rules:
   - exact-inspiration identification requires one candidate to dominate all others by >=2 independent evidence points **and** have a direct link/mention by Tiamat; otherwise exact identity remains unresolved;
   - shared family traits may be promoted only if present in every top pre-launch candidate.
7. Do not infer any Puzzle #11 payload from a candidate-specific trick.

No private-key operations.

## Status

- Stages 1–114: completed and reviewed.
- Stage 114: VALID NEGATIVE — Reddit thread provides historical context but no corroborated solve path.
- Stage 115: selected for launch.
