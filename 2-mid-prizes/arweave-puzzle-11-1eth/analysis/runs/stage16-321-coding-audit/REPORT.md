# Stage 16 — 0x321 coding-choice audit

**Experiment:** A11-EXP-016

This stage asks whether the robust 12-bit H/V sequence has strong evidence for the specific hexadecimal reading 0x321, rather than merely being a stable binary pattern.

## Representation look-elsewhere

- Exact identity hexadecimal 321 under a fixed 12-bit null: 1/4096 = 0.000244.
- Allowing identity/reverse/complement/reverse-complement and common hex/octal/decimal representations, the fraction containing 321 or 123 is 242/4096 = 0.059082.
- Observed sequence common-choice hits: [{'transform': 'identity', 'representation': 'hex3', 'value': '321'}]

## Does the skyline support 4+4+4 grouping?

- Building gaps (after buildings 1..11): [4, 4, 2, 2, 102, 2, 2, 2, 2, 2, 4]
- Gap after building 4: 2 px
- Gap after building 8: 2 px
- Largest gap: 102 px after building 5
- Are 4 and 8 the two strongest geometric boundaries? False

## Interpretation

The image geometry does not independently support the 4+4+4 split needed for three hexadecimal nibbles. Therefore 0x321 should be treated as a post-hoc encoding candidate, not yet as an author-intended instruction.

The broader representation probability quantifies the look-elsewhere penalty: a memorable 321/123 appearance becomes less surprising once common reversals/complements and bases are allowed.
This does not invalidate the robust H/V structure itself; it only audits the evidential weight of naming that structure 0x321.
