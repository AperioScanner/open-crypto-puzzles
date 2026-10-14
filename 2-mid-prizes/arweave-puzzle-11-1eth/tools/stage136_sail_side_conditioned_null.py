#!/usr/bin/env python3
"""A11-EXP-136 — test whether Stage135's strong association is ordinary V shading.

Stage135 found a replicated left-NEG / right-POS large-sail pencil hatch split,
with nearly the SAME left/right polarity at both vertical levels. Its previous
fully exchangeable sign-permutation null ignores the drawing convention that
lines on opposite sides of a triangle naturally lean in opposite directions.

We therefore condition on LEFT/RIGHT panel and test only incremental UPPER vs
LOWER orientation changes, with an EXACT joint hypergeometric permutation null.
No thresholds, source ROIs, stroke detector or sign counts are tuned to outcome.

Synthetic fixed counts contrast natural V-shading (negative control) against
deliberately reversing hatch signs vertically (positive control). Recompute the
four real aggregate count tables directly from original source pixels to verify
Stage135's saved aggregates before a decision.

No ordered strokes are persisted. No key, BIP39, address or wallet activity.
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
from stage135_full_sail_quadrant_orientation import (
    quadrant_matrix, CELLS, FORMATS
)

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR=ROOT/"analysis"/"runs"/"stage135-full-sail-quadrant-orientation"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage136-side-conditioned-sail-null"
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"

# Statistical criteria predeclared before examining any Stage136 output.
P_GATE=.01
MIN_VERTICAL_DELTA=.25
MIN_SOURCE_TRACKS=40
MIN_QUADRANT_TRACKS=4
MIN_VERTICAL_SIDES_WITH_DIFFERENCE=1
STAGES=(("left",0,2),("right",1,3))
EPS=1e-12

def per_side_chisq(top_pos,top_neg,bottom_pos,bottom_neg):
    table=np.array([[top_pos,top_neg],[bottom_pos,bottom_neg]],dtype=np.float64)
    n=float(table.sum())
    if n<=0:return 0.
    row=table.sum(axis=1,keepdims=True)
    col=table.sum(axis=0,keepdims=True)
    expectation=row@col/n
    return float(np.sum(np.where(expectation>0,(table-expectation)**2/
                                 np.maximum(expectation,1e-12),0.)))

def score(table):
    return sum(per_side_chisq(*table[u],*table[l]) for _,u,l in STAGES)

def hypergeom_upper_pos_prob(upper_total,lower_total,total_pos,x):
    n=upper_total+lower_total
    if n==0:return 1.
    if x<0 or x>upper_total or x>total_pos or total_pos-x>lower_total:
        return 0.
    # Conditional on side-specific POS total & upper/lower quadrant sizes.
    return (math.comb(total_pos,x)
            *math.comb(n-total_pos,upper_total-x)
            /math.comb(n,upper_total))

def exact_conditioned_p(table):
    """Exact 2-sided-like Pearson tail, conditioning on each x-side's totals.

    Labels are exchangeable ONLY between upper/lower *within* left and right
    side, unlike Stage135's global permutation. Enumerate all feasible pairs
    of upper POS counts under the independent conditional hypergeometric null.
    """
    table=np.asarray(table,dtype=np.int64)
    obs=float(score(table))
    side_support=[]
    for _,up,lo in STAGES:
        row1=int(table[up].sum())
        row2=int(table[lo].sum())
        ones=int(table[up,0]+table[lo,0])
        lo_x=max(0,ones-row2)
        hi_x=min(row1,ones)
        side=[]
        for x in range(lo_x,hi_x+1):
            top_pos=x; top_neg=row1-x
            bottom_pos=ones-x;bottom_neg=row2-(ones-x)
            prob=hypergeom_upper_pos_prob(row1,row2,ones,x)
            chi=per_side_chisq(top_pos,top_neg,bottom_pos,bottom_neg)
            side.append((x,float(prob),chi))
        side_support.append(side)
    tail=0.
    normalization=0.
    for _,p_left,stat_left in side_support[0]:
        for _,p_right,stat_right in side_support[1]:
            joint=p_left*p_right
            normalization+=joint
            if stat_left+stat_right>=obs-EPS:tail+=joint
    return float(tail/max(normalization,EPS)),int(len(side_support[0])*len(side_support[1]))

def fractions(table):
    a=np.asarray(table,dtype=np.int64)
    return [float(v[0]/max(1,v.sum())) for v in a]

def evaluate(table):
    a=np.asarray(table,dtype=np.int64)
    ps=fractions(a)
    p,total_tables=exact_conditioned_p(a)
    # Index layout UL,UR,LL,LR. Difference POS fraction upper minus lower.
    deltas={"left":round(ps[0]-ps[2],6),"right":round(ps[1]-ps[3],6)}
    n=int(a.sum())
    enough=bool(n>=MIN_SOURCE_TRACKS
                and all(int(a[i].sum())>=MIN_QUADRANT_TRACKS for i in range(4)))
    enough_vertical=sum(abs(d)>=MIN_VERTICAL_DELTA for d in deltas.values())>=MIN_VERTICAL_SIDES_WITH_DIFFERENCE
    strong=bool(enough and p<=P_GATE and enough_vertical)
    return {
        "count_table":{CELLS[i]:[int(x) for x in a[i]] for i in range(4)},
        "side_specific_vertical_delta":deltas,
        "conditional_chi_square":round(score(a),6),
        "exact_side_conditioned_p":round(p,10),
        "conditional_table_count":total_tables,
        "eligible":enough,
        "passes_new_structure_gate":strong
    }

def controls():
    # Negative: naturally mirrored "V" diagonals, constant upper/lower
    # sign preferences on each geometric SIDE.
    natural=np.array([
        [2,18],   # upper-left: slants negative
        [18,2],   # upper-right: slants positive
        [2,18],   # lower-left: same negative convention
        [18,2],   # lower-right: same positive convention
    ],np.int64)
    # Positive: extra coding-like vertical sign reversals within each SIDE.
    vertical=np.array([
        [18,2],  # upper-left positive
        [2,18],  # upper-right negative
        [2,18],  # lower-left negative (reverses)
        [18,2],  # lower-right positive (reverses)
    ],np.int64)
    balanced=np.full((4,2),10,np.int64)
    neg=evaluate(natural)
    pos=evaluate(vertical)
    bal=evaluate(balanced)
    passed=bool(
        neg["exact_side_conditioned_p"]>.05
        and not neg["passes_new_structure_gate"]
        and pos["exact_side_conditioned_p"]<=P_GATE
        and pos["passes_new_structure_gate"]
        and bal["exact_side_conditioned_p"]>.05
        and not bal["passes_new_structure_gate"]
    )
    return {"passed":passed,"natural_v_shading_negative":neg,
            "vertical_reversal_positive":pos,
            "balanced_negative":bal}

def source_aggregate(gray):
    out={}
    for name,img in variants(gray).items():
        if name not in FORMATS:continue
        patch,mask,meta=full_sail_roi(img)
        tracks=track_across_thresholds(patch,mask)
        matrix,classes,excluded=quadrant_matrix(tracks,meta["box"])
        out[name]={"counts":matrix,
                   "classifiable":int(classes),
                   "excluded":int(excluded)}
    return out

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=EXPECTED_SHA:raise SystemExit("Wrong canonical source hash")
    prior=json.loads(PRIOR.read_text())
    if prior["canonical_sha256"]!=digest or not prior["synthetic_controls"]["passed"]:
        raise SystemExit("Stage135 source/control mismatch")
    image=np.array(Image.open(PNG).convert("L"))
    if image.shape!=(1105,1600):raise SystemExit("Unexpected image shape")

    controls_result=controls()
    fresh=source_aggregate(image)
    fidelity=True
    results={}
    for v in FORMATS:
        measured=fresh[v]
        fresh_counts={CELLS[i]:measured["counts"][i].tolist() for i in range(4)}
        prev=prior["by_variant"][v]
        same=bool(fresh_counts==prev["counts_by_quadrant"]
                  and measured["classifiable"]==prev["classifiable_tracks"]
                  and measured["excluded"]==prev["near_seam_or_midline_excluded"])
        fidelity=fidelity and same
        results[v]={**evaluate(measured["counts"]),
                    "prior_source_reproduction_pass":same,
                    "classifiable":measured["classifiable"],
                    "excluded_seam_midline":measured["excluded"]}
    adequate=all(results[v]["eligible"] for v in FORMATS)
    strong=all(results[v]["passes_new_structure_gate"] for v in FORMATS)
    delta_signs={(v,side):
                 (1 if results[v]["side_specific_vertical_delta"][side]>0 else
                  -1 if results[v]["side_specific_vertical_delta"][side]<0 else 0)
                 for v in FORMATS for side,_,_ in STAGES}
    sign_consistency=all(len({delta_signs[v,side] for v in FORMATS})==1
                         for side,_,_ in STAGES)
    replicated=bool(strong and sign_consistency)
    decision=(
        "CONTROL_FAILURE" if not controls_result["passed"] else
        "SOURCE_REPRODUCTION_FAILURE" if not fidelity else
        "INSUFFICIENT_SAIL_SECTOR_COVERAGE" if not adequate else
        "ADDITIONAL_VERTICAL_HATCH_STRUCTURE_REPLICATED" if replicated else
        "SIDE_DEPENDENCE_EXPLAINS_PREVIOUS_ASSOCIATION"
    )
    result={
        "experiment_id":"A11-EXP-136",
        "hypothesis":"Stage135 side-vs-hatch association is potentially ordinary mirror V-shading; a distinctive visual design must show upper/lower modulation AFTER holding x-side constant.",
        "input":"same canonical source and immutable Stage132/135 geometry/Stage94 detector; all four image formats; independent recomputation checked against Stage135 counts",
        "canonical_sha256":digest,
        "statistic":"exact conditional 2×2 Pearson-tail under independent within-side hypergeometric label exchangeability, jointly enumerating upper POS counts for left and right sides",
        "controls":controls_result,
        "stage135_aggregate_reproduction_pass":fidelity,
        "source_variants":results,
        "all_adequate":adequate,
        "all_strong":strong,
        "direction_consistency":sign_consistency,
        "replicated_additional_structure":replicated,
        "decision":decision,
        "stop_rule":"If controls/source reproduction fail do not interpret target; require all 4 versions p<=.01, top-vs-bottom signed contrast >=.25 in at least one side and consistent directions to promote. Otherwise a natural left/right sail convention suffices for the measured association.",
        "scope_limit":"This does not establish normal artist intent; it only checks whether there is evidence beyond left/right V-shading. Multiple-puzzle/look-elsewhere selection is not accounted for; four renderings are correlated observations, not independent experimental replications.",
        "security":"No ordered strokes, text extraction, words, private keys, mnemonics, wallet addresses or transactions."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
        "# Stage 136 — is Stage135 just normal mirrored sail hatching?",
        "",
        f"- Canonical image: **{digest==EXPECTED_SHA}**",
        f"- Synthetic natural-V vs vertical-reversal controls: **{controls_result['passed']}**",
        f"- Exact Stage135 source aggregate reproduction: **{fidelity}**",
        f"- Adequate format coverage: **{sum(results[v]['eligible'] for v in FORMATS)}/4**",
        f"- Excess vertical pattern beyond left/right side: **{sum(results[v]['passes_new_structure_gate'] for v in FORMATS)}/4**",
        f"- Decision: **{decision}**",
        "",
        "| Source | p after conditioning on side | left upper−lower POS | right upper−lower POS |",
        "|---|---:|---:|---:|"
    ]
    for v in FORMATS:
        z=results[v];d=z["side_specific_vertical_delta"]
        lines.append(f"| {v} | {z['exact_side_conditioned_p']:.6f} | {d['left']:+.3f} | {d['right']:+.3f} |")
    lines+=["","## Interpretation",""]
    if not controls_result["passed"] or not fidelity:
        lines.append("Controls or exact aggregate reproduction failed. Repair Stage136, do not classify real image.")
    elif not adequate:
        lines.append("Insufficient source coverage in the fixed sail sectors; no real-data inference.")
    elif replicated:
        lines.append("An extra vertical modulation persists beyond normal side-based V hatching. Independent drawing controls and manual review needed; **not** a code.")
    else:
        lines.append("The strong Stage135 association is consistent with left/right symmetric V-style pencil strokes. There is no demonstrated additional vertical coding layer under this fixed side-conditioned test.")
    lines+=["","Statistical note: prior p-values assume more exchangeability than normal drawing permits. Current p values condition on x-side but do not correct for the broader historical search.",
            "No secret data or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":136,"controls":controls_result["passed"],
                      "source_match":fidelity,"decision":decision}))

if __name__=="__main__":main()
