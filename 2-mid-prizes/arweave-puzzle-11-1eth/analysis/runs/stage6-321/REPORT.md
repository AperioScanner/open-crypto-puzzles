# Stage 6 — following the skyline 0x321 lead

The visually robust building sequence is HHVV HHVH HHHV. Taking H=0 and V=1 gives 0011 0010 0001 = 0x321; the complement gives 0xCDE.

This stage tested literal 3-2-1 bit-plane interpretations only as a bounded follow-up, not as an arbitrary sliding-window brute force.
- Unique 32-byte candidates generated: 1317
- Valid secp256k1 scalars checked: 1258
- ff21 two-byte prefix near-misses: 0
- Exact target match: false

## Format-invariance check

| JPEG quality | skyline sequence | preserved? | exact low-3 fraction | exact gray fraction |
|---:|:---|:---:|---:|---:|
| 95 | HHVVHHVHHHHV | True | 0.7233 | 0.7232 |
| 85 | HHVVHHVHHHHV | True | 0.6928 | 0.6753 |
| 70 | HHVVHHVHHHHV | True | 0.6904 | 0.6619 |
| 50 | HHVVHHVHHHHV | True | 0.6837 | 0.6511 |

Diagnostic images render bit planes 0-3, the natural/reversed low-three-bit residual, 3-2-1 false colour, 4-3-2 false colour and the top three MSBs.

Interpretation: if the skyline really is an intentional 0x321 marker, it may be an instruction rather than key material. The tests above cover only the most literal bit-plane reading.
