# Stage 97 — Puzzle #9 semantic-anchor + four-step source audit

**Experiment:** A11-EXP-097

- primary four-step quote recovered: **True**
- secondary quote sources with same tweet ID + #9 context: **2**
- four-step quote confidence: **PRIMARY_VERIFIED**
- official 'everything needed ... hidden in image' context: **False**
- literary/numeric crops robust across lossy variants: **True**
- five distinct bird colors in original: **True**
- bird color identities stable across variants: **False**
- semantic multi-anchor scaffold supported: **False**

## Visible anchors

- literary quote: `It was a bright cold day in April, and the clocks were striking thirteen.`
- numeric stamp: `12:05.04`
- bird colors: green, blue, orange, red, yellow

## Text-crop robustness

| anchor | jpeg85 edge corr | jpeg70 | resize roundtrip | robust |
|:---|---:|---:|---:|:---:|
| literary_quote | 0.974 | 0.967 | 0.827 | True |
| numeric_stamp | 0.954 | 0.935 | 0.873 | True |

## Bird-color robustness

| crop | expected | original | jpeg85 | jpeg70 | resize | stable |
|:---|:---|:---|:---|:---|:---|:---:|
| bird_green | green | green | yellow | yellow | yellow | False |
| bird_blue | blue | blue | blue | blue | blue | True |
| bird_orange | orange | orange | orange | orange | orange | True |
| bird_red | red | red | red | red | red | True |
| bird_yellow | yellow | yellow | yellow | yellow | yellow | True |

## Source hierarchy

| kind | fetched | exact four-step quote | tweet id | #9 context | image-only official phrase |
|:---|:---:|:---:|:---:|:---:|:---:|
| official_arweave_newsletter | False | False | False | False | False |
| official_arweave_telegram | True | False | False | True | False |
| secondary_crypto_puzzle_dossier_11 | True | True | True | True | False |
| secondary_crypto_puzzle_dossier_3 | True | True | True | True | False |
| twitter_syndication | True | False | False | False | False |
| wayback | True | True | False | False | False |

## Interpretation

The evidence is insufficient to promote a specific semantic multi-anchor mechanism. Preserve only the weaker image-only prior and do not transfer an assumed four-anchor scheme to Puzzle #11.

Crops are saved for direct visual review. No OCR-derived secret string, key candidate, or wallet operation is performed.
