# Stage 19 — independent small-sail remeasurement

**Experiment:** A11-EXP-019

Fixed band y=360..480; x<367 excluded because it belongs to the already-measured large sailboat.
Thresholds: [70, 85, 100, 110, 120, 135, 150, 165, 180].
Prior Stage-18 widths: [27, 53, 79, 83, 51].

## connected_components_close3

- Stable tracks: **5**
- Stable centers left→right: [675.5, 1046.5, 1144.5, 1269.5, 1361.0]
- Stable widths left→right: [80, 29, 56, 84, 85]
- First-three diagnostic: {'widths': [80, 29, 56], 'differences': [-51, 27], 'ap_error': 78}
- Prior comparison: {'comparable': True, 'prior': [27, 53, 79, 83, 51], 'remeasured': [80, 29, 56, 84, 85], 'signed_differences': [53, -24, -23, 1, 34], 'max_abs_difference': 53}

## vertical_projection_runs

- Stable tracks: **5**
- Stable centers left→right: [671.5, 1046.5, 1145.0, 1268.0, 1361.0]
- Stable widths left→right: [76, 28, 54, 81, 83]
- First-three diagnostic: {'widths': [76, 28, 54], 'differences': [-48, 26], 'ap_error': 74}
- Prior comparison: {'comparable': True, 'prior': [27, 53, 79, 83, 51], 'remeasured': [76, 28, 54, 81, 83], 'signed_differences': [49, -25, -25, -2, 32], 'max_abs_difference': 49}

## Pre-registered decision

- Both independent methods support +26,+26 within ±3 px: **False**

## Interpretation

The Stage-18 +26,+26 progression does not replicate across both independent segmentation families. It is therefore downgraded as a likely measurement/segmentation artifact rather than an author clue.

No alphabet/modulo interpretation is inferred by this experiment.
