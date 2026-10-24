# Stage184 — fixed synthetic full-canvas transform frame check

- Checks: **20/20**
- Global n16 valid negative: **True**
- Global n64 positive full gate: **True**
- Global n256 positive full gate: **False**
- Decision: **MAX_MATCH_ONLY_NOT_ORIGINAL_GATE**

| Known marks | Mode | Original | JPEG85 | JPEG70 | Resize | Resize matched original | Full old gate |
|---:|---|---:|---:|---:|---:|---:|---|
| 16 | ROI-local | 15 | 16 | 15 | 15 | 15/15 (1.0000) | False |
| 16 | Full-canvas | 15 | 16 | 16 | 15 | 15/15 (1.0000) | False |
| 64 | ROI-local | 48 | 46 | 51 | 42 | 37/48 (0.7708) | True |
| 64 | Full-canvas | 48 | 49 | 51 | 44 | 37/48 (0.7708) | True |
| 256 | ROI-local | 89 | 97 | 79 | 64 | 46/89 (0.5169) | False |
| 256 | Full-canvas | 89 | 88 | 88 | 73 | 48/89 (0.5393) | False |

No natural image pixels or ordered strokes were examined. Four encodings derive from the same artificial image. A successful positive fixture is not evidence of an intentional message in the real puzzle.
