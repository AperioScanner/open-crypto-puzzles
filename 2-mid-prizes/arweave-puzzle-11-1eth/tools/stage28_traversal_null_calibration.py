#!/usr/bin/env python3
"""Stage 28: null-calibrate Stage-27 traversal anomalies with block-shuffled surrogates.

Non-cryptographic. Tests whether the already-observed text-like L-bit0 traversals are
more exceptional than expected from the image's biased, locally correlated bitplane.
Also rescans with multi-byte file signatures only.
"""
from __future__ import annotations
import json, zlib
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
RUN27=ROOT/"analysis"/"runs"/"stage27-traversal-byte-diagnostics"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage28-traversal-null-calibration"
OUT.mkdir(parents=True,exist_ok=True)

BLOCK=32
N_SURR=100
MAGICS=[
    ("PNG",b"\x89PNG\r\n\x1a\n"),
    ("ZIP",b"PK\x03\x04"),
    ("GZIP",b"\x1f\x8b\x08"),
    ("PDF",b"%PDF-"),
    ("ELF",b"\x7fELF"),
    ("GIF87a",b"GIF87a"),
    ("GIF89a",b"GIF89a"),
    ("SQLITE",b"SQLite format 3\x00"),
    ("RAR",b"Rar!\x1a\x07"),
    ("7Z",b"7z\xbc\xaf\x27\x1c"),
]

def orient(arr,k,flip):
    x=np.rot90(arr,k)
    return np.fliplr(x) if flip else x

def traverse(arr,mode):
    if mode=="row": return arr.ravel()
    if mode=="col": return arr.T.ravel()
    if mode=="row_serp":
        x=arr.copy(); x[1::2]=x[1::2,::-1]; return x.ravel()
    if mode=="col_serp":
        x=arr.T.copy(); x[1::2]=x[1::2,::-1]; return x.ravel()
    raise ValueError(mode)

def pack(arr,bits,traversal,bitorder):
    pix=traverse(arr,traversal)
    b=np.stack([((pix>>q)&1) for q in bits],axis=1).ravel().astype(np.uint8)
    n=(len(b)//8)*8
    return np.packbits(b[:n],bitorder=bitorder).tobytes()

def metrics(data):
    a=np.frombuffer(data,dtype=np.uint8)
    printable=float(np.mean((a==9)|(a==10)|(a==13)|((a>=32)&(a<=126)))) if len(a) else 0.0
    best=cur=0
    for x in data:
        if x in (9,10,13) or 32<=x<=126:
            cur+=1; best=max(best,cur)
        else: cur=0
    ratio=len(zlib.compress(data,9))/max(1,len(data))
    hits=[]
    for name,sig in MAGICS:
        pos=data.find(sig)
        if pos>=0: hits.append({"name":name,"offset":pos})
    return {"printable_fraction":printable,"longest_printable_run":best,"zlib_ratio":ratio,"magic_hits":hits}

def apply_cfg(arr,cfg):
    x=orient(arr,int(cfg["rot90"]),bool(cfg["flip_lr"]))
    return pack(x,tuple(cfg["bits"]),cfg["traversal"],cfg["bitorder"])

def block_shuffle(arr,rng):
    out=arr.copy()
    H,W=arr.shape
    hh=(H//BLOCK)*BLOCK; ww=(W//BLOCK)*BLOCK
    tiles=[]
    for y in range(0,hh,BLOCK):
        for x in range(0,ww,BLOCK):
            tiles.append(arr[y:y+BLOCK,x:x+BLOCK].copy())
    perm=rng.permutation(len(tiles))
    k=0
    for y in range(0,hh,BLOCK):
        for x in range(0,ww,BLOCK):
            out[y:y+BLOCK,x:x+BLOCK]=tiles[int(perm[k])]; k+=1
    return out

def cfg_key(c):
    return (c["channel"],c["rot90"],c["flip_lr"],c["traversal"],c["selection"],c["bitorder"])

def main():
    stage27=json.loads(RUN27.read_text())
    # Stage 27's strongest text-like streams are the fixed family under review.
    candidates=[]
    seen=set()
    for c in stage27["top_printable"][:20]:
        k=cfg_key(c)
        if k in seen or c["channel"]!="L": continue
        seen.add(k); candidates.append(c)
    candidates=candidates[:12]

    img=np.array(Image.open(SOURCE))
    L=img[:,:,0]
    observed=[]
    for cfg in candidates:
        m=metrics(apply_cfg(L,cfg))
        observed.append({"config":{k:cfg[k] for k in ("channel","rot90","flip_lr","traversal","selection","bits","bitorder")},"metrics":m})
    obs_max_print=max(x["metrics"]["printable_fraction"] for x in observed)
    obs_max_run=max(x["metrics"]["longest_printable_run"] for x in observed)
    obs_min_zlib=min(x["metrics"]["zlib_ratio"] for x in observed)
    obs_magic=sum(bool(x["metrics"]["magic_hits"]) for x in observed)

    rng=np.random.default_rng(2801)
    null=[]
    for i in range(N_SURR):
        s=block_shuffle(L,rng)
        ms=[metrics(apply_cfg(s,cfg)) for cfg in candidates]
        null.append({
            "max_printable":max(x["printable_fraction"] for x in ms),
            "max_run":max(x["longest_printable_run"] for x in ms),
            "min_zlib":min(x["zlib_ratio"] for x in ms),
            "magic_streams":sum(bool(x["magic_hits"]) for x in ms),
        })
    def upper(key,obs):
        return (1+sum(x[key]>=obs for x in null))/(1+len(null))
    def lower(key,obs):
        return (1+sum(x[key]<=obs for x in null))/(1+len(null))

    p_print=upper("max_printable",obs_max_print)
    p_run=upper("max_run",obs_max_run)
    p_zlib=lower("min_zlib",obs_min_zlib)
    p_magic=upper("magic_streams",obs_magic)
    promoted=sum(p<0.025 for p in (p_print,p_run,p_zlib))>=2 or (obs_magic>0 and p_magic<0.025)

    result={
      "experiment_id":"A11-EXP-028",
      "scope":"null calibration of Stage-27 top printable L-bit0 traversal family using 32x32 block-shuffled surrogates; multi-byte signatures only; no secret reconstruction",
      "candidate_streams":len(candidates),
      "surrogates":N_SURR,
      "observed":{"max_printable":obs_max_print,"max_run":obs_max_run,"min_zlib":obs_min_zlib,"magic_streams":obs_magic},
      "empirical_p":{"max_printable_upper":p_print,"max_run_upper":p_run,"min_zlib_lower":p_zlib,"magic_streams_upper":p_magic},
      "promoted":promoted,
      "observed_streams":observed,
      "null_summary":{
        "max_printable_median":float(np.median([x["max_printable"] for x in null])),
        "max_run_median":float(np.median([x["max_run"] for x in null])),
        "min_zlib_median":float(np.median([x["min_zlib"] for x in null])),
        "magic_streams_max":int(max(x["magic_streams"] for x in null)),
      }
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=["# Stage 28 — traversal anomaly null calibration","",
        "**Experiment:** A11-EXP-028","",
        f"- Fixed Stage-27 candidate streams: **{len(candidates)}**",
        f"- 32×32 block-shuffled surrogates: **{N_SURR}**",
        f"- Observed max printable fraction: **{obs_max_print:.6f}** (empirical p={p_print:.4f})",
        f"- Observed max printable run: **{obs_max_run}** (p={p_run:.4f})",
        f"- Observed min zlib ratio: **{obs_min_zlib:.6f}** (p={p_zlib:.4f})",
        f"- Observed streams with specific multi-byte magic: **{obs_magic}** (p={p_magic:.4f})",
        f"- Promotion rule satisfied: **{promoted}**","",
        "## Interpretation",""]
    if promoted:
        md.append("At least two independent traversal metrics are unusually extreme relative to matched block-shuffled surrogates, or a specific multi-byte signature is exceptional. The next stage should localize and reproduce that traversal anomaly.")
    else:
        md.append("The Stage-27 text/compressibility anomalies are not exceptional enough under matched block-shuffled surrogates. Retire generic traversal-text hunting and choose the next hypothesis from the spatial/statistical evidence in Stages 23–26.")
    md += ["","One-byte JSON markers from Stage 27 are explicitly excluded because they generate chance hits.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-028","promoted":promoted,"p_print":p_print,"p_run":p_run,"p_zlib":p_zlib,"p_magic":p_magic}))

if __name__=="__main__": main()
