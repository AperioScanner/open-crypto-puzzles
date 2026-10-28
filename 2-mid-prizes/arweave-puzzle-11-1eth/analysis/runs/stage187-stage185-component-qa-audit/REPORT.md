# Stage187 — Stage185 composite-component QA protocol audit

- Archive/provenance/fresh-counter checks: **13/13**
- Previously archived Stage185 sites reviewed: **45**
- False Stage185 multi-component QA assertions: **10**
- Decision: **STAGE185_COMPOSITE_COMPONENT_QA_MISMATCH_CONFIRMED**

| Old fixture family | Sites | Composite-flag mismatches |
|---|---:|---:|
| curved | 15 | 10 |
| broken | 15 | 0 |
| curved_broken | 15 | 0 |

The Stage185 code checks separate line supports and then labels their
count as a composite >=2 connected-component/contour guard. Its
preregistered condition concerned connected features in the composed
object. Passing Stage185's 44/44 QA therefore does **not** verify that
specific preregistered composite condition. It does not invalidate the
prior finding that positive recovery was inadequate; no Stage185
criterion, report, code, or source-derived claim was revised.

The 45 old synthetic cases are in-sample protocol audits, NOT
independent scientific holdouts. No natural-image pixels were read.
No clue, message, cryptographic or wallet inference is supported.
