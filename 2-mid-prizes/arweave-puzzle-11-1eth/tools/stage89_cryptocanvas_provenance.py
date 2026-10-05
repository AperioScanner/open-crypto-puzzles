#!/usr/bin/env python3
"""Stage 89: CryptoCanvas provenance + metadata audit.

Public-source, non-secret research only.

A 2021 Puzzling StackExchange comment reported that reverse-image search found
Puzzle #11 inside the five-item OpenSea collection "cryptocanvas.xyz - CANVAS".
The collection currently indexes as Jul 2020, after Puzzle #11's Apr 2020
publication. This stage checks whether the collection is merely a derivative
mirror or preserves independently useful metadata/provenance.

No private-key generation, derivation, reconstruction, enumeration, verification,
or wallet access is performed.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage89-cryptocanvas-provenance"
OUT.mkdir(parents=True,exist_ok=True)

CONTRACT="0x0b0b70905137786cf705102c194a1b4916d8c4d0"
TOKEN_IDS=[1,2,3,4,5]
PUZZLE_TOKEN=5
OPENSEA_COLLECTION="https://opensea.io/collection/cryptocanvas-xyz"
OPENSEA_ITEM=f"https://opensea.io/item/ethereum/{CONTRACT}/{PUZZLE_TOKEN}"
STACKEXCHANGE="https://puzzling.stackexchange.com/questions/97537/image-steganography-hidden-message-inside-image-png-8-bit-grayalpha?noredirect=1"

RPCS=[
    "https://ethereum-rpc.publicnode.com",
    "https://cloudflare-eth.com",
]
IPFS_GATEWAYS=[
    "https://ipfs.io/ipfs/",
    "https://cloudflare-ipfs.com/ipfs/",
]

TRANSFER_TOPIC="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TOKENURI_SELECTOR="0xc87b56dd"
OWNEROF_SELECTOR="0x6352211e"

SESSION=requests.Session()
SESSION.headers.update({
    "User-Agent":"Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0; public provenance audit)"
})

def sha256_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def fetch(url:str, timeout=25):
    r=SESSION.get(url,timeout=timeout,allow_redirects=True)
    r.raise_for_status()
    return r

def rpc_call(method,params):
    errors=[]
    for endpoint in RPCS:
        try:
            r=SESSION.post(endpoint,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=25)
            r.raise_for_status()
            j=r.json()
            if "error" in j:
                raise RuntimeError(j["error"])
            return j.get("result"),endpoint
        except Exception as e:
            errors.append({"endpoint":endpoint,"error":repr(e)})
    raise RuntimeError(f"all RPC endpoints failed: {errors}")

def abi_uint(n:int)->str:
    return f"{n:064x}"

def decode_abi_string(hexdata:str):
    if not hexdata or hexdata=="0x":
        return None
    raw=bytes.fromhex(hexdata[2:])
    if len(raw)<64:
        return None
    off=int.from_bytes(raw[:32],"big")
    if off+32>len(raw):
        return None
    ln=int.from_bytes(raw[off:off+32],"big")
    start=off+32
    end=start+ln
    if end>len(raw):
        return None
    return raw[start:end].decode("utf-8","replace")

def decode_owner(hexdata:str):
    if not hexdata or len(hexdata)<42:
        return None
    h=hexdata[2:].rjust(64,"0")
    return "0x"+h[-40:].lower()

def resolve_uri(uri:str):
    if not uri:
        return []
    if uri.startswith("ipfs://"):
        tail=uri[len("ipfs://"):]
        return [g+tail for g in IPFS_GATEWAYS]
    if uri.startswith("ar://"):
        tail=uri[len("ar://"):]
        return [f"https://arweave.net/{tail}"]
    if uri.startswith("http://") or uri.startswith("https://"):
        return [uri]
    if uri.startswith("data:"):
        return [uri]
    return []

def load_json_uri(uri:str):
    if uri.startswith("data:application/json;base64,"):
        b=base64.b64decode(uri.split(",",1)[1])
        return json.loads(b),{"source":"data-uri","sha256":sha256_bytes(b)}
    if uri.startswith("data:application/json,"):
        from urllib.parse import unquote
        s=unquote(uri.split(",",1)[1])
        b=s.encode()
        return json.loads(s),{"source":"data-uri","sha256":sha256_bytes(b)}
    errors=[]
    for u in resolve_uri(uri):
        try:
            r=fetch(u)
            b=r.content
            return r.json(),{"source":u,"sha256":sha256_bytes(b),"bytes":len(b),"content_type":r.headers.get("content-type")}
        except Exception as e:
            errors.append({"url":u,"error":repr(e)})
    return None,{"errors":errors}

def load_media(uri:str):
    errors=[]
    for u in resolve_uri(uri):
        if u.startswith("data:image/"):
            try:
                head,payload=u.split(",",1)
                b=base64.b64decode(payload) if ";base64" in head else payload.encode()
                return b,{"source":"data-uri","sha256":sha256_bytes(b),"bytes":len(b)}
            except Exception as e:
                errors.append({"url":"data-uri","error":repr(e)})
                continue
        try:
            r=fetch(u)
            return r.content,{"source":u,"sha256":sha256_bytes(r.content),"bytes":len(r.content),"content_type":r.headers.get("content-type")}
        except Exception as e:
            errors.append({"url":u,"error":repr(e)})
    return None,{"errors":errors}

def image_similarity(media:bytes):
    orig_b=SOURCE.read_bytes()
    out={"canonical_sha256":sha256_bytes(orig_b),"media_sha256":sha256_bytes(media)}
    try:
        a=np.array(Image.open(BytesIO(orig_b)).convert("L"))
        b=np.array(Image.open(BytesIO(media)).convert("L"))
        out["canonical_shape"]=list(a.shape)
        out["media_shape"]=list(b.shape)
        if b.shape!=a.shape:
            b=np.array(Image.fromarray(b).resize((a.shape[1],a.shape[0]),Image.Resampling.LANCZOS))
            out["resized_for_comparison"]=True
        else:
            out["resized_for_comparison"]=False
        aa=a.astype(np.float64).ravel()
        bb=b.astype(np.float64).ravel()
        if aa.std()>1e-9 and bb.std()>1e-9:
            out["pearson_gray"]=float(np.corrcoef(aa,bb)[0,1])
        else:
            out["pearson_gray"]=0.0
        diff=np.abs(a.astype(np.int16)-b.astype(np.int16))
        out["mean_abs_gray_delta"]=float(diff.mean())
        out["exact_gray_fraction"]=float(np.mean(a==b))
        # 64x64 perceptual correlation is tolerant to resampling/compression.
        ar=np.array(Image.fromarray(a).resize((64,64),Image.Resampling.LANCZOS),dtype=float).ravel()
        br=np.array(Image.fromarray(b).resize((64,64),Image.Resampling.LANCZOS),dtype=float).ravel()
        out["pearson_64x64"]=float(np.corrcoef(ar,br)[0,1]) if ar.std()>1e-9 and br.std()>1e-9 else 0.0
    except Exception as e:
        out["image_error"]=repr(e)
    return out

def token_uri(token_id):
    data=TOKENURI_SELECTOR+abi_uint(token_id)
    res,endpoint=rpc_call("eth_call",[{"to":CONTRACT,"data":data},"latest"])
    return decode_abi_string(res),endpoint

def owner_of(token_id):
    data=OWNEROF_SELECTOR+abi_uint(token_id)
    res,endpoint=rpc_call("eth_call",[{"to":CONTRACT,"data":data},"latest"])
    return decode_owner(res),endpoint

def first_transfer_log(token_id):
    topic_token="0x"+abi_uint(token_id)
    # Collection is indexed Jul 2020. Search a bounded historical window first,
    # then fall back to a few broader 1M-block windows if needed.
    ranges=[
        (10_000_000,11_000_000),
        (9_000_000,10_000_000),
        (11_000_000,12_000_000),
    ]
    errors=[]
    for lo,hi in ranges:
        try:
            logs,endpoint=rpc_call("eth_getLogs",[{
                "address":CONTRACT,
                "fromBlock":hex(lo),
                "toBlock":hex(hi),
                "topics":[TRANSFER_TOPIC,None,None,topic_token],
            }])
            if logs:
                log=sorted(logs,key=lambda z:int(z["blockNumber"],16))[0]
                return log,endpoint
        except Exception as e:
            errors.append({"range":[lo,hi],"error":repr(e)})
    return None,{"errors":errors}

def block_info(hex_block):
    b,endpoint=rpc_call("eth_getBlockByNumber",[hex_block,False])
    return b,endpoint

def tx_info(txhash):
    tx,endpoint=rpc_call("eth_getTransactionByHash",[txhash])
    return tx,endpoint

def topic_addr(topic):
    if not topic:
        return None
    h=topic[2:].rjust(64,"0")
    return "0x"+h[-40:].lower()

def parse_opensea_html():
    out={}
    for label,url in (("collection",OPENSEA_COLLECTION),("item5",OPENSEA_ITEM),("stackexchange",STACKEXCHANGE)):
        try:
            r=fetch(url)
            t=r.text
            entry={
                "url":url,
                "status":r.status_code,
                "bytes":len(r.content),
                "sha256":sha256_bytes(r.content),
            }
            if label=="collection":
                entry["mentions_jul_2020"]=bool(re.search(r"Jul\s+2020",t,re.I))
                entry["mentions_five_items"]=bool(re.search(r">\s*5\s*<",t))
            if label=="item5":
                media=re.findall(r"https://i2c\.seadn\.io/[^\"'<> ]+",t)
                entry["media_urls"]=list(dict.fromkeys(media))[:10]
                owner=re.findall(r"0x[a-fA-F0-9]{40}",t)
                entry["addresses"]=list(dict.fromkeys(x.lower() for x in owner))[:20]
            if label=="stackexchange":
                entry["mentions_cryptocanvas"]=("cryptocanvas" in t.lower())
                entry["mentions_reverse_image"]=("reverse image" in t.lower())
            out[label]=entry
        except Exception as e:
            out[label]={"url":url,"error":repr(e)}
    return out

def main():
    result={
        "experiment_id":"A11-EXP-089",
        "scope":"public on-chain and web provenance audit of the CryptoCanvas reverse-image lead; no private-key operations",
        "contract":CONTRACT,
        "sources":{
            "opensea_collection":OPENSEA_COLLECTION,
            "opensea_item5":OPENSEA_ITEM,
            "stackexchange":STACKEXCHANGE,
        },
        "web_html":parse_opensea_html(),
        "tokens":{},
    }

    token5_media=None
    for tid in TOKEN_IDS:
        row={"token_id":tid}
        try:
            uri,ep=token_uri(tid)
            row["token_uri"]=uri
            row["token_uri_rpc"]=ep
            meta,meta_info=load_json_uri(uri) if uri else (None,{"error":"no tokenURI"})
            row["metadata_fetch"]=meta_info
            if isinstance(meta,dict):
                row["metadata"]={
                    "name":meta.get("name"),
                    "description":meta.get("description"),
                    "image":meta.get("image") or meta.get("image_url"),
                    "external_url":meta.get("external_url"),
                    "attributes":meta.get("attributes"),
                }
                image_uri=row["metadata"]["image"]
                if image_uri:
                    media,mi=load_media(image_uri)
                    row["media_fetch"]=mi
                    if media:
                        row["media_sha256"]=sha256_bytes(media)
                        if tid==PUZZLE_TOKEN:
                            token5_media=media
            else:
                row["metadata"]=None
        except Exception as e:
            row["token_uri_error"]=repr(e)

        try:
            owner,ep=owner_of(tid)
            row["current_owner"]=owner
            row["owner_rpc"]=ep
        except Exception as e:
            row["owner_error"]=repr(e)

        log,ep=first_transfer_log(tid)
        if log:
            mint={
                "block_number":int(log["blockNumber"],16),
                "transaction_hash":log["transactionHash"],
                "from":topic_addr(log["topics"][1]) if len(log.get("topics",[]))>1 else None,
                "to":topic_addr(log["topics"][2]) if len(log.get("topics",[]))>2 else None,
                "rpc":ep,
            }
            try:
                b,bep=block_info(log["blockNumber"])
                ts=int(b["timestamp"],16)
                mint["timestamp_unix"]=ts
                mint["timestamp_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(ts))
                mint["block_rpc"]=bep
            except Exception as e:
                mint["block_error"]=repr(e)
            try:
                tx,tep=tx_info(log["transactionHash"])
                if tx:
                    mint["tx_from"]=tx.get("from","").lower()
                    mint["tx_to"]=(tx.get("to") or "").lower() if tx.get("to") else None
                mint["tx_rpc"]=tep
            except Exception as e:
                mint["tx_error"]=repr(e)
            row["first_transfer"]=mint
        else:
            row["first_transfer_lookup"]=ep

        result["tokens"][str(tid)]=row

    # Fallback: if RPC metadata media failed, try media URLs embedded in OpenSea item HTML.
    if token5_media is None:
        urls=result.get("web_html",{}).get("item5",{}).get("media_urls",[])
        errs=[]
        for u in urls:
            try:
                rr=fetch(u)
                token5_media=rr.content
                result["opensea_media_fallback"]={
                    "url":u,
                    "sha256":sha256_bytes(token5_media),
                    "bytes":len(token5_media),
                }
                break
            except Exception as e:
                errs.append({"url":u,"error":repr(e)})
        if errs:
            result["opensea_media_fallback_errors"]=errs

    if token5_media:
        result["token5_image_similarity"]=image_similarity(token5_media)
        (OUT/"token5-media.bin").write_bytes(token5_media)
    else:
        result["token5_image_similarity"]={"error":"token #5 media unavailable from tokenURI and OpenSea HTML fallbacks"}

    # Provenance interpretation.
    mint5=result["tokens"].get("5",{}).get("first_transfer")
    metadata5=result["tokens"].get("5",{}).get("metadata") or {}
    sim=result.get("token5_image_similarity",{})
    puzzle_date="2020-04-22T14:06:21Z"
    flags={
        "mint_after_puzzle":None,
        "media_strongly_matches_puzzle":False,
        "media_byte_exact":False,
        "metadata_has_nonempty_description":bool(metadata5.get("description")),
    }
    if mint5 and mint5.get("timestamp_utc"):
        flags["mint_after_puzzle"]=mint5["timestamp_utc"]>puzzle_date
    flags["media_byte_exact"]=bool(sim.get("media_sha256") and sim.get("media_sha256")==sim.get("canonical_sha256"))
    flags["media_strongly_matches_puzzle"]=bool(
        flags["media_byte_exact"] or
        sim.get("pearson_64x64",0)>=0.95 or
        sim.get("pearson_gray",0)>=0.95
    )
    result["provenance_flags"]=flags

    if flags["mint_after_puzzle"] is True and flags["media_strongly_matches_puzzle"]:
        verdict="POST_PUBLICATION_DERIVATIVE_OR_MIRROR"
    elif flags["mint_after_puzzle"] is False and flags["media_strongly_matches_puzzle"]:
        verdict="POTENTIAL_PREPUBLICATION_SOURCE"
    elif flags["media_strongly_matches_puzzle"]:
        verdict="MATCHING_MEDIA_PROVENANCE_DATE_UNRESOLVED"
    else:
        verdict="UNRESOLVED_OR_WEAK_MEDIA_MATCH"
    result["verdict"]=verdict

    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    rows=[]
    for tid in TOKEN_IDS:
        t=result["tokens"].get(str(tid),{})
        m=t.get("metadata") or {}
        mint=t.get("first_transfer") or {}
        rows.append([
            tid,
            m.get("name"),
            m.get("description"),
            t.get("current_owner"),
            mint.get("timestamp_utc"),
            mint.get("to"),
            mint.get("tx_from"),
        ])

    md=[
        "# Stage 89 — CryptoCanvas provenance and metadata audit",
        "",
        "**Experiment:** A11-EXP-089",
        "",
        f"- Contract: `{CONTRACT}`",
        f"- Verdict: **{verdict}**",
        f"- Token #5 mint after Puzzle #11: **{flags['mint_after_puzzle']}**",
        f"- Token #5 media strongly matches canonical puzzle: **{flags['media_strongly_matches_puzzle']}**",
        f"- Token #5 media byte-exact: **{flags['media_byte_exact']}**",
        f"- Token #5 metadata has description: **{flags['metadata_has_nonempty_description']}**",
        "",
        "## Token inventory",
        "",
        "| token | name | description | current owner | first transfer UTC | first recipient | tx sender |",
        "|---:|:---|:---|:---|:---|:---|:---|",
    ]
    def esc(v):
        if v is None: return ""
        return str(v).replace("|","\\|").replace("\n"," ")
    for row in rows:
        md.append("| "+" | ".join(esc(v) for v in row)+" |")

    md += ["","## Token #5 image comparison",""]
    for k,v in result.get("token5_image_similarity",{}).items():
        md.append(f"- {k}: `{esc(v)}`")

    md += [
        "",
        "## Interpretation",
        "",
    ]
    if verdict=="POST_PUBLICATION_DERIVATIVE_OR_MIRROR":
        md.append("The on-chain collection postdates the original April 2020 puzzle and carries media strongly matching the puzzle. Without an independent identity link to Tiamat, treat CryptoCanvas as a later derivative/mirror, not author evidence. Preserve any token metadata as a historical lead only.")
    elif verdict=="POTENTIAL_PREPUBLICATION_SOURCE":
        md.append("The matching media appears on-chain before the public Puzzle #11 announcement. This would materially promote CryptoCanvas as a possible source/provenance clue and warrants identity linkage in the next stage.")
    else:
        md.append("The available public endpoints do not establish a clean provenance relationship. Do not infer an author link from the OpenSea collection alone.")

    md += [
        "",
        "Sources:",
        f"- {STACKEXCHANGE}",
        f"- {OPENSEA_COLLECTION}",
        f"- {OPENSEA_ITEM}",
        "",
        "No private-key material was generated or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-089",
        "verdict":verdict,
        "flags":flags,
    }))

if __name__=="__main__":
    main()
