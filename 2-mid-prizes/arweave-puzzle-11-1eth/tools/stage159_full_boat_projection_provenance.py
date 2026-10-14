#!/usr/bin/env python3
"""A11-EXP-159: corrected true large-boat projection versus ordinary silhouette.

Replicates Stage12's old source metadata, then compares corrected Stage132
large sail + hull only to shape-only and periodic synthetic controls.
No decoding or cryptographic/financial access.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from stage12_count_perimeter import projection_periodicity
from stage112_corrected_sail_width_progression import variants
from stage132_large_sail_legacy_bbox_audit import POLYGONS

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR=ROOT/"analysis"/"runs"/"stage12-count-perimeter"/"result.json"
STAGE158=ROOT/"analysis"/"runs"/"stage158-corrected-large-boat-counts"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage159-full-boat-projection"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
THRESHOLDS=(110,140,170)
EXPECTED_LEGACY=(44,320,359,599)
EXPECTED_BOUNDS=(18,391,533,947)
KERNEL=np.ones((5,5),np.uint8)

def masks_and_box(shape):
    mask=np.zeros(shape,np.uint8)
    allpts=[]
    for pts in (POLYGONS["large_sail"],POLYGONS["large_hull"]):
        img=np.zeros(shape,np.uint8)
        p=np.array(pts,np.int32)
        cv2.fillPoly(img,[p],255)
        img=cv2.erode(img,KERNEL,iterations=1)
        mask=np.maximum(mask,img)
        allpts.extend(pts)
    pts=np.array(allpts,np.int32)
    box=(int(pts[:,0].min()-7),int(pts[:,1].min()-7),
         int(pts[:,0].max()+8),int(pts[:,1].max()+8))
    if box!=EXPECTED_BOUNDS:raise RuntimeError(f"Fixed box changed: {box}")
    x0,y0,x1,y1=box
    return mask[y0:y1,x0:x1]>0,box

def whiten(frame,mask):
    out=frame.copy()
    out[~mask]=255
    return out

def fixture(mask,kind):
    raw=np.full(mask.shape,255,np.uint8)
    if kind=="flat":
        raw[mask]=0
    elif kind=="period12":
        y,x=np.indices(raw.shape)
        raw[mask&(x%12<5)]=0
    else: raise ValueError(kind)
    return raw

def controls(mask):
    rows=[]
    for kind in ("flat","period12"):
        for fmt,frame in variants(fixture(mask,kind)).items():
            if fmt not in FORMATS:continue
            img=whiten(frame,mask)
            for t in THRESHOLDS:
                reading=projection_periodicity(img,t)["x"]
                if kind=="flat":
                    passed=(reading["best_lag"]==3 and reading["score"]>=.78)
                else:
                    passed=(11<=reading["best_lag"]<=13 and reading["score"]>=.67)
                rows.append({"kind":kind,"format":fmt,"threshold":t,
                    "lag":reading["best_lag"],"score":round(reading["score"],6),
                    "pass":bool(passed)})
    return {"pass":len(rows)==24 and all(r["pass"] for r in rows),
            "passed":sum(r["pass"] for r in rows),"cases":len(rows),
            "failures":[r for r in rows if not r["pass"]]}

def legacy_replay(gray):
    hist=json.loads(PRIOR.read_text())
    original=next(v for v in hist["regions"] if v["name"]=="large_sailboat")
    if tuple(original["bbox"])!=EXPECTED_LEGACY:
        raise RuntimeError("Historical ROI mutated")
    ex=original["projection_periodicity_t140"]
    x0,y0,x1,y1=EXPECTED_LEGACY
    actual=projection_periodicity(gray[y0:y1,x0:x1],140)
    passing=all(actual[a]["best_lag"]==ex[a]["best_lag"]
                and abs(actual[a]["score"]-ex[a]["score"])<=1e-6
                for a in ("x","y"))
    return {"pass":bool(passing),"expected":ex,"observed":actual}

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Canonical SHA mismatch")
    previous=json.loads(STAGE158.read_text())
    if previous["decision"] not in (
       "NO_STABLE_FULL_LARGE_BOAT_COUNT_CORROBORATION",
       "CORRECTED_FULL_BOAT_321_OR_123_NEEDS_VISUAL_REVIEW"):
        raise RuntimeError("Stage158 does not have a valid completed scientific decision")
    gray=np.asarray(Image.open(SOURCE).convert("L"))
    if gray.shape!=(1105,1600):raise RuntimeError("Image dimensions changed")
    mask,box=masks_and_box(gray.shape)
    replay=legacy_replay(gray)
    calibration=controls(mask)
    x0,y0,x1,y1=box
    real={}
    for fmt,frame in variants(gray).items():
        if fmt not in FORMATS:continue
        full=whiten(frame[y0:y1,x0:x1],mask)
        real[fmt]={str(t):projection_periodicity(full,t) for t in THRESHOLDS}
    flat={}
    for fmt,frame in variants(fixture(mask,"flat")).items():
        if fmt not in FORMATS:continue
        full=whiten(frame,mask)
        flat[fmt]={str(t):projection_periodicity(full,t) for t in THRESHOLDS}
    observations=[]
    for fmt in FORMATS:
        for t in THRESHOLDS:
            r=real[fmt][str(t)]["x"]
            f=flat[fmt][str(t)]["x"]
            observations.append({"format":fmt,"threshold":t,
                "real_x_lag":r["best_lag"],"real_x_score":r["score"],
                "flat_x_lag":f["best_lag"],"flat_x_score":f["score"],
                "abs_score_delta":abs(r["score"]-f["score"])})
    compatible=all(x["real_x_lag"]==3 and x["flat_x_lag"]==3 and
                  x["abs_score_delta"]<=.30 for x in observations)
    lags={x["real_x_lag"] for x in observations}
    alternative=(len(lags)==1 and next(iter(lags)) is not None
                 and next(iter(lags))>=6
                 and all(x["real_x_score"]>=.70 for x in observations))
    verdict=("CONTROL_FAILURE" if not calibration["pass"]
        else "HISTORICAL_REPLAY_FAILURE" if not replay["pass"]
        else "SOURCE_LAG3_COMPATIBLE_WITH_FULL_BOAT_SILHOUETTE" if compatible
        else "NONTRIVIAL_FULL_BOAT_PROJECTION_REQUIRES_REVIEW" if alternative
        else "SOURCE_PROJECTION_INCONCLUSIVE")
    result={"experiment_id":"A11-EXP-159","original_sha256":digest,
         "immutable_source":"Stage132 full sail and hull polygons, fixed 5x5 erosion and 7px bounding pad",
         "fixed_box":box,"legacy_roi":EXPECTED_LEGACY,
         "old_stage12_exact_replay":replay,"controls":calibration,
         "real_by_format":real,"shape_only_by_format":flat,
         "precommitted_observations":observations,
         "compatible_with_silhouette":compatible,"nontrivial_pattern":alternative,
         "decision":verdict,
         "scope_limit":"Only the y/x short-lag projection statistic of Stage12 legacy large-sailboat region. Image re-encodings are not independent source replication. Positive lag does not establish a digit, intention, or hidden message.",
         "safety":"Non-secret original-image analysis: no private key, mnemonic, wallet, address or outside-site research."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage159 — audit Stage12 old large-boat projection with full source","",
       f"- PNG SHA correct: **{digest==SHA}**",
       f"- Stage12 old x/y projection exact replay: **{replay['pass']}**",
       f"- Flat shape / x-period12 controls: **{calibration['passed']}/{calibration['cases']}**",
       f"- Five-source? No: true FULL LARGE sail + hull mask with 7px box pad.",
       f"- Corrected x lag3 shape explanation stable 12/12: **{compatible}**",
       f"- Decision: **{verdict}**","",
       "| Format/threshold | real x lag/score | flat x lag/score | score difference |",
       "|---|---|---|---|"]
    for p in observations:
        lines.append(f"| {p['format']} t{p['threshold']} | {p['real_x_lag']} / {p['real_x_score']:.3f} | {p['flat_x_lag']} / {p['flat_x_score']:.3f} | {p['abs_score_delta']:.3f} |")
    lines+=["","The source ROI was defective in Stage12, but recovering the complete source does not by itself indicate a hidden digit. No keys, wallets or off-image material involved.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":159,"controls":f"{calibration['passed']}/{calibration['cases']}",
         "old_replay":replay["pass"],"compatible":compatible,"decision":verdict}))
if __name__=="__main__":main()
