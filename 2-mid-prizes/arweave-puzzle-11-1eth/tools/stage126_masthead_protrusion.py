#!/usr/bin/env python3
"""Stage 126: tiny masthead extensions above the five true small sails.

A predeclared, image-only secondary-detail audit of the five individual
mastheads. Checks whether thin dark vertical strokes extend above the triangular
sail tip in a stable mixed present/absent pattern. Different from Stage 105's
interior-ray counting, Stage 122's sail-side shading, Stage 124's outline base
offset and Stage 125's outlier comparison. No words, keys or wallets.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage126-masthead-protrusion"
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED_SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"

# True five sail centers and conservative top-of-triangle zones documented
# in Stages 122/124; no source-dependent coordinate optimization.
SITES=(
    ("sail_1",1042,448,98,35),
    ("sail_2",1148,433,99,38),
    ("sail_3",1282,411,103,44),
    ("sail_4",1372,397,101,42),
    ("sail_5",1490,357,106,47),
)
FORMATS=("original","jpeg85","jpeg70","down75_up")
X_JITTER=(-2,0,2)
T0,T1=3,18  # fixed zone above the synthetic triangular apex at top+24
INK_CUTOFF=175
BIN_MIN_ROWS=10
EDGE_MIN_ROWS=9
MIN_CONTIGUOUS=8
ABSENCE_MAX_ROWS=3

def longest_run(flags):
    best=cur=0
    for x in flags:
        cur=(cur+1 if x else 0)
        best=max(best,cur)
    return best

def inspect(img,site,dx):
    _,cx,top,height,half=site
    x=int(cx+dx)
    y0=int(top+T0); y1=int(top+T1)
    if x-8<0 or x+8>=img.shape[1] or y0<0 or y1>=img.shape[0]:
        return {"classification":"?","reason":"OUT_OF_BOUNDS"}
    # Entire strip is bounded above the visible triangle's apex.
    lines=(img[y0:y1,x-3:x+4]<INK_CUTOFF)
    row_ink=lines.any(axis=1)
    ink_n=int(row_ink.sum())
    longest=int(longest_run(row_ink))
    patch=img[y0-2:y1+2,x-8:x+9]
    edge=cv2.Canny(patch,60,150)
    rows=edge[2:2+y1-y0,4:13].any(axis=1)
    edge_n=int(rows.sum())
    edge_run=int(longest_run(rows))
    positive=(ink_n>=BIN_MIN_ROWS and edge_n>=EDGE_MIN_ROWS
              and longest>=MIN_CONTIGUOUS and edge_run>=MIN_CONTIGUOUS)
    negative=(ink_n<=ABSENCE_MAX_ROWS and edge_n<=ABSENCE_MAX_ROWS)
    label="EXTENDED" if positive else "ABSENT" if negative else "?"
    return {"classification":label,"ink_rows":ink_n,"edge_rows":edge_n,
            "ink_longest_run":longest,"edge_longest_run":edge_run}

def synthetic(site,kind):
    _,cx,top,height,half=site
    img=np.full((1105,1600),255,np.uint8)
    apex=(cx,top+24)
    base_y=top+height-6
    left=(cx-half,base_y)
    right=(cx+half,base_y)
    cv2.line(img,apex,left,0,2,cv2.LINE_AA)
    cv2.line(img,apex,right,0,2,cv2.LINE_AA)
    cv2.line(img,left,right,0,2,cv2.LINE_AA)
    # Distracting pencilled hatches occur INSIDE the sail below its tip.
    rng=np.random.default_rng(12600+cx)
    for z in range(7):
        y=int(rng.integers(top+35,base_y-4))
        t=(y-(top+24))/max(1,height-30)
        px=cx+int(rng.uniform(-half,half)*t)
        cv2.line(img,(px,y),(px+int(rng.integers(-4,5)),y+5),0,1,cv2.LINE_AA)
    if kind=="extension":
        cv2.line(img,(cx,top+1),(cx,top+28),0,2,cv2.LINE_AA)
    elif kind=="side_decoy":
        # Nearby unrelated vertical line must NOT be read as a mast extension.
        cv2.line(img,(cx+13,top+1),(cx+13,top+18),0,2,cv2.LINE_AA)
    elif kind!="absent":
        raise ValueError(kind)
    return img

def controls():
    records=[]
    failures=[]
    for site in SITES:
        for kind in ("extension","absent","side_decoy"):
            all_variants=variants(synthetic(site,kind))
            expected="EXTENDED" if kind=="extension" else "ABSENT"
            for variant in FORMATS:
                for dx in X_JITTER:
                    row=inspect(all_variants[variant],site,dx)
                    ok=row["classification"]==expected
                    record={"site":site[0],"variant":variant,
                            "dx":dx,"control":kind,"expected":expected,
                            "observed":row["classification"],"passed":ok}
                    records.append(record)
                    if not ok:failures.append(record)
    return {"cases":len(records),"passes":len(records)-len(failures),
            "passed":not failures,"failures":failures[:40]}

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=EXPECTED_SHA:
        raise SystemExit("Canonical image SHA mismatch")
    original=np.asarray(Image.open(PNG).convert("L"))
    if original.shape!=(1105,1600):
        raise SystemExit("Wrong image geometry")
    checks=controls()
    all_formats=variants(original)
    site_results=[]
    stable=[]
    for site in SITES:
        observations=[]
        for variant in FORMATS:
            for dx in X_JITTER:
                obs=inspect(all_formats[variant],site,dx)
                observations.append({"format":variant,"dx":dx,**obs})
        c=[v["classification"] for v in observations]
        stable_class=c[0] if len(set(c))==1 and c[0]!="?" else None
        if stable_class is not None:
            stable.append(stable_class)
        site_results.append({"site":site[0],
            "stable_class":stable_class,"observations":observations})
    mixed=(len(stable)>=4 and len(set(stable))==2)
    decision=("CONTROL_FAILURE" if not checks["passed"] else
              "MIXED_MASTHEAD_EXTENSIONS" if mixed else
              "UNIFORM_MASTHEAD_STATE" if len(stable)>=4 and len(set(stable))==1 else
              "INCONCLUSIVE_MASTHEAD_SOURCE_COVERAGE")
    result={
        "experiment_id":"A11-EXP-126",
        "hypothesis":"Visible tiny mast extensions above the five triangular sail tips might create a mixed present/absent sequence independent from shading/widths/ray counts.",
        "scope":"5 predeclared small-sail masthead windows x ±2px; RGB-to-grayscale; original/JPEG85/JPEG70/resize; no secret extraction",
        "canonical_sha256":digest,
        "sites_predeclared":[list(s) for s in SITES],
        "apex_strip_relative_y":[T0,T1],
        "gates":{"binary_ink_rows_min":BIN_MIN_ROWS,
                 "edge_rows_min":EDGE_MIN_ROWS,"contiguous_min":MIN_CONTIGUOUS,
                 "absence_max_rows":ABSENCE_MAX_ROWS},
        "controls":checks,
        "sites":site_results,
        "stable_site_count":len(stable),
        "mixed_states":mixed,
        "decision":decision,
        "coverage_guard":"Calibrated on straight-line synthetic drawings with same apex/height. An ambiguous original masthead remains inconclusive; unobserved smaller flags or separate glyphs not covered.",
        "safety_guard":"Visual measurements only. No mnemonic/key/address candidates, wallet calls or transactions.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    report=[
        "# Stage 126 — tiny masthead extension audit",
        "",
        f"- Canonical image SHA verified: **{digest==EXPECTED_SHA}**",
        f"- Synthetic positive/negative/side-decoy controls: **{checks['passes']}/{checks['cases']}**",
        f"- Stable real masthead classifications: **{len(stable)}/5**",
        f"- Both states present: **{mixed}**",
        f"- Decision: **{decision}**",
        "",
        "| small sail | stable extension state |",
        "|---:|:---:|",
    ]
    for i,s in enumerate(site_results,1):
        report.append(f"| {i} | {s['stable_class'] or '?'} |")
    report+=["","## Interpretation",""]
    if not checks["passed"]:
        report.append("Detector failed synthetic controls. Do not interpret real results; fix Stage 126.")
    elif mixed:
        report.append("A binary-like mixed marker pattern survived prescribed controls; requires independent manual verification and cannot be read as a secret.")
    elif decision=="UNIFORM_MASTHEAD_STATE":
        report.append("A uniform masthead feature is ordinary illustration structure, not a nontrivial five-item code.")
    else:
        report.append("These fixed masthead windows do not identify a reproducible mixed feature with sufficient coverage; do not falsely call all physical masthead markings absent.")
    report.append("\nNo secret material handled.\n")
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":126,"controls_pass":checks["passed"],
         "stable":len(stable),"decision":decision}))
if __name__=="__main__":
    main()
