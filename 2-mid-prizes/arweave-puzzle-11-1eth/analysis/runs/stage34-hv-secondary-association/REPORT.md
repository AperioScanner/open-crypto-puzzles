# Stage 34 — H/V selector × secondary-detail association audit

**Experiment:** A11-EXP-034

- Fixed H/V sequence: `HHVVHHVHHHHV`
- V buildings: **[3, 4, 7, 12]**
- Exact label permutations: **495**
- Projection-periodicity features are excluded to avoid circularity with hatch orientation.

## Per-feature exact tests

| feature | H mean | V mean | abs diff | exact p | Bonferroni p |
|:---|---:|---:|---:|---:|---:|
| small_component_density | 22.388533 | 31.752614 | 9.364081 | 0.4101 | 1.0000 |
| small_component_instability_ratio | 0.300357 | 0.238163 | 0.062194 | 0.4465 | 1.0000 |
| mid_component_density | 1.456713 | 1.390865 | 0.065848 | 0.9071 | 1.0000 |
| perimeter_w2 | 0.365892 | 0.330249 | 0.035643 | 0.3475 | 1.0000 |

## Multivariate exact tests

- observed within-class SSE: **45.533284**, exact lower-tail p = **0.7010**
- observed H/V centroid distance²: **0.925019**, exact upper-tail p = **0.7010**
- promotion rule satisfied: **False**

## Interpretation

The fixed H/V labels do not organize the Stage-12 secondary-detail measurements strongly enough under exact permutation testing. Keep H/V as a real format-stable visual pattern, but downgrade the specific hypothesis that it selects a second channel of counted building details.

A positive association would still require visual replication because connected-component statistics can partly reflect drawing construction rather than intentional coding.
