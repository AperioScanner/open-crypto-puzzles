# Stage 118 — exact two-cell Braille audit

**Experiment:** A11-EXP-118

- sequence: **HHVVHHVHHHHV**
- positive control pass: **True**
- any observed two-letter reading: **False**
- count-matched familywise probability: **0.488889** (242/495)
- promoted: **False**

| reading | cell 1 dots | cell 2 dots | decoded | both letters |
|:---|:---|:---|:---:|:---:|
| ltr_H_raised | [1, 2, 5, 6] | [2, 3, 4, 5] | ?T | False |
| ltr_V_raised | [3, 4] | [1, 6] | ?? | False |
| rtl_H_raised | [2, 3, 4, 5] | [1, 2, 5, 6] | T? | False |
| rtl_V_raised | [1, 6] | [3, 4] | ?? | False |

## Interpretation

The fixed H/V sequence does not support an exceptional two-cell standard Braille reading. Retire Braille and do not expand this negative into arbitrary binary alphabets.

No private-key material was generated or tested.
