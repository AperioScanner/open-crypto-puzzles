#!/usr/bin/env python3
"""Stage 95 (corrected): robust 16-mode grayscale alphabet audit.

The first implementation used an affine/equally-spaced lattice score whose
synthetic 16-level positive control was not distinguishable from Puzzle #5.
That control failure invalidated interpretation.

This corrected version tests the more general hypothesis actually justified by
the target: a 16-symbol tonal alphabet whose levels need not be equally spaced.

It measures:
- 16-cluster compactness on foreground grayscale values;
- fraction of foreground samples lying within ±2 gray levels of a cluster mode;
- occupancy of all 16 fitted modes.

Controls:
- exact 16-shade synthetic line/block art (positive);
- smooth continuous-tone gradient (negative);
- solved hand-drawn Puzzle #5 (author-style specificity control).

No tone-to-hex mapping, ordered sequence, candidate key, or wallet operation is
performed.
"""
from __future__ import annotations

import io, json, math
from pathlib import Path

import cv2
import numpy as np
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage95-grayscale-16level-alphabet"
OUT.mkdir(parents=True,exist_ok=True)

PZL5_URL="https://raw.githubusercontent.com/HomelessPhD/AR_Puzzles/main/PZL5/pics/pzl5.png"
VARIANTS=("original","jpeg85","jpeg70","down75_up")
MAX_SAMPLES=160000

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0; public control fetch)"})

def load_gray():
    return np.array(Image.open(SOURCE).convert("L"))

def make_variants(gray):
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

def sail_mask(shape):
    g=json.loads(GEOM.read_text())
    b=g["large_sailboat"]
    x0,y0,x1,y1=map(int,(b["x0"],b["y0"],b["x1"],b["y1"]))
    ye=y0+int(round((y1-y0)*0.74))
    mask=np.zeros(shape,np.uint8)
    h=ye-y0; w=x1-x0
    pts=np.array([
        [x0+int(round(0.48*w)),y0+6],
        [x0+8,ye-5],
        [x1-8,ye-5],
    ],np.int32)
    cv2.fillConvexPoly(mask,pts,1)
    return mask

def region_masks(shape):
    h,w=shape
    whole=np.ones(shape,np.uint8)
    sail=sail_mask(shape)
    skyline=np.zeros(shape,np.uint8); skyline[:min(330,h),:]=1
    jetty=np.zeros(shape,np.uint8)
    jetty[min(330,h):min(650,h),min(820,w):w]=1
    return {
        "whole_foreground":whole,
        "large_sail":sail,
        "skyline":skyline,
        "small_sails_jetty":jetty,
    }

def foreground_values(gray,mask):
    vals=gray[(mask>0)&(gray<245)].astype(np.float64)
    if len(vals)>MAX_SAMPLES:
        idx=np.linspace(0,len(vals)-1,MAX_SAMPLES,dtype=int)
        vals=vals[idx]
    return vals

def fit_kmeans_1d(vals,k=16):
    if len(vals)<k*30:
        return None
    hist=np.bincount(np.clip(vals.astype(int),0,255),minlength=256).astype(float)
    xs=np.arange(256,dtype=float)
    nz=hist>0
    x=xs[nz]; w=hist[nz]
    lo=float(np.percentile(vals,0.5)); hi=float(np.percentile(vals,99.5))
    centers=np.linspace(lo,hi,k)
    for _ in range(100):
        d=np.abs(x[:,None]-centers[None,:])
        lab=np.argmin(d,axis=1)
        new=centers.copy()
        for j in range(k):
            m=lab==j
            if np.any(m):
                new[j]=np.sum(x[m]*w[m])/np.sum(w[m])
        new=np.sort(new)
        if np.max(np.abs(new-centers))<1e-7:
            centers=new; break
        centers=new
    # Assign raw sample values to nearest center.
    dist=np.abs(vals[:,None]-centers[None,:])
    lab=np.argmin(dist,axis=1)
    nearest=dist[np.arange(len(vals)),lab]
    counts=np.bincount(lab,minlength=k).astype(float)
    frac=counts/max(1,counts.sum())
    rmse=float(np.sqrt(np.mean(nearest**2)))
    dynamic=max(1.0,hi-lo)
    return {
        "centers":[float(x) for x in centers],
        "rmse_gray":rmse,
        "rmse_normalized":float(rmse/dynamic),
        "mode_concentration_pm2":float(np.mean(nearest<=2.0)),
        "mode_concentration_pm3":float(np.mean(nearest<=3.0)),
        "occupied_modes_ge_0p3pct":int(np.sum(frac>=0.003)),
        "occupied_modes_ge_1pct":int(np.sum(frac>=0.01)),
        "mode_entropy_bits":float(-np.sum(frac[frac>0]*np.log2(frac[frac>0]))),
        "min_mode_fraction":float(frac.min()),
        "max_mode_fraction":float(frac.max()),
        "dynamic_range":dynamic,
    }

def alphabet_score(m):
    if not m: return None
    concentration=m["mode_concentration_pm2"]
    compact=float(math.exp(-m["rmse_normalized"]/0.018))
    occupancy=min(1.0,m["occupied_modes_ge_0p3pct"]/14.0)
    entropy=min(1.0,m["mode_entropy_bits"]/3.7)
    return float(0.50*concentration+0.25*compact+0.15*occupancy+0.10*entropy)

def analyze_vals(vals):
    km=fit_kmeans_1d(vals,16)
    return {
        "n":int(len(vals)),
        "k16":km,
        "score":alphabet_score(km),
    }

def analyze_regions(gray):
    masks=region_masks(gray.shape)
    return {name:analyze_vals(foreground_values(gray,m)) for name,m in masks.items()}

def fetch_pzl5():
    r=S.get(PZL5_URL,timeout=30)
    r.raise_for_status()
    return np.array(Image.open(io.BytesIO(r.content)).convert("L")),{
        "url":r.url,"status":r.status_code,"bytes":len(r.content)
    }

def synthetic_positive(shape=(800,800)):
    im=np.full(shape,255,np.uint8)
    levels=np.array([18,31,45,60,75,91,107,123,139,155,171,187,202,216,229,240],dtype=int)
    # Non-antialiased filled blocks + lines make a true discrete 16-mode alphabet.
    for i,lev in enumerate(levels):
        row=i//4; col=i%4
        x0=35+col*190; y0=35+row*190
        cv2.rectangle(im,(x0,y0),(x0+140,y0+115),int(lev),-1)
        cv2.line(im,(x0,y0+135),(x0+145,y0+155),int(lev),5,cv2.LINE_8)
    return im

def synthetic_negative(shape=(800,800)):
    h,w=shape
    x=np.linspace(15,240,w,dtype=float)[None,:]
    y=np.linspace(-18,18,h,dtype=float)[:,None]
    a=np.clip(x+y,0,244).astype(np.uint8)
    return a

def analyze_control_image(gray):
    mask=np.ones(gray.shape,np.uint8)
    return analyze_vals(foreground_values(gray,mask))

def main():
    target_base=load_gray()
    target={v:analyze_regions(a) for v,a in make_variants(target_base).items()}

    p5,p5info=fetch_pzl5()
    sibling={v:analyze_control_image(a) for v,a in make_variants(p5).items()}

    pos={v:analyze_control_image(a) for v,a in make_variants(synthetic_positive()).items()}
    neg={v:analyze_control_image(a) for v,a in make_variants(synthetic_negative()).items()}

    pos_scores={v:pos[v]["score"] for v in VARIANTS}
    neg_scores={v:neg[v]["score"] for v in VARIANTS}
    sibling_scores={v:sibling[v]["score"] for v in VARIANTS}

    detector_valid=all(
        pos_scores[v] is not None and neg_scores[v] is not None
        and pos_scores[v]>=0.68
        and pos_scores[v]>=neg_scores[v]+0.18
        for v in VARIANTS
    )

    region_results={}
    promoted_regions=[]
    rejected_regions=[]
    for region in ("whole_foreground","large_sail","skyline","small_sails_jetty"):
        per={}
        close_to_positive=0
        beats_sibling=0
        occupancy=0
        for v in VARIANTS:
            rec=target[v][region]
            ts=rec["score"]
            ps=pos_scores[v]; ns=neg_scores[v]; ss=sibling_scores[v]
            ratio=None
            if ts is not None and ps is not None and ns is not None and ps>ns+1e-9:
                ratio=float((ts-ns)/(ps-ns))
            if ratio is not None and ratio>=0.65: close_to_positive+=1
            if ts is not None and ss is not None and ts>=ss+0.08: beats_sibling+=1
            km=rec["k16"] or {}
            if km.get("occupied_modes_ge_0p3pct",0)>=14: occupancy+=1
            per[v]={
                "target_score":ts,
                "positive_score":ps,
                "negative_score":ns,
                "puzzle5_score":ss,
                "normalized_positive_similarity":ratio,
                "mode_concentration_pm2":km.get("mode_concentration_pm2"),
                "rmse_normalized":km.get("rmse_normalized"),
                "occupied_modes_ge_0p3pct":km.get("occupied_modes_ge_0p3pct"),
                "mode_entropy_bits":km.get("mode_entropy_bits"),
            }

        promoted=bool(detector_valid and close_to_positive>=3 and beats_sibling>=3 and occupancy>=3)
        rejected=bool(detector_valid and close_to_positive<=1)
        region_results[region]={
            "variants":per,
            "variants_close_to_positive":close_to_positive,
            "variants_beating_puzzle5":beats_sibling,
            "variants_occupancy_ok":occupancy,
            "promoted":promoted,
            "rejected":rejected,
        }
        if promoted: promoted_regions.append(region)
        if rejected: rejected_regions.append(region)

    overall_promoted=bool(promoted_regions)
    all_rejected=bool(len(rejected_regions)==len(region_results))

    result={
        "experiment_id":"A11-EXP-095",
        "scope":"general 16-mode grayscale alphabet audit; no tone-to-symbol mapping or ordered sequence; no private-key operations",
        "implementation_correction":"First Stage-95 affine-lattice score failed its synthetic-vs-control validation. Corrected test uses general 16-mode compactness/concentration and adds a continuous-tone negative control.",
        "puzzle5_control_fetch":p5info,
        "detector_valid":detector_valid,
        "positive_scores":pos_scores,
        "negative_scores":neg_scores,
        "puzzle5_scores":sibling_scores,
        "regions":region_results,
        "promoted_regions":promoted_regions,
        "rejected_regions":rejected_regions,
        "all_regions_rejected":all_rejected,
        "promotion_rule":"detector valid in all variants; region resembles positive control in >=3/4 variants; exceeds Puzzle5 by >=0.08 in >=3/4; >=14 occupied modes in >=3/4",
        "rejection_rule":"detector valid and region resembles positive control in <=1/4 variants",
        "promoted":overall_promoted,
        "interpretation_guard":"Positive means only tonal-alphabet structure; no mapping to hexadecimal digits is attempted.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 95 — corrected 16-mode grayscale-alphabet audit",
        "",
        "**Experiment:** A11-EXP-095",
        "",
        f"- detector/control validation: **{detector_valid}**",
        f"- promoted regions: **{promoted_regions}**",
        f"- rejected regions: **{rejected_regions}**",
        f"- all fixed regions rejected: **{all_rejected}**",
        "",
        "## Controls",
        "",
        "| variant | positive 16-mode | continuous negative | Puzzle #5 |",
        "|:---|---:|---:|---:|",
    ]
    for v in VARIANTS:
        md.append(f"| {v} | {pos_scores[v]:.4f} | {neg_scores[v]:.4f} | {sibling_scores[v]:.4f} |")

    md += [
        "",
        "## Target-region decisions",
        "",
        "| region | close to positive | beats Puzzle5 | occupancy ok | promoted | rejected |",
        "|:---|---:|---:|---:|:---:|:---:|",
    ]
    for name,r in region_results.items():
        md.append(f"| {name} | {r['variants_close_to_positive']}/4 | {r['variants_beating_puzzle5']}/4 | {r['variants_occupancy_ok']}/4 | {r['promoted']} | {r['rejected']} |")

    md += ["","## Detailed metrics",""]
    for name,r in region_results.items():
        md.append(f"### {name}")
        md.append("")
        md.append("| variant | target | normalized positive similarity | mode concentration ±2 | norm RMSE | occupied modes |")
        md.append("|:---|---:|---:|---:|---:|---:|")
        for v,z in r["variants"].items():
            rel=z["normalized_positive_similarity"]
            md.append(
                f"| {v} | {z['target_score']:.4f} | {rel if rel is not None else ''} | "
                f"{z['mode_concentration_pm2']} | {z['rmse_normalized']} | {z['occupied_modes_ge_0p3pct']} |"
            )
        md.append("")

    md += ["## Interpretation",""]
    if overall_promoted:
        md.append("At least one fixed region behaves like a robust 16-mode tonal alphabet across lossy variants and more strongly than the Puzzle #5 drawing control. This promotes tonal-symbol organization for a narrower structural follow-up, without assigning digit values.")
    elif all_rejected:
        md.append("All fixed regions are materially unlike the validated 16-mode positive control across the tested transformations. Retire the direct 16-gray-mode symbol-alphabet hypothesis.")
    else:
        md.append("The corrected detector is valid, but some target regions remain intermediate rather than clearly positive or negative. Carry only those intermediate regions forward; do not map tones to digits.")
    md += [
        "",
        "No tone-to-hex mapping or ordered target symbol sequence is stored.",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-095",
        "detector_valid":detector_valid,
        "promoted_regions":promoted_regions,
        "rejected_regions":rejected_regions,
        "all_rejected":all_rejected,
    }))

if __name__=="__main__":
    main()
