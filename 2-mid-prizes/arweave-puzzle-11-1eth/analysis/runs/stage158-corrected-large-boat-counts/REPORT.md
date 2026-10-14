# Stage158 — Full original large boat counts, repairing Stage15 source ROI

- Canonical SHA256 verified: **True**
- Old Stage15 large-boat 5-threshold exact replay: **5/5**
- Fixed 321/123/negative synthetic controls: **60/60**
- Source stable 321/123 signature in all 4 formats: **False**
- Decision: **NO_STABLE_FULL_LARGE_BOAT_COUNT_CORROBORATION**

| Threshold | old truncated Stage15 bbox count | corrected source sail+hull count |
|---:|---|---|
| 80 | [122, 5, 1] | [445, 4, 2] |
| 110 | [102, 5, 1] | [323, 1, 2] |
| 140 | [71, 4, 1] | [208, 2, 2] |
| 170 | [49, 4, 1] | [147, 1, 2] |
| 200 | [26, 2, 2] | [98, 1, 2] |

Full true ship polygons are reused unchanged from Stage132 and do not overlap the missing old right/bottom content. No other Stage15 region was retested; no private keys or messages decoded.
