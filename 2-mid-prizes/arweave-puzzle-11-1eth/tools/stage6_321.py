#!/usr/bin/env python3
"""Stage 6: follow the robust skyline 0x321 lead without unbounded brute force.

The skyline hatching reads HHVV HHVH HHHV. If H=0 and V=1 this is binary
0011 0010 0001 = hex 321. This stage tests the most literal "3-2-1" bit-plane
interpretations, renders them for visual inspection, and checks whether the visual
321 marker survives ordinary format conversion while exact low bits do not.

No candidate private key is persisted. An exact target-address match aborts with code 78.
"""
from __future__ import annotations
import io, json, hashlib
from pathlib import Path
from itertools import permutations
import numpy as np
import cv2
from PIL import Image
from Crypto.Hash import keccak
from coincurve import PrivateKey

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage6-321"
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
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

def transforms(a):
    # Eight visually natural raster traversals.
    for tr in (False,True):
        b=a.T if tr else a
        for fy in (False,True):
            for fx in (False,True):
                c=b[::-1 if fy else 1,::-1 if fx else 1]
                yield f"t{int(tr)}y{int(fy)}x{int(fx)}",c

def pack_planes(arr,planes):
    vals=arr.ravel()
    bits=np.stack([((vals>>p)&1) for p in planes],axis=1).ravel().astype(np.uint8)
    usable=(len(bits)//8)*8
    return np.packbits(bits[:usable],bitorder="big").tobytes()

def sobel_class(gray,b):
    x0,x1,y0,y1=b["x0"],b["x1"],b["roof_y"],b["bottom_y"]
    mx=max(5,int((x1-x0)*0.12)); my=max(6,int((y1-y0)*0.12))
    c=gray[y0+my:y1-my,x0+mx:x1-mx]
    c=cv2.GaussianBlur(c,(3,3),0)
    gx=cv2.Sobel(c,cv2.CV_64F,1,0,ksize=3)
    gy=cv2.Sobel(c,cv2.CV_64F,0,1,ksize=3)
    ex=float(np.mean(np.abs(gx))); ey=float(np.mean(np.abs(gy)))
    score=(ex-ey)/(ex+ey+1e-12)
    return "V" if score>0.06 else ("H" if score<-0.06 else "M")

def save_binary(name,plane):
    Image.fromarray(np.where(plane,0,255).astype(np.uint8),mode="L").save(OUT/name)

def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=EXPECTED:
        raise SystemExit("wrong source")
    im=Image.open(SOURCE)
    a=np.array(im)
    gray=a[:,:,0].astype(np.uint8)
    alpha=a[:,:,1].astype(np.uint8)
    geom=json.loads(GEOM.read_text())

    # Diagnostics for the literal 3,2,1 interpretation (1-indexed -> bit positions 2,1,0).
    low3=gray & 7
    low3rev=((low3&1)<<2) | (low3&2) | ((low3&4)>>2)
    Image.fromarray((low3.astype(np.uint16)*255//7).astype(np.uint8),mode="L").save(OUT/"low3-natural.png")
    Image.fromarray((low3rev.astype(np.uint16)*255//7).astype(np.uint8),mode="L").save(OUT/"low3-bit-reversed.png")
    for p in range(4):
        save_binary(f"bit{p}.png",(gray>>p)&1)
    rgb321=np.dstack([((gray>>2)&1)*255,((gray>>1)&1)*255,(gray&1)*255]).astype(np.uint8)
    rgb432=np.dstack([((gray>>3)&1)*255,((gray>>2)&1)*255,((gray>>1)&1)*255]).astype(np.uint8)
    Image.fromarray(rgb321,mode="RGB").save(OUT/"planes-321-rgb.png")
    Image.fromarray(rgb432,mode="RGB").save(OUT/"planes-432-rgb.png")

    # Also save the top three MSBs for comparison; these should mostly reproduce the drawing.
    high3=(gray>>5)&7
    Image.fromarray((high3.astype(np.uint16)*255//7).astype(np.uint8),mode="L").save(OUT/"high3.png")

    seen=set(); checks=0; near=0; exact=False; fam={}
    def check(raw,family):
        nonlocal checks,near,exact
        if len(raw)!=32 or raw in seen: return
        seen.add(raw)
        addr=eth_addr(raw)
        if addr is None: return
        checks+=1; fam[family]=fam.get(family,0)+1
        if addr.startswith("ff21"): near+=1
        if addr==TARGET: exact=True

    # Bounded candidate family: whole-stream digests and endpoints only.
    regions={
      "full":gray,
      "skyline":gray[0:340,:],
      "bigboat":gray[300:620,20:390],
      "pierboats":gray[330:760,850:1600],
    }
    plane_orders=[
      (2,1,0),(0,1,2),       # one-indexed 3-2-1 and reverse
      (3,2,1),(1,2,3),       # zero-indexed literal 3-2-1 and reverse
    ]
    for rname,reg in regions.items():
        for oname,o in transforms(reg):
            # low-3 byte-valued visual residual
            for repname,data in (
                ("low3",(o&7).tobytes()),
                ("low3rev",(((o&1)<<2)|(o&2)|((o&4)>>2)).astype(np.uint8).tobytes()),
            ):
                for hname,raw in digests(data):
                    check(raw,f"{rname}:{oname}:{repname}:{hname}")
                    check(raw[::-1],f"{rname}:{oname}:{repname}:{hname}:rev")
            for planes in plane_orders:
                data=pack_planes(o,planes)
                if len(data)>=32:
                    for tag,raw in (("head",data[:32]),("tail",data[-32:])):
                        check(raw,f"{rname}:{oname}:planes{planes}:{tag}")
                        check(raw[::-1],f"{rname}:{oname}:planes{planes}:{tag}:rev")
                for hname,raw in digests(data):
                    check(raw,f"{rname}:{oname}:planes{planes}:{hname}")
                    check(raw[::-1],f"{rname}:{oname}:planes{planes}:{hname}:rev")
            if exact: break
        if exact: break

    if exact:
        print("MATCH_DETECTED")
        raise SystemExit(78)

    # Format-invariance experiment: JPEG destroys exact low bits but should preserve the
    # human-visible hatch orientation if that is the intended clue/carrier.
    base_seq="".join(sobel_class(gray,b) for b in geom["buildings"])
    jpeg_tests=[]
    for q in (95,85,70,50):
        buf=io.BytesIO()
        Image.fromarray(gray,mode="L").save(buf,format="JPEG",quality=q)
        j=np.array(Image.open(io.BytesIO(buf.getvalue())).convert("L"),dtype=np.uint8)
        seq="".join(sobel_class(j,b) for b in geom["buildings"])
        exact_low3=float(np.mean((j&7)==(gray&7)))
        exact_gray=float(np.mean(j==gray))
        jpeg_tests.append({"quality":q,"skyline_sequence":seq,"same_as_original":seq==base_seq,
                           "low3_exact_fraction":exact_low3,"gray_exact_fraction":exact_gray})

    result={
      "skyline_sequence":base_seq,
      "skyline_H0V1_bits":"001100100001",
      "skyline_H0V1_hex":"321",
      "skyline_H1V0_hex":"cde",
      "candidate_family":"bounded 3-2-1 literal transforms only",
      "unique_32byte_candidates":len(seen),
      "valid_scalars_checked":checks,
      "near_ff21":near,
      "exact_match":False,
      "families":dict(sorted(fam.items())),
      "jpeg_invariance":jpeg_tests,
      "diagnostics":[
        "low3-natural.png","low3-bit-reversed.png","bit0.png","bit1.png","bit2.png","bit3.png",
        "planes-321-rgb.png","planes-432-rgb.png","high3.png"
      ],
      "security_note":"No candidate private key is stored. Exact matches abort before result persistence."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=["# Stage 6 — following the skyline 0x321 lead","",
        "The visually robust building sequence is HHVV HHVH HHHV. Taking H=0 and V=1 gives 0011 0010 0001 = 0x321; the complement gives 0xCDE.",
        "",
        "This stage tested literal 3-2-1 bit-plane interpretations only as a bounded follow-up, not as an arbitrary sliding-window brute force.",
        f"- Unique 32-byte candidates generated: {len(seen)}",
        f"- Valid secp256k1 scalars checked: {checks}",
        f"- ff21 two-byte prefix near-misses: {near}",
        "- Exact target match: false","",
        "## Format-invariance check","",
        "| JPEG quality | skyline sequence | preserved? | exact low-3 fraction | exact gray fraction |",
        "|---:|:---|:---:|---:|---:|"]
    for x in jpeg_tests:
        md.append(f"| {x['quality']} | {x['skyline_sequence']} | {x['same_as_original']} | {x['low3_exact_fraction']:.4f} | {x['gray_exact_fraction']:.4f} |")
    md += ["",
      "Diagnostic images render bit planes 0-3, the natural/reversed low-three-bit residual, 3-2-1 false colour, 4-3-2 false colour and the top three MSBs.",
      "",
      "Interpretation: if the skyline really is an intentional 0x321 marker, it may be an instruction rather than key material. The tests above cover only the most literal bit-plane reading.",
      ""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"exhausted-bounded-no-match","checks":checks,"near":near,"jpeg":jpeg_tests}))

if __name__=="__main__":
    main()
