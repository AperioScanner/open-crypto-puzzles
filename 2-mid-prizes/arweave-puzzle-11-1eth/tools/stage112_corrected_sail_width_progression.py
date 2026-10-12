#!/usr/bin/env python3
"""Stage 112: corrected five-sail width-progression replication.

Stage 18 reported widths [27,53,79,83,51], whose first three form +26,+26.
Stage 19 later appeared to refute that result, but Stage 105/111 showed that
Stage 19 tracked the wrong object set (spurious x~675 object, missing x~1490).

This confirmatory stage re-detects the five true right-hand sails and measures
their visible sail widths with two independent estimators.

Safe scope only: no private-key generation, derivation, reconstruction,
enumeration, verification, or wallet access.
"""
from __future__ import annotations

import io, itertools, json, math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage112-corrected-sail-width-progression"
OUT.mkdir(parents=True,exist_ok=True)

SEARCH=(900,345,1585,500)
CENTER_THR=165
MIN_SEP=70
MASK_THRESHOLDS=(120,150,180)
VARIANTS=("original","jpeg85","jpeg70","down75_up")
PRIOR=np.array([27.,53.,79.,83.,51.])
AP_ERR_MAX=4.0
STEP_MIN=18.0
STEP_MAX=34.0

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
    small=Image.fromarray(gray).resize((round(w*.75),round(h*.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(small.resize((w,h),Image.Resampling.LANCZOS))
    return out

def smooth1(x,k=19):
    return np.convolve(x,np.ones(k)/k,mode="same")

def detect_centers(gray):
    x0,y0,x1,y1=SEARCH
    band=(gray[y0:y1,x0:x1]<CENTER_THR).astype(float)
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
    return [int(x) for _,x in sorted(chosen,key=lambda z:z[1])]

def boxes_from_centers(centers,w):
    mids=[(a+b)//2 for a,b in zip(centers[:-1],centers[1:])]
    edges=[max(SEARCH[0],centers[0]-55)]+mids+[min(w,centers[-1]+60)]
    return [(edges[i],SEARCH[1],edges[i+1],SEARCH[3]) for i in range(5)]

def crop(a,b):
    x0,y0,x1,y1=b
    return a[y0:y1,x0:x1]

def apex(c):
    bw=c<185
    h,w=bw.shape
    xa=max(2,int(.06*w)); xb=min(w-2,int(.94*w))
    ys,xs=np.where(bw[:int(.68*h),xa:xb])
    if len(ys)==0:
        return w/2,8.0
    xs=xs+xa
    ymin=int(np.min(ys))
    m=ys<=ymin+9
    return float(np.median(xs[m])),float(ymin+2)

def row_envelope_width(binary,ax,ay):
    h,w=binary.shape
    y0=max(0,int(round(ay+10)))
    y1=min(h,int(round(ay+92)),int(.74*h))
    vals=[]
    for y in range(y0,y1):
        xs=np.flatnonzero(binary[y])
        if len(xs)<4:
            continue
        # Keep only a generous local cone around the detected apex.
        xs=xs[np.abs(xs-ax)<=.48*w]
        if len(xs)<4:
            continue
        lo=float(np.percentile(xs,5))
        hi=float(np.percentile(xs,95))
        span=hi-lo+1
        if span>=5:
            vals.append(span)
    if len(vals)<8:
        return None
    # Near-base width without allowing a single hull/clutter row to dominate.
    return float(np.percentile(vals,90))

def mask_width(c):
    ax,ay=apex(c)
    vals=[]
    for thr in MASK_THRESHOLDS:
        dark=(c<thr).astype(np.uint8)
        dark=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,np.ones((2,2),np.uint8),iterations=1)
        v=row_envelope_width(dark>0,ax,ay)
        if v is not None:
            vals.append(v)
    return float(np.median(vals)) if vals else None

def edge_width(c):
    ax,ay=apex(c)
    e=cv2.Canny(c,45,135)>0
    return row_envelope_width(e,ax,ay)

def measure(c):
    return {"mask":mask_width(c),"edge":edge_width(c)}

def ap_stats(widths):
    w=np.asarray(widths,float)
    d1=float(w[1]-w[0]); d2=float(w[2]-w[1])
    err=float(abs(d2-d1))
    step=float((d1+d2)/2)
    return {"d1":d1,"d2":d2,"error":err,"mean_step":step}

def permutation_p(widths):
    w=np.asarray(widths,float)
    obs=ap_stats(w)["error"]
    errs=[]
    for p in itertools.permutations(w.tolist()):
        errs.append(ap_stats(p)["error"])
    return float(sum(e<=obs+1e-9 for e in errs)/len(errs))

def profile_gate(widths):
    s=ap_stats(widths)
    return bool(
        s["error"]<=AP_ERR_MAX
        and STEP_MIN<=s["mean_step"]<=STEP_MAX
        and s["d1"]>0 and s["d2"]>0
    )

def synthetic_set(widths):
    crops=[]
    for width in widths:
        W,H=120,155
        im=np.full((H,W),255,np.uint8)
        ax=60; ay=12; by=96
        half=width/2
        left=int(round(ax-half)); right=int(round(ax+half))
        cv2.line(im,(ax,ay),(left,by),0,2,cv2.LINE_AA)
        cv2.line(im,(ax,ay),(right,by),0,2,cv2.LINE_AA)
        cv2.line(im,(left,by),(right,by),0,2,cv2.LINE_AA)
        for frac in (.30,.50,.70):
            bx=int(round(left+(right-left)*frac))
            cv2.line(im,(ax,ay+2),(bx,by-2),0,1,cv2.LINE_AA)
        crops.append(im)
    return crops

def eval_synthetic(widths):
    crops=synthetic_set(widths)
    out={}
    for method in ("mask","edge"):
        vals=[]
        for c in crops:
            m=measure(c)[method]
            vals.append(float(m) if m is not None else None)
        ok=all(v is not None for v in vals)
        out[method]={
            "widths":vals,
            "ap":ap_stats(vals) if ok else None,
            "profile_gate":profile_gate(vals) if ok else False,
        }
    return out

def main():
    gray=load_gray()
    vv=variants(gray)

    centers={v:detect_centers(vv[v]) for v in VARIANTS}
    detector_ok=all(len(centers[v])==5 for v in VARIANTS)
    if not detector_ok:
        raise SystemExit(f"five-sail detection failed: {centers}")

    ref=np.array(centers["original"],float)
    drift=max(float(np.max(np.abs(np.array(centers[v],float)-ref))) for v in VARIANTS)

    per_variant={}
    for v in VARIANTS:
        boxes=boxes_from_centers(centers[v],vv[v].shape[1])
        rows=[]
        for b in boxes:
            rows.append(measure(crop(vv[v],b)))
        mask=[r["mask"] for r in rows]
        edge=[r["edge"] for r in rows]
        per_variant[v]={
            "centers":centers[v],
            "boxes":[list(x) for x in boxes],
            "mask_widths":mask,
            "edge_widths":edge,
            "mask_ap":ap_stats(mask) if all(x is not None for x in mask) else None,
            "edge_ap":ap_stats(edge) if all(x is not None for x in edge) else None,
            "mask_gate":all(x is not None for x in mask) and profile_gate(mask),
            "edge_gate":all(x is not None for x in edge) and profile_gate(edge),
        }

    pos=eval_synthetic([27,53,79,83,51])
    neg=eval_synthetic([27,53,70,83,51])
    controls_pass=bool(
        pos["mask"]["profile_gate"] and pos["edge"]["profile_gate"]
        and not neg["mask"]["profile_gate"] and not neg["edge"]["profile_gate"]
    )

    all_real_gates=all(
        per_variant[v]["mask_gate"] and per_variant[v]["edge_gate"]
        for v in VARIANTS
    )

    # Median profiles across variants.
    mask_mat=np.array([per_variant[v]["mask_widths"] for v in VARIANTS],float)
    edge_mat=np.array([per_variant[v]["edge_widths"] for v in VARIANTS],float)
    mask_med=np.median(mask_mat,axis=0)
    edge_med=np.median(edge_mat,axis=0)

    # Cross-method shape agreement: normalize each profile by its first width.
    mn=(mask_med-mask_med[0])
    en=(edge_med-edge_med[0])
    corr=float(np.corrcoef(mn,en)[0,1]) if np.std(mn)>0 and np.std(en)>0 else 0.0

    # Prior-profile agreement is deliberately coarse because the estimators differ.
    # We only require the same qualitative shape: first three increase, sail 4 is
    # near/above sail 3, and sail 5 drops materially from sail 4.
    def qualitative(w):
        return bool(
            w[0]<w[1]<w[2]
            and w[3]>=w[2]-8
            and w[4]<=w[3]-15
        )
    qualitative_pass=bool(qualitative(mask_med) and qualitative(edge_med))

    p_mask=permutation_p(mask_med)
    p_edge=permutation_p(edge_med)

    promoted=bool(
        controls_pass
        and drift<=8
        and all_real_gates
        and qualitative_pass
        and corr>=0.90
        and p_mask<=0.05
        and p_edge<=0.05
    )

    result={
        "experiment_id":"A11-EXP-112",
        "scope":"corrected five true right-hand sail width replication of Stage-18 first-three arithmetic progression; no private-key operations",
        "stage18_prior_widths":PRIOR.tolist(),
        "stage19_defect":"Stage 19 used x~675 as one of five tracks and omitted the true rightmost sail near x~1490; Stage 105/111 corrected the object set.",
        "detected_centers":centers,
        "max_center_drift_px":drift,
        "mask_thresholds":list(MASK_THRESHOLDS),
        "positive_control":pos,
        "negative_control":neg,
        "controls_pass":controls_pass,
        "variants":per_variant,
        "median_mask_widths":mask_med.tolist(),
        "median_edge_widths":edge_med.tolist(),
        "median_mask_ap":ap_stats(mask_med),
        "median_edge_ap":ap_stats(edge_med),
        "permutation_p_mask":p_mask,
        "permutation_p_edge":p_edge,
        "cross_method_profile_correlation":corr,
        "qualitative_stage18_shape_pass":qualitative_pass,
        "all_real_variant_method_gates_pass":all_real_gates,
        "promotion_rule":"positive/negative synthetic controls behave correctly; sail-center drift<=8px; both estimators in all four variants reproduce first-three AP error<=4px with positive mean step 18..34px; median profiles reproduce Stage-18 qualitative shape; cross-method profile correlation>=0.90; both fixed-order permutation p<=0.05",
        "promoted":promoted,
        "interpretation_guard":"Promotion confirms only a robust visual width progression. No modulo-26, alphabet, key, or secret interpretation is made here.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 112 — corrected five-sail width-progression replication",
        "",
        f"- five-sail detector stable: **{detector_ok}**",
        f"- max center drift: **{drift:.1f} px**",
        f"- centers original: **{centers['original']}**",
        f"- synthetic controls pass: **{controls_pass}**",
        f"- median mask widths: **{[round(x,2) for x in mask_med]}**",
        f"- median edge widths: **{[round(x,2) for x in edge_med]}**",
        f"- mask first-three AP: **{ap_stats(mask_med)}**",
        f"- edge first-three AP: **{ap_stats(edge_med)}**",
        f"- permutation p (mask/edge): **{p_mask:.5f} / {p_edge:.5f}**",
        f"- cross-method profile correlation: **{corr:.3f}**",
        f"- Stage-18 qualitative profile reproduced: **{qualitative_pass}**",
        f"- all real variant/method AP gates pass: **{all_real_gates}**",
        f"- promoted: **{promoted}**",
        "",
        "| variant | mask widths | mask AP err | edge widths | edge AP err |",
        "|:---|:---|---:|:---|---:|",
    ]
    for v in VARIANTS:
        r=per_variant[v]
        me=r["mask_ap"]["error"] if r["mask_ap"] else float("nan")
        ee=r["edge_ap"]["error"] if r["edge_ap"] else float("nan")
        md.append(
            f"| {v} | {[round(x,1) if x is not None else None for x in r['mask_widths']]} | "
            f"{me:.2f} | {[round(x,1) if x is not None else None for x in r['edge_widths']]} | {ee:.2f} |"
        )

    md += ["","## Interpretation",""]
    if promoted:
        md.append("The corrected true five-sail object set independently reproduces Stage 18's first-three arithmetic width progression across two estimators and lossy variants. The progression is restored as a real visual lead; its meaning remains unresolved.")
    else:
        md.append("The corrected true five-sail measurement does not robustly reproduce Stage 18's arithmetic progression under the confirmatory gates. Retire the +26/+26 sail-width lead.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-112",
        "controls_pass":controls_pass,
        "centers":centers["original"],
        "mask_med":mask_med.tolist(),
        "edge_med":edge_med.tolist(),
        "p_mask":p_mask,"p_edge":p_edge,
        "promoted":promoted
    }))

if __name__=="__main__":
    main()
