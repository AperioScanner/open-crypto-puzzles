# Stage188 — source-blind Stage187 crop attribution audit

- Integrity / fresh controls: **16/16**
- Full-ROI Stage187 site counts reproduced: **True**
- Number of synthetic site ROIs containing non-target foreground: **19/45**
- Site component counts changed by excluding non-target boats: **12/45**
- Full-ROI sites with <2 components: **10/45** (Stage187 literal figure)
- Object-isolated sites with <2 components: **15/45**
- Apparent full-ROI passes that are target-only failures: **5/45**
- Frozen decision: **STAGE187_CROSS_SITE_ATTRIBUTION_BIAS_CONFIRMED**

| Family | Sites | Foreign ink | Full-ROI <2 | Target-only <2 | False sufficiency |
|---|---:|---:|---:|---:|---:|
| curved | 15 | 7 | 10 | 15 | 5 |
| broken | 15 | 6 | 0 | 0 | 0 |
| curved_broken | 15 | 6 | 0 | 0 | 0 |

Stage187's 10/45 is an exact count of <2 **components inside fixed full-scene ROIs**.
It is not, without object isolation, an exact count of <2 components of each **named hull**.
The previous Stage127 original-source overlap warning is historical, not a new visual clue.
This measurement audits already-used synthetic drawings, NOT independent holdouts.
All historical Stage185–187 files, preregistration criteria and scientific failures are unchanged.
No natural original image pixels, solution, code, key or wallet-related data were evaluated.
