# Negatives ledger, Andy Bauch COG

Method for every row: a candidate reconstruction of the brick grid is decoded under the
stated hypothesis into a private key, both compressed and uncompressed P2PKH addresses are
derived, and each is compared byte-exact against `1HLodS8H2GoWbnBXWcz7EkY773dKdD4JEv` and
against 13 other addresses in the same series (some already solved, used as controls).
Acceptance requires exact address equality; a plausible-looking decoded string never counts
on its own.

| Hypothesis | Volume | Result | Witness | Date |
|---|---|---|---|---|
| Global tiling across the whole canvas (the method proven on the abstract "$N" pieces): a color-field offset scan (about 11,000 offsets per panel) plus a structural sweep over color count 2 to 32, character width 2 to 8, 8 reading orders, all offsets, and candidate lengths 30, 51 and 52 | tens of thousands of configurations across the 2 sweeps | 0 structurally valid candidates; period-30 multiples statistically indistinguishable from non-multiple control points | yes: the same detector finds the real, known periodic signal on other pieces in the series (BITCOIN $60, $70) and recovers a synthetic pattern reinjected after randomly repainting 85% of the grid | 2026 |
| Data inserted into one region of the image (the method proven on DOGECOIN $10 and CANNABISCOIN $10), 9 assumptions relaxed one at a time: cell size, region shape (103 shapes), panel overlap, white-as-symbol, minikey vs. hex, 16 reading orders, color count and character width pairs, repetition, 6 re-digitizations of the source images | about 2.3 million candidate windows, about 484 million decodings | 0 hits | yes: a known payload planted at signal-to-noise ratios up to 30, in several shapes and reading orders, is recovered every time before any negative is declared; the same 103 shapes pointed at DOGECOIN's own image correctly find DOGECOIN's real payload, not noise | 2026 |
| The raw 256-bit key laid out as a block (16x16, 8x32, 4x64) | 6,290,064 keys | 0 hits | yes: a known key replanted in all 3 arrangements is recovered | 2026 |
| XOR between the 3 panels | 2,616,768 keys | 0 hits | yes | 2026 |
| Row-to-row displacement (whole-row granularity only; segment-level displacement not tested) | 1,421,160 combinations | 0 valid WIF checksum | yes: an estimator for this channel is validated at 85.8% correct rows on a known injection | 2026 |
| Mask decoded as base58/ASCII text, 2 axes x 12 widths x 2 polarities | all 3 panels | 0 valid WIF checksum | no known-good calibration example for this specific test; reported as tried, not certified | 2026 |
| Brainwallet phrases built from the artist's own vocabulary | 902 phrases | 0 hits | no; a weak test by the researcher's own account | 2026 |

## What is confirmed, to prevent re-testing a false negative

- The color-extraction pipeline itself works: SWAGBUCKS, a sibling piece that initially looked
  mute, shows a genuine periodic signal once color extraction is corrected; a separate piece's
  translucent material caused an unrelated extraction problem. Neither piece "has no signal."
- A local 4-color quantization step lifted an early resolution ceiling: it recovers
  CANNABISCOIN's payload at 13 pixels per stud with 0.92 agreement, so color identity is no
  longer the blocking factor for a region-based reading of COG.
- The localized-region sweep run on COG covered color counts of 4 only; a sibling piece
  (SWAGBUCKS) needed color count 5 to find its real payload at the same character width. The
  same gap has not yet been closed on COG: this is a real hole in the coverage above, not a
  new hypothesis.
