# Stage 90 — corrected CryptoCanvas closure audit

**Experiment:** A11-EXP-090

- Verdict: **CONFIRMED_POSTPUBLICATION_MIRROR**
- Token #5 mint: **2020-07-24T16:19:20.000000Z**
- Token-specific OpenGraph artwork strong match: **True**
- ORB good matches: **266**
- Homography inliers: **239**
- Inlier fraction: **0.8984962406015038**

## Implementation correction

The first Stage-90 implementation incorrectly marked every SEADN image embedded in the current OpenSea page as token-specific. Those include recommendation assets from unrelated collections and chains, so the prior MISIDENTIFIED_REVERSE_IMAGE_LEAD verdict was invalid.

This rerun uses only token-specific evidence: Blockscout token #5 cached fields and the OpenSea OpenGraph card for the exact contract/token route. The OpenGraph card is segmented to its artwork rectangle and matched to the canonical puzzle with ORB + RANSAC homography.

## Interpretation

The token-specific OpenSea card contains artwork geometrically matching the canonical Puzzle #11 image. Combined with the July 2020 mint date, CryptoCanvas is a confirmed post-publication mirror/derivative, not the source of the April 2020 puzzle.

No private-key material was generated, reconstructed or tested.
