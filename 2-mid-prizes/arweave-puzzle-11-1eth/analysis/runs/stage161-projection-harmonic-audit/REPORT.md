# Stage161 — synthetic-only audit of Stage12 projection harmonics

- Original source SHA provenance (no real pixels measured): **True**
- Synthetic fixture integrity: **120/120**
- Flat-shape expected x lag3: **24/24**
- Period12 stripe cases best x-lag exactly12: **60/96**
- Period12 stripe cases best x-lag 24/36/etc (valid higher harmonics): **36/96**
- Period12 stripe cases whose best lag is NOT a multiple of12: **0/96**
- Stage12 normalized scores greater than 1: **48/120**
- Decision: **HARMONIC_FUNDAMENTAL_NONIDENTIFIABILITY_CONFIRMED**

| Synthetic family | Cases | Best-lag histogram | Scores over 1 |
|---|---:|---|---:|
| filled | 24 | {'3': 24} | 0 |
| stripe_width_2 | 24 | {'12': 12, '48': 12} | 12 |
| stripe_width_3 | 24 | {'12': 12, '36': 12} | 12 |
| stripe_width_4 | 24 | {'12': 12, '24': 12} | 12 |
| stripe_width_5 | 24 | {'12': 24} | 12 |

The old Stage12 method is a globally standardized overlap-normalized autocovariance, NOT a bounded Pearson correlation at each lag. A source with period12 may have strong higher harmonics, making an unqualified best-lag-as-fundamental reading unreliable. Source pixel interpretation is NOT updated by this synthetic-only calibration.

No new message, key or intentionally coded source feature established.
