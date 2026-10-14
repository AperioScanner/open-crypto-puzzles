#!/usr/bin/env python3
"""A11-EXP-160 — source provenance of Stage12 rectangular crop perimeter scores.

Two proven historical source defects: Stage132 large sail/hull box and Stage155
small-sail y-band. Replay the old Stage12 rectangular perimeter exactly,
then describe the source polygon-only corrected object measurements versus
ordinary filled silhouettes. Fixed preregistration: analysis/STAGE_QUEUE.md.
No crypto, key, BIP39, wallet, or off-image activity.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from stage12_count_perimeter import perimeter_fraction
from stage112_corrected_sail_width_progression import variants
from stage132_large_sail_legacy_bbox_audit import POLYGONS
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE12=ROOT/"analysis"/"runs"/"stage12-count-perimeter"/"result.json"
STAGE132=ROOT/"analysis"/"runs"/"stage132-large-sail-roi-coverage"/"result.json"
STAGE155=ROOT/"analysis"/"runs"/"stage155-small-sail-band-audit"/"result.json"
STAGE159=ROOT/"analysis"/"runs"/"stage159-full-boat-projection"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage160-full-object-perimeter-audit"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
THRESHOLD=140
WIDTHS=(1,2,4)
FORMATS=("original","jpeg85","jpeg70","down75_up")
LEGACY={
 "large_sailboat":(44,320,359,599),
 "small_sails_full_band":(0,360,1600,480),
}
FIXED_BOUNDS={
 "large_sailboat":(25,398,526,940),
 "small_sails_full_band":(1007,357,1538,547),
}
KER=np.ones((5,5),np.uint8)

def fixed_polygon_crops(shape):
    definitions={
        "large_sailboat":[POLYGONS["large_sail"],POLYGONS["large_hull"]],
        "small_sails_full_band":[p for n,p in TRIANGLES.items() if n.startswith("sail")],
    }
    output={}
    for label,group in definitions.items():
        merged=np.zeros(shape,np.uint8)
        allpoints=[]
        for polygon in group:
            v=np.asarray(polygon,np.int32)
            temp=np.zeros(shape,np.uint8)
            cv2.fillPoly(temp,[v],255)
            merged=np.maximum(merged,cv2.erode(temp,KER,iterations=1))
            allpoints.extend(polygon)
        pts=np.asarray(allpoints,np.int32)
        bbox=(int(pts[:,0].min()),int(pts[:,1].min()),
              int(pts[:,0].max()+1),int(pts[:,1].max()+1))
        if bbox!=FIXED_BOUNDS[label]:
            raise RuntimeError(f"source polygon geometry changed: {label} {bbox}")
        x0,y0,x1,y1=bbox
        submask=(merged[y0:y1,x0:x1]>0)
        output[label]={"bbox":bbox,"mask":submask,"area":int(submask.sum())}
    return output

def whiten_outside(original,mask):
    result=original.copy()
    result[~mask]=255
    return result

def calc_rings(frame):
    return {str(w):float(perimeter_fraction(frame,THRESHOLD,w)) for w in WIDTHS}

def eligible_ring_mask_pixels(mask,width):
    """Count image pixels that COULD affect the corrected crop-ring metric.

    If this is zero for the preregistered width2, then a zero edge measurement
    is mathematically forced by the mask and tells us NOTHING about source ink.
    """
    ring=np.zeros(mask.shape,np.bool_)
    ring[:width,:]=True
    ring[-width:,:]=True
    ring[:,:width]=True
    ring[:,-width:]=True
    return int(np.count_nonzero(mask & ring))

def archive_replay(gray):
    archive=json.loads(STAGE12.read_text())
    rows={}
    for label,bbox in LEGACY.items():
        row=next(z for z in archive["regions"] if z["name"]==label)
        if tuple(row["bbox"])!=bbox:
            raise RuntimeError("Stage12 historical bbox changed: "+label)
        x0,y0,x1,y1=bbox
        actual=calc_rings(gray[y0:y1,x0:x1])
        expected={str(w):float(row["perimeter_fraction_t140"]["w"+str(w)]) for w in WIDTHS}
        compare={str(w):abs(actual[str(w)]-expected[str(w)])<=1e-8 for w in WIDTHS}
        rows[label]={"original_box":bbox,"expected":expected,"actual":actual,"passes":compare}
    return {"pass":all(all(v["passes"].values()) for v in rows.values()),
            "passed":sum(sum(z["passes"].values()) for z in rows.values()),
            "cases":6,"by_region":rows}

def fixture(shape,kind):
    a=np.full(shape,255,np.uint8)
    if kind=="black_border_6":
        a[:6,:]=0
        a[-6:,:]=0
        a[:,:6]=0
        a[:,-6:]=0
    elif kind=="black_interior_white_border_6":
        a[6:-6,6:-6]=0
    else:
        raise ValueError(kind)
    return a

def controls(sources):
    cases=[]
    for region,info in sources.items():
        shape=info["mask"].shape
        for kind in ("black_border_6","black_interior_white_border_6"):
            for fmt,frame in variants(fixture(shape,kind)).items():
                if fmt not in FORMATS:continue
                z=calc_rings(frame)
                for w in WIDTHS:
                    value=z[str(w)]
                    passed=(value>=.90 if kind=="black_border_6" else value<=.10)
                    cases.append({"region":region,"fixture":kind,"variant":fmt,
                                  "width":w,"score":round(value,6),
                                  "pass":bool(passed)})
    return {"pass":len(cases)==48 and all(v["pass"] for v in cases),
            "passed":sum(v["pass"] for v in cases),"cases":len(cases),
            "failures":[c for c in cases if not c["pass"]]}

def safe_preconditions():
    stage132=json.loads(STAGE132.read_text())
    stage155=json.loads(STAGE155.read_text())
    stage159=json.loads(STAGE159.read_text())
    if stage132["decision"]!="LEGACY_LARGE_SAILBOAT_BBOX_INCOMPLETE":
        raise RuntimeError("Missing confirmed Stage132 defect")
    if stage155["decision"]!="LEGACY_SMALL_SAIL_BAND_MATERIALLY_TRUNCATES_TRUE_SAILS":
        raise RuntimeError("Missing confirmed Stage155 defect")
    if stage159["decision"]!="SOURCE_LAG3_COMPATIBLE_WITH_FULL_BOAT_SILHOUETTE":
        raise RuntimeError("Previous scientific Stage159 decision unvalidated")

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("canonical SHA mismatch")
    gray=np.asarray(Image.open(SOURCE).convert("L"))
    if gray.shape!=(1105,1600):raise RuntimeError("image shape mismatch")
    safe_preconditions()
    sources=fixed_polygon_crops(gray.shape)
    old=archive_replay(gray)
    ctl=controls(sources)
    realframes=variants(gray)
    measured={}
    for name,info in sources.items():
        x0,y0,x1,y1=info["bbox"]
        mask=info["mask"]
        flat=np.full(mask.shape,255,np.uint8)
        flat[mask]=0
        flatframes=variants(flat)
        byfmt={}
        for fmt in FORMATS:
            real=whiten_outside(realframes[fmt][y0:y1,x0:x1],mask)
            reference=whiten_outside(flatframes[fmt],mask)
            r=calc_rings(real)
            f=calc_rings(reference)
            byfmt[fmt]={"source_w":r,"shape_only_w":f,
                "source_minus_shape_w":{str(w):r[str(w)]-f[str(w)] for w in WIDTHS}}
        measured[name]={"fixed_bbox":info["bbox"],"mask_area":info["area"],
                        "by_format":byfmt}
    ring_coverage={name:{str(w):eligible_ring_mask_pixels(info["mask"],w)
                         for w in WIDTHS} for name,info in sources.items()}
    w2_informative=all(row["2"]>0 for row in ring_coverage.values())
    compatible=all(
        measured[name]["by_format"][fmt]["source_minus_shape_w"]["2"]<=.15
        for name in sources for fmt in FORMATS
    )
    outlier=any(
        all(measured[name]["by_format"][fmt]["source_w"]["2"]>=.25 and
            measured[name]["by_format"][fmt]["source_minus_shape_w"]["2"]>.15
            for fmt in FORMATS)
        for name in sources
    )
    decision=("CONTROL_FAILURE" if not ctl["pass"] else
              "HISTORICAL_REPLAY_FAILURE" if not old["pass"] else
              "MASKED_RECTANGLE_EDGE_NONINFORMATIVE_BY_CONSTRUCTION" if not w2_informative else
              "SOURCE_CROP_EDGE_COMPATIBLE_WITH_FILLED_GEOMETRY" if compatible else
              "CORRECTED_EDGE_EXCESS_WARRANTS_VISUAL_REVIEW" if outlier else
              "PERIMETER_MEASUREMENT_INCONCLUSIVE")
    result={
        "experiment_id":"A11-EXP-160","source_sha256":digest,
        "hypothesis":"Stage12 crop-border occupancy is not an intrinsic drawn-object contour; after known false ROIs are corrected, compare observed image ink at fixed rectangle edges to shape-only controls.",
        "historical_stage12_replay":old,
        "corrected_source_regions":"Fixed polygons from prior Stages132 and153; 5x5 erosion; tight native extents, no new annotations.",
        "fixed_gates":{"gray_less_than":THRESHOLD,"ring_widths":WIDTHS,
            "formats":FORMATS,
            "expected_shape_compatibility":"source w2 minus flat w2 <= 0.15 for both regions in all four variants",
            "excess_review":"source w2>=0.25 AND source minus flat >0.15 at one region, all four formats"},
        "synthetic_controls":ctl,
        "eligible_mask_pixels_in_crop_rings":ring_coverage,
        "source_w2_informative":bool(w2_informative),
        "corrected_vs_flat":measured,
        "source_shape_compatible":compatible,
        "exceptional_source_edge_occupancy":outlier,
        "decision":decision,
        "scope_limit":"The old crops and corrected masks describe different samples: their perimeter percentages cannot be compared as if they were object attributes. One source image in all formats. This is QA, not a cipher or author-intent claim.",
        "safety":"Image-source analysis only; no keys, wallets, mnemonics, addresses or external research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage160 — Corrected Stage12 crop-border/perimeter measurement source audit","",
        f"- Canonical image SHA correct: **{digest==SHA}**",
        f"- Six original Stage12 source crop perimeter percentages exactly reproduced: **{old['passed']}/{old['cases']}**",
        f"- Synthetic black-rim / white-rim fixture controls: **{ctl['passed']}/{ctl['cases']}**",
        f"- Real source pixels eligible in corrected width2 rings: **{ring_coverage['large_sailboat']['2']} large / {ring_coverage['small_sails_full_band']['2']} small**",
        f"- Real source edge occupancies consistent with filled silhouette control in both corrected objects and four formats: **{compatible}**",
        f"- Decision: **{decision}**","",
        "| Object | Historical cropped w2 (t140) | Corrected real w2 original | Fixed filled silhouette w2 | Source minus silhouette |",
        "|---|---:|---:|---:|---:|"]
    for name in LEGACY:
        h=old["by_region"][name]["actual"]["2"]
        v=measured[name]["by_format"]["original"]
        lines.append(f"| {name} | {h:.4f} | {v['source_w']['2']:.4f} | {v['shape_only_w']['2']:.4f} | {v['source_minus_shape_w']['2']:+.4f} |")
    lines+=["","**Interpretation:** Stage12's perimeter fraction was defined on the rectangle crop edge, not the hand-drawn outline. The old ROI is defective for both objects. If eligible pixels in the 2px corrected ring are ZERO, the corrected zero is guaranteed by mask erosion and cannot be evidence about original pencil marks. Historical counts and other already-validated regions were untouched.","",
           "The two different ROI definitions do not estimate the same quantity; numerical difference is provenance-only.","",
           "No hidden payload, key, wallet or BIP39 extraction attempted.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":160,"old_replay":f"{old['passed']}/{old['cases']}",
          "eligible_w2_pixels":{k:v["2"] for k,v in ring_coverage.items()},
          "controls":f"{ctl['passed']}/{ctl['cases']}",
          "shape":compatible,"exceptional":outlier,"decision":decision}))
if __name__=="__main__":
    main()
