#!/usr/bin/env python3
"""Stage 99: bounded whole-image visible alphanumeric/rebus audit.

Safe visual-text experiment only.

Motivation:
- solved sibling Puzzle #9 contains robust visible text and numeric anchors;
- Stage 36 explicitly did not perform OCR;
- Puzzle #11's author says the key is hidden in the image and format does not matter.

This stage searches only for short visible instruction-like tokens (3..20 chars)
across fixed semantic regions, three fixed visual transforms and four cardinal
rotations. Candidates must replicate after JPEG85+resize and be absent from
deterministic block-shuffled negatives.

A Puzzle #9 quote crop ("APRIL") and numeric crop ("12:05.04") are positive
controls.

IMPORTANT SAFETY GUARD:
- raw OCR text is never persisted;
- strings longer than 20 chars are never persisted;
- any 64-hex-like output is ignored;
- no candidate private key is constructed, derived, enumerated, or verified.
"""
from __future__ import annotations

import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
P11=ROOT/"clues"/"arweave-puzzle-11.png"
P9=ROOT/"analysis"/"runs"/"stage96-puzzle9-four-step-audit"/"puzzle9-primary.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage99-visible-alphanumeric-audit"
OUT.mkdir(parents=True,exist_ok=True)

ROTATIONS=(0,90,180,270)
TRANSFORMS=("gray","otsu","adaptive")
WHITELIST="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:._/-"
TOKEN_RE=re.compile(r"[A-Za-z0-9][A-Za-z0-9:._/-]{2,19}")
HEX64_RE=re.compile(r"(?i)^[0-9a-f]{64}$")

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

def rotate(a,degrees):
    k=(degrees//90)%4
    return np.rot90(a,k).copy()

def ocr_image(a,psm=11):
    # Upscale smaller crops to help text recognition.
    h,w=a.shape[:2]
    scale=1.0
    if max(h,w)<700:
        scale=2.5
    elif max(h,w)<1200:
        scale=1.6
    if scale!=1.0:
        a=cv2.resize(a,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_CUBIC)
    ok,png=cv2.imencode(".png",a)
    if not ok:
        return ""
    cmd=[
        "tesseract","stdin","stdout",
        "--oem","1","--psm",str(psm),"-l","eng",
        "-c",f"tessedit_char_whitelist={WHITELIST}",
    ]
    try:
        p=subprocess.run(cmd,input=png.tobytes(),stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=18,check=False)
        return p.stdout.decode("utf-8","replace")
    except Exception:
        return ""

def safe_tokens(text):
    # Never persist long OCR strings or anything key-shaped.
    out=[]
    for m in TOKEN_RE.finditer(text):
        t=m.group(0).upper().strip("._/-:")
        if not (3<=len(t)<=20):
            continue
        if HEX64_RE.fullmatch(t):
            continue
        # Avoid tokens made entirely of punctuation after normalization.
        if not re.search(r"[A-Z0-9]",t):
            continue
        out.append(t)
    return sorted(set(out))

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

def run_target_jobs(rgb,label):
    boxes=region_boxes(rgb.shape)
    records=[]
    for region,box in boxes.items():
        rcrop=crop(rgb,box)
        for rot in ROTATIONS:
            for tf in TRANSFORMS:
                a=rotate(transform(rcrop,tf),rot)
                text=ocr_image(a,psm=11)
                records.append({
                    "variant":label,
                    "region":region,
                    "rotation":rot,
                    "transform":tf,
                    "tokens":safe_tokens(text),
                })
    return records

def positive_controls():
    p9=load_rgb(P9)
    p9lossy=lossy_roundtrip(p9)
    controls={}
    for name,box,kind in (
        ("p9_quote_april",P9_QUOTE,"quote"),
        ("p9_numeric_120504",P9_NUMERIC,"numeric"),
    ):
        rows=[]
        for variant,a in (("original",p9),("lossy",p9lossy)):
            c=crop(a,box)
            for tf in TRANSFORMS:
                text=ocr_image(transform(c,tf),psm=6)
                toks=safe_tokens(text)
                digits=re.sub(r"\D","",text)
                rows.append({
                    "variant":variant,
                    "transform":tf,
                    "tokens":toks,
                    "digits_projection":digits[:24],
                })
        if kind=="quote":
            orig=sum("APRIL" in r["tokens"] for r in rows if r["variant"]=="original")
            lossy=sum("APRIL" in r["tokens"] for r in rows if r["variant"]=="lossy")
            passed=orig>=1 and lossy>=1
            detail={"original_april_paths":orig,"lossy_april_paths":lossy}
        else:
            def numeric_hit(r):
                d=r["digits_projection"]
                hits=sum(x in d for x in ("12","05","04"))
                return d.find("120504")>=0 or hits>=2
            orig=sum(numeric_hit(r) for r in rows if r["variant"]=="original")
            lossy=sum(numeric_hit(r) for r in rows if r["variant"]=="lossy")
            passed=orig>=1 and lossy>=1
            detail={"original_numeric_paths":orig,"lossy_numeric_paths":lossy}
        controls[name]={"passed":bool(passed),"detail":detail,"rows":rows}
    controls["all_pass"]=all(x["passed"] for k,x in controls.items() if k!="all_pass")
    return controls

def aggregate(records):
    by_key=defaultdict(set)
    counts=Counter()
    for r in records:
        path=(r["variant"],r["region"],r["rotation"],r["transform"])
        for t in r["tokens"]:
            by_key[t].add(path)
            counts[t]+=1
    return by_key,counts

def main():
    canonical=load_rgb(P11)
    lossy=lossy_roundtrip(canonical)

    orig_records=run_target_jobs(canonical,"original")
    lossy_records=run_target_jobs(lossy,"lossy")

    # Matched negative controls use the same semantic crops, shuffled internally.
    boxes=region_boxes(canonical.shape)
    neg_records=[]
    for region,box in boxes.items():
        neg=block_shuffle(crop(canonical,box))
        # Use all transforms/cardinal rotations for exact symmetry with the target.
        for rot in ROTATIONS:
            for tf in TRANSFORMS:
                text=ocr_image(rotate(transform(neg,tf),rot),psm=11)
                neg_records.append({
                    "variant":"shuffled",
                    "region":region,
                    "rotation":rot,
                    "transform":tf,
                    "tokens":safe_tokens(text),
                })

    controls=positive_controls()
    orig_map,orig_counts=aggregate(orig_records)
    lossy_map,lossy_counts=aggregate(lossy_records)
    neg_map,neg_counts=aggregate(neg_records)

    candidates=[]
    all_tokens=sorted(set(orig_map)|set(lossy_map))
    for tok in all_tokens:
        opaths=orig_map.get(tok,set())
        lpaths=lossy_map.get(tok,set())
        npaths=neg_map.get(tok,set())

        # Require >=2 transform paths for same original region+rotation.
        groups=defaultdict(set)
        for _,region,rot,tf in opaths:
            groups[(region,rot)].add(tf)

        qualifying=[]
        for (region,rot),tfs in groups.items():
            if len(tfs)<2:
                continue
            lossy_tfs={
                tf for variant,r,rr,tf in lpaths
                if r==region and rr==rot
            }
            neg_tfs={
                tf for variant,r,rr,tf in npaths
                if r==region and rr==rot
            }
            if lossy_tfs and not neg_tfs:
                qualifying.append({
                    "region":region,
                    "rotation":rot,
                    "original_transforms":sorted(tfs),
                    "lossy_transforms":sorted(lossy_tfs),
                })

        if qualifying:
            candidates.append({
                "token":tok,
                "qualifying_paths":qualifying,
                "original_occurrences":len(opaths),
                "lossy_occurrences":len(lpaths),
                "shuffled_occurrences":len(npaths),
            })

    candidates.sort(key=lambda x:(-len(x["qualifying_paths"]),-x["original_occurrences"],-x["lossy_occurrences"],x["token"]))

    # For diagnostics, keep only short aggregate tokens; no raw OCR is persisted.
    top_repeated=[]
    for tok,n in orig_counts.most_common(40):
        if 3<=len(tok)<=20:
            top_repeated.append({
                "token":tok,
                "original_paths":n,
                "lossy_paths":lossy_counts.get(tok,0),
                "shuffled_paths":neg_counts.get(tok,0),
            })

    promoted=bool(controls["all_pass"] and candidates)

    result={
        "experiment_id":"A11-EXP-099",
        "scope":"short visible alphanumeric/instruction-token OCR audit over fixed regions/transforms/cardinal rotations; no raw OCR persistence and no private-key operations",
        "regions":{k:list(v) for k,v in region_boxes(canonical.shape).items()},
        "transforms":list(TRANSFORMS),
        "rotations":list(ROTATIONS),
        "ocr_jobs":{
            "original":len(orig_records),
            "lossy":len(lossy_records),
            "shuffled_negative":len(neg_records),
        },
        "positive_controls":controls,
        "promoted_candidates":candidates,
        "promoted_candidate_count":len(candidates),
        "top_repeated_short_tokens":top_repeated,
        "promotion_rule":"Puzzle9 positive controls pass; token length 3..20; same token appears in >=2 preprocessing transforms for one Puzzle11 region+rotation, reappears after JPEG85+resize in that same region+rotation, and is absent from the matched shuffled control",
        "promoted":promoted,
        "safety_guard":"Raw OCR is not persisted. Tokens >20 chars are not persisted. 64-hex-like strings are ignored. No key candidate is constructed or verified.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 99 — whole-image visible alphanumeric/rebus audit",
        "",
        "**Experiment:** A11-EXP-099",
        "",
        f"- Puzzle #9 positive controls all pass: **{controls['all_pass']}**",
        f"- target OCR jobs: **{len(orig_records)+len(lossy_records)}**",
        f"- shuffled negative jobs: **{len(neg_records)}**",
        f"- promoted short tokens: **{len(candidates)}**",
        f"- stage promoted: **{promoted}**",
        "",
        "## Positive controls",
        "",
        f"- APRIL quote control: **{controls['p9_quote_april']['passed']}** — {controls['p9_quote_april']['detail']}",
        f"- 12:05.04 numeric control: **{controls['p9_numeric_120504']['passed']}** — {controls['p9_numeric_120504']['detail']}",
        "",
        "## Promoted Puzzle #11 tokens",
        "",
    ]
    if candidates:
        md.append("| token | region/rotation replications | original paths | lossy paths | shuffled |")
        md.append("|:---|:---|---:|---:|---:|")
        for x in candidates[:30]:
            reps="; ".join(f"{r['region']}@{r['rotation']}°" for r in x["qualifying_paths"])
            md.append(f"| {x['token']} | {reps} | {x['original_occurrences']} | {x['lossy_occurrences']} | {x['shuffled_occurrences']} |")
    else:
        md.append("None.")

    md += [
        "",
        "## Interpretation",
        "",
    ]
    if not controls["all_pass"]:
        md.append("The OCR harness failed its Puzzle #9 known-visible-anchor controls, so this stage is an implementation failure and must be fixed under Stage 99 before any Puzzle #11 conclusion.")
    elif candidates:
        md.append("At least one short visible token survives independent preprocessing and lossy re-encoding while disappearing under matched block shuffling. These are candidates for direct visual localization in the next stage; they are not secret/key material.")
    else:
        md.append("The validated OCR harness found no robust short alphanumeric/instruction token in the tested regions and cardinal rotations. Retire straightforward OCR-readable visible text as the hidden mechanism; visual rebuses/non-text semantics remain possible.")

    md += [
        "",
        "Raw OCR text is intentionally not saved. No long/key-shaped strings are persisted.",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-099",
        "controls_pass":controls["all_pass"],
        "candidate_count":len(candidates),
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
