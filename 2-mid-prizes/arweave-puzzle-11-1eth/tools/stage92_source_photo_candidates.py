#!/usr/bin/env python3
"""Stage 92: bounded source-photo candidate audit.

Tests the highest-priority genuinely untested historical claim from corrected
Stage 91: the harbor sketch may derive from an identifiable source photograph.

Scope is deliberately bounded:
- the exact Courageous Sailing racing page linked by a 2021 solver;
- 2019-2021 Wayback snapshots of that page and their image assets;
- a small Wikimedia Commons pool for Boston Harbor / sailing-race / skyline;
- a small unrelated-photo null pool.

Photo-to-sketch comparison uses geometry, not color semantics:
SIFT on grayscale, ORB on Canny edges, RANSAC homography, and post-homography
edge coverage. A transformed canonical-image positive control validates the
matcher.

No candidate private keys are generated, derived, reconstructed, enumerated,
verified, or tested.
"""
from __future__ import annotations

import html
import json
import math
import re
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin

import cv2
import numpy as np
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage92-source-photo-candidates"
OUT.mkdir(parents=True,exist_ok=True)

COURAGEOUS="https://courageoussailing.org/sailing/racing/"
CDX="https://web.archive.org/cdx/search/cdx"
COMMONS_API="https://commons.wikimedia.org/w/api.php"
MAX_CANDIDATES=110
MAX_BYTES=12_000_000

SEARCH_QUERIES=[
    "Boston Harbor sailing race skyline",
    "Boston sailboats skyline harbor",
    "sailing race city skyline",
    "Boston Harbor sailboats",
]
NULL_QUERY="mountain landscape photograph"

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0; public source-photo audit)"})

def clean_url(u,base=None):
    if not isinstance(u,str): return None
    u=html.unescape(u).strip().strip('"').strip("'").replace("\\/","/")
    if not u: return None
    if base: u=urljoin(base,u)
    if u.startswith("//"): u="https:"+u
    if not u.startswith(("http://","https://")): return None
    return u

def get_bytes(url,timeout=28):
    r=S.get(url,timeout=timeout,allow_redirects=True)
    r.raise_for_status()
    b=r.content
    if len(b)>MAX_BYTES:
        raise RuntimeError(f"asset too large: {len(b)}")
    return b,{"url":r.url,"status":r.status_code,"bytes":len(b),"content_type":r.headers.get("content-type","")}

def get_json(url,params=None,timeout=30):
    r=S.get(url,params=params,timeout=timeout)
    r.raise_for_status()
    return r.json(),{"url":r.url,"status":r.status_code,"bytes":len(r.content)}

def extract_image_urls(text,base):
    t=html.unescape(text).replace("\\/","/")
    raw=[]
    for pat in (
        r'<img[^>]+src=["\']([^"\']+)',
        r'<img[^>]+data-src=["\']([^"\']+)',
        r'<source[^>]+srcset=["\']([^"\']+)',
        r'<img[^>]+srcset=["\']([^"\']+)',
        r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    ):
        raw.extend(re.findall(pat,t,re.I))
    urls=[]
    for x in raw:
        # srcset may hold multiple "url 2x" entries.
        for part in x.split(","):
            u=part.strip().split(" ")[0]
            u=clean_url(u,base)
            if not u: continue
            low=u.lower()
            if any(z in low for z in (".png",".jpg",".jpeg",".webp",".gif","image","upload")):
                urls.append(u)
    seen=set(); out=[]
    for u in urls:
        if u not in seen:
            seen.add(u); out.append(u)
    return out

def courageous_current():
    out=[]
    meta={}
    try:
        b,info=get_bytes(COURAGEOUS)
        text=b.decode("utf-8","replace")
        urls=extract_image_urls(text,info["url"])
        meta={"fetch":info,"image_count":len(urls)}
        for u in urls[:50]:
            out.append({"url":u,"source":"courageous_current","ref":info["url"]})
    except Exception as e:
        meta={"error":repr(e)}
    return out,meta

def courageous_archive():
    out=[]; meta={}
    try:
        j,info=get_json(CDX,params={
            "url":COURAGEOUS,
            "output":"json",
            "fl":"timestamp,original,statuscode,digest",
            "filter":"statuscode:200",
            "from":"2019","to":"2021",
            "collapse":"digest",
            "limit":"30",
        })
        rows=[]
        if isinstance(j,list) and len(j)>1:
            hdr=j[0]
            rows=[dict(zip(hdr,x)) for x in j[1:]]
        meta={"index_fetch":info,"snapshots":len(rows)}
        # Sample early/middle/late distinct snapshots, max 8.
        if len(rows)>8:
            idx=np.linspace(0,len(rows)-1,8,dtype=int)
            rows=[rows[int(i)] for i in idx]
        for row in rows:
            ts=row.get("timestamp")
            orig=row.get("original") or COURAGEOUS
            if not ts: continue
            snap=f"https://web.archive.org/web/{ts}id_/{orig}"
            try:
                b,si=get_bytes(snap)
                text=b.decode("utf-8","replace")
                urls=extract_image_urls(text,orig)
                # Try current asset URL and archive replay of that exact asset.
                for u in urls[:35]:
                    out.append({"url":u,"source":"courageous_archive_asset_current","ref":snap})
                    out.append({"url":f"https://web.archive.org/web/{ts}id_/{u}","source":"courageous_archive_asset_replay","ref":snap})
            except Exception:
                continue
    except Exception as e:
        meta={"error":repr(e)}
    return out,meta

def commons_search(query,limit=18,source="commons"):
    out=[]; meta={}
    try:
        j,info=get_json(COMMONS_API,params={
            "action":"query","format":"json","generator":"search",
            "gsrsearch":query,"gsrnamespace":"6","gsrlimit":str(limit),
            "prop":"imageinfo","iiprop":"url|mime|size",
        })
        pages=(j.get("query") or {}).get("pages") or {}
        for _,p in pages.items():
            ii=(p.get("imageinfo") or [])
            if not ii: continue
            z=ii[0]
            u=z.get("thumburl") or z.get("url")
            if u:
                out.append({"url":u,"source":source,"ref":query,"title":p.get("title")})
        meta={"fetch":info,"query":query,"count":len(out)}
    except Exception as e:
        meta={"query":query,"error":repr(e)}
    return out,meta

def decode_image(b):
    im=Image.open(BytesIO(b)).convert("L")
    a=np.array(im)
    if min(a.shape)<80:
        raise RuntimeError(f"image too small {a.shape}")
    # Bound computation while preserving geometry.
    h,w=a.shape
    scale=min(1.0,1400/max(h,w))
    if scale<1:
        a=cv2.resize(a,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_AREA)
    return a

def canny(a):
    # Auto-ish fixed robust thresholds from median.
    med=float(np.median(a))
    lo=int(max(25,0.55*med)); hi=int(min(230,max(lo+30,1.15*med)))
    return cv2.Canny(a.astype(np.uint8),lo,hi)

def matcher_features(a,kind):
    if kind=="sift_gray":
        det=cv2.SIFT_create(nfeatures=6500,contrastThreshold=0.025,edgeThreshold=14)
        kp,des=det.detectAndCompute(a,None)
        return kp,des,cv2.NORM_L2,0.72
    if kind=="orb_edge":
        e=canny(a)
        det=cv2.ORB_create(nfeatures=6500,scaleFactor=1.2,nlevels=8,edgeThreshold=12,fastThreshold=7)
        kp,des=det.detectAndCompute(e,None)
        return kp,des,cv2.NORM_HAMMING,0.76
    raise ValueError(kind)

def edge_coverage(target,candidate,Hcand_to_target):
    te=canny(target)>0
    ce=canny(candidate)>0
    warped=cv2.warpPerspective(ce.astype(np.uint8),Hcand_to_target,(target.shape[1],target.shape[0]),flags=cv2.INTER_NEAREST)>0
    # 5px tolerance after drawing/photo domain change.
    kd=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
    wd=cv2.dilate(warped.astype(np.uint8),kd)>0
    td=cv2.dilate(te.astype(np.uint8),kd)>0
    target_cov=float(np.sum(te & wd)/max(1,np.sum(te)))
    cand_cov=float(np.sum(warped & td)/max(1,np.sum(warped)))
    return {"target_edge_coverage":target_cov,"candidate_edge_coverage":cand_cov,"edge_f1":float(2*target_cov*cand_cov/max(1e-9,target_cov+cand_cov))}

def compare_method(target,cand,kind):
    kt,dt,norm,ratio=matcher_features(target,kind)
    kc,dc,_,_=matcher_features(cand,kind)
    out={"target_keypoints":len(kt),"candidate_keypoints":len(kc),"good_matches":0,"homography_inliers":0,"inlier_fraction":0.0}
    if dt is None or dc is None or len(kt)<10 or len(kc)<10:
        return out
    bf=cv2.BFMatcher(norm)
    pairs=bf.knnMatch(dt,dc,k=2)
    good=[m for m,n in pairs if m.distance<ratio*n.distance]
    out["good_matches"]=len(good)
    if len(good)<8: return out
    # Query=target, train=candidate. Estimate candidate -> target.
    src=np.float32([kc[m.trainIdx].pt for m in good]).reshape(-1,1,2)
    dst=np.float32([kt[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    H,inliers=cv2.findHomography(src,dst,cv2.RANSAC,5.0,maxIters=5000,confidence=0.995)
    inc=int(inliers.sum()) if inliers is not None else 0
    out["homography_inliers"]=inc
    out["inlier_fraction"]=float(inc/max(1,len(good)))
    if H is not None and inc>=6:
        out.update(edge_coverage(target,cand,H))
    return out

def coarse_layout(target,cand):
    te=canny(target)
    ce=canny(cand)
    # Fit both to same 64x64 square; only a weak supporting metric.
    a=cv2.resize(te,(64,64),interpolation=cv2.INTER_AREA).astype(float).ravel()
    b=cv2.resize(ce,(64,64),interpolation=cv2.INTER_AREA).astype(float).ravel()
    if a.std()<1e-9 or b.std()<1e-9: return 0.0
    return float(np.corrcoef(a,b)[0,1])

def compare(target,cand):
    s=compare_method(target,cand,"sift_gray")
    o=compare_method(target,cand,"orb_edge")
    coarse=coarse_layout(target,cand)
    out={"sift_gray":s,"orb_edge":o,"coarse_edge_corr":coarse}
    def strong_method(m):
        return m.get("homography_inliers",0)>=20 and m.get("inlier_fraction",0)>=0.35 and m.get("edge_f1",0)>=0.12
    def interesting_method(m):
        return m.get("homography_inliers",0)>=10 and m.get("inlier_fraction",0)>=0.25 and m.get("edge_f1",0)>=0.07
    second_support=(s.get("homography_inliers",0)>=8 and o.get("homography_inliers",0)>=8) or coarse>=0.18
    out["strong_match"]=bool((strong_method(s) or strong_method(o)) and second_support)
    out["interesting_match"]=bool(out["strong_match"] or interesting_method(s) or interesting_method(o))
    # Ranking score, not a significance statistic.
    out["rank_score"]=float(
        max(s.get("homography_inliers",0)*s.get("inlier_fraction",0)*max(s.get("edge_f1",0),0.01),
            o.get("homography_inliers",0)*o.get("inlier_fraction",0)*max(o.get("edge_f1",0),0.01))
        + max(0,coarse)*2
    )
    return out

def positive_control(target):
    h,w=target.shape
    src=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
    dst=np.float32([[35,28],[w-75,15],[w-35,h-48],[55,h-15]])
    H=cv2.getPerspectiveTransform(src,dst)
    warped=cv2.warpPerspective(target,H,(w,h),borderValue=255)
    warped=cv2.GaussianBlur(warped,(3,3),0.7)
    noise=np.random.default_rng(9201).normal(0,3.0,warped.shape)
    warped=np.clip(warped.astype(float)+noise,0,255).astype(np.uint8)
    return compare(target,warped)

def main():
    target=np.array(Image.open(SOURCE).convert("L"))

    pool=[]
    source_meta={}

    cur,cm=courageous_current()
    pool.extend(cur); source_meta["courageous_current"]=cm

    arc,am=courageous_archive()
    pool.extend(arc); source_meta["courageous_archive"]=am

    for q in SEARCH_QUERIES:
        rows,m=commons_search(q,18,"commons_candidate")
        pool.extend(rows); source_meta[f"commons:{q}"]=m

    nulls,nm=commons_search(NULL_QUERY,14,"commons_null")
    pool.extend(nulls); source_meta["commons_null"]=nm

    # Dedupe by URL, preserving candidate source labels.
    by={}
    for x in pool:
        u=x.get("url")
        if not u: continue
        if u not in by:
            by[u]=dict(x)
            by[u]["refs"]=[{"source":x.get("source"),"ref":x.get("ref"),"title":x.get("title")}]
        else:
            by[u]["refs"].append({"source":x.get("source"),"ref":x.get("ref"),"title":x.get("title")})
    rows=list(by.values())[:MAX_CANDIDATES]

    results=[]
    for i,x in enumerate(rows):
        rec={k:v for k,v in x.items() if k!="refs"}
        rec["refs"]=x.get("refs",[])
        try:
            b,fi=get_bytes(x["url"])
            rec["fetch"]=fi
            cand=decode_image(b)
            rec["shape"]=list(cand.shape)
            rec["comparison"]=compare(target,cand)
        except Exception as e:
            rec["error"]=repr(e)
        results.append(rec)

    control=positive_control(target)
    control_pass=bool(control.get("strong_match"))

    cand_results=[r for r in results if r.get("source")!="commons_null" and r.get("comparison")]
    null_results=[r for r in results if r.get("source")=="commons_null" and r.get("comparison")]
    cand_results.sort(key=lambda r:r["comparison"].get("rank_score",0),reverse=True)
    null_results.sort(key=lambda r:r["comparison"].get("rank_score",0),reverse=True)

    strong=[r for r in cand_results if r["comparison"].get("strong_match")]
    interesting=[r for r in cand_results if r["comparison"].get("interesting_match")]
    null_strong=[r for r in null_results if r["comparison"].get("strong_match")]

    promoted=bool(control_pass and len(strong)>0 and len(null_strong)==0)
    result={
        "experiment_id":"A11-EXP-092",
        "scope":"bounded photo-source candidate audit over the exact historical Courageous Sailing lead, archived page assets and a small Commons skyline/sailing pool; no private-key operations",
        "source_meta":source_meta,
        "candidate_urls_total":len(rows),
        "candidate_images_scored":len(cand_results),
        "null_images_scored":len(null_results),
        "positive_control":control,
        "positive_control_pass":control_pass,
        "strong_candidate_matches":len(strong),
        "interesting_candidate_matches":len(interesting),
        "strong_null_matches":len(null_strong),
        "promoted":promoted,
        "promotion_rule":"positive control must pass; >=1 candidate must meet strong geometry gate; unrelated-photo null pool must have 0 strong matches",
        "top_candidates":cand_results[:20],
        "top_nulls":null_results[:10],
        "all_results":results,
        "coverage_limit":"A negative result rejects only the exact Courageous Sailing/Boston/public-Commons candidate pool tested here. It does not globally disprove that some other source photograph exists.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 92 — source-photo candidate audit",
        "",
        "**Experiment:** A11-EXP-092",
        "",
        f"- Candidate URLs gathered: **{len(rows)}**",
        f"- Candidate images scored: **{len(cand_results)}**",
        f"- Unrelated null images scored: **{len(null_results)}**",
        f"- Positive-control pass: **{control_pass}**",
        f"- Strong candidate matches: **{len(strong)}**",
        f"- Interesting candidate matches: **{len(interesting)}**",
        f"- Strong null matches: **{len(null_strong)}**",
        f"- Promotion rule satisfied: **{promoted}**",
        "",
        "## Top candidate geometry matches",
        "",
        "| source | score | strong | interesting | SIFT inliers/fraction/F1 | ORB inliers/fraction/F1 | coarse | URL |",
        "|:---|---:|:---:|:---:|:---|:---|---:|:---|",
    ]
    for r in cand_results[:15]:
        c=r["comparison"]; s=c["sift_gray"]; o=c["orb_edge"]
        url=r.get("url","").replace("|","%7C")
        md.append(
            f"| {r.get('source')} | {c.get('rank_score',0):.3f} | {c.get('strong_match')} | {c.get('interesting_match')} | "
            f"{s.get('homography_inliers',0)}/{s.get('inlier_fraction',0):.3f}/{s.get('edge_f1',0):.3f} | "
            f"{o.get('homography_inliers',0)}/{o.get('inlier_fraction',0):.3f}/{o.get('edge_f1',0):.3f} | "
            f"{c.get('coarse_edge_corr',0):.3f} | {url} |"
        )

    md += ["","## Interpretation",""]
    if promoted:
        md.append("At least one bounded public photo candidate shows unusually strong geometric correspondence to the sketch while the unrelated-photo null pool does not. The next stage should independently validate only the strongest candidate/source provenance.")
    elif interesting:
        md.append("No candidate met the strong predeclared gate, but one or more produced weaker geometry leads. Treat them as candidates for visual/manual provenance review only, not as established source photos.")
    else:
        md.append("No tested candidate page/photo pool produced meaningful geometric correspondence. Retire the exact Courageous Sailing/Boston candidate pool; do not recycle it without new evidence.")
    md += [
        "",
        "Coverage limit: this does not globally disprove an unknown source photograph outside the tested pool.",
        "",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-092",
        "control_pass":control_pass,"strong":len(strong),
        "interesting":len(interesting),"null_strong":len(null_strong),
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
