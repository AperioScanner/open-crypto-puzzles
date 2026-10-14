# Stage146 — verify native skyline two bands despite resample merging

- Source SHA verified: **True**
- Artificial two/single/no-band controls: **16/16**
- Replays Stage145 diagnostic source exactly: **True**
- Upper/lower fixed source bands both supported in 4/4: **True**
- Decision: **FIXED_NATIVE_SKYLINE_BANDS_REPRODUCIBLE**

| format | upper source x-bins | lower source x-bins | after deleting one stroke |
|---|---:|---:|---:|
| original | 8/12 | 11/12 | 8/12 |
| jpeg85 | 8/12 | 12/12 | 8/12 |
| jpeg70 | 8/12 | 12/12 | 8/12 |
| down75_up | 7/12 | 11/12 | 7/12 |

## Interpretation

Two separated original drawing regions retain long native horizontal line support even after JPEG/resampling, despite morphological connected-component merging. The rotated/mirrored visual 'spire' has an ordinary source-line explanation, not a uniquely encoded shape.

Source-contact: two-fixed-horizontal-source-bands.png.
No keys, seed words, wallet or external content.
