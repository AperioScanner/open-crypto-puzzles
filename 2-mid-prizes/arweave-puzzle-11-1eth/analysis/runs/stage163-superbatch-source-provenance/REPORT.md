# Stage163 — fixed original superbatch object ROI dependency audit

- Canonical SHA verified: **True**
- Predeclared source / manifest / replication guards: **7/7**
- Old superbatch directly using demonstrated bad source regions: **24/50**
- Affected source-scope tests: **20/42**
- Affected historical source-scope controls: **4/8**
- Old nominal uncorrected source-dependent results: **['A11-EXP-043', 'A11-EXP-061']**
- Stage88 failed original-scope replication also depends on bad ROIs for 43,61: **True**
- Decision: **VERIFIED_LEGACY_SUPERBATCH_OBJECT_CROP_SCOPE_DEFECT**

| Group | Directly affected old stages | Footprint defect |
|---|---|---|
| Main giant sail metrics | 37–46, 73 and controls 80,85,86 | Stage132 incomplete large_sailboat box |
| Five small sail metrics | 55–62, 74 and control 84 | Stage155 truncated y strip; Stage112 false object set |

NOTE: Stage87's 42 original BH-FDR results and Stage88's old-scope p-values were NOT recomputed. No result is promoted by this provenance audit. Unaffected means only NOT in the two exact dependency categories; it is not proof of perfect localization.

No keys, wallets, guesses, phrases or outside source searches.
