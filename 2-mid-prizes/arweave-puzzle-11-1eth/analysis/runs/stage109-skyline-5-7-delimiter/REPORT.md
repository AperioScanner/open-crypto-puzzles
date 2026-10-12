# Stage 109 — corrected central skyline gap / 5|7 delimiter audit

- synthetic detector control pass: **False**
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
| original | 100 | {'x0': 522, 'x1': 701, 'width': 179, 'mean_occupancy': 0.17337299571936443, 'occupancy_centers': [0.19784174588298298, 0.3478467211800546], 'overlap_px': 0} | False |
| original | 140 | {'x0': 709, 'x1': 887, 'width': 178, 'mean_occupancy': 0.22822121698526188, 'occupancy_centers': [0.2370076706918812, 0.4028421578421578], 'overlap_px': 102} | True |
| original | 180 | {'x0': 753, 'x1': 887, 'width': 134, 'mean_occupancy': 0.226477999612328, 'occupancy_centers': [0.2610824401217414, 0.4377114164904862], 'overlap_px': 102} | True |
| jpeg85 | 100 | {'x0': 521, 'x1': 702, 'width': 181, 'mean_occupancy': 0.17485829088039032, 'occupancy_centers': [0.1994298384542287, 0.351426578536553], 'overlap_px': 0} | False |
| jpeg85 | 140 | {'x0': 715, 'x1': 887, 'width': 172, 'mean_occupancy': 0.22635155542132282, 'occupancy_centers': [0.23755449229133438, 0.4021078921078921], 'overlap_px': 102} | True |
| jpeg85 | 180 | {'x0': 752, 'x1': 887, 'width': 135, 'mean_occupancy': 0.22668590668590669, 'occupancy_centers': [0.2607829851308112, 0.4375391032325339], 'overlap_px': 102} | True |
| jpeg70 | 100 | {'x0': 522, 'x1': 700, 'width': 178, 'mean_occupancy': 0.1739967897271268, 'occupancy_centers': [0.1964917123259312, 0.3452271231073074], 'overlap_px': 0} | False |
| jpeg70 | 140 | {'x0': 709, 'x1': 887, 'width': 178, 'mean_occupancy': 0.22880490296220632, 'occupancy_centers': [0.237206282090003, 0.4038582776446854], 'overlap_px': 102} | True |
| jpeg70 | 180 | {'x0': 753, 'x1': 887, 'width': 134, 'mean_occupancy': 0.22535375072688502, 'occupancy_centers': [0.26238968470728125, 0.4397909782525166], 'overlap_px': 102} | True |
| down75_up | 100 | {'x0': 521, 'x1': 701, 'width': 180, 'mean_occupancy': 0.1631313131313131, 'occupancy_centers': [0.18953816523332487, 0.34762761990484764], 'overlap_px': 0} | False |
| down75_up | 140 | {'x0': 709, 'x1': 887, 'width': 178, 'mean_occupancy': 0.23192762293885888, 'occupancy_centers': [0.24657148720354136, 0.41924946219424747], 'overlap_px': 102} | True |
| down75_up | 180 | {'x0': 754, 'x1': 887, 'width': 133, 'mean_occupancy': 0.23544575725026853, 'occupancy_centers': [0.2790421325197214, 0.46914514057371204], 'overlap_px': 102} | True |

## Interpretation

Even after correcting the detector, the 5|7 split does not satisfy the full robustness gate. Retire it as a coding delimiter.

No private-key material was generated or tested.
