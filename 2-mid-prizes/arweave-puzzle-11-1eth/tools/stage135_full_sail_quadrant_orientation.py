#!/usr/bin/env python3
"""A11-EXP-135 — location-vs-stroke-direction in the now-complete large sail.

The corrected Stage133 source polygon yielded 76-90 stable signed diagonal
strokes; Stage134's calibrated text-like-component heuristic did not promote
a multi-family visual pattern. This distinct image-only test asks if diagonal
orientations are organized by visible top/bottom and left/right sail sectors.

This is a statistical STRUCTURAL test, NOT transcription, BIP39, raw file bit
analysis, key derivation, or Ethereum account access. Ordered target strokes
are deliberately never stored. Four quadrant aggregates only.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage133_corrected_full_sail_strokes import full_sail_roi
from stage94_large_sail_stroke_carrier import track_across_thresholds

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage135-full-sail-quadrant-orientation"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
CELLS=("upper_left","upper_right","lower_left","lower_right")

# Stable physical source geometry, inherited EXACTLY from Stage132's polygon.
APEX=(242.,398.)
LEFT_FOOT=(56.,758.)
RIGHT_FOOT=(512.,760.)
BASE_CENTER=((LEFT_FOOT[0]+RIGHT_FOOT[0])/2,(LEFT_FOOT[1]+RIGHT_FOOT[1])/2)
MID_Y=(APEX[1]+BASE_CENTER[1])/2
SEAM_MARGIN_PX=8.
MIDLINE_MARGIN_PX=12.

MIN_CLASSIFIABLE=40
MIN_PER_CELL=4
MIN_CLASSIFIED_FRACTION=.55
PERMUTATIONS=20000
SEED=135
SIGN_P_THRESHOLD=.01
EFFECT_V_THRESHOLD=.35
MIN_MAJORITY_MARGIN=.10

def sector(global_x,global_y):
    dy=BASE_CENTER[1]-APEX[1]
    t=(global_y-APEX[1])/dy
    spine=APEX[0]+t*(BASE_CENTER[0]-APEX[0])
    if abs(global_x-spine)<SEAM_MARGIN_PX: return None
    if abs(global_y-MID_Y)<MIDLINE_MARGIN_PX: return None
    upper=global_y<MID_Y
    left=global_x<spine
    return (0 if upper else 2)+(0 if left else 1)

def quadrant_matrix(tracks,box):
    x0,y0,_,_=box
    table=np.zeros((4,2),np.int64)
    classifiable=0
    edge_excluded=0
    for tr in tracks:
        a=float(tr["angle"])
        if not 18<=abs(a)<=86:continue
        classifiable+=1
        gx=x0+float(tr["mx"])
        gy=y0+float(tr["my"])
        cell=sector(gx,gy)
        if cell is None:
            edge_excluded+=1
            continue
        # Positive/negative angle only; no serial ordering saved.
        table[cell,0 if a>0 else 1]+=1
    return table, classifiable, edge_excluded

def statistic(table):
    n=int(table.sum())
    if n==0:return 0.
    row=table.sum(axis=1,keepdims=True).astype(float)
    col=table.sum(axis=0,keepdims=True).astype(float)
    expected=row@col/max(1,n)
    sel=expected>0
    return float(np.sum(((table-expected)**2/np.maximum(expected,1e-12))[sel]))

def pvalue(table):
    """Fixed-total permutation within measured quadrant occupancies."""
    n=int(table.sum())
    sizes=table.sum(axis=1).astype(int)
    ones=int(table[:,0].sum())
    label=np.r_[np.ones(ones,np.uint8),np.zeros(n-ones,np.uint8)]
    index=np.repeat(np.arange(4),sizes)
    rng=np.random.default_rng(SEED)
    observed=statistic(table)
    hits=0
    for _ in range(PERMUTATIONS):
        signs=rng.permutation(label)
        cnt=np.bincount(index,weights=signs,minlength=4).astype(np.int64)
        trial=np.column_stack([cnt,sizes-cnt])
        if statistic(trial)>=observed-1e-12:
            hits+=1
    return (1+hits)/(1+PERMUTATIONS)

def summarize(table):
    n=int(table.sum())
    totals=table.sum(axis=1)
    proportions=[float(table[i,0]/totals[i]) if totals[i] else None for i in range(4)]
    majority=[
        "POS" if x is not None and x>=.5+MIN_MAJORITY_MARGIN else
        "NEG" if x is not None and x<=.5-MIN_MAJORITY_MARGIN else
        "AMBIGUOUS" for x in proportions
    ]
    chisq=statistic(table)
    effect=float(math.sqrt(chisq/n)) if n else 0.0
    return {
        "counts_by_quadrant":{CELLS[i]:[int(z) for z in table[i]] for i in range(4)},
        "quadrant_total":{CELLS[i]:int(totals[i]) for i in range(4)},
        "positive_fractions":{CELLS[i]:(round(proportions[i],6) if proportions[i] is not None else None)
                              for i in range(4)},
        "majority_by_quadrant":{CELLS[i]:majority[i] for i in range(4)},
        "chi_square":round(chisq,6),
        "cramers_v":round(effect,6),
        "fixed_conditional_permutation_p":round(pvalue(table),8) if n else None
    }

def synthetic_controls():
    # 4 predeclared sector populations, 20 tracks per group.
    # Strong patterned positive, exact same-count unpatterned negative.
    positive=np.array([[18,2],[2,18],[2,18],[18,2]],np.int64)
    negative=np.array([[10,10],[10,10],[10,10],[10,10]],np.int64)
    p=summarize(positive);n=summarize(negative)
    pattern=[p["majority_by_quadrant"][x] for x in CELLS]
    passed=bool(
        p["fixed_conditional_permutation_p"]<=SIGN_P_THRESHOLD
        and p["cramers_v"]>=EFFECT_V_THRESHOLD
        and pattern==["POS","NEG","NEG","POS"]
        and n["fixed_conditional_permutation_p"]>.05
        and n["cramers_v"]<.10
        and all(n["majority_by_quadrant"][x]=="AMBIGUOUS" for x in CELLS)
    )
    return {"passed":passed,"structured_positive":p,"balanced_negative":n}

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:raise SystemExit("canonical source SHA changed")
    original=np.array(Image.open(SOURCE).convert("L"))
    if original.shape!=(1105,1600):raise SystemExit("canonical dimensions changed")
    controls=synthetic_controls()
    vv=variants(original)
    real={}
    major=[]
    adequate=[]
    for form in FORMATS:
        patch,mask,meta=full_sail_roi(vv[form])
        tracks=track_across_thresholds(patch,mask)
        table,classified,excluded=quadrant_matrix(tracks,meta["box"])
        diag=summarize(table)
        sufficient=bool(
            classified>=MIN_CLASSIFIABLE
            and table.sum()/max(1,classified)>=MIN_CLASSIFIED_FRACTION
            and np.all(table.sum(axis=1)>=MIN_PER_CELL)
        )
        strong=bool(
            sufficient and diag["fixed_conditional_permutation_p"]<=SIGN_P_THRESHOLD
            and diag["cramers_v"]>=EFFECT_V_THRESHOLD
            and all(diag["majority_by_quadrant"][x]!="AMBIGUOUS" for x in CELLS)
            and len(set(diag["majority_by_quadrant"].values()))==2
        )
        real[form]={
            "classifiable_tracks":classified,
            "near_seam_or_midline_excluded":excluded,
            "aggregate_count":int(table.sum()),
            "adequate":sufficient,
            "passes_strong_gate":strong,
            **diag
        }
        adequate.append(sufficient)
        major.append(tuple(diag["majority_by_quadrant"][x] for x in CELLS))
    replicated=bool(all(adequate)
                    and all(real[v]["passes_strong_gate"] for v in FORMATS)
                    and len(set(major))==1)
    decision=(
        "CONTROL_FAILURE" if not controls["passed"] else
        "INSUFFICIENT_QUADRANT_SOURCE_COVERAGE" if not all(adequate) else
        "REPLICATED_SPATIAL_STROKE_ASSOCIATION_NEEDS_VISUAL_REVIEW" if replicated else
        "NO_REPLICATED_SPATIAL_STROKE_ASSOCIATION"
    )
    result={
        "experiment_id":"A11-EXP-135",
        "hypothesis":"the now fully visible large sail's diagonal stroke signs are organized by top/bottom × left/right geometric sectors, not randomly interleaved",
        "reason":"Stage132 proved an ROI defect; Stage133 recovered 76-90 full-sail classifiable strokes, mixed signed orientations; their spatial grouping was not tested in Stage94.",
        "scope":"fixed Stage132 triangle and Stage94 full-size stroke detector, four sectors; conditional sign-label permutation; original and three lossy variants; no ordered sign sequence persisted",
        "canonical_sha256":digest,
        "quadrant_definition":{"apex":APEX,"left_foot":LEFT_FOOT,"right_foot":RIGHT_FOOT,
            "seam_margin_px":SEAM_MARGIN_PX,"horizontal_midline_margin_px":MIDLINE_MARGIN_PX},
        "thresholds":{"min_tracks":MIN_CLASSIFIABLE,"min_per_quadrant":MIN_PER_CELL,
            "min_sector_retained_fraction":MIN_CLASSIFIED_FRACTION,
            "max_permutation_p":SIGN_P_THRESHOLD,"min_cramers_v":EFFECT_V_THRESHOLD,
            "min_majority_margin":MIN_MAJORITY_MARGIN,"permutations":PERMUTATIONS},
        "synthetic_controls":controls,
        "by_variant":real,
        "replicated_majorities":len(set(major))==1,
        "promoted":bool(controls["passed"] and replicated),
        "decision":decision,
        "limit":"Exploratory structural association in one manually fixed four-sector sail geometry; p value conditions on observed stroke locations but DOES NOT adjust for all historically explored puzzle hypotheses. Association cannot establish intent, decoding or secret data.",
        "safety":"No ordered target strokes saved; no private key, mnemonic, address, wallet or external source used."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
        "# Stage 135 — full-sail quadrant versus hatch-direction association","",
        f"- Canonical image SHA verified: **{digest==SHA}**",
        f"- Synthetic patterned-vs-unpatterned controls: **{controls['passed']}**",
        f"- Source coverage across four formats: **{sum(adequate)}/4**",
        f"- Strong spatial associations: **{sum(real[v]['passes_strong_gate'] for v in FORMATS)}/4**",
        f"- Replicated quadrant majority labels: **{len(set(major))==1}**",
        f"- Decision: **{decision}**","",
        "| variant | detected sign tracks | retained in 4 sectors | association p | effect V |",
        "|---|---:|---:|---:|---:|",
    ]
    for v in FORMATS:
        r=real[v]
        lines.append(f"| {v} | {r['classifiable_tracks']} | {r['aggregate_count']} | {r['fixed_conditional_permutation_p']} | {r['cramers_v']:.3f} |")
    lines+=["","## Interpretation",""]
    if not controls["passed"]:
        lines.append("Synthetic controls failed; repair SAME Stage135. No conclusion.")
    elif not all(adequate):
        lines.append("Too few sector-specific real strokes. Source-limited; do not claim no pattern.")
    elif replicated:
        lines.append("Quadrant-specific pencil directions are reproducible and statistically associated. Requires independent visual check; **not** an encoding or source of key material.")
    else:
        lines.append("No source-robust strong 2×2 quadrant association in the complete sail. Retire ONLY this spatial aggregation hypothesis, not other picture clues.")
    lines+=["","No secrets, wallets, keys or mnemonic words were generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":135,"controls":controls["passed"],
        "adequate":sum(adequate),"strong":sum(real[v]["passes_strong_gate"] for v in FORMATS),
        "decision":decision}))

if __name__=="__main__":
    main()
