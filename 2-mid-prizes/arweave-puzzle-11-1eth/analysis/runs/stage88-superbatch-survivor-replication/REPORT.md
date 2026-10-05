# Stage 88 — adversarial replication of superbatch survivors

**Experiment:** A11-EXP-088

The 37–86 superbatch produced three nominally interesting results but none survived FDR. This stage tests exactly those three with stricter, independent controls.

| candidate | original p | primary confirmation p | Holm p | family gate | confirmed |
|:---|---:|---:|---:|:---:|:---:|
| A11-EXP-043 | 0.033149 | 0.071713 | 0.215139 | False | False |
| A11-EXP-050 | 0.031056 | 0.682990 | 1.000000 | False | False |
| A11-EXP-061 | 0.039980 | 0.566667 | 1.000000 | False | False |

## A11-EXP-043 — large-boat vertical projection

- nuisance-matched original p: **0.071713**
- nuisance-matched lossy p: **0.051793**
- matched same-size windows: **250**

## A11-EXP-050 — rightmost reflection

- original high-pass p: **0.621134**
- original edge p: **0.322165**
- lossy high-pass p: **0.682990**
- lossy edge p: **0.399485**
- fixed half-band grayscale p-values: **[0.047872, 0.797872]**

## A11-EXP-061 — small-sail width/gap correlation

- connected_components_close3: |r|=0.444939, exact p=**0.533333**
- vertical_projection_runs: |r|=0.429893, exact p=**0.566667**
- Stage-61 detector components matching a Stage-19 stable center within 40px: **3/5**

## Decision: confirmed survivors = **[]**

No candidate is promoted merely for having been nominally significant in the superbatch. The next stage must follow the actual confirmation result.
