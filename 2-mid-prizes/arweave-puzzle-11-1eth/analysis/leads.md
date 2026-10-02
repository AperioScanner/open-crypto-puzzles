# Open leads, ranked

## 1. Interpret the robust skyline `0x321` marker as an instruction (active, visual-only)

The 12 building interiors form the stable H/V sequence `HHVVHHVHHHHV`; with H=0 and V=1 this is exactly `0011 0010 0001 = 0x321`. A11-EXP-010 tested whether this was caused by exact crop choices: all nine inner-margin choices preserved it, as did 100% of bounded perturbations through ±8 px; even at ±16 px, 85% of 400 full-sequence trials remained exact. This makes `321` a materially stronger clue than a one-off classifier artifact. The open question is semantic: what did the author expect a human solver to do with “3-2-1”? Stage 6 already tested the most literal bit-plane reading; future work should focus on human-readable instructions and image structure, not candidate-key generation.

## 2. Reconstruct the solved-puzzle design grammar (active, public-source research)

On 2020-04-23, while discussing #11, the author explicitly told a solver: “Look at the solved puzzles. If solutions make sense to you, you are good to go.” Surviving write-ups for solved #5, #7 and #8 show a recurring style: ordered visual rebuses, tiny but deliberate drawn details, cross-domain cultural references, counting, and occasional technical/page-context clues. Examples include #5’s drawn “O-O” resolving to the chess term Castle, and #7 mixing literature, numbers and visual/technical context. The next task is to build a compact mechanism inventory for solved siblings (#1/#2/#5/#7/#8) and test whether #11’s skyline, boats, watermark, hatching, object counts, or spatial order instantiate the same classes of clue.

## 3. Non-key `3-2-1` image diagnostics (active, bounded)

Stage 6 rendered the relevant grayscale bit planes and several 3-2-1 composites, but its main decision criterion was cryptographic. Revisit these views only as images: look for text-like strokes, repeated symbols, grids, ordering marks, or regions whose structure survives ordinary re-encoding. This lead is confirmed only by a reproducible visual structure, not by a private-key/address test.

## 4. Recover first-hand author/community context around #11 and #9 (needs archival evidence)

The public @ArweaveP archive recovered several strong contemporaneous clues: “format does not matter,” “the private key is hidden in the image,” “alternative forms of storing a private key,” and the instruction to look at solved puzzles. What remains is early Telegram/Discord/Weavemail material outside the later archive window, deleted replies, or a first-hand account of puzzle #9’s actual solve method.

## 5. Puzzle #9's real solving method, if it surfaces (standing watch)

#9 is the best sibling control because the author described it as related and it was solved in 2020 without a published method. A real write-up could reveal the intended visual grammar or construction technique. This is a standing information lead, not an active brute-force task.
