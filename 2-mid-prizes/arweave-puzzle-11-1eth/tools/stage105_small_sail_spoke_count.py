#!/usr/bin/env python3
"""Stage 105 (corrected): five-small-sail radial-spoke count audit.

The first implementation failed its synthetic controls and also inherited one
spurious Stage-19 x-track outside the actual right-hand sail cluster. This
rerun repairs both issues under the same stage number.

Safe visual-structure experiment only. No private-key operations.
"""
from __future__ import annotations
import io, json, math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage105-small-sail-spoke-count"
OUT.mkdir(parents=True,exist_ok=True)

SEARCH=(900,345,1585,500)
THR=165
MIN_SEP=70

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

def smooth1(x,k=19):
    ker=np.ones(k)/k
    return np.convolve(x,ker,mode="same")

def detect_centers(gray):
    x0,y0,x1,y1=SEARCH
    band=(gray[y0:y1,x0:x1]<THR).astype(float)
    # Emphasize upper 75% so hull/jetty contributes less than triangular sails.
    hh=band.shape[0]
    weights=np.linspace(1.35,0.35,hh)[:,None]
    score=smooth1(np.sum(band*weights,axis=0),21)
    candidates=[]
    for i in range(8,len(score)-8):
        if score[i]==np.max(score[i-8:i+9]):
            candidates.append((float(score[i]),i+x0))
    chosen=[]
    for sc,x in sorted(candidates,reverse=True):
        if all(abs(x-y)>=MIN_SEP for _,y in chosen):
            chosen.append((sc,x))
        if len(chosen)>=5:
            break
    chosen=sorted(chosen,key=lambda z:z[1])
    return [int(x) for _,x in chosen],score

def boxes_from_centers(centers,shape):
    h,w=shape
    if len(centers)!=5:
        return []
    mids=[(a+b)//2 for a,b in zip(centers[:-1],centers[1:])]
    edges=[max(900,centers[0]-55)]+mids+[min(w-1,centers[-1]+60)]
    boxes=[]
    for i,c in enumerate(centers):
        boxes.append((edges[i],345,edges[i+1],500))
    return boxes

def crop(a,b):
    x0,y0,x1,y1=b
    return a[y0:y1,x0:x1]

def skeletonize(binary):
    img=(binary>0).astype(np.uint8)*255
    sk=np.zeros_like(img)
    el=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    while True:
        er=cv2.erode(img,el)
        op=cv2.dilate(er,el)
        sk=cv2.bitwise_or(sk,cv2.subtract(img,op))
        img=er
        if cv2.countNonZero(img)==0:
            break
    return sk

def apex(c):
    bw=c<185
    h,w=bw.shape
    # Ignore first/last 5% x to avoid crop-boundary clutter.
    xa=max(2,int(0.05*w)); xb=min(w-2,int(0.95*w))
    ys,xs=np.where(bw[:int(0.70*h),xa:xb])
    if len(ys)==0:
        return w/2,8.0
    xs=xs+xa
    ymin=int(np.min(ys))
    m=ys<=ymin+10
    return float(np.median(xs[m])),float(ymin+2)

def cluster_angles(angles,gap=5.5):
    if not angles: return []
    aa=sorted(angles)
    groups=[[aa[0]]]
    for a in aa[1:]:
        if a-groups[-1][-1]<=gap:
            groups[-1].append(a)
        else:
            groups.append([a])
    return [float(np.median(g)) for g in groups if len(g)>=1]

def annulus_count(c):
    ax,ay=apex(c)
    dark=(c<THR).astype(np.uint8)
    dark=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,np.ones((2,2),np.uint8),iterations=1)
    sk=skeletonize(dark)
    yy,xx=np.where(sk>0)
    dx=xx-ax; dy=yy-ay
    rr=np.hypot(dx,dy)
    m=(dy>5)&(rr>=18)&(rr<=46)
    ang=np.degrees(np.arctan2(dx[m],dy[m]))
    ang=ang[(ang>=-62)&(ang<=62)]
    clusters=cluster_angles(ang.tolist(),5.5)
    return {"count":len(clusters),"angles":clusters,"apex":[ax,ay]}

def run_count_at_row(sk,y,ax):
    if y<0 or y>=sk.shape[0]:
        return 0,[]
    row=sk[y,:]>0
    xs=np.flatnonzero(row)
    if len(xs)==0: return 0,[]
    groups=[[int(xs[0])]]
    for x in xs[1:]:
        if int(x)-groups[-1][-1]<=3:
            groups[-1].append(int(x))
        else:
            groups.append([int(x)])
    centers=[float(np.median(g)) for g in groups]
    centers=[x for x in centers if abs(x-ax)<=0.48*sk.shape[1]]
    return len(centers),centers

def scanline_count(c):
    ax,ay=apex(c)
    dark=(c<THR).astype(np.uint8)
    dark=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,np.ones((2,2),np.uint8),iterations=1)
    sk=skeletonize(dark)
    vals=[]; rows=[]
    for off in (28,36,44):
        n,centers=run_count_at_row(sk,int(round(ay+off)),ax)
        vals.append(n); rows.append({"offset":off,"count":n,"centers":centers})
    return {"count":int(round(np.median(vals))),"rows":rows,"apex":[ax,ay]}

def eval_crop(c):
    a=annulus_count(c)
    s=scanline_count(c)
    agree=abs(a["count"]-s["count"])<=1
    consensus=int(round((a["count"]+s["count"])/2)) if agree else None
    return {"annulus":a,"scanline":s,"agreement":agree,"consensus":consensus}

def synthetic(n,w=120,h=145):
    im=np.full((h,w),255,np.uint8)
    ax=w//2; ay=12; by=105
    cv2.line(im,(ax,ay),(16,by),0,2,cv2.LINE_AA)
    cv2.line(im,(ax,ay),(104,by),0,2,cv2.LINE_AA)
    cv2.line(im,(16,by),(104,by),0,2,cv2.LINE_AA)
    for bx in np.linspace(25,95,n):
        cv2.line(im,(ax,ay+1),(int(round(bx)),by-3),0,2,cv2.LINE_AA)
    return im

def main():
    gray=load_gray()
    vv=variants(gray)
    centers,_=detect_centers(gray)
    boxes=boxes_from_centers(centers,gray.shape)
    if len(boxes)!=5:
        raise SystemExit(f"expected five detected sails, centers={centers}")

    controls={}
    det_a=[]; det_s=[]
    for n in (3,4,5,6,7):
        e=eval_crop(synthetic(n))
        controls[str(n)]=e
        det_a.append(e["annulus"]["count"])
        det_s.append(e["scanline"]["count"])
    mono_a=all(b>a for a,b in zip(det_a,det_a[1:]))
    mono_s=all(b>a for a,b in zip(det_s,det_s[1:]))
    controls_pass=bool(mono_a and mono_s)

    sails=[]; seq=[]; stable=0
    for i,b in enumerate(boxes,1):
        per={name:eval_crop(crop(a,b)) for name,a in vv.items()}
        vals=[per[v]["consensus"] for v in vv]
        ok=bool(all(x is not None for x in vals) and len(set(vals))==1)
        val=int(vals[0]) if ok else None
        if ok: stable+=1
        seq.append(val)
        sails.append({"id":i,"box":list(b),"variants":per,"stable":ok,"count":val})

    distinct=sorted(set(x for x in seq if x is not None))
    promoted=bool(controls_pass and stable>=4 and len(distinct)>=2)

    result={
        "experiment_id":"A11-EXP-105",
        "implementation_correction":"Replaced failed Hough/radial pair with skeleton-annulus + scanline-crossing estimators and re-detected the five sails only within the actual right-hand sail cluster x=900..1585.",
        "scope":"internal spoke/ray structure in five automatically detected right-hand small sails; no private-key operations",
        "search_box":list(SEARCH),
        "detected_centers":centers,
        "detected_boxes":[list(x) for x in boxes],
        "synthetic_controls":controls,
        "synthetic_annulus_counts":det_a,
        "synthetic_scanline_counts":det_s,
        "synthetic_annulus_monotonic":mono_a,
        "synthetic_scanline_monotonic":mono_s,
        "controls_pass":controls_pass,
        "sails":sails,
        "stable_sails":stable,
        "stable_spoke_sequence":seq,
        "distinct_stable_counts":distinct,
        "promotion_rule":"both synthetic 3..7-spoke detector responses are strictly monotonic; >=4/5 real sails have same consensus count across original/JPEG85/JPEG70/resize; >=2 distinct stable counts",
        "promoted":promoted,
        "interpretation_guard":"Promotion establishes only a robust visible internal-ray count sequence, not a secret mapping.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    seqtxt=" ".join("?" if x is None else str(x) for x in seq)
    md=[
        "# Stage 105 — corrected small-sail radial-spoke audit",
        "",
        f"- detected sail centers: **{centers}**",
        f"- synthetic annulus counts 3..7: **{det_a}**",
        f"- synthetic scanline counts 3..7: **{det_s}**",
        f"- controls pass: **{controls_pass}**",
        f"- stable real sails: **{stable}/5**",
        f"- stable sequence: **{seqtxt}**",
        f"- distinct counts: **{distinct}**",
        f"- promoted: **{promoted}**",
        "",
        "| sail | box | count | stable | original annulus | original scanline |",
        "|---:|:---|---:|:---:|---:|---:|",
    ]
    for r in sails:
        o=r["variants"]["original"]
        md.append(f"| {r['id']} | {r['box']} | {'' if r['count'] is None else r['count']} | {r['stable']} | {o['annulus']['count']} | {o['scanline']['count']} |")
    md += ["","## Interpretation",""]
    if not controls_pass:
        md.append("The corrected detector still fails synthetic controls. Stage 105 remains an implementation failure; do not interpret real-sail counts.")
    elif promoted:
        md.append("The five small sails contain a robust, nontrivial internal-ray count sequence across two estimators and lossy variants.")
    else:
        md.append("The validated detector finds no sufficiently stable, nontrivial internal-ray count sequence. Retire small-sail spoke-count coding.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-105","centers":centers,"controls_pass":controls_pass,"stable":stable,"sequence":seq,"promoted":promoted}))

if __name__=="__main__":
    main()
