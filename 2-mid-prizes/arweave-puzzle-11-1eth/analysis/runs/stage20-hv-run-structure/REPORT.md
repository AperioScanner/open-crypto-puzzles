# Stage 20 — exact H/V run-structure audit

**Experiment:** A11-EXP-020

Observed sequence: `HHVVHHVHHHHV`
Observed run lengths: `[2, 2, 2, 1, 4, 1]` (6 runs; longest H=4, longest V=2).
Conditioned null: all 495 sequences with exactly 8 H and 4 V.

| metric | observed | exact tail probability |
|:---|---:|---:|
| run count (low = blockier) | 6 | 0.5333 |
| longest H run | 4 | 0.6869 |
| longest V run | 2 | 0.7455 |
| transition count (low = blockier) | 5 | 0.5333 |
| Hamming distance to reverse (low = symmetric) | 8 | 1.0000 |

- Composite blockiness probability (runs <= observed AND longest-H >= observed): **0.4788**
- Exact same run-length pattern count: **1/495 = 0.0020**

## Interpretation

The H/V sequence is not unusually blocky under the composition-conditioned null. This weakens the idea that the arrangement itself carries an obvious low-complexity code; the robust orientation pattern may still be deliberate, but its run structure is not exceptional.

This stage deliberately ignores the 0x321 representation and tests only the H/V arrangement itself.
