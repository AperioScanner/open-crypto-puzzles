# Stage 26 — spectral and autocorrelation diagnostics

**Experiment:** A11-EXP-026

| channel | bit | peak/median | p99.9/median | peak dx,dy | top row lag | top col lag |
|:---:|---:|---:|---:|:---:|:---|:---|
| L | 0 | 33721.1 | 78.3 | (-1, -3) | (1, 0.9872948234723936) | (1, 0.9898281271511844) |
| L | 1 | 33616.3 | 81.1 | (1, 3) | (1, 0.9876416832705934) | (1, 0.9888122160587789) |
| L | 2 | 34245.3 | 85.4 | (-1, -3) | (1, 0.9879961317599817) | (1, 0.9889482196839677) |
| L | 3 | 35409.3 | 88.1 | (-1, -3) | (1, 0.9877022298481626) | (1, 0.9886772682770139) |
| A | 0 | 297.9 | 59.2 | (9, -5) | (1, 0.7014375509089236) | (1, 0.6559518930465053) |
| A | 1 | 154.2 | 58.8 | (9, -5) | (1, 0.7225475775471928) | (1, 0.5978937373040393) |

## Low-3 residual

- peak/median: 63512.3
- peak frequency offset: (-1, -3)
- strongest row lags: [(1, 0.9914478107703988), (2, 0.9830086291260466), (3, 0.9748533335758703), (4, 0.9692799000897969), (5, 0.9653718630756666)]
- strongest column lags: [(1, 0.9912679084920194), (2, 0.979738760154203), (3, 0.9682887062822504), (4, 0.9580519276714383), (5, 0.9475772109739882)]

## Interpretation

Strong spectral or lag peaks identify periodic/tiled structure worth localizing, but drawing strokes, scan/render artifacts and image dimensions can also create them. Peaks are leads only when they are unusual across multiple related planes or align with independent spatial anomalies.
