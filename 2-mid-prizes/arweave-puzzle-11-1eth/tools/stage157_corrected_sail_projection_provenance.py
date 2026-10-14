#!/usr/bin/env python3
"""Stage157: source-provenance control for Stage12 sail-band lag=3 projection.

Replays Stage12's unchanged projection_periodicity diagnostic, fixes ONLY its
known obsolete five-sail ROI using masks already established in Stage153,
and tests whether broad silhouettes alone create lag=3. No cryptographic
key/phrase/address/wallet reconstruction or external sources.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from stage12_count_perimeter import projection_periodicity
from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR=ROOT/"analysis"/"runs"/"stage12-count-perimeter"/"result.json"
PRIOR156=ROOT/"analysis"/"runs"/"stage156-corrected-sail-counts"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage157-corrected-sail-projection"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
THRESHOLDS=(110,140,170)
PAD=7
SITES={k:v for k,v in TRIANGLES.items() if k.startswith("sail")}

def build_mask(shape):
    mask=np.zeros(shape,np.uint8)
    for t in SITES.values():
        layer=np.zeros(shape,np.uint8)
        cv2.fillPoly(layer,[np.array(t,np.int32)],255)
        layer=cv2.erode(layer,np.ones((5,5),np.uint8),iterations=1)
        mask=np.maximum(mask,layer)
    pts=np.vstack([np.array(p,int) for p in SITES.values()])
    x0,y0=int(pts[:,0].min()-PAD),int(pts[:,1].min()-PAD)
    x1,y1=int(pts[:,0].max()+PAD+1),int(pts[:,1].max()+PAD+1)
    box=(x0,y0,x1,y1)
    if box!=(1000,350,1545,554):
        raise RuntimeError(f"Immutable mask bounds mismatch {box}")
    return (mask[y0:y1,x0:x1]>0),box

def only_sails(crop,mask):
    copy=crop.copy()
    copy[~mask]=255
    return copy

def synthetic(mask,kind):
    result=np.full(mask.shape,255,np.uint8)
    if kind=="flat_silhouette":
        result[mask]=0
    elif kind=="stripes_12":
        yy,xx=np.indices(result.shape)
        result[mask &(xx%12<3)]=0
    else:raise ValueError(kind)
    return result

def controls(mask):
    passed=0; observations=[]
    for kind in ("flat_silhouette","stripes_12"):
        for fmt,image in variants(synthetic(mask,kind)).items():
            if fmt not in FORMATS:continue
            frame=only_sails(image,mask)
            for t in THRESHOLDS:
                m=projection_periodicity(frame,t)["x"]
                good=(
                    (m["best_lag"]==3 and m["score"]>=.80)
                    if kind=="flat_silhouette" else
                    (11<=m["best_lag"]<=13 and m["score"]>=.70)
                )
                passed+=int(good)
                observations.append({"kind":kind,"fmt":fmt,"threshold":t,
                    "lag":m["best_lag"],"score":round(m["score"],6),"pass":bool(good)})
    return {"pass":passed==len(observations)==24,"passed":passed,
            "cases":len(observations),
            "failed_cases":[o for o in observations if not o["pass"]]}

def stage12_replay(gray):
    j=json.loads(PRIOR.read_text())
    historical=next(row for row in j["regions"] if row["name"]=="small_sails_full_band")
    expected=historical["projection_periodicity_t140"]
    measured=projection_periodicity(gray[360:480,:],140)
    ok=all(measured[axis]["best_lag"]==expected[axis]["best_lag"] and
            abs(measured[axis]["score"]-expected[axis]["score"])<=1e-6
            for axis in ("x","y"))
    return {"pass":bool(ok),"expected":expected,"measured":measured}

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if sha!=SHA:raise RuntimeError("canonical source mismatch")
    z=json.loads(PRIOR156.read_text())
    if z["decision"] not in (
          "NO_STABLE_FULL_SAIL_COUNT_CORROBORATION",
          "CORRECTED_SAIL_COUNT_SIGNATURE_REQUIRES_SOURCE_REVIEW"):
        raise RuntimeError("Stage156 not valid or not completed")
    im=cv2.imread(str(PNG),cv2.IMREAD_UNCHANGED)
    gray=im[:,:,0] if im.ndim==3 else im
    if gray.shape!=(1105,1600):raise RuntimeError("PNG dimensions changed")
    mask,box=build_mask(gray.shape)
    old=stage12_replay(gray)
    ctl=controls(mask)
    real={}
    for fmt,img in variants(gray).items():
        if fmt not in FORMATS:continue
        roi=only_sails(img[box[1]:box[3],box[0]:box[2]],mask)
        real[fmt]={str(thr):projection_periodicity(roi,thr)
                    for thr in THRESHOLDS}
    flat=variants(synthetic(mask,"flat_silhouette"))
    flats={
        fmt:{str(thr):projection_periodicity(only_sails(image,mask),thr)
             for thr in THRESHOLDS}
        for fmt,image in flat.items() if fmt in FORMATS
    }
    readings=[{"format":fmt,"threshold":t,
               "real_lag":real[fmt][str(t)]["x"]["best_lag"],
               "real_score":real[fmt][str(t)]["x"]["score"],
               "flat_lag":flats[fmt][str(t)]["x"]["best_lag"],
               "flat_score":flats[fmt][str(t)]["x"]["score"],
               "abs_score_diff":abs(real[fmt][str(t)]["x"]["score"]-
                                    flats[fmt][str(t)]["x"]["score"])}
              for fmt in FORMATS for t in THRESHOLDS]
    silhouette=all(x["real_lag"]==3 and x["flat_lag"]==3 and
                   x["abs_score_diff"]<=.30 for x in readings)
    stable_lags={x["real_lag"] for x in readings}
    nontrivial=(len(stable_lags)==1 and next(iter(stable_lags))>=6
                and all(x["real_score"]>=.70 for x in readings))
    decision=("CONTROL_FAILURE" if not ctl["pass"] else
              "HISTORICAL_REPLAY_FAILURE" if not old["pass"] else
              "SOURCE_LAG3_COMPATIBLE_WITH_SILHOUETTE" if silhouette else
              "NONTRIVIAL_SOURCE_PROJECTION_REQUIRES_REVIEW" if nontrivial else
              "SOURCE_PROJECTION_INCONCLUSIVE")
    result={
        "experiment_id":"A11-EXP-157","source_sha256":sha,
        "motivation":"Stage155 proved prior Stage12 y-band excluded four genuine sails; Stage156 non-secret count recheck found no stable 321 or 123.",
        "historical_stage12_lag_replay":old,
        "source_fixed_bbox":box,"fixed_sail_polygon_source":"Stage153 5 genuine sail polygons",
        "fixed_gates":{"source_thresholds":THRESHOLDS,"source_formats":FORMATS,
           "mask_erosion":5,"bbox_padding":PAD,"control_flat":"x lag 3 and score>=0.80",
           "control_period12":"x lag 11..13 and score>=0.70",
           "real_silhouette_compatible":"x lag3 in all 12 with abs real-minus-flat score<=0.30",
           "nontrivial_source":"same x lag>=6 in all 12 and score>=0.70"},
        "synthetic_controls":ctl,
        "by_variant":real,"flat_silhouette_by_variant":flats,
        "source_vs_flat":readings,
        "source_silhouette_compatible":silhouette,
        "source_nontrivial_consistent":nontrivial,
        "decision":decision,
        "interpretation_limit":"Autocorrelation at short lags is a normal consequence of smooth silhouettes and pencil continuity. JPEG variants are image stability tests, not independent replicates; negative of this fixed projection rule cannot exclude other hidden structures.",
        "safety":"Pure canonical source geometry/stroke diagnostic. No key, BIP39, wallet, address or off-source search."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage157 — source-vs-silhouette control of old Stage12 projection lag","",
      f"- Original PNG SHA verified: **{sha==SHA}**",
      f"- Old Stage12 projection (x and y lag/score) exact replay: **{old['pass']}**",
      f"- Synthetic flat-vs-period12 controls: **{ctl['passed']}/{ctl['cases']}**",
      f"- Corrected ROI: x={box[0]}..{box[2]}, y={box[1]}..{box[3]} (only 5 true sail polygon interiors)",
      f"- Original old-band x-lag: **{old['measured']['x']['best_lag']}**; old score **{old['measured']['x']['score']:.3f}**",
      f"- Corrected source lag3 compatible with silhouette across 12: **{silhouette}**",
      f"- Decision: **{decision}**","",
      "| Source/threshold | corrected lag/score | flat geometry lag/score | abs difference |",
      "|---|---|---|---|"]
    for x in readings:
        lines.append(f"| {x['format']} t{x['threshold']} | {x['real_lag']} / {x['real_score']:.3f} | {x['flat_lag']} / {x['flat_score']:.3f} | {x['abs_score_diff']:.3f} |")
    lines+=["","The old y=[360,480) measurement was not a full five-sail inspection. A close match of corrected source lag3 to filled polygon silhouettes is mundane geometry, not an encoded three or an instruction.","",
      "This analysis does not derive, reconstruct or test any secret; no additional Stage is implied by a null result.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":157,"controls":f"{ctl['passed']}/{ctl['cases']}",
       "historical_replay":old["pass"],"silhouette":silhouette,"decision":decision}))
if __name__=="__main__":main()
