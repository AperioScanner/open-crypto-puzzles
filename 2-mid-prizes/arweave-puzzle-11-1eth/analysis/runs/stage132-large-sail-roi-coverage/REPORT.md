# Stage 132 — audit legacy large sailboat bounding-box coverage

- Canonical SHA verified: **True**
- Legacy bounding box: **[44, 320, 359, 599]**
- Synthetic full vs truncated controls: **True** (12 + 12/24)
- Real threshold×reencoding cases meeting fixed incomplete-ROI gate: **12/12**
- Decision: **LEGACY_LARGE_SAILBOAT_BBOX_INCOMPLETE**

| fixed region | original source ink outside legacy bbox (thr=170) | density |
|---|---:|---:|
| large_sail | 0.667 | 0.666 |
| large_hull | 1.000 | 0.594 |

## Interpretation

The old ROI excludes most visible pencil ink in fixed large-sail/hull polygons. Review earlier ROI-dependent measurements with accurate bounds; this is an image-geometry defect, NOT a discovered code.

Source overlay: large-sail-legacy-bbox-overlay.png.
No keys or wallet operations.
