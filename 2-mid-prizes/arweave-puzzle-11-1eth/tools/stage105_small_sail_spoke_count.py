#!/usr/bin/env python3
"""Stage 105: five-small-sail radial-spoke count audit.

Safe visual-structure experiment only.

Tests whether the five small sails carry robust counts of apex-to-base rays.
Prior sail stages tested widths, gaps and lean direction, not internal spoke
counts.

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
OUT=ROOT/"analysis"/"runs"/"stage105-small-sail-spoke-count"
OUT.mkdir(parents=True,exist_ok=True)

Y0,Y1=360,480
PAD=8
THRESHOLDS=(120,160,200)

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
        x0=int(round(np.median([z["x0"] for z in t["items"]]))) - PAD
        x1=int(round(np.median([z["x1"] for z in t["items"]]))) + PAD
        out.append((x0,Y0,x1,Y1))
    return out

def crop(a,b):
    x0,y0,x1,y1=b
    return a[y0:y1,x0:x1]

def apex(c,thr=180):
    bw=c<thr
    h,w=bw.shape
    ys,xs=np.where(bw[:max(12,int(0.60*h)),:])
    if len(ys)==0:
        return (w/2,10.0)
    ymin=int(ys.min())
    m=ys<=ymin+12
    xx=xs[m]
    # Ignore extreme crop borders if possible.
    xx=xx[(xx>=2)&(xx<=w-3)] if len(xx) else xx
    ax=float(np.median(xx)) if len(xx) else w/2
    return ax,float(ymin+2)

def cluster_angles(angles,sep=7.0):
    if not angles: return []
    aa=sorted(float(x) for x in angles)
    groups=[[aa[0]]]
    for a in aa[1:]:
        if a-groups[-1][-1]<=sep:
            groups[-1].append(a)
        else:
            groups.append([a])
    return [float(np.median(g)) for g in groups]

def point_line_distance(px,py,x1,y1,x2,y2):
    den=math.hypot(x2-x1,y2-y1)
    if den<1e-9: return 1e9
    return abs((y2-y1)*px-(x2-x1)*py+x2*y1-y2*x1)/den

def hough_count(c):
    ax,ay=apex(c)
    counts=[]
    angle_sets=[]
    for thr in THRESHOLDS:
        bw=((c<thr).astype(np.uint8)*255)
        e=cv2.Canny(bw,50,150)
        raw=cv2.HoughLinesP(
            e,1,np.pi/180,threshold=8,
            minLineLength=max(10,int(0.18*c.shape[0])),maxLineGap=5
        )
        angles=[]
        if raw is not None:
            for x1,y1,x2,y2 in np.asarray(raw).reshape(-1,4):
                x1=float(x1); y1=float(y1); x2=float(x2); y2=float(y2)
                if max(y1,y2)<ay+22: continue
                if min(y1,y2)>ay+36: continue
                if point_line_distance(ax,ay,x1,y1,x2,y2)>11: continue
                # angle from apex to lower endpoint, measured from vertical.
                if y1>=y2:
                    lx,ly=x1,y1
                else:
                    lx,ly=x2,y2
                dy=ly-ay
                if dy<18: continue
                ang=math.degrees(math.atan2(lx-ax,dy))
                if abs(ang)>65: continue
                angles.append(ang)
        cl=cluster_angles(angles,sep=7.0)
        counts.append(len(cl))
        angle_sets.append(cl)
    return {
        "apex":[ax,ay],
        "threshold_counts":counts,
        "count":int(round(np.median(counts))) if counts else 0,
        "angle_clusters":angle_sets,
    }

def radial_profile_count(c):
    ax,ay=apex(c)
    h,w=c.shape
    bw=(c<180).astype(np.uint8)
    # Sample candidate base x positions and measure ink occupancy along each ray.
    xs=np.arange(3,w-3,dtype=float)
    yend=min(h-5,ay+0.72*(h-ay))
    scores=[]
    for bx in xs:
        n=max(18,int(yend-ay))
        yy=np.linspace(ay+7,yend,n)
        xx=np.linspace(ax,bx,n)
        xi=np.clip(np.rint(xx).astype(int),0,w-1)
        yi=np.clip(np.rint(yy).astype(int),0,h-1)
        vals=[]
        for off in (-1,0,1):
            vals.append(bw[yi,np.clip(xi+off,0,w-1)])
        score=float(np.mean(np.maximum.reduce(vals)))
        scores.append(score)
    s=np.asarray(scores,float)
    if len(s)<7:
        return {"count":0,"peaks":[],"apex":[ax,ay]}
    # Smooth over ~5 px and find strong local maxima.
    sm=np.convolve(s,np.ones(5)/5.0,mode="same")
    baseline=float(np.median(sm))
    mx=float(np.max(sm))
    cutoff=max(baseline+0.08,0.28*mx)
    peaks=[]
    for i in range(3,len(sm)-3):
        if sm[i]>=cutoff and sm[i]==np.max(sm[i-3:i+4]):
            # local prominence
            left=float(np.min(sm[i-3:i]))
            right=float(np.min(sm[i+1:i+4]))
            if sm[i]-max(left,right)>=0.035:
                if not peaks or i-peaks[-1]>=5:
                    peaks.append(i)
                elif sm[i]>sm[peaks[-1]]:
                    peaks[-1]=i
    return {
        "count":len(peaks),
        "peaks":[float(xs[i]) for i in peaks],
        "apex":[ax,ay],
        "baseline":baseline,
        "max_score":mx,
    }

def eval_crop(c):
    h=hough_count(c)
    r=radial_profile_count(c)
    agree=abs(h["count"]-r["count"])<=1
    consensus=int(round((h["count"]+r["count"])/2)) if agree else None
    return {
        "hough":h,
        "radial":r,
        "agreement":agree,
        "consensus":consensus,
    }

def synthetic(n,w=100,h=120):
    im=np.full((h,w),255,np.uint8)
    ax=w//2; ay=10; base_y=88
    # sail outline
    cv2.line(im,(ax,ay),(14,base_y),0,2,cv2.LINE_AA)
    cv2.line(im,(ax,ay),(86,base_y),0,2,cv2.LINE_AA)
    cv2.line(im,(14,base_y),(86,base_y),0,2,cv2.LINE_AA)
    # n internal spokes, excluding the outline endpoints.
    for bx in np.linspace(22,78,n):
        cv2.line(im,(ax,ay+2),(int(round(bx)),base_y-3),0,2,cv2.LINE_AA)
    return im

def main():
    gray=load_gray()
    vv=variants(gray)
    bb=boxes()
    if len(bb)!=5:
        raise SystemExit(f"expected 5 small-sail boxes, got {len(bb)}")

    controls={}
    controls_pass=True
    for n in (3,4,5,6,7):
        e=eval_crop(synthetic(n))
        # Detector may include outline rays, but the response must be monotonic
        # and estimator agreement must hold. Store actual consensus for calibration.
        controls[str(n)]=e
        controls_pass=controls_pass and e["agreement"] and e["consensus"] is not None

    detected=[controls[str(n)]["consensus"] for n in (3,4,5,6,7)]
    monotonic=bool(all(b>a for a,b in zip(detected,detected[1:]))) if all(x is not None for x in detected) else False
    controls_pass=bool(controls_pass and monotonic)

    sails=[]
    stable=0
    seq=[]
    for i,b in enumerate(bb,1):
        per={name:eval_crop(crop(a,b)) for name,a in vv.items()}
        vals=[per[v]["consensus"] for v in vv]
        ok=bool(
            all(x is not None for x in vals)
            and len(set(vals))==1
            and all(per[v]["agreement"] for v in vv)
        )
        val=int(vals[0]) if ok else None
        if ok: stable+=1
        seq.append(val)
        sails.append({"id":i,"box":list(b),"variants":per,"stable":ok,"count":val})

    distinct=sorted(set(x for x in seq if x is not None))
    promoted=bool(controls_pass and stable>=4 and len(distinct)>=2)

    result={
        "experiment_id":"A11-EXP-105",
        "scope":"internal radial-spoke counts in five fixed small sails; no private-key operations",
        "synthetic_controls":controls,
        "synthetic_detected_consensus":detected,
        "synthetic_monotonic":monotonic,
        "controls_pass":controls_pass,
        "sails":sails,
        "stable_sails":stable,
        "stable_spoke_sequence":seq,
        "distinct_stable_counts":distinct,
        "promotion_rule":"synthetic 3..7-spoke detector response is monotonic with Hough/radial agreement; >=4/5 real sails have same consensus count across original/JPEG85/JPEG70/resize; >=2 distinct counts",
        "promoted":promoted,
        "interpretation_guard":"Promotion establishes only a robust visible spoke-count sequence, not a key mapping.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    seqtxt=" ".join("?" if x is None else str(x) for x in seq)
    md=[
        "# Stage 105 — five-small-sail radial-spoke count audit",
        "",
        "**Experiment:** A11-EXP-105",
        "",
        f"- synthetic controls pass: **{controls_pass}**",
        f"- synthetic detected sequence for drawn 3..7 spokes: **{detected}**",
        f"- stable real sails: **{stable}/5**",
        f"- stable spoke sequence: **{seqtxt}**",
        f"- distinct stable counts: **{distinct}**",
        f"- promoted: **{promoted}**",
        "",
        "| sail | stable count | stable | orig Hough | orig radial |",
        "|---:|---:|:---:|---:|---:|",
    ]
    for r in sails:
        o=r["variants"]["original"]
        md.append(f"| {r['id']} | {'' if r['count'] is None else r['count']} | {r['stable']} | {o['hough']['count']} | {o['radial']['count']} |")
    md += ["","## Interpretation",""]
    if not controls_pass:
        md.append("The synthetic spoke-count controls do not validate the detector. This is an implementation failure and must be fixed under Stage 105.")
    elif promoted:
        md.append("The small sails contain a robust, nontrivial radial-spoke count sequence across two estimators and lossy variants. This visible count family is eligible for a semantic/ordering follow-up.")
    else:
        md.append("Radial-spoke counts are not sufficiently stable/nontrivial across the five small sails. Retire small-sail spoke-count coding.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-105",
        "controls_pass":controls_pass,"stable":stable,
        "sequence":seq,"promoted":promoted
    }))

if __name__=="__main__":
    main()
