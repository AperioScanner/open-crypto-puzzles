#!/usr/bin/env python3
"""Stage 120: exact visual stroke-template reuse among the five true small sails.

Only the canonical image is read. This test asks whether two or more sails
repeat the same *hand-drawn interior fingerprint* after geometric scaling and
optional reflection. It does not encode words, secrets, keys, or wallet data.

This is different from stages 18/112 (width progression), 102 (L/R direction),
105 (spoke count), and 111 (cross-object x alignment).
"""
from __future__ import annotations

import hashlib
import io
import itertools
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from stage112_corrected_sail_width_progression import (
    detect_centers, boxes_from_centers, variants,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "clues" / "arweave-puzzle-11.png"
OUT = ROOT / "analysis" / "runs" / "stage120-sail-motif-reuse"
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED_HASH = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
NORM_HW = (155, 128)
REAL_VARIANTS = ("original", "jpeg85", "jpeg70", "down75_up")
FIXED_MIN_INLIERS = 25
FIXED_MIN_FRACTION = 0.18

def norm_crop(gray, box):
    x0,y0,x1,y1 = map(int, box)
    roi = gray[y0:y1,x0:x1]
    if roi.size == 0:
        raise ValueError("Empty detected crop")
    return cv2.resize(roi, (NORM_HW[1], NORM_HW[0]), interpolation=cv2.INTER_AREA)

def pair_orb(a,b):
    """Affine RANSAC support for identical interior texture under modest scale."""
    orb = cv2.ORB_create(nfeatures=650,fastThreshold=6,edgeThreshold=8,patchSize=15)
    k1,d1 = orb.detectAndCompute(a, None)
    k2,d2 = orb.detectAndCompute(b, None)
    n1,n2 = len(k1),len(k2)
    result = {"features_a":n1,"features_b":n2,
              "good_matches":0,"inliers":0,"inlier_fraction":0.0}
    if d1 is None or d2 is None or min(n1,n2) < 8:
        return result
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    good = [m for pair in bf.knnMatch(d1,d2,k=2)
            if len(pair)==2 for m,n in [pair] if m.distance < 0.70*n.distance]
    result["good_matches"]=len(good)
    if len(good) < 6:
        return result
    src=np.float32([k1[m.queryIdx].pt for m in good])
    dst=np.float32([k2[m.trainIdx].pt for m in good])
    cv2.setRNGSeed(120)
    _,mask=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,
                                        ransacReprojThreshold=2.5)
    inliers=int(mask.sum()) if mask is not None else 0
    result["inliers"]=inliers
    result["inlier_fraction"]=round(inliers/min(n1,n2),6)
    return result

def pair_both(a,b):
    original=pair_orb(a,b)
    mirrored=pair_orb(a,np.ascontiguousarray(np.fliplr(b)))
    if (mirrored["inlier_fraction"],mirrored["inliers"]) > (
        original["inlier_fraction"], original["inliers"]):
        return {"mirror":True,**mirrored}
    return {"mirror":False,**original}

def synth_sail(seed):
    """Fixed outline/hull; independent stochastic interior pencil strokes."""
    rng=np.random.default_rng(seed)
    h,w=NORM_HW
    a=np.full((h,w),255,np.uint8)
    apex=(64,13);left=(22,116);right=(106,116)
    for p in (left,right):
        cv2.line(a,apex,p,0,2,cv2.LINE_AA)
    cv2.line(a,left,right,0,2,cv2.LINE_AA)
    cv2.line(a,apex,(64,125),0,2,cv2.LINE_AA)
    cv2.line(a,(15,126),(114,126),0,2,cv2.LINE_AA)
    for i in range(17):
        y=int(rng.integers(25,80))
        alpha=(y-apex[1])/(116-apex[1])
        lo=int(64+(22-64)*alpha);hi=int(64+(106-64)*alpha)
        x=int(rng.integers(lo,64) if i%2==0 else rng.integers(64,hi+1))
        base=int(rng.integers(23,106))
        cv2.line(a,(x,y),(base,115),0,1,cv2.LINE_AA)
    for _ in range(9):
        x=int(rng.integers(19,110));y=int(rng.integers(127,145))
        dx=int(rng.integers(-7,9));dy=int(rng.integers(1,6))
        cv2.line(a,(x,y),(x+dx,y+dy),0,1,cv2.LINE_AA)
    return a

def calibrate():
    base=synth_sail(0)
    h,w=NORM_HW
    transform=np.float32([[0.96,0,3],[0,0.96,-2]])
    duplicate=cv2.warpAffine(base,transform,(w,h),borderValue=255)
    encoded=cv2.imencode(".jpg",duplicate,[cv2.IMWRITE_JPEG_QUALITY,70])[1]
    duplicate=cv2.imdecode(encoded,cv2.IMREAD_GRAYSCALE)
    positive=pair_both(base,duplicate)
    reflected=pair_both(base,np.ascontiguousarray(np.fliplr(duplicate)))
    independent=[pair_both(base,synth_sail(seed)) for seed in range(1,25)]
    max_independent=max(x["inlier_fraction"] for x in independent)
    # Precommitted familywise gate. A known repeated fingerprint must stand
    # substantially above independent redraws of the same sail outline.
    cutoff=max(FIXED_MIN_FRACTION,max_independent+0.10)
    controls_pass=bool(
        positive["inliers"] >= 25
        and positive["inlier_fraction"] >= cutoff+0.05
        and reflected["inlier_fraction"] >= cutoff+0.05
        and max_independent < FIXED_MIN_FRACTION
    )
    return {
        "same_stroke_positive":positive,
        "mirrored_duplicate_positive":reflected,
        "independently_redrawn_controls":len(independent),
        "independent_max_fraction":round(float(max_independent),6),
        "familywise_fraction_gate":round(float(cutoff),6),
        "controls_pass":controls_pass,
    }

def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha != EXPECTED_HASH:
        raise SystemExit("canonical image hash differs: "+sha)
    gray=np.array(Image.open(SOURCE).convert("L"))
    if gray.shape != (1105,1600):
        raise SystemExit("incorrect canonical image shape")

    controls=calibrate()
    transformed=variants(gray)
    per_variant={}
    center_tracks={}
    for name in REAL_VARIANTS:
        im=transformed[name]
        centers=detect_centers(im)
        center_tracks[name]=centers
        if len(centers)!=5:
            raise SystemExit("five real sails not recovered in "+name)
        boxes=boxes_from_centers(centers,im.shape[1])
        crops=[norm_crop(im,b) for b in boxes]
        rows=[]
        for i,j in itertools.combinations(range(5),2):
            r=pair_both(crops[i],crops[j])
            rows.append({"sails":[i+1,j+1],**r})
        per_variant[name]=rows

    reference=np.array(center_tracks["original"])
    max_drift=max(int(max(abs(np.array(x)-reference))) for x in center_tracks.values())
    detectors_pass=max_drift<=8
    cutoff=controls["familywise_fraction_gate"]
    strong=[]
    matched_count={}
    for idx,(i,j) in enumerate(itertools.combinations(range(1,6),2)):
        measures=[per_variant[v][idx] for v in REAL_VARIANTS]
        n=sum(x["inliers"]>=FIXED_MIN_INLIERS
              and x["inlier_fraction"]>=cutoff for x in measures)
        stable_mirror=len({m["mirror"] for m in measures})==1
        keep=bool(n==len(REAL_VARIANTS) and stable_mirror)
        matched_count[f"{i}-{j}"]=n
        if keep:
            strong.append({"sails":[i,j],"observations":measures})

    supported=bool(controls["controls_pass"] and detectors_pass)
    promoted=bool(supported and len(strong)>0)
    decision=("CONTROL_FAILURE" if not supported else
              "REPLICATED_TEMPLATE_REUSE" if promoted else
              "NO_EXACT_STROKE_TEMPLATE_REUSE")
    result={
        "experiment_id":"A11-EXP-120",
        "scope":"image-only exact stroke-template reuse among five right-hand sails; no secret/key/word operations",
        "canonical_sha256":sha,
        "controls":controls,
        "detected_centers":center_tracks,
        "detector_drift_px":max_drift,
        "detectors_pass":detectors_pass,
        "variants":per_variant,
        "familywise_pair_gate": {
            "min_inliers":FIXED_MIN_INLIERS,
            "min_fraction":cutoff,
            "all_variants_required":True,
            "consistent_mirror_required":True,
        },
        "passing_variant_counts_by_pair":matched_count,
        "replicated_pairs":strong,
        "promoted":promoted,
        "decision":decision,
        "coverage_guard":"Only repeated, affine-compatible *interior stroke fingerprints* at the normalized sail crop. A negative does not refute common triangular semantics or any BIP39 hypothesis.",
        "safety_guard":"Only reads canonical PNG, never creates or evaluates keys, mnemonics, or wallet transactions.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
        "# Stage 120 — five-sail interior motif-reuse test",
        "",
        "- Scope: image-only; checks repeated interior pen strokes, not widths/directions or cryptographic values.",
        f"- Canonical PNG SHA256 verified: **{sha==EXPECTED_HASH}**",
        f"- Synthetic duplicate/redraw controls: **{controls['controls_pass']}**",
        f"- Detector stable across image variants: **{detectors_pass}**, drift **{max_drift}px**",
        f"- Independent-redraw maximum: **{controls['independent_max_fraction']:.4f}**",
        f"- Pair matching cutoff: **{cutoff:.4f}** plus **{FIXED_MIN_INLIERS}** RANSAC inliers",
        f"- Replicated repeated-stroke pairs: **{len(strong)}**",
        f"- Decision: **{decision}**",
        "",
        "| sails | original inliers | original fraction | passing variants/4 |",
        "|:---|---:|---:|---:|",
    ]
    for idx,(i,j) in enumerate(itertools.combinations(range(1,6),2)):
        original=per_variant["original"][idx]
        lines.append(f"| {i}–{j} | {original['inliers']} | {original['inlier_fraction']:.3f} | {matched_count[f'{i}-{j}']}/4 |")
    lines += ["","## Interpretation",""]
    if not supported:
        lines.append("Control or detector failure: this result is not interpretable. Repair Stage 120 rather than promoting/retiring anything.")
    elif promoted:
        lines.append("One or more sail pairs have repeated interior stroke fingerprints after affine matching and lossy replication. Confirm the specific pair independently before semantic inference.")
    else:
        lines.append("No replicated, affine-compatible identical pen-stroke template among the five sails under calibrated controls. Retire *direct graphic duplication only*; do not infer that sail symbols are meaningless.")
    lines += ["","No keys, mnemonic words, secret candidates, or wallet operations were generated or evaluated.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"experiment_id":"A11-EXP-120","controls_pass":controls["controls_pass"],
                      "detectors_pass":detectors_pass,
                      "strong_pairs":len(strong),"decision":decision}))

if __name__=="__main__":
    main()
