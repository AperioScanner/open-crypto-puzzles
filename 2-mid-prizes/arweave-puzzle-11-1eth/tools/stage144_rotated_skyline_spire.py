#!/usr/bin/env python3
"""A11-EXP-144 — provenance of pointed vertical spine in reversed rotated skyline.

The user's second transformed image has a central narrow black vertical
"spire" alongside mirrored building steps, unlike the white negative-space
pair tested in Stage143. A horizontal source skyline/waterfront rule becomes
vertical upon 90-degree rotation. Test this specific source mechanism, without
attributing a temple, tower or chess symbol to the original drawing.

Source window, method and controls fixed before target analysis. The script
reproduces both roof-facing and waterfront-facing skyline compositions and
ablates only long, original-source horizontal marks around the detected rule.
A source line removed by ablation cannot be a new author-drawn vertical symbol.

No wordlists, keys, wallet, candidate generation or off-image search.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage144-rotated-skyline-spire"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")

# The long horizontal waterfront line is visible immediately below skyline
# facades in the native image. All geometry below is source-pixel geometry.
X0,X1=180,1595
Y0,Y1=225,292
ROOF_VIEW_TOP=0
ROOF_VIEW_BOTTOM=330
DARK=175
OPEN_KERNEL=35
LOCAL_Y_RADIUS=3
N_BLOCKS=12
MIN_COVERED_BLOCKS=9
MIN_ABLATION_BLOCK_DROP=6
MAX_NEGATIVE_BLOCKS=4

def long_horizontal(source):
    sub=source[Y0:Y1,X0:X1]
    dark=(sub<DARK).astype(np.uint8)*255
    opened=cv2.morphologyEx(
        dark,cv2.MORPH_OPEN,
        np.ones((1,OPEN_KERNEL),np.uint8),
        iterations=1
    )
    return opened

def scored_line(source):
    mask=long_horizontal(source)
    h,w=mask.shape
    scores=[]
    for y in range(LOCAL_Y_RADIUS,h-LOCAL_Y_RADIUS):
        bands=mask[y-LOCAL_Y_RADIUS:y+LOCAL_Y_RADIUS+1,:]
        cells=[]
        for i in range(N_BLOCKS):
            xa=(i*w)//N_BLOCKS
            xb=((i+1)*w)//N_BLOCKS
            cells.append(bool(np.any(bands[:,xa:xb]>0)))
        scores.append({
            "original_y":int(Y0+y),
            "covered_blocks":int(sum(cells)),
            "covered_binary":cells
        })
    best=sorted(scores,key=lambda d:(-d["covered_blocks"],d["original_y"]))[0]
    return best,mask

def strip(source,best):
    out=source.copy()
    mask=long_horizontal(source)
    # REPAIR: selecting only pixels at y ±3 removes the top of a 2-px
    # antialiased stroke but LEAVES its lower rows. The initial 4/4 copied
    # positive controls kept 12/12 covered x-blocks after that partial cut.
    # Select each ENTIRE horizontal-opening connected component intersecting
    # the original fixed ±3px row seed. This removes one actual pencil-stroke
    # component from endpoint to endpoint without expanding the seed search,
    # relaxing gates or inventing new source content.
    yc=best["original_y"]-Y0
    ylo=max(0,yc-LOCAL_Y_RADIUS)
    yhi=min(mask.shape[0],yc+LOCAL_Y_RADIUS+1)
    binary=(mask>0).astype(np.uint8)
    n,labels,_,_=cv2.connectedComponentsWithStats(binary,connectivity=8)
    seed_labels=np.unique(labels[ylo:yhi,:])
    seed_labels=seed_labels[seed_labels>0]
    keep=np.isin(labels,seed_labels).astype(np.uint8)*255
    enlarged=cv2.dilate(keep,np.ones((3,3),np.uint8),iterations=1)
    patch=out[Y0:Y1,X0:X1]
    patch[enlarged>0]=255
    return out

def evaluate(source):
    best,_=scored_line(source)
    without=strip(source,best)
    remaining,_=scored_line(without)
    delta=best["covered_blocks"]-remaining["covered_blocks"]
    matched=(
        best["covered_blocks"]>=MIN_COVERED_BLOCKS
        and delta>=MIN_ABLATION_BLOCK_DROP
    )
    return {
        "best_source_horizon_y":best["original_y"],
        "source_horizontal_support_blocks":best["covered_blocks"],
        "post_horizontal_rule_removal_blocks":remaining["covered_blocks"],
        "source_blocks_lost_by_ablation":int(delta),
        "unmodified_source_rule_explains_vertical_spire":bool(matched),
    }

def synthetic(with_rule):
    rng=np.random.default_rng(144)
    a=np.full((1105,1600),255,np.uint8)
    # Varied facades are a negative control for the possibility that
    # independent building roofs/hatching accidentally create one coherent
    # horizontal line across all twelve long-range source bins.
    for i in range(12):
        x=int(X0+i*(X1-X0)/12)
        xmax=min(X1,x+int((X1-X0)/12)-10)
        ybase=int(220+rng.integers(-12,18))
        for xx in range(x+6,xmax-5,10):
            cv2.line(a,(xx,140),(xx,ybase),0,1,cv2.LINE_AA)
        for yy in (155,180,205):
            cv2.line(a,(x+6,yy+i%3),(min(xmax,x+28),yy+i%3),
                     0,1,cv2.LINE_AA)
    if with_rule:
        y=260
        for i in range(X0,X1-12,67):
            cv2.line(a,(i,y),(min(X1-1,i+58),y),0,2,cv2.LINE_AA)
    return a

def controls():
    positive={}
    negative={}
    for fmt,img in variants(synthetic(True)).items():
        if fmt in FORMATS:positive[fmt]=evaluate(img)
    for fmt,img in variants(synthetic(False)).items():
        if fmt in FORMATS:negative[fmt]=evaluate(img)
    pos=sum(x["unmodified_source_rule_explains_vertical_spire"]
            for x in positive.values())
    neg=sum(x["source_horizontal_support_blocks"]<=MAX_NEGATIVE_BLOCKS
            and not x["unmodified_source_rule_explains_vertical_spire"]
            for x in negative.values())
    return {"pass":pos==4 and neg==4,
            "positive_passing_formats":pos,
            "negative_passing_formats":neg,
            "positive":positive,"negative":negative}

def mirror_pair(skyline,reverse):
    # In Stage143, the inner boundary faced the roofs. In the user's SECOND
    # rotated presentation, the mirrored pair instead faces skyline bases.
    # We deliberately render both alternatives, not assert a screenshot's
    # unknown cropping equals this exact geometry.
    rotated=cv2.rotate(skyline,cv2.ROTATE_90_COUNTERCLOCKWISE)
    a=rotated if reverse else np.fliplr(rotated)
    b=np.fliplr(a)
    pair=np.hstack([a,b])
    return cv2.resize(pair,(594,800),interpolation=cv2.INTER_AREA)

def contact(source,diagnostic):
    clean=strip(source,{"original_y":diagnostic["best_source_horizon_y"]})
    crop=lambda z:z[ROOF_VIEW_TOP:ROOF_VIEW_BOTTOM,X0:X1]
    originals={
        "roof facing (prior construction)":mirror_pair(crop(source),False),
        "base facing (new construction)":mirror_pair(crop(source),True),
        "base facing, long rule removed":mirror_pair(crop(clean),True),
    }
    sheet=Image.new("RGB",(594*3,835),"white")
    draw=ImageDraw.Draw(sheet)
    for i,(name,pixels) in enumerate(originals.items()):
        x=594*i
        sheet.paste(Image.fromarray(pixels).convert("RGB"),(x,30))
        draw.text((x+5,8),name,fill=(0,0,0))
    sheet.save(OUT/"skyline-spire-provenance-contact.png")

    # The source line's location is shown independently of any mirrored view.
    full=Image.fromarray(source).convert("RGB")
    dr=ImageDraw.Draw(full)
    y=diagnostic["best_source_horizon_y"]
    dr.rectangle((X0,Y0,X1,Y1),outline=(220,30,30),width=3)
    dr.line([(X0,y),(X1,y)],fill=(30,70,220),width=2)
    full.save(OUT/"source-skyline-rule-location.png")

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:raise SystemExit("Canonical image hash mismatch")
    gray=np.asarray(Image.open(SOURCE).convert("L"))
    if gray.shape!=(1105,1600):raise SystemExit("Wrong image dimensions")
    ctl=controls()
    results={fmt:evaluate(a) for fmt,a in variants(gray).items()
             if fmt in FORMATS}
    consistent=all(results[v]["unmodified_source_rule_explains_vertical_spire"]
                   for v in FORMATS)
    y_positions=[results[v]["best_source_horizon_y"] for v in FORMATS]
    y_stable=max(y_positions)-min(y_positions)<=3
    source_confirmed=consistent and y_stable
    decision=(
        "CONTROL_FAILURE" if not ctl["pass"] else
        "SOURCE_HORIZON_EXPLAINS_ROTATED_SPIRE"
        if source_confirmed else
        "SPIRE_SOURCE_HORIZON_NOT_CONFIRMED"
    )
    report={
        "experiment_id":"A11-EXP-144",
        "hypothesis":"the pointed central vertical spire in the second mirrored/rotated montage is ordinary original skyline waterfront baseline, rotated into a vertical line and enhanced by bilateral reflection",
        "observation":"User's second transformed picture shows a narrow central dark spire with stacked horizontal skyline building blocks on both sides",
        "source_sha256":digest,
        "registered_source_region":{"x":[X0,X1],"y":[Y0,Y1]},
        "fixed_feature_gates":{
            "long_horizontal_open_kernel":OPEN_KERNEL,
            "dark_threshold":DARK,
            "number_source_x_blocks":N_BLOCKS,
            "max_y_drift":3,
            "required_source_coverage_blocks":MIN_COVERED_BLOCKS,
            "required_ablation_block_drop":MIN_ABLATION_BLOCK_DROP
        },
        "calibration_repair":"Initial positive horizon synthetic scored 12/12 before and after partial 3px ablation. Repaired only the ablation primitive: erase complete detected long-horizontal connected components touching the unchanged seed row, keeping all precommitted source ROIs/thresholds.","controls":ctl,
        "source_variants":results,
        "same_source_y_under_lossy_formats":y_stable,
        "independent_new_spire_evidence":False,
        "decision":decision,
        "scope_note":"Representative reconstruction uses skyline crop y0..330, not asserted pixel-equal to user's unknown crop/flip settings. This test only explains a source horizontal line rotating into a vertical apparent spire; it cannot confirm or exclude every possible hidden symbol or artist intention.",
        "safety":"No secret candidates, BIP39, private keys, wallet access, addresses or off-image research."
    }
    (OUT/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    contact(gray,results["original"])
    lines=[
        "# Stage144 — source origin of the central spire in reversed skyline mirror",
        "",
        f"- Canonical source verified: **{digest==SHA}**",
        "- Calibration repair: remove full connected horizontal strokes seeded at the same fixed y±3 instead of clipping their upper pixels.",
        f"- Synthetic horizon and independent-building null controls: **{ctl['pass']}** (4/4 + 4/4)",
        f"- Original line near skyline/waterfront y: **{results['original']['best_source_horizon_y']}**",
        f"- Vertical-spire provenance across four formats: **{consistent}**",
        f"- Skyline-row alignment stable: **{y_stable}**",
        f"- Decision: **{decision}**",
        "",
        "| format | horizon x-block support | after rule removal | blocks lost |",
        "|---|---:|---:|---:|"
    ]
    for v in FORMATS:
        x=results[v]
        lines.append(f"| {v} | {x['source_horizontal_support_blocks']}/12 | {x['post_horizontal_rule_removal_blocks']}/12 | {x['source_blocks_lost_by_ablation']} |")
    lines+=["","## Interpretation",""]
    if not ctl["pass"]:
        lines.append("Failed calibration. Do not interpret real original. Repair SAME Stage144.")
    elif source_confirmed:
        lines.append("A preexisting horizontal waterfront line rotates into the apparent central vertical spike; bilateral symmetry is artificially introduced by the montage. No independent spire/tower glyph confirmed.")
    else:
        lines.append("This fixed provenance test did not verify a continuous source skyline rule robust enough to explain the spike. The image still cannot be called a deliberate tower based only on artificial reflection.")
    lines+=["","Artifacts: source-skyline-rule-location.png and skyline-spire-provenance-contact.png.",
             "No secret material or off-image research.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":144,"controls":ctl["pass"],
                      "source_confirmed":source_confirmed,
                      "decision":decision}))

if __name__=="__main__":
    main()
