#!/usr/bin/env python3
"""Stage 27: traversal-order byte diagnostics without secret reconstruction."""
from __future__ import annotations
import json, math, zlib
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage27-traversal-byte-diagnostics"
OUT.mkdir(parents=True,exist_ok=True)

MAGICS=[
    ("PNG",b"\x89PNG\r\n\x1a\n"),
    ("ZIP",b"PK\x03\x04"),
    ("GZIP",b"\x1f\x8b"),
    ("PDF",b"%PDF"),
    ("ELF",b"\x7fELF"),
    ("JSON_OBJ",b"{"),
    ("JSON_ARR",b"["),
]

def entropy_bytes(data):
    if not data: return 0.0
    h=np.bincount(np.frombuffer(data,dtype=np.uint8),minlength=256).astype(np.float64)
    p=h[h>0]/h.sum()
    return float(-(p*np.log2(p)).sum())

def printable_fraction(data):
    if not data: return 0.0
    a=np.frombuffer(data,dtype=np.uint8)
    return float(np.mean((a==9)|(a==10)|(a==13)|((a>=32)&(a<=126))))

def longest_printable_run(data):
    best=cur=0
    for b in data:
        if b in (9,10,13) or 32<=b<=126:
            cur+=1; best=max(best,cur)
        else: cur=0
    return best

def magic_hits(data):
    hits=[]
    for name,sig in MAGICS:
        pos=data.find(sig)
        if pos>=0:
            hits.append({"name":name,"offset":pos})
    return hits

def stats(data):
    if not data: return {}
    comp=zlib.compress(data,9)
    return {
      "bytes":len(data),
      "byte_entropy":entropy_bytes(data),
      "printable_fraction":printable_fraction(data),
      "longest_printable_run":longest_printable_run(data),
      "zero_fraction":data.count(0)/len(data),
      "ff_fraction":data.count(255)/len(data),
      "zlib_ratio":len(comp)/len(data),
      "magic_hits":magic_hits(data),
    }

def traverse(arr,mode):
    if mode=="row": return arr.ravel()
    if mode=="col": return arr.T.ravel()
    if mode=="row_serp":
        x=arr.copy()
        x[1::2]=x[1::2,::-1]
        return x.ravel()
    if mode=="col_serp":
        x=arr.T.copy()
        x[1::2]=x[1::2,::-1]
        return x.ravel()
    raise ValueError(mode)

def orient(arr,k,flip):
    x=np.rot90(arr,k)
    if flip: x=np.fliplr(x)
    return x

def bit_stream(arr,sel):
    bits=np.stack([((arr>>b)&1) for b in sel],axis=-1).reshape(arr.shape[0],arr.shape[1],-1)
    return bits

def pack_selected(arr,sel,traversal,bitorder):
    # Traverse pixels first, then selected bits within each pixel in sel order.
    pix=traverse(arr,traversal)
    bits=np.stack([((pix>>b)&1) for b in sel],axis=1).ravel().astype(np.uint8)
    n=(len(bits)//8)*8
    return np.packbits(bits[:n],bitorder=bitorder).tobytes()

def main():
    a=np.array(Image.open(SOURCE))
    channels={"L":a[:,:,0],"A":a[:,:,1]}
    selections={"b0":(0,),"b1":(1,),"b2":(2,),"b3":(3,),"low2":(0,1),"low3":(0,1,2),"low4":(0,1,2,3)}
    rows=[]
    for ch,arr in channels.items():
        for k in range(4):
            for flip in (False,True):
                x=orient(arr,k,flip)
                for trav in ("row","col","row_serp","col_serp"):
                    for name,sel in selections.items():
                        if ch=="A" and name not in ("b0","b1","b2","b3","low2"):
                            continue
                        for bitorder in ("big","little"):
                            data=pack_selected(x,sel,trav,bitorder)
                            s=stats(data)
                            rows.append({"channel":ch,"rot90":k,"flip_lr":flip,"traversal":trav,"selection":name,"bits":list(sel),"bitorder":bitorder,**s})
    # synthetic control: known benign text encoded into an LSB stream to verify printable/magic sensitivity.
    msg=(b"STEGO-CONTROL:HELLO-WORLD\n"*128)
    carrier=np.zeros(len(msg)*8,dtype=np.uint8)
    rawbits=np.unpackbits(np.frombuffer(msg,dtype=np.uint8),bitorder="big")
    carrier[:len(rawbits)]=rawbits
    ctrl=np.packbits(carrier,bitorder="big").tobytes()
    control=stats(ctrl)

    ranked_print=sorted(rows,key=lambda r:(-r["printable_fraction"],-r["longest_printable_run"]))[:20]
    ranked_comp=sorted(rows,key=lambda r:r["zlib_ratio"])[:20]
    with_magic=[r for r in rows if r["magic_hits"]]
    result={"experiment_id":"A11-EXP-027","scope":"traversal-order byte statistics only; no candidate-key reconstruction or wallet verification","tested_streams":len(rows),"top_printable":ranked_print,"top_compressible":ranked_comp,"magic_hits":with_magic,"synthetic_text_control":control}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=["# Stage 27 — traversal-order byte diagnostics","",
        "**Experiment:** A11-EXP-027","",
        f"Streams tested: **{len(rows)}** across L/A channels, 8 orientations, row/column/serpentine traversals, selected low bitplanes and both byte bit orders.","",
        "## Most printable streams","",
        "| ch | rot | flip | traversal | selection | order | printable | longest run | entropy | zlib ratio |",
        "|:---:|---:|:---:|:---|:---|:---:|---:|---:|---:|---:|"]
    for r in ranked_print[:12]:
        md.append(f"| {r['channel']} | {r['rot90']} | {r['flip_lr']} | {r['traversal']} | {r['selection']} | {r['bitorder']} | {r['printable_fraction']:.4f} | {r['longest_printable_run']} | {r['byte_entropy']:.4f} | {r['zlib_ratio']:.4f} |")
    md += ["","## Most compressible streams","",
           "| ch | rot | flip | traversal | selection | order | zlib ratio | printable | entropy |",
           "|:---:|---:|:---:|:---|:---|:---:|---:|---:|---:|"]
    for r in ranked_comp[:12]:
        md.append(f"| {r['channel']} | {r['rot90']} | {r['flip_lr']} | {r['traversal']} | {r['selection']} | {r['bitorder']} | {r['zlib_ratio']:.4f} | {r['printable_fraction']:.4f} | {r['byte_entropy']:.4f} |")
    md += ["",f"Magic-signature-bearing streams: **{len(with_magic)}**","",
           "## Interpretation","",
           "This stage searches for traversal orders that become conspicuously text-like, compressible, or file-signature-like without interpreting any 32-byte material as a secret. Any anomaly must be reproduced and localized before promotion.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-027","streams":len(rows),"magic_streams":len(with_magic),"best_printable":ranked_print[0]["printable_fraction"],"best_zlib":ranked_comp[0]["zlib_ratio"]}))

if __name__=="__main__": main()
