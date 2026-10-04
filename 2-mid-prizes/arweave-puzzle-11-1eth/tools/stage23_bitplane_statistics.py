#!/usr/bin/env python3
"""Stage 23: per-bitplane entropy, balance, lag and pair-of-values diagnostics."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage23-bitplane-statistics"
OUT.mkdir(parents=True,exist_ok=True)

def entropy01(p):
    if p<=0 or p>=1: return 0.0
    return -p*math.log2(p)-(1-p)*math.log2(1-p)

def lag_agree(bits,axis):
    if axis==1:
        a,b=bits[:,:-1],bits[:,1:]
    else:
        a,b=bits[:-1,:],bits[1:,:]
    return float(np.mean(a==b)) if a.size else 0.0

def pov_stat(vals):
    h=np.bincount(vals.ravel(),minlength=256).astype(np.float64)
    a=h[0::2]; b=h[1::2]; den=a+b
    valid=den>0
    chi=float(np.sum(((a[valid]-b[valid])**2)/den[valid])) if np.any(valid) else 0.0
    imbalance=float(np.sum(np.abs(a-b))/max(1.0,np.sum(den)))
    return {"pair_chi":chi,"pair_abs_imbalance":imbalance}

def analyze(name,arr):
    rows=[]
    for bit in range(8):
        b=((arr>>bit)&1).astype(np.uint8)
        p=float(b.mean())
        row={"bit":bit,"p1":p,"entropy":entropy01(p),"row_neighbor_agreement":lag_agree(b,1),"col_neighbor_agreement":lag_agree(b,0)}
        rows.append(row)
    return {"name":name,"shape":list(arr.shape),"bitplanes":rows,"pair_of_values":pov_stat(arr)}

def main():
    a=np.array(Image.open(SOURCE))
    L=a[:,:,0]; A=a[:,:,1]
    g=json.loads(GEOM.read_text())
    s=g["large_sailboat"]; y0,y1=g["small_sails_band_y"]
    regions={
      "full_L":L,
      "full_A":A,
      "first48_L":L[:48,:],
      "skyline_L":L[:340,200:],
      "large_sail_L":L[s["y0"]:s["y1"],s["x0"]:s["x1"]],
      "small_sails_band_L":L[y0:y1,:],
      "bottom_water_L":L[650:,:],
    }
    result={"experiment_id":"A11-EXP-023","scope":"descriptive bitplane entropy/balance/spatial agreement and pair-of-values diagnostics only; no private-key operations","regions":[analyze(k,v) for k,v in regions.items()]}
    # synthetic LSB replacement controls for the full grayscale channel
    rng=np.random.default_rng(2301)
    controls=[]
    for rate in (0.25,0.50):
        x=L.copy()
        sel=rng.random(x.shape)<rate
        rnd=rng.integers(0,2,size=x.shape,dtype=np.uint8)
        x[sel]=(x[sel]&0xFE)|rnd[sel]
        controls.append({"lsb_replacement_rate":rate,"analysis":analyze("synthetic",x)})
    result["synthetic_controls"]=controls
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=["# Stage 23 — bitplane statistical steganalysis","",
        "**Experiment:** A11-EXP-023","",
        "Descriptive statistics only: bit balance, entropy, horizontal/vertical neighbor agreement, and even/odd pair-of-values imbalance. Synthetic LSB-replacement controls are included.",""]
    for reg in result["regions"]:
        md += [f"## {reg['name']}","",f"- pair abs imbalance: {reg['pair_of_values']['pair_abs_imbalance']:.6f}",f"- pair chi: {reg['pair_of_values']['pair_chi']:.2f}","",
               "| bit | p(1) | entropy | row agree | col agree |","|---:|---:|---:|---:|---:|"]
        for x in reg["bitplanes"]:
            md.append(f"| {x['bit']} | {x['p1']:.6f} | {x['entropy']:.6f} | {x['row_neighbor_agreement']:.6f} | {x['col_neighbor_agreement']:.6f} |")
        md.append("")
    md += ["## Interpretation","",
           "An LSB payload would often push low-bit balance/entropy and pair-of-values behavior toward synthetic replacement controls, but natural image processing can create similar effects. This stage therefore ranks statistical anomalies; it does not infer or reconstruct hidden key material.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-023","regions":len(result["regions"])}))

if __name__=="__main__": main()
