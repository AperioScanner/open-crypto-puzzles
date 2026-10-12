# Stage 109 — corrected central skyline gap / 5|7 delimiter audit

- synthetic detector control pass: **True**
- dominant geometry gap after building: **5**
- dominant gap width: **102 px**
- second-largest gap width: **4 px**
- width ratio: **25.50×**
- dominant share of inter-building gap space: **0.797**
- normalized midpoint distance from canvas center: **0.021**
- independent detector matches all 12 conditions: **False**
- exchangeable-gap null p: **0.000005**
- promoted: **False**

## Detection checks

| variant | threshold | best detected low-occupancy corridor | match |
|:---|---:|:---|:---:|
| original | 100 | None | False |
| original | 140 | None | False |
| original | 180 | None | False |
| jpeg85 | 100 | None | False |
| jpeg85 | 140 | None | False |
| jpeg85 | 180 | None | False |
| jpeg70 | 100 | None | False |
| jpeg70 | 140 | None | False |
| jpeg70 | 180 | None | False |
| down75_up | 100 | None | False |
| down75_up | 140 | None | False |
| down75_up | 180 | None | False |

## Interpretation

Even after correcting the detector, the 5|7 split does not satisfy the full robustness gate. Retire it as a coding delimiter.

No private-key material was generated or tested.
