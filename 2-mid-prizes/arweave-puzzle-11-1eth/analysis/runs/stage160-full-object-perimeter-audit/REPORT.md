# Stage160 — Corrected Stage12 crop-border/perimeter measurement source audit

- Canonical image SHA correct: **True**
- Six original Stage12 source crop perimeter percentages exactly reproduced: **6/6**
- Synthetic black-rim / white-rim fixture controls: **48/48**
- Real source edge occupancies consistent with filled silhouette control in both corrected objects and four formats: **True**
- Decision: **SOURCE_CROP_EDGE_COMPATIBLE_WITH_FILLED_GEOMETRY**

| Object | Historical cropped w2 (t140) | Corrected real w2 original | Fixed filled silhouette w2 | Source minus silhouette |
|---|---:|---:|---:|---:|
| large_sailboat | 0.2347 | 0.0000 | 0.0000 | +0.0000 |
| small_sails_full_band | 0.1399 | 0.0000 | 0.0000 | +0.0000 |

**Interpretation:** Stage12's perimeter fraction was defined on the rectangle crop edge, not the hand-drawn outline. The old ROI is defective for both objects and no source geometry correction establishes a hidden code. Historical counts and other already-validated regions were untouched.

The two different ROI definitions do not estimate the same quantity; numerical difference is provenance-only.

No hidden payload, key, wallet or BIP39 extraction attempted.
