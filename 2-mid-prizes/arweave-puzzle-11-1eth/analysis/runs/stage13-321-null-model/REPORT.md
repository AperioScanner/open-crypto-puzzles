# Stage 13 — 0x321 null-model significance

**Experiment:** A11-EXP-013

This stage asks a narrow question: how surprising is the robust 12-building H/V sequence if building orientations were otherwise random? It is statistical only and does not touch private-key material.

- Observed sequence: HHVVHHVHHHHV
- Binary under H=0, V=1: 001100100001
- Hex: 0x321
- V count: 4/12

## Exact null-model probabilities

| null model | probability | approximately |
|:---|---:|---:|
| Uniform 12-bit sequence, exact 0x321 | 0.00024414 | 1 in 4096 |
| Uniform, allow H/V polarity (0x321 or 0xCDE) | 0.00048828 | 1 in 2048 |
| Condition on exactly four V buildings | 0.00202020 | 1 in 495 |
| Bernoulli with p(V)=4/12, exact pattern | 0.00048171 | 1 in 2076 |

## Look-elsewhere correction examples

- There are 14 strict descending consecutive 3-hex-digit patterns out of 4096.
- Counting either ascending or descending consecutive triplets gives 28 patterns out of 4096.
- Conditioned on four 1-bits, descending-triplet patterns occupy 2 of 495 sequences.

## Interpretation

The exact 321 pattern is uncommon under simple nulls and Stage 10 showed that the underlying H/V sequence is geometrically robust. That strengthens 321 as a lead.

However, this is not a formal discovery p-value: the building segmentation, H/V coding, and recognition of a memorable hexadecimal pattern were not specified before looking at the image. A genuine second clue should independently point toward 3-2-1, ordering, countdown, selection, or a related semantic operation before 321 is treated as intentional.
