#!/usr/bin/env python3
"""Stage 90: CryptoCanvas closure audit.

Public-source provenance research only. This stage closes the post-publication
CryptoCanvas branch by looking for cached token #5 metadata/media and contract
deployment provenance.

No private-key generation, derivation, reconstruction, enumeration, verification,
or wallet access is performed.
"""
from __future__ import annotations

import html
import json
import re
import hashlib
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote

import cv2
import numpy as np
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
RUN89=ROOT/"analysis"/"runs"/"stage89-cryptocanvas-provenance"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage90-cryptocanvas-closure"
OUT.mkdir(parents=True,exist_ok=True)

CONTRACT="0x0b0b70905137786cf705102c194a1b4916d8c4d0"
TOKEN_IDS=[1,2,3,4,5]
TOKEN5=5
BLOCKSCOUT="https://eth.blockscout.com/api/v2"
OPENSEA_ITEM=f"https://opensea.io/item/ethereum/{CONTRACT}/{TOKEN5}"
ARCHIVE_CDX="https://web.archive.org/cdx/search/cdx"
MAX_IMAGE_CANDIDATES=60
MAX_ARCHIVE_SNAPSHOTS=24

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0; public provenance audit)"})

def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def get_json(url,params=None,timeout=30):
    r=S.get(url,params=params,timeout=timeout,allow_redirects=True)
    r.raise_for_status()
    return r.json(),{"url":r.url,"status":r.status_code,"bytes":len(r.content),"sha256":sha256(r.content)}

def get_bytes(url,timeout=30):
    r=S.get(url,timeout=timeout,allow_redirects=True)
    r.raise_for_status()
    return r.content,{
        "url":r.url,
        "status":r.status_code,
        "bytes":len(r.content),
        "sha256":sha256(r.content),
        "content_type":r.headers.get("content-type",""),
    }

def clean_url(u):
    if not isinstance(u,str):
        return None
    u=html.unescape(u)
    u=u.replace("\\/","/")
    u=u.replace("\u002F","/").replace("\u002f","/")
    u=u.replace("\u0026","&")
    u=u.strip().strip('"').strip("'").rstrip("\\")
    if u.startswith("//"):
        u="https:"+u
    if u.startswith("ipfs://"):
        return "https://ipfs.io/ipfs/"+u[len("ipfs://"):]
    if u.startswith("ar://"):
        return "https://arweave.net/"+u[len("ar://"):]
    if u.startswith("http://") or u.startswith("https://"):
        return u
    return None

def candidate_urls_from_obj(obj):
    out=[]
    def walk(x,path=""):
        if isinstance(x,dict):
            for k,v in x.items():
                walk(v,f"{path}.{k}" if path else str(k))
        elif isinstance(x,list):
            for i,v in enumerate(x):
                walk(v,f"{path}[{i}]")
        elif isinstance(x,str):
            u=clean_url(x)
            if u and (re.search(r"\.(?:png|jpe?g|webp|gif)(?:\?|$)",u,re.I) or any(z in path.lower() for z in ("image","media","animation","content","asset"))):
                out.append((path,u))
    walk(obj)
    seen=set(); ans=[]
    for path,u in out:
        if u in seen: continue
        seen.add(u); ans.append({"path":path,"url":u})
    return ans

def parse_urls_from_html(text):
    # Normalize common JSON/HTML escaping first.
    t=html.unescape(text).replace("\\/","/").replace("\u002F","/").replace("\u002f","/").replace("\u0026","&")
    urls=re.findall(r"https?://[^\s\"'<>]+",t)
    out=[]
    seen=set()
    for raw in urls:
        u=clean_url(raw)
        if not u or u in seen:
            continue
        if re.search(r"\.(?:png|jpe?g|webp|gif)(?:\?|$)",u,re.I) or "image" in u.lower() or "media" in u.lower():
            seen.add(u); out.append(u)
    return out

def dhash(gray,hash_size=16):
    im=Image.fromarray(gray).resize((hash_size+1,hash_size),Image.Resampling.LANCZOS)
    a=np.asarray(im,dtype=np.int16)
    bits=(a[:,1:]>a[:,:-1]).ravel()
    return bits

def image_metrics(b:bytes):
    original=np.asarray(Image.open(SOURCE).convert("L"))
    cand=np.asarray(Image.open(BytesIO(b)).convert("L"))
    out={
        "sha256":sha256(b),
        "shape":[int(cand.shape[0]),int(cand.shape[1])],
        "canonical_shape":[int(original.shape[0]),int(original.shape[1])],
    }
    a=np.asarray(Image.fromarray(original).resize((64,64),Image.Resampling.LANCZOS),dtype=float)
    c=np.asarray(Image.fromarray(cand).resize((64,64),Image.Resampling.LANCZOS),dtype=float)
    if a.std()>1e-9 and c.std()>1e-9:
        out["pearson64"]=float(np.corrcoef(a.ravel(),c.ravel())[0,1])
    else:
        out["pearson64"]=0.0
    da=dhash(original); dc=dhash(cand)
    out["dhash256_hamming"]=int(np.sum(da!=dc))
    out["aspect_ratio_delta"]=float(abs((cand.shape[1]/cand.shape[0])-(original.shape[1]/original.shape[0])))
    out["strong_match"]=bool(out["pearson64"]>=0.90 or out["dhash256_hamming"]<=20)
    out["clear_nonmatch"]=bool(out["pearson64"]<=0.35 and out["dhash256_hamming"]>=75)
    return out

def blockscout_get(path):
    url=BLOCKSCOUT+path
    try:
        return get_json(url)
    except Exception as e:
        return None,{"url":url,"error":repr(e)}

def resolve_tx(txhash):
    if not txhash:
        return None
    j,info=blockscout_get(f"/transactions/{txhash}")
    if not isinstance(j,dict):
        return {"fetch":info}
    return {
        "hash":j.get("hash"),
        "from":(j.get("from") or {}).get("hash") if isinstance(j.get("from"),dict) else j.get("from"),
        "to":(j.get("to") or {}).get("hash") if isinstance(j.get("to"),dict) else j.get("to"),
        "timestamp":j.get("timestamp"),
        "block":j.get("block"),
        "status":j.get("status"),
        "method":j.get("method"),
        "fetch":info,
    }

def archive_index():
    try:
        j,info=get_json(ARCHIVE_CDX,params={
            "url":"cryptocanvas.xyz/*",
            "output":"json",
            "fl":"timestamp,original,statuscode,mimetype,digest",
            "filter":"statuscode:200",
            "from":"2020",
            "to":"2021",
            "collapse":"digest",
            "limit":"500",
        },timeout=35)
        if not isinstance(j,list) or len(j)<2:
            return [],info
        header=j[0]
        rows=[dict(zip(header,row)) for row in j[1:]]
        return rows,info
    except Exception as e:
        return [],{"url":ARCHIVE_CDX,"error":repr(e)}

def fetch_archive_snapshot(timestamp,original):
    url=f"https://web.archive.org/web/{timestamp}id_/{original}"
    try:
        b,info=get_bytes(url,timeout=35)
        return b,info
    except Exception as e:
        return None,{"url":url,"error":repr(e)}

def add_candidate(store,url,source_kind,source_ref,decisive=False):
    u=clean_url(url)
    if not u: return
    if u in store: 
        store[u]["sources"].append({"kind":source_kind,"ref":source_ref,"decisive":decisive})
        store[u]["decisive"]=store[u]["decisive"] or decisive
        return
    store[u]={
        "url":u,
        "sources":[{"kind":source_kind,"ref":source_ref,"decisive":decisive}],
        "decisive":decisive,
    }

def main():
    r89=json.loads(RUN89.read_text())
    result={
        "experiment_id":"A11-EXP-090",
        "scope":"close CryptoCanvas post-publication mirror lead using indexed cached metadata/media and deployment provenance; no private-key operations",
        "stage89_token5_mint_utc":r89.get("tokens",{}).get("5",{}).get("first_transfer",{}).get("timestamp_utc"),
        "contract":CONTRACT,
        "blockscout":{},
        "tokens":{},
        "archive":{},
    }

    # Contract/address provenance.
    address,address_info=blockscout_get(f"/addresses/{CONTRACT}")
    smart,smart_info=blockscout_get(f"/smart-contracts/{CONTRACT}")
    result["blockscout"]["address_fetch"]=address_info
    result["blockscout"]["smart_contract_fetch"]=smart_info

    if isinstance(address,dict):
        keep=("hash","name","is_contract","is_verified","creation_tx_hash","creator_address_hash","coin_balance","has_beacon_chain_withdrawals")
        result["blockscout"]["address"]={k:address.get(k) for k in keep if k in address}
    if isinstance(smart,dict):
        keep=("name","compiler_version","optimization_enabled","verified_at","is_verified","creator_address_hash","creation_tx_hash","language","evm_version","license_type")
        result["blockscout"]["smart_contract"]={k:smart.get(k) for k in keep if k in smart}

    creation_hash=None
    for src in (address if isinstance(address,dict) else {}, smart if isinstance(smart,dict) else {}):
        for key in ("creation_tx_hash","creation_transaction_hash"):
            if src.get(key):
                creation_hash=src[key]
                break
        if creation_hash: break
    result["blockscout"]["creation_transaction"]=resolve_tx(creation_hash)

    candidates={}

    # Indexed token instances, including cached metadata/image.
    for tid in TOKEN_IDS:
        inst,info=blockscout_get(f"/tokens/{CONTRACT}/instances/{tid}")
        row={"token_id":tid,"fetch":info}
        if isinstance(inst,dict):
            row["owner"]=(inst.get("owner") or {}).get("hash") if isinstance(inst.get("owner"),dict) else inst.get("owner")
            row["metadata"]=inst.get("metadata")
            row["image_url"]=inst.get("image_url")
            row["external_app_url"]=inst.get("external_app_url")
            row["animation_url"]=inst.get("animation_url")
            row["is_unique"]=inst.get("is_unique")
            row["token_type"]=inst.get("token_type")
            for x in candidate_urls_from_obj(inst):
                decisive=(tid==TOKEN5 and any(k in x["path"].lower() for k in ("metadata","image_url","animation")))
                add_candidate(candidates,x["url"],"blockscout_token_instance",f"token:{tid}:{x['path']}",decisive=decisive)
        # Reuse confirmed first mint hash from Stage89 and resolve sender via Blockscout.
        mint=r89.get("tokens",{}).get(str(tid),{}).get("first_transfer",{})
        row["mint"]=mint
        row["mint_transaction"]=resolve_tx(mint.get("transaction_hash"))
        result["tokens"][str(tid)]=row

    # Current OpenSea item HTML: collect every embedded image/media URL, excluding
    # only known static framework assets from being decisive.
    try:
        b,info=get_bytes(OPENSEA_ITEM)
        text=b.decode("utf-8","replace")
        result["opensea_fetch"]=info
        urls=parse_urls_from_html(text)
        result["opensea_embedded_image_url_count"]=len(urls)
        result["opensea_embedded_image_urls"]=urls[:80]
        for u in urls[:80]:
            low=u.lower()
            if any(x in low for x in ("favicon","logo","sprite","icon")):
                continue
            decisive=("seadn.io" in low or "/nft/" in low or "/media/" in low)
            add_candidate(candidates,u,"opensea_embedded","item5",decisive=decisive)
    except Exception as e:
        result["opensea_error"]=repr(e)

    # Internet Archive wildcard inventory. Focus on token 5 API/media-like paths.
    rows,archive_info=archive_index()
    result["archive"]["index_fetch"]=archive_info
    result["archive"]["row_count"]=len(rows)
    result["archive"]["rows"]=rows[:200]
    relevant=[]
    for row in rows:
        u=row.get("original","")
        low=u.lower()
        if ("token/5" in low or "/5" in low or re.search(r"\.(png|jpe?g|webp|gif)(\?|$)",low)):
            relevant.append(row)
    result["archive"]["relevant_rows"]=relevant[:100]

    for row in relevant[:MAX_ARCHIVE_SNAPSHOTS]:
        ts=row.get("timestamp"); orig=row.get("original")
        if not ts or not orig: continue
        snap,si=fetch_archive_snapshot(ts,orig)
        if not snap:
            continue
        mime=(row.get("mimetype") or "").lower()
        if "json" in mime or "token/5" in orig.lower():
            try:
                obj=json.loads(snap.decode("utf-8","replace"))
                result["archive"].setdefault("token5_json_snapshots",[]).append({
                    "timestamp":ts,"original":orig,"fetch":si,"json":obj
                })
                for x in candidate_urls_from_obj(obj):
                    add_candidate(candidates,x["url"],"wayback_token5_json",f"{ts}:{orig}:{x['path']}",decisive=True)
            except Exception:
                pass
        if mime.startswith("image/") or re.search(r"\.(png|jpe?g|webp|gif)(\?|$)",orig,re.I):
            # Snapshot itself can be a decisive candidate only when its URL is token5-linked;
            # otherwise it is merely an archive image lead.
            u=si.get("url")
            if u:
                add_candidate(candidates,u,"wayback_image",f"{ts}:{orig}",decisive=("token/5" in orig.lower()))

    # Bounded candidate download and image comparison.
    scored=[]
    for i,(u,row) in enumerate(list(candidates.items())[:MAX_IMAGE_CANDIDATES]):
        rec={**row}
        try:
            b,fi=get_bytes(u,timeout=25)
            rec["fetch"]=fi
            try:
                rec["metrics"]=image_metrics(b)
            except Exception as ie:
                rec["image_decode_error"]=repr(ie)
        except Exception as e:
            rec["fetch_error"]=repr(e)
        scored.append(rec)

    def rank_key(x):
        m=x.get("metrics") or {}
        return (-float(m.get("pearson64",-2.0)), int(m.get("dhash256_hamming",999)))
    scored.sort(key=rank_key)
    result["image_candidates_tested"]=len(scored)
    result["image_candidates"]=scored
    result["top_image_candidates"]=scored[:15]

    strong=[x for x in scored if (x.get("metrics") or {}).get("strong_match")]
    strong_decisive=[x for x in strong if x.get("decisive")]
    decisive_scored=[x for x in scored if x.get("decisive") and x.get("metrics")]
    clear_decisive_nonmatches=[x for x in decisive_scored if x["metrics"].get("clear_nonmatch")]

    mint_after=True  # established by Stage 89
    if strong_decisive:
        verdict="CONFIRMED_POSTPUBLICATION_MIRROR"
    elif decisive_scored and len(clear_decisive_nonmatches)==len(decisive_scored):
        verdict="MISIDENTIFIED_REVERSE_IMAGE_LEAD"
    else:
        verdict="POSTPUBLICATION_COLLECTION_NO_MEDIA_PROOF"

    result["verdict"]=verdict
    result["strong_matches"]=strong[:20]
    result["strong_decisive_matches"]=strong_decisive[:20]
    result["decisive_candidates_scored"]=len(decisive_scored)
    result["clear_decisive_nonmatches"]=len(clear_decisive_nonmatches)
    result["interpretation_guard"]="Addresses are provenance identifiers only; no identity attribution is inferred without independent public evidence."

    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 90 — CryptoCanvas closure audit",
        "",
        "**Experiment:** A11-EXP-090",
        "",
        f"- Verdict: **{verdict}**",
        f"- Token #5 mint: **{result['stage89_token5_mint_utc']}**",
        f"- Image candidates tested: **{len(scored)}**",
        f"- Decisive original-media candidates successfully scored: **{len(decisive_scored)}**",
        f"- Strong decisive matches to Puzzle #11: **{len(strong_decisive)}**",
        "",
        "## Contract provenance",
        "",
        f"- address record: `{result['blockscout'].get('address')}`",
        f"- smart-contract record: `{result['blockscout'].get('smart_contract')}`",
        f"- creation transaction: `{result['blockscout'].get('creation_transaction')}`",
        "",
        "## Mint transactions",
        "",
        "| token | mint UTC | mint recipient | tx sender |",
        "|---:|:---|:---|:---|",
    ]
    for tid in TOKEN_IDS:
        row=result["tokens"].get(str(tid),{})
        mint=row.get("mint") or {}
        tx=row.get("mint_transaction") or {}
        md.append(f"| {tid} | {mint.get('timestamp_utc','')} | {mint.get('to','')} | {tx.get('from','')} |")

    md += [
        "",
        "## Best recovered image candidates",
        "",
        "| source | decisive | pearson64 | dHash/256 | strong | URL |",
        "|:---|:---:|---:|---:|:---:|:---|",
    ]
    for x in scored[:12]:
        m=x.get("metrics") or {}
        src=",".join(z.get("kind","") for z in x.get("sources",[])[:2])
        url=x.get("url","").replace("|","%7C")
        md.append(f"| {src} | {x.get('decisive')} | {m.get('pearson64','')} | {m.get('dhash256_hamming','')} | {m.get('strong_match','')} | {url} |")

    md += ["","## Interpretation",""]
    if verdict=="CONFIRMED_POSTPUBLICATION_MIRROR":
        md.append("Recovered token #5 media strongly matches the canonical puzzle image, but the NFT mint occurred months after Puzzle #11. CryptoCanvas is therefore a confirmed post-publication mirror/derivative, not a source clue.")
    elif verdict=="MISIDENTIFIED_REVERSE_IMAGE_LEAD":
        md.append("Recovered token #5 media is decisively different from the canonical puzzle image. The 2021 reverse-image-search association is treated as a misidentification.")
    else:
        md.append("The collection definitely postdates Puzzle #11, but no authoritative original token #5 media was recovered strongly enough to validate or falsify the reverse-image-search report. The CryptoCanvas branch is closed as non-source evidence.")

    md += [
        "",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-090",
        "verdict":verdict,
        "tested":len(scored),
        "strong_decisive":len(strong_decisive),
        "decisive_scored":len(decisive_scored),
    }))

if __name__=="__main__":
    main()
