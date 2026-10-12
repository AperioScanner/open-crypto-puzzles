#!/usr/bin/env python3
"""Stage 119: watermark-directed @ArweaveP profile/header archive audit.

Puzzle #11 visibly contains "twitter.com/ArweaveP". Stage 117 independently
promoted visible-symbol reading + cross-domain conversion as recurrent author
mechanisms. Earlier archive stages reconstructed posts/replies, not the profile
visual layer.

This stage asks only whether the contemporaneous profile/header imagery reused
or materially contained the Puzzle #11 artwork.

Safe public-source experiment. No private-key operations.
"""
from __future__ import annotations

import io, json, re, urllib.parse, urllib.request
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
P11=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage119-arweavep-profile-archive"
OUT.mkdir(parents=True,exist_ok=True)

UA="Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0)"
FROM="20200420"
TO="20200502"
MAX_SNAPSHOTS=10
MAX_IMAGES=24

def fetch(url,timeout=22):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def text_fetch(url):
    return fetch(url).decode("utf-8","replace")

def cdx_urls():
    targets=[
        "twitter.com/ArweaveP",
        "twitter.com/ArweaveP/",
        "twitter.com/ArweaveP/with_replies",
    ]
    rows=[]
    errors=[]
    for target in targets:
        q=urllib.parse.urlencode({
            "url":target,
            "from":FROM[:4],
            "to":TO[:4],
            "output":"json",
            "filter":"statuscode:200",
            "filter":"timestamp:"+FROM[:6]+"*",
            "collapse":"digest",
        },doseq=True)
        url="https://web.archive.org/cdx/search/cdx?"+q
        try:
            obj=json.loads(text_fetch(url))
            if len(obj)>=2:
                hdr=obj[0]
                for row in obj[1:]:
                    d=dict(zip(hdr,row))
                    ts=d.get("timestamp","")
                    if FROM<=ts[:8]<=TO:
                        rows.append(d)
        except Exception as e:
            errors.append({"url":url,"error":type(e).__name__})
    # de-dup by timestamp+original
    seen=set(); out=[]
    for r in sorted(rows,key=lambda x:x.get("timestamp","")):
        k=(r.get("timestamp"),r.get("original"))
        if k in seen: continue
        seen.add(k); out.append(r)
    return out[:MAX_SNAPSHOTS],errors

def extract_meta(html):
    title=""
    m=re.search(r"<title[^>]*>(.*?)</title>",html,re.I|re.S)
    if m:
        title=re.sub(r"\s+"," ",re.sub("<[^>]+>","",m.group(1))).strip()[:300]
    desc=[]
    for pat in [
        r'<meta[^>]+(?:name|property)=["\'](?:description|og:description|twitter:description)["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\'](?:description|og:description|twitter:description)["\']',
    ]:
        desc += re.findall(pat,html,re.I|re.S)
    desc=[re.sub(r"\s+"," ",x).strip()[:500] for x in desc]

    urls=set()
    # Profile/header CDN references and social card images.
    for u in re.findall(r'https?://[^"\'<>\s]+',html):
        uu=u.replace("&amp;","&")
        if ("pbs.twimg.com/profile_images/" in uu or
            "pbs.twimg.com/profile_banners/" in uu or
            "pbs.twimg.com/media/" in uu):
            urls.add(uu)
    for pat in [
        r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image(?::src)?)["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image(?::src)?)["\']',
    ]:
        for u in re.findall(pat,html,re.I|re.S):
            if u.startswith("http"):
                urls.add(u.replace("&amp;","&"))
    return title,desc,sorted(urls)

def archive_asset_url(ts,url):
    # Strip an existing Wayback wrapper if present.
    m=re.search(r"https?://web\.archive\.org/web/\d+(?:[a-z_]+)?/(https?://.*)",url)
    if m:
        url=m.group(1)
    return f"https://web.archive.org/web/{ts}id_/{url}"

def decode_image(data):
    try:
        return np.array(Image.open(io.BytesIO(data)).convert("RGB"))
    except Exception:
        return None

def orb_score(ref_rgb,cand_rgb):
    rg=cv2.cvtColor(ref_rgb,cv2.COLOR_RGB2GRAY)
    cg=cv2.cvtColor(cand_rgb,cv2.COLOR_RGB2GRAY)
    orb=cv2.ORB_create(nfeatures=5000,scaleFactor=1.2,nlevels=8)
    k1,d1=orb.detectAndCompute(rg,None)
    k2,d2=orb.detectAndCompute(cg,None)
    if d1 is None or d2 is None or len(k1)<8 or len(k2)<8:
        return {"good_matches":0,"inliers":0,"inlier_fraction":0.0}
    bf=cv2.BFMatcher(cv2.NORM_HAMMING)
    knn=bf.knnMatch(d1,d2,k=2)
    good=[a for a,b in knn if a.distance<0.75*b.distance]
    inliers=0
    if len(good)>=6:
        src=np.float32([k1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
        dst=np.float32([k2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
        H,mask=cv2.findHomography(src,dst,cv2.RANSAC,5.0)
        if mask is not None:
            inliers=int(mask.ravel().sum())
    return {
        "good_matches":len(good),
        "inliers":inliers,
        "inlier_fraction":float(inliers/max(1,len(good))),
    }

def positive_control(ref):
    # Resize and crop a large central area, simulating a profile/header derivative.
    h,w=ref.shape[:2]
    c=ref[int(.08*h):int(.82*h),int(.06*w):int(.94*w)]
    c=cv2.resize(c,(900,420),interpolation=cv2.INTER_AREA)
    return orb_score(ref,c)

def main():
    ref=np.array(Image.open(P11).convert("RGB"))
    control=positive_control(ref)
    control_pass=bool(control["inliers"]>=25 and control["inlier_fraction"]>=0.35)

    snaps,cdx_errors=cdx_urls()
    snapshot_rows=[]
    assets=[]
    for s in snaps:
        ts=s.get("timestamp","")
        orig=s.get("original","https://twitter.com/ArweaveP")
        way=f"https://web.archive.org/web/{ts}id_/{orig}"
        try:
            html=text_fetch(way)
        except Exception as e:
            snapshot_rows.append({
                "timestamp":ts,"original":orig,"fetch_ok":False,
                "error":type(e).__name__,
            })
            continue
        title,desc,imgurls=extract_meta(html)
        exact_handle=bool(re.search(r"ArweaveP",title+" "+" ".join(desc)+" "+html[:200000],re.I))
        snapshot_rows.append({
            "timestamp":ts,
            "original":orig,
            "fetch_ok":True,
            "title":title,
            "descriptions":desc[:5],
            "exact_handle_seen":exact_handle,
            "image_url_count":len(imgurls),
        })
        for u in imgurls:
            assets.append((ts,u))

    # de-dup candidate assets
    seen=set(); uniq=[]
    for ts,u in assets:
        key=re.sub(r"[?&](?:format|name)=[^&]+","",u)
        if key in seen: continue
        seen.add(key); uniq.append((ts,u))
    uniq=uniq[:MAX_IMAGES]

    image_results=[]
    for i,(ts,u) in enumerate(uniq):
        candidates=[archive_asset_url(ts,u),u]
        data=None; src=None
        for cu in candidates:
            try:
                data=fetch(cu,timeout=18)
                src=cu
                break
            except Exception:
                pass
        if data is None:
            image_results.append({"index":i,"url":u[:500],"fetch_ok":False})
            continue
        im=decode_image(data)
        if im is None:
            image_results.append({"index":i,"url":u[:500],"fetch_ok":False,"decode":False})
            continue
        score=orb_score(ref,im)
        strong=bool(score["inliers"]>=25 and score["inlier_fraction"]>=0.35)
        image_results.append({
            "index":i,
            "url":u[:500],
            "fetch_ok":True,
            "shape":list(im.shape[:2]),
            **score,
            "strong_derivative":strong,
        })

    recovered=[x for x in snapshot_rows if x.get("fetch_ok") and x.get("exact_handle_seen")]
    source_control_pass=bool(recovered)
    strong_assets=[x for x in image_results if x.get("strong_derivative")]
    promoted=bool(source_control_pass and control_pass and strong_assets)

    decision=(
        "PROFILE_VISUAL_DERIVATIVE"
        if promoted else
        "SOURCE_FAILURE"
        if not source_control_pass else
        "NO_PROFILE_VISUAL_DERIVATIVE"
    )

    result={
        "experiment_id":"A11-EXP-119",
        "scope":"Wayback audit of @ArweaveP profile/header visual context around Puzzle #11 publication; no secret/key operations",
        "date_window":[FROM,TO],
        "cdx_errors":cdx_errors,
        "snapshots_found":len(snaps),
        "snapshot_rows":snapshot_rows,
        "source_control_pass":source_control_pass,
        "orb_positive_control":control,
        "orb_control_pass":control_pass,
        "candidate_profile_assets":len(uniq),
        "image_results":image_results,
        "strong_derivative_count":len(strong_assets),
        "decision":decision,
        "promoted":promoted,
        "promotion_rule":"timestamped exact-handle archive snapshot recovered; transformed-canonical ORB control passes; at least one contemporaneous profile/header/media asset has >=25 RANSAC inliers and >=0.35 inlier fraction to canonical Puzzle #11",
        "interpretation_guard":"A negative only retires direct profile/header visual reuse, not all external semantic references.",
        "safety_guard":"Public profile metadata and image similarity only. No private-key material generated or tested.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 119 — watermark-directed @ArweaveP profile/header archive audit",
        "",
        "**Experiment:** A11-EXP-119",
        "",
        f"- snapshots found: **{len(snaps)}**",
        f"- exact-handle source control: **{source_control_pass}**",
        f"- ORB positive control: **{control_pass}** ({control['inliers']} inliers, {control['inlier_fraction']:.3f})",
        f"- profile/header/media assets tested: **{len(uniq)}**",
        f"- strong Puzzle #11 derivatives: **{len(strong_assets)}**",
        f"- decision: **{decision}**",
        "",
        "## Snapshot metadata",
        "",
    ]
    if snapshot_rows:
        for x in snapshot_rows:
            md.append(f"- {x.get('timestamp','?')} fetch={x.get('fetch_ok')} handle={x.get('exact_handle_seen')} title={x.get('title','')!r}")
    else:
        md.append("- none")

    md += ["","## Image comparisons",""]
    if image_results:
        md += [
            "| idx | fetched | inliers | fraction | strong |",
            "|---:|:---:|---:|---:|:---:|",
        ]
        for x in image_results:
            md.append(
                f"| {x['index']} | {x.get('fetch_ok',False)} | {x.get('inliers',0)} | "
                f"{x.get('inlier_fraction',0.0):.3f} | {x.get('strong_derivative',False)} |"
            )
    else:
        md.append("No profile/header image assets were recoverable.")

    md += ["","## Interpretation",""]
    if not source_control_pass:
        md.append("Archive source recovery failed. Do not interpret this as a negative; repair Stage 119 under the same stage number.")
    elif promoted:
        md.append("A contemporaneous @ArweaveP profile/header asset is a strong geometric derivative of Puzzle #11. This materially promotes the watermark-directed external-context route.")
    else:
        md.append("The contemporaneous profile archive was recovered, but no profile/header asset is a strong visual derivative of Puzzle #11. Retire direct profile/header visual reuse while keeping broader cross-domain semantics open.")

    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-119",
        "source_control_pass":source_control_pass,
        "orb_control_pass":control_pass,
        "assets":len(uniq),
        "strong":len(strong_assets),
        "decision":decision,
    }))

if __name__=="__main__":
    main()
