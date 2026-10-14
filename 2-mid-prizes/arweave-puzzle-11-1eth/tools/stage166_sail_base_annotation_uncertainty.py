#!/usr/bin/env python3
"""Stage166: source-blind sensitivity of Stage165 hand-annotated sail foot widths.

Original ten left/right x endpoints independently vary by {-4,0,+4}px.
3^10 choices compress to 5^5 widths with multiplicities [1,2,3,2,1].
Uses EXACT Stage88 absolute Pearson and 120 permutations. No visual recrops,
new symbols, key, phrase, address or wallet operations. Preregistered.
"""
from __future__ import annotations
import itertools,json,hashlib
from pathlib import Path
import numpy as np
from stage153_under_pier_triangle_junctions import TRIANGLES
from stage88_superbatch_survivor_replication import exact_width_gap

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR=ROOT/"analysis"/"runs"/"stage165-corrected-sail-width-gap"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage166-sail-annotation-uncertainty"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
BASE=(70,76,88,84,94)
FORMATS=("original","jpeg85","jpeg70","down75_up")
DELTAS=(-8,-4,0,4,8)
WEIGHTS=(1,2,3,2,1)

def evaluator(widths,centers):
    """Vectorized exact 120-index-permutation test, independently replayed."""
    perms=np.asarray(list(itertools.permutations(range(5))),dtype=np.int16)
    x=widths[:,perms[:,:4]]
    xc=x-x.mean(axis=2,keepdims=True)
    g=np.diff(np.asarray(centers,float))
    yc=g-g.mean()
    num=np.einsum("ijk,k->ij",xc,yc,optimize=True)
    den=np.sqrt(np.einsum("ijk,ijk->ij",xc,xc)*np.dot(yc,yc))
    signed=np.divide(num,den,out=np.zeros_like(num),where=den>1.e-12)
    r=np.abs(signed[:,0])
    p=np.mean(np.abs(signed)>=r[:,None]-1.e-15,axis=1)
    return p,r,signed[:,0]

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    old=json.loads(PRIOR.read_text())
    original_annotated=tuple(int(abs(t[2][0]-t[1][0]))
        for name,t in TRIANGLES.items() if name.startswith("sail"))
    checks={
        "source_SHA":sha==SHA==old["canonical_SHA"],
        "Stage165_negative":old["decision"]=="NO_SIGNIFICANT_TRUE_SAIL_BASE_WIDTH_GAP_RELATION",
        "annotation_base_widths":original_annotated==BASE==tuple(old["fixed_true_sail_widths"]),
        "Stage165_source_controls":all(old["source_guards"].values()),
        "Stage165_numerical_controls":old["synthetic_and_permutation_controls"]["pass"],
        "four_formats":set(old["per_variant"])==set(FORMATS),
    }
    pos=exact_width_gap([106,134,90,118,50],old["per_variant"]["original"]["centers"])
    neg=exact_width_gap([30]*5,old["per_variant"]["original"]["centers"])
    checks["positive_fixture"]=(pos["exact_permutations"]==120
         and pos["exact_p"]<=.05 and pos["abs_correlation"]>=.999)
    checks["constant_negative"]=(neg["exact_permutations"]==120
         and neg["exact_p"]==1.0 and neg["abs_correlation"]==0.0)
    diff=np.asarray(list(itertools.product(DELTAS,repeat=5)),dtype=np.float64)
    mult=dict(zip(DELTAS,WEIGHTS))
    weight=np.asarray([np.prod([mult[int(d)] for d in row]) for row in diff],dtype=np.int64)
    w=np.asarray(BASE,dtype=float)[None,:]+diff
    checks["unique_3125"]=len(w)==3125
    checks["labelled_59049"]=int(weight.sum())==59049
    checks["all_positive_widths"]=bool(np.all(w>0))
    baseidx=np.flatnonzero(np.all(diff==0,axis=1))
    checks["unperturbed_present"]=len(baseidx)==1
    by_format={}
    pvals=[];corrs=[];signs=[]
    for fmt in FORMATS:
        a=old["per_variant"][fmt]
        ref=exact_width_gap(BASE,a["centers"])
        pa,ra,sa=evaluator(w,a["centers"])
        good=(ref["exact_permutations"]==120
           and abs(ref["exact_p"]-a["exact_p"])<=1e-8
           and abs(ref["abs_correlation"]-a["abs_correlation"])<=1e-8
           and abs(pa[int(baseidx[0])]-ref["exact_p"])<=1e-8
           and abs(ra[int(baseidx[0])]-ref["abs_correlation"])<=1e-8)
        checks["Stage165_120_permutation_replay_"+fmt]=bool(good)
        by_format[fmt]={"baseline_p":ref["exact_p"],
           "baseline_abs_r":ref["abs_correlation"],
           "min_p":float(pa.min()),"max_p":float(pa.max()),
           "min_abs_r":float(ra.min()),"max_abs_r":float(ra.max()),
           "single_nominal_p_le_005_unique":int(np.count_nonzero(pa<=.05)),
           "single_nominal_p_le_005_labelled":int(weight[pa<=.05].sum())}
        pvals.append(pa);corrs.append(ra);signs.append(sa)
    P=np.column_stack(pvals);R=np.column_stack(corrs);S=np.column_stack(signs)
    single=np.any(P<=.05,axis=1)
    all_nominal=np.all(P<=.05,axis=1)
    same_sign=np.all(S>0,axis=1)|np.all(S<0,axis=1)
    joint=all_nominal & np.all(R>=.85,axis=1) & same_sign
    none=np.all(P>.05,axis=1)
    passed=bool(all(checks.values()))
    decision=("CONTROL_FAILURE" if not passed else
       "ROBUST_NON_SIGNIFICANCE_UNDER_4PX_ENDPOINT_JITTER" if bool(np.all(none)) else
       "ANNOTATION_JITTER_CAN_FLIP_STAGE165_JOINT_GATE" if bool(np.any(joint)) else
       "PARTIAL_SINGLE_FORMAT_SIGNIFICANCE_UNDER_JITTER" if bool(np.any(single)) else
       "INCONCLUSIVE_ANNOTATION_JITTER")
    def sizes(mask):
        return {"unique":int(np.count_nonzero(mask)),
                "labelled":int(weight[mask].sum())}
    groups={"any_single_format_p_le_005":sizes(single),
            "four_formats_p_le_005":sizes(all_nominal),
            "complete_original_Stage165_joint_gate":sizes(joint),
            "all_formats_p_gt_005":sizes(none)}
    data={"experiment_id":"A11-EXP-166","source_hash_provenance_only":sha,
       "source_pixels_reexamined":False,
       "prior_hand_annotated_base_widths":BASE,
       "endpoint_displacement_per_side_px":(-4,0,4),
       "derived_width_changes_px":DELTAS,
       "multiplicity_per_derived_width_change":WEIGHTS,
       "synthetic_labelled_endpoint_assignments":int(weight.sum()),
       "unique_width_vectors":len(w),
       "controls":checks,"controls_passed":sum(checks.values()),"controls_total":len(checks),
       "by_format":by_format,"sensitivity_counts":groups,"decision":decision,
       "scope_limit":"Artificial exhaustive coordinate uncertainties are NOT 59,049 independent image measurements and are NOT posterior probabilities. No source contour is remeasured, and a p-value in a perturbed vector is not evidence of author coding.",
       "safety":"No cryptographic material, BIP39, wallet/address access or external research."}
    (OUT/"result.json").write_text(json.dumps(data,indent=2)+"\n")
    report=["# Stage166 — ±4px manual sail-foot coordinate uncertainty stress test","",
       f"- Original SHA provenance only: **{sha==SHA}**",
       f"- Fixed source and numerical controls: **{sum(checks.values())}/{len(checks)}**",
       f"- Precommitted synthetic labelled endpoint sets: **{int(weight.sum()):,}** = {len(w)} unique width vectors",
       f"- Original Stage165 p: **{by_format['original']['baseline_p']:.6f}**",
       f"- Any single-format significant p<=.05: **{groups['any_single_format_p_le_005']['unique']}/{len(w)}** unique",
       f"- Full Stage165 four-format r>=.85, p<=.05, same-sign gate: **{groups['complete_original_Stage165_joint_gate']['unique']}/{len(w)}** unique",
       f"- Decision: **{decision}**","","| Format | Prior p | Min p in synthetic ±4px jitter | Max p |","|---|---:|---:|---:|"]
    for fmt in FORMATS:
        q=by_format[fmt]
        report.append(f"| {fmt} | {q['baseline_p']:.6f} | {q['min_p']:.6f} | {q['max_p']:.6f} |")
    report+=["","All results are sensitivity diagnostics for EXISTING hand annotations, not new pixel measurements or decoded clues. Repeated lossy renderings do not make the annotated widths independent. No key or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":166,"controls":f"{sum(checks.values())}/{len(checks)}",
       "single_significant":int(single.sum()),"joint_significant":int(joint.sum()),
       "decision":decision}))
if __name__=="__main__":main()
