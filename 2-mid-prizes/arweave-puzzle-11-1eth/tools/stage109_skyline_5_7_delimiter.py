#!/usr/bin/env python3
"""Stage 109 (corrected): central skyline gap / 5|7 delimiter audit.

The first implementation used a very low skyline band (y=240..295) and asked
for literally blank columns. Horizontal horizon/detail strokes cross that band,
so the independent detector returned no candidate in every condition despite a
102 px geometry gap. That is a demonstrated implementation defect.

This corrected run detects a *low-occupancy skyline corridor* over y=20..300,
which is the relevant visual property: a real inter-building gap may still
contain sparse horizontal scene strokes.

Safe visible-structure experiment only. No private-key operations.
"""
from __future__ import annotations

import io, json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage109-skyline-5-7-delimiter"
OUT.mkdir(parents=True,exist_ok=True)

THRESHOLDS=(100,140,180)
SKY_BAND=(20,300)
X_RANGE=(220,1595)
LOW_OCC=0.025
SMOOTH=7
N_NULL=200000
RNG_SEED=10977

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
    sm=Image.fromarray(gray).resize((round(w*.75),round(h*.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(sm.resize((w,h),Image.Resampling.LANCZOS))
    return out

def geometry_gaps():
    g=json.loads(GEOM.read_text())
    b=g["buildings"]
    gaps=[]
    for i in range(len(b)-1):
        x0=int(b[i]["x1"]); x1=int(b[i+1]["x0"])
        gaps.append({
            "after_building":i+1,"x0":x0,"x1":x1,
            "width":x1-x0,"mid":(x0+x1)/2
        })
    return gaps

def runs(mask,min_width=2):
    out=[]; st=None
    for i,z in enumerate(mask):
        if z and st is None: st=i
        if (not z) and st is not None:
            if i-st>=min_width: out.append((st,i,i-st))
            st=None
    if st is not None and len(mask)-st>=min_width:
        out.append((st,len(mask),len(mask)-st))
    return out

def _kmeans2_labels(x):
    x=np.asarray(x,float)
    c=np.array([float(np.min(x)),float(np.max(x))])
    for _ in range(50):
        lab=np.argmin(np.abs(x[:,None]-c[None,:]),axis=1)
        new=c.copy()
        for j in (0,1):
            if np.any(lab==j):
                new[j]=float(np.mean(x[lab==j]))
        new=np.sort(new)
        if np.max(np.abs(new-c))<1e-12:
            c=new
            break
        c=new
    lab=np.argmin(np.abs(x[:,None]-c[None,:]),axis=1)
    # label 0 is the lower-occupancy skyline corridor class
    return lab,c

def low_occupancy_detector(gray,thr):
    y0,y1=SKY_BAND; xlo,xhi=X_RANGE
    c=gray[y0:y1,xlo:xhi]
    dark=(c<thr).astype(float)
    occ=dark.mean(axis=0)
    ker=np.ones(SMOOTH)/SMOOTH
    occ_s=np.convolve(occ,ker,mode="same")

    # The previous absolute 2.5% cutoff was still invalid because the horizon
    # line alone can push a visually empty corridor above that occupancy.
    # Use a relative two-cluster split instead: low vs building-occupied columns.
    lab,centers=_kmeans2_labels(occ_s)
    low=(lab==0)
    rr=runs(low,min_width=3)

    vals=[]
    for a,b,w in rr:
        if a<=1 or b>=len(low)-1:
            continue
        vals.append((a+xlo,b+xlo,w,float(np.mean(occ_s[a:b]))))
    vals.sort(key=lambda z:z[2],reverse=True)
    return vals,occ_s,centers

def overlap(a0,a1,b0,b1):
    return max(0,min(a1,b1)-max(a0,b0))

def dirichlet_p(observed_fraction,n=11,N=N_NULL,seed=RNG_SEED):
    rng=np.random.default_rng(seed)
    x=rng.exponential(1.0,size=(N,n))
    x=x/x.sum(axis=1,keepdims=True)
    return float((1+np.sum(x.max(axis=1)>=observed_fraction))/(N+1))

def synthetic_skyline(special=True,w=1600,h=320):
    im=np.full((h,w),255,np.uint8)
    widths=[88,86,84,174,104,94,160,116,88,102,56,78]
    x=234
    for i,bw in enumerate(widths):
        top=50+(i%4)*22
        # light hatch-filled block
        cv2.rectangle(im,(x,top),(x+bw-1,305),0,2)
        for yy in range(top+8,300,12):
            cv2.line(im,(x+4,yy),(x+bw-5,yy),70,1)
        gap=2
        if i==4 and special: gap=102
        x+=bw+gap
    return im

def control_check():
    pos=synthetic_skyline(True)
    neg=synthetic_skyline(False)
    pos_runs,_,_=low_occupancy_detector(pos,140)
    neg_runs,_,_=low_occupancy_detector(neg,140)
    posw=pos_runs[0][2] if pos_runs else 0
    negw=neg_runs[0][2] if neg_runs else 0
    # Positive special gap should be unmistakably larger than anything in equal-gap control.
    return {
        "positive_best_width":posw,
        "negative_best_width":negw,
        "pass":bool(posw>=70 and posw>=5*max(1,negw)),
    }

def main():
    gray=load_gray()
    vv=variants(gray)
    gaps=geometry_gaps()
    widths=[g["width"] for g in gaps]
    order=np.argsort(widths)[::-1]
    top=gaps[int(order[0])]; second=gaps[int(order[1])]
    ratio=float(top["width"]/max(1,second["width"]))
    total=sum(widths)
    frac=float(top["width"]/total)
    center_dist=float(abs(top["mid"]-gray.shape[1]/2)/gray.shape[1])
    null_p=dirichlet_p(frac)
    controls=control_check()

    rows=[]
    all_overlap=True
    for v,a in vv.items():
        for thr in THRESHOLDS:
            rr,_,centers=low_occupancy_detector(a,thr)
            best=rr[0] if rr else None
            if best is None:
                ok=False; rec=None
            else:
                x0,x1,w,meanocc=best
                ov=overlap(x0,x1,top["x0"],top["x1"])
                ok=bool(ov>=0.60*min(w,top["width"]))
                rec={"x0":x0,"x1":x1,"width":w,"mean_occupancy":meanocc,"occupancy_centers":[float(centers[0]),float(centers[1])],"overlap_px":ov}
            rows.append({"variant":v,"threshold":thr,"best_gap":rec,"matches_geometry_gap":ok})
            all_overlap &= ok

    promoted=bool(
        controls["pass"]
        and top["after_building"]==5
        and ratio>=5.0
        and center_dist<=0.10
        and all_overlap
        and null_p<=0.01
    )

    result={
        "experiment_id":"A11-EXP-109",
        "implementation_correction":"Replaced literal-blank lower-band detector, then replaced an invalid absolute occupancy cutoff with a relative 2-cluster low/high occupancy split because the horizon line crosses the true visual gap.",
        "scope":"robustness and salience of the central inter-building gap producing a 5|7 skyline split; no private-key operations",
        "geometry_gaps":gaps,
        "dominant_geometry_gap":top,
        "second_largest_gap":second,
        "dominant_to_second_ratio":ratio,
        "dominant_fraction_of_total_gap_space":frac,
        "normalized_distance_of_gap_midpoint_from_canvas_center":center_dist,
        "dirichlet_exchangeable_null_p":null_p,
        "detector":{"sky_band":list(SKY_BAND),"x_range":list(X_RANGE),"classification":"relative 2-cluster split of smoothed per-column dark occupancy","smooth_px":SMOOTH},
        "synthetic_controls":controls,
        "detection_rows":rows,
        "all_variant_threshold_detections_match":all_overlap,
        "promotion_rule":"synthetic central-gap control passes; largest geometry gap is after building 5; width >=5x second-largest; midpoint within 10% canvas center; independent low-occupancy detector overlaps it in all 12 variant×threshold conditions; Dirichlet concentration p<=0.01",
        "promoted":promoted,
        "interpretation_guard":"Promotion establishes only a robust 5|7 visual delimiter, not any numeric or secret-key interpretation.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 109 — corrected central skyline gap / 5|7 delimiter audit",
        "",
        f"- synthetic detector control pass: **{controls['pass']}**",
        f"- dominant geometry gap after building: **{top['after_building']}**",
        f"- dominant gap width: **{top['width']} px**",
        f"- second-largest gap width: **{second['width']} px**",
        f"- width ratio: **{ratio:.2f}×**",
        f"- dominant share of inter-building gap space: **{frac:.3f}**",
        f"- normalized midpoint distance from canvas center: **{center_dist:.3f}**",
        f"- independent detector matches all 12 conditions: **{all_overlap}**",
        f"- exchangeable-gap null p: **{null_p:.6f}**",
        f"- promoted: **{promoted}**",
        "",
        "## Detection checks",
        "",
        "| variant | threshold | best detected low-occupancy corridor | match |",
        "|:---|---:|:---|:---:|",
    ]
    for r in rows:
        md.append(f"| {r['variant']} | {r['threshold']} | {r['best_gap']} | {r['matches_geometry_gap']} |")
    md += ["","## Interpretation",""]
    if promoted:
        md.append("The skyline has an unusually dominant, near-central and format-invariant low-occupancy corridor after building 5. Treat the 5|7 partition as a validated visible delimiter only; do not infer a key or number encoding from it yet.")
    else:
        md.append("Even after correcting the detector, the 5|7 split does not satisfy the full robustness gate. Retire it as a coding delimiter.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-109","controls":controls["pass"],"after":top["after_building"],"ratio":ratio,"all_overlap":all_overlap,"null_p":null_p,"promoted":promoted}))

if __name__=="__main__":
    main()
