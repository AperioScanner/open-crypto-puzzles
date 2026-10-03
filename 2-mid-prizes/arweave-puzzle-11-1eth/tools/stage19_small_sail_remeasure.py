#!/usr/bin/env python3
"""Stage 19: independently re-measure the five small-sail widths.

Non-cryptographic. Two bounded segmentation families are used across fixed grayscale
thresholds: connected components and vertical-projection runs. The large sailboat
region is excluded using its already-measured bbox. No private-key operations.
"""
from __future__ import annotations
import json
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage19-small-sail-remeasure"
OUT.mkdir(parents=True,exist_ok=True)

THRESHOLDS=(70,85,100,110,120,135,150,165,180)
PRIOR=[27,53,79,83,51]

def cluster_tracks(observations, x_tol=18):
    # observations: list of dicts with threshold,x0,x1,width,center
    obs=sorted(observations,key=lambda z:z["center"])
    clusters=[]
    for o in obs:
        best=None; bestd=None
        for c in clusters:
            d=abs(o["center"]-c["center_median"])
            if d<=x_tol and (bestd is None or d<bestd):
                best=c; bestd=d
        if best is None:
            best={"items":[],"center_median":o["center"]}
            clusters.append(best)
        best["items"].append(o)
        best["center_median"]=float(np.median([x["center"] for x in best["items"]]))
    out=[]
    for c in clusters:
        by_thr={}
        for o in c["items"]:
            t=str(o["threshold"])
            # keep widest candidate if same threshold lands in cluster
            if t not in by_thr or o["width"]>by_thr[t]["width"]:
                by_thr[t]=o
        vals=list(by_thr.values())
        widths=[x["width"] for x in vals]
        centers=[x["center"] for x in vals]
        out.append({
            "threshold_support":len(vals),
            "support_fraction":len(vals)/len(THRESHOLDS),
            "center_median":float(np.median(centers)) if centers else None,
            "width_median":float(np.median(widths)) if widths else None,
            "width_mad":float(np.median(np.abs(np.array(widths)-np.median(widths)))) if widths else None,
            "items":vals,
        })
    return sorted(out,key=lambda z:z["center_median"])

def component_candidates(gray,y0,y1,xmin,thr):
    crop=gray[y0:y1,xmin:]
    mask=(crop<thr).astype(np.uint8)
    kernel=np.ones((3,3),np.uint8)
    closed=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel,iterations=1)
    n,_,stats,_=cv2.connectedComponentsWithStats(closed,8)
    out=[]
    for i in range(1,n):
        x=int(stats[i,cv2.CC_STAT_LEFT])+xmin
        y=int(stats[i,cv2.CC_STAT_TOP])+y0
        w=int(stats[i,cv2.CC_STAT_WIDTH]); h=int(stats[i,cv2.CC_STAT_HEIGHT])
        area=int(stats[i,cv2.CC_STAT_AREA])
        if not (15<=w<=120 and 18<=h<=120 and 60<=area<=6000):
            continue
        extent=area/(w*h)
        if not (0.04<=extent<=0.80):
            continue
        out.append({"threshold":int(thr),"x0":x,"x1":x+w-1,"width":w,"height":h,"area":area,"center":x+(w-1)/2})
    return out

def projection_candidates(gray,y0,y1,xmin,thr):
    crop=gray[y0:y1,xmin:]
    mask=(crop<thr)
    col=mask.sum(axis=0)
    active=col>=3
    # close column gaps of up to 2 pixels
    a=active.astype(np.uint8)[None,:]
    a=cv2.morphologyEx(a,cv2.MORPH_CLOSE,np.ones((1,3),np.uint8),iterations=1)[0].astype(bool)
    out=[]; start=None
    for i,v in enumerate(list(a)+[False]):
        if v and start is None:
            start=i
        elif not v and start is not None:
            end=i-1; w=end-start+1
            if 15<=w<=120:
                x0=xmin+start; x1=xmin+end
                out.append({"threshold":int(thr),"x0":x0,"x1":x1,"width":int(w),"center":(x0+x1)/2})
            start=None
    return out

def select_stable(tracks):
    return [t for t in tracks if t["threshold_support"]>=6 and t["width_mad"]<=6]

def summarize_method(name,observations):
    tracks=cluster_tracks(observations)
    stable=select_stable(tracks)
    widths=[int(round(t["width_median"])) for t in stable]
    centers=[round(t["center_median"],1) for t in stable]
    first3=None
    if len(widths)>=3:
        first3={
            "widths":widths[:3],
            "differences":[widths[1]-widths[0],widths[2]-widths[1]],
            "ap_error":abs((widths[1]-widths[0])-(widths[2]-widths[1])),
        }
    return {"method":name,"observations":len(observations),"tracks":tracks,"stable_tracks":stable,"stable_widths_left_to_right":widths,"stable_centers_left_to_right":centers,"first3":first3}

def compare_prior(widths):
    if len(widths)!=5: return {"comparable":False}
    diffs=[int(a-b) for a,b in zip(widths,PRIOR)]
    return {"comparable":True,"prior":PRIOR,"remeasured":widths,"signed_differences":diffs,"max_abs_difference":max(abs(x) for x in diffs)}

def main():
    g=json.loads(GEOM.read_text())
    img=cv2.imread(str(SOURCE),cv2.IMREAD_UNCHANGED)
    if img is None: raise SystemExit("image load failed")
    gray=img[:,:,0] if img.ndim==3 else img
    y0,y1=map(int,g["small_sails_band_y"])
    xmin=int(g["large_sailboat"]["x1"])+8

    comp=[]; proj=[]
    for t in THRESHOLDS:
        comp.extend(component_candidates(gray,y0,y1,xmin,t))
        proj.extend(projection_candidates(gray,y0,y1,xmin,t))
    A=summarize_method("connected_components_close3",comp)
    B=summarize_method("vertical_projection_runs",proj)
    A["prior_comparison"]=compare_prior(A["stable_widths_left_to_right"])
    B["prior_comparison"]=compare_prior(B["stable_widths_left_to_right"])

    def ap26(s):
        f=s.get("first3")
        return bool(f and len(f["differences"])==2 and max(abs(d-26) for d in f["differences"])<=3)

    robust_ap26=ap26(A) and ap26(B)
    result={
        "experiment_id":"A11-EXP-019",
        "scope":"small-sail band remeasurement across fixed thresholds with two independent segmentation families; no private-key operations",
        "thresholds":list(THRESHOLDS),
        "band_y":[y0,y1],
        "excluded_x_below":xmin,
        "prior_widths":PRIOR,
        "methods":[A,B],
        "both_methods_support_first3_step26_within_3px":robust_ap26,
        "promotion_rule":"both segmentation families must yield >=3 stable left-to-right tracks whose first two width differences are each within 3 px of +26; stronger prior-width confirmation additionally requires exactly five stable tracks per method",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=["# Stage 19 — independent small-sail remeasurement","",
        "**Experiment:** A11-EXP-019","",
        f"Fixed band y={y0}..{y1}; x<{xmin} excluded because it belongs to the already-measured large sailboat.",
        f"Thresholds: {list(THRESHOLDS)}.",
        f"Prior Stage-18 widths: {PRIOR}.",""]
    for s in (A,B):
        md += [f"## {s['method']}","",
               f"- Stable tracks: **{len(s['stable_tracks'])}**",
               f"- Stable centers left→right: {s['stable_centers_left_to_right']}",
               f"- Stable widths left→right: {s['stable_widths_left_to_right']}",
               f"- First-three diagnostic: {s['first3']}",
               f"- Prior comparison: {s['prior_comparison']}",""]
    md += ["## Pre-registered decision","",
           f"- Both independent methods support +26,+26 within ±3 px: **{robust_ap26}**","",
           "## Interpretation",""]
    if robust_ap26:
        md.append("The Stage-18 +26,+26 progression survives two independent segmentation families and multiple thresholds, so it is promoted as a robust visual measurement lead. Semantic interpretation still remains open.")
    else:
        md.append("The Stage-18 +26,+26 progression does not replicate across both independent segmentation families. It is therefore downgraded as a likely measurement/segmentation artifact rather than an author clue.")
    md += ["","No alphabet/modulo interpretation is inferred by this experiment.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-019","component_widths":A["stable_widths_left_to_right"],"projection_widths":B["stable_widths_left_to_right"],"robust_ap26":robust_ap26}))

if __name__=="__main__": main()
