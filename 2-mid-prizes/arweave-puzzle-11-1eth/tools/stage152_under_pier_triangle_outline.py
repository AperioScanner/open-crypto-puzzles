#!/usr/bin/env python3
"""A11-EXP-152 — does the open under-pier contour form a CLOSED triangle?

Stage151 found the candidate under the right-hand pier has 15.4% interior dark
pen stroke coverage, unlike all five genuine small sails (~76–85%). The
candidate might still be an UNHATCHED triangular motif rather than a dock
support. This tests ONLY the three OUTLINE SIDES using the original fixed
Stage151 six source triangles, never fitting new vertices or patch offsets.

A controlled closed triangle, missing-base V/brace and solitary vertical mast
are evaluated at all six affine-normalized geometry sites × all four variants
(72 known-answer measurements). Five true small sail outlines serve as real
source controls; at least four must be stably recovered before candidate claim.

No wordlist, BIP39, private key, wallet, address, guessed code or off-image data.
"""
from __future__ import annotations

import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

from stage112_corrected_sail_width_progression import variants
from stage151_under_pier_triangle import (
    OBJECTS,KNOWN,TARGET,CANON,canonicalize,SHA
)

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR=ROOT/"analysis"/"runs"/"stage151-under-pier-triangle"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage152-under-pier-closed-outline"
OUT.mkdir(parents=True,exist_ok=True)
FORMATS=("original","jpeg85","jpeg70","down75_up")
LINE_THICKNESS=3
SOURCE_DARK_THRESHOLD=185
SAMPLE_RADIUS=4
SAMPLE_COUNT=45
SAMPLE_T_MIN=.17
SAMPLE_T_MAX=.83
MIN_PER_EDGE_SUPPORT=.58
MIN_KNOWN_SAILS=4
EXPECTED_CONTROL_CASES=3*6*4
EDGES=(("left",(64,0),(0,127)),
       ("right",(64,0),(127,127)),
       ("base",(0,127),(127,127)))

def edge_ink_fraction(rectified,start,end):
    a=np.asarray(start,dtype=float)
    b=np.asarray(end,dtype=float)
    h,w=rectified.shape
    found=0
    for t in np.linspace(SAMPLE_T_MIN,SAMPLE_T_MAX,SAMPLE_COUNT):
        x,y=np.round((1-t)*a+t*b).astype(int)
        xlo=max(0,x-SAMPLE_RADIUS);xhi=min(w,x+SAMPLE_RADIUS+1)
        ylo=max(0,y-SAMPLE_RADIUS);yhi=min(h,y+SAMPLE_RADIUS+1)
        patch=rectified[ylo:yhi,xlo:xhi]
        found+=int(bool(patch.size) and bool(np.any(patch<SOURCE_DARK_THRESHOLD)))
    return float(found/SAMPLE_COUNT)

def measure(original,poly):
    normalized=canonicalize(original,poly)
    edges={name:round(edge_ink_fraction(normalized,a,b),6)
           for name,a,b in EDGES}
    closed=all(s>=MIN_PER_EDGE_SUPPORT for s in edges.values())
    return {"edge_dark_support":edges,"closed_three_edge_triangle":bool(closed)}

def draw_fixture(kind):
    source=np.full((128,128),255,np.uint8)
    if kind in ("full_three_edges","V_without_base"):
        for _,a,b in EDGES[:3 if kind=="full_three_edges" else 2]:
            cv2.line(source,a,b,0,LINE_THICKNESS,cv2.LINE_AA)
    elif kind=="vertical_mast_only":
        cv2.line(source,(64,0),(64,127),0,LINE_THICKNESS,cv2.LINE_AA)
    else:
        raise ValueError(kind)
    return source

def synthetic_scene(kind):
    a=np.full((1105,1600),255,np.uint8)
    rect=draw_fixture(kind)
    for points in OBJECTS.values():
        affine=cv2.getAffineTransform(CANON,np.float32(points))
        target=cv2.warpAffine(rect,affine,(1600,1105),
          flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
        np.minimum(a,target,out=a)
    return a

def calibration():
    examples={}
    valid=0;total=0
    for kind in ("full_three_edges","V_without_base","vertical_mast_only"):
        ref=variants(synthetic_scene(kind))
        expected=(kind=="full_three_edges")
        examples[kind]={}
        for form in FORMATS:
            observations={}
            for name,coords in OBJECTS.items():
                read=measure(ref[form],coords)
                ok=bool(read["closed_three_edge_triangle"]==expected)
                observations[name]={"pass":ok,"sides":read["edge_dark_support"]}
                total+=1;valid+=int(ok)
            examples[kind][form]=observations
    return {"pass":bool(total==EXPECTED_CONTROL_CASES and valid==total),
            "passed_cases":valid,"cases":total,"fixtures":examples}

def stage151_source_ok():
    prior=json.loads(PRIOR.read_text())
    return bool(prior["original_sha256"]==SHA
       and prior["controls"]["pass"]
       and prior["positive_real_sails_stable"]>=4)

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Canonical PNG checksum changed")
    source=np.asarray(Image.open(PNG).convert("L"))
    if source.shape!=(1105,1600):raise RuntimeError("Image dimensions invalid")
    fixture=calibration()
    previous=stage151_source_ok()
    observations={v:{name:measure(im,pts) for name,pts in OBJECTS.items()}
          for v,im in variants(source).items() if v in FORMATS}
    real_sails={name:all(observations[v][name]["closed_three_edge_triangle"]
                   for v in FORMATS) for name in KNOWN}
    known=sum(real_sails.values())
    candidate=all(observations[v][TARGET]["closed_three_edge_triangle"]
                  for v in FORMATS)
    decision=("CONTROL_FAILURE" if not fixture["pass"] else
              "STAGE151_SOURCE_REPRODUCTION_FAILURE" if not previous else
              "INSUFFICIENT_KNOWN_SAIL_OUTLINE_RECALL" if known<MIN_KNOWN_SAILS else
              "UNDER_PIER_CLOSED_TRIANGLE_WARRANTS_VISUAL_REVIEW" if candidate else
              "UNDER_PIER_NO_FULL_THREE_SIDED_SAIL_OUTLINE")
    result={
        "experiment_id":"A11-EXP-152",
        "hypothesis":"the white triangle beneath the right-hand pier could have a complete but unhatched three-sided triangular outline, different from confirmed dense sail panels",
        "motivation":"Stage151 compared interior hatch density and rejected a densely filled sixth sail; it did NOT independently test whether the candidate's THREE edges close, unlike an open mooring brace.",
        "scope":"Stage151 immutable 5 real small sail triangles + 1 under-pier candidate polygon, affine normalization to 128x128; line support along the fixed three edges with 45 sample locations/edge and +/-4px local source tolerance, 4 source/reencoded formats",
        "sha256":digest,
        "thresholds":{"max_distance_px":SAMPLE_RADIUS,"dark_gray_less_than":SOURCE_DARK_THRESHOLD,
                      "min_per_edge_detected_fraction":MIN_PER_EDGE_SUPPORT,
                      "samples_per_side":SAMPLE_COUNT,
                      "min_real_sail_positive_outlines":MIN_KNOWN_SAILS},
        "control":fixture,
        "stage151_source_chain_valid":previous,
        "real_five_sail_outline_recovery":real_sails,
        "real_sail_outlines_stable":known,
        "under_pier_full_outline_four_formats":candidate,
        "by_variant":observations,
        "decision":decision,
        "scope_limit":"One visually preselected triangle, fixed hand-annotated vertices; source line crossings may trigger edge ink even if their semantics differ. A complete outline alone does NOT establish an extra sail or steganography. A negative addresses only that fixed triangle outline geometry.",
        "safety":"No cryptographic key material, BIP39, seed phrases, wallets, addresses, checking or off-image research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    report=[
        "# Stage152 — is the under-pier outline a CLOSED triangle?","",
        f"- Source hash verified: **{digest==SHA}**",
        f"- Closed / open-V / mast-only synthetic controls: **{fixture['passed_cases']}/{fixture['cases']}**",
        f"- Stage151 original image source chain verified: **{previous}**",
        f"- Five real sail outlines reproduced in all four variants: **{known}/5**",
        f"- Under-pier outline closed in 4/4: **{candidate}**",
        f"- Decision: **{decision}**","",
        "| region | original left edge | right edge | base edge |",
        "|---|---:|---:|---:|"
    ]
    for name in OBJECTS:
        edges=observations["original"][name]["edge_dark_support"]
        report.append(f"| {name} | {edges['left']:.2f} | {edges['right']:.2f} | {edges['base']:.2f} |")
    report+=["","## Interpretation",""]
    if not fixture["pass"] or not previous or known<MIN_KNOWN_SAILS:
        report.append("Controls/source validation failed: repair Stage152 before interpreting original.")
    elif candidate:
        report.append("All three source outline edges meet the calibrated closure test, though no dense panel is present. A manually inspected open-structure/sail distinction is still required; no code is inferred.")
    else:
        report.append("The under-pier contour does not reconstruct a robust, fully three-sided sail-like triangle at the preselected anchors; it is consistent with open crossing dock ropes/struts. No independent sixth sail confirmed.")
    report+=["","No key, mnemonic or wallet actions.",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":152,"controls":fixture["pass"],
      "prior":previous,"known":known,"candidate":candidate,
      "decision":decision}))

if __name__=="__main__":main()
