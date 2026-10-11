#!/usr/bin/env python3
"""Stage 97: Puzzle #9 semantic-anchor + four-step source corroboration audit.

Safe public-source research only.

This stage does not try to recover Puzzle #9's private key. It asks two narrower
questions:

1. Is the often-cited "required 4 steps ... brute forced one" author statement
   sufficiently corroborated to use as a mechanism prior?
2. Does the canonical #9 image contain robust, format-tolerant visible semantic
   anchors (quote, numeric stamp, five colored birds) that justify treating #9
   as a semantic/multi-anchor sibling rather than as evidence for a specific
   pixel-channel carrier?

No private-key generation, derivation, enumeration, reconstruction, verification
or wallet access is performed.
"""
from __future__ import annotations

import hashlib
import html
import io
import json
import math
import re
from pathlib import Path

import cv2
import numpy as np
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
P9=ROOT/"analysis"/"runs"/"stage96-puzzle9-four-step-audit"/"puzzle9-primary.png"
OUT=ROOT/"analysis"/"runs"/"stage97-puzzle9-semantic-anchors"
OUT.mkdir(parents=True,exist_ok=True)

TWEET_ID="1272111084867129344"
TWEET_URL=f"https://twitter.com/arweavep/status/{TWEET_ID}"
SYNDICATION=f"https://cdn.syndication.twimg.com/tweet-result?id={TWEET_ID}&lang=en"
CDX="https://web.archive.org/cdx/search/cdx"

OFFICIAL_NEWSLETTER="https://arweave.medium.com/arweave-newsletter-december-e83e962bcb9b"
OFFICIAL_TELEGRAM="https://t.me/s/arweaveannouncements?after=127"
SECONDARY_11="https://raw.githubusercontent.com/itsnex1s/crypto-puzzle-list/main/unsolved/arweave-puzzle-11-1eth.md"
SECONDARY_3="https://raw.githubusercontent.com/itsnex1s/crypto-puzzle-list/main/unsolved/arweave-puzzle-3-1000ar.md"

QUOTE_EXPECTED="The puzzle required 4 steps. My guess is the solver figured out 3 and brute forced one, that's why he is silent"
IMAGE_ONLY_EXPECTED="everything needed to crack this code is hidden in the image"

# Fixed direct-visual anchor crops on the canonical 900x635 image.
CROPS={
    "literary_quote":(10,350,265,455),
    "numeric_stamp":(755,565,898,633),
    "bird_green":(145,115,270,365),
    "bird_blue":(270,105,405,365),
    "bird_orange":(585,25,795,205),
    "bird_red":(615,320,825,565),
    "bird_yellow":(165,420,350,635),
}
BIRD_EXPECTED={
    "bird_green":"green",
    "bird_blue":"blue",
    "bird_orange":"orange",
    "bird_red":"red",
    "bird_yellow":"yellow",
}
VARIANT_NAMES=("original","jpeg85","jpeg70","down75_up")

MANUAL_TRANSCRIPTIONS={
    "literary_quote":"It was a bright cold day in April, and the clocks were striking thirteen.",
    "numeric_stamp":"12:05.04",
}

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0; public source audit)"})

def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def fetch_text(url,timeout=25):
    r=S.get(url,timeout=timeout,allow_redirects=True)
    r.raise_for_status()
    return html.unescape(r.text),{
        "url":r.url,"status":r.status_code,"bytes":len(r.content),
        "sha256":sha256(r.content)
    }

def variants(gray):
    out={"original":gray}
    for q in (85,70):
        b=io.BytesIO()
        Image.fromarray(gray).save(b,format="JPEG",quality=q,optimize=False,progressive=False)
        b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("RGB"))
    h,w=gray.shape[:2]
    small=Image.fromarray(gray).resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(small.resize((w,h),Image.Resampling.LANCZOS))
    return out

def crop(a,box):
    x0,y0,x1,y1=box
    return a[y0:y1,x0:x1]

def edge_corr(a,b):
    ga=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY) if a.ndim==3 else a
    gb=cv2.cvtColor(b,cv2.COLOR_RGB2GRAY) if b.ndim==3 else b
    ea=cv2.Canny(ga,60,160).astype(float).ravel()
    eb=cv2.Canny(gb,60,160).astype(float).ravel()
    if ea.std()<1e-9 or eb.std()<1e-9:
        return 0.0
    return float(np.corrcoef(ea,eb)[0,1])

def hue_label(rgb):
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    h=hsv[:,:,0]
    s=hsv[:,:,1]
    v=hsv[:,:,2]
    m=(s>=90)&(v>=60)
    if np.sum(m)<50:
        return {"label":"none","dominant_hue":None,"saturated_pixels":int(np.sum(m))}
    vals=h[m]
    hist=np.bincount(vals,minlength=180).astype(float)
    # circular smoothing
    ext=np.r_[hist[-4:],hist,hist[:4]]
    ker=np.ones(9)/9.0
    sm=np.convolve(ext,ker,mode="same")[4:-4]
    peak=int(np.argmax(sm))
    # OpenCV hue 0..179.
    if peak<=6 or peak>=174:
        lab="red"
    elif peak<=18:
        lab="orange"
    elif peak<=36:
        lab="yellow"
    elif peak<=85:
        lab="green"
    elif peak<=132:
        lab="blue"
    elif peak<=160:
        lab="purple"
    else:
        lab="red"
    return {
        "label":lab,
        "dominant_hue":peak,
        "saturated_pixels":int(np.sum(m)),
        "peak_fraction":float(hist[peak]/max(1,hist.sum())),
    }

def source_record(url,kind):
    rec={"url":url,"kind":kind}
    try:
        text,info=fetch_text(url)
        rec["fetch"]=info
        low=re.sub(r"\s+"," ",text).lower()
        qlow=QUOTE_EXPECTED.lower()
        rec["has_exact_four_step_quote"]=qlow in low
        rec["has_tweet_id"]=TWEET_ID in text
        rec["mentions_puzzle9"]=bool(re.search(r"puzzle\s*#?\s*9|puzzle\s+9|100\s*dai",low))
        rec["mentions_image_only"]=IMAGE_ONLY_EXPECTED.lower() in low
        if rec["has_exact_four_step_quote"]:
            i=low.find(qlow)
            rec["quote_context"]=re.sub(r"\s+"," ",text[max(0,i-900):i+len(QUOTE_EXPECTED)+1200])[:2600]
        if rec["mentions_image_only"]:
            i=low.find(IMAGE_ONLY_EXPECTED.lower())
            rec["image_only_context"]=re.sub(r"\s+"," ",text[max(0,i-600):i+len(IMAGE_ONLY_EXPECTED)+900])[:2000]
    except Exception as e:
        rec["error"]=repr(e)
    return rec

def syndication_record():
    rec={"url":SYNDICATION,"kind":"twitter_syndication"}
    try:
        r=S.get(SYNDICATION,timeout=20)
        rec["status"]=r.status_code
        rec["bytes"]=len(r.content)
        if r.ok:
            j=r.json()
            rec["json"]=j
            text=str(j.get("text") or j.get("full_text") or "")
            rec["has_exact_four_step_quote"]=QUOTE_EXPECTED.lower() in text.lower()
            rec["text"]=text
        else:
            rec["has_exact_four_step_quote"]=False
    except Exception as e:
        rec["error"]=repr(e)
        rec["has_exact_four_step_quote"]=False
    return rec

def wayback_page_record(url,phrase,kind):
    rec={"url":url,"kind":kind,"verified":False}
    try:
        r=S.get(CDX,params={
            "url":url,
            "output":"json",
            "filter":"statuscode:200",
            "fl":"timestamp,original,statuscode,digest",
            "from":"2020","to":"2022",
            "collapse":"digest",
            "limit":"30",
        },timeout=20)
        r.raise_for_status()
        rows=r.json()
        rec["cdx_rows"]=rows[1:] if isinstance(rows,list) and len(rows)>1 else []
        for row in rec["cdx_rows"][:10]:
            ts=row[0]
            snap=f"https://web.archive.org/web/{ts}id_/{url}"
            try:
                rr=S.get(snap,timeout=15)
                if not rr.ok: continue
                txt=html.unescape(re.sub(r"\\s+"," ",rr.text))
                if phrase.lower() in txt.lower():
                    rec["verified"]=True
                    rec["snapshot"]=snap
                    rec["snapshot_sha256"]=sha256(rr.content)
                    rec["mentions_image_only"]=True
                    i=txt.lower().find(phrase.lower())
                    rec["image_only_context"]=txt[max(0,i-700):i+len(phrase)+1000]
                    break
            except Exception:
                continue
    except Exception as e:
        rec["error"]=repr(e)
    return rec

def wayback_record():
    rec={"url":TWEET_URL,"kind":"wayback"}
    try:
        r=S.get(CDX,params={
            "url":TWEET_URL,
            "output":"json",
            "filter":"statuscode:200",
            "fl":"timestamp,original,statuscode,digest",
            "from":"2020","to":"2022",
            "collapse":"digest",
            "limit":"30",
        },timeout=20)
        r.raise_for_status()
        rows=r.json()
        rec["cdx_rows"]=rows[1:] if isinstance(rows,list) and len(rows)>1 else []
        rec["verified"]=False
        for row in rec["cdx_rows"][:8]:
            ts=row[0]
            snap=f"https://web.archive.org/web/{ts}id_/{TWEET_URL}"
            try:
                rr=S.get(snap,timeout=15)
                if not rr.ok: continue
                text=html.unescape(re.sub(r"\s+"," ",rr.text))
                if QUOTE_EXPECTED.lower() in text.lower():
                    rec["verified"]=True
                    rec["snapshot"]=snap
                    rec["snapshot_sha256"]=sha256(rr.content)
                    i=text.lower().find(QUOTE_EXPECTED.lower())
                    rec["quote_context"]=text[max(0,i-900):i+len(QUOTE_EXPECTED)+1200]
                    break
            except Exception:
                continue
    except Exception as e:
        rec["error"]=repr(e)
        rec["verified"]=False
    return rec

def main():
    im=Image.open(P9).convert("RGB")
    rgb=np.array(im)
    if rgb.shape[:2]!=(635,900):
        raise SystemExit(f"unexpected P9 shape {rgb.shape}")
    vv=variants(rgb)

    # Persist fixed direct-review crops.
    crop_hashes={}
    for name,box in CROPS.items():
        arr=crop(rgb,box)
        p=OUT/f"{name}.png"
        Image.fromarray(arr).save(p)
        crop_hashes[name]=sha256(p.read_bytes())

    anchor_robustness={}
    for name in ("literary_quote","numeric_stamp"):
        base=crop(vv["original"],CROPS[name])
        per={}
        for variant,a in vv.items():
            per[variant]=edge_corr(base,crop(a,CROPS[name]))
        anchor_robustness[name]={
            "manual_transcription":MANUAL_TRANSCRIPTIONS[name],
            "crop_sha256":crop_hashes[name],
            "edge_correlations":per,
            "robust":bool(all(per[v]>=0.55 for v in ("jpeg85","jpeg70","down75_up"))),
        }

    bird_results={}
    labels_original=[]
    all_stable=True
    for name,expected in BIRD_EXPECTED.items():
        per={}
        for variant,a in vv.items():
            per[variant]=hue_label(crop(a,CROPS[name]))
        labels_original.append(per["original"]["label"])
        base_hue=per["original"].get("dominant_hue")
        hue_drifts={}
        for v in VARIANT_NAMES:
            hv=per[v].get("dominant_hue")
            if base_hue is None or hv is None:
                hue_drifts[v]=None
            else:
                d=abs(int(hv)-int(base_hue))
                hue_drifts[v]=min(d,180-d)
        stable=bool(
            per["original"]["label"]==expected
            and all(hue_drifts[v] is not None and hue_drifts[v]<=6 for v in VARIANT_NAMES)
        )
        bird_results[name]={
            "expected_visual_label":expected,
            "variants":per,
            "hue_drift_from_original":hue_drifts,
            "stability_rule":"original expected category + circular dominant-hue drift <=6/180 in every variant",
            "stable_expected_label":stable,
            "crop_sha256":crop_hashes[name],
        }
        all_stable=all_stable and stable
    five_distinct=len(set(labels_original))==5

    sources=[
        source_record(OFFICIAL_NEWSLETTER,"official_arweave_newsletter"),
        wayback_page_record(OFFICIAL_NEWSLETTER,IMAGE_ONLY_EXPECTED,"official_arweave_newsletter_wayback"),
        source_record(OFFICIAL_TELEGRAM,"official_arweave_telegram"),
        source_record(SECONDARY_11,"secondary_crypto_puzzle_dossier_11"),
        source_record(SECONDARY_3,"secondary_crypto_puzzle_dossier_3"),
        syndication_record(),
        wayback_record(),
    ]

    primary_verified=any(
        (x.get("kind") in ("twitter_syndication","wayback"))
        and (x.get("has_exact_four_step_quote") or x.get("verified"))
        for x in sources
    )
    secondary_quote_sources=[
        x for x in sources
        if x.get("kind","").startswith("secondary_")
        and x.get("has_exact_four_step_quote")
        and x.get("has_tweet_id")
        and x.get("mentions_puzzle9")
    ]
    official_image_only=any(
        x.get("kind","").startswith("official_")
        and (x.get("mentions_image_only") or x.get("verified") and x.get("kind")=="official_arweave_newsletter_wayback")
        for x in sources
    )

    if primary_verified:
        quote_confidence="PRIMARY_VERIFIED"
    elif len(secondary_quote_sources)>=2:
        quote_confidence="MULTI_SOURCE_SECONDARY_CORROBORATED"
    elif len(secondary_quote_sources)==1:
        quote_confidence="SINGLE_SECONDARY"
    else:
        quote_confidence="UNVERIFIED"

    text_anchors_robust=all(x["robust"] for x in anchor_robustness.values())
    semantic_scaffold=bool(
        official_image_only
        and quote_confidence in ("PRIMARY_VERIFIED","MULTI_SOURCE_SECONDARY_CORROBORATED")
        and text_anchors_robust
        and all_stable
        and five_distinct
    )

    result={
        "experiment_id":"A11-EXP-097",
        "scope":"Puzzle #9 visible semantic-anchor robustness + four-step source hierarchy; no private-key operations",
        "p9_image_sha256":sha256(P9.read_bytes()),
        "manual_visual_transcriptions":MANUAL_TRANSCRIPTIONS,
        "anchor_crops":{k:{"box":list(CROPS[k]),"sha256":crop_hashes[k]} for k in CROPS},
        "text_anchor_robustness":anchor_robustness,
        "bird_color_anchors":bird_results,
        "five_distinct_bird_colors_original":five_distinct,
        "all_bird_colors_stable_across_variants":all_stable,
        "source_records":sources,
        "primary_four_step_quote_verified":primary_verified,
        "secondary_quote_sources_count":len(secondary_quote_sources),
        "official_image_only_context_verified":official_image_only,
        "four_step_quote_confidence":quote_confidence,
        "semantic_multi_anchor_scaffold_supported":semantic_scaffold,
        "interpretation_guard":"Visible anchors being robust does not prove which anchors participate in the solve or that 'four steps' means four visible clue objects.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 97 — Puzzle #9 semantic-anchor + four-step source audit",
        "",
        "**Experiment:** A11-EXP-097",
        "",
        f"- primary four-step quote recovered: **{primary_verified}**",
        f"- secondary quote sources with same tweet ID + #9 context: **{len(secondary_quote_sources)}**",
        f"- four-step quote confidence: **{quote_confidence}**",
        f"- official 'everything needed ... hidden in image' context: **{official_image_only}**",
        f"- literary/numeric crops robust across lossy variants: **{text_anchors_robust}**",
        f"- five distinct bird colors in original: **{five_distinct}**",
        f"- bird color identities stable across variants: **{all_stable}**",
        f"- semantic multi-anchor scaffold supported: **{semantic_scaffold}**",
        "",
        "## Visible anchors",
        "",
        f"- literary quote: `{MANUAL_TRANSCRIPTIONS['literary_quote']}`",
        f"- numeric stamp: `{MANUAL_TRANSCRIPTIONS['numeric_stamp']}`",
        "- bird colors: green, blue, orange, red, yellow",
        "",
        "## Text-crop robustness",
        "",
        "| anchor | jpeg85 edge corr | jpeg70 | resize roundtrip | robust |",
        "|:---|---:|---:|---:|:---:|",
    ]
    for name,r in anchor_robustness.items():
        c=r["edge_correlations"]
        md.append(f"| {name} | {c['jpeg85']:.3f} | {c['jpeg70']:.3f} | {c['down75_up']:.3f} | {r['robust']} |")

    md += [
        "",
        "## Bird-color robustness",
        "",
        "| crop | expected | original | jpeg85 | jpeg70 | resize | stable |",
        "|:---|:---|:---|:---|:---|:---|:---:|",
    ]
    for name,r in bird_results.items():
        v=r["variants"]
        md.append(
            f"| {name} | {r['expected_visual_label']} | {v['original']['label']}({v['original']['dominant_hue']}) | "
            f"{v['jpeg85']['label']}({v['jpeg85']['dominant_hue']}) | {v['jpeg70']['label']}({v['jpeg70']['dominant_hue']}) | "
            f"{v['down75_up']['label']}({v['down75_up']['dominant_hue']}) | {r['stable_expected_label']} |"
        )

    md += ["","## Source hierarchy","",
           "| kind | fetched | exact four-step quote | tweet id | #9 context | image-only official phrase |",
           "|:---|:---:|:---:|:---:|:---:|:---:|"]
    for x in sources:
        fetched=bool(x.get("fetch") or x.get("status") or x.get("cdx_rows") is not None)
        md.append(
            f"| {x.get('kind')} | {fetched} | {bool(x.get('has_exact_four_step_quote') or x.get('verified'))} | "
            f"{bool(x.get('has_tweet_id'))} | {bool(x.get('mentions_puzzle9'))} | {bool(x.get('mentions_image_only'))} |"
        )

    md += ["","## Interpretation",""]
    if semantic_scaffold:
        md.append("Puzzle #9 provides a defensible semantic/multi-anchor sibling prior: official material says everything needed was in the image, the four-step author quote is at least independently corroborated, and the image contains multiple visible anchors that remain stable under ordinary re-encoding. This does **not** identify which anchor maps to which solve step.")
    else:
        md.append("The evidence is insufficient to promote a specific semantic multi-anchor mechanism. Preserve only the weaker image-only prior and do not transfer an assumed four-anchor scheme to Puzzle #11.")

    md += [
        "",
        "Crops are saved for direct visual review. No OCR-derived secret string, key candidate, or wallet operation is performed.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-097",
        "quote_confidence":quote_confidence,
        "official_image_only":official_image_only,
        "text_anchors_robust":text_anchors_robust,
        "bird_colors_stable":all_stable,
        "semantic_scaffold":semantic_scaffold,
    }))

if __name__=="__main__":
    main()
