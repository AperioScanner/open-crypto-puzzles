# Research state — Arweave Puzzle #11

Last updated: 2026-10-01

## Objective

Find a 32-byte secp256k1 private key whose standard Ethereum address is exactly:

`0xFF2142E98E09b5344994F9bEB9C56C95506B9F17`

Success requires an exact address match. Prefix or partial matches are not evidence of success.

## Safety / handling

- Never broadcast a transaction.
- Never publish a discovered private key.
- If an exact match is found, stop the search and record only that an exact cryptographic match was found plus non-secret verification metadata.


## Current assistant research boundary

The active ChatGPT work on this branch is limited to non-secret research: public-clue recovery, visual semantics, image/steganography diagnostics, statistical structure, historical comparison, and reproducible code/tests that do **not** generate, derive, enumerate, or verify candidate private keys against the funded wallet. Historical experiments already present in this branch may contain address-verification counts; they are retained as prior work but are not extended by the active assistant scope.

## Canonical artifact

- Image: `clues/arweave-puzzle-11.png`
- Expected SHA-256: `c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1`
- Arweave tx: `CzITHnEIlkQw9SbaX5futCzFrKk1qe_NwvWnIBmP2fY`

## Existing knowledge

Read before adding experiments:

1. `README.md`
2. `analysis/tested.md`
3. `analysis/leads.md`
4. `clues/author-posts.md`
5. `puzzle.json`

The existing fork already includes substantial negative work: geometry and metadata families, alpha inspection, 7,168 pixel bitstreams for ASCII/compressed payloads, 79,863 unique valid scalars from first-row 256-bit windows, barcode scans, and 1,488 HD derivations from one skyline transcription.

## Research protocol

Every new experiment must record:

| Field | Requirement |
|---|---|
| ID | Stable identifier, e.g. A11-EXP-001 |
| Hypothesis | What encoding is being tested |
| Evidence | Why the hypothesis is plausible |
| Scope | Exact search space |
| Method | Reproducible decoding procedure |
| Controls | Synthetic/known-good checks |
| Result | Exact-match count and candidate count |
| Coverage limit | What remains untested |
| Artifacts | Script/report paths |
| Date | UTC or local date |

Do not rerun an exhausted scope unless the previous experiment is shown to be incomplete or incorrect.

## Current priority

### P1 — identify a format-invariant visual carrier using known public information

Stage 31 decisively favors the visual/semantic route: the robust 12-building H/V texture survives all tested lossy JPEG/resampling variants at 12/12 under two independent classifiers, while exact foreground bit-0 agreement collapses to ~0.52–0.55.

The author also said the **public escrow address** is present somewhere in the image. Because that 160-bit value is already known and public, it can be used as a known-answer probe to discover the carrier mechanism without generating or verifying private-key material.

Stage 32 tests the simplest dimension-motivated visual hypothesis: image width 1600 px = 160 address bits × 10 px, using only coarse visible features, lossy-reproduction requirements, and familywise null calibration.

### P2 — retain the H/V texture without forcing `0x321`

The sequence `HHVVHHVHHHHV` remains a strong reproducible visual feature. The hexadecimal `0x321` interpretation was retired in Stage 22 due to grouping/representation look-elsewhere effects. H/V may still act as a selector, ordering clue, or semantic signal.

### P3 — solved-puzzle visual grammar

Use human-readable semantics, tiny secondary details, counting, rebuses, selection, and ordered interpretation as the main prior for future visual hypotheses.

### P4 — archival context

The mirrored #11 launch window is exhausted. Remaining archival value is in external early discussion or a first-hand account of Puzzle #9's solve method.

## Stop conditions

Stop and request review if:

1. a new clue materially changes the safe hypothesis space;
2. a planned scope becomes computationally unreasonable without justified reduction;
3. a proposed experiment would duplicate an exhausted scope;
4. the next step would require generating, deriving, reconstructing, enumerating, or verifying candidate private keys or attempting wallet access.


## 2026-10-13 — superseding operating scope

The user instructed: stop exploring Twitter/external social references, concentrate strictly on the image. Stage 119 archival-source partial coverage is shelved rather than called a negative. Stage 120 tests only repeated stroke templates among five independently localized small-sail regions in the canonical image. Preserve previous negative scopes and controls. Do not enumerate, derive, test, validate or reconstruct BIP39 mnemonic phrases, private keys or funded-wallet access.

## 2026-10-14 — Current verified source-research stop after Stage165 (supersedes older Stage32 prioritization)

- Work is exclusively NON-SECRET, canonical-source visual/geometry/method QA. Do not derive, enumerate, verify or reconstruct any private key, mnemonic, funded-wallet access or new candidate public-address matching. Do not reopen Twitter/social/outside-image source archaeology. The initial P1 known-address probe text above is HISTORICAL, not the active assistant directive.
- Latest scientific stage: Stage165 Actions #38647720314 SUCCESS. Confirmed source/controls 13/13 plus numerical 7/7, no significant base sail width vs following gap correlation (exact original p=.616667). Previous stage164 verified Stage112 original partial width windows omitted significant real ink in 3/5 sails; stage163 verified 24/50 original superbatch source defects; stage162 retested the genuinely full main sail for 16-tone structure and found none with 22/22 calibrated controls.
- Strongest descriptive original image feature remains 12 building hatch orientation HHVVHHVHHHHV. Its 0x321 reading has no independent support and Stage22 withdrew code-interpretation priority. No intentional message or puzzle solution has been authenticated. No Stage166 justified absent genuinely independent visual observation/implementation defect. GitHub branch research/arweave11-chatgpt preserves full reports.

## 2026-10-14 — Stage168 latest completed: stop on unresolved true sail-foot boundary

Stage166 #38648679111 numerical synthetic uncertainty (16/16 controls) demonstrates Stage165 p=.616667 can change under some hypothesized ±4px endpoint annotations (33/3125 unique width sets), not a real-image discovery. Repaired Stage167 #38649376400 passed 160/160 shifted-line/blank controls, but pixel source scores favored 3 inner shifted rays, only 1 exact original and 6 unresolved feet. Stage168 #38649693254 passed 12/12 original pixel provenance checks; a qualitative assistant view of raw-vs-guide contact suggests shifted rays are interior hatching rather than reliable EXTERIOR sail boundaries; no independent human-certification claim, no new corrected base coordinates. No original image encoded message or wallet solution was verified, and no Stage169 is justified solely by existing numerical fragility. GitHub branch research/arweave11-chatgpt retains all source/case reports; secret key/address/mnemonic and social research remain prohibited in active work.

## 2026-10-14 — Latest reviewed stage 170 (supersedes earlier image-source stop statements)

Stage169 #38651453418 original-source fixed outside-white/inside-dark flank test PASSED 128/128 synthetics and 6/6 provenance, but source decisions conflicted (sail5 right original0 supported, sail4 right inward-8 supported; sail2 right/sail3 left unclassified). Stage170 #38651782990 proved exact original pixel replay and raw-contact integrity 15/15; assistant-only visual review found hull/hatching confounds and no independently certified corrective footpoint positions. The Stage165 annotation-specific p=.616667 is unchanged; Stage166 theoretical sensitivity to +/-4px remains a caution, not a new discovery. Source original image is unmodified and no solution, key, BIP39 mnemonic, wallet address, or author-intended code is verified. Further Stages require independent falsifiable picture evidence, not tuning offsets to make a numerically significant target. Active scope stays canonical image and NONSECRET visual research only, no social/external source or wallet operations.

## 2026-10-14 — Stages171 and 172 closed: synthetic-overlap abstention, no source-boundary resolution

Most recent verified workflow Stage172 #38653841075 GitHub SUCCESS, 13/13 controls and 352 SOURCE-BLIND synthetic known-truth grayscale neighbor stroke doses. Original Stage169 outer-edge contrast classifier correctly labels clean controls and abstains more often with nearby synthetic boat ink, including at pale gray in some fixed scenes; 0 confidently wrong edges. Preceding Stage171 #38653441187 PASS 12/12 source/fixture QA and replays Stage169 128/128 clean tests; 96/96 stronger exterior neighboring boat strokes cause abstention. These synthetic studies do not establish the original illustrator's exact sail footpoints or any prize secret. Original source Stage169 mixed and Stage170 original pixel-verified contact 15/15 remain unchanged. Stage165 old hand-annotation p=.616667 not recomputed. Research remains NONSECRET image/geometry only; do not undertake wallets, seed or BIP39 address matching or external/social investigation. No Stage173 yet: require independent canonical picture feature or confirmed important implementation defect.

## 2026-10-14 — Latest verified Stage174 actual masthead retest; source defect in historical Stage126 closed

Stage173 #38659613143 verified a specific source/fixture masthead geometry mismatch: historical Stage126 real-tip detector looked 3..17 pixels BELOW actual five sail apices but its synthetic controls looked ABOVE artificially low generated tips (12/12 geometry controls). Stage174 #38659851003 repaired ONLY the shared calibration/source coordinate frame by using tip-24 virtual top with otherwise exact original detector; 180/180 known positive/negative side-decoy calibration and 9/9 source provenance controls pass. All five canonical original above-apex window classifications stable ABSENT across four format transformations and x±2 pixels. This invalidates interpreting Stage126 old 4/5 EXTENDED as actual masthead protrusions; it does NOT exclude subtler or off-center artwork beyond the fixed detector. Other image carriers remain unverified; puzzle remains unsolved. No new Stage175 unless independent source clue or method defect. Active GitHub branch research/arweave11-chatgpt only. No private keys, address comparisons, mnemonics, wallet actions or off-image/social work.

## 2026-10-14 — Latest verified Stage177 radial source scope; no decoded clue

Stage175 #38660475315 SUCCESS 18/18 code/geometry control checks: historical Stage105 had synthetic ray count calibration failure and mistakenly anchored 3/5 sail apexes far from real source tips. Stage176 #38660822377 successful workflow with 240/240 new synthetic known-count controls but INSUFFICIENT_REAL_SAIL_PROFILE_COVERAGE (18/20 source occupancy checks and some measured peaks beyond calibrated n3..7). Stage177 #38661236139 24/24 known-connected-vs-lower-only synthetic controls, 6/6 source provenance, disjoint upper real-pencil checks of two n8-profile source sails did not establish >=6/8 continuing upper ridges (sail1 0/8 and sail2 4/8 original; less/unstable under transformed variants). Official source decision INCONCLUSIVE_UPPER_TRACE_CORROBORATION. The recovered count is not a validated physical radial line count or authored message. No Stage178 simply to seek codes; a new independent original-image observation or reproducible important detector error is needed. Active research stays canonical image and NONSECRET visual analysis only, no private key, mnemonic, addresses, wallet or social/external sources.
