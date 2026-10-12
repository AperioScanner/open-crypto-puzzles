#!/usr/bin/env python3
"""Stage 100: spatial localization of Stage-99 OCR survivors.

Safe visual-text experiment only.

Stage 99 showed region-level repetition of four short OCR tokens, but did not
prove that different preprocessing paths were reading the same physical glyphs.
This stage requires canonical-coordinate co-localization.

Fixed candidate set from Stage 99:
- SSS @ full, 0 deg
- EAE @ lower_water, 0 deg
- BEE @ full, 0 deg
- IES @ full, 0 deg

Controls:
- Puzzle #9 APRIL crop
- Puzzle #9 12:05.04 crop

Safety:
- raw OCR output is never persisted;
- only the four predeclared short tokens and positive-control anchors are retained;
- no long/key-shaped text is stored;
- no private-key generation, derivation, reconstruction, enumeration, or wallet
  verification is performed.
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
import subprocess
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
P11=ROOT/"clues"/"arweave-puzzle-11.png"
P9=ROOT/"analysis"/"runs"/"stage96-puzzle9-four-step-audit"/"puzzle9-primary.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage100-ocr-spatial-localization"
OUT.mkdir(parents=True,exist_ok=True)

TRANSFORMS=("gray","otsu","adaptive")
WHITELIST="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:._/-"

CANDIDATES={
    "SSS":{"region":"full","rotation":0},
    "EAE":{"region":"lower_water","rotation":0},
    "BEE":{"region":"full","rotation":0},
    "IES":{"region":"full","rotation":0},
}

P9_QUOTE=(10,350,265,455)
P9_NUMERIC=(755,565,898,633)

def load_rgb(path):
    return np.array(Image.open(path).convert("RGB"))

def lossy_roundtrip(rgb):
    im=Image.fromarray(rgb)
    b=io.BytesIO()
    im.save(b,format="JPEG",quality=85,optimize=False,progressive=False)
    b.seek(0)
    j=Image.open(b).convert("RGB")
    w,h=j.size
    small=j.resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    return np.array(small.resize((w,h),Image.Resampling.LANCZOS))

def region_boxes(shape):
    h,w=shape[:2]
    g=json.loads(GEOM.read_text())
    b=g["large_sailboat"]
    return {
        "full":(0,0,w,h),
        "skyline":(0,0,w,min(330,h)),
        "large_sailboat":(int(b["x0"]),int(b["y0"]),int(b["x1"]),int(b["y1"])),
        "small_sails_jetty":(min(820,w),min(330,h),w,min(650,h)),
        "lower_water":(0,min(650,h),w,h),
    }

def crop(a,box):
    x0,y0,x1,y1=box
    return a[y0:y1,x0:x1]

def transform(rgb,name):
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    if name=="gray":
        return gray
    if name=="otsu":
        _,bw=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return bw
    if name=="adaptive":
        return cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,31,9)
    raise ValueError(name)

def block_shuffle(rgb,block=32,seed=9901):
    h,w=rgb.shape[:2]
    ph=((h+block-1)//block)*block
    pw=((w+block-1)//block)*block
    pad=np.full((ph,pw,3),255,np.uint8)
    pad[:h,:w]=rgb
    tiles=[]
    for y in range(0,ph,block):
        for x in range(0,pw,block):
            tiles.append(pad[y:y+block,x:x+block].copy())
    rng=np.random.default_rng(seed+h*13+w*17)
    perm=rng.permutation(len(tiles))
    out=np.empty_like(pad)
    i=0
    for y in range(0,ph,block):
        for x in range(0,pw,block):
            out[y:y+block,x:x+block]=tiles[int(perm[i])]
            i+=1
    return out[:h,:w]

def tsv_words(a,psm):
    """Return word boxes in coordinates of the *input* array."""
    h,w=a.shape[:2]
    scale=1.0
    if max(h,w)<700:
        scale=2.5
    elif max(h,w)<1200:
        scale=1.6
    if scale!=1.0:
        a2=cv2.resize(a,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_CUBIC)
    else:
        a2=a
    ok,png=cv2.imencode(".png",a2)
    if not ok:
        return []
    cmd=[
        "tesseract","stdin","stdout",
        "--oem","1","--psm",str(psm),"-l","eng",
        "-c",f"tessedit_char_whitelist={WHITELIST}",
        "tsv",
    ]
    try:
        p=subprocess.run(
            cmd,input=png.tobytes(),stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,timeout=20,check=False
        )
        txt=p.stdout.decode("utf-8","replace")
    except Exception:
        return []
    rows=[]
    rd=csv.DictReader(io.StringIO(txt),delimiter="\t")
    for r in rd:
        text=(r.get("text") or "").strip()
        if not text:
            continue
        try:
            conf=float(r.get("conf","-1"))
            x=float(r["left"])/scale
            y=float(r["top"])/scale
            ww=float(r["width"])/scale
            hh=float(r["height"])/scale
        except Exception:
            continue
        if ww<=0 or hh<=0:
            continue
        rows.append({
            "text":text,
            "conf":conf,
            "box":[x,y,x+ww,y+hh],
        })
    return rows

def norm_word(s):
    return re.sub(r"[^A-Z0-9:._/-]+","",s.upper()).strip("._/-:")

def token_matches(word,target):
    n=norm_word(word)
    if target=="120504":
        d=re.sub(r"\D","",word)
        return ("120504" in d) or sum(x in d for x in ("12","05","04"))>=2
    return target in n

def canonical_box(local_box,region_box):
    x0,y0,_,_=region_box
    a,b,c,d=local_box
    return [a+x0,b+y0,c+x0,d+y0]

def center(box):
    return ((box[0]+box[2])/2,(box[1]+box[3])/2)

def box_size(box):
    return (max(1e-6,box[2]-box[0]),max(1e-6,box[3]-box[1]))

def iou(a,b):
    ix0=max(a[0],b[0]); iy0=max(a[1],b[1])
    ix1=min(a[2],b[2]); iy1=min(a[3],b[3])
    iw=max(0.0,ix1-ix0); ih=max(0.0,iy1-iy0)
    inter=iw*ih
    aa=max(1e-9,(a[2]-a[0])*(a[3]-a[1]))
    bb=max(1e-9,(b[2]-b[0])*(b[3]-b[1]))
    return inter/max(1e-9,aa+bb-inter)

def compatible_boxes(a,b):
    ca=center(a); cb=center(b)
    cd=math.hypot(ca[0]-cb[0],ca[1]-cb[1])
    wa,ha=box_size(a); wb,hb=box_size(b)
    wr=min(wa,wb)/max(wa,wb); hr=min(ha,hb)/max(ha,hb)
    ov=iou(a,b)
    return bool(cd<=18.0 and (ov>=0.20 or (wr>=0.55 and hr>=0.55)))

def crop_corr(a,b,box,pad=8):
    h,w=a.shape[:2]
    x0=max(0,int(math.floor(box[0]-pad)))
    y0=max(0,int(math.floor(box[1]-pad)))
    x1=min(w,int(math.ceil(box[2]+pad)))
    y1=min(h,int(math.ceil(box[3]+pad)))
    if x1-x0<4 or y1-y0<4:
        return 0.0
    ga=cv2.cvtColor(a[y0:y1,x0:x1],cv2.COLOR_RGB2GRAY).astype(float).ravel()
    gb=cv2.cvtColor(b[y0:y1,x0:x1],cv2.COLOR_RGB2GRAY).astype(float).ravel()
    if ga.std()<1e-9 or gb.std()<1e-9:
        return 1.0 if np.allclose(ga,gb) else 0.0
    return float(np.corrcoef(ga,gb)[0,1])

def collect_occurrences(rgb,label,region,region_box,target,psm=11):
    rcrop=crop(rgb,region_box)
    out=[]
    for tf in TRANSFORMS:
        words=tsv_words(transform(rcrop,tf),psm=psm)
        for w in words:
            if token_matches(w["text"],target):
                out.append({
                    "variant":label,
                    "region":region,
                    "transform":tf,
                    "conf":float(w["conf"]),
                    "box":canonical_box(w["box"],region_box),
                })
    return out

def cluster_occurrences(occ):
    clusters=[]
    # Highest confidence first produces stable seeds.
    for x in sorted(occ,key=lambda z:z["conf"],reverse=True):
        best=None
        for cl in clusters:
            if any(compatible_boxes(x["box"],y["box"]) for y in cl):
                best=cl
                break
        if best is None:
            clusters.append([x])
        else:
            best.append(x)
    return clusters

def summarize_clusters(clusters,orig_rgb,lossy_rgb):
    out=[]
    for cl in clusters:
        orig=[x for x in cl if x["variant"]=="original"]
        lossy=[x for x in cl if x["variant"]=="lossy"]
        otrans=sorted(set(x["transform"] for x in orig))
        ltrans=sorted(set(x["transform"] for x in lossy))
        boxes=[x["box"] for x in cl]
        med=[
            float(np.median([b[0] for b in boxes])),
            float(np.median([b[1] for b in boxes])),
            float(np.median([b[2] for b in boxes])),
            float(np.median([b[3] for b in boxes])),
        ]
        confs=[x["conf"] for x in cl if x["conf"]>=0]
        corr=crop_corr(orig_rgb,lossy_rgb,med)
        out.append({
            "original_transforms":otrans,
            "lossy_transforms":ltrans,
            "original_count":len(orig),
            "lossy_count":len(lossy),
            "median_box":[round(v,2) for v in med],
            "mean_conf":float(np.mean(confs)) if confs else -1.0,
            "max_conf":float(max(confs)) if confs else -1.0,
            "original_lossy_crop_corr":corr,
            "qualifies":bool(len(otrans)>=2 and len(ltrans)>=1 and corr>=0.70),
        })
    out.sort(key=lambda x:(not x["qualifies"],-len(x["original_transforms"]),-len(x["lossy_transforms"]),-x["mean_conf"]))
    return out

def save_diag(rgb,box,path,pad=18):
    h,w=rgb.shape[:2]
    x0=max(0,int(math.floor(box[0]-pad))); y0=max(0,int(math.floor(box[1]-pad)))
    x1=min(w,int(math.ceil(box[2]+pad))); y1=min(h,int(math.ceil(box[3]+pad)))
    Image.fromarray(rgb[y0:y1,x0:x1]).save(path)

def positive_control(p9,p9lossy,name,box,target):
    region_box=box
    occ=[]
    for label,a in (("original",p9),("lossy",p9lossy)):
        rcrop=crop(a,box)
        for tf in TRANSFORMS:
            words=tsv_words(transform(rcrop,tf),psm=6)
            for w in words:
                if token_matches(w["text"],target):
                    occ.append({
                        "variant":label,
                        "region":name,
                        "transform":tf,
                        "conf":float(w["conf"]),
                        "box":canonical_box(w["box"],region_box),
                    })
    sm=summarize_clusters(cluster_occurrences(occ),p9,p9lossy)
    passed=any(x["qualifies"] for x in sm)
    return {"passed":passed,"clusters":sm,"occurrence_count":len(occ)}

def main():
    canonical=load_rgb(P11)
    lossy=lossy_roundtrip(canonical)
    boxes=region_boxes(canonical.shape)

    p9=load_rgb(P9)
    p9lossy=lossy_roundtrip(p9)
    controls={
        "APRIL":positive_control(p9,p9lossy,"p9_quote",P9_QUOTE,"APRIL"),
        "120504":positive_control(p9,p9lossy,"p9_numeric",P9_NUMERIC,"120504"),
    }
    controls_pass=all(x["passed"] for x in controls.values())

    results={}
    survivors=[]
    for tok,cfg in CANDIDATES.items():
        region=cfg["region"]
        rbox=boxes[region]
        occ=[]
        occ.extend(collect_occurrences(canonical,"original",region,rbox,tok,psm=11))
        occ.extend(collect_occurrences(lossy,"lossy",region,rbox,tok,psm=11))
        clusters=summarize_clusters(cluster_occurrences(occ),canonical,lossy)

        # Symmetric shuffled control: same block permutation applied independently
        # to original and lossy region pixels.
        s0=block_shuffle(crop(canonical,rbox))
        s1=block_shuffle(crop(lossy,rbox))
        local_box=(0,0,s0.shape[1],s0.shape[0])
        neg=[]
        neg.extend(collect_occurrences(s0,"original","shuffle",local_box,tok,psm=11))
        neg.extend(collect_occurrences(s1,"lossy","shuffle",local_box,tok,psm=11))
        neg_clusters=summarize_clusters(cluster_occurrences(neg),s0,s1)
        neg_qual=sum(1 for x in neg_clusters if x["qualifies"])

        qualifying=[x for x in clusters if x["qualifies"]]
        # A real localized token should have at least one target co-localized
        # cluster and no equally persistent shuffled cluster.
        survived=bool(controls_pass and qualifying and neg_qual==0)

        # Save only the strongest qualifying short-token crop.
        artifact=None
        if survived:
            best=qualifying[0]
            artifact=f"{tok.lower()}-localized.png"
            save_diag(canonical,best["median_box"],OUT/artifact)

        results[tok]={
            "stage99_region":region,
            "occurrence_count":len(occ),
            "clusters":clusters,
            "qualifying_target_clusters":len(qualifying),
            "shuffled_occurrence_count":len(neg),
            "shuffled_clusters":neg_clusters,
            "qualifying_shuffled_clusters":neg_qual,
            "survived":survived,
            "diagnostic_crop":artifact,
        }
        if survived:
            survivors.append(tok)

    result={
        "experiment_id":"A11-EXP-100",
        "scope":"canonical-coordinate spatial confirmation of exactly four Stage-99 short OCR candidates; no raw OCR persistence and no private-key operations",
        "candidates":CANDIDATES,
        "positive_controls":controls,
        "controls_pass":controls_pass,
        "results":results,
        "survivors":survivors,
        "promotion_rule":"Puzzle9 APRIL and numeric localization controls pass; candidate has same physical location across >=2 original transforms and >=1 lossy transform with <=18px center displacement plus overlap/size agreement and crop correlation>=0.70; zero equally persistent shuffled clusters",
        "promoted":bool(survivors),
        "safety_guard":"Only predeclared short tokens and bounding boxes are persisted. Raw OCR and long/key-shaped strings are discarded. No key candidate is constructed or verified.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 100 — spatial localization of Stage-99 OCR survivors",
        "",
        "**Experiment:** A11-EXP-100",
        "",
        f"- APRIL localization control: **{controls['APRIL']['passed']}**",
        f"- 12:05.04 localization control: **{controls['120504']['passed']}**",
        f"- all controls pass: **{controls_pass}**",
        f"- survivors: **{survivors}**",
        f"- stage promoted: **{bool(survivors)}**",
        "",
        "## Candidate results",
        "",
        "| token | target occurrences | qualifying target clusters | shuffled occurrences | qualifying shuffled clusters | survived | best box/conf/corr |",
        "|:---|---:|---:|---:|---:|:---:|:---|",
    ]
    for tok,r in results.items():
        q=[x for x in r["clusters"] if x["qualifies"]]
        if q:
            b=q[0]
            best=f"{b['median_box']} / {b['mean_conf']:.1f} / {b['original_lossy_crop_corr']:.3f}"
        else:
            best=""
        md.append(
            f"| {tok} | {r['occurrence_count']} | {r['qualifying_target_clusters']} | "
            f"{r['shuffled_occurrence_count']} | {r['qualifying_shuffled_clusters']} | "
            f"{r['survived']} | {best} |"
        )

    md += ["","## Interpretation",""]
    if not controls_pass:
        md.append("The localization harness failed a known Puzzle #9 visible-anchor control. This is an implementation failure and must be fixed under Stage 100 before interpreting Puzzle #11.")
    elif survivors:
        md.append("At least one Stage-99 short OCR candidate is repeatedly read from the same physical image location across preprocessing and lossy re-encoding while lacking an equally persistent shuffled-control location. Only those survivors warrant direct visual/rebus follow-up.")
    else:
        md.append("None of the Stage-99 tokens survives physical co-localization. Retire them as region-level OCR hallucinations and do not interpret the strings semantically.")

    md += [
        "",
        "Only small diagnostic crops for surviving short tokens are saved.",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-100",
        "controls_pass":controls_pass,
        "survivors":survivors,
        "promoted":bool(survivors),
    }))

if __name__=="__main__":
    main()
