# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-05

## Control loop

1. GitHub Actions executes a bounded experiment.
2. The stage commits non-secret `REPORT.md` + `result.json`.
3. ChatGPT reads the actual result before choosing the next adaptive experiment.
4. Failed implementations are fixed under the same stage number.
5. No private-key generation, derivation, reconstruction, enumeration, verification, or wallet access.

## Review through aggregate Stage 87

The approved superbatch A11-EXP-037..086 completed successfully, followed by aggregate A11-EXP-087.

Aggregate result:
- 50 subexperiments
- 42 FDR-tested hypotheses
- **0 PROMOTED**
- **3 INTERESTING**
- **39 NULL**
- 7 control passes, 1 control failure, 0 errors

Nominal survivors:
1. **A11-EXP-050** — rightmost grayscale reflection correlation, p=0.031056, q=0.425414
2. **A11-EXP-043** — large-boat vertical projection peak, p=0.033149, q=0.425414
3. **A11-EXP-061** — small-sail width vs following-gap correlation, p=0.039980, q=0.425414

None survives FDR. They are therefore leads for falsification/replication, not discoveries.

## Adaptive decision — Stage 88

**A11-EXP-088: adversarial replication of exactly the three nominal survivors.**

The purpose is to determine whether any of the three persists under an independent, stricter control rather than continuing directly from a nominal p-value.

### EXP-043 confirmation
Re-test the large-sail vertical-projection statistic against **same-size nuisance-matched windows**, matched only on mean darkness, ink fraction and edge density. Use the same matched controls after JPEG85+resampling.

### EXP-050 confirmation
The original grayscale reflection effect may be driven by broad tonal layout. Require replication after:
- high-pass removal of low-frequency tone;
- edge-only representation;
- two fixed 200px spatial halves;
- JPEG85+resampling.

### EXP-061 confirmation
Do not reuse the superbatch detector. Recompute width/following-gap correlation from both independent Stage-19 segmentation families and enumerate all 5! width permutations exactly.

### Multiple-testing rule
The three primary confirmatory p-values are Holm-adjusted. A lead survives only if:
- its family-specific replication gate passes; and
- Holm-adjusted p <= 0.05.

## Status

- Stages 1–36: completed.
- Superbatch 37–86: completed.
- Aggregate 87: completed + reviewed.
- Stage 88: launched.
- Hourly controller: enabled.
