# Stage 12 — counting and perimeter diagnostics

**Experiment:** A11-EXP-012

Motivation: solved siblings use small-detail counting, secondary marks, perimeter, and overall visual context. This stage inventories those feature classes in Puzzle #11 without generating or checking any private-key material.

## Stable small-component counts

| region | median components (3–200 px) | MAD across thresholds |
|:---|---:|---:|
| first_row_visual_strip | 2.0 | 1.0 |
| building_03 | 8.0 | 2.0 |
| building_09 | 7.0 | 2.0 |
| building_06 | 9.0 | 3.0 |
| building_02 | 8.0 | 3.0 |
| building_12 | 35.0 | 6.0 |
| building_01 | 20.0 | 6.0 |
| building_04 | 139.0 | 7.0 |

## Highest perimeter ink fractions at threshold 140

| region | 2px perimeter ink fraction |
|:---|---:|
| building_09 | 0.4519 |
| building_02 | 0.4332 |
| building_01 | 0.4123 |
| building_06 | 0.4036 |
| building_03 | 0.3987 |
| building_08 | 0.3464 |
| building_12 | 0.3125 |
| building_05 | 0.3114 |

## Strongest projection periodicities at threshold 140

| region | score | x best lag | y best lag |
|:---|---:|---:|---:|
| large_sailboat | 0.9924 | 3 | 3 |
| small_sails_full_band | 0.9696 | 3 | 3 |
| first_row_visual_strip | 0.9672 | 3 | 3 |
| skyline_full_band | 0.9334 | 3 | 3 |
| building_02 | 0.8363 | 3 | 3 |
| building_08 | 0.7784 | 3 | 85 |
| building_12 | 0.7396 | 13 | 3 |
| building_10 | 0.7138 | 4 | 41 |

## Interpretation

This run is a census, not a solve. Regions with stable small-component counts, unusually strong perimeter occupancy, or strong 1-D periodicity are promoted for visual inspection in the next stage. Any apparent 3/2/1 count is only interesting if it is stable across thresholds and visually corresponds to deliberate marks.

Diagnostic image: secondary-detail-contact-sheet.png
