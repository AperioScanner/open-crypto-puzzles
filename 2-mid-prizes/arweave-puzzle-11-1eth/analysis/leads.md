# Open leads, ranked

## 1. Format-invariant visual / semantic carrier (highest priority)

Stage 31 is the strongest route-selection result so far. The building H/V texture remained 12/12 stable under two independent classifiers across JPEG 95/85/70, down/up resampling, up/down resampling, and a combined JPEG+resampling transform. Exact foreground bit-0 agreement simultaneously collapsed to ~0.52–0.55.

This makes fragile exact-pixel LSB encoding a poor fit to the author's statement that image format does not matter. Prioritize features a human can still see after ordinary conversion/resizing.

## 2. Known public escrow address as a positive visual probe (active)

The author said the public escrow address `0xFF2142E98E09b5344994F9bEB9C56C95506B9F17` is also included somewhere in the image. That gives a rare known-answer signal.

The first bounded probe is especially motivated by dimensions: the address is 160 bits and the source image is 1600 px wide, exactly 10 px per address bit. Stage 32 tests only this simple coarse-stripe family with null calibration and lossy-reproduction requirements.

## 3. Robust H/V skyline texture, interpretation unresolved (active)

`HHVVHHVHHHHV` is real, robust and format-stable. Stage 22 retired the post-hoc hexadecimal `0x321` interpretation as primary, but the underlying H/V texture remains a plausible selector or semantic clue.

Do not revive 321-specific transforms without an independent reason.

## 4. Solved-puzzle visual/semantic grammar (active)

Stage 11 showed the author's solved puzzles favor visible secondary details, counting, rebuses, ordered interpretation and cross-domain semantic references. Use this as the main prior for new visual hypotheses.

## 5. Generic traversal / exact low bits (strongly downgraded)

Stages 28–30 resolved the apparent traversal anomaly as ordinary foreground/background structure. Stage 31 then directly showed that exact low bits are fragile under format conversion while the visual H/V structure survives.

Do not continue generic low-bit enumeration without a new independent clue.

## 6. Alpha channel (exhausted / low priority)

The 434 non-opaque pixels remain localized to the large sailboat anti-aliasing halo and are consistent with compositing.

## 7. External archival evidence / Puzzle #9 solve method (standing)

Still valuable: early Telegram/Discord/Weavemail material, deleted replies, screenshots, quoted replies, or a first-hand account of Puzzle #9's actual solve method.
