#!/usr/bin/env python3
"""Stage 24: RS-style LSB diagnostics with synthetic controls."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage24-rs-lsb"
OUT.mkdir(parents=True,exist_ok=True)

MASK=(1,0,1,0)

def discr(g):
    return np.abs(np.diff(g.astype(np.int16),axis=1)).sum(axis=1)

def flip_pos(x,m):
    y=x.copy()
    for i,v in enumerate(m):
        if not v: continue
        z=y[:,i]
        y[:,i]=np.where((z&1)==0,np.minimum(z+1,255),z-1)
    return y

def flip_neg(x,m):
    y=x.copy()
    for i,v in enumerate(m):
        if not v: continue
        z=y[:,i]
        y[:,i]=np.where((z&1)==0,np.maximum(z-1,0),np.minimum(z+1,255))
    return y

def rs(arr):
    flat=arr.ravel()
    n=(len(flat)//4)*4
    g=flat[:n].reshape(-1,4)
    f0=discr(g)
    fp=discr(flip_pos(g,MASK))
    fn=discr(flip_neg(g,MASK))
    rp=int(np.sum(fp>f0)); sp=int(np.sum(fp<f0))
    rn=int(np.sum(fn>f0)); sn=int(np.sum(fn<f0))
    groups=len(g)
    return {"groups":groups,"R_pos":rp,"S_pos":sp,"R_neg":rn,"S_neg":sn,
            "RminusS_pos":(rp-sp)/groups,"RminusS_neg":(rn-sn)/groups,
            "symmetry_gap":abs((rp-sp)-(rn-sn))/groups}

def replace_lsb(arr,rate,rng):
    x=arr.copy()
    sel=rng.random(x.shape)<rate
    rnd=rng.integers(0,2,size=x.shape,dtype=np.uint8)
    x[sel]=(x[sel]&0xFE)|rnd[sel]
    return x

def main():
    a=np.array(Image.open(SOURCE))
    L=a[:,:,0]; A=a[:,:,1]
    rng=np.random.default_rng(2401)
    result={"experiment_id":"A11-EXP-024","scope":"RS-style LSB diagnostics only; no payload reconstruction or private-key operations","channels":{}}
    for name,arr in (("L",L),("A",A)):
        entry={"original":rs(arr),"synthetic_controls":[]}
        for rate in (0.10,0.25,0.50,1.0):
            entry["synthetic_controls"].append({"lsb_replacement_rate":rate,"rs":rs(replace_lsb(arr,rate,rng))})
        result["channels"][name]=entry
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=["# Stage 24 — RS-style LSB diagnostics","",
        "**Experiment:** A11-EXP-024","",
        "The statistic compares regular/singular group asymmetry under positive and negative LSB flips. Synthetic LSB-replacement controls calibrate direction and scale.",""]
    for name,e in result["channels"].items():
        o=e["original"]
        md += [f"## {name} channel","",f"- original symmetry gap: **{o['symmetry_gap']:.6f}**",
               f"- original R-S positive: {o['RminusS_pos']:.6f}",
               f"- original R-S negative: {o['RminusS_neg']:.6f}","",
               "| synthetic LSB replacement | symmetry gap | R-S pos | R-S neg |","|---:|---:|---:|---:|"]
        for c in e["synthetic_controls"]:
            r=c["rs"]
            md.append(f"| {c['lsb_replacement_rate']:.2f} | {r['symmetry_gap']:.6f} | {r['RminusS_pos']:.6f} | {r['RminusS_neg']:.6f} |")
        md.append("")
    md += ["## Interpretation","",
           "Similarity to a synthetic replacement control is evidence only of LSB statistical behavior, not proof of an embedded message. Strong differences from all controls weaken simple global LSB replacement as a carrier model.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-024","L_gap":result["channels"]["L"]["original"]["symmetry_gap"],"A_gap":result["channels"]["A"]["original"]["symmetry_gap"]}))

if __name__=="__main__": main()
