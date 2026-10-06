# Arweave Puzzle #11 — adaptive controller

Last updated: 2026-10-06

## Anti-recycling rule

Do **not** reopen a hypothesis classified COVERED, RETIRED, or independently falsified unless one of these is true:

1. a concrete implementation defect is demonstrated in the earlier test; or
2. genuinely new independent evidence changes the hypothesis.

Historical popularity alone is not a reason to retest an exhausted idea.

## Review through corrected Stage 91

The first Stage-91 audit had a self-reference bug: claims mentioned in the current controller/leads/worklog or in the Stage-91 script itself were incorrectly counted as prior coverage. That implementation was fixed and Stage 91 rerun under the same stage number.

Corrected reconciliation:

- **RETIRED_BY_LATER_EVIDENCE: 3**
- **COVERED: 4**
- **PARTIAL: 1**
- **UNTESTED: 2**

### Genuinely untested historical claims

1. **Source-photo hypothesis** — a public 2021 solver suggested the harbor sketch may derive from a real photograph, noting that another puzzle in the series used a photo-context mechanism. No prior branch stage/tool directly tests photo provenance.
2. **Pier/supports as X / IX / XI Roman numerals** — objective visual interpretation has not been directly tested, but the historical evidence is weaker and explicitly speculative.

### Partial, not fresh

- **5 buildings left / 7 buildings right** — the count was already included in the broad historical geometry/object-count sweep, but not independently supported as a semantic instruction. Keep secondary; do not prioritize it over genuinely untested claims.

### Already covered/retired

- alpha ring/halo
- anomalous first row
- H/V building hatching
- 1 large + 5 small boats
- 203-second timestamp anomaly
- Arweave identifier decoding to 32 bytes (explicitly tested in Stage 3)
- CryptoCanvas reverse-image lead (closed as a July-2020 post-publication mirror)

## Next stage

**Stage 92 — source-photo candidate audit.**

Motivation:
- this is the highest-priority genuinely untested public historical claim;
- it fits the author's instruction to look at solved puzzles and the series' use of external semantic context;
- it is independent of the heavily exhausted pixel/LSB/HV/statistical families.

Bounded scope:
1. Fetch the exact historical candidate page linked by the solver: `https://courageoussailing.org/sailing/racing/`.
2. Query Internet Archive CDX for 2019–2021 snapshots of that page and recover page-image candidates where possible.
3. Query a small public Wikimedia Commons candidate pool for Boston Harbor / sailing-race / skyline images.
4. Compare candidates to the canonical sketch using geometry-focused methods tolerant of photo→drawing style change:
   - SIFT/ORB feature matching on Canny/line representations;
   - RANSAC homography inlier counts/fractions;
   - coarse edge-layout correlation.
5. Include a transformed canonical-image positive control to prove the geometric matcher works.
6. Pre-register a strong-match gate requiring agreement across independent geometry metrics; do not promote weak semantic resemblance by eye.

A negative result retires the **specific linked/Boston candidate pool**, not the global possibility that some unknown photograph exists.

## Status

- Stages 1–91: completed.
- Corrected Stage 91: COMPLETED + REVIEWED.
- Stage 92: selected for launch.
