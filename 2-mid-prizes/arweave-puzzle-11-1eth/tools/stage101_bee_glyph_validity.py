#!/usr/bin/env python3
"""Stage 101: adversarial glyph-validity audit for localized OCR token BEE.

Stage 100 found one spatially stable OCR reading, "BEE", at a fixed image box.
Direct visual inspection suggests the box is horizontal hatching rather than
literal letters. This stage tests that distinction.

Safe scope:
- exact token under test is fixed to BEE;
- no raw OCR is persisted;
- no long/key-shaped OCR output is retained;
- no private-key generation, derivation, reconstruction, enumeration,
  verification, or wallet access.

Tests:
1. OCR persistence under crop jitter, image loss, preprocessing and 6 PSM modes.
2. Rendered BEE positives in several ordinary fonts.
3. Nuisance-matched same-size line-art controls.
4. Independent glyph topology: vertical-stem continuity and horizontal/vertical
   gradient-energy balance.
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
P11=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage101-bee-glyph-validity"
OUT.mkdir(parents=True,exist_ok=True)

TOKEN="BEE"
BASE_BOX=(803,520.5,883,545)
PAD=18
JITTERS=((0,0),(-6,0),(6,0),(0,-6),(0,6))
TRANSFORMS=("gray","otsu","adaptive")
PSMS=(6,7,8,10,11,13)
VARIANTS=("original","jpeg85","jpeg70","down75_up")
NEGATIVE_K=8
GRID_STEP=70
WHITELIST="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:._/-"

FONT_PATHS=(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)

def load_rgb():
    return np.array(Image.open(P11).convert("RGB"))

def image_variants(rgb):
    out={"original":rgb}
    for q in (85,70):
        b=io.BytesIO()
        Image.fromarray(rgb).save(b,format="JPEG",quality=q,optimize=False,progressive=False)
        b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("RGB"))
    h,w=rgb.shape[:2]
    small=Image.fromarray(rgb).resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(small.resize((w,h),Image.Resampling.LANCZOS))
    return out

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

def bounded_box(box,shape):
    h,w=shape[:2]
    x0,y0,x1,y1=box
    return (
        max(0,int(math.floor(x0))),
        max(0,int(math.floor(y0))),
        min(w,int(math.ceil(x1))),
        min(h,int(math.ceil(y1))),
    )

def expanded_box(base,shape,dx=0,dy=0,pad=PAD):
    x0,y0,x1,y1=base
    return bounded_box((x0-pad+dx,y0-pad+dy,x1+pad+dx,y1+pad+dy),shape)

def crop(rgb,box):
    x0,y0,x1,y1=box
    return rgb[y0:y1,x0:x1]

def norm_word(s):
    return re.sub(r"[^A-Z0-9:._/-]+","",s.upper()).strip("._/-:")

def tesseract_hit(a,psm):
    """Return only whether BEE is read and best confidence; discard all OCR text."""
    h,w=a.shape[:2]
    scale=1.0
    if max(h,w)<700:
        scale=3.0
    elif max(h,w)<1200:
        scale=1.6
    if scale!=1.0:
        a=cv2.resize(a,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_CUBIC)
    ok,png=cv2.imencode(".png",a)
    if not ok:
        return False,-1.0
    cmd=[
        "tesseract","stdin","stdout",
        "--oem","1","--psm",str(psm),"-l","eng",
        "-c",f"tessedit_char_whitelist={WHITELIST}",
        "tsv",
    ]
    try:
        p=subprocess.run(cmd,input=png.tobytes(),stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL,timeout=16,check=False)
        txt=p.stdout.decode("utf-8","replace")
    except Exception:
        return False,-1.0
    best=-1.0
    rd=csv.DictReader(io.StringIO(txt),delimiter="\t")
    for r in rd:
        word=(r.get("text") or "").strip()
        if not word:
            continue
        if TOKEN not in norm_word(word):
            continue
        try:
            conf=float(r.get("conf","-1"))
        except Exception:
            conf=-1.0
        best=max(best,conf)
    return best>=0,best

def evaluate_window_variants(vv,base_box,use_jitters):
    jobs=[]
    jitters=JITTERS if use_jitters else ((0,0),)
    for variant in VARIANTS:
        rgb=vv[variant]
        for dx,dy in jitters:
            box=expanded_box(base_box,rgb.shape,dx,dy,PAD)
            c=crop(rgb,box)
            for tf in TRANSFORMS:
                a=transform(c,tf)
                for psm in PSMS:
                    hit,conf=tesseract_hit(a,psm)
                    jobs.append({
                        "variant":variant,
                        "dx":dx,"dy":dy,
                        "transform":tf,"psm":psm,
                        "hit":bool(hit),
                        "conf":float(conf),
                    })
    return summarize_jobs(jobs),jobs

def summarize_jobs(jobs):
    total=len(jobs)
    hits=[x for x in jobs if x["hit"]]
    variant_hits={v:sum(x["hit"] for x in jobs if x["variant"]==v) for v in VARIANTS}
    psm_hits={str(p):sum(x["hit"] for x in jobs if x["psm"]==p) for p in PSMS}
    tf_hits={t:sum(x["hit"] for x in jobs if x["transform"]==t) for t in TRANSFORMS}
    jit_hits={}
    for dx,dy in sorted(set((x["dx"],x["dy"]) for x in jobs)):
        jit_hits[f"{dx},{dy}"]=sum(x["hit"] for x in jobs if x["dx"]==dx and x["dy"]==dy)
    confs=[x["conf"] for x in hits if x["conf"]>=0]
    return {
        "jobs":total,
        "hits":len(hits),
        "hit_rate":float(len(hits)/max(1,total)),
        "variants_with_hit":sum(v>0 for v in variant_hits.values()),
        "psm_modes_with_hit":sum(v>0 for v in psm_hits.values()),
        "transforms_with_hit":sum(v>0 for v in tf_hits.values()),
        "jitters_with_hit":sum(v>0 for v in jit_hits.values()),
        "variant_hits":variant_hits,
        "psm_hits":psm_hits,
        "transform_hits":tf_hits,
        "jitter_hits":jit_hits,
        "mean_hit_conf":float(np.mean(confs)) if confs else -1.0,
        "max_hit_conf":float(max(confs)) if confs else -1.0,
    }

def render_bee(font_path,canvas=(120,64),font_size=31):
    im=Image.new("RGB",canvas,"white")
    draw=ImageDraw.Draw(im)
    font=ImageFont.truetype(font_path,font_size)
    # modern Pillow bbox
    b=draw.textbbox((0,0),TOKEN,font=font)
    tw=b[2]-b[0]; th=b[3]-b[1]
    x=(canvas[0]-tw)//2-b[0]
    y=(canvas[1]-th)//2-b[1]
    draw.text((x,y),TOKEN,font=font,fill="black")
    return np.array(im)

def synthetic_variant_set(rgb):
    return image_variants(rgb)

def max_run(vec):
    best=cur=0
    for z in vec:
        if z:
            cur+=1; best=max(best,cur)
        else:
            cur=0
    return best

def glyph_metrics(rgb):
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    _,bw=cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    dark=bw>0
    h,w=dark.shape
    vrun=max((max_run(dark[:,x]) for x in range(w)),default=0)
    hrun=max((max_run(dark[y,:]) for y in range(h)),default=0)
    gx=cv2.Sobel(gray.astype(np.float32),cv2.CV_32F,1,0,ksize=3)
    gy=cv2.Sobel(gray.astype(np.float32),cv2.CV_32F,0,1,ksize=3)
    ex=float(np.mean(gx*gx)); ey=float(np.mean(gy*gy))
    balance=float(min(ex,ey)/max(ex,ey)) if max(ex,ey)>1e-12 else 0.0
    return {
        "vertical_stem_fraction":float(vrun/max(1,h)),
        "horizontal_run_fraction":float(hrun/max(1,w)),
        "gradient_balance":balance,
        "vertical_edge_energy_fraction":float(ex/(ex+ey+1e-12)),
        "ink_fraction":float(np.mean(dark)),
        "edge_density":float(np.mean(cv2.Canny(gray,60,160)>0)),
    }

def nuisance(rgb):
    m=glyph_metrics(rgb)
    return np.array([
        m["ink_fraction"],
        m["edge_density"],
        m["vertical_edge_energy_fraction"],
        float(255-cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY).mean())/255.0,
    ],dtype=float)

def overlap_fraction(a,b):
    ix0=max(a[0],b[0]); iy0=max(a[1],b[1])
    ix1=min(a[2],b[2]); iy1=min(a[3],b[3])
    inter=max(0,ix1-ix0)*max(0,iy1-iy0)
    aa=max(1,(a[2]-a[0])*(a[3]-a[1]))
    return inter/aa

def matched_control_boxes(rgb,target_window):
    h,w=rgb.shape[:2]
    tw=target_window[2]-target_window[0]
    th=target_window[3]-target_window[1]
    target_crop=crop(rgb,target_window)
    nt=nuisance(target_crop)
    boxes=[]; feats=[]
    for y in range(0,h-th+1,GRID_STEP):
        for x in range(0,w-tw+1,GRID_STEP):
            b=(x,y,x+tw,y+th)
            if overlap_fraction(b,target_window)>0.05:
                continue
            c=crop(rgb,b)
            boxes.append(b); feats.append(nuisance(c))
    F=np.stack(feats)
    sd=F.std(axis=0)
    sd=np.where(sd<1e-9,1.0,sd)
    dist=np.sqrt(np.sum(((F-nt)/sd)**2,axis=1))
    order=np.argsort(dist)[:NEGATIVE_K]
    return [boxes[int(i)] for i in order],nt

def contact_sheet(vv,target_box):
    # 4 variants x 3 transforms, target window only.
    tiles=[]
    for variant in VARIANTS:
        c=crop(vv[variant],target_box)
        for tf in TRANSFORMS:
            a=transform(c,tf)
            a=cv2.resize(a,(240,128),interpolation=cv2.INTER_NEAREST)
            if a.ndim==2:
                a=cv2.cvtColor(a,cv2.COLOR_GRAY2RGB)
            tiles.append((variant,tf,a))
    sheet=Image.new("RGB",(3*250,4*154),"white")
    draw=ImageDraw.Draw(sheet)
    for i,(v,tf,a) in enumerate(tiles):
        row=i//3; col=i%3
        sheet.paste(Image.fromarray(a),(col*250,row*154))
        draw.text((col*250+4,row*154+130),f"{v} / {tf}",fill="black")
    sheet.save(OUT/"bee-target-contact-sheet.png")

def main():
    canonical=load_rgb()
    vv=image_variants(canonical)
    target_window=expanded_box(BASE_BOX,canonical.shape,0,0,PAD)

    target_summary,target_jobs=evaluate_window_variants(vv,BASE_BOX,use_jitters=True)
    target_glyph=glyph_metrics(crop(canonical,target_window))

    # Rendered positive controls.
    positives={}
    pos_rates=[]
    pos_stems=[]
    pos_balances=[]
    for fp in FONT_PATHS:
        if not Path(fp).exists():
            continue
        rgb=render_bee(fp)
        sv=synthetic_variant_set(rgb)
        # Synthetic box is full canvas; PAD=0 equivalent via exact base.
        base=(PAD,PAD,rgb.shape[1]-PAD,rgb.shape[0]-PAD)
        # To reuse expanded_box with PAD, choose interior box whose expansion is full canvas.
        sm,jobs=evaluate_window_variants(sv,base,use_jitters=False)
        gm=glyph_metrics(rgb)
        positives[Path(fp).name]={"ocr":sm,"glyph":gm}
        pos_rates.append(sm["hit_rate"])
        pos_stems.append(gm["vertical_stem_fraction"])
        pos_balances.append(gm["gradient_balance"])

    positive_valid=bool(
        len(positives)>=3
        and np.median(pos_rates)>=0.35
        and min(pos_rates)>=0.15
    )
    positive_median_rate=float(np.median(pos_rates)) if pos_rates else 0.0
    positive_min_stem=float(min(pos_stems)) if pos_stems else 1.0
    positive_min_balance=float(min(pos_balances)) if pos_balances else 1.0

    # Nuisance-matched line-art controls, no jitter.
    control_boxes,nt=matched_control_boxes(canonical,target_window)
    controls=[]
    control_rates=[]
    for i,b in enumerate(control_boxes):
        # The box itself is already padded-size. Convert to an interior base that
        # expands back to b under PAD.
        ib=(b[0]+PAD,b[1]+PAD,b[2]-PAD,b[3]-PAD)
        sm,_=evaluate_window_variants(vv,ib,use_jitters=False)
        gm=glyph_metrics(crop(canonical,b))
        controls.append({
            "index":i,
            "box":list(b),
            "ocr":sm,
            "glyph":gm,
        })
        control_rates.append(sm["hit_rate"])

    max_control_rate=float(max(control_rates)) if control_rates else 0.0
    median_control_rate=float(np.median(control_rates)) if control_rates else 0.0

    rate_gate=bool(
        positive_valid
        and target_summary["hit_rate"]>=0.35*positive_median_rate
        and target_summary["hit_rate"]>=max_control_rate+0.10
    )
    diversity_gate=bool(
        target_summary["variants_with_hit"]>=3
        and target_summary["psm_modes_with_hit"]>=3
        and target_summary["jitters_with_hit"]>=3
    )
    glyph_gate=bool(
        target_glyph["vertical_stem_fraction"]>=0.55*positive_min_stem
        and target_glyph["gradient_balance"]>=0.55*positive_min_balance
    )
    promoted=bool(positive_valid and rate_gate and diversity_gate and glyph_gate)

    contact_sheet(vv,target_window)
    Image.fromarray(crop(canonical,target_window)).save(OUT/"bee-target-window.png")

    result={
        "experiment_id":"A11-EXP-101",
        "scope":"adversarial literal-glyph validation of the single Stage-100 BEE location; no raw OCR persistence and no private-key operations",
        "target_token":TOKEN,
        "stage100_box":list(BASE_BOX),
        "target_window":list(target_window),
        "jitter_offsets":[list(x) for x in JITTERS],
        "transforms":list(TRANSFORMS),
        "psm_modes":list(PSMS),
        "variants":list(VARIANTS),
        "target_ocr":target_summary,
        "target_glyph":target_glyph,
        "positive_controls":positives,
        "positive_controls_valid":positive_valid,
        "positive_median_hit_rate":positive_median_rate,
        "positive_min_vertical_stem_fraction":positive_min_stem,
        "positive_min_gradient_balance":positive_min_balance,
        "matched_lineart_controls":controls,
        "max_matched_control_hit_rate":max_control_rate,
        "median_matched_control_hit_rate":median_control_rate,
        "gates":{
            "rate_gate":rate_gate,
            "diversity_gate":diversity_gate,
            "glyph_gate":glyph_gate,
        },
        "promotion_rule":"rendered BEE controls valid; target hit rate >=35% of positive median and >= max matched-control rate +0.10; target hits in >=3 variants, >=3 PSM modes, >=3 crop jitters; vertical-stem fraction and gradient balance each >=55% of the weakest rendered BEE control",
        "promoted":promoted,
        "interpretation_guard":"Promotion means only that the patch behaves like literal BEE text under adversarial tests; it does not establish semantic relevance.",
        "safety_guard":"Raw OCR is discarded. Only BEE hit/no-hit/confidence aggregates are persisted. No key candidate is constructed or verified.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 101 — BEE adversarial glyph-validity audit",
        "",
        "**Experiment:** A11-EXP-101",
        "",
        f"- rendered BEE controls valid: **{positive_valid}**",
        f"- target OCR hit rate: **{target_summary['hit_rate']:.3f}** ({target_summary['hits']}/{target_summary['jobs']})",
        f"- positive-control median hit rate: **{positive_median_rate:.3f}**",
        f"- max matched line-art control hit rate: **{max_control_rate:.3f}**",
        f"- target variants with BEE hit: **{target_summary['variants_with_hit']}/4**",
        f"- target PSM modes with hit: **{target_summary['psm_modes_with_hit']}/6**",
        f"- target crop jitters with hit: **{target_summary['jitters_with_hit']}/5**",
        f"- target vertical-stem fraction: **{target_glyph['vertical_stem_fraction']:.3f}**",
        f"- weakest positive vertical-stem fraction: **{positive_min_stem:.3f}**",
        f"- target gradient balance: **{target_glyph['gradient_balance']:.3f}**",
        f"- weakest positive gradient balance: **{positive_min_balance:.3f}**",
        f"- rate gate: **{rate_gate}**",
        f"- diversity gate: **{diversity_gate}**",
        f"- glyph gate: **{glyph_gate}**",
        f"- stage promoted: **{promoted}**",
        "",
        "## Rendered BEE controls",
        "",
        "| font | hit rate | variants | PSM modes | vertical stem | gradient balance |",
        "|:---|---:|---:|---:|---:|---:|",
    ]
    for name,r in positives.items():
        o=r["ocr"]; g=r["glyph"]
        md.append(
            f"| {name} | {o['hit_rate']:.3f} | {o['variants_with_hit']}/4 | "
            f"{o['psm_modes_with_hit']}/6 | {g['vertical_stem_fraction']:.3f} | "
            f"{g['gradient_balance']:.3f} |"
        )

    md += [
        "",
        "## Matched line-art controls",
        "",
        "| idx | box | BEE hit rate | vertical stem | gradient balance |",
        "|---:|:---|---:|---:|---:|",
    ]
    for r in controls:
        md.append(
            f"| {r['index']} | {r['box']} | {r['ocr']['hit_rate']:.3f} | "
            f"{r['glyph']['vertical_stem_fraction']:.3f} | {r['glyph']['gradient_balance']:.3f} |"
        )

    md += ["","## Interpretation",""]
    if not positive_valid:
        md.append("Rendered BEE controls do not validate the adversarial harness. This is an implementation failure and must be fixed under Stage 101.")
    elif promoted:
        md.append("The localized patch behaves substantially more like literal BEE text than matched line-art controls across crop perturbations, PSM modes and lossy variants. Only now is direct visual/rebus interpretation justified.")
    else:
        md.append("The localized Stage-100 BEE reading fails the adversarial literal-glyph test. Retire BEE as a Tesseract hallucination caused by stable line hatching; do not interpret the word semantically.")

    md += [
        "",
        "Artifacts: `bee-target-window.png`, `bee-target-contact-sheet.png`.",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-101",
        "positive_valid":positive_valid,
        "target_hit_rate":target_summary["hit_rate"],
        "max_control_rate":max_control_rate,
        "gates":{"rate":rate_gate,"diversity":diversity_gate,"glyph":glyph_gate},
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
