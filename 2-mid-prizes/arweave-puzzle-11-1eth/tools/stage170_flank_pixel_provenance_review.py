#!/usr/bin/env python3
"""A11-EXP-170: original-source pixel provenance for Stage169 mixed flank results.

No new source detector, crop optimization or decoding. Replay Stage169
inside/outside scores exactly, preserve raw grayscale crops byte-for-byte,
and show source vs guide/sample-point copies in separate panels so that
a human can inspect interior hatching/adjacent boat contamination.
Controls preregistered in analysis/STAGE_QUEUE.md.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

from stage153_under_pier_triangle_junctions import TRIANGLES
from stage169_sail_outer_flank_contrast import (
    SOURCE_SITES,T_SAMPLES,FLANK_OFFSETS,compare_two)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR169=ROOT/"analysis"/"runs"/"stage169-sail-outer-flank-contrast"/"result.json"
PRIOR168=ROOT/"analysis"/"runs"/"stage168-sail-foot-review"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage170-flank-pixel-provenance"
OUT.mkdir(parents=True,exist_ok=True)
RAW=OUT/"unaltered_source_crops"
RAW.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FMT="original"
CROP_T0=.65
PAD=25
ZOOM=3
TILE=398
TILE_H=330
HEAD=37
CANVAS_BG=247

def key(site,index):
    return site+("_left" if index==1 else "_right")

def source_bounds(apex,foot,dx,shape):
    ax,ay=apex
    fx,fy=foot
    sample=[
        (ax+CROP_T0*(fx-ax),ay+CROP_T0*(fy-ay)),
        (ax+CROP_T0*(fx+dx-ax),ay+CROP_T0*(fy-ay)),
        (fx,fy),(fx+dx,fy)]
    xmin=min(x for x,y in sample)-max(FLANK_OFFSETS)-PAD
    xmax=max(x for x,y in sample)+max(FLANK_OFFSETS)+PAD
    ymin=min(y for x,y in sample)-PAD
    ymax=max(y for x,y in sample)+PAD
    return (max(0,int(np.floor(xmin))),
            max(0,int(np.floor(ymin))),
            min(shape[1],int(np.ceil(xmax))+1),
            min(shape[0],int(np.ceil(ymax))+1))

def overlay(crop,box,apex,foot,dx,sign):
    result=cv2.cvtColor(crop,cv2.COLOR_GRAY2BGR)
    xa,ya=apex;xf,yf=foot
    x0,y0,_,_=box
    def p(t,shift):
        return (int(round(xa+t*(xf+shift-xa)))-x0,
                int(round(ya+t*(yf-ya)))-y0)
    cv2.line(result,p(float(T_SAMPLES[0]),dx),
             p(float(T_SAMPLES[-1]),dx),(30,150,225),1,cv2.LINE_AA)
    for t in T_SAMPLES:
        x,y=p(float(t),dx)
        for k in FLANK_OFFSETS:
            # Colors annotate every original Stage169 sample pixel.
            cv2.circle(result,(x-sign*k,y),0,(185,65,10),-1)
            cv2.circle(result,(x+sign*k,y),0,(0,20,245),-1)
        cv2.circle(result,(x,y),0,(0,210,210),-1)
    cv2.drawMarker(result,(xf+dx-x0,yf-y0),
       (100,20,200),cv2.MARKER_CROSS,7,1)
    return result

def tile(image,title):
    arr=(cv2.cvtColor(image,cv2.COLOR_GRAY2BGR) if image.ndim==2
         else image)
    h,w=arr.shape[:2]
    enlarged=cv2.resize(arr,(w*ZOOM,h*ZOOM),interpolation=cv2.INTER_NEAREST)
    max_w=TILE-12;max_h=TILE_H-HEAD-10
    factor=min(1.0,max_w/enlarged.shape[1],max_h/enlarged.shape[0])
    if factor<1:
        enlarged=cv2.resize(enlarged,(max(1,int(enlarged.shape[1]*factor)),
            max(1,int(enlarged.shape[0]*factor))),interpolation=cv2.INTER_NEAREST)
    surface=np.full((TILE_H,TILE,3),CANVAS_BG,np.uint8)
    cv2.putText(surface,title,(7,23),
                cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1,cv2.LINE_AA)
    hh,ww=enlarged.shape[:2]
    x=(TILE-ww)//2
    y=HEAD+max(0,(TILE_H-HEAD-hh)//2)
    surface[y:y+hh,x:x+ww]=enlarged
    return surface

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    j169=json.loads(PRIOR169.read_text())
    j168=json.loads(PRIOR168.read_text())
    fixed=[("sail2",2,-8),("sail3",1,8),("sail4",2,-8),("sail5",2,-8)]
    checks={
        "canonical_sha":digest==SHA==j169["canonical_source_sha256"],
        "Stage169_calibration_128":
            j169["synthetic_source_independent_controls"]["pass"]
            and j169["synthetic_source_independent_controls"]["passed"]==128,
        "Stage169_predecessor_guards":all(
            j169["predecessor_and_fixed_site_guards"].values()),
        "Stage169_mixed_scientific_decision":
            j169["decision"]=="INSUFFICIENT_SOURCE_FLANK_CONTRAST",
        "Stage168_contact_provenance":
            j168["decision"]=="CONTACT_SHEET_READY_FOR_MANUAL_SOURCE_REVIEW"
            and j168["controls_passed"]==j168["controls_total"]==12,
        "unchanged_four_sites":list(SOURCE_SITES)==fixed,
    }
    img=np.asarray(Image.open(SOURCE).convert("L"))
    if img.shape!=(1105,1600):raise RuntimeError("Original dimensions changed")
    sheet=np.full((len(fixed)*TILE_H,3*TILE,3),CANVAS_BG,np.uint8)
    records=[]
    for rank,(site,index,dx) in enumerate(fixed):
        k=key(site,index)
        apex,foot=TRIANGLES[site][0],TRIANGLES[site][index]
        sign=1 if index==2 else -1
        now=compare_two(img,apex,foot,dx,sign)
        old=j169["real_by_source_variant"]["original"][k]
        same=(now["selected_dx"]==old["selected_dx"]
              and now["confident"]==old["confident"]
              and all(abs(now["original_dx0"][q]-old["original_dx0"][q])<=1e-6
                     for q in ("inside","outside","contrast"))
              and all(abs(now["inward_candidate_dx"+str(dx)][q]-
                          old["inward_candidate_dx"+str(dx)][q])<=1e-6
                      for q in ("inside","outside","contrast")))
        checks["score_exact_replay_"+k]=bool(same)
        bbox=source_bounds(apex,foot,dx,img.shape)
        x0,y0,x1,y1=bbox
        crop=img[y0:y1,x0:x1].copy()
        if crop.size==0:raise RuntimeError("Bad fixed crop")
        raw_file=RAW/(k+".png")
        if not cv2.imwrite(str(raw_file),crop):
            raise RuntimeError("Could not write raw source PNG")
        reread=cv2.imread(str(raw_file),cv2.IMREAD_GRAYSCALE)
        exact=np.array_equal(crop,reread) and np.array_equal(crop,img[y0:y1,x0:x1])
        checks["pixel_exact_readback_"+k]=bool(exact)
        guides=(tile(crop,k+" RAW original"),
                tile(overlay(crop,bbox,apex,foot,0,sign),k+" original x0"),
                tile(overlay(crop,bbox,apex,foot,dx,sign),k+f" inward {dx:+d}"))
        for col,part in enumerate(guides):
            sheet[rank*TILE_H:(rank+1)*TILE_H,col*TILE:(col+1)*TILE]=part
        records.append({"site":k,"raw_bbox_xyxy":bbox,
           "apex":apex,"original_foot":foot,"inward_dx":dx,
           "raw_pixel_sha256":hashlib.sha256(crop.tobytes()).hexdigest(),
           "raw_pixel_exact":bool(exact),
           "replayed_original_contrast":now["original_dx0"]["contrast"],
           "replayed_inward_contrast":now["inward_candidate_dx"+str(dx)]["contrast"],
           "replayed_original_outside_dark":now["original_dx0"]["outside"],
           "replayed_inward_outside_dark":now["inward_candidate_dx"+str(dx)]["outside"]})
    checks["contact_saved"]=bool(cv2.imwrite(str(OUT/"stage169-flank-raw-vs-sampling-guides.png"),sheet))
    decision=("CONTACT_SHEET_READY_FOR_CRITICAL_VISUAL_REVIEW"
            if all(checks.values()) else "CONTROL_FAILURE")
    result={"experiment_id":"A11-EXP-170",
      "original_sha256":digest,
      "scope":"Readback verification of fixed Stage169 original-source flank pixels and guide-overlay provenance; NO new hypothesis or classifier.",
      "checks":checks,"checks_passed":sum(checks.values()),
      "checks_total":len(checks),
      "raw_crop_and_flank_score_replays":records,
      "guide_color_legend":"Yellow=ray pixels; blue=interior darkness samples; red=exterior whiteness samples. Guides appear ONLY in separate copies, not raw original.",
      "visual_review_pending":True,
      "decision":decision,
      "interpretation_guard":"This validates original pixel provenance and the exact Stage169 scorer, not the objective accuracy of any selected outer sail vertex. Nearby hatches/boat hull/rigging can contaminate scored exterior flank.",
      "safety":"No mnemonic, key, wallet, address comparison, external/social search or OCR."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage170 — direct raw pixel check of Stage169 sail-flank contrast","",
      f"- Canonical SHA: **{digest==SHA}**",
      f"- Structural and 4/4 score/pixel raw replay guards: **{sum(checks.values())}/{len(checks)}**",
      f"- Decision: **{decision}**","",
      "Each 3-panel row: UNALTERED RAW grayscale original, original x0 sampled ray, previous fixed inward ray. Yellow points=ray, blue=inside, red=outside; these markers are NOT drawn by the puzzle author.","",
      "| Site | original contrast | inward contrast | original outside dark | inward outside dark |",
      "|---|---:|---:|---:|---:|"]
    for rec in records:
        lines.append(f"| {rec['site']} | {rec['replayed_original_contrast']:.3f} | {rec['replayed_inward_contrast']:.3f} | {rec['replayed_original_outside_dark']:.3f} | {rec['replayed_inward_outside_dark']:.3f} |")
    lines+=["","Human-readable image stage169-flank-raw-vs-sampling-guides.png is a PROVENANCE aid only. Subjective analysis cannot independently certify the outer contour. No source endpoint or Stage165 width/p-value has been modified.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":170,"checks":f"{sum(checks.values())}/{len(checks)}",
         "decision":decision}))
if __name__=="__main__":main()
