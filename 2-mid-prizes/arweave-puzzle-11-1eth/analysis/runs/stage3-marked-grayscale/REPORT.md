# Stage 3 — alpha-marked grayscale and boat-focus sweep

- Alpha-marked pixels: 434
- Alpha bbox: [0, 378, 551, 1102]
- Unique 32-byte candidates generated: 55466
- Valid secp256k1 scalars checked: 44872
- Addresses beginning with ff21: 1
- Exact target match: **False**

This stage treats the alpha halo as a possible *marker* and tests the corresponding grayscale content, rather than interpreting alpha values as the payload itself.
It also checks bounded hashes of the marked boat crop and a small public identifier family.
No private-key candidate is persisted.
