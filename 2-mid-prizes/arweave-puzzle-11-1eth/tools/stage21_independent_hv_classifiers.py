#!/usr/bin/env python3
"""Stage 21: independent replication of the 12-building H/V texture sequence.

Non-cryptographic. Re-tests the visual H/V labels with two methods that are independent
of Stage 5's signed Sobel classifier: Fourier anisotropy and multi-scale morphological
line response. The goal is to decide whether the H/V pattern itself is a classifier artifact.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage21-independent-hv-classifiers"
OUT.mkdir(parents=True,exist_ok=True)

BASELINE="HHVVHHVHHHHV"

def inner_crop(gray,b,frac=0.12):
    x0,x1,y0,y1=b["x0"],b["x1"],b["roof_y"],b["bottom_y"]
    mx=max(5,int((x1-x0)*frac)); my=max(6,int((y1-y0)*frac))
    return gray[y0+my:y1-my,x0+mx:x1-mx]

def fourier_class(crop):
    x=crop.astype(np.float64)
    x-=x.mean()
    h,w=x.shape
    if min(h,w)<12: return "M",0.0
    wy=np.hanning(h)[:,None]; wx=np.hanning(w)[None,:]
    p=np.abs(np.fft.fftshift(np.fft.fft2(x*wy*wx)))**2
    yy,xx=np.indices(p.shape)
    cy=(h-1)/2; cx=(w-1)/2
    dx=xx-cx; dy=yy-cy
    r=np.hypot(dx,dy)
    valid=(r>=3)&(r<=0.45*min(h,w))
    # Frequency energy near horizontal axis indicates vertical spatial strokes.
    horiz=valid&(np.abs(dy)<=0.35*np.maximum(np.abs(dx),1e-9))
    vert=valid&(np.abs(dx)<=0.35*np.maximum(np.abs(dy),1e-9))
    eh=float(p[horiz].sum()); ev=float(p[vert].sum())
    score=(eh-ev)/(eh+ev+1e-12)
    cls="V" if score>0.05 else ("H" if score<-0.05 else "M")
    return cls,score

def morph_class(crop):
    # Threshold family and line lengths fixed in advance.
    votes=[]; details=[]
    for thr in (100,140,180):
        ink=(crop<thr).astype(np.uint8)*255
        for L in (7,11,15):
            kh=cv2.getStructuringElement(cv2.MORPH_RECT,(L,1))
            kv=cv2.getStructuringElement(cv2.MORPH_RECT,(1,L))
            oh=cv2.morphologyEx(ink,cv2.MORPH_OPEN,kh)
            ov=cv2.morphologyEx(ink,cv2.MORPH_OPEN,kv)
            eh=float(oh.sum()); ev=float(ov.sum())
            score=(ev-eh)/(ev+eh+1e-12)
            # More surviving vertical line structure => V.
            c="V" if score>0.03 else ("H" if score<-0.03 else "M")
            votes.append(c); details.append({"threshold":thr,"length":L,"score":score,"class":c})
    h=votes.count("H"); v=votes.count("V")
    cls="V" if v>h else ("H" if h>v else "M")
    margin=(v-h)/len(votes)
    return cls,margin,details

def main():
    g=json.loads(GEOM.read_text())
    img=cv2.imread(str(SOURCE),cv2.IMREAD_UNCHANGED)
    if img is None: raise SystemExit("image load failed")
    gray=img[:,:,0] if img.ndim==3 else img

    fseq=[]; mseq=[]; rows=[]
    for b in g["buildings"]:
        crop=inner_crop(gray,b)
        fc,fs=fourier_class(crop)
        mc,mm,md=morph_class(crop)
        fseq.append(fc); mseq.append(mc)
        rows.append({"id":b["id"],"baseline":BASELINE[b["id"]-1],
                     "fourier":{"class":fc,"score":fs},
                     "morph":{"class":mc,"vote_margin":mm,"details":md}})
    fseq="".join(fseq); mseq="".join(mseq)
    fagree=sum(a==b for a,b in zip(fseq,BASELINE))
    magree=sum(a==b for a,b in zip(mseq,BASELINE))
    both=sum((fseq[i]==BASELINE[i] and mseq[i]==BASELINE[i]) for i in range(12))
    result={
      "experiment_id":"A11-EXP-021",
      "scope":"independent visual texture classifiers only; no private-key operations",
      "baseline":BASELINE,
      "fourier_sequence":fseq,
      "fourier_agreement":fagree,
      "morph_sequence":mseq,
      "morph_agreement":magree,
      "both_methods_agree_with_baseline":both,
      "buildings":rows,
      "promotion_rule":"pattern considered independently replicated if each method agrees with baseline on >=10/12 buildings and at least 9/12 are jointly confirmed",
      "replicated":bool(fagree>=10 and magree>=10 and both>=9)
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=["# Stage 21 — independent H/V classifier replication","",
        "**Experiment:** A11-EXP-021","",
        f"- Stage-5 baseline: `{BASELINE}`",
        f"- Fourier anisotropy: `{fseq}` — agreement **{fagree}/12**",
        f"- Morphological line response: `{mseq}` — agreement **{magree}/12**",
        f"- Jointly confirmed baseline labels: **{both}/12**",
        f"- Pre-registered replication rule satisfied: **{result['replicated']}**","",
        "## Interpretation",""]
    if result["replicated"]:
        md.append("The H/V skyline pattern survives two classifiers that do not reuse the Stage-5 signed-Sobel decision rule. This makes a classifier artifact less likely. It still does not validate the hexadecimal 0x321 interpretation.")
    else:
        md.append("The H/V pattern does not replicate strongly enough under two independent classifiers. That would substantially weaken the skyline-marker hypothesis and support retiring it.")
    md += ["","Stage 22 will synthesize all 321-specific evidence and apply a stop rule before the research pivots to bit-level steganalysis.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-021","fourier":fagree,"morph":magree,"joint":both,"replicated":result["replicated"]}))

if __name__=="__main__": main()
