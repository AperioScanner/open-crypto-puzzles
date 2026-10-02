#!/usr/bin/env python3
"""Stage 15: pre-registered semantic-region 3-2-1 count test.

Non-cryptographic experiment. Uses the same semantically defined regions, thresholds,
and component-size bands as Stage 12. It asks whether any *independent* region has a
stable visible-component signature equal to 3-2-1 (or its reverse 1-2-3) without
introducing new thresholds or candidate-key logic after seeing the result.
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage15-semantic-321-counts"
OUT.mkdir(parents=True,exist_ok=True)

THRESHOLDS=(80,110,140,170,200)
TARGETS={(3,2,1):"321",(1,2,3):"123"}

def clamp(box,w,h):
    x0,y0,x1,y1=map(int,box)
    x0=max(0,min(w-2,x0)); x1=max(x0+2,min(w,x1))
    y0=max(0,min(h-2,y0)); y1=max(y0+2,min(h,y1))
    return x0,y0,x1,y1

def inner_building(b,frac=0.08):
    x0,x1,y0,y1=b["x0"],b["x1"],b["roof_y"],b["bottom_y"]
    mx=max(3,int((x1-x0)*frac)); my=max(4,int((y1-y0)*frac))
    return (x0+mx,y0+my,x1-mx,y1-my)

def band_counts(crop,thr):
    mask=(crop<thr).astype(np.uint8)
    n,_,stats,_=cv2.connectedComponentsWithStats(mask,8)
    areas=stats[1:,cv2.CC_STAT_AREA].astype(int).tolist() if n>1 else []
    return (
        sum(3<=a<=200 for a in areas),
        sum(201<=a<=2000 for a in areas),
        sum(a>2000 for a in areas),
    )

def score_series(series,target):
    arr=np.array(series,dtype=int)
    tgt=np.array(target,dtype=int)
    exact=[tuple(x)==target for x in arr]
    l1=np.abs(arr-tgt).sum(axis=1)
    med=tuple(np.median(arr,axis=0).astype(int))
    mad=tuple(np.median(np.abs(arr-np.median(arr,axis=0)),axis=0))
    return {
        "target":"".join(map(str,target)),
        "exact_thresholds":int(sum(exact)),
        "exact_fraction":float(np.mean(exact)),
        "median_counts":list(med),
        "mad_counts":[float(x) for x in mad],
        "mean_l1_distance":float(np.mean(l1)),
        "min_l1_distance":int(np.min(l1)),
    }

def main():
    geom=json.loads(GEOM.read_text())
    img=cv2.imread(str(SOURCE),cv2.IMREAD_UNCHANGED)
    if img is None: raise SystemExit("image load failed")
    gray=img[:,:,0] if img.ndim==3 else img
    h,w=gray.shape

    rois=[]
    for b in geom["buildings"]:
        rois.append((f"building_{b['id']:02d}",inner_building(b)))
    s=geom["large_sailboat"]
    rois.append(("large_sailboat",(s["x0"],s["y0"],s["x1"],s["y1"])))
    y0,y1=geom["small_sails_band_y"]
    rois.append(("small_sails_full_band",(0,y0,w,y1)))
    rois.append(("first_row_visual_strip",(0,0,w,48)))
    rois.append(("skyline_full_band",(200,0,w,340)))

    rows=[]
    for name,box in rois:
        x0,y0,x1,y1=clamp(box,w,h)
        crop=gray[y0:y1,x0:x1]
        series=[band_counts(crop,t) for t in THRESHOLDS]
        scores=[score_series(series,t) for t in TARGETS]
        best=min(scores,key=lambda x:(-x["exact_thresholds"],x["mean_l1_distance"]))
        rows.append({
            "region":name,
            "bbox":[x0,y0,x1,y1],
            "counts_by_threshold":[{"threshold":t,"small_mid_large":list(c)} for t,c in zip(THRESHOLDS,series)],
            "target_scores":scores,
            "best_target":best,
        })

    # Pre-registered promotion rule: >=4/5 exact thresholds in one semantic region.
    promoted=[]
    for r in rows:
        for s in r["target_scores"]:
            if s["exact_thresholds"]>=4:
                promoted.append({"region":r["region"],**s})

    # Secondary descriptive check only: exact match at any one threshold, not promoted.
    incidental=[]
    for r in rows:
        for entry in r["counts_by_threshold"]:
            tup=tuple(entry["small_mid_large"])
            if tup in TARGETS:
                incidental.append({
                    "region":r["region"],
                    "threshold":entry["threshold"],
                    "pattern":TARGETS[tup],
                    "counts":list(tup),
                })

    ranked=sorted(rows,key=lambda r:(-r["best_target"]["exact_thresholds"],r["best_target"]["mean_l1_distance"],r["region"]))

    result={
        "experiment_id":"A11-EXP-015",
        "scope":"same semantic ROIs, thresholds and size bands as Stage 12; tests stable 3-2-1 or 1-2-3 component-count signatures only; no private-key operations",
        "thresholds":list(THRESHOLDS),
        "component_bands_px":{"small":[3,200],"medium":[201,2000],"large":[2001,None]},
        "promotion_rule":">=4 of 5 thresholds exactly equal 3,2,1 or 1,2,3 in a single pre-defined semantic region",
        "promoted":promoted,
        "incidental_single_threshold_matches":incidental,
        "regions":rows,
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 15 — semantic-region 3-2-1 count test","",
        "**Experiment:** A11-EXP-015","",
        "This is a pre-registered, non-cryptographic follow-up to Stage 12. It reuses the same semantic regions, five thresholds, and three connected-component area bands. No new threshold or band was selected after observing the result.","",
        f"- Promotion rule: {result['promotion_rule']}",
        f"- Promoted independent 321/123 signatures: **{len(promoted)}**",
        f"- Incidental one-threshold exact matches (descriptive only): **{len(incidental)}**",
        "",
        "## Closest regions","",
        "| region | best target | exact thresholds | mean L1 distance | median small/mid/large |",
        "|:---|:---:|---:|---:|:---:|",
    ]
    for r in ranked[:10]:
        b=r["best_target"]
        md.append(f"| {r['region']} | {b['target']} | {b['exact_thresholds']}/5 | {b['mean_l1_distance']:.2f} | {tuple(b['median_counts'])} |")
    md += ["","## Incidental exact matches",""]
    if incidental:
        for x in incidental:
            md.append(f"- {x['region']} at threshold {x['threshold']}: {x['pattern']} ({x['counts']})")
    else:
        md.append("- None.")
    md += ["","## Interpretation",""]
    if promoted:
        md.append("At least one pre-defined semantic region independently reproduces a stable 3-2-1/1-2-3 component-count signature. This deserves direct visual inspection and crop-robustness replication before treating it as corroboration.")
    else:
        md.append("No pre-defined semantic region independently reproduces a stable 3-2-1/1-2-3 component-count signature under the Stage 12 measurement scheme. This weakens the simplest '321 is repeated as object counts' hypothesis and prevents cherry-picking isolated thresholds.")
    md += ["","This result does not test the meaning of the skyline 0x321 marker; it only tests one independent count-based corroboration route.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-015","promoted":len(promoted),"incidental":len(incidental),"top":[(r["region"],r["best_target"]["target"],r["best_target"]["exact_thresholds"],round(r["best_target"]["mean_l1_distance"],2)) for r in ranked[:5]]}))

if __name__=="__main__":
    main()
