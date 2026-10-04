#!/usr/bin/env python3
"""Stage 31: format-invariance audit of visual H/V structure versus exact low bits.

Non-cryptographic. Re-encodes/resamples the source image, then compares:
1) independent H/V building-texture classifiers, and
2) exact grayscale low-bit agreement against the original.

The goal is route selection, not payload extraction.
"""
from __future__ import annotations
import io, json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage31-format-invariance"
OUT.mkdir(parents=True,exist_ok=True)

BASELINE="HHVVHHVHHHHV"

def inner_crop(gray,b,frac=0.12):
    x0,x1,y0,y1=b["x0"],b["x1"],b["roof_y"],b["bottom_y"]
    mx=max(5,int((x1-x0)*frac))
    my=max(6,int((y1-y0)*frac))
    return gray[y0+my:y1-my,x0+mx:x1-mx]

def fourier_class(crop):
    x=crop.astype(np.float64)
    x-=x.mean()
    h,w=x.shape
    if min(h,w)<12:
        return "M",0.0
    wy=np.hanning(h)[:,None]
    wx=np.hanning(w)[None,:]
    p=np.abs(np.fft.fftshift(np.fft.fft2(x*wy*wx)))**2
    yy,xx=np.indices(p.shape)
    cy=(h-1)/2
    cx=(w-1)/2
    dx=xx-cx
    dy=yy-cy
    r=np.hypot(dx,dy)
    valid=(r>=3)&(r<=0.45*min(h,w))
    horiz=valid&(np.abs(dy)<=0.35*np.maximum(np.abs(dx),1e-9))
    vert=valid&(np.abs(dx)<=0.35*np.maximum(np.abs(dy),1e-9))
    eh=float(p[horiz].sum())
    ev=float(p[vert].sum())
    score=(eh-ev)/(eh+ev+1e-12)
    cls="V" if score>0.05 else ("H" if score<-0.05 else "M")
    return cls,score

def morph_class(crop):
    votes=[]
    for thr in (100,140,180):
        ink=(crop<thr).astype(np.uint8)*255
        for L in (7,11,15):
            kh=cv2.getStructuringElement(cv2.MORPH_RECT,(L,1))
            kv=cv2.getStructuringElement(cv2.MORPH_RECT,(1,L))
            oh=cv2.morphologyEx(ink,cv2.MORPH_OPEN,kh)
            ov=cv2.morphologyEx(ink,cv2.MORPH_OPEN,kv)
            eh=float(oh.sum())
            ev=float(ov.sum())
            score=(ev-eh)/(ev+eh+1e-12)
            votes.append("V" if score>0.03 else ("H" if score<-0.03 else "M"))
    h=votes.count("H")
    v=votes.count("V")
    return "V" if v>h else ("H" if h>v else "M")

def classify(gray,geom):
    fs=[]
    ms=[]
    for b in geom["buildings"]:
        c=inner_crop(gray,b)
        fs.append(fourier_class(c)[0])
        ms.append(morph_class(c))
    fseq="".join(fs)
    mseq="".join(ms)
    return {
        "fourier_sequence":fseq,
        "morph_sequence":mseq,
        "fourier_agreement":sum(a==b for a,b in zip(fseq,BASELINE)),
        "morph_agreement":sum(a==b for a,b in zip(mseq,BASELINE)),
    }

def jpeg_roundtrip(gray,quality):
    im=Image.fromarray(gray,mode="L")
    buf=io.BytesIO()
    im.save(buf,format="JPEG",quality=quality,optimize=False,progressive=False)
    buf.seek(0)
    return np.array(Image.open(buf).convert("L"))

def resample_roundtrip(gray,scale):
    h,w=gray.shape
    im=Image.fromarray(gray,mode="L")
    nw=max(1,round(w*scale))
    nh=max(1,round(h*scale))
    small=im.resize((nw,nh),Image.Resampling.LANCZOS)
    back=small.resize((w,h),Image.Resampling.LANCZOS)
    return np.array(back)

def bit_agreement(original,changed,mask=None):
    rows=[]
    if mask is None:
        mask=np.ones(original.shape,dtype=bool)
    for bit in range(4):
        a=((original>>bit)&1)[mask]
        b=((changed>>bit)&1)[mask]
        rows.append({"bit":bit,"agreement":float(np.mean(a==b))})
    return rows

def main():
    src=np.array(Image.open(SOURCE))
    original=src[:,:,0] if src.ndim==3 else src
    geom=json.loads(GEOM.read_text())

    variants={
        "original":original,
        "jpeg_q95":jpeg_roundtrip(original,95),
        "jpeg_q85":jpeg_roundtrip(original,85),
        "jpeg_q70":jpeg_roundtrip(original,70),
        "down75_up":resample_roundtrip(original,0.75),
        "up125_down":resample_roundtrip(original,1.25),
    }
    variants["jpeg85_down75_up"]=resample_roundtrip(variants["jpeg_q85"],0.75)

    foreground=original<250
    skyline=np.zeros_like(foreground,dtype=bool)
    skyline[:340,200:]=True
    fg_skyline=foreground&skyline

    rows=[]
    for name,img in variants.items():
        c=classify(img,geom)
        rows.append({
            "variant":name,
            **c,
            "bit_agreement_full":bit_agreement(original,img),
            "bit_agreement_foreground":bit_agreement(original,img,foreground),
            "bit_agreement_foreground_skyline":bit_agreement(original,img,fg_skyline),
            "mean_abs_pixel_delta":float(np.mean(np.abs(original.astype(np.int16)-img.astype(np.int16)))),
        })

    lossy=[r for r in rows if r["variant"]!="original"]
    visual_stable=all(r["fourier_agreement"]>=10 and r["morph_agreement"]>=10 for r in lossy)
    lowbit_collapsed=sum(
        next(x["agreement"] for x in r["bit_agreement_foreground"] if x["bit"]==0)<0.65
        for r in lossy
    )>=3

    result={
        "experiment_id":"A11-EXP-031",
        "scope":"format/resampling robustness of visual H/V texture versus exact grayscale low-bit agreement; no payload reconstruction or private-key operations",
        "baseline":BASELINE,
        "variants":rows,
        "decision_rule":{
            "visual_stable":"all lossy variants must have >=10/12 agreement under both independent H/V classifiers",
            "lowbit_collapsed":"at least 3 lossy variants must have foreground bit-0 exact agreement <0.65",
        },
        "visual_stable":bool(visual_stable),
        "lowbit_collapsed":bool(lowbit_collapsed),
        "promote_visual_semantic_route":bool(visual_stable and lowbit_collapsed),
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 31 — format-invariance audit",
        "",
        "**Experiment:** A11-EXP-031",
        "",
        "| variant | Fourier agree | Morph agree | fg bit0 agree | fg-sky bit0 agree | mean abs pixel delta |",
        "|:---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        fg0=next(x["agreement"] for x in r["bit_agreement_foreground"] if x["bit"]==0)
        sg0=next(x["agreement"] for x in r["bit_agreement_foreground_skyline"] if x["bit"]==0)
        md.append(f"| {r['variant']} | {r['fourier_agreement']}/12 | {r['morph_agreement']}/12 | {fg0:.4f} | {sg0:.4f} | {r['mean_abs_pixel_delta']:.3f} |")
    md += [
        "",
        f"- Visual H/V stability rule: **{visual_stable}**",
        f"- Low-bit-collapse rule: **{lowbit_collapsed}**",
        f"- Promote format-invariant visual/semantic route: **{result['promote_visual_semantic_route']}**",
        "",
        "## Interpretation",
        "",
        "If the H/V texture survives lossy conversion/resampling while exact bit-0 agreement collapses, that supports prioritizing visible/semantic image structure over fragile exact-pixel LSB encoding. This is route-selection evidence, not proof that H/V itself is the hidden carrier.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-031",
        "visual_stable":visual_stable,
        "lowbit_collapsed":lowbit_collapsed,
        "promote_visual_semantic_route":result["promote_visual_semantic_route"],
    }))

if __name__=="__main__":
    main()
