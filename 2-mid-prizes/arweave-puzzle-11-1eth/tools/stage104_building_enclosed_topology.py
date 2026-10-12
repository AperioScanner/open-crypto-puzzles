#!/usr/bin/env python3
"""Stage 104: enclosed-white-space / window-topology audit across 12 buildings.

Safe visual-structure experiment only.

This stage tests whether building interiors contain robust counts of enclosed
white regions ("holes"/window-like spaces) that survive threshold and lossy
image changes. This is distinct from prior dark-component/perimeter counts.

No private-key generation, derivation, reconstruction, enumeration,
verification, or wallet access is performed.
"""
from __future__ import annotations

import io, json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE12=ROOT/"analysis"/"runs"/"stage12-count-perimeter"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage104-building-enclosed-topology"
OUT.mkdir(parents=True,exist_ok=True)

THRESHOLDS=(100,130,160,190)
MIN_AREA=9
MAX_FRAC=0.15

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

def building_boxes():
    j=json.loads(STAGE12.read_text())
    rows=[]
    for r in j["regions"]:
        if r["name"].startswith("building_"):
            rows.append((r["name"],tuple(map(int,r["bbox"]))))
    rows.sort()
    if len(rows)!=12:
        raise RuntimeError(f"expected 12 building boxes, got {len(rows)}")
    return rows

def crop(a,b):
    x0,y0,x1,y1=b
    return a[y0:y1,x0:x1]

def binary_dark(c,thr):
    dark=(c<thr).astype(np.uint8)*255
    # Join tiny raster gaps in visible outlines, but do not bridge distant marks.
    return cv2.morphologyEx(dark,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8),iterations=1)

def hole_count_cc(dark):
    white=(dark==0).astype(np.uint8)
    n,lab,stats,_=cv2.connectedComponentsWithStats(white,8)
    h,w=white.shape
    limit=MAX_FRAC*h*w
    count=0
    areas=[]
    for i in range(1,n):
        x,y,ww,hh,area=map(int,stats[i])
        touches=(x==0 or y==0 or x+ww>=w or y+hh>=h)
        if touches: continue
        if MIN_AREA<=area<=limit:
            count+=1
            areas.append(area)
    return count,sorted(areas)

def hole_count_contours(dark):
    # Holes in a dark-foreground mask appear as child contours.
    contours,hier=cv2.findContours(dark,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hier is None:
        return 0,[]
    hier=hier[0]
    h,w=dark.shape
    limit=MAX_FRAC*h*w
    count=0
    areas=[]
    for i,c in enumerate(contours):
        parent=int(hier[i][3])
        if parent<0: continue
        area=float(abs(cv2.contourArea(c)))
        if MIN_AREA<=area<=limit:
            count+=1
            areas.append(area)
    return count,sorted(areas)

def eval_crop(c):
    rows=[]
    for thr in THRESHOLDS:
        dark=binary_dark(c,thr)
        c1,a1=hole_count_cc(dark)
        c2,a2=hole_count_contours(dark)
        rows.append({
            "threshold":thr,
            "cc_count":c1,
            "contour_count":c2,
            "agreement":c1==c2,
        })
    pairs=[(r["cc_count"],r["contour_count"]) for r in rows if r["agreement"]]
    if not pairs:
        return {"thresholds":rows,"consensus":None,"support":0}
    vals=[x[0] for x in pairs]
    # modal count among thresholds with method agreement
    uniq,counts=np.unique(vals,return_counts=True)
    idx=int(np.argmax(counts))
    val=int(uniq[idx]); support=int(counts[idx])
    return {"thresholds":rows,"consensus":val,"support":support}

def synthetic(nholes,w=110,h=160):
    im=np.full((h,w),255,np.uint8)
    # closed building shell
    cv2.rectangle(im,(10,10),(w-11,h-11),0,3)
    # n white "windows" enclosed by black rectangular frames
    coords=[(25,35),(65,35),(25,85),(65,85)]
    for i in range(nholes):
        x,y=coords[i]
        cv2.rectangle(im,(x-8,y-8),(x+12,y+12),0,3)
    return im

def main():
    gray=load_gray()
    vv=variants(gray)
    boxes=building_boxes()

    controls={}
    for n in range(4):
        e=eval_crop(synthetic(n))
        controls[str(n)]=e
    controls_pass=all(
        controls[str(n)]["consensus"]==n and controls[str(n)]["support"]>=3
        for n in range(4)
    )

    buildings=[]
    stable=0
    seq=[]
    for name,b in boxes:
        per={v:eval_crop(crop(a,b)) for v,a in vv.items()}
        vals=[per[v]["consensus"] for v in vv]
        supports=[per[v]["support"] for v in vv]
        ok=bool(None not in vals and len(set(vals))==1 and min(supports)>=3)
        val=int(vals[0]) if ok else None
        if ok:
            stable+=1
            seq.append(val)
        else:
            seq.append(None)
        buildings.append({
            "name":name,
            "box":list(b),
            "variants":per,
            "stable":ok,
            "count":val,
        })

    distinct=sorted(set(x for x in seq if x is not None))
    promoted=bool(controls_pass and stable>=9 and len(distinct)>=3)

    result={
        "experiment_id":"A11-EXP-104",
        "scope":"enclosed-white-space topology counts in 12 fixed building interiors; no private-key operations",
        "thresholds":list(THRESHOLDS),
        "min_area":MIN_AREA,
        "max_area_fraction":MAX_FRAC,
        "synthetic_controls":controls,
        "controls_pass":controls_pass,
        "buildings":buildings,
        "stable_buildings":stable,
        "stable_count_sequence":seq,
        "distinct_stable_counts":distinct,
        "promotion_rule":"synthetic 0/1/2/3-hole controls pass; >=9/12 buildings have same count across original/JPEG85/JPEG70/resize with >=3/4 threshold support and connected-component/contour agreement; >=3 distinct count values",
        "promoted":promoted,
        "interpretation_guard":"Promotion establishes only a robust visible topological count sequence, not a mapping to secret material.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    seq_txt=" ".join("?" if x is None else str(x) for x in seq)
    md=[
        "# Stage 104 — building enclosed-space topology audit",
        "",
        "**Experiment:** A11-EXP-104",
        "",
        f"- synthetic controls pass: **{controls_pass}**",
        f"- stable buildings: **{stable}/12**",
        f"- stable count sequence: **{seq_txt}**",
        f"- distinct stable counts: **{distinct}**",
        f"- promoted: **{promoted}**",
        "",
        "| building | stable count | stable | original support |",
        "|:---|---:|:---:|---:|",
    ]
    for r in buildings:
        o=r["variants"]["original"]
        md.append(f"| {r['name']} | {'' if r['count'] is None else r['count']} | {r['stable']} | {o['support']}/4 |")

    md += ["","## Interpretation",""]
    if promoted:
        md.append("The building interiors contain a robust, nontrivial enclosed-space count sequence across lossy variants and two independent topology estimators. This visible count family is eligible for a semantic/ordering follow-up.")
    else:
        md.append("Enclosed white-space counts are not sufficiently stable/nontrivial across the 12 buildings. Retire building-hole/window topology as a coding family.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-104",
        "controls_pass":controls_pass,"stable":stable,
        "distinct":distinct,"promoted":promoted
    }))

if __name__=="__main__":
    main()
