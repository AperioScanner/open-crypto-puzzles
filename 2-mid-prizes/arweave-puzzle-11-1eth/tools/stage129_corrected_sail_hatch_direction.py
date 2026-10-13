#!/usr/bin/env python3
"""A11-EXP-129 — corrected five-small-sail *interior diagonal hatch* direction.

Stage 102 attempted sail L/R stroke-orientation decoding using the defective
Stage-19 x~675 sail track, and omitted the true rightmost sail at x~1490.
Stage 112 independently demonstrated that object-association error. Here we
measure diagonal hatch STROKES (not sail triangle outlines, side-darkness,
mastheads, widths or hull slopes) in five true sail interiors.

Bounded, calibrated structural observation only. No mnemonic, private key,
Ethereum/wallet, Twitter or external-reference operations.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage129-corrected-sail-hatch-direction"
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
SITES=(
    ("small_1",1042,448,98,35),
    ("small_2",1148,433,99,38),
    ("small_3",1282,411,103,44),
    ("small_4",1372,397,101,42),
    ("small_5",1490,357,106,47),
)
MODES=("original","jpeg85","jpeg70","down75_up")
HATCH_MIN_Y=.31
HATCH_MAX_Y=.82
INNER_MIN_FRAC=.20
INNER_MAX_FRAC=.73
CLASS_GATE=.23
MIN_SOBEL_ENERGY=1800.
MIN_HOUGH_LENGTH=22.
MAX_ANGLE_FROM_HORIZ=76.
MIN_ANGLE_FROM_HORIZ=16.

def get_patch(img,site):
    _,cx,top,h,half=site
    pad=10
    x0=cx-half-pad;x1=cx+half+pad+1
    return img[top:top+h,x0:x1]

def mask_for_shape(shape,half):
    h,w=shape
    cx=(w-1)/2
    yy,xx=np.indices((h,w))
    t=yy/float(max(1,h))
    dist=np.abs(xx-cx)
    width=np.maximum(1,t*half)
    interior=(t>=HATCH_MIN_Y)&(t<=HATCH_MAX_Y)
    interior &= (dist>=np.maximum(4.,INNER_MIN_FRAC*width))
    interior &= (dist<=INNER_MAX_FRAC*width)
    return interior.astype(np.uint8)

def sobel_score(a,mask):
    f=a.astype(np.float32)
    gx=cv2.Sobel(f,cv2.CV_32F,1,0,ksize=3)
    gy=cv2.Sobel(f,cv2.CV_32F,0,1,ksize=3)
    mag=np.hypot(gx,gy)
    sel=(mask>0)&(mag>18)
    if not sel.any():
        return {"score":None,"energy":0.}
    theta=np.arctan2(gy[sel],gx[sel])+np.pi/2
    weights=mag[sel]
    swing=np.sin(2*theta)
    energy=float(weights.sum())
    denom=float(np.sum(weights*np.abs(swing)))+1e-9
    value=float(np.sum(weights*swing)/denom) if denom>0 else 0.
    return {"score":round(value,6) if energy>=MIN_SOBEL_ENERGY else None,
            "energy":round(energy,2)}

def hough_score(a,mask):
    edges=cv2.Canny(a,55,145)
    edges[mask==0]=0
    lines=cv2.HoughLinesP(edges,1,np.pi/180,threshold=6,
                          minLineLength=9,maxLineGap=3)
    positive=negative=0.
    if lines is not None:
        for x1,y1,x2,y2 in np.asarray(lines).reshape(-1,4):
            dx=float(x2-x1);dy=float(y2-y1)
            if abs(dx)<3:continue
            angle=math.degrees(math.atan2(dy,dx))
            while angle>90:angle-=180
            while angle<=-90:angle+=180
            if not(MIN_ANGLE_FROM_HORIZ<=abs(angle)<=MAX_ANGLE_FROM_HORIZ):
                continue
            length=math.hypot(dx,dy)
            if angle>0:positive+=length
            else:negative+=length
    total=positive+negative
    return {"score":round((positive-negative)/total,6)
            if total>=MIN_HOUGH_LENGTH else None,
            "length":round(total,2)}

def inspect_patch(p,half):
    m=mask_for_shape(p.shape,half)
    s=sobel_score(p,m)
    h=hough_score(p,m)
    if s["score"] is None or h["score"] is None:
        classification=None
    elif s["score"]>=CLASS_GATE and h["score"]>=CLASS_GATE:
        classification="POS"
    elif s["score"]<=-CLASS_GATE and h["score"]<=-CLASS_GATE:
        classification="NEG"
    else:
        classification=None
    return {"sobel":s,"hough":h,"class":classification,
            "mask_pixels":int(m.sum())}

def control_patch(site,kind):
    _,cx,top,h,half=site
    w=half*2+21
    center=(w-1)//2
    p=np.full((h,w),255,np.uint8)
    m=mask_for_shape(p.shape,half)
    hatch=np.full((h,w),255,np.uint8)
    # Only interior lines and NO triangle outline: avoids incorrectly measuring
    # outline orientation rather than diagonal pencil hatching.
    sign={"POS":1,"NEG":-1,"NEUTRAL":0}[kind]
    for offset in range(-125,125,7):
        if sign:
            y0=offset
            y1=int(round(offset+sign*.72*(w-1)))
        else:
            y0=y1=offset
        cv2.line(hatch,(0,y0),(w-1,y1),0,2,cv2.LINE_AA)
    p[m>0]=hatch[m>0]
    return p

def suite_controls():
    cases=[]
    errors=[]
    for site in SITES:
        for expected in ("POS","NEG","NEUTRAL"):
            synthetic=control_patch(site,expected)
            for variant,img in variants(synthetic).items():
                if variant not in MODES:continue
                reading=inspect_patch(img,site[4])
                observed=reading["class"]
                passed=(observed==expected if expected!="NEUTRAL"
                        else observed is None)
                case={"site":site[0],"kind":expected,
                      "variant":variant,"observed":observed,
                      "sobel":reading["sobel"]["score"],
                      "hough":reading["hough"]["score"],
                      "passed":bool(passed)}
                cases.append(case)
                if not passed:errors.append(case)
    return {"pass":len(errors)==0,"cases":len(cases),
            "passed_cases":len(cases)-len(errors),
            "failures":errors[:35]}

def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=EXPECTED_SHA:raise SystemExit("canonical SHA256 differs")
    im=np.asarray(Image.open(SOURCE).convert("L"))
    if im.shape!=(1105,1600):
        raise SystemExit("wrong image shape")
    controls=suite_controls()
    vv=variants(im)
    real=[]
    stable=[]
    for site in SITES:
        results={}
        per=[]
        for v in MODES:
            patch=get_patch(vv[v],site)
            a=inspect_patch(patch,site[4])
            results[v]=a
            per.append(a["class"])
        agreed=(per[0] if per[0] is not None
                and all(x==per[0] for x in per) else None)
        if agreed is not None:stable.append(agreed)
        real.append({"site":site[0],"stable":agreed,"per_variant":results})
    distinct=len(set(stable))
    sufficient=len(stable)>=4
    mixed=distinct==2 and sufficient
    decision=("CONTROL_FAILURE" if not controls["pass"] else
              "INSUFFICIENT_REAL_HATCH_COVERAGE" if not sufficient else
              "MIXED_SAIL_HATCH_DIRECTION_REQUIRES_REVIEW" if mixed else
              "NO_MIXED_FIVE_SAIL_HATCH_DIRECTION")
    result={
        "experiment_id":"A11-EXP-129",
        "hypothesis":"five genuine small sail interiors contain a replicated mixed signed diagonal hatch-orientation sequence",
        "evidence":"Stage 102 reused Stage19 mis-associated sail boxes; Stage112 showed that x~675 was not a sail and x~1490 was omitted. This is the corrected-object retry of interior-hatch polarity, not outline leaning.",
        "scope":"five true visible triangular sail interiors; Sobel gradient tangents versus Hough diagonal segments; original/JPEG85/JPEG70/75%-resampled",
        "canonical_sha256":sha,
        "sites":[list(x) for x in SITES],
        "gates":{"class_abs_score":CLASS_GATE,"sobel_min_energy":MIN_SOBEL_ENERGY,
                 "hough_min_diagonal_length":MIN_HOUGH_LENGTH,
                 "min_stable_sites":4,"both_signs_required":True},
        "controls":controls,
        "real":real,"stable_count":len(stable),
        "stable_classes":stable,"mixed":mixed,"decision":decision,
        "stop":"control failure => repair Stage129; <4/5 real stable => INCONCLUSIVE; >=4/5 but no mix => narrow negative; mixed => independent visual validation needed, not a cipher",
        "scope_limit":"Only texture tangent directions in fixed mask inside five correctly localized sails; does not assess arbitrary semantic symbols, precise stroke counts or cryptographic mappings.",
        "safety":"No key, mnemonic, wallet, address or outside-image operation.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=[
        "# Stage 129 — corrected true-five-sail interior hatch direction","",
        f"- SHA256 verified: **{sha==EXPECTED_SHA}**",
        f"- Synthetic controls: **{controls['passed_cases']}/{controls['cases']}**",
        f"- Stable real sail classes: **{len(stable)}/5**",
        f"- Both signs found: **{mixed}**",
        f"- Decision: **{decision}**","",
        "| sail | class | original Sobel | original Hough |",
        "|---|---|---:|---:|",
    ]
    for r in real:
        a=r["per_variant"]["original"]
        md.append(f"| {r['site']} | {r['stable'] or '?'} | {a['sobel']['score']} | {a['hough']['score']} |")
    md+=["","## Interpretation",""]
    if not controls["pass"]:
        md.append("Synthetic controls failed, fix Stage129; no real conclusion.")
    elif not sufficient:
        md.append("Insufficient stable diagonal texture across the five original sails. Inconclusive, not proof of absence.")
    elif mixed:
        md.append("Mixed diagonal texture found; requires independent image-only review before intentional-code speculation.")
    else:
        md.append("No stable mixed polarity under corrected true-sail masks. Retire this exact hatch-sign family only.")
    md+=["","No secret or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"stage":129,"controls":controls["pass"],
                      "stable":len(stable),"decision":decision}))
if __name__=="__main__":
    main()
