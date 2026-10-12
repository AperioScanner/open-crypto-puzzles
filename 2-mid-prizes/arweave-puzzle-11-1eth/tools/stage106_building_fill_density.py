#!/usr/bin/env python3
"""Stage 106: building fill-density bimodality audit.

Safe visual-structure experiment only.

Tests whether the twelve fixed building interiors form a robust sparse/dense
binary sequence independent of the already-known H/V hatch orientation.

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
STAGE12=ROOT/"analysis"/"runs"/"stage12-count-perimeter"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage106-building-fill-density"
OUT.mkdir(parents=True,exist_ok=True)

HV="HHVVHHVHHHHV"
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
    small=Image.fromarray(gray).resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(small.resize((w,h),Image.Resampling.LANCZOS))
    return out

def boxes():
    j=json.loads(STAGE12.read_text())
    rows=[]
    for r in j["regions"]:
        if r["name"].startswith("building_"):
            rows.append((r["name"],tuple(map(int,r["bbox"]))))
    rows.sort()
    if len(rows)!=12:
        raise RuntimeError(f"expected 12 boxes, got {len(rows)}")
    return rows

def crop(a,b):
    x0,y0,x1,y1=b
    return a[y0:y1,x0:x1]

def metric_values(gray,bb):
    dark=[]; ink=[]
    for _,b in bb:
        c=crop(gray,b)
        dark.append(float(np.mean(255.0-c))/255.0)
        ink.append(float(np.mean(c<140)))
    return {"mean_darkness":np.array(dark,float),"ink140":np.array(ink,float)}

def kmeans2(x):
    x=np.asarray(x,float)
    c=np.array([float(np.min(x)),float(np.max(x))])
    for _ in range(50):
        d=np.abs(x[:,None]-c[None,:])
        lab=np.argmin(d,axis=1)
        new=c.copy()
        for j in (0,1):
            if np.any(lab==j):
                new[j]=float(np.mean(x[lab==j]))
        new=np.sort(new)
        if np.max(np.abs(new-c))<1e-10:
            c=new; break
        c=new
    lab=np.argmin(np.abs(x[:,None]-c[None,:]),axis=1)
    # Ensure label 1 = darker/higher metric.
    if c[0]>c[1]:
        c=c[::-1]; lab=1-lab
    sizes=[int(np.sum(lab==j)) for j in (0,1)]
    means=[float(np.mean(x[lab==j])) if sizes[j] else 0.0 for j in (0,1)]
    stds=[float(np.std(x[lab==j],ddof=1)) if sizes[j]>1 else 0.0 for j in (0,1)]
    pooled=math.sqrt(max(1e-12,((sizes[0]-1)*stds[0]**2+(sizes[1]-1)*stds[1]**2)/max(1,sizes[0]+sizes[1]-2)))
    sep=abs(means[1]-means[0])/pooled if pooled>1e-9 else 99.0
    return {
        "labels":lab.astype(int).tolist(),
        "centers":[float(c[0]),float(c[1])],
        "sizes":sizes,
        "separation_pooled_sd":float(sep),
    }

def classify(gray,bb):
    vals=metric_values(gray,bb)
    return {k:{"values":v.tolist(),**kmeans2(v)} for k,v in vals.items()}

def render_building(dense,vertical,size=(80,120)):
    w,h=size
    im=np.full((h,w),255,np.uint8)
    cv2.rectangle(im,(2,2),(w-3,h-3),0,2)
    gap=5 if dense else 12
    if vertical:
        for x in range(8,w-7,gap):
            cv2.line(im,(x,7),(x,h-8),0,2,cv2.LINE_AA)
    else:
        for y in range(8,h-7,gap):
            cv2.line(im,(7,y),(w-8,y),0,2,cv2.LINE_AA)
    return im

def control_variants(patches):
    # apply identical transform family patchwise
    outs={v:[] for v in VARIANTS}
    for p in patches:
        outs["original"].append(p)
        for q in (85,70):
            b=io.BytesIO()
            Image.fromarray(p).save(b,format="JPEG",quality=q)
            b.seek(0)
            outs[f"jpeg{q}"].append(np.array(Image.open(b).convert("L")))
        h,w=p.shape
        sm=Image.fromarray(p).resize((round(w*.75),round(h*.75)),Image.Resampling.LANCZOS)
        outs["down75_up"].append(np.array(sm.resize((w,h),Image.Resampling.LANCZOS)))
    return outs

def classify_patches(patches):
    dark=np.array([float(np.mean(255.0-p))/255.0 for p in patches])
    ink=np.array([float(np.mean(p<140)) for p in patches])
    return {"mean_darkness":kmeans2(dark),"ink140":kmeans2(ink)}

def main():
    gray=load_gray()
    bb=boxes()
    vv=variants(gray)
    real={v:classify(vv[v],bb) for v in VARIANTS}

    # Synthetic control: 6 sparse + 6 dense, orientation alternates independently.
    expected=[0]*6+[1]*6
    patches=[]
    for i in range(12):
        dense=i>=6
        vertical=(i%2==0)
        patches.append(render_building(dense,vertical))
    cv=control_variants(patches)
    controls={}
    controls_pass=True
    for v in VARIANTS:
        c=classify_patches(cv[v])
        controls[v]=c
        for metric in ("mean_darkness","ink140"):
            controls_pass &= (c[metric]["labels"]==expected)
            controls_pass &= (c[metric]["separation_pooled_sd"]>=1.5)

    per_variant={}
    variant_ok=True
    for v in VARIANTS:
        a=real[v]["mean_darkness"]
        b=real[v]["ink140"]
        agree=sum(x==y for x,y in zip(a["labels"],b["labels"]))
        balanced=all(3<=n<=9 for n in a["sizes"]) and all(3<=n<=9 for n in b["sizes"])
        separated=(a["separation_pooled_sd"]>=1.5 and b["separation_pooled_sd"]>=1.5)
        ok=(agree>=10 and balanced and separated)
        per_variant[v]={
            "metric_agreement":agree,
            "balanced":balanced,
            "separated":separated,
            "ok":ok,
        }
        variant_ok &= ok

    # Per-building stability requires both metrics to agree in every variant.
    final=[]
    stable_flags=[]
    for i in range(12):
        labs=[]
        for v in VARIANTS:
            labs.append(real[v]["mean_darkness"]["labels"][i])
            labs.append(real[v]["ink140"]["labels"][i])
        stable=(len(set(labs))==1)
        stable_flags.append(stable)
        final.append(labs[0] if stable else None)

    stable_count=sum(stable_flags)
    hv=[1 if x=="V" else 0 for x in HV]
    known=[x for x in final if x is not None]
    mism=None; inv_mism=None; redundant=False
    if stable_count==12:
        mism=sum(int(a!=b) for a,b in zip(final,hv))
        inv_mism=sum(int(a!=(1-b)) for a,b in zip(final,hv))
        redundant=(min(mism,inv_mism)<=1)

    distinct=set(x for x in final if x is not None)
    promoted=bool(
        controls_pass and variant_ok and stable_count>=10 and len(distinct)==2 and not redundant
    )

    result={
        "experiment_id":"A11-EXP-106",
        "scope":"12-building sparse/dense fill-category stability using mean darkness and ink fraction; no private-key operations",
        "synthetic_controls":controls,
        "controls_pass":bool(controls_pass),
        "real_variants":real,
        "variant_gates":per_variant,
        "stable_buildings":stable_count,
        "stable_density_labels":final,
        "known_hv_sequence":HV,
        "hv_mismatches_if_complete":mism,
        "inverse_hv_mismatches_if_complete":inv_mism,
        "redundant_with_hv":redundant,
        "promotion_rule":"synthetic sparse/dense controls pass; each real variant has >=10/12 metric agreement, balanced 3..9 clusters and >=1.5 pooled-SD separation for both metrics; >=10/12 buildings stable across metrics+variants; two classes present; not nearly identical to H/V or inverse",
        "promoted":promoted,
        "interpretation_guard":"Promotion establishes only a robust independent visible density category sequence, not a secret mapping.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    seq="".join("?" if x is None else ("D" if x else "S") for x in final)
    md=[
        "# Stage 106 — building fill-density bimodality audit",
        "",
        f"- synthetic controls pass: **{bool(controls_pass)}**",
        f"- real variant gates all pass: **{variant_ok}**",
        f"- stable buildings: **{stable_count}/12**",
        f"- density sequence (S=sparse,D=dense): **{seq}**",
        f"- redundant with H/V: **{redundant}**",
        f"- promoted: **{promoted}**",
        "",
        "| variant | metric agreement | balanced | separated | gate |",
        "|:---|---:|:---:|:---:|:---:|",
    ]
    for v,g in per_variant.items():
        md.append(f"| {v} | {g['metric_agreement']}/12 | {g['balanced']} | {g['separated']} | {g['ok']} |")
    md += ["","## Interpretation",""]
    if promoted:
        md.append("The building interiors form a robust sparse/dense sequence independent of the H/V hatch sequence. This is a genuine second visible building channel eligible for semantic follow-up.")
    elif redundant:
        md.append("A stable density split exists but is effectively the same information as H/V orientation, so it is not promoted as a new channel.")
    else:
        md.append("Building fill density does not form a sufficiently stable, well-separated independent binary channel. Retire density coding.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-106",
        "controls_pass":bool(controls_pass),"variant_ok":bool(variant_ok),
        "stable":stable_count,"sequence":seq,"redundant":redundant,"promoted":promoted
    }))

if __name__=="__main__":
    main()
