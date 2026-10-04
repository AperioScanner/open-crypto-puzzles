# Stage 28 — traversal anomaly null calibration

**Experiment:** A11-EXP-028

- Fixed Stage-27 candidate streams: **12**
- 32×32 block-shuffled surrogates: **100**
- Observed max printable fraction: **0.109059** (empirical p=0.0099)
- Observed max printable run: **8** (p=0.8416)
- Observed min zlib ratio: **0.464995** (p=0.0099)
- Observed streams with specific multi-byte magic: **0** (p=1.0000)
- Promotion rule satisfied: **True**

## Interpretation

At least two independent traversal metrics are unusually extreme relative to matched block-shuffled surrogates, or a specific multi-byte signature is exceptional. The next stage should localize and reproduce that traversal anomaly.

One-byte JSON markers from Stage 27 are explicitly excluded because they generate chance hits.
