# Stage155 — old small-sail band source coverage and code provenance

- Canonical PNG SHA verified: **True**
- Literal obsolete small-sails y band: **[360, 480]**
- Synthetic controls: **40/40**.
- Original + lossy variants: 3 thresholds x 4 renderings = **12** measured conditions per sail.
- All real source sails have >=200 dark ink px in every setting: **True**.
- Material ink omission (>=25% excluded in ALL 12 settings): **4/5**.
- Decision: **LEGACY_SMALL_SAIL_BAND_MATERIALLY_TRUNCATES_TRUE_SAILS**.

| True sail | Fixed apex/base y | Geometric area excluded | Ink excluded (original, threshold 110) | Ink excluded (original, threshold 170) | Ink excluded (original, threshold 210) | Stable across 12 |
|---|---|---:|---:|---:|---:|---|
| sail1 | 448–546 | 92.1% | 92.7% | 91.8% | 91.6% | True |
| sail2 | 433–532 | 80.3% | 75.8% | 77.0% | 77.7% | True |
| sail3 | 411–514 | 56.9% | 54.9% | 55.3% | 55.8% | True |
| sail4 | 397–498 | 33.0% | 30.8% | 31.5% | 31.4% | True |
| sail5 | 357–463 | 0.0% | 0.0% | 0.0% | 0.0% | False |

## Static dependency search (read-only)

- Tool/workflow files scanned: **212**.
- Exact small_sails_band_y field references outside this audit script: **4**.
- Generic geometry.json references outside this audit script: **68**.
- These are TEXT matches only; do not infer that a recorded workflow used the obsolete band.

### Exact field usages
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage12_count_perimeter.py:86: y0,y1=geom["small_sails_band_y"]
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage19_small_sail_remeasure.py:126: y0,y1=map(int,g["small_sails_band_y"])
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage15_semantic_321_counts.py:76: y0,y1=geom["small_sails_band_y"]
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage23_bitplane_statistics.py:47: s=g["large_sailboat"]; y0,y1=g["small_sails_band_y"]

### Generic file usages (investigation only)
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage91_historical_clue_reconciliation.py:231: p in ("analysis/tested.md","README.md","data/geometry.json","puzzle.json")
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage103_building_roof_profiles.py:32: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage5_visual_structure.py:11: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage35_building_reflection_coupling.py:25: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage132_large_sail_legacy_bbox_audit.py:25: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage132_large_sail_legacy_bbox_audit.py:184: "scope":"manual fixed large sail and hull silhouettes + old data/geometry.json ROI, 3 thresholds, original/JPEG85/JPEG70/resampling",
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage139_reflection_coverage_audit.py:46: GEOMETRY=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage111_sail_skyline_alignment.py:23: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage12_count_perimeter.py:16: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage10_marker_robustness.py:17: GEOM = ROOT / "data" / "geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage3_marked_grayscale.py:128: # Bounded hashes of the marked boat region. The geometry box is from data/geometry.json;
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage150_v_facade_lower_h_perturb.py:37: GEOMETRY=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage95_grayscale_16level_alphabet.py:36: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage121_building_hatch_line_counts.py:23: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage17_orientation_geometry_independence.py:7: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage19_small_sail_remeasure.py:16: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage148_hv_building_aspect_confounds.py:40: GEOMETRY=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage18_small_sail_sequence.py:7: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage15_semantic_321_counts.py:19: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage6_321.py:23: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage94_large_sail_stroke_carrier.py:19: GEOM=ROOT/"data"/"geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/fig_geometry.py:9: measurement. Every box comes from data/geometry.json; nothing here is invented.
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/fig_geometry.py:24: data/geometry.json (measured bounding boxes)
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/fig_geometry.py:36: DATA_FILE = ROOT / "data" / "geometry.json"
- 2-mid-prizes/arweave-puzzle-11-1eth/tools/stage16_321_coding_audit.py:15: GEOM=ROOT/"data"/"geometry.json"

## Interpretation limits

The five sail polygons were fixed by past verified source work. A confirmed stale geometric description should be kept as historical provenance and not silently overwritten.
Four of five known sail bases are BELOW the old band; the Stage155 dark-ink measurement independently quantifies how much of the original pencil drawing was omitted.
The old small sail widths and wrong source object from Stage112 are separate earlier corrections; Stage132's large-sail bbox defect is also separate.
No statement about secret encoding, wallet access or solver progress is justified by this audit.
Source crop comparison: five-sails-versus-legacy-band.png (raw crop at left, guides at right).
