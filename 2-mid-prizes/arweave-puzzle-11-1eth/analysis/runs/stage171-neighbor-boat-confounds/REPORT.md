# Stage171 — synthetic adjacent boat/hull dark stroke confound audit

- Canonical PNG SHA provenance only: **True**
- Original Stage169 clean synthetic replay: **128/128**
- Structural/adversarial integrity controls: **12/12**
- Clean two-true-edge controls: **32/32**
- Adversarial synthetic cases: **96**
- False source-EDGE accepted under known-wrong candidate: **0/96**
- Correct: **0**, unresolved: **96**
- False edge accepted in all four formats for a precommitted scene: **0**
- Scientific decision: **STAGE169_NEIGHBOR_NUISANCE_CAUSES_CLASSIFICATION_LOSS**

| Exterior nuisance | Known cases | Correct | False edge confidently accepted | Unresolved |
|---|---:|---:|---:|---:|
| outside_parallel_11 | 32 | 0 | 0 | 32 |
| outside_cross_20_to_4 | 32 | 0 | 0 | 32 |
| outside_gray_boat_wedge | 32 | 0 | 0 | 32 |

Known truth is defined by SYNTHETIC geometry; this test does not measure or reclassify any actual photo/sail pixels. The four JPEG/PNG formats are repeated transformations of the same fixture, not independent artwork. Do not feed any Stage169 inwards into Stage165 or claim a secret.
