#!/usr/bin/env python3
"""Stage 8: orientation-guided skyline geometry.

The 12 building hatch orientations form the robust visual marker HHVV HHVH HHHV = 0x321
when H=0,V=1. A natural non-arbitrary follow-up is to let the hatch direction select the
matching building dimension: horizontal hatch -> width, vertical hatch -> height (and the
inverse as a control). This stage tests bounded serializations/transforms of that 12-value
sequence against the Ethereum target.

No candidate private key is persisted. Exact matches abort before result persistence.
"""
from __future__ import annotations
import hashlib, json, struct
from pathlib import Path
from itertools import product
from Crypto.Hash import keccak
from coincurve import PrivateKey

ROOT=Path(__file__).resolve().parents[1]
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage8-orientation-geometry"
OUT.mkdir(parents=True,exist_ok=True)
TARGET="ff2142e98e09b5344994f9beb9c56c95506b9f17"
ORDER=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
ORIENT="HHVVHHVHHHHV"

# Community transcription in HomelessPhD/PZL11, deliberately approximate multiples of 5/10.
COMM_HEIGHT=[100,190,90,165,240,55,180,160,90,160,100,190]
COMM_WIDTH =[115,90,100,170,100,100,150,110,110,100,70,50]

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

def serializations(vals):
    # Deduplicated, bounded representation family.
    outs={}
    seqs={"fwd":vals,"rev":list(reversed(vals))}
    for sname,v in seqs.items():
        # Integer byte encodings where range permits.
        if all(0 <= x <= 255 for x in v):
            outs[f"{sname}:u8"]=bytes(v)
        if all(0 <= x <= 65535 for x in v):
            outs[f"{sname}:u16be"]=b"".join(struct.pack(">H",x) for x in v)
            outs[f"{sname}:u16le"]=b"".join(struct.pack("<H",x) for x in v)
        for sep in ("",","," ","-",";",":","|"):
            outs[f"{sname}:dec:{repr(sep)}"]=sep.join(str(x) for x in v).encode()
            outs[f"{sname}:hex:{repr(sep)}"]=sep.join(format(x,"x") for x in v).encode()
            outs[f"{sname}:hex2:{repr(sep)}"]=sep.join(format(x,"02x") for x in v).encode()
        # Compact nibble when values genuinely lie in 0..15.
        if all(0 <= x < 16 for x in v):
            hs="".join(format(x,"x") for x in v)
            if len(hs)%2: hs="0"+hs
            outs[f"{sname}:nibbles"]=bytes.fromhex(hs)
    # Deduplicate by bytes while preserving one provenance label.
    seen={}
    for k,v in outs.items():
        seen.setdefault(v,k)
    return [(label,data) for data,label in seen.items()]

def transform_sequences(vals):
    """Small, justified quantization/difference family."""
    out={}
    out["raw"]=list(vals)
    # Geometry in both automated and community readings is visibly coarse; test common grid sizes.
    for q in (2,5,10):
        out[f"floor/{q}"]=[x//q for x in vals]
        out[f"round/{q}"]=[int(round(x/q)) for x in vals]
        out[f"mod{q}"]=[x%q for x in vals]
    # Adjacent differences can represent skyline steps rather than absolute scale.
    out["diff"]=[vals[0]]+[vals[i]-vals[i-1] for i in range(1,len(vals))]
    out["absdiff"]=[vals[0]]+[abs(vals[i]-vals[i-1]) for i in range(1,len(vals))]
    # First differences modulo 256 only as a byte-safe representation, not a search expansion.
    out["diffmod256"]=[x%256 for x in out["diff"]]
    # Keep only non-negative transforms for integer serializers.
    return {k:v for k,v in out.items() if all(x>=0 for x in v)}

def direct32(data):
    """Only obvious 32-byte direct mappings: pad/truncate at both ends."""
    out=[]
    if len(data)==32:
        out.append(("exact",data))
    elif len(data)<32:
        out += [
          ("lpad0",b"\0"*(32-len(data))+data),
          ("rpad0",data+b"\0"*(32-len(data))),
        ]
    else:
        out += [("head32",data[:32]),("tail32",data[-32:])]
    return out

def main():
    g=json.loads(GEOM.read_text())
    b=g["buildings"]
    exact_height=[x["bottom_y"]-x["roof_y"] for x in b]
    exact_height_inc=[x["bottom_y"]-x["roof_y"]+1 for x in b]
    exact_width=[x["x1"]-x["x0"] for x in b]
    exact_width_inc=[x["x1"]-x["x0"]+1 for x in b]

    sources={
      "auto_exclusive":(exact_height,exact_width),
      "auto_inclusive":(exact_height_inc,exact_width_inc),
      "community":(COMM_HEIGHT,COMM_WIDTH),
    }
    selections={}
    for sname,(heights,widths) in sources.items():
        selections[f"{sname}:Hwidth_Vheight"]=[
          widths[i] if ORIENT[i]=="H" else heights[i] for i in range(12)]
        selections[f"{sname}:Hheight_Vwidth"]=[
          heights[i] if ORIENT[i]=="H" else widths[i] for i in range(12)]
        # Controls: unselected dimensions, to prove stage accounting includes baseline families.
        selections[f"{sname}:heights"]=list(heights)
        selections[f"{sname}:widths"]=list(widths)

    checked=set(); valid=0; near=0; exact=False; family_counts={}
    def check(raw,family):
        nonlocal valid,near,exact
        if len(raw)!=32 or raw in checked: return
        checked.add(raw)
        addr=eth_addr(raw)
        if addr is None: return
        valid+=1
        family_counts[family]=family_counts.get(family,0)+1
        if addr.startswith("ff21"): near+=1
        if addr==TARGET: exact=True

    tested_sequences={}
    for selname,vals in selections.items():
        tested_sequences[selname]=vals
        for tname,tvals in transform_sequences(vals).items():
            for sername,data in serializations(tvals):
                base=f"{selname}:{tname}:{sername}"
                for hname,raw in digests(data):
                    check(raw,base+":"+hname)
                    check(raw[::-1],base+":"+hname+":scalar-rev")
                    if exact: break
                if exact: break
                for dname,raw in direct32(data):
                    check(raw,base+":direct:"+dname)
                    check(raw[::-1],base+":direct:"+dname+":scalar-rev")
                    if exact: break
                if exact: break
            if exact: break
        if exact: break

    if exact:
        print("MATCH_DETECTED")
        raise SystemExit(78)

    result={
      "orientation":ORIENT,
      "orientation_H0V1_hex":"321",
      "tested_selected_sequences":tested_sequences,
      "unique_32byte_candidates":len(checked),
      "valid_scalars_checked":valid,
      "near_ff21":near,
      "exact_match":False,
      "scope":[
        "automated exclusive/inclusive pixel dimensions plus community approximate dimensions",
        "H->width,V->height and inverse orientation selection, with heights/widths controls",
        "raw, grid quantization 2/5/10, modulo grids, adjacent differences/absolute differences",
        "u8/u16 BE/LE, decimal/hex separated text, compact nibbles when applicable",
        "SHA-256, double-SHA-256, Keccak-256, BLAKE2s, bounded direct 32-byte mappings",
        "forward/reverse sequence and scalar-byte reversal"
      ],
      "security_note":"No candidate private key is persisted."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=["# Stage 8 — orientation-guided skyline geometry","",
        "The robust hatch marker is HHVV HHVH HHHV = 0x321 under H=0,V=1.",
        "This stage uses hatch direction as a selector for building dimension (H→width, V→height), with the inverse and raw height/width sequences as controls.","",
        "## Selected sequences",""]
    for k,v in tested_sequences.items():
        md.append(f"- {k}: {v}")
    md += ["",
      f"- Unique 32-byte candidates generated: {len(checked)}",
      f"- Valid secp256k1 scalars checked: {valid}",
      f"- ff21 prefix near-misses: {near}",
      "- Exact target match: false","",
      "This rules out the bounded, most literal interpretation that each building's hatch selects its horizontal or vertical dimension and that the resulting 12 values are directly serialized or hashed by common transforms.",
      ""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"bounded-no-match","unique":len(checked),"valid":valid,"near":near}))

if __name__=="__main__":
    main()
