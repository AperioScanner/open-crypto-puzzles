# Stage 91 — historical solver-clue reconciliation

**Experiment:** A11-EXP-091

- StackExchange records recovered: **12**
- Historical claims audited: **10**
- Status counts: **{'RETIRED_BY_LATER_EVIDENCE': 3, 'COVERED': 4, 'PARTIAL': 1, 'UNTESTED': 2}**

## Reconciliation

| claim | status | priority | repo evidence paths |
|:---|:---|---:|:---|
| sketch may derive from an identifiable source photograph | **UNTESTED** | 5 |  |
| pier/supports resemble X / IX / XI Roman numerals | **UNTESTED** | 3 |  |
| Arweave/file identifier decodes to 32 bytes | **COVERED** | 2 | tools/stage3_marked_grayscale.py |
| 5 buildings left / 7 buildings right | **PARTIAL** | 2 | analysis/tested.md |
| create/modify timestamps differ by 203 seconds | **RETIRED_BY_LATER_EVIDENCE** | 1 |  |
| alpha anomalies/ring around large boat | **RETIRED_BY_LATER_EVIDENCE** | 0 | analysis/tested.md, analysis/STATE.md, tools/stage3_marked_grayscale.py, tools/stage6_321.py |
| 1 large boat / 5 small boats | **COVERED** | 0 | analysis/tested.md, analysis/runs/stage88-superbatch-survivor-replication/result.json, analysis/runs/stage36-large-boat-visual-reveal/result.json, analysis/runs/stage19-small-sail-remeasure/REPORT.md |
| buildings alternate horizontal/vertical hatch directions | **COVERED** | 0 | analysis/tested.md, analysis/STATE.md, analysis/runs/stage17-orientation-geometry-independence/REPORT.md, analysis/runs/stage17-orientation-geometry-independence/result.json |
| reverse-image search leads to CryptoCanvas/OpenSea | **RETIRED_BY_LATER_EVIDENCE** | 0 | analysis/runs/stage90-cryptocanvas-closure/REPORT.md, analysis/runs/stage90-cryptocanvas-closure/result.json, analysis/runs/stage89-cryptocanvas-provenance/REPORT.md, tools/stage89_cryptocanvas_provenance.py |
| anomalous first image row | **COVERED** | 0 | analysis/runs/stage7-first-row-steg/REPORT.md, analysis/runs/stage9-first-row-structure/REPORT.md, analysis/runs/stage90-cryptocanvas-closure/REPORT.md, analysis/runs/stage12-count-perimeter/REPORT.md |

## Ranked genuinely untested claims

1. **sketch may derive from an identifiable source photograph** (`source_photo_hypothesis`, priority 5)
2. **pier/supports resemble X / IX / XI Roman numerals** (`pier_roman_numeral`, priority 3)

## Interpretation

This stage is a source/coverage delta audit, not a solve. It prevents recycling historical ideas already exhausted in the branch and identifies which public observations, if any, still justify a bounded visual/semantic experiment.

No private-key material was generated, reconstructed or tested.
