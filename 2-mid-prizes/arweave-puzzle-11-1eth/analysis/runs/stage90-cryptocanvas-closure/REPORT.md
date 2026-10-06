# Stage 90 — CryptoCanvas closure audit

**Experiment:** A11-EXP-090

- Verdict: **MISIDENTIFIED_REVERSE_IMAGE_LEAD**
- Token #5 mint: **2020-07-24T16:19:20.000000Z**
- Image candidates tested: **60**
- Decisive original-media candidates successfully scored: **58**
- Strong decisive matches to Puzzle #11: **0**

## Contract provenance

- address record: `{'hash': '0x0b0B70905137786cf705102c194a1b4916d8c4D0', 'name': 'CANVAS', 'is_contract': True, 'is_verified': True, 'creator_address_hash': '0xD8424eE7cC2520F7Dae828f84f99F53Ac0Dd6734', 'coin_balance': '0', 'has_beacon_chain_withdrawals': False}`
- smart-contract record: `{'name': 'CANVAS', 'compiler_version': 'v0.5.16+commit.9c3226ce', 'optimization_enabled': False, 'verified_at': '2026-01-02T15:59:33.370242Z', 'is_verified': True, 'language': 'solidity', 'evm_version': 'default', 'license_type': 'none'}`
- creation transaction: `{'hash': '0x9eeeb25429f558cff0dbde868ff6086b7a9daa5437fe2d97772e354c31f608cf', 'from': '0xD8424eE7cC2520F7Dae828f84f99F53Ac0Dd6734', 'to': None, 'timestamp': '2020-07-17T16:51:01.000000Z', 'block': None, 'status': 'ok', 'method': None, 'fetch': {'url': 'https://eth.blockscout.com/api/v2/transactions/0x9eeeb25429f558cff0dbde868ff6086b7a9daa5437fe2d97772e354c31f608cf', 'status': 200, 'bytes': 31903, 'sha256': 'ad244e12966436953bf33fe5a00a6cc29212c39564f41383fd75bfbac79c31b3'}}`

## Mint transactions

| token | mint UTC | mint recipient | tx sender |
|---:|:---|:---|:---|
| 1 | 2020-07-17T17:21:02.000000Z | 0xd8424ee7cc2520f7dae828f84f99f53ac0dd6734 | 0xD8424eE7cC2520F7Dae828f84f99F53Ac0Dd6734 |
| 2 | 2020-07-20T07:52:30.000000Z | 0x718ffdc2b4e813e7d200c6086b5425fd6a219cff | 0x718FfdC2b4e813E7d200C6086B5425fd6a219CFF |
| 3 | 2020-07-22T20:57:20.000000Z | 0xd8424ee7cc2520f7dae828f84f99f53ac0dd6734 | 0xD8424eE7cC2520F7Dae828f84f99F53Ac0Dd6734 |
| 4 | 2020-07-22T23:26:00.000000Z | 0xd8424ee7cc2520f7dae828f84f99f53ac0dd6734 | 0xD8424eE7cC2520F7Dae828f84f99F53Ac0Dd6734 |
| 5 | 2020-07-24T16:19:20.000000Z | 0xfdae2f991a521f54bbef89048922dff9bac2d96b | 0xFdAe2f991a521F54bbEF89048922DFf9bAC2D96B |

## Best recovered image candidates

| source | decisive | pearson64 | dHash/256 | strong | URL |
|:---|:---:|---:|---:|:---:|:---|
| opensea_embedded | True | 0.28265036859692066 | 124 | False | https://i2c.seadn.io/collection/usdt-shell/image/2f80f07bf192ca8237ca9bdcb33aa4/212f80f07bf192ca8237ca9bdcb33aa4.png |
| opensea_embedded | True | 0.21330259310968336 | 113 | False | https://i2c.seadn.io/base/85ccd4ee998c4ce3865ba0a877b00e85/7efe747bb96f8fd6edb11d192a1323/7a7efe747bb96f8fd6edb11d192a1323.png |
| opensea_embedded | True | 0.2023895148687956 | 97 | False | https://i2c.seadn.io/flow/0x99af3eea856556646c98c8b9b2548fe815240750/26c76e755987f76b76e2e4005e9f52/4126c76e755987f76b76e2e4005e9f52.png |
| opensea_embedded | True | 0.18634590444666493 | 111 | False | https://i2c.seadn.io/base/0xb2000000000000000000004884b426556b92883d/2073e550fac0d3fec805b24e357aad/172073e550fac0d3fec805b24e357aad.png |
| opensea_embedded | True | 0.17829801354606137 | 122 | False | https://i2c.seadn.io/base/0xb200000000000000000000c2e324d24d7eecd1fb/7d986c60c14a1f0addd53a623b8261/a87d986c60c14a1f0addd53a623b8261.jpeg |
| opensea_embedded | True | 0.1354526881427995 | 115 | False | https://i2c.seadn.io/base/0xb200000000000000000000d9192b6b456483c2e8/0c9dd22e40312a66b3fed6719feae3/d40c9dd22e40312a66b3fed6719feae3.png |
| opensea_embedded | True | 0.12169327417570104 | 134 | False | https://i2c.seadn.io/base/aab9893c55c34593a694ea3027f874c0/5fcf18e465e61a68bcae360229deb7/af5fcf18e465e61a68bcae360229deb7.jpeg |
| opensea_embedded | True | 0.11063126939825424 | 119 | False | https://i2c.seadn.io/base/0xb2000000000000000000002d0ba3164cc74f58b7/5dab252d82f50ac19fbbf52d3f597d/835dab252d82f50ac19fbbf52d3f597d.jpeg |
| opensea_embedded | True | 0.10484703385714013 | 110 | False | https://i2c.seadn.io/base/67463b8d6eab5157562b4a5c/e228f0dc1634447364fa8741c0431f/75e228f0dc1634447364fa8741c0431f.png |
| opensea_embedded | True | 0.10089275706616592 | 117 | False | https://i2c.seadn.io/base/0544bb670446453e916b2fedb0cdd5eb/63b7ea6c5d346d1be0c5ac3d0ceb66/a663b7ea6c5d346d1be0c5ac3d0ceb66.png |
| opensea_embedded | True | 0.08103308305981455 | 113 | False | https://i2c.seadn.io/ethereum/67463bc1d2898b5cd98b05c7/4b171c151a4ff5853dcf92a307524d/2e4b171c151a4ff5853dcf92a307524d.png |
| opensea_embedded | True | 0.07352888392435648 | 125 | False | https://i2c.seadn.io/base/0xb200000000000000000000397293cb8cda9a10c5/6266986c02cb208f5573e9f9f4dcd6/396266986c02cb208f5573e9f9f4dcd6.png |

## Interpretation

Recovered token #5 media is decisively different from the canonical puzzle image. The 2021 reverse-image-search association is treated as a misidentification.

No private-key material was generated, reconstructed or tested.
