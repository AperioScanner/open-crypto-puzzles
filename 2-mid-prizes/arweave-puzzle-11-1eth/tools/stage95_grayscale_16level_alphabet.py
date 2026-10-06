#!/usr/bin/env python3
"""Stage 95: 16-level grayscale-alphabet audit.

Safe, non-cryptographic mechanism test.

Hypothesis: Puzzle #11 may encode the 64-hex-character key through a visible
16-symbol grayscale alphabet rather than through exact LSBs. This stage tests
only whether a robust 16-level tonal alphabet exists. It never maps tones to
hex digits, emits an ordered symbol sequence, or constructs/verifies a key.

Controls:
- synthetic 16-level line art (positive);
- solved hand-drawn Puzzle #5 image from the public HomelessPhD archive
  converted to grayscale (author-style drawing control).

Target regions are fixed in advance:
- whole foreground
- large sail interior
- skyline/building band
- small-sails/jetty band
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
VARIANT_NAMES=("original","jpeg85","jpeg70","down75_up")
MAX_SAMPLES=120000

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
    skyline=np.zeros(shape,np.uint8); skyline[0:min(330,h),:]=1
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
        # deterministic evenly spaced sample preserves histogram shape
        idx=np.linspace(0,len(vals)-1,MAX_SAMPLES,dtype=int)
        vals=vals[idx]
    return vals

def lattice_metrics(vals):
    if len(vals)<200:
        return {"n":int(len(vals)),"valid":False}
    p1=float(np.percentile(vals,1))
    p99=float(np.percentile(vals,99))
    if p99-p1<15:
        return {"n":int(len(vals)),"valid":False,"p1":p1,"p99":p99}
    z=np.clip((vals-p1)/(p99-p1)*15.0,0,15)
    nearest=np.rint(z)
    resid=np.abs(z-nearest)
    bins=np.bincount(nearest.astype(int),minlength=16).astype(float)
    frac=bins/max(1,bins.sum())
    occupied=int(np.sum(frac>=0.003))
    entropy=float(-np.sum(frac[frac>0]*np.log2(frac[frac>0])))
    return {
        "n":int(len(vals)),
        "valid":True,
        "p1":p1,
        "p99":p99,
        "mean_normalized_lattice_residual":float(resid.mean()),
        "median_normalized_lattice_residual":float(np.median(resid)),
        "sharp_fraction_r008":float(np.mean(resid<=0.08)),
        "sharp_fraction_r012":float(np.mean(resid<=0.12)),
        "occupied_levels_ge_0p3pct":occupied,
        "level_entropy_bits":entropy,
        "level_min_fraction":float(frac.min()),
        "level_max_fraction":float(frac.max()),
    }

def kmeans1d_sse(vals,k):
    if len(vals)<k*10:
        return None
    # deterministic weighted histogram Lloyd k-means
    hist=np.bincount(np.clip(vals.astype(int),0,255),minlength=256).astype(float)
    xs=np.arange(256,dtype=float)
    nz=hist>0
    xs2=xs[nz]; wt=hist[nz]
    lo=float(np.percentile(vals,1)); hi=float(np.percentile(vals,99))
    centers=np.linspace(lo,hi,k)
    for _ in range(50):
        d=np.abs(xs2[:,None]-centers[None,:])
        lab=np.argmin(d,axis=1)
        new=centers.copy()
        for j in range(k):
            m=lab==j
            if np.any(m):
                new[j]=np.sum(xs2[m]*wt[m])/np.sum(wt[m])
        if np.max(np.abs(new-centers))<1e-6:
            centers=new; break
        centers=new
    d=(xs2[:,None]-centers[None,:])**2
    lab=np.argmin(d,axis=1)
    sse=float(np.sum(wt*np.min(d,axis=1))/max(1,np.sum(wt)))
    return sse

def cluster_metrics(vals):
    ss={}
    for k in (15,16,17):
        ss[k]=kmeans1d_sse(vals,k)
    if any(v is None or v<=0 for v in ss.values()):
        return {"valid":False,"sse":ss}
    gain15to16=(ss[15]-ss[16])/ss[15]
    gain16to17=(ss[16]-ss[17])/ss[16]
    elbow=float(gain15to16-gain16to17)
    return {
        "valid":True,
        "sse_per_sample":{"15":ss[15],"16":ss[16],"17":ss[17]},
        "gain_15_to_16":float(gain15to16),
        "gain_16_to_17":float(gain16to17),
        "elbow16":elbow,
    }

def histogram_peak_metrics(vals):
    hist=np.bincount(np.clip(vals.astype(int),0,255),minlength=256).astype(float)
    hist[245:]=0
    sm=cv2.GaussianBlur(hist.reshape(-1,1),(1,0),1.2).ravel()
    mx=max(1.0,float(sm.max()))
    peaks=[]
    for i in range(3,242):
        if sm[i]>sm[i-1] and sm[i]>=sm[i+1] and sm[i]>=0.015*mx:
            # local prominence against +/-3 neighborhood minima
            base=max(float(np.min(sm[i-3:i])),float(np.min(sm[i+1:i+4])))
            prom=(sm[i]-base)/mx
            if prom>=0.004:
                peaks.append((i,float(sm[i]/mx),float(prom)))
    return {
        "significant_peak_count":len(peaks),
        "peak_positions":[p[0] for p in peaks[:40]],
    }

def analyze_values(vals):
    out=lattice_metrics(vals)
    out["clusters"]=cluster_metrics(vals)
    out["histogram_peaks"]=histogram_peak_metrics(vals) if len(vals)>=200 else {"significant_peak_count":0}
    return out

def analyze_target(gray):
    masks=region_masks(gray.shape)
    out={}
    for name,mask in masks.items():
        out[name]=analyze_values(foreground_values(gray,mask))
    return out

def fetch_pzl5():
    r=S.get(PZL5_URL,timeout=30)
    r.raise_for_status()
    return np.array(Image.open(io.BytesIO(r.content)).convert("L")),{
        "url":r.url,"status":r.status_code,"bytes":len(r.content)
    }

def synthetic_control(shape=(800,800)):
    h,w=shape
    im=np.full((h,w),255,np.uint8)
    levels=np.linspace(20,230,16).astype(int)
    # Each tone gets multiple visible line segments and rectangles.
    for i,level in enumerate(levels):
        y=30+i*45
        cv2.line(im,(40,y),(760,y),int(level),5,cv2.LINE_AA)
        cv2.rectangle(im,(60+(i%4)*170,y+8),(150+(i%4)*170,y+30),int(level),-1)
    return im

def score_record(rec):
    if not rec.get("valid"): return None
    cl=rec.get("clusters") or {}
    if not cl.get("valid"): return None
    # Strong 16-level alphabet: many occupied levels, narrow residuals, and an
    # actual elbow at k=16. Score is descriptive and bounded roughly 0..1.
    occ=min(1.0,rec["occupied_levels_ge_0p3pct"]/14.0)
    sharp=min(1.0,rec["sharp_fraction_r008"]/0.55)
    resid=max(0.0,1.0-rec["mean_normalized_lattice_residual"]/0.25)
    elbow=max(0.0,min(1.0,(cl["elbow16"]+0.02)/0.08))
    return float(0.35*sharp+0.30*resid+0.20*occ+0.15*elbow)

def main():
    original=load_gray()
    tv=make_variants(original)
    target={name:analyze_target(a) for name,a in tv.items()}

    pzl5,p5info=fetch_pzl5()
    p5v=make_variants(pzl5)
    sibling={}
    for name,a in p5v.items():
        mask=np.ones(a.shape,np.uint8)
        sibling[name]=analyze_values(foreground_values(a,mask))

    synth=synthetic_control()
    sv=make_variants(synth)
    synthetic={}
    for name,a in sv.items():
        mask=np.ones(a.shape,np.uint8)
        synthetic[name]=analyze_values(foreground_values(a,mask))

    synthetic_scores={k:score_record(v) for k,v in synthetic.items()}
    sibling_scores={k:score_record(v) for k,v in sibling.items()}

    controls_valid=all(
        synthetic_scores[k] is not None and sibling_scores[k] is not None
        and synthetic_scores[k] >= sibling_scores[k] + 0.12
        for k in VARIANT_NAMES
    )

    region_evidence={}
    promoted_regions=[]
    for region in ("whole_foreground","large_sail","skyline","small_sails_jetty"):
        per={}
        relative=[]
        peak_ok=0
        occ_ok=0
        for variant in VARIANT_NAMES:
            rec=target[variant][region]
            ts=score_record(rec)
            ss=synthetic_scores[variant]
            bs=sibling_scores[variant]
            if ts is None or ss is None or bs is None or ss<=bs+1e-9:
                rel=None
            else:
                rel=float((ts-bs)/(ss-bs))
                relative.append(rel)
            peaks=(rec.get("histogram_peaks") or {}).get("significant_peak_count",0)
            if 10<=peaks<=22: peak_ok+=1
            if rec.get("occupied_levels_ge_0p3pct",0)>=12: occ_ok+=1
            per[variant]={
                "target_score":ts,
                "sibling_score":bs,
                "synthetic_score":ss,
                "relative_to_sibling_synthetic":rel,
                "occupied_levels":rec.get("occupied_levels_ge_0p3pct"),
                "peak_count":peaks,
                "mean_lattice_residual":rec.get("mean_normalized_lattice_residual"),
                "sharp_fraction_r008":rec.get("sharp_fraction_r008"),
                "elbow16":(rec.get("clusters") or {}).get("elbow16"),
            }
        median_rel=float(np.median(relative)) if relative else -999.0
        passes=bool(
            controls_valid and len(relative)==4 and
            median_rel>=0.60 and
            sum(x>=0.45 for x in relative)>=3 and
            peak_ok>=3 and occ_ok>=3
        )
        region_evidence[region]={
            "variants":per,
            "median_relative_evidence":median_rel,
            "variants_relative_ge_0p45":sum(x>=0.45 for x in relative),
            "peak_gate_variants":peak_ok,
            "occupancy_gate_variants":occ_ok,
            "promoted":passes,
        }
        if passes: promoted_regions.append(region)

    promoted=bool(promoted_regions)

    result={
        "experiment_id":"A11-EXP-095",
        "scope":"16-level grayscale alphabet structure only; no level-to-symbol mapping, no ordered target sequence, no private-key operations",
        "puzzle5_control_fetch":p5info,
        "controls_valid":controls_valid,
        "synthetic_scores":synthetic_scores,
        "sibling_puzzle5_scores":sibling_scores,
        "target_region_evidence":region_evidence,
        "promoted_regions":promoted_regions,
        "promotion_rule":"synthetic score exceeds Puzzle5 control by >=0.12 in every variant; target region median relative evidence >=0.60 with >=3/4 variants >=0.45; >=3 variants have 12+ occupied levels and 10..22 significant histogram peaks",
        "promoted":promoted,
        "interpretation_guard":"A positive result would establish only a robust 16-level tonal alphabet candidate, not a digit mapping or key.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 95 — 16-level grayscale-alphabet audit",
        "",
        "**Experiment:** A11-EXP-095",
        "",
        f"- synthetic-vs-Puzzle5 control validation: **{controls_valid}**",
        f"- promoted target regions: **{promoted_regions}**",
        f"- promotion rule satisfied: **{promoted}**",
        "",
        "## Control scores",
        "",
        "| variant | synthetic 16-level | Puzzle #5 drawing | delta |",
        "|:---|---:|---:|---:|",
    ]
    for v in VARIANT_NAMES:
        ss=synthetic_scores[v]; bs=sibling_scores[v]
        delta=(ss-bs) if ss is not None and bs is not None else None
        md.append(f"| {v} | {ss if ss is not None else ''} | {bs if bs is not None else ''} | {delta if delta is not None else ''} |")

    md += [
        "",
        "## Target regions",
        "",
        "| region | median relative evidence | variants >=0.45 | peak gate | occupancy gate | promoted |",
        "|:---|---:|---:|---:|---:|:---:|",
    ]
    for name,r in region_evidence.items():
        md.append(f"| {name} | {r['median_relative_evidence']:.3f} | {r['variants_relative_ge_0p45']}/4 | {r['peak_gate_variants']}/4 | {r['occupancy_gate_variants']}/4 | {r['promoted']} |")

    md += ["","## Detailed target metrics",""]
    for region,r in region_evidence.items():
        md.append(f"### {region}")
        md.append("")
        md.append("| variant | target score | relative | occupied | peaks | mean residual | sharp@0.08 | elbow16 |")
        md.append("|:---|---:|---:|---:|---:|---:|---:|---:|")
        for v,z in r["variants"].items():
            rel=z["relative_to_sibling_synthetic"]
            md.append(
                f"| {v} | {z['target_score'] if z['target_score'] is not None else ''} | "
                f"{rel if rel is not None else ''} | {z['occupied_levels']} | {z['peak_count']} | "
                f"{z['mean_lattice_residual']} | {z['sharp_fraction_r008']} | {z['elbow16']} |"
            )
        md.append("")

    md += ["## Interpretation",""]
    if promoted:
        md.append("At least one fixed Puzzle #11 region exhibits a 16-level tonal structure that behaves substantially more like the synthetic 16-shade alphabet than the solved hand-drawn Puzzle #5 control and survives lossy transformations. This promotes tonal-symbol organization for a narrower follow-up, without mapping levels to digits.")
    else:
        md.append("No fixed region satisfies the predeclared 16-level alphabet criteria relative to both synthetic and author-style drawing controls. Retire the direct 16-gray-level symbol-alphabet hypothesis.")
    md += [
        "",
        "No tone-to-hex mapping or ordered target symbol sequence is stored.",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-095",
        "controls_valid":controls_valid,
        "promoted_regions":promoted_regions,
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
