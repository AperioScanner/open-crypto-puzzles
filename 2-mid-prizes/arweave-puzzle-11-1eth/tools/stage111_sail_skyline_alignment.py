#!/usr/bin/env python3
"""Stage 111: small-sail ↔ skyline vertical-alignment audit.

Safe visual-semantic experiment only.

Tests whether the five right-hand small sailboats align in x with one consecutive
block of five skyline buildings on the same canvas.

No fitted translation or scale is allowed in the target statistic.
No private-key generation, derivation, reconstruction, enumeration,
verification, or wallet access is performed.
"""
from __future__ import annotations

import io, json, math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage111-sail-skyline-alignment"
OUT.mkdir(parents=True,exist_ok=True)

SEARCH=(900,345,1585,500)
THR=165
MIN_SEP=70
N_TRANSLATION=40000
N_SPACING=50000
RNG_SEED=1112026
VARIANTS=("original","jpeg85","jpeg70","down75_up")

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
    band=(gray[y0:y1,x0:x1]<THR).astype(float)
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

def building_centers():
    g=json.loads(GEOM.read_text())
    return np.array([(float(b["x0"])+float(b["x1"]))/2.0 for b in g["buildings"]],float)

def block_rms(sails,buildings,start):
    block=buildings[start:start+5]
    return float(np.sqrt(np.mean((np.asarray(sails,float)-block)**2)))

def best_block(sails,buildings):
    vals=[block_rms(sails,buildings,i) for i in range(8)]
    idx=int(np.argmin(vals))
    return idx,vals[idx],vals

def null_translation(observed,buildings,rng,n):
    x0,_,x1,_=SEARCH
    obs=np.asarray(observed,float)
    pattern=obs-obs[0]
    span=float(pattern[-1])
    hi=x1-span
    vals=np.empty(n,float)
    for i in range(n):
        start=float(rng.uniform(x0,hi))
        rr=pattern+start
        vals[i]=best_block(rr,buildings)[1]
    return vals

def null_spacing(buildings,rng,n):
    x0,_,x1,_=SEARCH
    vals=[]
    while len(vals)<n:
        rr=np.sort(rng.uniform(x0,x1,5))
        if float(np.min(np.diff(rr)))<MIN_SEP:
            continue
        vals.append(best_block(rr,buildings)[1])
    return np.asarray(vals,float)

def p_empirical(null,obs):
    return float((1+np.sum(null<=obs))/(len(null)+1))

def main():
    gray=load_gray()
    vv=variants(gray)
    bc=building_centers()

    centers={name:detect_centers(vv[name]) for name in VARIANTS}
    detector_ok=all(len(x)==5 for x in centers.values())
    if not detector_ok:
        raise SystemExit(f"failed to detect five sails in every variant: {centers}")

    original=np.array(centers["original"],float)
    drift=max(
        float(np.max(np.abs(np.asarray(centers[v],float)-original)))
        for v in VARIANTS
    )

    variant_results={}
    best_blocks=[]
    for v in VARIANTS:
        idx,rms,allr=best_block(centers[v],bc)
        best_blocks.append(idx)
        variant_results[v]={
            "sail_centers":centers[v],
            "best_building_block":[idx+1,idx+5],
            "best_rms":rms,
            "all_block_rms":allr,
        }
    same_block=len(set(best_blocks))==1

    obs_idx,obs_rms,_=best_block(original,bc)
    rng=np.random.default_rng(RNG_SEED)
    nt=null_translation(original,bc,rng,N_TRANSLATION)
    ns=null_spacing(bc,rng,N_SPACING)
    p_trans=p_empirical(nt,obs_rms)
    p_space=p_empirical(ns,obs_rms)

    # Synthetic aligned control: known block 7..11 plus small fixed perturbations.
    ctrl_idx=6
    ctrl=bc[ctrl_idx:ctrl_idx+5]+np.array([-4,3,-2,5,-3],float)
    ci,cr,_=best_block(ctrl,bc)
    control_pass=bool(ci==ctrl_idx and cr<6.0)

    promoted=bool(
        control_pass
        and same_block
        and drift<=8.0
        and p_trans<=0.05
        and p_space<=0.05
    )

    result={
        "experiment_id":"A11-EXP-111",
        "scope":"same-canvas x alignment between five right-hand small sails and all eight consecutive five-building skyline blocks; no fitted target translation/scale and no private-key operations",
        "search_band":list(SEARCH),
        "building_centers":bc.tolist(),
        "variant_results":variant_results,
        "same_best_block_all_variants":same_block,
        "max_sail_center_drift_px":drift,
        "observed_best_block":[obs_idx+1,obs_idx+5],
        "observed_best_rms_px":obs_rms,
        "nulls":{
            "translation_preserving":{
                "n":N_TRANSLATION,
                "p_familywise":p_trans,
                "median_best_rms":float(np.median(nt)),
                "q05_best_rms":float(np.quantile(nt,.05)),
            },
            "spacing_constrained":{
                "n":N_SPACING,
                "minimum_spacing_px":MIN_SEP,
                "p_familywise":p_space,
                "median_best_rms":float(np.median(ns)),
                "q05_best_rms":float(np.quantile(ns,.05)),
            },
        },
        "synthetic_aligned_control":{
            "known_block":[7,11],
            "centers":ctrl.tolist(),
            "recovered_block":[ci+1,ci+5],
            "rms_px":cr,
            "pass":control_pass,
        },
        "promotion_rule":"synthetic aligned control passes; same best consecutive 5-building block across original/JPEG85/JPEG70/resize; max sail-center drift <=8 px; familywise p<=0.05 under both translation-preserving and spacing-constrained nulls",
        "promoted":promoted,
        "interpretation_guard":"Promotion would establish only a visible cross-object correspondence, not a mapping to secret material.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 111 — small-sail ↔ skyline vertical-alignment audit",
        "",
        f"- synthetic aligned control pass: **{control_pass}**",
        f"- original sail centers: **{centers['original']}**",
        f"- best building block: **{obs_idx+1}–{obs_idx+5}**",
        f"- direct alignment RMS: **{obs_rms:.2f} px**",
        f"- same best block across all image variants: **{same_block}**",
        f"- max sail-center drift: **{drift:.1f} px**",
        f"- translation-preserving familywise p: **{p_trans:.5f}**",
        f"- spacing-constrained familywise p: **{p_space:.5f}**",
        f"- promoted: **{promoted}**",
        "",
        "| variant | sail centers | best block | RMS px |",
        "|:---|:---|:---:|---:|",
    ]
    for v in VARIANTS:
        r=variant_results[v]
        md.append(f"| {v} | {r['sail_centers']} | {r['best_building_block'][0]}–{r['best_building_block'][1]} | {r['best_rms']:.2f} |")
    md += ["","## Interpretation",""]
    if promoted:
        md.append("The five small sailboats are unusually and robustly vertically aligned with one consecutive five-building skyline block under both null models. This correspondence is eligible for a semantic selector/order follow-up.")
    else:
        md.append("The apparent sail-to-building alignment is not exceptional under the predeclared familywise nulls and/or is not stable enough across variants. Retire direct vertical correspondence.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-111",
        "block":[obs_idx+1,obs_idx+5],
        "rms":obs_rms,
        "p_translation":p_trans,
        "p_spacing":p_space,
        "drift":drift,
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
