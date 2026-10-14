# Stage167 — visible sail-foot diagonal alignment against 5 fixed x offsets

- Canonical original SHA confirmed: **True**
- Source and predecessor guards: **6/6**
- Synthetic shifted/known and blank controls: **160/160**
- Sail footpoints with stable original 0px shift: **1/10**
- Sail footpoints with stable alternate offset: **3/10**
- Unresolved footpoints: **6/10**
- Decision: **ANNOTATED_FOOT_SHIFT_REQUIRES_MANUAL_SOURCE_REVIEW**

| Original sail foot | Original best offset | Top line-ink support | Margin | Four-format result |
|---|---:|---:|---:|---|
| sail1_left | None | 0.85 | 0.03 | unresolved |
| sail1_right | None | 0.87 | 0.06 | unresolved |
| sail2_left | None | 0.87 | 0.09 | unresolved |
| sail2_right | 0 | 0.88 | 0.17 | original0 |
| sail3_left | 8 | 0.98 | 0.32 | alternate |
| sail3_right | None | 1.00 | 0.02 | unresolved |
| sail4_left | None | 0.82 | 0.12 | unresolved |
| sail4_right | -8 | 0.95 | 0.43 | alternate |
| sail5_left | None | 0.68 | 0.17 | unresolved |
| sail5_right | -8 | 0.77 | 0.17 | alternate |

Source answer concerns sloping-ink alignment only; it does not locate physical footpoint junctions accurately nor derive any corrected base width. No annotated endpoints were modified to seek statistical significance.

No mnemonic, wallet, secret, off-source context or code reconstruction.
