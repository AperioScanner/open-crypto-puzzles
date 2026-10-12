#!/usr/bin/env python3
"""Stage 109: central skyline gap / 5|7 delimiter audit.

Safe visible-structure experiment only.

Tests whether the 12-building skyline contains a robust dominant gap after
building 5, producing a visible 5|7 split.

No private-key generation, derivation, reconstruction, enumeration,
verification, or wallet access is performed.
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
BAND=(240,295)
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
    small=Image.fromarray(gray).resize((round(w*.75),round(h*.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(small.resize((w,h),Image.Resampling.LANCZOS))
    return out

def geometry_gaps():
    g=json.loads(GEOM.read_text())
    b=g["buildings"]
    gaps=[]
    for i in range(len(b)-1):
        x0=int(b[i]["x1"])
        x1=int(b[i+1]["x0"])
        gaps.append({
            "after_building":i+1,
            "x0":x0,
            "x1":x1,
            "width":x1-x0,
            "mid":(x0+x1)/2,
        })
    return gaps

def blank_runs(mask_1d,min_width=2):
    runs=[]
    start=None
    for i,z in enumerate(mask_1d):
        if z and start is None:
            start=i
        if (not z) and start is not None:
            if i-start>=min_width:
                runs.append((start,i,i-start))
            start=None
    if start is not None and len(mask_1d)-start>=min_width:
        runs.append((start,len(mask_1d),len(mask_1d)-start))
    return runs

def detect_gap(gray,thr):
    y0,y1=BAND
    c=gray[y0:y1,:]
    dark=(c<thr).astype(np.uint8)
    # Fill small horizontal holes within building hatching, but preserve the
    # much larger open skyline gap.
    k=cv2.getStructuringElement(cv2.MORPH_RECT,(9,3))
    filled=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,k,iterations=1)
    occ=np.mean(filled,axis=0)
    blank=occ<0.05
    runs=blank_runs(blank,min_width=2)
    # Exclude outer canvas margins; we care only about gaps internal to skyline.
    internal=[r for r in runs if r[0]>200 and r[1]<1595]
    internal.sort(key=lambda r:r[2],reverse=True)
    return internal

def overlap(a0,a1,b0,b1):
    return max(0,min(a1,b1)-max(a0,b0))

def dirichlet_p(observed_fraction,n=11,N=N_NULL,seed=RNG_SEED):
    rng=np.random.default_rng(seed)
    # Uniform Dirichlet over exchangeable gap allocations conditioned on total.
    x=rng.exponential(1.0,size=(N,n))
    x=x/x.sum(axis=1,keepdims=True)
    mx=x.max(axis=1)
    return float((1+np.sum(mx>=observed_fraction))/(N+1))

def main():
    gray=load_gray()
    vv=variants(gray)
    gaps=geometry_gaps()
    widths=[g["width"] for g in gaps]
    order=np.argsort(widths)[::-1]
    top=gaps[int(order[0])]
    second=gaps[int(order[1])]
    ratio=float(top["width"]/max(1,second["width"]))
    total=sum(widths)
    frac=float(top["width"]/total)
    center_dist=float(abs(top["mid"]-gray.shape[1]/2)/gray.shape[1])
    null_p=dirichlet_p(frac)

    rows=[]
    all_overlap=True
    for v,a in vv.items():
        for thr in THRESHOLDS:
            runs=detect_gap(a,thr)
            best=runs[0] if runs else None
            if best is None:
                ok=False
                rec=None
            else:
                x0,x1,w=best
                ov=overlap(x0,x1,top["x0"],top["x1"])
                ok=bool(ov>=0.60*min(w,top["width"]))
                rec={"x0":x0,"x1":x1,"width":w,"overlap_px":ov}
            rows.append({"variant":v,"threshold":thr,"best_gap":rec,"matches_geometry_gap":ok})
            all_overlap &= ok

    promoted=bool(
        top["after_building"]==5
        and ratio>=5.0
        and center_dist<=0.10
        and all_overlap
        and null_p<=0.01
    )

    result={
        "experiment_id":"A11-EXP-109",
        "scope":"robustness and salience of the central inter-building gap producing a 5|7 skyline split; no private-key operations",
        "geometry_gaps":gaps,
        "dominant_geometry_gap":top,
        "second_largest_gap":second,
        "dominant_to_second_ratio":ratio,
        "dominant_fraction_of_total_gap_space":frac,
        "normalized_distance_of_gap_midpoint_from_canvas_center":center_dist,
        "dirichlet_exchangeable_null_p":null_p,
        "detection_rows":rows,
        "all_variant_threshold_detections_match":all_overlap,
        "promotion_rule":"largest geometry gap is after building 5; width >=5x second-largest; midpoint within 10% of canvas center; independent lower-skyline detector overlaps it in all 12 variant×threshold conditions; Dirichlet concentration p<=0.01",
        "promoted":promoted,
        "interpretation_guard":"Promotion establishes only a robust 5|7 visual delimiter, not any numeric or secret-key interpretation.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 109 — central skyline gap / 5|7 delimiter audit",
        "",
        f"- dominant geometry gap after building: **{top['after_building']}**",
        f"- dominant gap width: **{top['width']} px**",
        f"- second-largest gap width: **{second['width']} px**",
        f"- width ratio: **{ratio:.2f}×**",
        f"- dominant share of total inter-building gap: **{frac:.3f}**",
        f"- normalized midpoint distance from canvas center: **{center_dist:.3f}**",
        f"- independent detector matches all 12 conditions: **{all_overlap}**",
        f"- exchangeable-gap null p: **{null_p:.6f}**",
        f"- promoted: **{promoted}**",
        "",
        "## Detection checks",
        "",
        "| variant | threshold | best detected gap | match |",
        "|:---|---:|:---|:---:|",
    ]
    for r in rows:
        md.append(f"| {r['variant']} | {r['threshold']} | {r['best_gap']} | {r['matches_geometry_gap']} |")
    md += ["","## Interpretation",""]
    if promoted:
        md.append("The skyline contains an unusually dominant, near-central and format-invariant gap after building 5, so the 12 buildings are robustly partitioned as 5|7. This promotes the delimiter itself for semantic follow-up; it does not validate any number/key interpretation.")
    else:
        md.append("The apparent 5|7 skyline split is not robust/salient enough under the predeclared tests. Retire it as a coding delimiter.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-109",
        "after":top["after_building"],"ratio":ratio,"center_dist":center_dist,
        "all_overlap":all_overlap,"null_p":null_p,"promoted":promoted
    }))

if __name__=="__main__":
    main()
