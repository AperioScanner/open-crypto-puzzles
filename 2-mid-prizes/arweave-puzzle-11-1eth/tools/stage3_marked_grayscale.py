#!/usr/bin/env python3
"""Stage 3: alpha-marked grayscale, boat-focus, and public identifier sweep.

The alpha anomaly may be a marker rather than the payload itself. This stage tests the
corresponding grayscale values at every alpha<255 coordinate, plus bounded whole-crop
hashes around the marked boat and a small public-identifier family.

No private-key candidate is persisted. On an exact target match the process emits only
MATCH_DETECTED and exits 78.
"""
from __future__ import annotations
import base64, hashlib, json
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image
from Crypto.Hash import keccak
from coincurve import PrivateKey

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage3-marked-grayscale"
EXPECTED="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
TARGET="ff2142e98e09b5344994f9beb9c56c95506b9f17"
ORDER=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
KNOWN=bytes([1])*32
KNOWN_ADDR="1a642f0e3c3af545e7acbd38b07251b3990914f1"
TXID="CzITHnEIlkQw9SbaX5futCzFrKk1qe_NwvWnIBmP2fY"

def address(raw: bytes):
    if len(raw)!=32: return None
    n=int.from_bytes(raw,"big")
    if not 0<n<ORDER: return None
    pub=PrivateKey(raw).public_key.format(compressed=False)[1:]
    return keccak.new(digest_bits=256,data=pub).digest()[-20:].hex()

assert address(KNOWN)==KNOWN_ADDR

def spatial_orders(records):
    # record = (x,y,L,A)
    by_row=sorted(records,key=lambda r:(r[1],r[0]))
    by_col=sorted(records,key=lambda r:(r[0],r[1]))
    rows=defaultdict(list); cols=defaultdict(list)
    for r in records: rows[r[1]].append(r); cols[r[0]].append(r)
    sr=[]; sc=[]
    for i,y in enumerate(sorted(rows)):
        sr.extend(sorted(rows[y],key=lambda r:r[0],reverse=bool(i&1)))
    for i,x in enumerate(sorted(cols)):
        sc.extend(sorted(cols[x],key=lambda r:r[1],reverse=bool(i&1)))
    return {
      "row":by_row,"row_rev":list(reversed(by_row)),
      "col":by_col,"col_rev":list(reversed(by_col)),
      "serp_row":sr,"serp_row_rev":list(reversed(sr)),
      "serp_col":sc,"serp_col_rev":list(reversed(sc)),
    }

def symbol_bits(vals, planes):
    a=np.asarray(vals,dtype=np.uint8)
    return np.stack([((a>>p)&1) for p in planes],axis=1).ravel()

def bit_windows(bits):
    # Cover every bit start by packing each alignment once, then sliding by bytes.
    for off in range(8):
        usable=((len(bits)-off)//8)*8
        if usable<256: continue
        data=np.packbits(bits[off:off+usable],bitorder="big").tobytes()
        for i in range(len(data)-31):
            yield off+i*8,data[i:i+32]

def digest_candidates(data: bytes):
    yield hashlib.sha256(data).digest()
    yield hashlib.sha256(hashlib.sha256(data).digest()).digest()
    yield keccak.new(digest_bits=256,data=data).digest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=EXPECTED: raise SystemExit("wrong source sha256")
    a=np.array(Image.open(SOURCE))
    if a.shape!=(1105,1600,2): raise SystemExit(f"unexpected image shape {a.shape}")
    L=a[:,:,0].astype(np.uint8); A=a[:,:,1].astype(np.uint8)
    ys,xs=np.where(A<255)
    rec=[(int(x),int(y),int(L[y,x]),int(A[y,x])) for y,x in zip(ys,xs)]
    orders=spatial_orders(rec)

    seen=set(); valid=0; near=0; families=defaultdict(int); exact=False
    def check(raw,family):
        nonlocal valid,near,exact
        if raw in seen: return
        seen.add(raw)
        addr=address(raw)
        if addr is None: return
        valid+=1; families[family]+=1
        if addr.startswith("ff21"): near+=1
        if addr==TARGET: exact=True

    selections=[(i,) for i in range(8)]+[(0,1),(1,0),(0,1,2),(2,1,0),(0,1,2,3),(3,2,1,0)]
    for oname,rr in orders.items():
        gray=[r[2] for r in rr]
        reps={"L":gray,"L_inv":[255-v for v in gray]}
        for rname,vals in reps.items():
            data=bytes(vals)
            # direct byte windows
            for i in range(max(0,len(data)-31)):
                raw=data[i:i+32]
                check(raw,f"{oname}:{rname}:bytewin")
                check(raw[::-1],f"{oname}:{rname}:bytewin:scalar-rev")
                if exact: break
            if exact: break

            # every bit-aligned 256-bit window from selected bitplanes
            for planes in selections:
                bits=symbol_bits(vals,planes)
                for _,raw in bit_windows(bits):
                    check(raw,f"{oname}:{rname}:planes{''.join(map(str,planes))}")
                    check(raw[::-1],f"{oname}:{rname}:planes{''.join(map(str,planes))}:scalar-rev")
                    if exact: break
                if exact: break
            if exact: break

            for raw in digest_candidates(data):
                check(raw,f"{oname}:{rname}:whole-digest")
                check(raw[::-1],f"{oname}:{rname}:whole-digest:scalar-rev")
                if exact: break
            if exact: break
        if exact: break

    # Bounded hashes of the marked boat region. The geometry box is from data/geometry.json;
    # the alpha box is measured directly from the canonical image. Margins remain small.
    if not exact:
        boxes={
          "geometry":(44,320,360,600),
          "alpha":(int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1),
        }
        for bname,(x0,y0,x1,y1) in boxes.items():
            for margin in (0,1,2,4,8,16,32):
                xa=max(0,x0-margin); ya=max(0,y0-margin)
                xb=min(L.shape[1],x1+margin); yb=min(L.shape[0],y1+margin)
                crop=a[ya:yb,xa:xb,:]
                orientations=[]
                for tr in (False,True):
                    base=crop.transpose(1,0,2) if tr else crop
                    for fy in (False,True):
                        for fx in (False,True):
                            orientations.append(base[::-1 if fy else 1,::-1 if fx else 1,:])
                for oi,o in enumerate(orientations):
                    reps={
                      "L":o[:,:,0].tobytes(),
                      "A":o[:,:,1].tobytes(),
                      "LA":o.tobytes(),
                      "alpha-selected-L":o[:,:,0][o[:,:,1]<255].tobytes(),
                    }
                    for rname,data in reps.items():
                        if not data: continue
                        for raw in digest_candidates(data):
                            check(raw,f"crop:{bname}:m{margin}:o{oi}:{rname}:digest")
                            check(raw[::-1],f"crop:{bname}:m{margin}:o{oi}:{rname}:digest:scalar-rev")
                            if exact: break
                        if exact: break
                    if exact: break
                if exact: break
            if exact: break

    # Public filename / Arweave-transaction identifier family, motivated by the 43-char ID
    # decoding to exactly 32 bytes. No secret input is used.
    identifier_checked=0
    if not exact:
        pad="="*((4-len(TXID)%4)%4)
        txraw=base64.urlsafe_b64decode(TXID+pad)
        assert len(txraw)==32
        atoms=[
          ("txid-ascii",TXID.encode()),
          ("txid-raw",txraw),
          ("txid-filename",(TXID+".png").encode()),
          ("arweave-url",("https://arweave.net/"+TXID).encode()),
          ("watermark",b"https://twitter.com/ArweaveP"),
        ]
        for name,data in atoms:
            directs=[data] if len(data)==32 else []
            for raw in directs+list(digest_candidates(data)):
                identifier_checked+=1
                check(raw,f"identifier:{name}")
                check(raw[::-1],f"identifier:{name}:scalar-rev")
                if exact: break
            if exact: break

    if exact:
        print("MATCH_DETECTED")
        raise SystemExit(78)

    result={
      "source_sha256":sha,
      "alpha_marked_pixels":len(rec),
      "alpha_bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
      "orders_tested":list(orders),
      "bit_selections":[list(x) for x in selections],
      "unique_candidates_seen":len(seen),
      "valid_scalars_checked":valid,
      "near_ff21_addresses":near,
      "identifier_candidate_records":identifier_checked,
      "exact_match_detected":False,
      "families":dict(sorted(families.items())),
      "scope":[
        "grayscale and inverted-grayscale values at all alpha<255 coordinates",
        "8 spatial orders; direct 32-byte windows; every bit start for 14 bitplane selections",
        "normal and reversed scalar byte order; SHA-256/double-SHA-256/Keccak whole-sequence digests",
        "bounded SHA-256/double-SHA-256/Keccak hashes of geometry/alpha boat crops at margins 0..32 under 8 orientations",
        "small public Arweave transaction-id / filename / watermark identifier family",
      ],
      "security_note":"No candidate private key is stored. Exact matches abort before writing this report.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=[
      "# Stage 3 — alpha-marked grayscale and boat-focus sweep","",
      f"- Alpha-marked pixels: {len(rec)}",
      f"- Alpha bbox: {result['alpha_bbox']}",
      f"- Unique 32-byte candidates generated: {len(seen)}",
      f"- Valid secp256k1 scalars checked: {valid}",
      f"- Addresses beginning with ff21: {near}",
      "- Exact target match: **False**","",
      "This stage treats the alpha halo as a possible *marker* and tests the corresponding grayscale content, rather than interpreting alpha values as the payload itself.",
      "It also checks bounded hashes of the marked boat crop and a small public identifier family.",
      "No private-key candidate is persisted.","",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"exhausted-no-match","valid_scalars_checked":valid,"unique_candidates":len(seen),"near_ff21":near}))

if __name__=="__main__":
    main()
