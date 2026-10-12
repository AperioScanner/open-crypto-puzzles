#!/usr/bin/env python3
"""Stage 102: five-small-sail directional-orientation audit.

Safe structural experiment only. Tests whether the five small sailboats form a
robust left/right visible orientation sequence.

No private-key generation, derivation, reconstruction, enumeration,
verification, or wallet access is performed.
"""
from __future__ import annotations

import io, json, math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
RUN19=ROOT/"analysis"/"runs"/"stage19-small-sail-remeasure"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage102-small-sail-direction"
OUT.mkdir(parents=True,exist_ok=True)

Y0,Y1=360,480
THRESHOLDS=(100,140,180)
PAD=8

def load_gray():
    return np.array(Image.open(SOURCE).convert("L"))

def variants(gray):
    out={"original":gray}
    for q in (85,70):
        b=io.BytesIO()
        Image.fromarray(gray).save(b,format="JPEG",quality=q,optimize=False,progressive=False)
        b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("L"))
    h,w=gray.shape
    small=Image.fromarray(gray).resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(small.resize((w,h),Image.Resampling.LANCZOS))
    return out

def boxes():
    j=json.loads(RUN19.read_text())
    tracks=j["methods"][0]["stable_tracks"]
    out=[]
    for t in tracks:
        # Median x extents from threshold observations.
        x0=int(round(np.median([z["x0"] for z in t["items"]]))) - PAD
        x1=int(round(np.median([z["x1"] for z in t["items"]]))) + PAD
        out.append((x0,Y0,x1,Y1))
    return out

def crop(a,b):
    x0,y0,x1,y1=b
    return a[y0:y1,x0:x1]

def hough_score(c,thr):
    bw=((c<thr).astype(np.uint8)*255)
    e=cv2.Canny(bw,50,150)
    raw=cv2.HoughLinesP(e,1,np.pi/180,threshold=10,minLineLength=12,maxLineGap=5)
    pos=neg=0.0
    if raw is not None:
        for x1,y1,x2,y2 in np.asarray(raw).reshape(-1,4):
            dx=float(x2-x1); dy=float(y2-y1)
            ln=math.hypot(dx,dy)
            if ln<12: continue
            ang=math.degrees(math.atan2(dy,dx))
            while ang>90: ang-=180
            while ang<=-90: ang+=180
            if not (18<=abs(ang)<=75):
                continue
            if ang>0: pos+=ln
            else: neg+=ln
    return float((pos-neg)/(pos+neg+1e-9))

def sobel_score(c):
    x=c.astype(np.float32)
    gx=cv2.Sobel(x,cv2.CV_32F,1,0,ksize=3)
    gy=cv2.Sobel(x,cv2.CV_32F,0,1,ksize=3)
    mag=np.hypot(gx,gy)
    if np.max(mag)<=1e-9: return 0.0
    cut=np.percentile(mag,72)
    m=mag>=cut
    # Edge tangent angle = gradient angle + 90deg.
    theta=np.arctan2(gy[m],gx[m])+np.pi/2
    # sin(2theta) gives signed diagonal orientation and ignores 180deg polarity.
    w=mag[m]
    num=float(np.sum(w*np.sin(2*theta)))
    den=float(np.sum(w*np.abs(np.sin(2*theta)))+1e-9)
    return num/den

def direction(score,dead=0.12):
    if score>dead: return "R"
    if score<-dead: return "L"
    return "?"

def synthetic(lean):
    im=np.full((120,100),255,np.uint8)
    # mast + triangular sail + hull
    cv2.line(im,(50,18),(50,92),0,2,cv2.LINE_AA)
    if lean=="R":
        pts=np.array([[51,24],[52,78],[86,72]],np.int32)
    else:
        pts=np.array([[49,24],[48,78],[14,72]],np.int32)
    cv2.polylines(im,[pts],True,0,2,cv2.LINE_AA)
    cv2.line(im,(18,93),(82,93),0,2,cv2.LINE_AA)
    return im

def eval_crop(c):
    hs=[hough_score(c,t) for t in THRESHOLDS]
    hmed=float(np.median(hs))
    ss=float(sobel_score(c))
    hd=direction(hmed)
    sd=direction(ss)
    consensus=hd if hd==sd and hd!="?" else "?"
    return {
        "hough_scores":hs,
        "hough_median":hmed,
        "sobel_score":ss,
        "hough_direction":hd,
        "sobel_direction":sd,
        "consensus":consensus,
    }

def main():
    gray=load_gray()
    vv=variants(gray)
    bb=boxes()
    if len(bb)!=5:
        raise SystemExit(f"expected 5 small-sail boxes, got {len(bb)}")

    controls={}
    for lean in ("L","R"):
        e=eval_crop(synthetic(lean))
        controls[lean]=e
    controls_pass=(controls["L"]["consensus"]=="L" and controls["R"]["consensus"]=="R")

    per=[]
    stable_count=0
    seq=[]
    for i,b in enumerate(bb,1):
        ev={name:eval_crop(crop(a,b)) for name,a in vv.items()}
        dirs=[ev[v]["consensus"] for v in vv]
        nonq=[d for d in dirs if d!="?"]
        stable=(len(nonq)==4 and len(set(nonq))==1)
        d=nonq[0] if stable else "?"
        if stable: stable_count+=1
        seq.append(d)
        per.append({"id":i,"box":list(b),"variants":ev,"stable":stable,"direction":d})

    classes=set(x for x in seq if x in ("L","R"))
    nontrivial=(classes=={"L","R"})
    promoted=bool(controls_pass and stable_count>=4 and nontrivial)

    result={
        "experiment_id":"A11-EXP-102",
        "scope":"five small-sail left/right visible orientation stability; no private-key operations",
        "band_y":[Y0,Y1],
        "boxes":[list(x) for x in bb],
        "thresholds":list(THRESHOLDS),
        "synthetic_controls":controls,
        "controls_pass":controls_pass,
        "sails":per,
        "stable_sails":stable_count,
        "visible_direction_sequence":"".join(seq),
        "both_direction_classes_present":nontrivial,
        "promotion_rule":"synthetic L/R controls pass; >=4/5 sails have same Hough+Sobel consensus direction in all four image variants; both L and R appear",
        "promoted":promoted,
        "interpretation_guard":"Promotion establishes only a robust visible L/R object sequence, not a key mapping.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 102 — five-small-sail directional-orientation audit",
        "",
        "**Experiment:** A11-EXP-102",
        "",
        f"- synthetic controls pass: **{controls_pass}**",
        f"- stable sails: **{stable_count}/5**",
        f"- visible sequence: **{''.join(seq)}**",
        f"- both direction classes present: **{nontrivial}**",
        f"- promoted: **{promoted}**",
        "",
        "| sail | direction | stable | original Hough | original Sobel |",
        "|---:|:---:|:---:|---:|---:|",
    ]
    for r in per:
        o=r["variants"]["original"]
        md.append(f"| {r['id']} | {r['direction']} | {r['stable']} | {o['hough_median']:.3f} | {o['sobel_score']:.3f} |")
    md += ["","## Interpretation",""]
    if promoted:
        md.append("The five small sailboats contain a robust mixed L/R orientation sequence that survives lossy re-encoding under two independent estimators. This sequence is eligible for a semantic ordering/selection follow-up.")
    else:
        md.append("The small sailboats do not provide a sufficiently stable, nontrivial L/R sequence. Retire sail-direction coding.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-102",
        "controls_pass":controls_pass,"stable":stable_count,
        "sequence":"".join(seq),"promoted":promoted
    }))

if __name__=="__main__":
    main()
