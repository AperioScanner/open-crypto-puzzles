#!/usr/bin/env python3
"""Stage 127: five small-boat hull waterline slopes (image only).

Investigates the visible lower hull/waterline, NOT sail orientation, mastheads,
sail outline offsets, shading, sail widths or duplicated raster templates.

Five static hull strips are derived from pre-existing apex/height annotations.
Signed horizontal-ish Hough segment slopes are measured independently from
gray-threshold and Canny edges in 4 image variants. Synthetic up/down/level
hulls and unrelated-diagonal decoys are calibrated first.

No wallet, BIP39, key or social-content operations.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage127-hull-waterline-slope"
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
SITES=(
    ("sail_1",1042,448,98,35),
    ("sail_2",1148,433,99,38),
    ("sail_3",1282,411,103,44),
    ("sail_4",1372,397,101,42),
    ("sail_5",1490,357,106,47),
)
FORMATS=("original","jpeg85","jpeg70","down75_up")
METHODS=("edge","binary")
SLOPE_SIGN=.12
SLOPE_LEVEL=.055
MIN_SEGMENTS=2
MIN_LENGTH_TOTAL=48.
MAX_SLOPE=.58

def crop(img,site):
    _,cx,top,h,half=site
    by=top+h
    return img[by-7:by+34,cx-half-18:cx+half+19].copy()

def weighted_median(values,weights):
    ix=np.argsort(values)
    v=np.asarray(values)[ix]
    w=np.asarray(weights)[ix]
    return float(v[np.searchsorted(np.cumsum(w),.5*sum(w))])

def measure(img,site,method):
    c=crop(img,site)
    if c.size==0 or min(c.shape)<20:
        return {"valid":False,"reason":"crop"}
    if method=="edge":
        mask=cv2.Canny(c,50,130)
    elif method=="binary":
        dark=(c<165).astype(np.uint8)*255
        mask=cv2.Canny(dark,55,145)
    else:
        raise ValueError(method)
    lines=cv2.HoughLinesP(mask,1,np.pi/180,threshold=12,
                          minLineLength=17,maxLineGap=5)
    slopes=[]; lengths=[]; accepted=[]
    if lines is not None:
        for x1,y1,x2,y2 in np.asarray(lines).reshape(-1,4):
            dx=float(x2-x1);dy=float(y2-y1)
            if abs(dx)<15:
                continue
            slope=dy/dx
            ln=math.hypot(dx,dy)
            midx=(x1+x2)/2;midy=(y1+y2)/2
            # Keep the hull middle, not sail mast or lower slanting pier.
            if (abs(slope)>MAX_SLOPE or
                not(5<=midy<=29) or
                not(9<=midx<=c.shape[1]-10)):
                continue
            slopes.append(float(slope))
            lengths.append(float(ln))
            accepted.append([int(x1),int(y1),int(x2),int(y2)])
    support=float(sum(lengths))
    valid=(len(slopes)>=MIN_SEGMENTS and support>=MIN_LENGTH_TOTAL)
    med=weighted_median(slopes,lengths) if valid else None
    cls=None if med is None else (
        "DOWN_RIGHT" if med>=SLOPE_SIGN else
        "UP_RIGHT" if med<=-SLOPE_SIGN else
        "LEVEL" if abs(med)<=SLOPE_LEVEL else
        None
    )
    return {"valid":bool(valid),"segments":len(slopes),
            "total_length":round(support,3),
            "median_slope":round(med,5) if med is not None else None,
            "class":cls,"segments_first3":accepted[:3]}

def synthetic(kind,decoy=False):
    img=np.full((1105,1600),255,np.uint8)
    # Every vessel has a fixed triangular sail above its separate hull.
    for name,cx,top,h,half in SITES:
        by=top+h
        pts=[(cx,top+8),(cx-half,by-9),(cx+half,by-9)]
        cv2.line(img,pts[0],pts[1],0,2,cv2.LINE_AA)
        cv2.line(img,pts[0],pts[2],0,2,cv2.LINE_AA)
        cv2.line(img,pts[1],pts[2],0,1,cv2.LINE_AA)
        cls=kind[name]
        slope={"DOWN_RIGHT":.26,"UP_RIGHT":-.26,"LEVEL":0.}[cls]
        left=cx-half-11
        right=cx+half+11
        mid=(left+right)/2
        for off in (6,10,15,20):
            # Four thick, slightly different hull pencil strokes.
            a=(left,int(round(by+off+slope*(left-mid))))
            b=(right,int(round(by+off+slope*(right-mid))))
            cv2.line(img,a,b,0,2,cv2.LINE_AA)
        if decoy:
            # Unrelated diagonal just BELOW selected Hough-midpoint band.
            cv2.line(img,(cx-12,by+29),(cx+12,by+38),0,2,cv2.LINE_AA)
    return img

def classify_scene(image):
    transformed=variants(image)
    outputs=[]
    for site in SITES:
        readings=[]
        classes=[]
        for v in FORMATS:
            for method in METHODS:
                r=measure(transformed[v],site,method)
                readings.append({"variant":v,"method":method,**r})
                classes.append(r["class"])
        agreed=(classes[0] if all(c==classes[0] and c is not None
                                for c in classes) else None)
        outputs.append({"site":site[0],"stable_class":agreed,
                        "readings":readings})
    return outputs

def count_classes(rows):
    return {k:sum(x["stable_class"]==k for x in rows)
            for k in ("UP_RIGHT","LEVEL","DOWN_RIGHT")}

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if sha!=EXPECTED_SHA: raise SystemExit("Canonical PNG mismatch")
    im=np.array(Image.open(PNG).convert("L"))
    if im.shape!=(1105,1600): raise SystemExit("PNG dimensions mismatch")
    neutral={s[0]:"LEVEL" for s in SITES}
    mixed={s[0]:k for s,k in zip(SITES,
        ("DOWN_RIGHT","UP_RIGHT","DOWN_RIGHT","UP_RIGHT","LEVEL"))}
    ctrl_mixed=classify_scene(synthetic(mixed))
    ctrl_neutral=classify_scene(synthetic(neutral,decoy=True))
    positive_pass=all(a["stable_class"]==mixed[a["site"]] for a in ctrl_mixed)
    negative_pass=all(a["stable_class"]=="LEVEL" for a in ctrl_neutral)
    controls={"positive_mixed_pass":bool(positive_pass),
              "negative_level_with_decoy_pass":bool(negative_pass),
              "pass":bool(positive_pass and negative_pass),
              "mixed_classes":{x["site"]:x["stable_class"] for x in ctrl_mixed},
              "neutral_classes":{x["site"]:x["stable_class"] for x in ctrl_neutral}}

    real=classify_scene(im)
    stable=sum(x["stable_class"] is not None for x in real)
    counts=count_classes(real)
    mixed_real=counts["UP_RIGHT"]>0 and counts["DOWN_RIGHT"]>0 and stable>=4
    decision=("CONTROL_FAILURE" if not controls["pass"] else
              "INSUFFICIENT_HULL_ISOLATION" if stable<4 else
              "MIXED_HULL_SLOPE_CANDIDATE" if mixed_real else
              "NO_MIXED_HULL_SLOPES")

    result={
        "experiment_id":"A11-EXP-127",
        "hypothesis":"small-boat hull waterlines show stable opposite-sign slopes across boats rather than a consistent drawing/perspective convention",
        "scope":"five predeclared hull bands below five corrected sail tips; binary-edge and Canny Hough on four variants; excludes sail panel, masts and isolated tilted strokes",
        "canonical_sha256":sha,
        "hull_sites":[list(x) for x in SITES],
        "thresholds":{"min_segments":MIN_SEGMENTS,"min_line_length_sum":MIN_LENGTH_TOTAL,
                      "up_down_gate":SLOPE_SIGN,"neutral_gate":SLOPE_LEVEL,
                      "max_abs_slope":MAX_SLOPE},
        "controls":controls,"real":real,"stable_sites":stable,
        "real_classes":counts,"mixed":bool(mixed_real),
        "decision":decision,
        "stopping_rule":"Fail synthetic copied opposite-sign hull and level-with-pier-decoy controls => repair Stage127; if <4/5 real hulls classify stably => inconclusive; if both UP/DOWN stable and >=4/5 => visual candidate to verify; otherwise narrow negative.",
        "scope_limit":"This tests only keel/hull waterline inclination in these exact windows. Unseen symbols, arbitrary hull silhouettes and perspective are not ruled out.",
        "safety_guard":"No seed phrases, private keys, BIP39, wallet operations or outside-image references."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    # Preserve source alignment evidence in a 5-crop contact strip for audit.
    contact=Image.new("RGB",(240*5,150),"white")
    draw=ImageDraw.Draw(contact)
    for i,site in enumerate(SITES):
        a=crop(im,site)
        pil=Image.fromarray(a).resize((214,100),Image.Resampling.NEAREST).convert("RGB")
        contact.paste(pil,(i*240+8,32))
        draw.text((i*240+8,7),site[0]+" "+str(real[i]["stable_class"]),fill="black")
    contact.save(OUT/"hull-roi-contact.png")
    md=["# Stage 127 — small-hull waterline angle test","",
        f"- Source SHA256 verified: **{sha==EXPECTED_SHA}**",
        f"- Synthetic mixed positive and level+decoy negatives: **{controls['pass']}**",
        f"- Real hulls stably classified: **{stable}/5**",
        f"- Sign classes: **{counts}**",
        f"- Decision: **{decision}**","",
        "| hull | stable class |",
        "|---|---|"]
    for row in real: md.append(f"| {row['site']} | {row['stable_class'] or '?'} |")
    md+=["","## Interpretation","",
       ("Controls failed; do not draw real-image conclusions."
        if not controls["pass"] else
        "Too few real hulls localized reliably; this is INCONCLUSIVE."
        if stable<4 else
        "Opposite hull slopes detected; review the actual ROI sheet before interpreting."
        if mixed_real else
        "No stable bidirectional hull-waterline code under these fixed masks; retire only this exact signed-slope hypothesis."),
       "","No secret material handled.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"stage":127,"controls":controls["pass"],"stable":stable,
                      "decision":decision}))

if __name__=="__main__":main()
