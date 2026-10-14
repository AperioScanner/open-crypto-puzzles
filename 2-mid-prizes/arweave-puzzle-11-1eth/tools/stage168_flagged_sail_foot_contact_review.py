#!/usr/bin/env python3
"""Stage168: fixed source-only diagnostic contact review of Stage167 flagged feet.

Four PREDECLARED sites only: 3 stable nonzero-offset candidates and one
original-zero reference. Image left panels are byte-identical crop pixels
from the canonical drawing. Guides occupy separate copies; no drawn guide
can be treated as author ink. No contour fitting, width recalculation, p-value
search, private key/wallet/mnemonic or outside source.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE167=ROOT/"analysis"/"runs"/"stage167-sail-footpoint-pixel-alignment"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage168-sail-foot-review"
OUT.mkdir(parents=True,exist_ok=True)
RAW_OUT=OUT/"raw_original_crops"
RAW_OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
SITES=(
 ("sail2",2,0),
 ("sail3",1,8),
 ("sail4",2,-8),
 ("sail5",2,-8),
)
T0=.65
T1=1.0
PAD=30
ZOOM=3
TILE=360
HEADER=38
CANVAS_BG=245

def key(site,index):return f"{site}_{'left' if index==1 else 'right'}"

def bounds(apex,foot,shift,shape):
    xa,ya=apex
    xf,yf=foot
    vals=[
      ((1-T0)*xa+T0*xf,(1-T0)*ya+T0*yf),
      (xf,yf),
      ((1-T0)*xa+T0*(xf+shift),(1-T0)*ya+T0*yf),
      (xf+shift,yf)]
    xs=[x for x,y in vals];ys=[y for x,y in vals]
    x0=max(0,int(np.floor(min(xs)))-PAD)
    y0=max(0,int(np.floor(min(ys)))-PAD)
    x1=min(shape[1],int(np.ceil(max(xs)))+PAD+1)
    y1=min(shape[0],int(np.ceil(max(ys)))+PAD+1)
    return x0,y0,x1,y1

def guide(crop,box,apex,foot,shift):
    out=cv2.cvtColor(crop,cv2.COLOR_GRAY2BGR)
    x0,y0,_,_=box
    ax,ay=apex
    fx,fy=foot
    fx+=shift
    src0=((1-T0)*ax+T0*fx,(1-T0)*ay+T0*fy)
    orig=tuple(int(round(v)) for v in (src0[0]-x0,src0[1]-y0))
    end=(int(round(fx-x0)),int(round(fy-y0)))
    cv2.line(out,orig,end,(5,80,230) if shift==0 else (210,130,20),1,cv2.LINE_8)
    cv2.drawMarker(out,end,(0,0,255) if shift==0 else (255,140,0),
                   cv2.MARKER_CROSS,7,1)
    return out

def make_tile(arr,title):
    img=cv2.cvtColor(arr,cv2.COLOR_GRAY2BGR) if arr.ndim==2 else arr
    height,width=img.shape[:2]
    zoom=cv2.resize(img,(width*ZOOM,height*ZOOM),interpolation=cv2.INTER_NEAREST)
    s=min(1.0,float(TILE-14)/max(zoom.shape[:2]))
    if s<1.0:
        zoom=cv2.resize(zoom,(max(1,int(zoom.shape[1]*s)),max(1,int(zoom.shape[0]*s))),
                       interpolation=cv2.INTER_NEAREST)
    tile=np.full((TILE,TILE,3),CANVAS_BG,np.uint8)
    cv2.putText(tile,title,(8,24),cv2.FONT_HERSHEY_SIMPLEX,.47,(0,0,0),1,cv2.LINE_AA)
    hh,ww=zoom.shape[:2]
    x=(TILE-ww)//2;y=HEADER+max(0,(TILE-HEADER-hh)//2)
    y=min(y,TILE-hh)
    tile[y:y+hh,x:x+ww]=zoom
    return tile

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    stage167=json.loads(STAGE167.read_text())
    src=np.asarray(Image.open(SOURCE).convert("L"))
    flags=stage167["stable_same_nonzero_offsets"]
    actual={(z["site"],z["offset_px"]) for z in flags}
    expected={(key(s,i),off) for s,i,off in SITES if off!=0}
    orig0=set(stage167["stable_original_offset_zero"])
    checks={
       "canonical_SHA":digest==SHA==stage167["source_sha256"],
       "repaired_Stage167_160_known_controls":stage167["synthetic_fixture_controls"]["passed"]==160
                 and stage167["synthetic_fixture_controls"]["pass"],
       "Stage167_final_source_decision":stage167["decision"]=="ANNOTATED_FOOT_SHIFT_REQUIRES_MANUAL_SOURCE_REVIEW",
       "three_exact_nonzero_sites":actual==expected,
       "one_original_zero_reference":orig0=={"sail2_right"},
       "four_immutable_sites":len(SITES)==4,
       "canonical_dimensions":src.shape==(1105,1600)}
    sheet=np.full((len(SITES)*TILE,3*TILE,3),CANVAS_BG,np.uint8)
    rows=[]
    for rank,(site,index,offset) in enumerate(SITES):
        apex=TRIANGLES[site][0]
        foot=TRIANGLES[site][index]
        bb=bounds(apex,foot,offset,src.shape)
        x0,y0,x1,y1=bb
        crop=src[y0:y1,x0:x1]
        name=key(site,index)
        assert crop.size and x0<x1 and y0<y1
        raw_file=RAW_OUT/(name+".png")
        cv2.imwrite(str(raw_file),crop)
        readback=cv2.imread(str(raw_file),cv2.IMREAD_GRAYSCALE)
        pixel_equal=np.array_equal(crop,src[y0:y1,x0:x1]) and np.array_equal(crop,readback)
        checks["raw_crop_exact_"+name]=bool(pixel_equal)
        panel0=make_tile(crop,name+" RAW unannotated")
        panel1=make_tile(guide(crop,bb,apex,foot,0),name+" original 0px")
        panel2=make_tile(guide(crop,bb,apex,foot,offset),name+f" Stage167 {offset:+d}px")
        sheet[rank*TILE:(rank+1)*TILE,:TILE]=panel0
        sheet[rank*TILE:(rank+1)*TILE,TILE:2*TILE]=panel1
        sheet[rank*TILE:(rank+1)*TILE,2*TILE:3*TILE]=panel2
        r=stage167["source_by_format_site"]["original"][name]
        rows.append({"site":name,"stage167_selected_dx":offset,
           "source_apex":apex,"source_annotated_foot":foot,
           "raw_bbox":bb,"raw_shape":list(crop.shape),
           "raw_pixel_SHA256":hashlib.sha256(crop.tobytes()).hexdigest(),
           "raw_pixel_equal":bool(pixel_equal),
           "stage167_source_best_support":r["top_support"],
           "stage167_source_best_second_margin":r["support_margin"]})
    success=cv2.imwrite(str(OUT/"sail-feet-original-vs-guides.png"),sheet)
    checks["contact_image_saved"]=bool(success)
    good=all(checks.values())
    decision="CONTACT_SHEET_READY_FOR_MANUAL_SOURCE_REVIEW" if good else "CONTROL_FAILURE"
    data={
       "experiment_id":"A11-EXP-168",
       "canonical_source_sha256":digest,
       "purpose":"Visual-original-image diagnostic, NOT new pixel-pattern extraction, detected offset selection or cryptographic testing.",
       "fixed_stage167_source_sites":rows,
       "structural_checks":checks,"controls_passed":sum(checks.values()),
       "controls_total":len(checks),"decision":decision,
       "interpretation_guard":"Left panels retain original grayscale pixels; colored guides in right panels are generated by code and never counted as author marks. A guide following a hatch/hull line is not proof of a true sail outline. No Stage165 width or p-value is revised.",
       "safety":"Canonical source and archived reports only, no wallets, private keys, addresses, BIP39, text payload derivation or outside research."
    }
    (OUT/"result.json").write_text(json.dumps(data,indent=2)+"\n")
    report=["# Stage168 — manual source-visual review contact of three Stage167 nonzero offsets","",
       f"- Canonical PNG SHA verified: **{digest==SHA}**",
       f"- Prior Stage167 archive and raw crop provenance checks: **{sum(checks.values())}/{len(checks)}**",
       "- Unmodified raw source crop at LEFT, original 0px guide in MIDDLE, fixed Stage167 +8/-8px guide at RIGHT.",
       f"- Decision: **{decision}**",""]
    for z in rows:
        report.append(f"- {z['site']}: original raw crop SHA-256 {z['raw_pixel_SHA256']}; Stage167 dx {z['stage167_selected_dx']:+d}px; original source support {z['stage167_source_best_support']:.3f}; margin {z['stage167_source_best_second_margin']:.3f}")
    report+=["","**Required human judgment:** determine whether each blue/orange shifted guide follows the OUTER sail edge rather than dense interior hatching, another boat's hull, or pier rigging. If not unambiguous, retain INCONCLUSIVE instead of modifying annotated widths.","",
      "This generation does not independently validate physical corner connectivity, image-coded meaning, keys or wallets. No source artwork was edited.",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":168,"checks":f"{sum(checks.values())}/{len(checks)}",
                      "rows":len(rows),"decision":decision}))
if __name__=="__main__":main()
