#!/usr/bin/env python3
"""A11-EXP-142 — true large hull upper↔lower mirrored pen-stroke fingerprint.

Stage41's historical "large-boat top/bottom symmetry" used the wrong
large_sailboat ROI (44,320)-(359,599). Stage132 proved that ROI excluded ALL
actual hull pixels. This precommitted image-only test audits genuine hull
interior strokes reflected around a fixed y=860.5 axis (NO axis search).

It is a separate anatomical direction from Stage141's left/right hull-mirror
test. Compare high-pass pencil texture and low-pass ink separately in two
fixed fore/aft x bands, across canonical/JPEG85/JPEG70/downsampled renderings.
A mirrored illustrative outline is not evidence of encoding or copied strokes.

Controls: exactly mirrored independently generated synthetic upper-hull
strokes vs independent redraw lower-hull controls, both with the SAME fixed
hull support polygons/mask and four lossy versions. Never derive keys,
seed phrases, wallet addresses or crypto candidate material.
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
IMAGE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage142-true-hull-vertical-mirror"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
HULL_POLY=np.asarray(POLYGONS["large_hull"],np.int32)

# Axis at 860.5, fixed by the large hull polygon central band. Exact
# pixel-pair y coordinates add to 1721.
UPPER_Y=(798,847)
LOWER_Y=(875,924)
assert UPPER_Y[1]-UPPER_Y[0]==LOWER_Y[1]-LOWER_Y[0]
assert UPPER_Y[0]+LOWER_Y[1]-1==1721
X_BANDS=(("fore_hull",95,235),("aft_hull",315,455))
EROSION=7
DARK_THRESHOLD=175
MIN_PAIRED_MASK=1200
MIN_SIDE_DENSITY=.075
MIN_LOW_PASS_CORR=.72
MIN_HIGH_PASS_CORR=.56

def fixed_hull_mask():
    base=np.zeros((1105,1600),np.uint8)
    cv2.fillPoly(base,[HULL_POLY],1)
    return cv2.erode(base,np.ones((EROSION,EROSION),np.uint8))>0
MASK=fixed_hull_mask()

def pearson(a,b,where):
    x=np.asarray(a[where],np.float64)
    y=np.asarray(b[where],np.float64)
    if x.size==0:return 0.
    x-=x.mean();y-=y.mean()
    den=float(np.linalg.norm(x)*np.linalg.norm(y))
    return float(x.dot(y)/den) if den>1e-9 else 0.

def extract(image):
    dark=(255-image.astype(np.float32))/255.
    low=cv2.GaussianBlur(dark,(0,0),1.4)
    high=dark-cv2.GaussianBlur(dark,(0,0),4.)
    upper=slice(*UPPER_Y)
    lower=slice(*LOWER_Y)
    result={}
    for name,x0,x1 in X_BANDS:
        xx=slice(x0,x1)
        valid=MASK[upper,xx]&np.flipud(MASK[lower,xx])
        n=int(valid.sum())
        a=image[upper,xx]
        b=np.flipud(image[lower,xx])
        density_up=float(np.mean(a[valid]<DARK_THRESHOLD)) if n else 0.
        density_down=float(np.mean(b[valid]<DARK_THRESHOLD)) if n else 0.
        adequate=(n>=MIN_PAIRED_MASK
                  and min(density_up,density_down)>=MIN_SIDE_DENSITY)
        lo=(pearson(low[upper,xx],np.flipud(low[lower,xx]),valid)
            if adequate else None)
        hi=(pearson(high[upper,xx],np.flipud(high[lower,xx]),valid)
            if adequate else None)
        matching=bool(adequate and lo>=MIN_LOW_PASS_CORR
                      and hi>=MIN_HIGH_PASS_CORR)
        result[name]={
            "paired_mask_pixels":n,
            "upper_ink_density":round(density_up,6),
            "lower_ink_density":round(density_down,6),
            "valid":bool(adequate),
            "ink_corr":round(lo,6) if lo is not None else None,
            "detail_corr":round(hi,6) if hi is not None else None,
            "mirrored_pencil_fingerprint":matching
        }
    return result

def scatter_strokes(image,seed,top):
    rng=np.random.default_rng(seed)
    lo,hi=UPPER_Y if top else LOWER_Y
    for _,x0,x1 in X_BANDS:
        for _ in range(130):
            xx=int(rng.integers(x0+8,x1-8))
            yy=int(rng.integers(lo+5,hi-5))
            dx=int(rng.integers(-13,14))
            dy=int(rng.integers(-12,13))
            dest=(int(np.clip(xx+dx,x0+2,x1-3)),
                  int(np.clip(yy+dy,lo+2,hi-3)))
            cv2.line(image,(xx,yy),dest,0,int(rng.integers(1,3)),cv2.LINE_AA)

def synthetic(is_mirrored):
    img=np.full((1105,1600),255,np.uint8)
    scatter_strokes(img,142,top=True)
    if is_mirrored:
        img[LOWER_Y[0]:LOWER_Y[1],:]=np.flipud(img[UPPER_Y[0]:UPPER_Y[1],:])
    else:
        scatter_strokes(img,274,top=False)
    return img

def calibrate():
    positive=variants(synthetic(True))
    negative=variants(synthetic(False))
    pos={v:extract(positive[v]) for v in FORMATS}
    neg={v:extract(negative[v]) for v in FORMATS}
    pos_pass=sum(all(t["valid"] and t["mirrored_pencil_fingerprint"]
                     for t in pos[v].values()) for v in FORMATS)
    neg_pass=sum(all(t["valid"] and not t["mirrored_pencil_fingerprint"]
                     for t in neg[v].values()) for v in FORMATS)
    return {
        "pass":bool(pos_pass==4 and neg_pass==4),
        "cases":len(FORMATS)*len(X_BANDS)*2,
        "positive_format_passes":pos_pass,
        "independent_redraw_negative_format_passes":neg_pass,
        "positive":pos,
        "negative":neg
    }

def main():
    hash_=hashlib.sha256(IMAGE.read_bytes()).hexdigest()
    if hash_!=SHA:raise SystemExit("Source SHA256 changed")
    img=np.asarray(Image.open(IMAGE).convert("L"))
    if img.shape!=(1105,1600):raise SystemExit("Unexpected image dimensions")
    controls=calibrate()
    scene={v:extract(a) for v,a in variants(img).items() if v in FORMATS}
    source_ok=all(all(x["valid"] for x in scene[v].values()) for v in FORMATS)
    mirrored=all(all(x["mirrored_pencil_fingerprint"] for x in scene[v].values())
                 for v in FORMATS)
    decision=("CONTROL_FAILURE" if not controls["pass"] else
              "INSUFFICIENT_CORRECTED_HULL_SOURCE" if not source_ok else
              "VERTICALLY_MIRRORED_HULL_PENCIL_FINGERPRINT_REQUIRES_REVIEW"
              if mirrored else "NO_UPPER_LOWER_HULL_PENCIL_TEMPLATE_MIRROR")
    payload={
        "experiment_id":"A11-EXP-142",
        "hypothesis":"the genuine large hull has its interior upper/lower pencil marks duplicated by vertical reflection about the fixed central hull axis, beyond natural vessel-silhouette shape",
        "justification":"Historical Stage41 boat y-symmetry used a rectangle with zero true hull coverage; Stage132 proved the defect. Stage141 tested true hull L/R symmetry but not U/D.",
        "scope":"immutable Stage132 hull polygon; y-axis 860.5 and x-band fore/aft fixed; 2 texture channels and 4 image variants",
        "canonical_sha256":hash_,
        "source_geometry":{"hull_polygon":HULL_POLY.tolist(),
                           "mirror_y_axis":860.5,
                           "upper_y":list(UPPER_Y),"lower_y":list(LOWER_Y),
                           "fore_aft_x_bands":[list(z) for z in X_BANDS],
                           "border_erosion_px":EROSION},
        "thresholds":{"min_mask_pairs":MIN_PAIRED_MASK,
                      "min_ink_density":MIN_SIDE_DENSITY,
                      "ink_correlation":MIN_LOW_PASS_CORR,
                      "detail_correlation":MIN_HIGH_PASS_CORR},
        "controls":controls,
        "real":scene,
        "source_adequate":source_ok,
        "full_mirror_replicated":mirrored,
        "decision":decision,
        "limits":"Only the predeclared axis and two hull interior strips. This cannot address approximate hull outline symmetry, hidden lettering, altered axis positions or secrets.",
        "safety":"No cryptographic candidates, BIP39, mnemonic words, keys, wallets, addresses or social/external sources."
    }
    (OUT/"result.json").write_text(json.dumps(payload,indent=2)+"\n")
    md=["# Stage 142 — corrected hull upper/lower pencil-stroke mirror","",
        f"- Canonical PNG verified: **{hash_==SHA}**",
        f"- Synthetic mirror positives: **{controls['positive_format_passes']}/4**",
        f"- Independent redraw negatives: **{controls['independent_redraw_negative_format_passes']}/4**",
        f"- Real hull pixels source-adequate: **{source_ok}**",
        f"- Vertical copied-pencil fingerprint replicated: **{mirrored}**",
        f"- Decision: **{decision}**","",
        "| format | fore ink corr | fore detail corr | aft ink corr | aft detail corr |",
        "|---|---:|---:|---:|---:|"]
    for v in FORMATS:
        fore=scene[v]["fore_hull"];aft=scene[v]["aft_hull"]
        md.append(f"| {v} | {fore['ink_corr']} | {fore['detail_corr']} | {aft['ink_corr']} | {aft['detail_corr']} |")
    md+=["","## Interpretation",""]
    if not controls["pass"]:
        md.append("Controls failed: repair Stage142 before real-data inference.")
    elif not source_ok:
        md.append("Insufficient source coverage to test mirrored hull-pencil strokes. Inconclusive.")
    elif mirrored:
        md.append("Mirror-copied internal pencil strokes detected; requires independent visual review before assigning meaning.")
    else:
        md.append("No vertical reflection-copy of the real hull's interior pencil details in these two fixed bands, despite calibrated controls; ordinary approximate hull shape is not excluded.")
    md+=["","No private-key, mnemonic, wallet or address operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"stage":142,"controls":controls["pass"],
                      "coverage":source_ok,"mirrored":mirrored,
                      "decision":decision}))

if __name__=="__main__":
    main()
