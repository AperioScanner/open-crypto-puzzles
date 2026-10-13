#!/usr/bin/env python3
"""A11-EXP-131 — isolated hand-drawn marks in blank sky (image-only).

Prior image-only experiments used skyline buildings, water, sail/pier and the
very first 48px strip. This test confines its fixed windows to blank sky
*outside* building rectangles, and checks whether deliberate short isolated
dashes recur reliably versus single-pixel raster/scanning specks.

No text decoding, mnemonic, key material, address checks, web/social browsing
or wallet activity. A reproducible mark count alone is not a code.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage131-isolated-sky-marks"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"

# Predeclared unoccupied sky: intentionally excludes facades, boat hulls,
# water and the 0..48 full-canvas strip used by Stage12.
ROIS={
    "left_blank_sky":(20,57,195,215),
    "central_sky_gap":(792,54,864,174),
    "upper_right_sky":(1170,53,1335,96),
    "right_top_sky":(1363,15,1491,92),
}
FORMATS=("original","jpeg85","jpeg70","down75_up")
THRESHOLDS=(90,140,190)
MIN_AREA=12
MAX_AREA=250
MIN_MAJOR=8
MIN_MINOR=2
MIN_BORDER=4
MAX_EXTENT=.80
MIN_STABLE_REGIONS=3
MIN_POSITIVE_REGIONS=2

def _eligible(x,y,w,h,area,width,height):
    if not(MIN_AREA<=area<=MAX_AREA):return False
    if x<MIN_BORDER or y<MIN_BORDER: return False
    if x+w>=width-MIN_BORDER or y+h>=height-MIN_BORDER:return False
    major=max(w,h);minor=min(w,h)
    if major<MIN_MAJOR or minor<MIN_MINOR:return False
    extent=area/max(1,w*h)
    if extent>MAX_EXTENT:return False
    return True

def connected_components(gray,thr):
    bw=(gray<thr).astype(np.uint8)
    n,_,stats,_=cv2.connectedComponentsWithStats(bw,8)
    height,width=gray.shape
    ans=[]
    for row in stats[1:]:
        x,y,w,h,area=(int(v) for v in row)
        if _eligible(x,y,w,h,area,width,height):
            ans.append((x,y,w,h))
    return sorted(ans)

def contour_components(gray,thr):
    bw=(gray<thr).astype(np.uint8)*255
    contours,_=cv2.findContours(bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    height,width=gray.shape
    ans=[]
    for c in contours:
        x,y,w,h=cv2.boundingRect(c)
        # Pixel occupied count inside bounding rectangle is more reliable
        # than geometric polygon area for thin pencil strokes.
        local=bw[y:y+h,x:x+w]
        area=int(np.count_nonzero(local))
        if _eligible(x,y,w,h,area,width,height):
            ans.append((x,y,w,h))
    return sorted(ans)

def synthetic(shape,typ):
    h,w=shape
    a=np.full((h,w),255,np.uint8)
    if typ=="dashes":
        for frac in (.22,.49,.76):
            x=int(w*frac);y=int(h*frac)
            cv2.line(a,(x-6,y-3),(x+8,y+4),0,2,cv2.LINE_AA)
    elif typ=="speckles":
        rng=np.random.default_rng(131)
        # Single-pixel salt noise cannot count as an intentional dash.
        for _ in range(38):
            x=int(rng.integers(8,w-8))
            y=int(rng.integers(8,h-8))
            a[y,x]=0
    else:raise ValueError(typ)
    return a

def analyze(gray):
    by={}
    for v,im in variants(gray).items():
        if v not in FORMATS:continue
        by[v]={str(t):{
            "cc":connected_components(im,t),
            "contour":contour_components(im,t)
        } for t in THRESHOLDS}
    sequences=[d[k] for v in by.values() for d in v.values() for k in ("cc","contour")]
    values=[len(x) for x in sequences]
    # Compare each sorted bounding box against baseline at ≤3 px
    # translation/scale drift so a count from an unrelated blotch cannot
    # silently become the same symbolic mark.
    baseline=sequences[0]
    def boxes_near(test):
        return (len(test)==len(baseline)
                and all(all(abs(a-b)<=3 for a,b in zip(box1,box2))
                        for box1,box2 in zip(baseline,test)))
    stable=all(boxes_near(s) for s in sequences)
    return {
        "by_variant":{
            v:{k:{m:len(z) for m,z in value.items()} for k,value in rows.items()}
            for v,rows in by.items()
        },
        "stable":bool(stable),
        "stable_count":values[0] if stable else None,
        "count_range":[min(values),max(values)],
        "original_boxes":baseline[:40]
    }

def control_suite():
    rows={}
    for typ in ("dashes","speckles"):
        for name,(x0,y0,x1,y1) in ROIS.items():
            image=synthetic((y1-y0,x1-x0),typ)
            rows[f"{typ}:{name}"]=analyze(image)
    failures=[]
    for key,r in rows.items():
        typ=key.split(":")[0]
        expected=3 if typ=="dashes" else 0
        if not (r["stable"] and r["stable_count"]==expected):
            failures.append({"control":key,"expected":expected,
                             "stable":r["stable"],"count_range":r["count_range"]})
    return {"pass":not failures,"cases":len(rows)*len(FORMATS)*len(THRESHOLDS)*2,
            "failures":failures,"results":{k:{
                "stable":v["stable"],"count_range":v["count_range"]
            } for k,v in rows.items()}}

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=SHA:raise SystemExit("Wrong canonical PNG")
    im=np.asarray(Image.open(PNG).convert("L"))
    if im.shape!=(1105,1600):raise SystemExit("Image dimensions changed")
    controls=control_suite()
    real={}
    for name,(x0,y0,x1,y1) in ROIS.items():
        real[name]={"roi":[x0,y0,x1,y1],
                     **analyze(im[y0:y1,x0:x1])}
    stable=[r["stable_count"] for r in real.values() if r["stable"]]
    positive=sum(int(x>0) for x in stable)
    promotable=(len(stable)>=MIN_STABLE_REGIONS
                and positive>=MIN_POSITIVE_REGIONS)
    decision=("CONTROL_FAILURE" if not controls["pass"] else
              "STABLE_SKY_MARK_CANDIDATE" if promotable else
              "NO_REPLICATED_ISOLATED_SKY_MARK_PATTERN")
    result={
        "experiment_id":"A11-EXP-131",
        "date":"2026-10-13",
        "hypothesis":"isolated ink marks in untouched sky might be intentional repeatable dashes rather than scanning speckles",
        "evidence":"Visible sky contains a few isolated pencil flecks outside the main buildings and boats; Stage12 counted components only in the top 0..48 full-width strip.",
        "scope":"four fixed blank sky ROIs below y=48 and outside buildings; two object-measurement algorithms x three thresholds x four re-encodings",
        "canonical_sha256":digest,
        "rois":ROIS,
        "criteria":{"min_area":MIN_AREA,"max_area":MAX_AREA,
                    "min_major":MIN_MAJOR,"min_minor":MIN_MINOR,
                    "min_border":MIN_BORDER,
                    "min_stable_regions":MIN_STABLE_REGIONS,
                    "min_positive_regions":MIN_POSITIVE_REGIONS,
                    "match_tolerance_px":3},
        "controls":controls,
        "real":real,
        "stable_region_count":len(stable),
        "positive_region_count":positive,
        "promoted":bool(controls["pass"] and promotable),
        "decision":decision,
        "coverage_guard":"Only isolated marks of 12-250 pixels within these sky windows. No broader negative for other markings or text; a count of sky flecks is not by itself a secret.",
        "safety":"Pure canonical image diagnostics. No key, seed phrase, BIP39, wallet or social-source operations."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    rows=["# Stage 131 — isolated sky mark consistency","",
        f"- Canonical image SHA verified: **{digest==SHA}**",
        f"- Dashes-vs-speckles controls: **{controls['pass']}** ({controls['cases']} readings)",
        f"- Stable real regions: **{len(stable)}/4**",
        f"- Stable nonzero-mark regions: **{positive}/4**",
        f"- Decision: **{decision}**","",
        "| sky region | observed counts min/max | stable |",
        "|---|---:|:---:|"]
    for name,r in real.items():
        rows.append(f"| {name} | {r['count_range']} | {r['stable_count'] if r['stable'] else '?'} |")
    rows+=["","## Interpretation","",
           "A visible structure must pass calibration and lossy/source-location consistency to qualify as an independently reviewable clue.",
           "No private keys, words, addresses or wallet access.",""]
    (OUT/"REPORT.md").write_text("\n".join(rows))
    # Human-auditable source ROIs, no arbitrary enhancements or OCR.
    sheet=Image.new("RGB",(760,400),"white")
    draw=ImageDraw.Draw(sheet)
    for i,(name,(x0,y0,x1,y1)) in enumerate(ROIS.items()):
        roi=Image.fromarray(im[y0:y1,x0:x1]).convert("RGB")
        roi.thumbnail((340,155))
        x=10+(i%2)*380;y=10+(i//2)*195
        draw.text((x,y),name+" "+str(real[name]["count_range"]),fill=(0,0,0))
        sheet.paste(roi,(x,y+25))
    sheet.save(OUT/"sky-roi-contact.png")
    print(json.dumps({"stage":131,"controls_pass":controls["pass"],
        "stable_regions":len(stable),"positive_regions":positive,
        "decision":decision}))

if __name__=="__main__":
    main()
