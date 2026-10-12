# Stage 109 — corrected central skyline gap / 5|7 delimiter audit

- synthetic detector control pass: **False**
- dominant geometry gap after building: **5**
- dominant gap width: **102 px**
- second-largest gap width: **4 px**
- width ratio: **25.50×**
- dominant share of inter-building gap space: **0.797**
- normalized midpoint distance from canvas center: **0.021**
- independent detector matches all 12 conditions: **True**
- exchangeable-gap null p: **0.000005**
- promoted: **False**

## Detection checks

| variant | threshold | best detected low-occupancy corridor | match |
|:---|---:|:---|:---:|
| original | 100 | {'x0': 777, 'x1': 983, 'width': 206, 'mean_occupancy': 0.08701703982563899, 'occupancy_centers': [0.1509329593906528, 0.34169639578196315], 'overlap_px': 102} | True |
| original | 140 | {'x0': 777, 'x1': 981, 'width': 204, 'mean_occupancy': 0.10078781512605042, 'occupancy_centers': [0.17546219167939284, 0.3781036552552055], 'overlap_px': 102} | True |
| original | 180 | {'x0': 777, 'x1': 982, 'width': 205, 'mean_occupancy': 0.11591587854654059, 'occupancy_centers': [0.2049799303607699, 0.42907010261731804], 'overlap_px': 102} | True |
| jpeg85 | 100 | {'x0': 776, 'x1': 983, 'width': 207, 'mean_occupancy': 0.08808291432515032, 'occupancy_centers': [0.1512296433725005, 0.3428173866949377], 'overlap_px': 102} | True |
| jpeg85 | 140 | {'x0': 777, 'x1': 982, 'width': 205, 'mean_occupancy': 0.10161772025883523, 'occupancy_centers': [0.17602098401437324, 0.37911919368974584], 'overlap_px': 102} | True |
| jpeg85 | 180 | {'x0': 778, 'x1': 982, 'width': 204, 'mean_occupancy': 0.11467837134853943, 'occupancy_centers': [0.20473752297127382, 0.42906529843575847], 'overlap_px': 102} | True |
| jpeg70 | 100 | {'x0': 776, 'x1': 983, 'width': 207, 'mean_occupancy': 0.0876737651582372, 'occupancy_centers': [0.1503475603439345, 0.3413566195709053], 'overlap_px': 102} | True |
| jpeg70 | 140 | {'x0': 777, 'x1': 982, 'width': 205, 'mean_occupancy': 0.10168491786958685, 'occupancy_centers': [0.1762134583563155, 0.37955726438419307], 'overlap_px': 102} | True |
| jpeg70 | 180 | {'x0': 778, 'x1': 982, 'width': 204, 'mean_occupancy': 0.11506102440976392, 'occupancy_centers': [0.2053471566562568, 0.4294029077796531], 'overlap_px': 102} | True |
| down75_up | 100 | {'x0': 775, 'x1': 983, 'width': 208, 'mean_occupancy': 0.08660714285714287, 'occupancy_centers': [0.14750976562499998, 0.3458238851095994], 'overlap_px': 102} | True |
| down75_up | 140 | {'x0': 777, 'x1': 982, 'width': 205, 'mean_occupancy': 0.10422100547536088, 'occupancy_centers': [0.18080573087022617, 0.3878020533366721], 'overlap_px': 102} | True |
| down75_up | 180 | {'x0': 778, 'x1': 982, 'width': 204, 'mean_occupancy': 0.12312675070028012, 'occupancy_centers': [0.2183078334614526, 0.44943341467021586], 'overlap_px': 102} | True |

## Interpretation

Even after correcting the detector, the 5|7 split does not satisfy the full robustness gate. Retire it as a coding delimiter.

No private-key material was generated or tested.
