# Stage 31 — format-invariance audit

**Experiment:** A11-EXP-031

| variant | Fourier agree | Morph agree | fg bit0 agree | fg-sky bit0 agree | mean abs pixel delta |
|:---|---:|---:|---:|---:|---:|
| original | 12/12 | 12/12 | 1.0000 | 1.0000 | 0.000 |
| jpeg_q95 | 12/12 | 12/12 | 0.5513 | 0.5485 | 0.525 |
| jpeg_q85 | 12/12 | 12/12 | 0.5507 | 0.5471 | 1.528 |
| jpeg_q70 | 12/12 | 12/12 | 0.5507 | 0.5470 | 2.789 |
| down75_up | 12/12 | 12/12 | 0.5270 | 0.5258 | 7.339 |
| up125_down | 12/12 | 12/12 | 0.5296 | 0.5278 | 2.920 |
| jpeg85_down75_up | 12/12 | 12/12 | 0.5230 | 0.5228 | 7.576 |

- Visual H/V stability rule: **True**
- Low-bit-collapse rule: **True**
- Promote format-invariant visual/semantic route: **True**

## Interpretation

If the H/V texture survives lossy conversion/resampling while exact bit-0 agreement collapses, that supports prioritizing visible/semantic image structure over fragile exact-pixel LSB encoding. This is route-selection evidence, not proof that H/V itself is the hidden carrier.
