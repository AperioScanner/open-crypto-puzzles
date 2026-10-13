# Stage 119 — watermark-directed @ArweaveP profile/header archive audit

**Experiment:** A11-EXP-119

- snapshots attempted: **4**
- authenticated profile snapshots: **0**
- authenticated tweet-page witnesses: **1**
- avatar/banner images decoded: **1/0**
- exact-handle source control: **True**
- author-attribution synthetic control: **True**
- 256px avatar ORB positive control: **True** (35 inliers)
- ORB positive control: **True** (681 inliers, 0.973)
- owner-attributed profile/header assets attempted: **1**
- strong Puzzle #11 derivatives: **0**
- decision: **PARTIAL_PROFILE_COVERAGE**

## Snapshot metadata

- 20200430185132 type=tweet_witness fetch=True handle=True attributed=1 unaudited_urls=4 title='Arweave Puzzle on Twitter: "Like I specified, the private key is hidden in the image. One way to try is MEW: Access by Private Key 🤐 good luck!… "'
- 20200430210602 type=tweet_witness fetch=False handle=None attributed=None unaudited_urls=None title=''
- 20200501121921 type=tweet_witness fetch=False handle=None attributed=None unaudited_urls=None title=''
- 20200502173835 type=tweet_witness fetch=False handle=None attributed=None unaudited_urls=None title=''

## Image comparisons

| idx | role | fetched | inliers | fraction | strong |
|---:|:---|:---:|---:|---:|:---:|
| 0 | avatar | True | 0 | 0.000 | False |

## Interpretation

Partial coverage: only observed profile assets assessed. Do not retire unobserved profile/header layers; keep Stage 119 open unless independently corroborated.

No private-key material was generated or tested.
