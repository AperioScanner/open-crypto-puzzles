#!/usr/bin/env python3
"""Stage 30: semantic-source decomposition of the Stage-29 traversal anomaly.

Non-cryptographic. The fixed source-x clusters promoted/localized in Stage 29 are split
by semantic y bands and by foreground/background pixels. The goal is to determine whether
the anomaly follows ordinary drawn objects / blank background or persists independently.
"""
from __future__ import annotations
import json, zlib
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
RUN29=ROOT/"analysis"/"runs"/"stage29-traversal-localization"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage30-traversal-source-decomposition"
OUT.mkdir(parents=True,exist_ok=True)

BIT=0
FOREGROUND_THR=250

def pack_bits(vals,bit=BIT,bitorder="big"):
    bits=((vals>>bit)&1).astype(np.uint8)
    n=(len(bits)//8)*8
    if n==0:
        return b""
    return np.packbits(bits[:n],bitorder=bitorder).tobytes()

def metrics(data):
    if not data:
        return {"bytes":0,"printable_fraction":0.0,"longest_printable_run":0,"zlib_ratio":None}
    a=np.frombuffer(data,dtype=np.uint8)
    printable=float(np.mean((a==9)|(a==10)|(a==13)|((a>=32)&(a<=126))))
    best=cur=0
    for x in data:
        if x in (9,10,13) or 32<=x<=126:
            cur+=1; best=max(best,cur)
        else:
            cur=0
    return {"bytes":len(data),"printable_fraction":printable,"longest_printable_run":best,"zlib_ratio":len(zlib.compress(data,9))/len(data)}

def serp_columns(region):
    # Emulate the source-space equivalent of the canonical Stage-29 family:
    # column-wise scan with alternating vertical direction.
    cols=[]
    H,W=region.shape
    for x in range(W-1,-1,-1):
        col=region[:,x]
        if ((W-1-x) % 2)==1:
            col=col[::-1]
        cols.append(col)
    return np.concatenate(cols) if cols else np.array([],dtype=np.uint8)

def region_metrics(arr,x0,x1,y0,y1):
    r=arr[y0:y1,x0:x1]
    seq=serp_columns(r)
    fg=seq[seq<FOREGROUND_THR]
    bg=seq[seq>=FOREGROUND_THR]
    return {
      "bbox":[x0,y0,x1,y1],
      "all":metrics(pack_bits(seq)),
      "foreground":metrics(pack_bits(fg)),
      "background":metrics(pack_bits(bg)),
      "foreground_fraction":float(len(fg)/max(1,len(seq))),
    }

def main():
    img=np.array(Image.open(SOURCE))
    L=img[:,:,0]
    H,W=L.shape
    s29=json.loads(RUN29.read_text())

    # Fixed from Stage 29 before this test:
    # contiguous high-printability cluster spans source x≈176..385;
    # contiguous high-compressibility cluster spans x≈769..948;
    # extreme left blank-margin control spans x≈0..58.
    clusters={
      "printable_cluster":(176,385),
      "compressible_cluster":(769,948),
      "left_margin_control":(0,58),
    }
    bands={
      "upper_skyline":(0,320),
      "boats_mid":(320,620),
      "lower_water":(620,H),
      "full_height":(0,H),
    }

    rows=[]
    for cname,(x0,x1) in clusters.items():
        for bname,(y0,y1) in bands.items():
            rows.append({"cluster":cname,"band":bname,**region_metrics(L,x0,x1,y0,y1)})

    # Cross-bitplane check on the full-height source clusters.
    bit_rows=[]
    for cname,(x0,x1) in clusters.items():
        r=L[:,x0:x1]
        seq=serp_columns(r)
        for bit in range(4):
            bit_rows.append({"cluster":cname,"bit":bit,**metrics(pack_bits(seq,bit=bit))})

    result={
      "experiment_id":"A11-EXP-030",
      "scope":"semantic y-band and foreground/background decomposition of fixed Stage-29 source-x clusters; no payload reconstruction or private-key operations",
      "foreground_threshold":FOREGROUND_THR,
      "clusters":clusters,
      "bands":bands,
      "region_metrics":rows,
      "cross_bitplane_full_height":bit_rows,
      "decision_rule":"If printable/compressibility extremes are concentrated in semantic object/background subsets rather than persisting across bands and pixel classes, favor ordinary image structure over a hidden LSB carrier.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=["# Stage 30 — semantic source decomposition of traversal anomaly","",
        "**Experiment:** A11-EXP-030","",
        f"Foreground threshold: gray < {FOREGROUND_THR}. Fixed source-x clusters come from Stage 29; no new region was selected after seeing Stage-30 values.","",
        "| cluster | band | fg fraction | all printable | all zlib | fg printable | fg zlib | bg printable | bg zlib |",
        "|:---|:---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        def f(v):
            return "NA" if v is None else f"{v:.4f}"
        md.append(
            f"| {r['cluster']} | {r['band']} | {r['foreground_fraction']:.3f} | "
            f"{r['all']['printable_fraction']:.4f} | {f(r['all']['zlib_ratio'])} | "
            f"{r['foreground']['printable_fraction']:.4f} | {f(r['foreground']['zlib_ratio'])} | "
            f"{r['background']['printable_fraction']:.4f} | {f(r['background']['zlib_ratio'])} |"
        )
    md += ["","## Full-height cross-bitplane comparison","",
           "| cluster | bit | printable | run | zlib |","|:---|---:|---:|---:|---:|"]
    for r in bit_rows:
        md.append(f"| {r['cluster']} | {r['bit']} | {r['printable_fraction']:.4f} | {r['longest_printable_run']} | {r['zlib_ratio']:.4f} |")
    md += ["","## Interpretation","",
           "If the Stage-29 anomaly follows specific drawn-object bands or blank-background strips, it is more parsimoniously explained by natural image structure. Persistence across semantic bands, foreground/background classes, and uniquely in bit 0 would strengthen a carrier hypothesis.",
           ""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-030","regions":len(rows),"bit_rows":len(bit_rows)}))

if __name__=="__main__":
    main()
