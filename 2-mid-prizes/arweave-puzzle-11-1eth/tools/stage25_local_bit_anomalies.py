#!/usr/bin/env python3
"""Stage 25: local entropy/anomaly maps for low bitplanes."""
from __future__ import annotations
import json, math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage25-local-bit-anomalies"
OUT.mkdir(parents=True,exist_ok=True)

TILE=64

def entropy01(p):
    if p<=0 or p>=1: return 0.0
    return -p*math.log2(p)-(1-p)*math.log2(1-p)

def robust_z(vals):
    x=np.array(vals,float)
    med=float(np.median(x)); mad=float(np.median(np.abs(x-med)))+1e-9
    return (x-med)/(1.4826*mad),med,mad

def main():
    a=np.array(Image.open(SOURCE))
    channels={"L":a[:,:,0],"A":a[:,:,1]}
    planes=[("L",i) for i in range(4)]+[("A",0)]
    rows=[]
    maps={}
    for ch,bit in planes:
        arr=((channels[ch]>>bit)&1).astype(np.uint8)
        metrics=[]; coords=[]
        H,W=arr.shape
        for y in range(0,H,TILE):
            for x in range(0,W,TILE):
                t=arr[y:min(y+TILE,H),x:min(x+TILE,W)]
                if t.size<256: continue
                p=float(t.mean()); ent=entropy01(p)
                ha=float(np.mean(t[:,:-1]==t[:,1:])) if t.shape[1]>1 else 0
                va=float(np.mean(t[:-1,:]==t[1:,:])) if t.shape[0]>1 else 0
                score_raw=(1-ent)+abs(ha-0.5)+abs(va-0.5)
                metrics.append(score_raw); coords.append((x,y,t.shape[1],t.shape[0],p,ent,ha,va))
        z,med,mad=robust_z(metrics)
        ranked=np.argsort(np.abs(z))[::-1]
        top=[]
        for idx in ranked[:20]:
            x,y,w,h,p,ent,ha,va=coords[idx]
            top.append({"x":x,"y":y,"w":w,"h":h,"p1":p,"entropy":ent,"row_agreement":ha,"col_agreement":va,"robust_z":float(z[idx])})
        rows.append({"channel":ch,"bit":bit,"tile_size":TILE,"median_raw_score":med,"mad_raw_score":mad,"top_anomalies":top})
        # grayscale robust-z map for review
        grid_h=(H+TILE-1)//TILE; grid_w=(W+TILE-1)//TILE
        m=np.zeros((grid_h,grid_w),np.float32)
        for idx,(x,y,*_) in enumerate(coords):
            m[y//TILE,x//TILE]=abs(float(z[idx]))
        q=np.percentile(m,99) if np.any(m) else 1
        vis=np.clip(m/max(q,1e-9)*255,0,255).astype(np.uint8)
        vis=cv2.resize(vis,(W,H),interpolation=cv2.INTER_NEAREST)
        fn=f"{ch}_bit{bit}_anomaly.png"
        cv2.imwrite(str(OUT/fn),vis); maps[f"{ch}{bit}"]=fn
    result={"experiment_id":"A11-EXP-025","scope":"64x64 local low-bit entropy/spatial-agreement anomaly ranking; no payload reconstruction or private-key operations","planes":rows,"maps":maps}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=["# Stage 25 — local low-bit anomaly maps","",
        "**Experiment:** A11-EXP-025","",
        "Each 64×64 tile is ranked by a robust combination of bit entropy deviation and horizontal/vertical neighbor agreement. Diagnostic maps are grayscale robust-z heatmaps.",""]
    for r in rows:
        md += [f"## {r['channel']} bit {r['bit']}","",
               "| x | y | entropy | row agree | col agree | robust |","|---:|---:|---:|---:|---:|---:|"]
        for t in r["top_anomalies"][:10]:
            md.append(f"| {t['x']} | {t['y']} | {t['entropy']:.4f} | {t['row_agreement']:.4f} | {t['col_agreement']:.4f} | {t['robust_z']:.2f} |")
        md.append("")
    md += ["## Interpretation","",
           "Localized anomalies are candidates for later visual/statistical follow-up. Natural edges, flat backgrounds and pasted/anti-aliased objects can also generate strong low-bit anomalies, so location consistency across planes and independent methods is required before promotion.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-025","planes":len(rows)}))

if __name__=="__main__": main()
