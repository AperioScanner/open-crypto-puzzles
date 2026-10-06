#!/usr/bin/env python3
"""Stage 90 (corrected): CryptoCanvas closure audit.

The first Stage-90 implementation over-classified unrelated images embedded in
the current OpenSea page as token-specific evidence. This corrected rerun keeps
only token-specific sources as decisive.

Public-source provenance research only. No private-key operations.
"""
from __future__ import annotations

import hashlib, html, json, re
from io import BytesIO
from pathlib import Path

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
TOKEN5=5
BLOCKSCOUT="https://eth.blockscout.com/api/v2"
OPENSEA_ITEM=f"https://opensea.io/item/ethereum/{CONTRACT}/{TOKEN5}"

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0; public provenance audit)"})

def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def get_bytes(url,timeout=30):
    r=S.get(url,timeout=timeout,allow_redirects=True)
    r.raise_for_status()
    return r.content,{
        "url":r.url,"status":r.status_code,"bytes":len(r.content),
        "sha256":sha256(r.content),"content_type":r.headers.get("content-type","")
    }

def get_json(url,timeout=30):
    b,info=get_bytes(url,timeout)
    return json.loads(b),info

def clean_url(u):
    if not isinstance(u,str): return None
    u=html.unescape(u).replace("\\/","/").replace("\u002F","/").replace("\u002f","/")
    u=u.replace("\u0026","&").strip().strip('"').strip("'").rstrip("\\")
    if u.startswith("//"): u="https:"+u
    if u.startswith("ipfs://"): u="https://ipfs.io/ipfs/"+u[len("ipfs://"):]
    if u.startswith("ar://"): u="https://arweave.net/"+u[len("ar://"):]
    return u if u.startswith(("http://","https://")) else None

def blockscout(path):
    url=BLOCKSCOUT+path
    try:
        return get_json(url)
    except Exception as e:
        return None,{"url":url,"error":repr(e)}

def largest_bright_region(gray):
    mask=(gray>=235).astype(np.uint8)
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8),iterations=2)
    n,lab,stats,_=cv2.connectedComponentsWithStats(mask,8)
    candidates=[]
    H,W=gray.shape
    for i in range(1,n):
        x,y,w,h,area=map(int,stats[i])
        if area<0.05*H*W: continue
        candidates.append((area,(x,y,x+w,y+h)))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]

def orb_match(canonical,candidate):
    orb=cv2.ORB_create(nfeatures=5000,scaleFactor=1.2,nlevels=8,edgeThreshold=15,fastThreshold=10)
    kp1,d1=orb.detectAndCompute(canonical,None)
    kp2,d2=orb.detectAndCompute(candidate,None)
    out={"canonical_keypoints":len(kp1),"candidate_keypoints":len(kp2)}
    if d1 is None or d2 is None or len(kp1)<20 or len(kp2)<20:
        out.update({"good_matches":0,"homography_inliers":0,"inlier_fraction":0.0,"strong_match":False})
        return out
    bf=cv2.BFMatcher(cv2.NORM_HAMMING)
    pairs=bf.knnMatch(d1,d2,k=2)
    good=[m for m,n in pairs if m.distance < 0.75*n.distance]
    out["good_matches"]=len(good)
    if len(good)<8:
        out.update({"homography_inliers":0,"inlier_fraction":0.0,"strong_match":False})
        return out
    src=np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    dst=np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
    Hmat,inliers=cv2.findHomography(src,dst,cv2.RANSAC,5.0)
    inc=int(inliers.sum()) if inliers is not None else 0
    frac=inc/max(1,len(good))
    out["homography_inliers"]=inc
    out["inlier_fraction"]=float(frac)
    out["strong_match"]=bool(inc>=25 and frac>=0.45)
    return out

def compare_token_card(card_bytes):
    canonical=np.array(Image.open(SOURCE).convert("L"))
    card=np.array(Image.open(BytesIO(card_bytes)).convert("L"))
    bbox=largest_bright_region(card)
    out={
        "card_sha256":sha256(card_bytes),
        "card_shape":list(card.shape),
        "artwork_bbox":list(bbox) if bbox else None,
    }
    if not bbox:
        out["strong_match"]=False
        out["error"]="no large bright artwork region"
        return out,None
    x0,y0,x1,y1=bbox
    art=card[y0:y1,x0:x1]
    if art.shape[0]>30 and art.shape[1]>30:
        art=art[4:-4,4:-4]
    match=orb_match(canonical,art)
    out["orb"]=match
    out["strong_match"]=bool(match.get("strong_match"))
    return out,art

def extract_og_url(text):
    pats=[
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    ]
    for p in pats:
        m=re.search(p,text,re.I)
        if m:
            return clean_url(m.group(1))
    return None

def main():
    s89=json.loads(RUN89.read_text())
    mint=s89.get("tokens",{}).get("5",{}).get("first_transfer",{})
    result={
        "experiment_id":"A11-EXP-090",
        "scope":"corrected token-specific CryptoCanvas closure audit; no private-key operations",
        "implementation_correction":"Previous Stage-90 run incorrectly treated unrelated OpenSea embedded recommendation images as decisive token #5 media. This rerun restricts decisive evidence to token-specific sources.",
        "contract":CONTRACT,
        "token5_mint":mint,
        "mint_after_puzzle":True,
    }

    addr,ai=blockscout(f"/addresses/{CONTRACT}")
    smart,si=blockscout(f"/smart-contracts/{CONTRACT}")
    result["contract_address_fetch"]=ai
    result["smart_contract_fetch"]=si
    if isinstance(addr,dict):
        result["contract_creator"]=addr.get("creator_address_hash")
        result["contract_name"]=addr.get("name")
    if isinstance(smart,dict):
        result["compiler_version"]=smart.get("compiler_version")
        result["verified_at"]=smart.get("verified_at")

    inst,ii=blockscout(f"/tokens/{CONTRACT}/instances/5")
    result["token5_instance_fetch"]=ii
    result["token5_instance"]={
        "metadata":inst.get("metadata") if isinstance(inst,dict) else None,
        "image_url":inst.get("image_url") if isinstance(inst,dict) else None,
        "animation_url":inst.get("animation_url") if isinstance(inst,dict) else None,
        "external_app_url":inst.get("external_app_url") if isinstance(inst,dict) else None,
    }

    decisive=[]
    if isinstance(inst,dict):
        for key in ("image_url","animation_url"):
            u=clean_url(inst.get(key))
            if u: decisive.append({"source":f"blockscout:{key}","url":u})

    try:
        html_bytes,oi=get_bytes(OPENSEA_ITEM)
        text=html_bytes.decode("utf-8","replace")
        result["opensea_item_fetch"]=oi
        og=extract_og_url(text)
        result["token5_opengraph_url"]=og
        if og:
            card,ci=get_bytes(og)
            result["token5_opengraph_fetch"]=ci
            cmp,art=compare_token_card(card)
            result["token5_opengraph_artwork_match"]=cmp
            (OUT/"token5-opengraph-card.png").write_bytes(card)
            if art is not None:
                Image.fromarray(art).save(OUT/"token5-opengraph-artwork.png")
    except Exception as e:
        result["opensea_error"]=repr(e)

    cached=[]
    canonical=np.array(Image.open(SOURCE).convert("L"))
    for d in decisive:
        rec=dict(d)
        try:
            b,fi=get_bytes(d["url"])
            rec["fetch"]=fi
            cand=np.array(Image.open(BytesIO(b)).convert("L"))
            rec["orb"]=orb_match(canonical,cand)
        except Exception as e:
            rec["error"]=repr(e)
        cached.append(rec)
    result["token_specific_cached_media"]=cached

    ogstrong=bool(result.get("token5_opengraph_artwork_match",{}).get("strong_match"))
    cachedstrong=any((x.get("orb") or {}).get("strong_match") for x in cached)

    if ogstrong or cachedstrong:
        verdict="CONFIRMED_POSTPUBLICATION_MIRROR"
    else:
        verdict="POSTPUBLICATION_COLLECTION_NO_MEDIA_PROOF"

    result["verdict"]=verdict
    result["hypothesis_decision"]={
        "prepublication_source":"RETIRED",
        "postpublication_mirror":"CONFIRMED" if verdict=="CONFIRMED_POSTPUBLICATION_MIRROR" else "UNRESOLVED",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    cmp=result.get("token5_opengraph_artwork_match",{})
    orb=cmp.get("orb",{})
    md=[
        "# Stage 90 — corrected CryptoCanvas closure audit",
        "",
        "**Experiment:** A11-EXP-090",
        "",
        f"- Verdict: **{verdict}**",
        f"- Token #5 mint: **{mint.get('timestamp_utc')}**",
        f"- Token-specific OpenGraph artwork strong match: **{ogstrong}**",
        f"- ORB good matches: **{orb.get('good_matches')}**",
        f"- Homography inliers: **{orb.get('homography_inliers')}**",
        f"- Inlier fraction: **{orb.get('inlier_fraction')}**",
        "",
        "## Implementation correction",
        "",
        "The first Stage-90 implementation incorrectly marked every SEADN image embedded in the current OpenSea page as token-specific. Those include recommendation assets from unrelated collections and chains, so the prior MISIDENTIFIED_REVERSE_IMAGE_LEAD verdict was invalid.",
        "",
        "This rerun uses only token-specific evidence: Blockscout token #5 cached fields and the OpenSea OpenGraph card for the exact contract/token route. The OpenGraph card is segmented to its artwork rectangle and matched to the canonical puzzle with ORB + RANSAC homography.",
        "",
        "## Interpretation",
        "",
    ]
    if verdict=="CONFIRMED_POSTPUBLICATION_MIRROR":
        md.append("The token-specific OpenSea card contains artwork geometrically matching the canonical Puzzle #11 image. Combined with the July 2020 mint date, CryptoCanvas is a confirmed post-publication mirror/derivative, not the source of the April 2020 puzzle.")
    else:
        md.append("The collection definitely postdates Puzzle #11, but token-specific media evidence is insufficient to confirm the 2021 reverse-image-search report.")
    md += ["","No private-key material was generated, reconstructed or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-090","verdict":verdict,"ogstrong":ogstrong,"orb":orb}))

if __name__=="__main__":
    main()
