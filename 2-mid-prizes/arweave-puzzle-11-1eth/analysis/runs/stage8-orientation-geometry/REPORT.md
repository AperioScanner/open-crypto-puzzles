# Stage 8 — orientation-guided skyline geometry

The robust hatch marker is HHVV HHVH HHHV = 0x321 under H=0,V=1.
This stage uses hatch direction as a selector for building dimension (H→width, V→height), with the inverse and raw height/width sequences as controls.

## Selected sequences

- auto_exclusive:Hwidth_Vheight: [88, 86, 144, 212, 104, 94, 250, 116, 88, 102, 56, 226]
- auto_exclusive:Hheight_Vwidth: [167, 245, 84, 174, 292, 106, 160, 220, 137, 208, 144, 78]
- auto_exclusive:heights: [167, 245, 144, 212, 292, 106, 250, 220, 137, 208, 144, 226]
- auto_exclusive:widths: [88, 86, 84, 174, 104, 94, 160, 116, 88, 102, 56, 78]
- auto_inclusive:Hwidth_Vheight: [89, 87, 145, 213, 105, 95, 251, 117, 89, 103, 57, 227]
- auto_inclusive:Hheight_Vwidth: [168, 246, 85, 175, 293, 107, 161, 221, 138, 209, 145, 79]
- auto_inclusive:heights: [168, 246, 145, 213, 293, 107, 251, 221, 138, 209, 145, 227]
- auto_inclusive:widths: [89, 87, 85, 175, 105, 95, 161, 117, 89, 103, 57, 79]
- community:Hwidth_Vheight: [115, 90, 90, 165, 100, 100, 180, 110, 110, 100, 70, 190]
- community:Hheight_Vwidth: [100, 190, 100, 170, 240, 55, 150, 160, 90, 160, 100, 50]
- community:heights: [100, 190, 90, 165, 240, 55, 180, 160, 90, 160, 100, 190]
- community:widths: [115, 90, 100, 170, 100, 100, 150, 110, 110, 100, 70, 50]

- Unique 32-byte candidates generated: 55385
- Valid secp256k1 scalars checked: 55384
- ff21 prefix near-misses: 2
- Exact target match: false

This rules out the bounded, most literal interpretation that each building's hatch selects its horizontal or vertical dimension and that the resulting 12 values are directly serialized or hashed by common transforms.
