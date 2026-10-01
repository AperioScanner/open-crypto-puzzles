#!/usr/bin/env python3
"""Stage 7: test a historically plausible first-row private-key stego protocol.

surg0r/steg (public since 2015) describes itself as a "bitcoin steganography library",
hides a private-key string in the R-channel LSB of consecutive first-row pixels, prepends
one length byte, and appends four ASCII hex checksum characters from sha256(data).

Puzzle #11 has a documented anomalous first row, so this is a targeted protocol test rather
than a generic brute force. We test the exact protocol plus small representation/order variants.

No candidate private key is persisted. Exact target matches abort with exit code 78.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
import numpy as np
from PIL import Image
from Crypto.Hash import keccak
from coincurve import PrivateKey

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage7-first-row-steg"
OUT.mkdir(parents=True,exist_ok=True)
TARGET="ff2142e98e09b5344994f9beb9c56c95506b9f17"
ORDER=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
HEX64=re.compile(rb"^[0-9a-fA-F]{64}$")
B58=b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def eth_addr(raw):
    if len(raw)!=32: return None
    n=int.from_bytes(raw,"big")
    if not 0<n<ORDER: return None
    pub=PrivateKey(raw).public_key.format(compressed=False)[1:]
    return keccak.new(digest_bits=256,data=pub).digest()[-20:].hex()

def b58decode(s):
    n=0
    for ch in s:
        p=B58.find(bytes([ch]))
        if p<0: return None
        n=n*58+p
    out=n.to_bytes((n.bit_length()+7)//8,"big") if n else b""
    pad=len(s)-len(s.lstrip(b"1"))
    return b"\0"*pad+out

def wif_to_raw(s):
    dec=b58decode(s)
    if not dec or len(dec) not in (37,38): return None
    body,chk=dec[:-4],dec[-4:]
    if hashlib.sha256(hashlib.sha256(body).digest()).digest()[:4]!=chk: return None
    if body[0] not in (0x80,0xef): return None
    payload=body[1:]
    if len(payload)==33 and payload[-1]==1: payload=payload[:-1]
    return payload if len(payload)==32 else None

def bits_to_bytes(bits,bitorder):
    usable=(len(bits)//8)*8
    return np.packbits(bits[:usable],bitorder=bitorder).tobytes()

def checksum_flags(data,chk):
    h=hashlib.sha256(data).hexdigest().encode()
    raw=hashlib.sha256(data).digest()
    return {
      "surg0r_hex_tail4": chk==h[-4:],
      "hex_head4": chk==h[:4],
      "raw_head4": chk==raw[:4],
      "raw_tail4": chk==raw[-4:],
    }

def maybe_check_key(payload):
    candidates=[]
    if HEX64.match(payload):
        candidates.append(bytes.fromhex(payload.decode()))
    if len(payload)==32:
        candidates.append(payload)
    w=wif_to_raw(payload)
    if w is not None:
        candidates.append(w)
    for raw in candidates:
        if eth_addr(raw)==TARGET:
            return True
    return False

def main():
    a=np.array(Image.open(SOURCE))
    L=a[:,:,0].astype(np.uint8)
    A=a[:,:,1].astype(np.uint8)
    row_sources={"gray":L[0,:],"alpha":A[0,:]}
    tests=[]; exact=False

    for src_name,row in row_sources.items():
      for plane in range(8):
        base=((row>>plane)&1).astype(np.uint8)
        for direction,bits0 in (("forward",base),("reverse",base[::-1])):
          for invert,bits in ((False,bits0),(True,1-bits0)):
            for bitorder in ("big","little"):
              # The historical protocol starts at bit 0; offsets 0..15 cover tiny
              # alignment drift without turning this into an unbounded search.
              for bitoff in range(16):
                bs=bits_to_bytes(bits[bitoff:],bitorder)
                if len(bs)<6: continue
                length=bs[0]
                # Historical payload: one length byte, then length bytes where the
                # final 4 bytes are checksum characters.
                record={
                  "source":src_name,"plane":plane,"direction":direction,
                  "invert":invert,"bitorder":bitorder,"bit_offset":bitoff,
                  "length_byte":int(length),"available_bytes":len(bs)-1,
                }
                if 4 <= length <= min(199,len(bs)-1):
                    block=bs[1:1+length]
                    data,chk=block[:-4],block[-4:]
                    flags=checksum_flags(data,chk)
                    printable=sum(32<=x<127 for x in data)/max(1,len(data))
                    record.update({
                      "payload_len":len(data),
                      "checksum":flags,
                      "printable_fraction":printable,
                      "payload_sha256":hashlib.sha256(data).hexdigest(),
                      "looks_hex64":bool(HEX64.match(data)),
                      "looks_wif":bool(len(data) in (51,52) and all(ch in B58 for ch in data)),
                    })
                    if maybe_check_key(data):
                        exact=True
                    # Also check a 64-hex substring inside a protocol payload; do not persist it.
                    for m in re.finditer(rb"[0-9a-fA-F]{64}",data):
                        if maybe_check_key(m.group(0)):
                            exact=True
                    # Check raw 32-byte windows only at payload boundaries, not every offset.
                    if len(data)>=32:
                        if maybe_check_key(data[:32]) or maybe_check_key(data[-32:]):
                            exact=True
                tests.append(record)
                if exact: break
              if exact: break
            if exact: break
          if exact: break
        if exact: break
      if exact: break

    if exact:
        print("MATCH_DETECTED")
        raise SystemExit(78)

    # Summarise strongest protocol-like decodes. Never persist payload bytes.
    valid_checksum=[t for t in tests if any(t.get("checksum",{}).values())]
    plausible=sorted(
      [t for t in tests if "payload_len" in t],
      key=lambda t:(any(t["checksum"].values()),t.get("looks_hex64",False),t.get("looks_wif",False),t["printable_fraction"]),
      reverse=True
    )[:40]
    # Exact canonical interpretation at gray LSB, forward, non-inverted, MSB-first, offset 0.
    canonical=next(t for t in tests if t["source"]=="gray" and t["plane"]==0 and t["direction"]=="forward"
                   and t["invert"] is False and t["bitorder"]=="big" and t["bit_offset"]==0)

    result={
      "historical_reference":{
        "repo":"surg0r/steg",
        "public_since":"2015-11-22",
        "mechanism":"first row, red-channel LSB, 1-byte length, payload plus 4 ASCII hex chars from sha256(data) tail",
      },
      "canonical_gray_lsb_decode":canonical,
      "total_protocol_variants":len(tests),
      "valid_checksum_variants":len(valid_checksum),
      "valid_checksum_metadata":valid_checksum,
      "top_plausible_metadata":plausible,
      "exact_target_match":False,
      "security_note":"Payload bytes and private-key candidates are never persisted."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=["# Stage 7 — historical first-row private-key stego protocol","",
        "Targeted reference: public surg0r/steg code from 2015. It hides a private-key string in consecutive first-row R-channel LSBs, with one length byte and a four-character SHA-256 checksum suffix.",
        "",
        f"- Protocol/order variants checked: {len(tests)}",
        f"- Variants with any supported checksum match: {len(valid_checksum)}",
        "- Exact Ethereum target match: false",
        "",
        "## Canonical surg0r-style read of this image","",
        f"- First decoded length byte: {canonical['length_byte']}",
        f"- Bytes available after length: {canonical['available_bytes']}"]
    if "payload_len" in canonical:
        md += [
          f"- Payload bytes before checksum: {canonical['payload_len']}",
          f"- Printable fraction: {canonical['printable_fraction']:.3f}",
          f"- Exact surg0r checksum valid: {canonical['checksum']['surg0r_hex_tail4']}",
          f"- Looks like 64 hex: {canonical['looks_hex64']}",
          f"- Looks like WIF: {canonical['looks_wif']}",
        ]
    md += ["",
      "The first-row anomaly makes this family historically relevant, but this bounded test found no winning key and records no candidate payload.",
      ""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"no-match","variants":len(tests),"checksum_matches":len(valid_checksum),"canonical_length":canonical["length_byte"]}))

if __name__=="__main__":
    main()
