#!/usr/bin/env python3
"""Stage 113: exact 64 x 25 px visual-cell carrier audit.

Motivation:
- source width = 1600 px
- raw Ethereum private key display width = 64 hex characters
- 1600 = 64 * 25 exactly

This stage does NOT decode, persist, print, map to hex, reconstruct, or verify
an ordered 64-symbol sequence. It tests only whether the 64 fixed-width visual
cells behave like a robust 16-state, phase-aligned visual carrier.

Safe scope only: no private-key generation, derivation, reconstruction,
enumeration, verification, or wallet access.
"""
from __future__ import annotations

import io, json, math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage113-64x25-visual-cell-carrier"
OUT.mkdir(parents=True,exist_ok=True)

CELL_W=25
N_CELLS=64
N_STATES=16
PHASES=tuple(range(CELL_W))
VARIANTS=("original","jpeg85","jpeg70","down75_up")
K_VALUES=tuple(range(2,21))

def load_gray(path=SOURCE):
    return np.array(Image.open(path).convert("L"))

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

def entropy16(c):
    hist,_=np.histogram(c,bins=16,range=(0,256))
    p=hist.astype(float)
    p=p/p.sum()
    p=p[p>0]
    return float(-np.sum(p*np.log2(p))/4.0)  # normalize to [0,1]

def cell_features(c):
    x=c.astype(np.float32)
    feats=[
        float(np.mean(x)/255.0),
        float(np.std(x)/128.0),
    ]
    for thr in (100,140,180):
        feats.append(float(np.mean(x<thr)))

    edges=cv2.Canny(c,60,160)>0
    feats.append(float(np.mean(edges)))

    gx=cv2.Sobel(x,cv2.CV_32F,1,0,ksize=3)
    gy=cv2.Sobel(x,cv2.CV_32F,0,1,ksize=3)
    ex=float(np.mean(gx*gx)); ey=float(np.mean(gy*gy))
    feats.append(float(ex/(ex+ey+1e-9)))
    feats.append(float(min(ex,ey)/(max(ex,ey)+1e-9)))

    feats.append(entropy16(c))

    dark=(c<160)
    ys=np.where(dark)[0]
    feats.append(float(np.mean(ys)/(max(1,c.shape[0]-1))) if len(ys) else 0.5)

    bw=(dark.astype(np.uint8)*255)
    n,lab,stats,_=cv2.connectedComponentsWithStats(bw,8)
    comps=0
    for i in range(1,n):
        if stats[i,cv2.CC_STAT_AREA]>=3:
            comps+=1
    feats.append(float(min(comps,80)/80.0))
    return np.asarray(feats,float)

def feature_cells(gray,phase):
    if gray.shape[1] != CELL_W*N_CELLS:
        raise ValueError(f"expected width {CELL_W*N_CELLS}, got {gray.shape[1]}")
    shifted=np.roll(gray,-int(phase),axis=1)
    return np.stack([
        cell_features(shifted[:,i*CELL_W:(i+1)*CELL_W])
        for i in range(N_CELLS)
    ])

def standardize(X,mean=None,sd=None):
    if mean is None:
        mean=X.mean(axis=0)
    if sd is None:
        sd=X.std(axis=0)
    sd=np.where(sd<1e-8,1.0,sd)
    return (X-mean)/sd,mean,sd

def kmeans_fit(X,k,restarts=12):
    best=None
    for r in range(restarts):
        rng=np.random.default_rng(113000+k*97+r)
        first=int(rng.integers(0,len(X)))
        centers=[X[first].copy()]
        while len(centers)<k:
            C=np.stack(centers)
            d=np.min(np.sum((X[:,None,:]-C[None,:,:])**2,axis=2),axis=1)
            if float(d.sum())<=1e-12:
                choices=[i for i in range(len(X)) if all(np.linalg.norm(X[i]-z)>1e-9 for z in centers)]
                if not choices:
                    centers.append(X[int(rng.integers(0,len(X)))].copy())
                else:
                    centers.append(X[choices[int(rng.integers(0,len(choices)))]] .copy())
            else:
                p=d/d.sum()
                centers.append(X[int(rng.choice(len(X),p=p))].copy())
        C=np.stack(centers)
        lab=np.zeros(len(X),int)
        for _ in range(100):
            D=np.sum((X[:,None,:]-C[None,:,:])**2,axis=2)
            nl=np.argmin(D,axis=1)
            if np.array_equal(nl,lab) and _>0:
                break
            lab=nl
            for j in range(k):
                m=(lab==j)
                if np.any(m):
                    C[j]=X[m].mean(axis=0)
                else:
                    C[j]=X[int(rng.integers(0,len(X)))]
        inertia=float(np.sum((X-C[lab])**2))
        if best is None or inertia<best[0]:
            best=(inertia,lab.copy(),C.copy())
    return best[1],best[2],best[0]

def assign(X,C):
    D=np.sum((X[:,None,:]-C[None,:,:])**2,axis=2)
    return np.argmin(D,axis=1)

def silhouette(X,lab):
    n=len(X)
    uniq=np.unique(lab)
    if len(uniq)<2 or len(uniq)>=n:
        return -1.0
    D=np.sqrt(np.sum((X[:,None,:]-X[None,:,:])**2,axis=2))
    s=[]
    for i in range(n):
        same=np.where(lab==lab[i])[0]
        same=same[same!=i]
        a=float(np.mean(D[i,same])) if len(same) else 0.0
        b=float("inf")
        for u in uniq:
            if u==lab[i]:
                continue
            idx=np.where(lab==u)[0]
            if len(idx):
                b=min(b,float(np.mean(D[i,idx])))
        if not np.isfinite(b):
            s.append(0.0)
        else:
            den=max(a,b)
            s.append((b-a)/den if den>1e-12 else 0.0)
    return float(np.mean(s))

def phase_eval(vv,phase):
    X0=feature_cells(vv["original"],phase)
    Z0,mean,sd=standardize(X0)
    lab,C,_=kmeans_fit(Z0,N_STATES)
    sil=silhouette(Z0,lab)

    stabs=[]
    for v in VARIANTS[1:]:
        X=feature_cells(vv[v],phase)
        Z,_,_=standardize(X,mean,sd)
        lv=assign(Z,C)
        stabs.append(float(np.mean(lv==lab)))
    stability=float(np.mean(stabs))

    counts=np.bincount(lab,minlength=N_STATES)
    occupied=int(np.sum(counts>0))
    singletons=int(np.sum(counts==1))
    occ_factor=min(1.0,occupied/12.0)
    singleton_factor=max(0.0,1.0-singletons/12.0)
    score=float(max(0.0,sil)*stability*occ_factor*singleton_factor)
    return {
        "silhouette_k16":sil,
        "cross_variant_stability":stability,
        "occupied_states":occupied,
        "singleton_states":singletons,
        "score":score,
    }

def k_sweep(gray):
    X=feature_cells(gray,0)
    Z,_,_=standardize(X)
    rows=[]
    for k in K_VALUES:
        lab,C,inertia=kmeans_fit(Z,k)
        rows.append({
            "k":k,
            "silhouette":silhouette(Z,lab),
            "occupied":int(len(np.unique(lab))),
            "inertia":float(inertia),
        })
    best=max(rows,key=lambda r:r["silhouette"])
    k16=next(r for r in rows if r["k"]==16)
    rank=1+sum(r["silhouette"]>k16["silhouette"]+1e-12 for r in rows)
    effectively_tied=bool(best["silhouette"]-k16["silhouette"]<=0.02)
    return rows,best,rank,effectively_tied

def evaluate_image(gray):
    vv=variants(gray)
    phases=[{"phase":p,**phase_eval(vv,p)} for p in PHASES]
    phases_sorted=sorted(phases,key=lambda r:r["score"],reverse=True)
    p0=next(r for r in phases if r["phase"]==0)
    phase_rank=1+sum(r["score"]>p0["score"]+1e-12 for r in phases)
    ks,best,k16_rank,k16_tied=k_sweep(gray)

    structural_gate=bool(
        p0["cross_variant_stability"]>=0.90
        and p0["occupied_states"]>=12
        and p0["singleton_states"]<=4
        and phase_rank==1
        and k16_tied
    )
    return {
        "phase0":p0,
        "phase0_rank":phase_rank,
        "top_phase_scores":phases_sorted[:5],
        "all_phase_scores":phases,
        "k_sweep":ks,
        "best_k":best,
        "k16_silhouette_rank":k16_rank,
        "k16_effectively_tied_best":k16_tied,
        "structural_gate":structural_gate,
    }

def synthetic_positive(h=320):
    """JPEG-stable aligned 16-state control with exact 25-px boundaries.

    Each state is a broad, distinct mean tone. Every state occurs four times in
    a fixed shuffled order. Phase-0 cells are pure repeated states; off-phase
    cells mix unrelated neighboring tones, which should reduce the exact
    16-state structure. Mean/std are deliberately included in the coarse feature
    vector so this control validates the cell-boundary and clustering harness.
    """
    img=np.full((h,1600),245,np.uint8)
    rng=np.random.default_rng(113)
    labels=np.repeat(np.arange(N_STATES),4)
    rng.shuffle(labels)
    tones=np.linspace(25,235,N_STATES).round().astype(np.uint8)

    for i,s in enumerate(labels.tolist()):
        x0=i*CELL_W
        # Common guard bands isolate each state from resampling/JPEG bleed at
        # neighboring 25-px boundaries. Only the broad 17-px interior carries
        # the synthetic state.
        img[:,x0:x0+CELL_W]=245
        img[:,x0+4:x0+21]=tones[s]
    return img

def synthetic_negative(h=320):
    # Continuous field with no 25-px cell boundaries.
    img=np.full((h,1600),245,np.uint8)
    for x in range(0,1600,7):
        phase=2*math.pi*x/1600.0
        y=int(h*.50+h*.30*math.sin(3*phase))
        ang=.35*math.sin(5*phase)
        dx=18
        dy=int(dx*math.tan(ang))
        tone=int(55+35*(.5+.5*math.sin(7*phase)))
        cv2.line(img,(max(0,x-dx),max(0,y-dy)),(min(1599,x+dx),min(h-1,y+dy)),tone,1,cv2.LINE_AA)
    return img

def control_gate(ev,positive):
    if positive:
        return bool(
            ev["phase0"]["cross_variant_stability"]>=0.95
            and ev["phase0"]["occupied_states"]>=14
            and ev["phase0_rank"]==1
            and ev["k16_effectively_tied_best"]
        )
    return bool(not ev["structural_gate"])

def main():
    gray=load_gray()
    if gray.shape[1]!=1600:
        raise SystemExit(f"unexpected image width {gray.shape[1]}")

    pos=evaluate_image(synthetic_positive())
    neg=evaluate_image(synthetic_negative())
    pos_pass=control_gate(pos,True)
    neg_pass=control_gate(neg,False)
    controls_pass=bool(pos_pass and neg_pass)

    real=evaluate_image(gray)
    promoted=bool(controls_pass and real["structural_gate"])

    # Never persist cluster labels or any ordered 64-state sequence.
    result={
        "experiment_id":"A11-EXP-113",
        "scope":"64 vertical cells x 25 px; robust 16-state carrier-structure test only; no ordered class sequence persisted and no private-key operations",
        "exact_dimension_relation":"1600 px = 64 cells * 25 px",
        "features":["mean_gray","std_gray","ink100","ink140","ink180","edge_density","gradient_x_fraction","gradient_balance","entropy16","dark_y_centroid","component_density"],
        "positive_control":{
            "passed":pos_pass,
            "phase0":pos["phase0"],
            "phase0_rank":pos["phase0_rank"],
            "best_k":pos["best_k"],
            "k16_rank":pos["k16_silhouette_rank"],
            "k16_tied":pos["k16_effectively_tied_best"],
        },
        "negative_control":{
            "passed":neg_pass,
            "phase0":neg["phase0"],
            "phase0_rank":neg["phase0_rank"],
            "best_k":neg["best_k"],
            "k16_rank":neg["k16_silhouette_rank"],
            "k16_tied":neg["k16_effectively_tied_best"],
            "structural_gate":neg["structural_gate"],
        },
        "controls_pass":controls_pass,
        "real":{
            "phase0":real["phase0"],
            "phase0_rank":real["phase0_rank"],
            "top_phase_scores":real["top_phase_scores"],
            "best_k":real["best_k"],
            "k16_silhouette_rank":real["k16_silhouette_rank"],
            "k16_effectively_tied_best":real["k16_effectively_tied_best"],
            "structural_gate":real["structural_gate"],
        },
        "promotion_rule":"both controls pass; phase0 k16 assignments stable >=0.90 across lossy variants; >=12 states occupied; <=4 singleton states; phase0 ranks #1 among all 25 x-phases; k16 silhouette within 0.02 of best k=2..20",
        "promoted":promoted,
        "safety_guard":"No ordered 64-cell cluster labels are written, printed, mapped to hexadecimal, reconstructed as secret material, or verified against any wallet.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 113 — 64 × 25 px visual-cell carrier audit",
        "",
        "**Experiment:** A11-EXP-113",
        "",
        f"- exact relation: **1600 = 64 × 25**",
        f"- positive control pass: **{pos_pass}**",
        f"- negative control pass: **{neg_pass}**",
        f"- controls pass: **{controls_pass}**",
        f"- real phase-0 rank: **{real['phase0_rank']}/25**",
        f"- real k=16 silhouette: **{real['phase0']['silhouette_k16']:.4f}**",
        f"- real k=16 cross-variant stability: **{real['phase0']['cross_variant_stability']:.4f}**",
        f"- occupied k=16 states: **{real['phase0']['occupied_states']}/16**",
        f"- singleton states: **{real['phase0']['singleton_states']}**",
        f"- best k by silhouette: **{real['best_k']['k']}**",
        f"- k=16 silhouette rank: **{real['k16_silhouette_rank']}/19**",
        f"- k=16 effectively tied with best: **{real['k16_effectively_tied_best']}**",
        f"- real structural gate: **{real['structural_gate']}**",
        f"- promoted: **{promoted}**",
        "",
        "## Top phase scores",
        "",
        "| rank | phase | score | silhouette16 | stability | occupied | singletons |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for i,r in enumerate(real["top_phase_scores"],1):
        md.append(
            f"| {i} | {r['phase']} | {r['score']:.5f} | {r['silhouette_k16']:.4f} | "
            f"{r['cross_variant_stability']:.4f} | {r['occupied_states']} | {r['singleton_states']} |"
        )
    md += ["","## Interpretation",""]
    if not controls_pass:
        md.append("The carrier-structure harness failed its synthetic controls. Stage 113 is an implementation failure and must be repaired under the same stage number before interpreting Puzzle #11.")
    elif promoted:
        md.append("The exact 25-px phase behaves like a robust 16-state cell carrier under lossy re-encoding and is exceptional among all 25 possible phases. This promotes the 64×25 visual-cell geometry for a next-stage mechanism audit, without revealing or persisting any ordered symbols.")
    else:
        md.append("The exact 64×25 partition does not satisfy the predeclared carrier-structure gates. Retire simple one-hex-symbol-per-25px vertical-cell encoding.")
    md += [
        "",
        "No ordered 64-cell symbol sequence is stored or printed.",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-113",
        "controls_pass":controls_pass,
        "phase0_rank":real["phase0_rank"],
        "k16_stability":real["phase0"]["cross_variant_stability"],
        "best_k":real["best_k"]["k"],
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
