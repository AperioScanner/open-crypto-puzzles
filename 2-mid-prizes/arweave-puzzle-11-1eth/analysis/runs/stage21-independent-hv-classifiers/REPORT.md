# Stage 21 — independent H/V classifier replication

**Experiment:** A11-EXP-021

- Stage-5 baseline: `HHVVHHVHHHHV`
- Fourier anisotropy: `HHVVHHVHHHHV` — agreement **12/12**
- Morphological line response: `HHVVHHVHHHHV` — agreement **12/12**
- Jointly confirmed baseline labels: **12/12**
- Pre-registered replication rule satisfied: **True**

## Interpretation

The H/V skyline pattern survives two classifiers that do not reuse the Stage-5 signed-Sobel decision rule. This makes a classifier artifact less likely. It still does not validate the hexadecimal 0x321 interpretation.

Stage 22 will synthesize all 321-specific evidence and apply a stop rule before the research pivots to bit-level steganalysis.
