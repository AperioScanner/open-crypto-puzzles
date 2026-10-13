#!/usr/bin/env python3
"""Stage 123: image-only cross-region identical pencil-stroke patch reuse.

Question: do any 64x64 texture patches appear to have been duplicated between
three separate semantic regions (skyline, left foreground, right pier/boats)?
This is NOT Stage 120, which checked the *five small sails against each other*;
within-region comparisons and whole-sail matching are explicitly excluded.

A strictly fixed 32px search grid, 64px windows, original+3 lossy variants,
copy/independent-drawing synthetic controls, and very high full-resolution
correlation+IoU gates prevent generic similar pencil hatching from being called
intentional duplication. A match would be only a structural lead, not a key.
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
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage123-cross-region-stroke-reuse"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"

# Fixed 64px patch grid, no image-dependent re-selection or pixel-phase tuning.
REGIONS={
    "skyline":(230,32,1595,311),
    "water_largeboat":(80,310,928,1025),
    "pier_smallboats":(930,365,1595,890),
}
PATCH=64
STRIDE=32
INK_THR=175
MIN_INK=.07
MAX_INK=.80
THUMB=16
PAIR_POOL=60
HIGH_CORR_ORIGINAL=.95
HIGH_CORR_LOSSY=.91
MIN_INK_IOU=.82
VARIANTS=("original","jpeg85","jpeg70","down75_up")

def descriptor(p):
    ink=(p<INK_THR).astype(np.float32)
    occupancy=float(np.mean(ink))
    if not MIN_INK<=occupancy<=MAX_INK:
        return None
    small=cv2.resize(ink,(THUMB,THUMB),interpolation=cv2.INTER_AREA).ravel()
    sig=float(np.std(small))
    if sig<.065:
        return None
    return ((small-small.mean())/(sig+1e-9)).astype(np.float32)

def indexed_patches(image):
    h,w=image.shape
    out={}
    for name,(x0,y0,x1,y1) in REGIONS.items():
        rows=[]
        for y in range(y0,min(y1,h)-PATCH+1,STRIDE):
            for x in range(x0,min(x1,w)-PATCH+1,STRIDE):
                p=image[y:y+PATCH,x:x+PATCH]
                d=descriptor(p)
                if d is not None:
                    rows.append(((x,y),d))
        out[name]=rows
    return out

def cross_candidates(gray):
    rows=indexed_patches(gray)
    pairs=[]
    for (ra,a),(rb,b) in itertools.combinations(rows.items(),2):
        if not a or not b:
            continue
        A=np.array([v for _,v in a],np.float32)
        B=np.array([v for _,v in b],np.float32)
        matrix=(A@B.T)/(THUMB*THUMB)
        count=min(PAIR_POOL,matrix.size)
        flat=matrix.ravel()
        ix=np.argpartition(flat,-count)[-count:]
        for idx in sorted(ix,key=lambda j:float(flat[j]),reverse=True):
            i,j=np.unravel_index(int(idx),matrix.shape)
            x1,y1=a[i][0];x2,y2=b[j][0]
            if np.hypot(x1-x2,y1-y2)<128:
                continue
            pairs.append({"regions":[ra,rb],"at":[[x1,y1],[x2,y2]],
                          "thumbnail_corr":float(matrix[i,j])})
    pairs.sort(key=lambda r:r["thumbnail_corr"],reverse=True)
    # Dedup identical exact windows across coarse searches.
    chosen=[];seen=set()
    for row in pairs:
        k=tuple(map(tuple,row["at"]))
        if k not in seen:
            chosen.append(row)
            seen.add(k)
    return rows,chosen

def score_pair(image,pts):
    (x1,y1),(x2,y2)=pts
    a=image[y1:y1+PATCH,x1:x1+PATCH]
    b=image[y2:y2+PATCH,x2:x2+PATCH]
    if a.shape!=(PATCH,PATCH) or b.shape!=(PATCH,PATCH):
        raise ValueError("invalid grid crop")
    af=a.astype(float).ravel();bf=b.astype(float).ravel()
    denom=float(np.linalg.norm(af-af.mean())*np.linalg.norm(bf-bf.mean()))
    corr=float(np.dot(af-af.mean(),bf-bf.mean())/denom) if denom>1e-9 else 0.
    m1=a<INK_THR;m2=b<INK_THR
    union=int(np.logical_or(m1,m2).sum())
    iou=float(np.logical_and(m1,m2).sum()/union) if union else 0.
    return {"correlation":round(corr,6),"ink_iou":round(iou,6),
            "ink_fractions":[round(float(m1.mean()),4),round(float(m2.mean()),4)]}

def replicate(p,all_variants):
    scores={name:score_pair(all_variants[name],p["at"]) for name in VARIANTS}
    passed=bool(
        scores["original"]["correlation"]>=HIGH_CORR_ORIGINAL
        and all(scores[v]["correlation"]>=HIGH_CORR_LOSSY for v in VARIANTS[1:])
        and all(scores[v]["ink_iou"]>=MIN_INK_IOU for v in VARIANTS)
    )
    return {"regions":p["regions"],"at":p["at"],
            "coarse_corr":round(p["thumbnail_corr"],6),
            "scores":scores,"replicated":passed}

def examine(img,store_all=False):
    rows,candidates=cross_candidates(img)
    versions=variants(img)
    checks=[replicate(p,versions) for p in candidates]
    hit=[x for x in checks if x["replicated"]]
    return {
        "eligible_grid_windows":{k:len(v) for k,v in rows.items()},
        "pairs_considered":len(checks),
        "replicated_pair_count":len(hit),
        "replicated_pairs":hit[:20],
        "top_candidates":checks[:20] if store_all else checks[:3],
    }

def make_stroke_patch(seed):
    rng=np.random.default_rng(seed)
    im=np.full((PATCH,PATCH),255,np.uint8)
    for _ in range(17):
        x1,y1=(int(x) for x in rng.integers(7,PATCH-7,size=2))
        x2,y2=(int(x) for x in rng.integers(7,PATCH-7,size=2))
        cv2.line(im,(x1,y1),(x2,y2),0,int(rng.integers(1,3)),cv2.LINE_AA)
    return im

def make_control(copy):
    img=np.full((1105,1600),255,np.uint8)
    # Exact start points on different fixed grids, not inside the sail cluster.
    sites=((262,64),(112,342))
    p1=make_stroke_patch(123)
    p2=p1.copy() if copy else make_stroke_patch(456)
    for (x,y),p in zip(sites,(p1,p2)):
        img[y:y+PATCH,x:x+PATCH]=p
    return img

def main():
    checksum=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if checksum!=SHA:
        raise SystemExit("Unexpected canonical PNG SHA256")
    gray=np.array(Image.open(SOURCE).convert("L"))
    if gray.shape!=(1105,1600):
        raise SystemExit("Unexpected canonical pixel dimensions")

    pos=examine(make_control(copy=True))
    neg=examine(make_control(copy=False))
    controls_pass=bool(
        pos["replicated_pair_count"]>0
        and neg["replicated_pair_count"]==0
        and pos["eligible_grid_windows"]["skyline"]>0
        and pos["eligible_grid_windows"]["water_largeboat"]>0
    )
    real=examine(gray,store_all=True)
    covered=all(n>=15 for n in real["eligible_grid_windows"].values())
    decision=("CONTROL_FAILURE" if not controls_pass else
              "INSUFFICIENT_REGION_COVERAGE" if not covered else
              "CROSS_REGION_TEMPLATE_MATCH" if real["replicated_pair_count"] else
              "NO_FIXED_GRID_CROSS_REGION_COPY")
    result={
        "experiment_id":"A11-EXP-123",
        "date":"2026-10-13",
        "hypothesis":"an actual near-identical pencil motif may have been copied between different visible scene layers (skyline, large boat/water, small-boat pier)",
        "evidence":"Pencil hatch marks occur in skyline, foreground water and pier, but exact cross-layer raster duplication has not been tested.",
        "scope":"nonoverlapping semantic regions, original 64x64 patches on fixed 32px grid, strict cross-region comparisons only; no rotated/scaled/sub-grid copies tested",
        "sha256":checksum,
        "thresholds":{"window":PATCH,"stride":STRIDE,"occupancy":[MIN_INK,MAX_INK],
             "min_original_corr":HIGH_CORR_ORIGINAL,"min_lossy_corr":HIGH_CORR_LOSSY,
             "min_ink_iou":MIN_INK_IOU,"candidate_pool_per_region_pair":PAIR_POOL},
        "control_copy":pos,"control_independent":neg,
        "controls_pass":controls_pass,
        "real":real,"coverage_pass":covered,"decision":decision,
        "promotion_rule":"synthetic copied-patch positive and separately drawn negative must pass; each region has >=15 eligible patches; a cross-region pair must clear full-resolution corr and IoU in all four variants",
        "interpretation_guard":"No candidate private key or code constructed. A visual duplication would require manual confirmation and a second scale/grid before any intentional-clue inference.",
        "safety_guard":"Reads only a canonical public picture. No wallet or mnemonic operations.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=[
        "# Stage 123 — cross-region reused-pencil-patch audit",
        "",
        f"- Canonical SHA256: **{checksum==SHA}**",
        f"- Copy/independent-drawing controls: **{controls_pass}**",
        f"- Positive copied-patch hits: **{pos['replicated_pair_count']}**",
        f"- Negative independent-patch hits: **{neg['replicated_pair_count']}**",
        f"- Eligible real patches: **{real['eligible_grid_windows']}**",
        f"- Compared candidate pairs: **{real['pairs_considered']}**",
        f"- Cross-region replicated pairs: **{real['replicated_pair_count']}**",
        f"- Decision: **{decision}**",
        "",
        "## Top five original-scene candidates",
        "",
        "| regions | positions | original correlation | JPEG70 correlation | replicated |",
        "|:---|:---|---:|---:|:---:|",
    ]
    for x in real["top_candidates"][:5]:
        md.append(f"| {' / '.join(x['regions'])} | {x['at']} | {x['scores']['original']['correlation']:.3f} | {x['scores']['jpeg70']['correlation']:.3f} | {x['replicated']} |")
    md+=["","## Interpretation",""]
    if not controls_pass:
        md.append("Control failure; repair Stage 123 under same number. No real conclusion.")
    elif not covered:
        md.append("The image regions lack sufficient eligible drawn patches for this fixed grid; do not interpret a negative.")
    elif real["replicated_pair_count"]:
        md.append("At least one high-confidence cross-region repeated raster motif survived re-encoding. Confirm that exact location visually and with an independent grid/patch scale before drawing any design conclusion.")
    else:
        md.append("No exact cross-region repeated 64px stroke template meets this strict grid and lossy-consistency gate. This does not exclude freehand semantic repetition, rotated copies, or other visual clues.")
    md+=["","No mnemonic, key, candidate or wallet access was generated or used.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"experiment_id":"A11-EXP-123","controls_pass":controls_pass,
        "eligible":real["eligible_grid_windows"],"repeats":real["replicated_pair_count"],
        "decision":decision}))

if __name__=="__main__":
    main()
