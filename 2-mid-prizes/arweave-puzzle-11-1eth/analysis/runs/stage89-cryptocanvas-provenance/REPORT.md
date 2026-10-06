# Stage 89 — CryptoCanvas provenance and metadata audit

**Experiment:** A11-EXP-089

- Contract: `0x0b0b70905137786cf705102c194a1b4916d8c4d0`
- Verdict: **UNRESOLVED_OR_WEAK_MEDIA_MATCH**
- Token #5 mint after Puzzle #11: **True**
- Token #5 media strongly matches canonical puzzle: **False**
- Token #5 media byte-exact: **False**
- Token #5 metadata has description: **False**

## Token inventory

| token | name | description | current owner | first transfer UTC | first recipient | tx sender |
|---:|:---|:---|:---|:---|:---|:---|
| 1 |  |  | 0xdd10bb7829ba5ccd690e51b958bfadc207b83285 | 2020-07-17T17:21:02.000000Z | 0xd8424ee7cc2520f7dae828f84f99f53ac0dd6734 |  |
| 2 |  |  | 0x718ffdc2b4e813e7d200c6086b5425fd6a219cff | 2020-07-20T07:52:30.000000Z | 0x718ffdc2b4e813e7d200c6086b5425fd6a219cff |  |
| 3 |  |  | 0xd8424ee7cc2520f7dae828f84f99f53ac0dd6734 | 2020-07-22T20:57:20.000000Z | 0xd8424ee7cc2520f7dae828f84f99f53ac0dd6734 |  |
| 4 |  |  | 0x0386bf5e50ce1ce02b8b0417e679292f18476a40 | 2020-07-22T23:26:00.000000Z | 0xd8424ee7cc2520f7dae828f84f99f53ac0dd6734 |  |
| 5 |  |  | 0xfdae2f991a521f54bbef89048922dff9bac2d96b | 2020-07-24T16:19:20.000000Z | 0xfdae2f991a521f54bbef89048922dff9bac2d96b |  |

## Token #5 image comparison

- canonical_sha256: `c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1`
- media_sha256: `ba75bd7e768e64a53d5eaeabbeba20dbc1781ce88d1e462a3d69464ad911c850`
- canonical_shape: `[1105, 1600]`
- media_shape: `[630, 1200]`
- resized_for_comparison: `True`
- pearson_gray: `-0.08821032581893376`
- mean_abs_gray_delta: `155.18628054298642`
- exact_gray_fraction: `0.0900039592760181`
- pearson_64x64: `-0.13030806860376487`

## Interpretation

The available public endpoints do not establish a clean provenance relationship. Do not infer an author link from the OpenSea collection alone.

Sources:
- https://puzzling.stackexchange.com/questions/97537/image-steganography-hidden-message-inside-image-png-8-bit-grayalpha?noredirect=1
- https://opensea.io/collection/cryptocanvas-xyz
- https://opensea.io/item/ethereum/0x0b0b70905137786cf705102c194a1b4916d8c4d0/5

No private-key material was generated or tested.
