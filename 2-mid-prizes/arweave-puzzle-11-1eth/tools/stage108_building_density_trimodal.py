#!/usr/bin/env python3
"""Stage 108: three-level building-density audit.

Tests whether the 12 buildings are better described by a robust light/medium/dark
visible-density channel than by the unstable binary split from Stage 106/107.

Safe structural analysis only. No private-key operations.
"""
from __future__ import annotations
import io, json, math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE12=ROOT/"analysis"/"runs"/"stage12-count-perimeter"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage108-building-density-trimodal"
OUT.mkdir(parents=True,exist_ok=True)

VARIANTS=("original","jpeg85","jpeg70","down75_up")
MARGINS=(0.08,0.14,0.20)
JITTERS=((0,0),(-4,0),(4,0),(0,-4),(0,4))
METRICS=("mean_darkness","ink140","ink160")
HV="HHVVHHVHHHHV"

def load_gray():
    return np.array(Image.open(SOURCE).convert("L"))

def variants(gray):
    out={"original":gray}
    for q in (85,70):
        b=io.BytesIO()
        Image.fromarray(gray).save(b,format="JPEG",quality=q)
        b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("L"))
    h,w=gray.shape
    sm=Image.fromarray(gray).resize((round(w*.75),round(h*.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(sm.resize((w,h),Image.Resampling.LANCZOS))
    return out

def boxes():
    j=json.loads(STAGE12.read_text())
    rows=[]
    for r in j["regions"]:
        if r["name"].startswith("building_"):
            rows.append((r["name"],tuple(map(int,r["bbox"]))))
    rows.sort()
    if len(rows)!=12: raise RuntimeError("expected 12 building boxes")
    return rows

def perturb_box(b,margin,dx,dy,shape):
    h,w=shape
    x0,y0,x1,y1=b
    x0+=dx; x1+=dx; y0+=dy; y1+=dy
    bw=x1-x0; bh=y1-y0
    mx=int(round(bw*margin)); my=int(round(bh*margin))
    return (max(0,x0+mx),max(0,y0+my),min(w,x1-mx),min(h,y1-my))

def crop(a,b):
    x0,y0,x1,y1=b
    return a[y0:y1,x0:x1]

def metric(c,name):
    if name=="mean_darkness": return float(np.mean(255.0-c))/255.0
    if name=="ink140": return float(np.mean(c<140))
    if name=="ink160": return float(np.mean(c<160))
    raise ValueError(name)

def kmeans1d(x,k):
    x=np.asarray(x,float)
    qs=np.linspace(0,1,k+2)[1:-1]
    c=np.quantile(x,qs)
    for _ in range(100):
        lab=np.argmin(np.abs(x[:,None]-c[None,:]),axis=1)
        new=c.copy()
        for j in range(k):
            if np.any(lab==j): new[j]=np.mean(x[lab==j])
        new=np.sort(new)
        if np.max(np.abs(new-c))<1e-12:
            c=new; break
        c=new
    lab=np.argmin(np.abs(x[:,None]-c[None,:]),axis=1)
    return lab.astype(int),np.asarray(c,float)

def silhouette1d(x,lab):
    x=np.asarray(x,float); lab=np.asarray(lab,int)
    vals=[]
    for i in range(len(x)):
        same=np.where(lab==lab[i])[0]
        same=same[same!=i]
        a=np.mean(np.abs(x[i]-x[same])) if len(same) else 0.0
        b=1e9
        for g in sorted(set(lab.tolist())):
            if g==lab[i]: continue
            inds=np.where(lab==g)[0]
            if len(inds): b=min(b,float(np.mean(np.abs(x[i]-x[inds]))))
        if b==1e9: vals.append(0.0)
        else: vals.append((b-a)/max(a,b,1e-12))
    return float(np.mean(vals))

def bic_like(x,lab,centers):
    x=np.asarray(x,float); lab=np.asarray(lab,int)
    rss=float(np.sum((x-centers[lab])**2))
    n=len(x); k=len(centers)
    var=max(rss/n,1e-12)
    return float(n*np.log(var)+k*np.log(n))

def classify_condition(gray,bb,margin,jitter,mname,k):
    dx,dy=jitter
    vals=[]
    for _,b in bb:
        pb=perturb_box(b,margin,dx,dy,gray.shape)
        vals.append(metric(crop(gray,pb),mname))
    lab,c=kmeans1d(vals,k)
    return {
        "labels":lab.tolist(),
        "centers":c.tolist(),
        "silhouette":silhouette1d(vals,lab),
        "bic_like":bic_like(vals,lab,c),
        "values":vals,
    }

def synth_patch(level,vertical,size=(100,150)):
    # level: 0 light, 1 medium, 2 dark
    w,h=size
    im=np.full((h,w),255,np.uint8)
    im[3:6,3:w-3]=0; im[h-6:h-3,3:w-3]=0
    im[3:h-3,3:6]=0; im[3:h-3,w-6:w-3]=0
    gap=(14,8,4)[level]
    if vertical:
        for x in range(12,w-11,gap): im[10:h-10,max(0,x-1):min(w,x+1)]=0
    else:
        for y in range(12,h-11,gap): im[max(0,y-1):min(h,y+1),10:w-10]=0
    return im

def synth_variants(p):
    out={"original":p}
    for q in (85,70):
        b=io.BytesIO(); Image.fromarray(p).save(b,format="JPEG",quality=q); b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("L"))
    h,w=p.shape
    sm=Image.fromarray(p).resize((round(w*.75),round(h*.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(sm.resize((w,h),Image.Resampling.LANCZOS))
    return out

def validate_controls():
    expected=[0]*4+[1]*4+[2]*4
    base=[synth_patch(i//4,i%2==0) for i in range(12)]
    sv=[synth_variants(x) for x in base]
    failures=[]; total=0
    for v in VARIANTS:
        for m in MARGINS:
            for metric_name in METRICS:
                vals=[]
                for d in sv:
                    p=d[v]; h,w=p.shape
                    b=perturb_box((0,0,w,h),m,0,0,p.shape)
                    vals.append(metric(crop(p,b),metric_name))
                lab,c=kmeans1d(vals,3)
                total+=1
                if lab.tolist()!=expected:
                    failures.append({"variant":v,"margin":m,"metric":metric_name,"labels":lab.tolist()})
    return {"pass":len(failures)==0,"conditions":total,"failures":failures[:10]}

def main():
    gray=load_gray(); vv=variants(gray); bb=boxes()
    controls=validate_controls()

    conditions=[]
    label_votes=np.zeros((12,3),int)
    better3=0
    total=0
    for v in VARIANTS:
        for m in MARGINS:
            for j in JITTERS:
                for met in METRICS:
                    r2=classify_condition(vv[v],bb,m,j,met,2)
                    r3=classify_condition(vv[v],bb,m,j,met,3)
                    total+=1
                    for i,lab in enumerate(r3["labels"]): label_votes[i,lab]+=1
                    # require silhouette gain OR BIC-like improvement
                    better=(r3["silhouette"]>=r2["silhouette"]+0.05) or (r3["bic_like"]<=r2["bic_like"]-2.0)
                    better3+=int(better)
                    conditions.append({
                        "variant":v,"margin":m,"jitter":list(j),"metric":met,
                        "k2_sil":r2["silhouette"],"k3_sil":r3["silhouette"],
                        "k2_bic":r2["bic_like"],"k3_bic":r3["bic_like"],
                        "k3_labels":r3["labels"],"k3_better":better
                    })

    dominant=np.argmax(label_votes,axis=1)
    rates=np.max(label_votes,axis=1)/total
    stable90=int(np.sum(rates>=0.90))
    counts=[int(np.sum(dominant==k)) for k in range(3)]
    all_classes=all(c>=2 for c in counts)
    better_frac=better3/total

    hv=np.array([1 if x=="V" else 0 for x in HV])
    # test whether any one density class just copies H/V membership
    hv_redundant=False
    for k in range(3):
        z=(dominant==k).astype(int)
        mism=min(int(np.sum(z!=hv)),int(np.sum((1-z)!=hv)))
        if mism<=1: hv_redundant=True

    promoted=bool(
        controls["pass"] and stable90>=10 and all_classes
        and better_frac>=0.70 and not hv_redundant
    )

    names=("L","M","D")
    seq="".join(names[int(x)] for x in dominant)

    result={
        "experiment_id":"A11-EXP-108",
        "scope":"three-level light/medium/dark building density audit under 180 perturbation conditions; no private-key operations",
        "controls":controls,
        "conditions_tested":total,
        "k3_better_conditions":better3,
        "k3_better_fraction":better_frac,
        "dominant_labels":dominant.astype(int).tolist(),
        "dominant_sequence":seq,
        "per_building_match_rate":rates.tolist(),
        "buildings_ge_90pct":stable90,
        "class_counts":{"L":counts[0],"M":counts[1],"D":counts[2]},
        "all_classes_ge2":all_classes,
        "redundant_with_hv":hv_redundant,
        "promoted":promoted,
        "promotion_rule":"synthetic L/M/D controls pass; >=10/12 buildings have same k3 label in >=90% of 180 conditions; each class has >=2 members; k3 materially beats k2 in >=70% conditions; no density class is within 1 bit of H/V or inverse",
        "condition_summary":conditions,
        "interpretation_guard":"Promotion establishes only a robust three-level visible density channel, not a symbol/key mapping."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 108 — three-level building density audit","",
        f"- synthetic controls pass: **{controls['pass']}**",
        f"- k=3 better than k=2: **{better3}/{total} = {better_frac:.3f}**",
        f"- buildings stable >=90%: **{stable90}/12**",
        f"- sequence: **{seq}**",
        f"- class counts: **L={counts[0]}, M={counts[1]}, D={counts[2]}**",
        f"- redundant with H/V: **{hv_redundant}**",
        f"- promoted: **{promoted}**","",
        "| building | class | stability |",
        "|---:|:---:|---:|",
    ]
    for i,(lab,rate) in enumerate(zip(dominant,rates),1):
        md.append(f"| {i} | {names[int(lab)]} | {rate:.3f} |")
    md += ["","## Interpretation",""]
    if promoted:
        md.append("The binary failure resolves into a robust light/medium/dark three-level density channel. This is a stronger model than k=2 across most perturbations and is not reducible to H/V.")
    else:
        md.append("The tri-modal explanation does not satisfy the adversarial stability/model-comparison gates. Retire density coding rather than forcing a categorical interpretation.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-108","controls_pass":controls["pass"],"stable90":stable90,"better_frac":better_frac,"sequence":seq,"promoted":promoted}))

if __name__=="__main__":
    main()
