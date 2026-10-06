#!/usr/bin/env python3
"""Stage 96: Puzzle #9 four-step sibling reconstruction audit.

This stage uses newly surfaced public author evidence that solved sibling
Puzzle #9 "required 4 steps" and that the anonymous solver may have found three
and brute-forced one.

Goals:
- fetch the original #9 permaweb page and image assets;
- recover/verify the author tweet context through Wayback when available;
- compare #9/#11 construction at the mechanism level;
- identify new constraints for #11 without generating or checking any private
  key candidate.

No private-key derivation, enumeration, reconstruction, verification, or wallet
access is performed.
"""
from __future__ import annotations

import base64
import hashlib
import html
import io
import json
import math
import re
import struct
from pathlib import Path
from urllib.parse import urljoin

import cv2
import numpy as np
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
P11=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage96-puzzle9-four-step-audit"
OUT.mkdir(parents=True,exist_ok=True)

P9_PAGE="https://arweave.net/1--NRFY3naNwTlxBSRjzDPNUq-Cn1yLG2RmgGHZem9c"
AUTHOR_TWEET="https://twitter.com/ArweaveP/status/1272111084867129344"
CDX="https://web.archive.org/cdx/search/cdx"
MAX_ASSETS=30
MAX_BYTES=12_000_000

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0; public sibling audit)"})

def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def get_bytes(url,timeout=30):
    r=S.get(url,timeout=timeout,allow_redirects=True)
    r.raise_for_status()
    b=r.content
    if len(b)>MAX_BYTES:
        raise RuntimeError(f"asset too large: {len(b)}")
    return b,{
        "url":r.url,
        "status":r.status_code,
        "bytes":len(b),
        "content_type":r.headers.get("content-type",""),
        "sha256":sha256(b),
    }

def strip_html(s):
    s=re.sub(r"<script\b[^>]*>.*?</script>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<style\b[^>]*>.*?</style>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<br\s*/?>","\n",s,flags=re.I)
    s=re.sub(r"<[^>]+>"," ",s)
    return html.unescape(re.sub(r"\s+"," ",s)).strip()

def extract_asset_urls(text,base):
    t=html.unescape(text).replace("\\/","/")
    raw=[]
    patterns=(
        r'<img[^>]+src=["\']([^"\']+)',
        r'<img[^>]+data-src=["\']([^"\']+)',
        r'<source[^>]+src=["\']([^"\']+)',
        r'background-image\s*:\s*url\(([^)]+)\)',
        r'["\']([^"\']+\.(?:png|jpe?g|gif|webp|bmp|svg)(?:\?[^"\']*)?)["\']',
    )
    for p in patterns:
        raw.extend(re.findall(p,t,re.I))
    urls=[]
    for x in raw:
        x=x.strip().strip('"').strip("'")
        if x.startswith("data:image/"):
            urls.append(x)
            continue
        u=urljoin(base,x)
        if u.startswith(("http://","https://")):
            urls.append(u)
    seen=set(); out=[]
    for u in urls:
        if u not in seen:
            seen.add(u); out.append(u)
    return out

def decode_data_uri(uri):
    head,payload=uri.split(",",1)
    if ";base64" in head:
        return base64.b64decode(payload)
    from urllib.parse import unquote_to_bytes
    return unquote_to_bytes(payload)

def png_chunks(b):
    if not b.startswith(b"\x89PNG\r\n\x1a\n"):
        return []
    pos=8; rows=[]
    while pos+12<=len(b):
        ln=struct.unpack(">I",b[pos:pos+4])[0]
        typ=b[pos+4:pos+8].decode("latin1","replace")
        data=b[pos+8:pos+8+ln]
        rows.append({"type":typ,"length":ln,"data_preview":data[:200].decode("latin1","replace") if typ in ("tEXt","zTXt","iTXt") else None})
        pos+=12+ln
        if typ=="IEND": break
    return rows

def image_characteristics(b,label):
    im=Image.open(io.BytesIO(b))
    arr=np.array(im)
    gray=np.array(im.convert("L"))
    rec={
        "label":label,
        "format":im.format,
        "mode":im.mode,
        "size":[im.width,im.height],
        "sha256":sha256(b),
        "bytes":len(b),
        "pil_info":{str(k):str(v)[:500] for k,v in im.info.items()},
        "unique_gray_levels":int(len(np.unique(gray))),
        "gray_entropy_bits":None,
        "foreground_fraction_lt245":float(np.mean(gray<245)),
        "first_row_nonwhite_lt250":int(np.sum(gray[0,:]<250)),
        "edge_density":float(np.mean(cv2.Canny(gray,60,160)>0)),
    }
    hist=np.bincount(gray.ravel(),minlength=256).astype(float)
    p=hist[hist>0]/hist.sum()
    rec["gray_entropy_bits"]=float(-np.sum(p*np.log2(p)))
    rec["occupied_gray_bins"]=int(np.sum(hist>0))
    rec["rare_gray_bins_count_le10px"]=int(np.sum((hist>0)&(hist<=10)))

    # bitplane population + simple adjacent agreement, useful only as a
    # construction fingerprint, not as payload extraction.
    bp={}
    for bit in range(8):
        z=((gray>>bit)&1).astype(np.uint8)
        bp[str(bit)]={
            "ones_fraction":float(z.mean()),
            "horizontal_equal_fraction":float(np.mean(z[:,:-1]==z[:,1:])),
            "vertical_equal_fraction":float(np.mean(z[:-1,:]==z[1:,:])),
        }
    rec["gray_bitplanes"]=bp

    # Alpha characterization.
    if arr.ndim==3 and arr.shape[2] in (2,4):
        alpha=arr[:,:,-1].astype(np.uint8)
        rec["has_alpha"]=True
        rec["nonopaque_alpha_pixels"]=int(np.sum(alpha<255))
        rec["nonopaque_alpha_fraction"]=float(np.mean(alpha<255))
        if np.any(alpha<255):
            ys,xs=np.where(alpha<255)
            rec["alpha_bbox"]=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
            rec["alpha_min"]=int(alpha[alpha<255].min())
            rec["alpha_max_nonopaque"]=int(alpha[alpha<255].max())
            rec["alpha_unique_nonopaque"]=int(len(np.unique(alpha[alpha<255])))
    else:
        rec["has_alpha"]=False
        rec["nonopaque_alpha_pixels"]=0
        rec["nonopaque_alpha_fraction"]=0.0

    rec["png_chunks"]=png_chunks(b)
    rec["text_chunks"]=[
        x for x in rec["png_chunks"] if x["type"] in ("tEXt","zTXt","iTXt")
    ]

    # Coarse connected components and line organization.
    ink=(gray<180).astype(np.uint8)*255
    n,lab,stats,_=cv2.connectedComponentsWithStats(ink,8)
    areas=stats[1:,cv2.CC_STAT_AREA] if n>1 else np.array([],dtype=int)
    rec["ink_components_ge20"]=int(np.sum(areas>=20)) if len(areas) else 0
    lines=cv2.HoughLinesP(cv2.Canny(gray,60,160),1,np.pi/180,threshold=45,minLineLength=max(20,min(gray.shape)//15),maxLineGap=8)
    rec["long_hough_lines"]=int(0 if lines is None else len(np.asarray(lines).reshape(-1,4)))

    return rec,gray

def save_primary(b,gray):
    # Keep a bounded diagnostic copy for direct visual review.
    im=Image.open(io.BytesIO(b)).convert("RGB")
    if max(im.size)>1600:
        scale=1600/max(im.size)
        im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    im.save(OUT/"puzzle9-primary.png",format="PNG",optimize=True)

def fetch_p9():
    page_b,page_info=get_bytes(P9_PAGE)
    text=page_b.decode("utf-8","replace")
    urls=extract_asset_urls(text,page_info["url"])
    assets=[]
    for u in urls[:MAX_ASSETS]:
        rec={"url":u}
        try:
            if u.startswith("data:image/"):
                b=decode_data_uri(u)
                info={"url":"data-uri","status":200,"bytes":len(b),"sha256":sha256(b),"content_type":u.split(";",1)[0][5:]}
            else:
                b,info=get_bytes(u)
            rec["fetch"]=info
            try:
                im=Image.open(io.BytesIO(b))
                rec["image"]={
                    "format":im.format,"mode":im.mode,
                    "width":im.width,"height":im.height,
                    "area":im.width*im.height,
                }
                rec["_bytes"]=b
            except Exception as e:
                rec["decode_error"]=repr(e)
        except Exception as e:
            rec["fetch_error"]=repr(e)
        assets.append(rec)
    image_assets=[x for x in assets if x.get("image")]
    image_assets.sort(key=lambda x:(x["image"]["area"],x["fetch"]["bytes"]),reverse=True)
    primary=image_assets[0] if image_assets else None
    return {
        "page_fetch":page_info,
        "visible_text":strip_html(text)[:12000],
        "asset_urls":urls[:MAX_ASSETS],
        "assets":assets,
        "primary":primary,
    }

def recover_author_tweet():
    out={"tweet_url":AUTHOR_TWEET}
    try:
        r=S.get(CDX,params={
            "url":AUTHOR_TWEET,
            "output":"json",
            "filter":"statuscode:200",
            "fl":"timestamp,original,statuscode,digest",
            "from":"2020","to":"2022",
            "collapse":"digest",
            "limit":"50",
        },timeout=30)
        r.raise_for_status()
        j=r.json()
        rows=[]
        if isinstance(j,list) and len(j)>1:
            hdr=j[0]; rows=[dict(zip(hdr,x)) for x in j[1:]]
        out["cdx_rows"]=rows
        for row in rows[:12]:
            ts=row.get("timestamp"); orig=row.get("original")
            if not ts or not orig: continue
            snap=f"https://web.archive.org/web/{ts}id_/{orig}"
            try:
                b,info=get_bytes(snap)
                txt=strip_html(b.decode("utf-8","replace"))
                low=txt.lower()
                hit=("required 4 steps" in low or ("brute" in low and "steps" in low))
                if hit:
                    out["verified_snapshot"]={
                        "timestamp":ts,
                        "url":snap,
                        "fetch":info,
                        "text_excerpt":txt[:12000],
                        "contains_required_4_steps":"required 4 steps" in low,
                        "contains_bruteforce_word":"brute" in low,
                    }
                    break
            except Exception:
                continue
    except Exception as e:
        out["error"]=repr(e)
    return out

def compare_features(p9,p11):
    shared={}
    shared["same_native_mode"]=p9["mode"]==p11["mode"]
    shared["both_have_alpha"]=bool(p9["has_alpha"] and p11["has_alpha"])
    shared["both_png"]=bool(p9["format"]=="PNG" and p11["format"]=="PNG")

    p9_types=[x["type"] for x in p9.get("png_chunks",[])]
    p11_types=[x["type"] for x in p11.get("png_chunks",[])]
    shared["shared_png_chunk_types"]=sorted(set(p9_types)&set(p11_types))
    shared["p9_only_chunk_types"]=sorted(set(p9_types)-set(p11_types))
    shared["p11_only_chunk_types"]=sorted(set(p11_types)-set(p9_types))

    p9_text="\n".join(x.get("data_preview") or "" for x in p9.get("text_chunks",[]))
    p11_text="\n".join(x.get("data_preview") or "" for x in p11.get("text_chunks",[]))
    shared["p9_has_date_create"]="date:create" in p9_text
    shared["p9_has_date_modify"]="date:modify" in p9_text
    shared["p11_has_date_create"]="date:create" in p11_text
    shared["p11_has_date_modify"]="date:modify" in p11_text

    # Compare simple normalized descriptors; no claim of payload equivalence.
    shared["unique_gray_level_ratio_p9_to_p11"]=float(p9["unique_gray_levels"]/max(1,p11["unique_gray_levels"]))
    shared["edge_density_ratio_p9_to_p11"]=float(p9["edge_density"]/max(1e-9,p11["edge_density"]))
    shared["first_row_anomaly_fraction_p9"]=float(p9["first_row_nonwhite_lt250"]/max(1,p9["size"][0]))
    shared["first_row_anomaly_fraction_p11"]=float(p11["first_row_nonwhite_lt250"]/max(1,p11["size"][0]))

    return shared

def infer_constraints(page,primary,p9,p11,shared,tweet):
    constraints=[]

    if shared["p9_has_date_create"] and shared["p9_has_date_modify"] and shared["p11_has_date_create"] and shared["p11_has_date_modify"]:
        constraints.append({
            "rank":1,
            "constraint":"Shared create/modify metadata pattern is likely production lineage, not sufficient payload evidence.",
            "basis":"present in both #9 and #11",
        })
    if p9.get("unique_gray_levels",256)<=16:
        constraints.append({
            "rank":1,
            "constraint":"Solved #9 uses a very low-cardinality grayscale palette; quantization/visual-symbol steps deserve comparison, but exact #9 alpha encodings already failed as an oracle.",
            "basis":f"#9 unique grayscale levels={p9.get('unique_gray_levels')}",
        })
    if p9.get("has_alpha") and p11.get("has_alpha"):
        constraints.append({
            "rank":2,
            "constraint":"Alpha presence is shared construction context; treat alpha-only anomalies cautiously unless #9 shows structured nonopaque values unlike #11.",
            "basis":f"#9 nonopaque={p9.get('nonopaque_alpha_pixels')} vs #11={p11.get('nonopaque_alpha_pixels')}",
        })
    if tweet.get("verified_snapshot"):
        constraints.append({
            "rank":1,
            "constraint":"Any #11 mechanism model should permit a short multi-step pipeline with at least one bounded ambiguity/bruteforce-like step rather than a single direct readout.",
            "basis":"author's #9 four-step statement",
        })

    # Generic four-step decomposition, explicitly marked as inference.
    conceptual=[
        {"step":1,"role":"selection/where to look","status":"inferred"},
        {"step":2,"role":"extract visible/raster symbols","status":"inferred"},
        {"step":3,"role":"order/transform symbols","status":"inferred"},
        {"step":4,"role":"resolve one bounded ambiguity; author speculated brute force","status":"author-supported only for #9"},
    ]
    return sorted(constraints,key=lambda x:(x["rank"],x["constraint"])),conceptual

def main():
    p9page=fetch_p9()
    primary=p9page["primary"]
    if primary is None:
        raise SystemExit("No decodable Puzzle #9 image asset found")

    p9b=primary.pop("_bytes")
    p9char,p9gray=image_characteristics(p9b,"puzzle9_primary")
    save_primary(p9b,p9gray)

    p11b=P11.read_bytes()
    p11char,p11gray=image_characteristics(p11b,"puzzle11")

    tweet=recover_author_tweet()
    shared=compare_features(p9char,p11char)
    constraints,conceptual=infer_constraints(p9page,primary,p9char,p11char,shared,tweet)

    # Save a compact public-source page snapshot for reproducibility.
    safe_assets=[]
    for x in p9page["assets"]:
        y={k:v for k,v in x.items() if k!="_bytes"}
        safe_assets.append(y)

    result={
        "experiment_id":"A11-EXP-096",
        "scope":"Puzzle #9 public sibling construction + author four-step evidence audit; no private-key operations",
        "puzzle9_page":{
            "fetch":p9page["page_fetch"],
            "visible_text":p9page["visible_text"],
            "asset_urls":p9page["asset_urls"],
            "assets":safe_assets,
            "primary_asset":primary,
        },
        "author_four_step_evidence":tweet,
        "puzzle9_image":p9char,
        "puzzle11_image":p11char,
        "shared_construction":shared,
        "ranked_mechanism_constraints":constraints,
        "conceptual_four_step_model":conceptual,
        "interpretation_guard":"The four-step decomposition is a mechanism-level inference, not a recovered solution. No candidate key material is produced.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 96 — Puzzle #9 four-step sibling reconstruction audit",
        "",
        "**Experiment:** A11-EXP-096",
        "",
        f"- #9 page fetched: **{p9page['page_fetch']['status']==200}**",
        f"- #9 image assets decoded: **{sum(1 for x in safe_assets if x.get('image'))}**",
        f"- primary #9 image: **{primary.get('url')}**",
        f"- primary #9 mode/size: **{p9char['mode']} / {p9char['size']}**",
        f"- #9 unique grayscale levels: **{p9char['unique_gray_levels']}**",
        f"- #9 nonopaque alpha pixels: **{p9char['nonopaque_alpha_pixels']}**",
        f"- author four-step Wayback verification: **{bool(tweet.get('verified_snapshot'))}**",
        "",
        "## #9 vs #11 construction",
        "",
        f"- same native mode: **{shared['same_native_mode']}**",
        f"- both have alpha: **{shared['both_have_alpha']}**",
        f"- shared PNG chunk types: **{shared['shared_png_chunk_types']}**",
        f"- #9 date:create/date:modify: **{shared['p9_has_date_create']} / {shared['p9_has_date_modify']}**",
        f"- #11 date:create/date:modify: **{shared['p11_has_date_create']} / {shared['p11_has_date_modify']}**",
        "",
        "## Ranked mechanism constraints",
        "",
    ]
    if constraints:
        for c in constraints:
            md.append(f"- **P{c['rank']}** {c['constraint']} — {c['basis']}")
    else:
        md.append("- No new shared mechanism constraint promoted.")

    md += [
        "",
        "## Four-step model (inference, not solution)",
        "",
    ]
    for x in conceptual:
        md.append(f"{x['step']}. {x['role']} — {x['status']}")

    md += [
        "",
        "A diagnostic copy of the recovered primary #9 image is saved as `puzzle9-primary.png` for direct visual review.",
        "",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-096",
        "p9_mode":p9char["mode"],
        "p9_unique_gray":p9char["unique_gray_levels"],
        "tweet_verified":bool(tweet.get("verified_snapshot")),
        "constraint_count":len(constraints),
    }))

if __name__=="__main__":
    main()
