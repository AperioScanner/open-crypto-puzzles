# Stage153 source-corner audit — diagnostics, NOT a new Stage

- Canonical SHA-256 verified: c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1
- Original Stage153 decision unchanged: INSUFFICIENT_KNOWN_SAIL_JUNCTION_RECOVERY
- Original synthetic controls: 48/48.
- Original full 3-corner recovery on five known sails: 2/5.
- source-corner-audit.png: left crop = raw unedited pixel enlargement; right = separate arm-guide overlay.
- Distances are descriptions of alignment, not new gates, and DO NOT validate connectivity.
- Applying gray<215 is diagnostic only; the original gray<175 classifier is not changed.

| Original failing corner | Fixed vertex | Arm labels found | Median nearest ink to ideal arms px |
|---|---|---|---|
| sail1 #1 | (1042, 448) | [0, 1] | 3.07 / 0.55 |
| sail4 #1 | (1372, 397) | [0, 1] | 3.04 / 0.47 |
| sail4 #3 | (1414, 498) | [0, 1] | 4.00 / 0.00 |
| sail5 #3 | (1537, 463) | [1, 1] | 1.04 / 1.21 |
| under_pier #1 | (1052, 633) | [0, 1] | 2.24 / 0.51 |
| under_pier #2 | (1052, 778) | [0, 1] | 3.26 / 1.41 |

Interpretation limit: imperfect annotated vertices, sparse or curved pencil lines, faint ink, and genuinely disconnected lines can produce the same missing contact. Human comparison with source crops is required. A filled triangular sail is not automatically a perfectly joined three-edge outline.

No relaxed gates, new decoded message, key, mnemonic, wallet or external research.
