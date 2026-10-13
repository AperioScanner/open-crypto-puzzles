# Stage 123 — cross-region reused-pencil-patch audit

- Canonical SHA256: **True**
- Copy/independent-drawing controls: **True**
- Positive copied-patch hits: **5**
- Negative independent-patch hits: **0**
- Eligible real patches: **{'skyline': 228, 'water_largeboat': 265, 'pier_smallboats': 230}**
- Compared candidate pairs: **180**
- Cross-region replicated pairs: **0**
- Decision: **NO_FIXED_GRID_CROSS_REGION_COPY**

## Top five original-scene candidates

| regions | positions | original correlation | JPEG70 correlation | replicated |
|:---|:---|---:|---:|:---:|
| water_largeboat / pier_smallboats | [[144, 438], [1410, 365]] | 0.675 | 0.682 | False |
| water_largeboat / pier_smallboats | [[176, 374], [1186, 429]] | 0.640 | 0.649 | False |
| skyline / water_largeboat | [[1286, 128], [816, 470]] | 0.528 | 0.535 | False |
| skyline / pier_smallboats | [[870, 160], [930, 525]] | 0.639 | 0.644 | False |
| skyline / water_largeboat | [[1414, 96], [496, 790]] | 0.620 | 0.624 | False |

## Interpretation

No exact cross-region repeated 64px stroke template meets this strict grid and lossy-consistency gate. This does not exclude freehand semantic repetition, rotated copies, or other visual clues.

No mnemonic, key, candidate or wallet access was generated or used.
