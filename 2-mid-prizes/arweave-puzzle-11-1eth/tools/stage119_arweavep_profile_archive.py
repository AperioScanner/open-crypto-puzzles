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
    """Bounded archive lookup with documented, exact 2020 timestamp anchors.

    The former code overwrote the statuscode filter and discarded May captures
    while the CDX itself can timeout; the known tweet archives are fallbacks.
    """
    targets=[
        "https://twitter.com/ArweaveP",
        "https://twitter.com/arweavep",
        "https://twitter.com/ArweaveP/with_replies",
    ]
    found=[]
    errors=[]
    for target in targets:
        q=urllib.parse.urlencode([
            ("url",target),
            ("from",FROM),
            ("to",TO),
            ("output","json"),
            ("filter","statuscode:200"),
            ("fl","timestamp,original,statuscode,digest"),
            ("collapse","digest"),
            ("limit","60"),
        ])
        url="https://web.archive.org/cdx/search/cdx?"+q
        try:
            obj=json.loads(fetch(url,timeout=12).decode("utf-8","replace"))
            if len(obj)>=2:
                hdr=obj[0]
                for row in obj[1:]:
                    d=dict(zip(hdr,row))
                    ts=d.get("timestamp","")
                    if FROM<=ts[:8]<=TO:
                        d["source_type"]="profile"
                        found.append(d)
        except Exception as e:
            errors.append({"url":url,"error":type(e).__name__})

    # Snapshot URLs independently documented in Stage 98.
    # These are tweet pages, not evidence of entire profile/header coverage.
    # Tweet media are deliberately excluded from image comparisons.
    known=[
        ("20200430185132","https://twitter.com/ArweaveP/status/1253354733911359491"),
        ("20200430210602","https://twitter.com/ArweaveP/status/1253375599323856896"),
        ("20200501121921","https://twitter.com/ArweaveP/status/1253253461828931584"),
        ("20200502173835","https://twitter.com/ArweaveP/status/1252961944807641090"),
    ]
    seeds=[{"timestamp":ts,"original":u,"source_type":"tweet_witness"}
           for ts,u in known if FROM<=ts[:8]<=TO]
    seen=set()
    chosen=[]
    for row in sorted(found,key=lambda x:x.get("timestamp","")):
        k=(row.get("timestamp"),row.get("original","").lower().rstrip("/"))
        if k not in seen and len(chosen)<MAX_SNAPSHOTS-len(seeds):
            seen.add(k);chosen.append(row)
    for row in seeds:
        k=(row["timestamp"],row["original"].lower().rstrip("/"))
        if k not in seen:
            seen.add(k);chosen.append(row)
    return sorted(chosen,key=lambda x:x.get("timestamp","")),errors

def extract_meta(html):
    import html as html_lib
    markup=html_lib.unescape(html).replace("\\/","/").replace("\\u002F","/")
    title=""
    m=re.search(r"<title[^>]*>(.*?)</title>",markup,re.I|re.S)
    if m:
        title=re.sub(r"\s+"," ",re.sub("<[^>]+>","",m.group(1))).strip()[:300]
    desc=[]
    for pat in [
        r'<meta[^>]+(?:name|property)=["\'](?:description|og:description|twitter:description)["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\'](?:description|og:description|twitter:description)["\']',
    ]:
        desc += re.findall(pat,markup,re.I|re.S)
    desc=[re.sub(r"\s+"," ",x).strip()[:500] for x in desc]

    urls=set()
    # Restrict *profile* experiment to avatars/banners. Tweet media could
    # contain the Puzzle #11 artwork itself: a tautological false positive.
    for u in re.findall(r'https?://[^"\'<>\s]+',markup):
        u=u.rstrip(");,\\")
        host=urllib.parse.urlparse(u).netloc.lower()
        if host=="pbs.twimg.com" and (
            "/profile_images/" in u or "/profile_banners/" in u
        ):
            urls.add(u)
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
                "timestamp":ts,"original":orig,"source_type":s.get("source_type"),"fetch_ok":False,
                "error":type(e).__name__,
            })
            continue
        title,desc,imgurls=extract_meta(html)
        plain=re.sub(r"<[^>]+>"," ",html[:200000])
        exact_handle=bool(re.search(
            r'Arweave\s+Puzzle\s*@\s*ArweaveP\b|data-screen-name=["\']ArweaveP["\']|ArweaveP.s profile',
            title+" "+" ".join(desc)+" "+plain,re.I,
        ))
        snapshot_rows.append({
            "timestamp":ts,
            "original":orig,
            "source_type":s.get("source_type"),
            "fetch_ok":True,
            "title":title,
            "descriptions":desc[:5],
            "exact_handle_seen":exact_handle,
            "image_url_count":len(imgurls),
        })
        for u in imgurls:
            assets.append((ts,u,s.get("source_type")))

    # de-dup candidate assets
    seen=set(); uniq=[]
    for ts,u,source_type in assets:
        key=re.sub(r"[?&](?:format|name)=[^&]+","",u)
        if key in seen: continue
        seen.add(key); uniq.append((ts,u,source_type))
    uniq=uniq[:MAX_IMAGES]

    image_results=[]
    for i,(ts,u,source_type) in enumerate(uniq):
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
            image_results.append({"index":i,"url":u[:500],"role":"banner" if "/profile_banners/" in u else "avatar","source_type":source_type,"fetch_ok":False})
            continue
        im=decode_image(data)
        if im is None:
            image_results.append({"index":i,"url":u[:500],"role":"banner" if "/profile_banners/" in u else "avatar","source_type":source_type,"fetch_ok":False,"decode":False})
            continue
        score=orb_score(ref,im)
        strong=bool(score["inliers"]>=25 and score["inlier_fraction"]>=0.35)
        image_results.append({
            "index":i,
            "url":u[:500],
            "role":"banner" if "/profile_banners/" in u else "avatar",
            "source_type":source_type,
            "fetch_ok":True,
            "shape":list(im.shape[:2]),
            **score,
            "strong_derivative":strong,
        })

    recovered=[x for x in snapshot_rows if x.get("fetch_ok") and x.get("exact_handle_seen")]
    profile_witnesses=[x for x in recovered if x.get("source_type")=="profile"]
    tweet_witnesses=[x for x in recovered if x.get("source_type")=="tweet_witness"]
    tested=[x for x in image_results if x.get("fetch_ok")]
    avatar_tested=sum(x.get("role")=="avatar" for x in tested)
    banner_tested=sum(x.get("role")=="banner" for x in tested)
    source_control_pass=bool(recovered and tested)
    strong_assets=[x for x in tested if x.get("strong_derivative")]
    promoted=bool(source_control_pass and control_pass and strong_assets)
    full_coverage=bool(profile_witnesses and avatar_tested and banner_tested)

    decision=(
        "PROFILE_VISUAL_DERIVATIVE" if promoted else
        "SOURCE_FAILURE" if not source_control_pass else
        "NO_PROFILE_VISUAL_DERIVATIVE" if full_coverage else
        "PARTIAL_PROFILE_COVERAGE"
    )

    result={
        "experiment_id":"A11-EXP-119",
        "scope":"Wayback audit of @ArweaveP profile/header visual context around Puzzle #11 publication; no secret/key operations",
        "date_window":[FROM,TO],
        "cdx_errors":cdx_errors,
        "snapshots_found":len(snaps),
        "snapshot_rows":snapshot_rows,
        "source_control_pass":source_control_pass,
        "profile_witness_count":len(profile_witnesses),
        "tweet_witness_count":len(tweet_witnesses),
        "avatar_assets_tested":avatar_tested,
        "banner_assets_tested":banner_tested,
        "full_profile_header_coverage":full_coverage,
        "orb_positive_control":control,
        "orb_control_pass":control_pass,
        "candidate_profile_assets":len(uniq),
        "image_results":image_results,
        "strong_derivative_count":len(strong_assets),
        "decision":decision,
        "promoted":promoted,
        "promotion_rule":"timestamped archived profile or author-tweet witness; avatar/banner image decoded; ORB control passes; >=25 RANSAC inliers and >=0.35 inlier fraction; tweet media excluded",
        "interpretation_guard":"A negative only retires direct profile/header visual reuse, not all external semantic references.",
        "safety_guard":"Public profile metadata and image similarity only. No private-key material generated or tested.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 119 — watermark-directed @ArweaveP profile/header archive audit",
        "",
        "**Experiment:** A11-EXP-119",
        "",
        f"- snapshots attempted: **{len(snaps)}**",
        f"- authenticated profile snapshots: **{len(profile_witnesses)}**",
        f"- authenticated tweet-page witnesses: **{len(tweet_witnesses)}**",
        f"- avatar/banner images decoded: **{avatar_tested}/{banner_tested}**",
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
            md.append(f"- {x.get('timestamp','?')} type={x.get('source_type')} fetch={x.get('fetch_ok')} handle={x.get('exact_handle_seen')} title={x.get('title','')!r}")
    else:
        md.append("- none")

    md += ["","## Image comparisons",""]
    if image_results:
        md += [
            "| idx | role | fetched | inliers | fraction | strong |",
            "|---:|:---|:---:|---:|---:|:---:|",
        ]
        for x in image_results:
            md.append(
                f"| {x['index']} | {x.get('role')} | {x.get('fetch_ok',False)} | {x.get('inliers',0)} | "
                f"{x.get('inlier_fraction',0.0):.3f} | {x.get('strong_derivative',False)} |"
            )
    else:
        md.append("No profile/header image assets were recoverable.")

    md += ["","## Interpretation",""]
    if not source_control_pass:
        md.append("Archive source recovery failed. Do not interpret this as a negative; repair Stage 119 under the same stage number.")
    elif promoted:
        md.append("A contemporaneous @ArweaveP profile/header asset is a strong geometric derivative of Puzzle #11. This materially promotes the watermark-directed external-context route.")
    elif not full_coverage:
        md.append("Partial coverage: only observed profile assets assessed. Do not retire unobserved profile/header layers; keep Stage 119 open unless independently corroborated.")
    else:
        md.append("Authenticated period profile, avatar and banner recovered; no strong Puzzle #11 derivative detected. Retire direct visual reuse only, not broader cross-domain semantics.")

    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-119",
        "source_control_pass":source_control_pass,
        "orb_control_pass":control_pass,
        "assets":len(uniq),
        "avatar_tested":avatar_tested,
        "banner_tested":banner_tested,
        "strong":len(strong_assets),
        "decision":decision,
    }))

if __name__=="__main__":
    main()
