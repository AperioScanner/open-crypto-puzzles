#!/usr/bin/env python3
"""A11-EXP-146 — are two SOURCE-ANCHORED skyline bands robust to resampling?

Stage145 found 2 bands in the original and both JPEGs, but source bands became
ONE connected cluster after 75% down/up resampling. The archived values show
distinct strong row-support peaks y~237 and y~257 in native renderings, while
the resampled image contains y232..268 as a single joined morphological group.

This *registered source-quality follow-up* holds two fixed, nonoverlapping row
windows, not a free scan or a loosened downstream significance threshold:
upper y232..242, lower y252..267, in the unchanged Stage144 x180..1595 and
y225..292 source ROI and original 35px long-horizontal filter. It checks
whether the two separate SOURCE bands each have a long-stroke response,
and whether at least one survives removing the other selected stroke.

Synthetic fixtures: two separated horizontal lines, single upper only,
single lower only, and no horizontal lines, across four image variants.
All source findings are visual drawing geometry, NOT encoded symbols.
No wallet operations, keys, seed words, mnemonics or outside sources.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from stage112_corrected_sail_width_progression import variants
from stage144_rotated_skyline_spire import (
    SHA, X0, X1, Y0, Y1, FORMATS, N_BLOCKS, LOCAL_Y_RADIUS,
    long_horizontal, scored_line, strip, synthetic as blank_facades
)
from stage145_skyline_multiple_lines import evaluate as stage145_evaluate

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
PREV=ROOT/"analysis"/"runs"/"stage145-skyline-multi-horizontal"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage146-fixed-skyline-bands"
OUT.mkdir(parents=True,exist_ok=True)

# Fixed by Stage145 preexisting native/JPEG source observations,
# before inspecting any Stage146 outcome. Not a chess-specific score.
UPPER_Y=(232,242)  # inclusive absolute y
LOWER_Y=(252,267)
TEST_LINE_YS=(237,260)
MIN_SOURCE_BLOCKS=6
MIN_BLOCKS_AFTER_ONE_REMOVAL=6
MAX_FALSE_SOURCE_BLOCKS=4
PREVIOUS_STEP_AGREEMENT_REQUIRED=True

def coverage(mask,y0,y1):
    """Max 12-bin source horizontal support in a fixed y band (no fitting)."""
    cropped=mask[max(0,y0-Y0):min(Y1-Y0,y1-Y0+1),:]
    if cropped.size==0:return {"blocks":0,"ink_density":0.0}
    n,w=cropped.shape
    supports=[]
    for xx in range(N_BLOCKS):
        x0=(xx*w)//N_BLOCKS
        x1=((xx+1)*w)//N_BLOCKS
        supports.append(int(np.any(cropped[:,x0:x1]>0)))
    return {"blocks":int(sum(supports)),
            "ink_density":round(float(np.mean(cropped>0)),8)}

def measure(img):
    filtered=long_horizontal(img)
    upper=coverage(filtered,*UPPER_Y)
    lower=coverage(filtered,*LOWER_Y)
    best,_=scored_line(img)
    after=strip(img,best)
    residual=long_horizontal(after)
    after_up=coverage(residual,*UPPER_Y)
    after_down=coverage(residual,*LOWER_Y)
    both=(upper["blocks"]>=MIN_SOURCE_BLOCKS
          and lower["blocks"]>=MIN_SOURCE_BLOCKS)
    survives=max(after_up["blocks"],after_down["blocks"])>=MIN_BLOCKS_AFTER_ONE_REMOVAL
    return {
      "upper_horizontal_source_support":upper,
      "lower_horizontal_source_support":lower,
      "upper_remaining_after_single_stroke_removal":after_up,
      "lower_remaining_after_single_stroke_removal":after_down,
      "selected_source_line_y":best["original_y"],
      "both_band_regions_have_source_strokes":bool(both),
      "some_source_band_survives_single_line_ablation":bool(survives),
      "two_band_provenance_supported":bool(both and survives),
    }

def synthetic(kind):
    source=blank_facades(False)
    ys=(
       TEST_LINE_YS if kind=="two" else
       (TEST_LINE_YS[0],) if kind=="upper_only" else
       (TEST_LINE_YS[1],) if kind=="lower_only" else
       ()
    )
    for y in ys:
        for x in range(X0,X1-12,67):
            cv2.line(source,(x,y),(min(X1-1,x+58),y),
                     0,2,cv2.LINE_AA)
    return source

def test_controls():
    specs=(
      ("two",True),
      ("upper_only",False),
      ("lower_only",False),
      ("none",False)
    )
    results={}
    cases=0
    passed=0
    for name,expected in specs:
        results[name]={}
        for mode,img in variants(synthetic(name)).items():
            if mode not in FORMATS:continue
            obs=measure(img)
            actual=obs["two_band_provenance_supported"]
            # Every single-band/no-band negative must have fewer than
            # MIN_SOURCE_BLOCKS in at least one of the fixed ROIs.
            negative_safe=(expected or
                           min(obs["upper_horizontal_source_support"]["blocks"],
                               obs["lower_horizontal_source_support"]["blocks"])
                           <=MAX_FALSE_SOURCE_BLOCKS)
            ok=(actual==expected and negative_safe)
            results[name][mode]={
                "pass":bool(ok),"expected_two_bands":expected,
                "upper_blocks":obs["upper_horizontal_source_support"]["blocks"],
                "lower_blocks":obs["lower_horizontal_source_support"]["blocks"],
                "after_ablation_max":max(obs["upper_remaining_after_single_stroke_removal"]["blocks"],
                                         obs["lower_remaining_after_single_stroke_removal"]["blocks"])
            }
            cases+=1
            passed+=int(ok)
    return {
       "pass":cases==16 and passed==16,
       "cases":cases,"passed_cases":passed,"fixtures":results
    }

def replay_previous(img,prior):
    if not prior["controls"]["passed"] or prior["sha256"]!=SHA:
        return False
    if not prior["stage144_exact_reproduction"]:
        return False
    for mode,variant in variants(img).items():
        if mode not in FORMATS:continue
        old=prior["by_variant"][mode]
        now=stage145_evaluate(variant)
        if now["two_independent_skyline_horizon_bands"]!=old["two_independent_skyline_horizon_bands"]:
            return False
        if now["original_stage144"]!=old["original_stage144"]:
            return False
    return True

def visual_diagnostic(img,observed):
    source=Image.fromarray(img).convert("RGB")
    draw=ImageDraw.Draw(source)
    draw.rectangle((X0,UPPER_Y[0],X1,UPPER_Y[1]),
                   outline=(40,90,220),width=2)
    draw.rectangle((X0,LOWER_Y[0],X1,LOWER_Y[1]),
                   outline=(220,70,50),width=2)
    source.save(OUT/"two-fixed-horizontal-source-bands.png")

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if sha!=SHA:raise RuntimeError("canonical hash mismatch")
    img=np.asarray(Image.open(PNG).convert("L"))
    if img.shape!=(1105,1600):raise RuntimeError("source dimensions changed")
    prior=json.loads(PREV.read_text())
    controls=test_controls()
    source={fmt:measure(frame) for fmt,frame in variants(img).items()
            if fmt in FORMATS}
    provenance=replay_previous(img,prior)
    reproducible=all(source[fmt]["two_band_provenance_supported"]
                     for fmt in FORMATS)
    decision=(
       "CONTROL_FAILURE" if not controls["pass"] else
       "STAGE145_SOURCE_REPRODUCTION_FAILURE" if not provenance else
       "FIXED_NATIVE_SKYLINE_BANDS_REPRODUCIBLE"
       if reproducible else "TWO_BAND_SOURCE_NOT_CONFIRMED_IN_ALL_FORMATS"
    )
    result={
       "experiment_id":"A11-EXP-146",
       "hypothesis":"two nonoverlapping source horizontal-ink row bands that Stage145 saw in 3/4 versions remain physically present when downsampled JPEG morphology accidentally joins them",
       "basis":"Stage145 archive confirmed original and JPEG band centers y~237/257, but 75%-down-up joined the contiguous component while still retaining 8/12 source blocks after Stage144 ablation",
       "scope":"source-anchored upper y232..242 and lower y252..267, original Stage144 horizontal morphology 35px threshold175, 12 x-blocks and four lossy/source formats",
       "canonical_sha256":sha,
       "fixed_source_windows":{"x":[X0,X1],
                               "upper_y_inclusive":list(UPPER_Y),
                               "lower_y_inclusive":list(LOWER_Y)},
       "gates":{"min_blocks_per_band":MIN_SOURCE_BLOCKS,
               "min_remaining_blocks_after_one_line_ablation":MIN_BLOCKS_AFTER_ONE_REMOVAL},
       "controls":controls,
       "reproduced_stage145_source":provenance,
       "source_results":source,
       "two_source_bands_across_all_four_renderings":reproducible,
       "decision":decision,
       "method_limits":"Fixed windows derived from preceding native-image diagnostic, so statistical independence and author intent are not established. Source support from two bands does not prove independent physical pen strokes or uniqueness of a tower, chess piece, code or binary carrier. This is a source-provenance/re-encoding audit only.",
       "safety":"No wallet, BIP39, private key, mnemonic, address, off-image or social source access."
    }
    visual_diagnostic(img,source["original"])
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=[
       "# Stage146 — verify native skyline two bands despite resample merging","",
       f"- Source SHA verified: **{sha==SHA}**",
       f"- Artificial two/single/no-band controls: **{controls['passed_cases']}/{controls['cases']}**",
       f"- Replays Stage145 diagnostic source exactly: **{provenance}**",
       f"- Upper/lower fixed source bands both supported in 4/4: **{reproducible}**",
       f"- Decision: **{decision}**","",
       "| format | upper source x-bins | lower source x-bins | after deleting one stroke |",
       "|---|---:|---:|---:|"
    ]
    for v in FORMATS:
        z=source[v]
        n=max(z["upper_remaining_after_single_stroke_removal"]["blocks"],
              z["lower_remaining_after_single_stroke_removal"]["blocks"])
        md.append(f"| {v} | {z['upper_horizontal_source_support']['blocks']}/12 | {z['lower_horizontal_source_support']['blocks']}/12 | {n}/12 |")
    md+=["","## Interpretation",""]
    if not controls["pass"] or not provenance:
        md.append("Synthetic controls or prior-source replay failed. Repair Stage146; no claim about original.")
    elif reproducible:
        md.append("Two separated original drawing regions retain long native horizontal line support even after JPEG/resampling, despite morphological connected-component merging. The rotated/mirrored visual 'spire' has an ordinary source-line explanation, not a uniquely encoded shape.")
    else:
        md.append("The source-aligned paired bands did not replicate across all formats. No independent line-pair evidence; cannot infer a tower or code.")
    md+=["","Source-contact: two-fixed-horizontal-source-bands.png.",
         "No keys, seed words, wallet or external content.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"stage":146,"controls":controls["pass"],
                       "source_replay":provenance,"both":reproducible,
                       "decision":decision}))

if __name__=="__main__":
    main()
