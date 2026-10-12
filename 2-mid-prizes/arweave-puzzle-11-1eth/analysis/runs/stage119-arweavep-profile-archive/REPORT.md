# Stage 119 — watermark-directed @ArweaveP profile/header archive audit

**Experiment:** A11-EXP-119

- snapshots attempted: **4**
- authenticated profile snapshots: **0**
- authenticated tweet-page witnesses: **4**
- avatar/banner images decoded: **12/0**
- exact-handle source control: **True**
- ORB positive control: **True** (681 inliers, 0.973)
- profile/header/media assets tested: **21**
- strong Puzzle #11 derivatives: **0**
- decision: **PARTIAL_PROFILE_COVERAGE**

## Snapshot metadata

- 20200430185132 type=tweet_witness fetch=True handle=True title='Arweave Puzzle on Twitter: "Like I specified, the private key is hidden in the image. One way to try is MEW: Access by Private Key 🤐 good luck!… "'
- 20200430210602 type=tweet_witness fetch=True handle=True title='Arweave Puzzle on Twitter: "format does not matter… "'
- 20200501121921 type=tweet_witness fetch=True handle=True title='Arweave Puzzle on Twitter: "0xFF2142E98E09b5344994F9bEB9C56C95506B9F17 it is also included somewhere in the image 🧐… "'
- 20200502173835 type=tweet_witness fetch=True handle=True title='Arweave Puzzle on Twitter: "There is 1 ETH hidden in https://t.co/wyyxPDtXDH Puzzle 11 🧩. Please retweet to make more of these possible! #puzzle #steganography #arweave #cryptopuzzle… https://t.co/8llFe3yvq9"'

## Image comparisons

| idx | role | fetched | inliers | fraction | strong |
|---:|:---|:---:|---:|---:|:---:|
| 0 | avatar | True | 11 | 0.314 | False |
| 1 | avatar | True | 11 | 0.314 | False |
| 2 | avatar | True | 0 | 0.000 | False |
| 3 | avatar | True | 0 | 0.000 | False |
| 4 | avatar | False | 0 | 0.000 | False |
| 5 | avatar | False | 0 | 0.000 | False |
| 6 | avatar | False | 0 | 0.000 | False |
| 7 | avatar | False | 0 | 0.000 | False |
| 8 | avatar | False | 0 | 0.000 | False |
| 9 | avatar | False | 0 | 0.000 | False |
| 10 | avatar | False | 0 | 0.000 | False |
| 11 | avatar | False | 0 | 0.000 | False |
| 12 | avatar | False | 0 | 0.000 | False |
| 13 | avatar | True | 6 | 0.231 | False |
| 14 | avatar | True | 0 | 0.000 | False |
| 15 | avatar | True | 0 | 0.000 | False |
| 16 | avatar | True | 0 | 0.000 | False |
| 17 | avatar | True | 0 | 0.000 | False |
| 18 | avatar | True | 0 | 0.000 | False |
| 19 | avatar | True | 0 | 0.000 | False |
| 20 | avatar | True | 0 | 0.000 | False |

## Interpretation

Partial coverage: only observed profile assets assessed. Do not retire unobserved profile/header layers; keep Stage 119 open unless independently corroborated.

No private-key material was generated or tested.
