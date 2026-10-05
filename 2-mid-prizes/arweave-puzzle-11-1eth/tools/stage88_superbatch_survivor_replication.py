#!/usr/bin/env python3
"""Stage 88: adversarial replication of the three nominal superbatch survivors.

Safe scope only. This stage does not reconstruct, generate, enumerate, derive, or
verify private-key candidates and does not attempt wallet access.

The superbatch produced three nominal p<=0.05 results but none survived FDR.
Stage 88 does not invent new candidate families. It subjects exactly those three
survivors to independent / stricter confirmation tests:

A11-EXP-043 large-boat vertical projection:
  Recalibrate against nuisance-matched same-size windows rather than arbitrary
  random windows. Matching uses only mean darkness, ink fraction, and edge
  density, never the projection statistic. Same matched boxes are used after
  JPEG85+resampling.

A11-EXP-050 rightmost reflection correlation:
  Require the effect to survive removal of low-frequency tone (high-pass) and
  an edge-only representation, plus two fixed 200px spatial halves. Repeat
  high-pass/edge tests after JPEG85+resampling.

A11-EXP-061 small-sail width/following-gap correlation:
  Recompute the correlation using both independent Stage-19 segmentation
  families and exact enumeration of all 5! width permutations.

The three primary confirmatory p-values are Holm-adjusted. A survivor is
confirmed only when its family-specific replication gate passes and Holm p<=.05.
"""
from __future__ import annotations
import itertools, json, math
from pathlib import Path
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
RUN19=ROOT/"analysis"/"runs"/"stage19-small-sail-remeasure"/"result.json"
RUN43=ROOT/"analysis"/"runs"/"superbatch-37-87"/"exp_043"/"result.json"
RUN50=ROOT/"analysis"/"runs"/"superbatch-37-87"/"exp_050"/"result.json"
RUN61=ROOT/"analysis"/"runs"/"superbatch-37-87"/"exp_061"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage88-superbatch-survivor-replication"
OUT.mkdir(parents=True,exist_ok=True)

LARGE=(44,320,359,599)
MATCHED_K=250
GRID_STEP=16

def load_gray():
    return np.array(Image.open(SOURCE).convert("L"))

def lossy(gray):
    im=Image.fromarray(gray,mode="L")
    b=BytesIO()
    im.save(b,format="JPEG",quality=85,optimize=False,progressive=False)
    b.seek(0)
    j=Image.open(b).convert("L")
    h,w=gray.shape
    small=j.resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    return np.array(small.resize((w,h),Image.Resampling.LANCZOS))

def crop(a,box):
    x0,y0,x1,y1=map(int,box)
    return a[y0:y1,x0:x1]

def edge_mask(c):
    return cv2.Canny(c.astype(np.uint8),80,160)>0

def safe_corr(a,b):
    x=np.asarray(a,dtype=float).ravel()
    y=np.asarray(b,dtype=float).ravel()
    if len(x)!=len(y) or len(x)<3 or np.std(x)<1e-12 or np.std(y)<1e-12:
        return 0.0
    return float(np.corrcoef(x,y)[0,1])

def vproj_peak(c):
    m=(np.asarray(c)<180).astype(float)
    p=m.sum(axis=0)
    if len(p)<4 or np.std(p)<1e-12:
        return 0.0
    z=(p-p.mean())/(p.std()+1e-12)
    ac=np.correlate(z,z,mode="full")[len(z)-1:]
    hi=min(len(ac),max(4,len(ac)//2))
    return float(np.max(ac[2:hi])/(len(z)+1e-12)) if hi>2 else 0.0

def nuisance(c):
    c=np.asarray(c,dtype=np.uint8)
    return np.array([
        255.0-float(c.mean()),
        float((c<180).mean()),
        float(edge_mask(c).mean()),
    ],dtype=float)

def iou(a,b):
    ax0,ay0,ax1,ay1=a; bx0,by0,bx1,by1=b
    ix0=max(ax0,bx0); iy0=max(ay0,by0)
    ix1=min(ax1,bx1); iy1=min(ay1,by1)
    iw=max(0,ix1-ix0); ih=max(0,iy1-iy0)
    inter=iw*ih
    aa=(ax1-ax0)*(ay1-ay0); bb=(bx1-bx0)*(by1-by0)
    return inter/max(1,aa+bb-inter)

def upper_p(obs,null):
    return float((1+sum(v>=obs-1e-15 for v in null))/(1+len(null)))

def stage43_matched(gray,gray2):
    x0,y0,x1,y1=LARGE
    h=y1-y0; w=x1-x0
    target_n=nuisance(crop(gray,LARGE))
    boxes=[]
    nuis=[]
    H,W=gray.shape
    for y in range(0,H-h+1,GRID_STEP):
        for x in range(0,W-w+1,GRID_STEP):
            b=(x,y,x+w,y+h)
            if iou(b,LARGE)>0.05:
                continue
            boxes.append(b)
            nuis.append(nuisance(crop(gray,b)))
    N=np.stack(nuis,axis=0)
    sd=N.std(axis=0)
    sd=np.where(sd<1e-9,1.0,sd)
    dist=np.sqrt(np.sum(((N-target_n)/sd)**2,axis=1))
    order=np.argsort(dist)[:MATCHED_K]
    matched=[boxes[int(i)] for i in order]

    obs=vproj_peak(crop(gray,LARGE))
    null=[vproj_peak(crop(gray,b)) for b in matched]
    p0=upper_p(obs,null)

    obs2=vproj_peak(crop(gray2,LARGE))
    null2=[vproj_peak(crop(gray2,b)) for b in matched]
    p1=upper_p(obs2,null2)

    primary=max(p0,p1)
    return {
        "candidate":"A11-EXP-043",
        "name":"large-boat vertical projection peak",
        "original_superbatch_p":json.loads(RUN43.read_text())["p_value"],
        "matched_windows":len(matched),
        "target_nuisance":{
            "mean_darkness":float(target_n[0]),
            "ink180_fraction":float(target_n[1]),
            "edge_density":float(target_n[2]),
        },
        "obs":obs,
        "matched_null_median":float(np.median(null)),
        "matched_p":p0,
        "lossy_obs":obs2,
        "lossy_matched_null_median":float(np.median(null2)),
        "lossy_matched_p":p1,
        "primary_confirmation_p":primary,
        "family_gate":bool(p0<=0.05 and p1<=0.05),
        "gate_rule":"original and lossy nuisance-matched p must both be <=0.05",
    }

def reflection_rep(a,x0,x1,kind):
    u=a[0:320,x0:x1].astype(np.float32)
    d=np.flipud(a[320:640,x0:x1]).astype(np.float32)
    if kind=="highpass":
        u=u-cv2.GaussianBlur(u,(0,0),8.0)
        d=d-cv2.GaussianBlur(d,(0,0),8.0)
    elif kind=="edge":
        u=edge_mask(u.astype(np.uint8)).astype(float)
        d=edge_mask(d.astype(np.uint8)).astype(float)
    elif kind=="gray":
        pass
    else:
        raise ValueError(kind)
    return abs(safe_corr(u,d))

def reflection_null(a,x0,x1,kind):
    upper=a[0:320,x0:x1]
    lower=a[320:640,x0:x1]
    vals=[]
    width=x1-x0
    for s in range(7,max(8,width-6)):
        u=upper.astype(np.float32)
        d=np.flipud(np.roll(lower,s,axis=1)).astype(np.float32)
        if kind=="highpass":
            u=u-cv2.GaussianBlur(u,(0,0),8.0)
            d=d-cv2.GaussianBlur(d,(0,0),8.0)
        elif kind=="edge":
            u=edge_mask(u.astype(np.uint8)).astype(float)
            d=edge_mask(d.astype(np.uint8)).astype(float)
        vals.append(abs(safe_corr(u,d)))
    return vals

def reflection_test_one(a,x0,x1,kind):
    obs=reflection_rep(a,x0,x1,kind)
    null=reflection_null(a,x0,x1,kind)
    return {"obs":obs,"null_median":float(np.median(null)),"p":upper_p(obs,null)}

def stage50_replication(gray,gray2):
    full0={k:reflection_test_one(gray,1200,1600,k) for k in ("gray","highpass","edge")}
    full1={k:reflection_test_one(gray2,1200,1600,k) for k in ("highpass","edge")}
    halves0=[
        reflection_test_one(gray,1200,1400,"gray"),
        reflection_test_one(gray,1400,1600,"gray"),
    ]
    primary=max(
        full0["highpass"]["p"],full0["edge"]["p"],
        full1["highpass"]["p"],full1["edge"]["p"],
    )
    gate=bool(
        full0["highpass"]["p"]<=0.05 and
        full0["edge"]["p"]<=0.05 and
        full1["highpass"]["p"]<=0.05 and
        full1["edge"]["p"]<=0.05 and
        halves0[0]["p"]<=0.10 and halves0[1]["p"]<=0.10
    )
    return {
        "candidate":"A11-EXP-050",
        "name":"rightmost grayscale reflection correlation",
        "original_superbatch_p":json.loads(RUN50.read_text())["p_value"],
        "original_full":full0,
        "lossy_full":full1,
        "original_fixed_halves":halves0,
        "primary_confirmation_p":primary,
        "family_gate":gate,
        "gate_rule":"highpass+edge p<=0.05 on original and lossy, and both fixed raw-grayscale 200px halves p<=0.10",
    }

def exact_width_gap(widths,centers):
    widths=np.asarray(widths,dtype=float)
    centers=np.asarray(centers,dtype=float)
    gaps=np.diff(centers)
    obs=abs(safe_corr(widths[:-1],gaps))
    vals=[]
    for p in itertools.permutations(widths.tolist()):
        vals.append(abs(safe_corr(np.asarray(p,dtype=float)[:-1],gaps)))
    p=float(sum(v>=obs-1e-15 for v in vals)/len(vals))
    return {
        "widths":widths.tolist(),
        "centers":centers.tolist(),
        "following_gaps":gaps.tolist(),
        "abs_correlation":obs,
        "exact_permutations":len(vals),
        "exact_p":p,
        "null_median":float(np.median(vals)),
    }

def stage61_replication():
    s19=json.loads(RUN19.read_text())
    methods={}
    for m in s19["methods"]:
        methods[m["method"]]=exact_width_gap(
            m["stable_widths_left_to_right"],
            m["stable_centers_left_to_right"],
        )
    pvals=[v["exact_p"] for v in methods.values()]
    primary=max(pvals)

    s61=json.loads(RUN61.read_text())
    old_centers=np.array([z["cx"] for z in s61.get("components",[])],dtype=float)
    stable_centers=np.array(s19["methods"][0]["stable_centers_left_to_right"],dtype=float)
    nearest=[]
    for x in old_centers:
        d=float(np.min(np.abs(stable_centers-x))) if len(stable_centers) else float("inf")
        nearest.append(d)
    overlap=sum(d<=40 for d in nearest)

    gate=bool(all(p<=0.05 for p in pvals))
    return {
        "candidate":"A11-EXP-061",
        "name":"small-sail width vs following-gap correlation",
        "original_superbatch_p":s61["p_value"],
        "independent_stage19_methods":methods,
        "stage61_to_stage19_center_nearest_distance_px":nearest,
        "stage61_components_matching_stage19_within_40px":overlap,
        "primary_confirmation_p":primary,
        "family_gate":gate,
        "gate_rule":"both independent Stage-19 segmentation families must have exact permutation p<=0.05",
    }

def holm_adjust(named_p):
    ordered=sorted(named_p.items(),key=lambda kv:kv[1])
    m=len(ordered)
    out={}
    running=0.0
    for rank,(name,p) in enumerate(ordered,1):
        adj=min(1.0,(m-rank+1)*p)
        running=max(running,adj)
        out[name]=running
    return out

def main():
    gray=load_gray()
    gray2=lossy(gray)

    r43=stage43_matched(gray,gray2)
    r50=stage50_replication(gray,gray2)
    r61=stage61_replication()
    rows=[r43,r50,r61]

    primary={r["candidate"]:float(r["primary_confirmation_p"]) for r in rows}
    holm=holm_adjust(primary)
    for r in rows:
        r["holm_p"]=float(holm[r["candidate"]])
        r["confirmed"]=bool(r["family_gate"] and r["holm_p"]<=0.05)

    confirmed=[r["candidate"] for r in rows if r["confirmed"]]
    result={
        "experiment_id":"A11-EXP-088",
        "scope":"adversarial independent replication of exactly the three nominal superbatch survivors; no private-key operations",
        "candidates":rows,
        "holm_family_size":3,
        "confirmed_survivors":confirmed,
        "confirmed_count":len(confirmed),
        "decision_rule":"candidate survives only if its predeclared family replication gate passes AND Holm-adjusted primary confirmatory p<=0.05",
        "next_step_rule":"If zero survive, retire all three nominal superbatch hits and choose a new hypothesis family from public clues/semantic evidence. If one or more survive, localize only the strongest confirmed survivor in the next adaptive stage.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 88 — adversarial replication of superbatch survivors",
        "",
        "**Experiment:** A11-EXP-088",
        "",
        "The 37–86 superbatch produced three nominally interesting results but none survived FDR. This stage tests exactly those three with stricter, independent controls.",
        "",
        "| candidate | original p | primary confirmation p | Holm p | family gate | confirmed |",
        "|:---|---:|---:|---:|:---:|:---:|",
    ]
    for r in rows:
        md.append(f"| {r['candidate']} | {r['original_superbatch_p']:.6f} | {r['primary_confirmation_p']:.6f} | {r['holm_p']:.6f} | {r['family_gate']} | {r['confirmed']} |")
    md += [
        "",
        "## A11-EXP-043 — large-boat vertical projection",
        "",
        f"- nuisance-matched original p: **{r43['matched_p']:.6f}**",
        f"- nuisance-matched lossy p: **{r43['lossy_matched_p']:.6f}**",
        f"- matched same-size windows: **{r43['matched_windows']}**",
        "",
        "## A11-EXP-050 — rightmost reflection",
        "",
        f"- original high-pass p: **{r50['original_full']['highpass']['p']:.6f}**",
        f"- original edge p: **{r50['original_full']['edge']['p']:.6f}**",
        f"- lossy high-pass p: **{r50['lossy_full']['highpass']['p']:.6f}**",
        f"- lossy edge p: **{r50['lossy_full']['edge']['p']:.6f}**",
        f"- fixed half-band grayscale p-values: **{[round(x['p'],6) for x in r50['original_fixed_halves']]}**",
        "",
        "## A11-EXP-061 — small-sail width/gap correlation",
        "",
    ]
    for name,v in r61["independent_stage19_methods"].items():
        md.append(f"- {name}: |r|={v['abs_correlation']:.6f}, exact p=**{v['exact_p']:.6f}**")
    md += [
        f"- Stage-61 detector components matching a Stage-19 stable center within 40px: **{r61['stage61_components_matching_stage19_within_40px']}/5**",
        "",
        f"## Decision: confirmed survivors = **{confirmed}**",
        "",
        "No candidate is promoted merely for having been nominally significant in the superbatch. The next stage must follow the actual confirmation result.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-088",
        "confirmed":confirmed,
        "primary":primary,
        "holm":holm,
    }))

if __name__=="__main__":
    main()
