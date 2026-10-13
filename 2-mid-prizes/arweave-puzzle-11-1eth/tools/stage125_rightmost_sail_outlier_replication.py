#!/usr/bin/env python3
"""Stage 125: independent adversarial validation of Stage 124's one left-offset sail.

In Stage 124 the rightmost small sail alone met the negative lateral outline
offset gate, but the second sail was just below its signed-class threshold.
This NEW direct source observation motivates an adversarial source-geometry
check: does the fifth sail stay substantially more left-offset than all other
four under tiny apex placement jitters, thresholds, formats and a separate
localized edge/raster envelope routine? No words or keys are processed.
"""
from __future__ import annotations

import hashlib, json, itertools
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage124_true_sail_outline_offset import SITES, draw_control

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage125-rightmost-sail-outlier"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
X_JITTER=(-4,0,4)
Y_JITTER=(-3,0,3)
THRESHOLDS=(155,175,195)
METHODS=("binary","canny")
ROW_MIN=.54
MIN_OUTLIER_GAP=.16
LEFT_OFFSET_MIN=-.28
MIN_FRACTION=.90
MIN_EVALUATED_FRACTION=.90

def one_site(image,site,dx,dy,thr,method):
    _,cx,top,height,half=site
    cx=int(cx+dx);top=int(top+dy)
    x0=max(0,cx-2*half-16);x1=min(image.shape[1],cx+2*half+17)
    y0=max(0,top-7);y1=min(image.shape[0],top+height+7)
    crop=image[y0:y1,x0:x1]
    if method=="binary":
        mask=(crop<thr)
    else:
        mask=cv2.Canny(crop,max(15,int(thr*.32)),min(250,int(thr*.85)))>0
    offsets=[];tot=0
    band=max(8,int(round(.56*half)))
    for y in range(top+int(.39*height),top+int(.73*height)):
        tot+=1
        t=(y-(top+3))/float(max(1,height-3))
        yi=y-y0
        if yi<0 or yi>=mask.shape[0]: continue
        candidates=[]
        for center,is_left in ((cx-half*t,True),(cx+half*t,False)):
            lo=max(0,int(round(center-band))-x0)
            hi=min(mask.shape[1],int(round(center+band+1))-x0)
            indexes=np.flatnonzero(mask[yi,lo:hi])
            if not len(indexes):
                candidates.append(None)
            else:
                candidates.append(float(x0+lo+(indexes[0] if is_left else indexes[-1])))
        if None in candidates: continue
        left,right=candidates
        if not .45*2*half*t<=right-left<=2.35*2*half*t: continue
        offsets.append(((left+right)/2-cx)/max(.15,t)/half)
    if tot==0 or len(offsets)/tot<ROW_MIN:
        return None
    return float(np.median(offsets))

def suite(gray):
    vv=variants(gray)
    checks=[]
    for fmt,dx,dy,thr,method in itertools.product(
        FORMATS,X_JITTER,Y_JITTER,THRESHOLDS,METHODS
    ):
        vals=[one_site(vv[fmt],site,dx,dy,thr,method) for site in SITES]
        if any(v is None for v in vals):
            checks.append({"cfg":[fmt,dx,dy,thr,method],"valid":False})
            continue
        order=np.argsort(vals)
        most=int(order[0])
        gap=float(vals[order[1]]-vals[most])
        strong=bool(most==4 and gap>=MIN_OUTLIER_GAP and vals[4]<=LEFT_OFFSET_MIN)
        checks.append({"cfg":[fmt,dx,dy,thr,method],"valid":True,
                       "rightmost_is_outlier":strong,
                       "rightmost":round(float(vals[4]),5),
                       "runner_up_gap":round(gap,5),
                       "winner_sail":most+1})
    valid=[x for x in checks if x["valid"]]
    pos=sum(x["rightmost_is_outlier"] for x in valid)
    return {
        "cases":len(checks),"valid_cases":len(valid),
        "valid_fraction":round(len(valid)/len(checks),5),
        "rightmost_strong_outlier":pos,
        "rightmost_strong_fraction":round(pos/max(1,len(valid)),5),
        "min_rightmost_offset":round(min((x["rightmost"] for x in valid),default=0),5),
        "max_rightmost_offset":round(max((x["rightmost"] for x in valid),default=0),5),
        "winner_counts":{str(i):sum(x["winner_sail"]==i for x in valid)
                         for i in range(1,6)},
    }

def synthetic_scene(has_outlier):
    a=np.full((1105,1600),255,np.uint8)
    for i,site in enumerate(SITES):
        p=draw_control(site,"L" if has_outlier and i==4 else "N")
        # For the positive signal, the exact Stage-124 L offset -0.65
        # suffices for the fixed gap .16 when checked against 4 neutrals.
        a=np.minimum(a,p)
    return a

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if sha!=SHA: raise SystemExit("canonical input hash mismatch")
    image=np.array(Image.open(PNG).convert("L"))
    if image.shape!=(1105,1600): raise SystemExit("incorrect image dimensions")
    positive=suite(synthetic_scene(True))
    negative=suite(synthetic_scene(False))
    real=suite(image)
    positive_ok=(positive["valid_fraction"]>=MIN_EVALUATED_FRACTION
                 and positive["rightmost_strong_fraction"]>=MIN_FRACTION)
    negative_ok=(negative["valid_fraction"]>=MIN_EVALUATED_FRACTION
                 and negative["rightmost_strong_fraction"]<=.05)
    controls_pass=positive_ok and negative_ok
    covered=real["valid_fraction"]>=MIN_EVALUATED_FRACTION
    observed=real["rightmost_strong_fraction"]>=MIN_FRACTION
    decision=("CONTROL_FAILURE" if not controls_pass else
              "INSUFFICIENT_SOURCE_COVERAGE" if not covered else
              "REPLICATED_RIGHTMOST_OUTLIER" if observed else
              "UNREPLICATED_RIGHTMOST_OUTLIER")
    result={
        "experiment_id":"A11-EXP-125",
        "hypothesis":"Stage 124's single left-leaning rightmost sail is a genuine stand-out geometry signal rather than nearby-object contamination or apex anchoring jitter",
        "scope":"five correct small sails, ±4px x / ±3px y anchor jitter, three fixed ink thresholds, local binary+Canny envelope, four re-encodings; image only",
        "canonical_sha256":sha,
        "gates":{"x_jitter":list(X_JITTER),"y_jitter":list(Y_JITTER),
                 "thresholds":list(THRESHOLDS),"min_second_best_gap":MIN_OUTLIER_GAP,
                 "rightmost_max_offset":LEFT_OFFSET_MIN,
                 "min_fraction":MIN_FRACTION,
                 "min_source_coverage":MIN_EVALUATED_FRACTION},
        "control_fifth_left":positive,"control_all_neutral":negative,
        "controls_pass":controls_pass,"real":real,
        "coverage_pass":covered,"decision":decision,
        "interpretation_guard":"Only one visual outlier diagnostic. Nothing is mapped to a symbol, secret, wallet, or BIP39 word. A negative is not a negative for all other picture semantics.",
        "safety_guard":"No key generation, enumeration, verification, wallet access, or external social research.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=[
        "# Stage 125 — independent rightmost-sail outline-outlier audit","",
        f"- Canonical image verified: **{sha==SHA}**",
        f"- Synthetic unique-left control: **{positive['rightmost_strong_fraction']:.3f}**",
        f"- Synthetic all-neutral false positive: **{negative['rightmost_strong_fraction']:.3f}**",
        f"- Controls pass: **{controls_pass}**",
        f"- Real usable configurations: **{real['valid_cases']}/{real['cases']}**",
        f"- Real fifth-sail strong-outlier fraction: **{real['rightmost_strong_fraction']:.3f}**",
        f"- Decision: **{decision}**",
        "",
        "Does not infer intent or a secret and does not broaden any old negative.",""
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"stage":125,"controls_pass":controls_pass,
                      "real_valid":real["valid_fraction"],
                      "rightmost_outlier":real["rightmost_strong_fraction"],
                      "decision":decision}))
if __name__=="__main__":
    main()
