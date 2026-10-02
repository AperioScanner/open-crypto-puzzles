#!/usr/bin/env python3
"""Stage 12: counting/perimeter diagnostics for secondary visual details.

Motivated by the author's solved-puzzle grammar: small-detail counting, perimeter,
visual context, and secondary marks. Non-cryptographic only.
"""
from __future__ import annotations
import json
from pathlib import Path

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage12-count-perimeter"
OUT.mkdir(parents=True,exist_ok=True)

THRESHOLDS=(80,110,140,170,200)

def clamp(box,w,h):
    x0,y0,x1,y1=map(int,box)
    x0=max(0,min(w-2,x0)); x1=max(x0+2,min(w,x1))
    y0=max(0,min(h-2,y0)); y1=max(y0+2,min(h,y1))
    return x0,y0,x1,y1

def comp_stats(crop,thr):
    mask=(crop<thr).astype(np.uint8)
    n,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
    areas=stats[1:,cv2.CC_STAT_AREA].astype(int).tolist() if n>1 else []
    return {
        "ink_pixels":int(mask.sum()),
        "components_total":len(areas),
        "components_3_200":sum(3<=a<=200 for a in areas),
        "components_201_2000":sum(201<=a<=2000 for a in areas),
        "components_gt2000":sum(a>2000 for a in areas),
        "largest_areas":sorted(areas,reverse=True)[:12],
    }

def perimeter_fraction(crop,thr,width):
    mask=(crop<thr)
    h,w=mask.shape
    width=max(1,min(width,h//2,w//2))
    ring=np.zeros_like(mask,dtype=bool)
    ring[:width,:]=1; ring[-width:,:]=1; ring[:,:width]=1; ring[:,-width:]=1
    denom=int(ring.sum())
    return float(mask[ring].sum()/denom) if denom else 0.0

def projection_periodicity(crop,thr):
    mask=(crop<thr).astype(np.float64)
    out={}
    for axis,name in ((0,"x"),(1,"y")):
        p=mask.sum(axis=axis)
        if len(p)<8 or np.std(p)<1e-9:
            out[name]={"best_lag":None,"score":0.0}
            continue
        q=(p-p.mean())/(p.std()+1e-12)
        ac=np.correlate(q,q,mode="full")[len(q)-1:]
        ac=ac/(np.arange(len(q),0,-1))
        lo=3; hi=min(len(ac),max(8,len(q)//2))
        if hi<=lo:
            out[name]={"best_lag":None,"score":0.0}
            continue
        idx=int(np.argmax(ac[lo:hi]))+lo
        out[name]={"best_lag":idx,"score":float(ac[idx])}
    return out

def inner_building(b,frac=0.08):
    x0,x1,y0,y1=b["x0"],b["x1"],b["roof_y"],b["bottom_y"]
    mx=max(3,int((x1-x0)*frac)); my=max(4,int((y1-y0)*frac))
    return (x0+mx,y0+my,x1-mx,y1-my)

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

    results=[]
    contact=[]
    for name,box in rois:
        x0,y0,x1,y1=clamp(box,w,h)
        crop=gray[y0:y1,x0:x1]
        by_thr={str(t):comp_stats(crop,t) for t in THRESHOLDS}
        small_counts=[by_thr[str(t)]["components_3_200"] for t in THRESHOLDS]
        mid_counts=[by_thr[str(t)]["components_201_2000"] for t in THRESHOLDS]
        row={
            "name":name,
            "bbox":[x0,y0,x1,y1],
            "shape":[x1-x0,y1-y0],
            "thresholds":by_thr,
            "stable_small_component_median":float(np.median(small_counts)),
            "stable_small_component_mad":float(np.median(np.abs(np.array(small_counts)-np.median(small_counts)))),
            "stable_mid_component_median":float(np.median(mid_counts)),
            "stable_mid_component_mad":float(np.median(np.abs(np.array(mid_counts)-np.median(mid_counts)))),
            "perimeter_fraction_t140":{"w1":perimeter_fraction(crop,140,1),"w2":perimeter_fraction(crop,140,2),"w4":perimeter_fraction(crop,140,4)},
            "projection_periodicity_t140":projection_periodicity(crop,140),
        }
        results.append(row)

        # Diagnostic crop: threshold 140 with connected-component boxes for components 3..200 px.
        mask=((crop<140)*255).astype(np.uint8)
        vis=cv2.cvtColor(255-mask,cv2.COLOR_GRAY2BGR)
        n,lab,stats,_=cv2.connectedComponentsWithStats((crop<140).astype(np.uint8),8)
        for i in range(1,n):
            area=int(stats[i,cv2.CC_STAT_AREA])
            if 3<=area<=200:
                xx=int(stats[i,cv2.CC_STAT_LEFT]); yy=int(stats[i,cv2.CC_STAT_TOP])
                ww=int(stats[i,cv2.CC_STAT_WIDTH]); hh=int(stats[i,cv2.CC_STAT_HEIGHT])
                cv2.rectangle(vis,(xx,yy),(xx+ww,yy+hh),(0,0,255),1)
        scale=min(1.0,320/max(1,vis.shape[1]))
        if scale<1.0:
            vis=cv2.resize(vis,(max(1,int(vis.shape[1]*scale)),max(1,int(vis.shape[0]*scale))),interpolation=cv2.INTER_AREA)
        contact.append((name,vis))

    # Rank bounded anomalies that may merit human visual inspection.
    ranked_small=sorted(results,key=lambda r:(r["stable_small_component_mad"],-r["stable_small_component_median"]))[:8]
    ranked_perim=sorted(results,key=lambda r:-r["perimeter_fraction_t140"]["w2"])[:8]
    ranked_period=[]
    for r in results:
        best=max(r["projection_periodicity_t140"]["x"]["score"],r["projection_periodicity_t140"]["y"]["score"])
        ranked_period.append((best,r))
    ranked_period.sort(key=lambda z:-z[0])

    # Build a contact sheet.
    tile_w=360; tile_h=260
    rows=(len(contact)+3)//4
    sheet=np.full((rows*tile_h,4*tile_w,3),255,np.uint8)
    for i,(name,vis) in enumerate(contact):
        rr=i//4; cc=i%4
        y=rr*tile_h; x=cc*tile_w
        hh=min(vis.shape[0],tile_h-30); ww=min(vis.shape[1],tile_w)
        sheet[y:y+hh,x:x+ww]=vis[:hh,:ww]
        cv2.putText(sheet,name,(x+5,y+tile_h-8),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,0,0),1,cv2.LINE_AA)
    cv2.imwrite(str(OUT/"secondary-detail-contact-sheet.png"),sheet)

    result={
        "experiment_id":"A11-EXP-012",
        "scope":"visual counting, perimeter and projection diagnostics only; no secret reconstruction or wallet verification",
        "thresholds":list(THRESHOLDS),
        "regions":results,
        "top_stable_small_component_regions":[{"name":r["name"],"median":r["stable_small_component_median"],"mad":r["stable_small_component_mad"]} for r in ranked_small],
        "top_perimeter_regions":[{"name":r["name"],"fraction":r["perimeter_fraction_t140"]["w2"]} for r in ranked_perim],
        "top_periodic_regions":[{"name":r["name"],"score":float(s),"periodicity":r["projection_periodicity_t140"]} for s,r in ranked_period[:8]],
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 12 — counting and perimeter diagnostics","",
        "**Experiment:** A11-EXP-012","",
        "Motivation: solved siblings use small-detail counting, secondary marks, perimeter, and overall visual context. This stage inventories those feature classes in Puzzle #11 without generating or checking any private-key material.","",
        "## Stable small-component counts","",
        "| region | median components (3–200 px) | MAD across thresholds |",
        "|:---|---:|---:|",
    ]
    for r in ranked_small:
        md.append(f"| {r['name']} | {r['stable_small_component_median']:.1f} | {r['stable_small_component_mad']:.1f} |")
    md += ["","## Highest perimeter ink fractions at threshold 140","",
           "| region | 2px perimeter ink fraction |","|:---|---:|"]
    for r in ranked_perim:
        md.append(f"| {r['name']} | {r['perimeter_fraction_t140']['w2']:.4f} |")
    md += ["","## Strongest projection periodicities at threshold 140","",
           "| region | score | x best lag | y best lag |","|:---|---:|---:|---:|"]
    for s,r in ranked_period[:8]:
        px=r["projection_periodicity_t140"]["x"]["best_lag"]
        py=r["projection_periodicity_t140"]["y"]["best_lag"]
        md.append(f"| {r['name']} | {s:.4f} | {px} | {py} |")
    md += [
        "","## Interpretation","",
        "This run is a census, not a solve. Regions with stable small-component counts, unusually strong perimeter occupancy, or strong 1-D periodicity are promoted for visual inspection in the next stage. Any apparent 3/2/1 count is only interesting if it is stable across thresholds and visually corresponds to deliberate marks.",
        "","Diagnostic image: secondary-detail-contact-sheet.png",
        ""
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-012","regions":len(results),"top_small":result["top_stable_small_component_regions"][:3],"top_perimeter":result["top_perimeter_regions"][:3],"top_periodic":result["top_periodic_regions"][:3]}))

if __name__=="__main__":
    main()
