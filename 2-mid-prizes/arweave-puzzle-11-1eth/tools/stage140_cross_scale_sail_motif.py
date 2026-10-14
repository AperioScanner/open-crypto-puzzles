#!/usr/bin/env python3
"""A11-EXP-140 — is the large sail's *interior pencil template* scaled into a small sail?

The image's true large sail was miscropped for Stage94 and repaired in Stage132.
Stage120 compared *only* the five small sails, not the complete large sail.
Stage123 compared 64px fixed-grid copies without a change of scale.

We geometrically rectify the Stage132 complete-sail triangle and five corrected
small-sail triangles into 128x128 images. A repeated interior stroke fingerprint
would survive geometry normalization at comparable pixel positions. Two
independent descriptors are used, on BOTH inner left/right sail panels:
(1) normalized low-frequency dark ink, (2) normalized high-pass pencil marks.
We compare original/JPEG85/JPEG70/75% resampled variants and require every
variant to pass without selecting a favorable offset/rotation/threshold.

Synthetic controls: a canonical pen-stroke triangle copied into all five
true-size sails, and 5 independently re-sketched triangles with the same
silhouette and diagonal shading convention. All copy positives must be
recovered and all redraw negatives rejected before using actual image data.

No private keys, BIP39 phrases, wallets, addresses or external references.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage132_large_sail_legacy_bbox_audit import POLYGONS

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage140-cross-scale-sail-motif"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
W=H=128
CANON=np.float32([[64,0],[0,127],[127,127]])
SITES=(
    ("large",[(242,398),(56,758),(512,760)]),
    ("small_1",[(1042,448),(1007,546),(1077,546)]),
    ("small_2",[(1148,433),(1110,532),(1186,532)]),
    ("small_3",[(1282,411),(1238,514),(1326,514)]),
    ("small_4",[(1372,397),(1330,498),(1414,498)]),
    ("small_5",[(1490,357),(1443,463),(1537,463)]),
)
MIN_SOURCE_DENSITY=.10
MIN_SAIL_BINARY_CORR=.65
MIN_SAIL_DETAIL_CORR=.28
INNER_Y_MIN=.26
INNER_Y_MAX=.79
INNER_X_MIN=.17
INNER_X_MAX=.76
MIN_MASK_PIXELS=450

def panel_masks():
    yy,xx=np.indices((H,W))
    t=yy/(H-1)
    x=(xx-63.5)/63.5
    ok=(t>=INNER_Y_MIN)&(t<=INNER_Y_MAX)
    ok &= abs(x)>=INNER_X_MIN
    ok &= abs(x)<=INNER_X_MAX
    return {"left":ok&(x<0),"right":ok&(x>0)}

MASKS=panel_masks()

def rectify(image,triplet):
    points=np.asarray(triplet,dtype=np.float32)
    # Source pixels to a canonical sail triangle; bilinear interpolation.
    transform=cv2.getAffineTransform(points,CANON)
    return cv2.warpAffine(image,transform,(W,H),flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT,borderValue=255)

def two_features(rectified):
    ink=(255-rectified.astype(np.float32))/255.
    low=cv2.GaussianBlur(ink,(0,0),1.4)
    # Remove coarse left/right shading and curved triangular silhouette.
    detail=ink-cv2.GaussianBlur(ink,(0,0),3.)
    return {"dark":low,"detail":detail}

def corr(a,b,mask):
    x=a[mask].astype(np.float64)
    y=b[mask].astype(np.float64)
    x-=x.mean();y-=y.mean()
    den=float(np.linalg.norm(x)*np.linalg.norm(y))
    return float(np.dot(x,y)/den) if den>1e-10 else 0.

def pair_stats(a,b):
    aa=two_features(a); bb=two_features(b)
    values={}
    for side,m in MASKS.items():
        values[side]={
            "dark":round(corr(aa["dark"],bb["dark"],m),6),
            "detail":round(corr(aa["detail"],bb["detail"],m),6),
        }
    den_a={s:round(float(np.mean(a[m]<175)),6) for s,m in MASKS.items()}
    den_b={s:round(float(np.mean(b[m]<175)),6) for s,m in MASKS.items()}
    enough=all(
        den_a[s]>=MIN_SOURCE_DENSITY and den_b[s]>=MIN_SOURCE_DENSITY
        for s in MASKS
    )
    pass_template=bool(enough and all(
        values[s]["dark"]>=MIN_SAIL_BINARY_CORR
        and values[s]["detail"]>=MIN_SAIL_DETAIL_CORR for s in MASKS
    ))
    return {
        "panel_values":values,
        "density_large":den_a,
        "density_small":den_b,
        "enough_ink":enough,
        "template_match":pass_template,
    }

def synth_template(seed):
    rng=np.random.default_rng(seed)
    img=np.full((H,W),255,np.uint8)
    # Keep same triangular visual *silhouette* for all independently
    # drawn controls. Only RANDOM interior strokes differ by seed.
    apex=(64,0);left=(0,127);right=(127,127)
    for foot in (left,right):
        cv2.line(img,apex,foot,0,1,cv2.LINE_AA)
    cv2.line(img,left,right,0,1,cv2.LINE_AA)
    cv2.line(img,apex,(64,126),0,1,cv2.LINE_AA)
    for _ in range(90):
        y=int(rng.integers(30,94))
        t=y/127.
        lo=64-int(63*t)+6
        hi=64+int(63*t)-6
        if lo>=hi:continue
        x=int(rng.integers(lo,hi))
        side=1 if x>=64 else -1
        length=int(rng.integers(13,42))
        dx=side*int(round(length*rng.uniform(.3,.9)))
        end=(int(np.clip(x+dx,0,127)),int(np.clip(y+length,0,127)))
        cv2.line(img,(x,y),end,0,int(rng.integers(1,3)),cv2.LINE_AA)
    return img

def stamp(img,template,points):
    points=np.asarray(points,dtype=np.float32)
    min_x=max(0,int(np.floor(points[:,0].min()))-4)
    min_y=max(0,int(np.floor(points[:,1].min()))-4)
    max_x=min(img.shape[1],int(np.ceil(points[:,0].max()))+5)
    max_y=min(img.shape[0],int(np.ceil(points[:,1].max()))+5)
    local=points-np.float32([min_x,min_y])
    affine=cv2.getAffineTransform(CANON,local)
    patch=cv2.warpAffine(template,affine,(max_x-min_x,max_y-min_y),
                         flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT,borderValue=255)
    block=img[min_y:max_y,min_x:max_x]
    np.minimum(block,patch,out=block)

def synthetic_scene(reused):
    img=np.full((1105,1600),255,np.uint8)
    giant=synth_template(140)
    stamp(img,giant,SITES[0][1])
    for i,(_,points) in enumerate(SITES[1:],1):
        independently_redrawn=synth_template(140+i)
        stamp(img,giant if reused else independently_redrawn,points)
    return img

def inspect(image):
    frames=variants(image)
    per={}
    for fmt in FORMATS:
        img=frames[fmt]
        rectified={key:rectify(img,p) for key,p in SITES}
        base=rectified["large"]
        per[fmt]={name:pair_stats(base,rectified[name])
                  for name,_ in SITES[1:]}
    return per

def calibrate():
    positive=inspect(synthetic_scene(True))
    negative=inspect(synthetic_scene(False))
    positives=[positive[f][name] for f in FORMATS for name,_ in SITES[1:]]
    negatives=[negative[f][name] for f in FORMATS for name,_ in SITES[1:]]
    control_pass=bool(
        all(x["template_match"] for x in positives)
        and all(x["enough_ink"] and not x["template_match"] for x in negatives)
    )
    return {
        "pass":control_pass,
        "positive_cases":len(positives),
        "positive_pass":sum(x["template_match"] for x in positives),
        "negative_cases":len(negatives),
        "negative_pass":sum(not x["template_match"] and x["enough_ink"] for x in negatives),
        "positive_min_panel_dark":min(min(v["dark"] for v in p["panel_values"].values()) for p in positives),
        "positive_min_panel_detail":min(min(v["detail"] for v in p["panel_values"].values()) for p in positives),
        "negative_max_panel_dark":max(max(v["dark"] for v in p["panel_values"].values()) for p in negatives),
        "negative_max_panel_detail":max(max(v["detail"] for v in p["panel_values"].values()) for p in negatives),
    }

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Canonical image SHA changed")
    arr=np.asarray(Image.open(PNG).convert("L"))
    if arr.shape!=(1105,1600):raise RuntimeError("Image dimensions changed")
    controls=calibrate()
    results=inspect(arr)
    per_sail={}
    stable_matches=[]
    adequate=[]
    for name,_ in SITES[1:]:
        observations={f:results[f][name] for f in FORMATS}
        okay=all(z["enough_ink"] for z in observations.values())
        matched=all(z["template_match"] for z in observations.values())
        adequate.append(okay)
        if matched:stable_matches.append(name)
        per_sail[name]={"source_adequate":okay,
                        "replicated_template_match":matched,
                        "measurements":observations}
    decision=("CONTROL_FAILURE" if not controls["pass"] else
              "INSUFFICIENT_SAIL_INTERIOR_COVERAGE" if not all(adequate) else
              "CROSS_SCALE_COPY_FINGERPRINT_REQUIRES_REVIEW"
              if stable_matches else "NO_LARGE_TO_SMALL_STROKE_TEMPLATE_COPY")
    report={
        "experiment_id":"A11-EXP-140",
        "hypothesis":"the five true small sail drawings share a pen-stroke template geometrically copied from the complete large sail, after scale normalization",
        "motivation":"Stage120 compared only five small sails, Stage123 checked same-size 64px cross-region patches, while Stage132 verified giant sail source ROI had been truncated.",
        "source_sha256":digest,
        "sail_geometry_fixed":{n:p for n,p in SITES},
        "normalization":{"width":W,"height":H,
                         "interior_y":[INNER_Y_MIN,INNER_Y_MAX],
                         "interior_abs_x":[INNER_X_MIN,INNER_X_MAX]},
        "thresholds":{"min_source_density":MIN_SOURCE_DENSITY,
                      "min_dark_correlation_both_panels":MIN_SAIL_BINARY_CORR,
                      "min_detail_correlation_both_panels":MIN_SAIL_DETAIL_CORR},
        "controls":controls,
        "sails":per_sail,
        "stable_copied_sails":stable_matches,
        "decision":decision,
        "interpretation_limit":"Only linear affine normalization anchored at six fixed manually identified sail triangles; a positive would be a cross-scale reproduced *drawing* requiring source review, not an encoding. A negative does not exclude rough redraws, other landmarks or semantics.",
        "safety":"No private keys, BIP39, wallets, Ethereum, secrets or other sources used."
    }
    (OUT/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    lines=[
        "# Stage140 — cross-scale reused pencil template, large vs five small sails","",
        f"- Canonical source SHA verified: **{digest==SHA}**",
        f"- Cloned synthetic sail positive controls: **{controls['positive_pass']}/{controls['positive_cases']}**",
        f"- Independently redrawn synthetic sail negative controls: **{controls['negative_pass']}/{controls['negative_cases']}**",
        f"- Adequate real sail interior coverage: **{sum(adequate)}/5**",
        f"- Replicated large-to-small pen-stroke copies: **{len(stable_matches)}/5**",
        f"- Decision: **{decision}**","",
        "| small sail | source adequate | cross-scale copied-template match |",
        "|---|:---:|:---:|",
    ]
    for name,z in per_sail.items():
        lines.append(f"| {name} | {z['source_adequate']} | {z['replicated_template_match']} |")
    lines+=["","## Interpretation",""]
    if not controls["pass"]:lines.append("Control calibration failed. Repair this same Stage140; do NOT interpret real source.")
    elif not all(adequate):lines.append("The narrow fixed interior mask failed source coverage on at least one real sail. Inconclusive.")
    elif stable_matches:lines.append("At least one normalized interior pencil template shows copied-stroke correlation across all formats, requiring independent visual review. Does not imply any encoded secret.")
    else:lines.append("No cross-scale repeated pen-stroke fingerprint from the complete large sail into the five small sails under fixed affine normalization and calibrated controls.")
    lines+=["","No key, word list, wallet or off-image operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":140,"controls":controls["pass"],
                      "coverage":sum(adequate),"duplicates":len(stable_matches),
                      "decision":decision}))

if __name__=="__main__":main()
