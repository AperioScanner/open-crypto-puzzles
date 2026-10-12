#!/usr/bin/env python3
"""Stage 107: adversarial replication + independence audit of building density.

Safe visual-structure experiment only.

Stage 106 promoted a robust 12-building sparse/dense sequence:
DDSSDDSSDSSD

This stage tests whether those labels survive crop/margin perturbations and
quantifies association with the known H/V hatch sequence.

No private-key generation, derivation, reconstruction, enumeration,
verification, or wallet access is performed.
"""
from __future__ import annotations

import io, itertools, json, math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE12=ROOT/"analysis"/"runs"/"stage12-count-perimeter"/"result.json"
STAGE106=ROOT/"analysis"/"runs"/"stage106-building-fill-density"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage107-density-adversarial-replication"
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
        Image.fromarray(gray).save(b,format="JPEG",quality=q,optimize=False,progressive=False)
        b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("L"))
    h,w=gray.shape
    small=Image.fromarray(gray).resize((round(w*.75),round(h*.75)),Image.Resampling.LANCZOS)
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

def perturb_box(b,margin,dx,dy,shape):
    h,w=shape
    x0,y0,x1,y1=b
    x0+=dx; x1+=dx; y0+=dy; y1+=dy
    bw=max(1,x1-x0); bh=max(1,y1-y0)
    mx=int(round(bw*margin)); my=int(round(bh*margin))
    x0+=mx; x1-=mx; y0+=my; y1-=my
    x0=max(0,x0); y0=max(0,y0); x1=min(w,x1); y1=min(h,y1)
    if x1-x0<8 or y1-y0<8:
        raise RuntimeError("perturbed crop too small")
    return x0,y0,x1,y1

def crop(a,b):
    x0,y0,x1,y1=b
    return a[y0:y1,x0:x1]

def metric(c,name):
    if name=="mean_darkness":
        return float(np.mean(255.0-c))/255.0
    if name=="ink140":
        return float(np.mean(c<140))
    if name=="ink160":
        return float(np.mean(c<160))
    raise ValueError(name)

def kmeans2(x):
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
            c=new; break
        c=new
    lab=np.argmin(np.abs(x[:,None]-c[None,:]),axis=1)
    # 1 = higher darkness/ink = dense
    if c[0]>c[1]:
        c=c[::-1]; lab=1-lab
    return lab.astype(int),c

def classify_condition(gray,bb,margin,jitter,metric_name):
    vals=[]
    dx,dy=jitter
    for _,b in bb:
        pb=perturb_box(b,margin,dx,dy,gray.shape)
        vals.append(metric(crop(gray,pb),metric_name))
    lab,centers=kmeans2(vals)
    return lab.tolist(),[float(x) for x in centers],vals

def synthetic_patch(dense,vertical,size=(100,150)):
    w,h=size
    im=np.full((h,w),255,np.uint8)
    # thick outer shell
    im[3:6,3:w-3]=0; im[h-6:h-3,3:w-3]=0
    im[3:h-3,3:6]=0; im[3:h-3,w-6:w-3]=0
    gap=5 if dense else 12
    if vertical:
        for x in range(12,w-11,gap):
            im[10:h-10,max(0,x-1):min(w,x+1)]=0
    else:
        for y in range(12,h-11,gap):
            im[max(0,y-1):min(h,y+1),10:w-10]=0
    return im

def synth_variants(p):
    out={"original":p}
    for q in (85,70):
        b=io.BytesIO()
        Image.fromarray(p).save(b,format="JPEG",quality=q)
        b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("L"))
    h,w=p.shape
    sm=Image.fromarray(p).resize((round(w*.75),round(h*.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(sm.resize((w,h),Image.Resampling.LANCZOS))
    return out

def control_validation():
    expected=[0]*6+[1]*6
    base=[synthetic_patch(i>=6,i%2==0) for i in range(12)]
    sv=[synth_variants(p) for p in base]
    failures=[]
    total=0
    for v in VARIANTS:
        for margin in MARGINS:
            for metric_name in METRICS:
                vals=[]
                for d in sv:
                    p=d[v]
                    h,w=p.shape
                    b=perturb_box((0,0,w,h),margin,0,0,p.shape)
                    vals.append(metric(crop(p,b),metric_name))
                lab,_=kmeans2(vals)
                total+=1
                if lab.tolist()!=expected:
                    failures.append({"variant":v,"margin":margin,"metric":metric_name,"labels":lab.tolist()})
    return {"pass":len(failures)==0,"conditions":total,"failures":failures[:20]}

def phi(a,b):
    a=np.asarray(a,int); b=np.asarray(b,int)
    if a.std()==0 or b.std()==0: return 0.0
    return float(np.corrcoef(a,b)[0,1])

def exact_assoc_p(density,hv):
    obs=abs(phi(density,hv))
    vals=[]
    n=len(density); k=sum(density)
    for comb in itertools.combinations(range(n),k):
        z=np.zeros(n,dtype=int); z[list(comb)]=1
        vals.append(abs(phi(z,hv)))
    p=float(sum(v>=obs-1e-12 for v in vals)/len(vals))
    return obs,p,len(vals)

def main():
    gray=load_gray()
    vv=variants(gray)
    bb=boxes()
    s106=json.loads(STAGE106.read_text())
    ref=list(map(int,s106["stable_density_labels"]))
    if len(ref)!=12:
        raise RuntimeError("Stage106 reference labels missing")

    controls=control_validation()

    total_conditions=0
    match_counts=np.zeros(12,dtype=int)
    hamming=[]
    per_metric={m:[] for m in METRICS}
    condition_rows=[]

    for v in VARIANTS:
        for margin in MARGINS:
            for jitter in JITTERS:
                for m in METRICS:
                    labels,centers,vals=classify_condition(vv[v],bb,margin,jitter,m)
                    total_conditions+=1
                    match=np.array(labels)==np.array(ref)
                    match_counts+=match.astype(int)
                    hd=int(np.sum(~match))
                    hamming.append(hd)
                    per_metric[m].append(hd)
                    condition_rows.append({
                        "variant":v,"margin":margin,"jitter":list(jitter),"metric":m,
                        "hamming_vs_stage106":hd,
                        "cluster_centers":centers,
                    })

    rates=(match_counts/total_conditions).tolist()
    stable90=sum(r>=0.90 for r in rates)
    stable95=sum(r>=0.95 for r in rates)
    median_hamming=float(np.median(hamming))
    max_hamming=int(np.max(hamming))

    hv=[1 if x=="V" else 0 for x in HV]
    obs_phi,assoc_p,perm_n=exact_assoc_p(ref,hv)
    mism=sum(int(a!=b) for a,b in zip(ref,hv))
    inv_mism=sum(int(a!=(1-b)) for a,b in zip(ref,hv))
    redundant=min(mism,inv_mism)<=1

    state=[]
    counts={}
    for h,d in zip(HV,ref):
        s=h+("D" if d else "S")
        state.append(s)
        counts[s]=counts.get(s,0)+1

    promoted=bool(
        controls["pass"]
        and stable90>=10
        and median_hamming<=1
        and not redundant
    )

    if redundant:
        relation="REDUNDANT"
    elif assoc_p<0.05:
        relation="ASSOCIATED_BUT_DISTINCT"
    else:
        relation="STATISTICALLY_INDEPENDENT_AT_THIS_SAMPLE_SIZE"

    result={
        "experiment_id":"A11-EXP-107",
        "scope":"adversarial crop/margin/jitter replication of Stage106 density labels plus exact association audit vs H/V; no private-key operations",
        "stage106_reference_labels":ref,
        "stage106_reference_sequence":"".join("D" if x else "S" for x in ref),
        "controls":controls,
        "conditions_tested":total_conditions,
        "per_building_match_rate":rates,
        "buildings_ge_90pct":stable90,
        "buildings_ge_95pct":stable95,
        "median_condition_hamming_vs_stage106":median_hamming,
        "max_condition_hamming_vs_stage106":max_hamming,
        "per_metric_median_hamming":{k:float(np.median(v)) for k,v in per_metric.items()},
        "hv_sequence":HV,
        "density_vs_hv_abs_phi":obs_phi,
        "density_vs_hv_exact_p":assoc_p,
        "exact_permutations":perm_n,
        "hamming_to_hv":mism,
        "hamming_to_inverse_hv":inv_mism,
        "redundant_with_hv":redundant,
        "relation_to_hv":relation,
        "joint_state_sequence":state if promoted else None,
        "joint_state_counts":counts if promoted else None,
        "condition_summary":condition_rows,
        "promotion_rule":"synthetic perturbation controls pass; >=10/12 buildings reproduce Stage106 label in >=90% of 180 perturbation conditions; median condition Hamming<=1; not within 1 bit of H/V or inverse",
        "promoted":promoted,
        "interpretation_guard":"Promotion validates a second visible building channel only. Joint H/V×density states are not mapped to secret symbols.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    seq="".join("D" if x else "S" for x in ref)
    md=[
        "# Stage 107 — adversarial replication of building density channel",
        "",
        f"- synthetic perturbation controls pass: **{controls['pass']}**",
        f"- perturbation conditions tested: **{total_conditions}**",
        f"- buildings reproducing reference >=90%: **{stable90}/12**",
        f"- buildings reproducing reference >=95%: **{stable95}/12**",
        f"- median condition Hamming distance: **{median_hamming:.1f}**",
        f"- maximum condition Hamming distance: **{max_hamming}**",
        f"- reference density sequence: **{seq}**",
        f"- abs(phi) vs H/V: **{obs_phi:.4f}**",
        f"- exact association p: **{assoc_p:.4f}** ({perm_n} balanced assignments)",
        f"- relation to H/V: **{relation}**",
        f"- promoted: **{promoted}**",
        "",
        "## Per-building robustness",
        "",
        "| building | reference | match rate |",
        "|---:|:---:|---:|",
    ]
    for i,(lab,rate) in enumerate(zip(ref,rates),1):
        md.append(f"| {i} | {'D' if lab else 'S'} | {rate:.3f} |")
    if promoted:
        md += [
            "",
            "## Joint H/V × density states",
            "",
            f"- sequence: **{' '.join(state)}**",
            f"- counts: **{counts}**",
        ]
    md += ["","## Interpretation",""]
    if promoted:
        md.append("The Stage-106 sparse/dense labels survive aggressive crop, margin, metric and lossy perturbations and are not redundant with H/V. Treat fill density as a validated second visible building channel. The next stage may study the four joint visible states, but not map them directly to secret material.")
    else:
        md.append("The apparent Stage-106 density split does not survive adversarial crop/metric perturbations strongly enough, or collapses to the H/V channel. Downgrade/retire it.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-107",
        "controls_pass":controls["pass"],"stable90":stable90,
        "median_hamming":median_hamming,"relation":relation,"promoted":promoted
    }))

if __name__=="__main__":
    main()
