#!/usr/bin/env python3
"""Stage 29: localize and reproduce the Stage-28 L-bit0 traversal anomaly.

Non-cryptographic. Uses one fixed canonical member of the Stage-28 promoted equivalence
family, localizes printable/compressibility effects in fixed byte windows, calibrates the
max/min window statistics with block-shuffled surrogates, and compares the same traversal
across grayscale bitplanes 0..7.
"""
from __future__ import annotations
import json, zlib
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage29-traversal-localization"
OUT.mkdir(parents=True,exist_ok=True)

BLOCK=32
WINDOW_BYTES=4096
N_SURR=100

CFG={
    "rot90":1,
    "flip_lr":True,
    "traversal":"row_serp",
    "bitorder":"big",
}

def orient(arr):
    x=np.rot90(arr,CFG["rot90"])
    return np.fliplr(x) if CFG["flip_lr"] else x

def traverse(arr):
    mode=CFG["traversal"]
    if mode=="row":
        return arr.ravel()
    if mode=="col":
        return arr.T.ravel()
    if mode=="row_serp":
        x=arr.copy()
        x[1::2]=x[1::2,::-1]
        return x.ravel()
    if mode=="col_serp":
        x=arr.T.copy()
        x[1::2]=x[1::2,::-1]
        return x.ravel()
    raise ValueError(mode)

def pack_bit(arr,bit):
    x=orient(arr)
    pix=traverse(x)
    bits=((pix>>bit)&1).astype(np.uint8)
    n=(len(bits)//8)*8
    return np.packbits(bits[:n],bitorder=CFG["bitorder"]).tobytes()

def metrics(data):
    a=np.frombuffer(data,dtype=np.uint8)
    printable=float(np.mean((a==9)|(a==10)|(a==13)|((a>=32)&(a<=126)))) if len(a) else 0.0
    best=cur=0
    for x in data:
        if x in (9,10,13) or 32<=x<=126:
            cur+=1; best=max(best,cur)
        else:
            cur=0
    ratio=len(zlib.compress(data,9))/max(1,len(data))
    return {"printable_fraction":printable,"longest_printable_run":best,"zlib_ratio":ratio}

def window_metrics(data):
    out=[]
    for start in range(0,len(data),WINDOW_BYTES):
        chunk=data[start:start+WINDOW_BYTES]
        if len(chunk)<WINDOW_BYTES//2:
            continue
        out.append({"start_byte":start,"end_byte":start+len(chunk),**metrics(chunk)})
    return out

def oriented_coords(H,W):
    yy,xx=np.indices((H,W))
    xo=orient(xx)
    yo=orient(yy)
    return traverse(xo),traverse(yo)

def attach_bbox(windows,xseq,yseq):
    for w in windows:
        p0=w["start_byte"]*8
        p1=min(len(xseq),w["end_byte"]*8)
        xs=xseq[p0:p1]; ys=yseq[p0:p1]
        w["source_bbox"]=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
        w["source_center"]=[float(xs.mean()),float(ys.mean())]
    return windows

def block_shuffle(arr,rng):
    out=arr.copy()
    H,W=arr.shape
    hh=(H//BLOCK)*BLOCK
    ww=(W//BLOCK)*BLOCK
    tiles=[]
    for y in range(0,hh,BLOCK):
        for x in range(0,ww,BLOCK):
            tiles.append(arr[y:y+BLOCK,x:x+BLOCK].copy())
    perm=rng.permutation(len(tiles))
    k=0
    for y in range(0,hh,BLOCK):
        for x in range(0,ww,BLOCK):
            out[y:y+BLOCK,x:x+BLOCK]=tiles[int(perm[k])]
            k+=1
    return out

def upper(null,obs):
    return (1+sum(x>=obs for x in null))/(1+len(null))

def lower(null,obs):
    return (1+sum(x<=obs for x in null))/(1+len(null))

def main():
    img=np.array(Image.open(SOURCE))
    L=img[:,:,0]
    H,W=L.shape
    xseq,yseq=oriented_coords(H,W)

    streams={}
    for bit in range(8):
        data=pack_bit(L,bit)
        streams[str(bit)]={"global":metrics(data),"windows":attach_bbox(window_metrics(data),xseq,yseq)}

    b0=streams["0"]
    obs_max_print=max(w["printable_fraction"] for w in b0["windows"])
    obs_min_zlib=min(w["zlib_ratio"] for w in b0["windows"])
    obs_max_run=max(w["longest_printable_run"] for w in b0["windows"])

    rng=np.random.default_rng(2901)
    null_max_print=[]
    null_min_zlib=[]
    null_max_run=[]
    for _ in range(N_SURR):
        s=block_shuffle(L,rng)
        wm=window_metrics(pack_bit(s,0))
        null_max_print.append(max(w["printable_fraction"] for w in wm))
        null_min_zlib.append(min(w["zlib_ratio"] for w in wm))
        null_max_run.append(max(w["longest_printable_run"] for w in wm))

    p_print=upper(null_max_print,obs_max_print)
    p_zlib=lower(null_min_zlib,obs_min_zlib)
    p_run=upper(null_max_run,obs_max_run)

    top_print=sorted(b0["windows"],key=lambda w:w["printable_fraction"],reverse=True)[:10]
    top_zlib=sorted(b0["windows"],key=lambda w:w["zlib_ratio"])[:10]

    bitplane_rank_print=sorted(
        [{"bit":int(bit),**entry["global"]} for bit,entry in streams.items()],
        key=lambda x:x["printable_fraction"],reverse=True
    )
    bitplane_rank_zlib=sorted(
        [{"bit":int(bit),**entry["global"]} for bit,entry in streams.items()],
        key=lambda x:x["zlib_ratio"]
    )

    result={
      "experiment_id":"A11-EXP-029",
      "scope":"localization and cross-bitplane reproduction of the Stage-28 canonical L-bit0 traversal anomaly; no payload reconstruction or private-key operations",
      "canonical_config":CFG,
      "window_bytes":WINDOW_BYTES,
      "surrogates":N_SURR,
      "b0_global":b0["global"],
      "b0_familywise_observed":{"max_printable":obs_max_print,"min_zlib":obs_min_zlib,"max_run":obs_max_run},
      "b0_familywise_empirical_p":{"max_printable_upper":p_print,"min_zlib_lower":p_zlib,"max_run_upper":p_run},
      "top_printable_windows":top_print,
      "top_compressible_windows":top_zlib,
      "bitplane_global_rank_by_printability":bitplane_rank_print,
      "bitplane_global_rank_by_compressibility":bitplane_rank_zlib,
      "all_bitplanes":streams,
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=["# Stage 29 — localize and reproduce Stage-28 traversal anomaly","",
        "**Experiment:** A11-EXP-029","",
        f"Canonical fixed traversal: {CFG}.",
        f"Window size: {WINDOW_BYTES} bytes; block-shuffled surrogates: {N_SURR}.","",
        "## Familywise localization calibration","",
        f"- observed max window printable fraction: **{obs_max_print:.6f}** (p={p_print:.4f})",
        f"- observed min window zlib ratio: **{obs_min_zlib:.6f}** (p={p_zlib:.4f})",
        f"- observed max printable run: **{obs_max_run}** (p={p_run:.4f})","",
        "## Top printable windows","",
        "| start byte | printable | run | zlib | source bbox |",
        "|---:|---:|---:|---:|:---|"]
    for w in top_print:
        md.append(f"| {w['start_byte']} | {w['printable_fraction']:.4f} | {w['longest_printable_run']} | {w['zlib_ratio']:.4f} | {w['source_bbox']} |")
    md += ["","## Top compressible windows","",
           "| start byte | printable | run | zlib | source bbox |",
           "|---:|---:|---:|---:|:---|"]
    for w in top_zlib:
        md.append(f"| {w['start_byte']} | {w['printable_fraction']:.4f} | {w['longest_printable_run']} | {w['zlib_ratio']:.4f} | {w['source_bbox']} |")
    md += ["","## Same traversal across grayscale bitplanes","",
           "| bit | printable | run | zlib |",
           "|---:|---:|---:|---:|"]
    for r in sorted(bitplane_rank_print,key=lambda x:x["bit"]):
        md.append(f"| {r['bit']} | {r['printable_fraction']:.4f} | {r['longest_printable_run']} | {r['zlib_ratio']:.4f} |")
    md += ["","## Interpretation","",
           "If the familywise window anomaly remains significant and is spatially concentrated, the next stage should inspect those source regions with matched local controls. If the same behavior appears equally or more strongly in higher bitplanes, that favors ordinary image structure over an LSB-specific carrier.",
           ""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
      "status":"ok",
      "experiment_id":"A11-EXP-029",
      "p_print":p_print,
      "p_zlib":p_zlib,
      "p_run":p_run,
      "b0_print_rank":[x["bit"] for x in bitplane_rank_print].index(0)+1,
      "b0_zlib_rank":[x["bit"] for x in bitplane_rank_zlib].index(0)+1
    }))

if __name__=="__main__":
    main()
