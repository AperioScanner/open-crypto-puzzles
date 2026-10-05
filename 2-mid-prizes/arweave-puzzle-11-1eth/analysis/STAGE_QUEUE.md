# Arweave Puzzle #11 — adaptive controller + approved superbatch

Last updated: 2026-10-05

## Stage 36 review

Stage 36 completed successfully on 2026-10-04. The large-sailboat visual-text hypothesis was **not promoted**:

- 19 fixed reveal transforms
- target rank-1 on original image: **0**
- target rank-1 after lossy conversion: **3**
- rank-1 transforms replicated original→lossy: **0**
- manual-review priority rule: **False**

**Decision:** do not spend another serial stage on the large-sailboat text idea. Treat it as a negative result.

## Orchestration correction

The hourly ChatGPT controller is enabled again. It had been disabled during manual steering and therefore did not review Stage 36 automatically. The approved next action is the user's requested large independent battery.

## Superbatch 37–86

Run **50 bounded, non-secret experiments** in one GitHub Actions job, followed by aggregate experiment **87**.

The batch intentionally contains independent or semi-independent diagnostics that can all be selected from evidence available through Stage 36; none depends on the result of another subexperiment.

Families:

- **37–46:** large-sailboat structural uniqueness vs matched windows
- **47–54:** skyline ↔ water scene/reflection structure
- **55–62:** small-sail arrangement geometry
- **63–70:** ordered building-geometry structure
- **71–78:** semantic-region visual/glyph structure
- **79–86:** lossy-format robustness/negative controls
- **87:** aggregate ranking with Benjamini–Hochberg FDR, family labels, and promotion/interested/null classifications

No subexperiment may generate, derive, enumerate, reconstruct, or verify candidate private keys or attempt wallet access.

## Status

- Stages 1–36: completed.
- Stage 36: COMPLETED + REVIEWED — NEGATIVE.
- Superbatch 37–86: APPROVED / being launched.
- Aggregate 87: follows automatically inside the same workflow.
