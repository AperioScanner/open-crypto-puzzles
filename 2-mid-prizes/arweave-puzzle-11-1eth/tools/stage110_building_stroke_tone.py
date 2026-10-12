#!/usr/bin/env python3
"""Stage 110: building stroke-tone / pencil-pressure audit.

Safe visual-structure experiment only.

Tests whether the twelve fixed building interiors use stable discrete classes of
stroke darkness, independent of hatch orientation and fill amount.

No private-key generation, derivation, reconstruction, enumeration,
verification, or wallet access is performed.
"""
from __future__ import annotations

import io, itertools, json, math
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE12=ROOT/"analysis"/"runs"/"stage12-count-perimeter"/"result.json"
STAGE106=ROOT/"analysis"/"runs"/"stage106-building-fill-density"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage110-building-stroke-tone"
OUT.mkdir(parents=True,exist_ok=True)

VARIANTS=("original","jpeg85","jpeg70","down75_up")
MARGINS=(0.08,0.14,0.20)
JITTERS=((0,0),(-4,0),(4,0),(0,-4),(0,4))
METRICS=("otsu_ink_median_darkness","edge_median_darkness")
HV="HHVVHHVHHHHV"

def load_gray():
    return np.array(Image.open(SOURCE).convert("L"))

def image_variants(gray):
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

def building_boxes():
    j=json.loads(STAGE12.read_text())
    rows=[]
    for r in j["regions"]:
        if r["name"].startswith("building_"):
            rows.append((r["name"],tuple(map(int,r["bbox"]))))
    rows.sort()
    if len(rows)!=12:
        raise RuntimeError(f"expected 12 building boxes, got {len(rows)}")
    return rows

def perturb_box(b,margin,dx,dy,shape):
    h,w=shape
    x0,y0,x1,y1=b
    x0+=dx; x1+=dx; y0+=dy; y1+=dy
    bw=max(1,x1-x0); bh=max(1,y1-y0)
    mx=int(round(bw*margin)); my=int(round(bh*margin))
    x0=max(0,x0+mx); x1=min(w,x1-mx)
    y0=max(0,y0+my); y1=min(h,y1-my)
    if x1-x0<8 or y1-y0<8:
        raise RuntimeError("perturbed crop too small")
    return x0,y0,x1,y1

def crop(a,b):
    x0,y0,x1,y1=b
    return a[y0:y1,x0:x1]

def tone_metric(c,name):
    c=np.asarray(c,np.uint8)
    if name=="otsu_ink_median_darkness":
        thr,_=cv2.threshold(c,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        ink=c<c.astype(np.uint8).max()  # placeholder overwritten below
        ink=c<thr
        vals=c[ink]
        if vals.size<12:
            vals=c[c<230]
        if vals.size<12:
            return 0.0
        return float(np.median(255.0-vals))/255.0
    if name=="edge_median_darkness":
        e=cv2.Canny(c,45,135)
        vals=c[(e>0)&(c<245)]
        if vals.size<12:
            vals=c[c<220]
        if vals.size<12:
            return 0.0
        return float(np.median(255.0-vals))/255.0
    raise ValueError(name)

def optimal_1d_labels(values,k):
    x=np.asarray(values,float)
    n=len(x)
    order=np.argsort(x)
    xs=x[order]
    best=None
    for cuts in itertools.combinations(range(1,n),k-1):
        parts=np.split(xs,cuts)
        if any(len(p)==0 for p in parts):
            continue
        sse=float(sum(np.sum((p-p.mean())**2) for p in parts))
        if best is None or sse<best[0]:
            best=(sse,cuts,parts)
    if best is None:
        raise RuntimeError("clustering failed")
    sse,cuts,parts=best
    labels_sorted=np.empty(n,dtype=int)
    st=0
    centers=[]
    for lab,p in enumerate(parts):
        en=st+len(p)
        labels_sorted[st:en]=lab
        centers.append(float(np.mean(p)))
        st=en
    labels=np.empty(n,dtype=int)
    labels[order]=labels_sorted
    # Common-variance Gaussian-like BIC with a quantization-aware variance
    # floor. The tone metrics are medians of 8-bit grayscale values, so treating
    # sub-quantization residuals as arbitrarily precise lets k=3 overfit a true
    # binary control by splitting nearly identical values. A 2-level grayscale
    # noise floor is conservative and still far below the synthetic class gaps.
    var_floor=(2.0/255.0)**2
    bic=float(n*math.log(max(sse/n,var_floor)) + (2*k)*math.log(n))
    return {
        "k":k,
        "labels":labels.tolist(),
        "centers":centers,
        "sizes":[int(np.sum(labels==j)) for j in range(k)],
        "sse":sse,
        "bic":bic,
    }

def choose_model(values):
    m2=optimal_1d_labels(values,2)
    m3=optimal_1d_labels(values,3)
    win=2 if m2["bic"]<=m3["bic"] else 3
    return {"winner":win,"k2":m2,"k3":m3}

def classify_real(gray,boxes,margin,jitter,metric_name):
    dx,dy=jitter
    vals=[]
    for _,b in boxes:
        pb=perturb_box(b,margin,dx,dy,gray.shape)
        vals.append(tone_metric(crop(gray,pb),metric_name))
    return vals,choose_model(vals)

def render_patch(tone,vertical,dense,w=100,h=150):
    im=np.full((h,w),255,np.uint8)
    gap=6 if dense else 13
    cv2.rectangle(im,(4,4),(w-5,h-5),int(tone),2)
    if vertical:
        for x in range(10,w-9,gap):
            cv2.line(im,(x,10),(x,h-11),int(tone),2,cv2.LINE_AA)
    else:
        for y in range(10,h-9,gap):
            cv2.line(im,(10,y),(w-11,y),int(tone),2,cv2.LINE_AA)
    return im

def synth_set(k):
    if k==2:
        tones=[190]*6+[70]*6
        expected=[0]*6+[1]*6
    else:
        tones=[190]*4+[130]*4+[70]*4
        expected=[0]*4+[1]*4+[2]*4
    patches=[]
    for i,t in enumerate(tones):
        patches.append(render_patch(t,vertical=(i%2==0),dense=(i%3==0)))
    return patches,expected

def patch_variants(p):
    return image_variants(p)

def validate_synthetic(k):
    patches,expected=synth_set(k)
    pvars=[patch_variants(p) for p in patches]
    total=correct_model=0
    label_hits=0
    label_total=0
    for v in VARIANTS:
        for margin in MARGINS:
            for jitter in JITTERS:
                for metric_name in METRICS:
                    vals=[]
                    dx,dy=jitter
                    for pv in pvars:
                        p=pv[v]
                        h,w=p.shape
                        b=perturb_box((0,0,w,h),margin,dx,dy,p.shape)
                        vals.append(tone_metric(crop(p,b),metric_name))
                    ch=choose_model(vals)
                    total+=1
                    if ch["winner"]==k:
                        correct_model+=1
                    labs=ch[f"k{k}"]["labels"]
                    label_hits+=sum(int(a==b) for a,b in zip(labs,expected))
                    label_total+=len(expected)
    return {
        "k":k,
        "conditions":total,
        "correct_model_fraction":correct_model/total,
        "label_accuracy":label_hits/label_total,
        "pass":bool(correct_model/total>=0.95 and label_hits/label_total>=0.98),
    }

def hamming(a,b):
    return sum(int(x!=y) for x,y in zip(a,b))

def main():
    gray=load_gray()
    vv=image_variants(gray)
    bb=building_boxes()

    controls={"binary":validate_synthetic(2),"ternary":validate_synthetic(3)}
    controls_pass=all(x["pass"] for x in controls.values())

    rows=[]
    winner_counts={m:Counter() for m in METRICS}
    models_by_metric={m:[] for m in METRICS}
    for v in VARIANTS:
        for margin in MARGINS:
            for jitter in JITTERS:
                for metric_name in METRICS:
                    vals,ch=classify_real(vv[v],bb,margin,jitter,metric_name)
                    winner_counts[metric_name][ch["winner"]]+=1
                    models_by_metric[metric_name].append({
                        "variant":v,"margin":margin,"jitter":list(jitter),
                        "values":vals,"choice":ch,
                    })
                    rows.append({
                        "variant":v,"margin":margin,"jitter":list(jitter),
                        "metric":metric_name,
                        "winner":ch["winner"],
                        "bic2":ch["k2"]["bic"],"bic3":ch["k3"]["bic"],
                    })

    dominant={}
    for m in METRICS:
        n2=winner_counts[m][2]; n3=winner_counts[m][3]
        k=2 if n2>=n3 else 3
        dominant[m]={
            "k":k,
            "win_fraction":max(n2,n3)/max(1,n2+n3),
            "counts":{"2":n2,"3":n3},
        }

    same_k=len(set(dominant[m]["k"] for m in METRICS))==1
    dom_k=dominant[METRICS[0]]["k"] if same_k else None

    dominant_labels=None
    stability=None
    stable90=0
    class_counts=None
    redundant=False
    if same_k:
        all_labelings=[]
        for m in METRICS:
            for rec in models_by_metric[m]:
                all_labelings.append(rec["choice"][f"k{dom_k}"]["labels"])
        A=np.asarray(all_labelings,int)
        dominant_labels=[]
        stability=[]
        for i in range(12):
            cnt=Counter(A[:,i].tolist())
            lab,n=cnt.most_common(1)[0]
            dominant_labels.append(int(lab))
            stability.append(float(n/A.shape[0]))
        stable90=sum(x>=0.90 for x in stability)
        class_counts={str(j):dominant_labels.count(j) for j in range(dom_k)}

        if dom_k==2:
            hv=[1 if x=="V" else 0 for x in HV]
            density=json.loads(STAGE106.read_text())["stable_density_labels"]
            d_hv=min(hamming(dominant_labels,hv),hamming(dominant_labels,[1-x for x in hv]))
            d_den=min(hamming(dominant_labels,density),hamming(dominant_labels,[1-x for x in density]))
            redundant=(d_hv<=1 or d_den<=1)

    class_ok=bool(
        same_k and class_counts is not None
        and all(n>=2 for n in class_counts.values())
    )
    model_ok=bool(
        same_k and all(dominant[m]["win_fraction"]>=0.80 for m in METRICS)
    )
    promoted=bool(
        controls_pass and model_ok and stable90>=10 and class_ok and not redundant
    )

    result={
        "experiment_id":"A11-EXP-110",
        "scope":"per-building conditional stroke-tone classes under crop/loss perturbations; no private-key operations",
        "metrics":list(METRICS),
        "margins":list(MARGINS),
        "jitters":[list(x) for x in JITTERS],
        "variants":list(VARIANTS),
        "synthetic_controls":controls,
        "controls_pass":controls_pass,
        "winner_counts":{m:{str(k):int(v) for k,v in winner_counts[m].items()} for m in METRICS},
        "dominant_model_by_metric":dominant,
        "same_dominant_k":same_k,
        "dominant_k":dom_k,
        "dominant_labels":dominant_labels,
        "per_building_stability":stability,
        "buildings_ge_90pct":stable90,
        "class_counts":class_counts,
        "redundant_with_hv_or_retired_density":redundant,
        "promotion_rule":"binary and ternary synthetic tone controls pass; both real metrics choose the same k in >=80% of conditions; >=10/12 buildings retain the same ordered tone class in >=90% of all metric×variant×margin×jitter conditions; every class has >=2 members; binary result not within 1 bit of H/V or retired density labels",
        "promoted":promoted,
        "condition_summary":rows,
        "interpretation_guard":"Promotion validates only a visible stroke-tone channel. No class-to-secret mapping is attempted.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    if dominant_labels is None:
        seq="unresolved"
    else:
        alphabet="LMD" if dom_k==3 else "LD"
        seq="".join(alphabet[x] for x in dominant_labels)

    md=[
        "# Stage 110 — building stroke-tone / pencil-pressure audit",
        "",
        f"- synthetic binary control pass: **{controls['binary']['pass']}**",
        f"- synthetic ternary control pass: **{controls['ternary']['pass']}**",
        f"- real dominant models: **{dominant}**",
        f"- same dominant k across both metrics: **{same_k}**",
        f"- buildings stable >=90%: **{stable90}/12**",
        f"- tone sequence: **{seq}**",
        f"- class counts: **{class_counts}**",
        f"- redundant with H/V or retired density: **{redundant}**",
        f"- promoted: **{promoted}**",
        "",
        "## Synthetic controls",
        "",
        f"- binary correct-model fraction: {controls['binary']['correct_model_fraction']:.3f}, label accuracy: {controls['binary']['label_accuracy']:.3f}",
        f"- ternary correct-model fraction: {controls['ternary']['correct_model_fraction']:.3f}, label accuracy: {controls['ternary']['label_accuracy']:.3f}",
    ]
    if dominant_labels is not None:
        md += ["","## Per-building stability","","| building | class | stability |","|---:|:---:|---:|"]
        alphabet="LMD" if dom_k==3 else "LD"
        for i,(lab,st) in enumerate(zip(dominant_labels,stability),1):
            md.append(f"| {i} | {alphabet[lab]} | {st:.3f} |")
    md += ["","## Interpretation",""]
    if not controls_pass:
        md.append("The tone harness fails one or more synthetic controls. This is an implementation failure; do not interpret the real-image clustering.")
    elif promoted:
        md.append("The buildings carry a robust discrete stroke-tone channel that survives crop and lossy perturbations and is not redundant with H/V or the retired density split. This feature is eligible for a semantic joint-state follow-up.")
    else:
        md.append("Per-building stroke tone does not form a sufficiently stable, independently validated discrete channel. Retire stroke-tone coding.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-110",
        "controls_pass":controls_pass,"dominant":dominant,
        "same_k":same_k,"stable90":stable90,"sequence":seq,"promoted":promoted
    }))

if __name__=="__main__":
    main()
