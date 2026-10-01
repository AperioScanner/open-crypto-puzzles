#!/usr/bin/env python3
"""Stage 9: structure of the anomalous first image row.

A 2021 independent inspection reported 147 non-white pixels in row 0. Earlier tests scanned
the grayscale VALUES of that row, but not the binary POSITION MASK itself or its run/gap
structure. This stage closes that gap with bounded threshold masks and run/position encodings.

No candidate private key is persisted. Exact target matches abort before report persistence.
"""
from __future__ import annotations
import hashlib, json, struct
from pathlib import Path
import numpy as np
from PIL import Image
from Crypto.Hash import keccak
from coincurve import PrivateKey

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage9-first-row-structure"
OUT.mkdir(parents=True,exist_ok=True)
TARGET="ff2142e98e09b5344994f9beb9c56c95506b9f17"
ORDER=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def eth_addr(raw):
    if len(raw)!=32: return None
    n=int.from_bytes(raw,"big")
    if not 0<n<ORDER: return None
    pub=PrivateKey(raw).public_key.format(compressed=False)[1:]
    return keccak.new(digest_bits=256,data=pub).digest()[-20:].hex()

def digests(data):
    yield "sha256",hashlib.sha256(data).digest()
    yield "dsha256",hashlib.sha256(hashlib.sha256(data).digest()).digest()
    yield "keccak256",keccak.new(digest_bits=256,data=data).digest()
    yield "blake2s",hashlib.blake2s(data).digest()

def bit_windows(bits,bitorder):
    bits=np.asarray(bits,dtype=np.uint8)
    for off in range(8):
        usable=((len(bits)-off)//8)*8
        if usable<256: continue
        data=np.packbits(bits[off:off+usable],bitorder=bitorder).tobytes()
        for i in range(len(data)-31):
            yield off+i*8,data[i:i+32]

def runs(mask):
    """Return (value,start,length) runs."""
    m=np.asarray(mask,dtype=np.uint8)
    if not len(m): return []
    out=[]; s=0; cur=int(m[0])
    for i in range(1,len(m)):
        v=int(m[i])
        if v!=cur:
            out.append((cur,s,i-s)); s=i; cur=v
    out.append((cur,s,len(m)-s))
    return out

def serializations(vals):
    outs={}
    for direction,v in (("fwd",list(vals)),("rev",list(reversed(vals)))):
        if all(0<=x<=255 for x in v): outs[f"{direction}:u8"]=bytes(v)
        if all(0<=x<=65535 for x in v):
            outs[f"{direction}:u16be"]=b"".join(struct.pack(">H",x) for x in v)
            outs[f"{direction}:u16le"]=b"".join(struct.pack("<H",x) for x in v)
        for sep in ("",","," ","-",";",":","|"):
            outs[f"{direction}:dec:{repr(sep)}"]=sep.join(str(x) for x in v).encode()
            outs[f"{direction}:hex:{repr(sep)}"]=sep.join(format(x,"x") for x in v).encode()
    seen={}
    for k,v in outs.items(): seen.setdefault(v,k)
    return [(label,data) for data,label in seen.items()]

def direct32(data):
    if len(data)==32: return [("exact",data)]
    if len(data)<32:
        return [("lpad0",b"\0"*(32-len(data))+data),("rpad0",data+b"\0"*(32-len(data))]
    return [("head32",data[:32]),("tail32",data[-32:])]

def main():
    a=np.array(Image.open(SOURCE))
    row=a[0,:,0].astype(np.uint8)
    if len(row)!=1600: raise SystemExit("unexpected width")

    checked=set(); valid=0; near=0; exact=False; family={}
    def check(raw,name):
        nonlocal valid,near,exact
        if len(raw)!=32 or raw in checked: return
        checked.add(raw)
        addr=eth_addr(raw)
        if addr is None: return
        valid+=1; family[name]=family.get(name,0)+1
        if addr.startswith("ff21"): near+=1
        if addr==TARGET: exact=True

    thresholds=[255,254,253,252,251,250,248,245,240,235,230,220,200]
    threshold_stats=[]
    canonical_runs=None

    for thr in thresholds:
        mask=(row < thr).astype(np.uint8)
        rr=runs(mask)
        one_runs=[x for x in rr if x[0]==1]
        zero_runs=[x for x in rr if x[0]==0]
        threshold_stats.append({
          "threshold_lt":thr,"ones":int(mask.sum()),"run_count":len(rr),
          "one_run_count":len(one_runs),"zero_run_count":len(zero_runs),
          "one_run_lengths":[int(x[2]) for x in one_runs],
          "zero_run_lengths":[int(x[2]) for x in zero_runs],
        })
        if thr==255:
            canonical_runs=rr

        for direction,bits0 in (("fwd",mask),("rev",mask[::-1])):
          for invert,bits in (("raw",bits0),("inv",1-bits0)):
            for bitorder in ("big","little"):
                for pos,raw in bit_windows(bits,bitorder):
                    check(raw,f"mask<{thr}:{direction}:{invert}:{bitorder}:window")
                    check(raw[::-1],f"mask<{thr}:{direction}:{invert}:{bitorder}:window:scalar-rev")
                    if exact: break
                if exact: break
            if exact: break
          if exact: break
        if exact: break

        # Whole mask packed and digested.
        for bitorder in ("big","little"):
            data=np.packbits(mask,bitorder=bitorder).tobytes()
            for h,raw in digests(data):
                check(raw,f"mask<{thr}:{bitorder}:{h}")
                check(raw[::-1],f"mask<{thr}:{bitorder}:{h}:scalar-rev")

        # Position, delta, run and gap families.
        pos=np.where(mask==1)[0].astype(int).tolist()
        deltas=[pos[0]]+[pos[i]-pos[i-1] for i in range(1,len(pos))] if pos else []
        one_lengths=[x[2] for x in one_runs]
        zero_lengths=[x[2] for x in zero_runs]
        starts=[x[1] for x in one_runs]
        families={
          "positions":pos,
          "position_deltas":deltas,
          "one_run_lengths":one_lengths,
          "zero_gap_lengths":zero_lengths,
          "one_run_starts":starts,
        }
        for fname,vals in families.items():
            if not vals: continue
            for sname,data in serializations(vals):
                for h,raw in digests(data):
                    check(raw,f"lt{thr}:{fname}:{sname}:{h}")
                    check(raw[::-1],f"lt{thr}:{fname}:{sname}:{h}:scalar-rev")
                for dname,raw in direct32(data):
                    check(raw,f"lt{thr}:{fname}:{sname}:direct:{dname}")
                    check(raw[::-1],f"lt{thr}:{fname}:{sname}:direct:{dname}:scalar-rev")

    if exact:
        print("MATCH_DETECTED")
        raise SystemExit(78)

    # Canonical <255 run structure for human inspection.
    canon_one=[x for x in canonical_runs if x[0]==1]
    canon_zero=[x for x in canonical_runs if x[0]==0]
    canonical={
      "nonwhite_count":int(np.sum(row<255)),
      "nonwhite_positions":np.where(row<255)[0].astype(int).tolist(),
      "one_runs":[{"start":int(s),"length":int(n)} for _,s,n in canon_one],
      "zero_runs":[{"start":int(s),"length":int(n)} for _,s,n in canon_zero],
      "distinct_nonwhite_values":sorted(set(int(x) for x in row[row<255])),
      "nonwhite_value_counts":{str(int(v)):int(np.sum(row==v)) for v in sorted(set(row[row<255]))},
    }

    result={
      "canonical_lt255":canonical,
      "threshold_stats":threshold_stats,
      "unique_32byte_candidates":len(checked),
      "valid_scalars_checked":valid,
      "near_ff21":near,
      "exact_match":False,
      "scope":"binary first-row masks at 13 intensity thresholds; forward/reverse/invert; both bit orders; every 256-bit window; packed-mask hashes; nonwhite positions/deltas/run lengths/gap lengths/run starts serialized and hashed/direct-mapped",
      "security_note":"No candidate private key is persisted."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=["# Stage 9 — first-row position/run structure","",
        f"- Canonical non-white pixels (<255): {canonical['nonwhite_count']}",
        f"- Canonical non-white runs: {len(canon_one)}",
        f"- Distinct non-white grayscale values: {len(canonical['distinct_nonwhite_values'])}",
        f"- Unique 32-byte candidates generated: {len(checked)}",
        f"- Valid secp256k1 scalars checked: {valid}",
        f"- ff21 prefix near-misses: {near}",
        "- Exact target match: false","",
        "## Canonical <255 non-white runs (start:length)","",
        " ".join(f"{x['start']}:{x['length']}" for x in canonical["one_runs"]),"",
        "## Threshold summary","",
        "| threshold | ones | total runs | nonwhite runs |",
        "|---:|---:|---:|---:|"]
    for x in threshold_stats:
        md.append(f"| <{x['threshold_lt']} | {x['ones']} | {x['run_count']} | {x['one_run_count']} |")
    md += ["",
      "This closes a gap left by the earlier first-row value scan: it tests where anomalous pixels occur, not only their grayscale bit values.",
      ""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"bounded-no-match","nonwhite":canonical["nonwhite_count"],"runs":len(canon_one),"unique":len(checked),"valid":valid,"near":near}))

if __name__=="__main__":
    main()
