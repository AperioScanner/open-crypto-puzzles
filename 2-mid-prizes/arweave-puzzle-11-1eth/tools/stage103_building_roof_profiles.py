#!/usr/bin/env python3
"""Stage 103: 12-building roof-profile category audit.

Safe visual-structure experiment only.

Tests whether the twelve buildings form a robust sequence of roof-profile
categories independent of the already-tested H/V interior hatching.

Categories:
  "/"  = roof rises to the right
  "-"  = approximately flat
  "\\" = roof falls to the right

Two independent estimators:
- robust top-envelope slope
- near-horizontal Hough roof-line slope

No private-key generation, derivation, reconstruction, enumeration,
verification, or wallet access is performed.
"""
from __future__ import annotations

import io, json, math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage103-building-roof-profiles"
OUT.mkdir(parents=True,exist_ok=True)

THRESHOLDS=(110,150,190)
SLOPE_DEAD=0.08

def load_gray():
    return np.array(Image.open(SOURCE).convert("L"))

def variants(gray):
    out={"original":gray}
    for q in (85,70):
        b=io.BytesIO()
        Image.fromarray(gray).save(b,format="JPEG",quality=q,optimize=False,progressive=False)
        b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("L"))
    h,w=gray.shape
    small=Image.fromarray(gray).resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(small.resize((w,h),Image.Resampling.LANCZOS))
    return out

def cat_from_slope(s):
    # y increases downward, so negative image slope means visually rising right.
    if s < -SLOPE_DEAD:
        return "/"
    if s > SLOPE_DEAD:
        return "\\"
    return "-"

def robust_envelope_slope(c):
    h,w=c.shape
    slopes=[]
    for thr in THRESHOLDS:
        bw=c<thr
        xs=[]; ys=[]
        for x in range(w):
            yy=np.flatnonzero(bw[:,x])
            if len(yy):
                xs.append(x); ys.append(int(yy[0]))
        if len(xs)<max(12,int(0.30*w)):
            continue
        xs=np.asarray(xs,float); ys=np.asarray(ys,float)
        # central 80% avoids side walls dominating.
        lo=int(0.10*w); hi=int(0.90*w)
        m=(xs>=lo)&(xs<=hi)
        xs=xs[m]; ys=ys[m]
        if len(xs)<10: continue
        # Trim obvious interior outliers relative to median y.
        med=np.median(ys)
        mad=np.median(np.abs(ys-med))+1e-9
        keep=np.abs(ys-med)<=max(6.0,3.5*mad)
        xs=xs[keep]; ys=ys[keep]
        if len(xs)<10: continue
        slope=float(np.polyfit(xs,ys,1)[0])
        slopes.append(slope)
    return float(np.median(slopes)) if slopes else 999.0

def hough_roof_slope(c):
    vals=[]
    for thr in THRESHOLDS:
        bw=((c<thr).astype(np.uint8)*255)
        e=cv2.Canny(bw,50,150)
        raw=cv2.HoughLinesP(
            e,1,np.pi/180,threshold=max(8,int(c.shape[1]*0.10)),
            minLineLength=max(10,int(c.shape[1]*0.20)),maxLineGap=5
        )
        if raw is None:
            continue
        candidates=[]
        for x1,y1,x2,y2 in np.asarray(raw).reshape(-1,4):
            dx=float(x2-x1); dy=float(y2-y1)
            if abs(dx)<5: continue
            slope=dy/dx
            # roof should be relatively shallow, near top of crop.
            if abs(slope)>0.8: continue
            my=(y1+y2)/2
            if my>0.65*c.shape[0]: continue
            ln=math.hypot(dx,dy)
            candidates.append((ln,-my,slope))
        if candidates:
            candidates.sort(reverse=True)
            vals.append(float(candidates[0][2]))
    return float(np.median(vals)) if vals else 999.0

def eval_crop(c):
    a=robust_envelope_slope(c)
    b=hough_roof_slope(c)
    ca=cat_from_slope(a) if abs(a)<100 else "?"
    cb=cat_from_slope(b) if abs(b)<100 else "?"
    consensus=ca if ca==cb else "?"
    return {
        "envelope_slope":a,
        "hough_slope":b,
        "envelope_category":ca,
        "hough_category":cb,
        "consensus":consensus,
    }

def building_crop(gray,b):
    x0,x1,ry=int(b["x0"]),int(b["x1"]),int(b["roof_y"])
    # narrow roof band, including a little above and enough below for top edge.
    y0=max(0,ry-12)
    y1=min(gray.shape[0],ry+52)
    return gray[y0:y1,x0:x1],(x0,y0,x1,y1)

def synthetic(kind,w=120,h=64):
    im=np.full((h,w),255,np.uint8)
    if kind=="-":
        p1=(10,24); p2=(110,24)
    elif kind=="/":
        p1=(10,40); p2=(110,18)
    else:
        p1=(10,18); p2=(110,40)
    cv2.line(im,p1,p2,0,3,cv2.LINE_AA)
    cv2.line(im,(10,40),(10,62),0,2,cv2.LINE_AA)
    cv2.line(im,(110,40),(110,62),0,2,cv2.LINE_AA)
    return im

def main():
    gray=load_gray()
    vv=variants(gray)
    geom=json.loads(GEOM.read_text())
    buildings=geom["buildings"]

    controls={}
    for kind in ("/","-","\\"):
        e=eval_crop(synthetic(kind))
        controls[kind]=e
    controls_pass=all(controls[k]["consensus"]==k for k in controls)

    rows=[]
    stable=0
    sequence=[]
    for b in buildings:
        per={}
        box=None
        for name,a in vv.items():
            c,box=building_crop(a,b)
            per[name]=eval_crop(c)
        cons=[per[v]["consensus"] for v in vv]
        ok=bool(len(set(cons))==1 and cons[0]!="?")
        cat=cons[0] if ok else "?"
        if ok: stable+=1
        sequence.append(cat)
        rows.append({
            "id":int(b["id"]),
            "box":list(box),
            "variants":per,
            "stable":ok,
            "category":cat,
        })

    classes=set(x for x in sequence if x in ("/","-","\\"))
    nontrivial=len(classes)>=2
    promoted=bool(controls_pass and stable>=10 and nontrivial)

    result={
        "experiment_id":"A11-EXP-103",
        "scope":"12-building roof-profile category stability independent of H/V hatching; no private-key operations",
        "thresholds":list(THRESHOLDS),
        "slope_dead_zone":SLOPE_DEAD,
        "synthetic_controls":controls,
        "controls_pass":controls_pass,
        "buildings":rows,
        "stable_buildings":stable,
        "roof_sequence":"".join(sequence),
        "categories_present":sorted(classes),
        "nontrivial":nontrivial,
        "promotion_rule":"synthetic /,-,\\ controls pass; >=10/12 buildings have same envelope+Hough consensus category across original/JPEG85/JPEG70/resize; >=2 categories represented",
        "promoted":promoted,
        "interpretation_guard":"Promotion establishes only a robust visible roof-category sequence, not a key mapping.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 103 — 12-building roof-profile category audit",
        "",
        "**Experiment:** A11-EXP-103",
        "",
        f"- synthetic controls pass: **{controls_pass}**",
        f"- stable buildings: **{stable}/12**",
        f"- roof sequence: **{''.join(sequence)}**",
        f"- categories present: **{sorted(classes)}**",
        f"- promoted: **{promoted}**",
        "",
        "| building | category | stable | orig envelope slope | orig Hough slope |",
        "|---:|:---:|:---:|---:|---:|",
    ]
    for r in rows:
        o=r["variants"]["original"]
        md.append(
            f"| {r['id']} | {r['category']} | {r['stable']} | "
            f"{o['envelope_slope']:.3f} | {o['hough_slope']:.3f} |"
        )
    md += ["","## Interpretation",""]
    if promoted:
        md.append("The building roofs form a robust mixed visible category sequence under two independent estimators and lossy re-encoding. This sequence is eligible for a semantic ordering/selection follow-up.")
    else:
        md.append("Building roof profiles do not yield a sufficiently stable, nontrivial category sequence. Retire roof-profile coding.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-103",
        "controls_pass":controls_pass,
        "stable":stable,
        "sequence":"".join(sequence),
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
