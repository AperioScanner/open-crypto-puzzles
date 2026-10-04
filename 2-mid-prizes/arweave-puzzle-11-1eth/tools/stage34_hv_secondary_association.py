#!/usr/bin/env python3
"""Stage 34: exact H/V selector × secondary-detail association audit.

Safe, non-cryptographic experiment. Reuses measurements already produced in Stage 12
and the robust H/V labels established independently in Stages 5/21. No new image feature
is selected after seeing Stage-34 outcomes.

Question: do the four V buildings and eight H buildings also separate on secondary-detail
statistics, consistent with H/V acting as a deliberate selector/class label?
"""
from __future__ import annotations
import itertools, json, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RUN12=ROOT/"analysis"/"runs"/"stage12-count-perimeter"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage34-hv-secondary-association"
OUT.mkdir(parents=True,exist_ok=True)

BASELINE="HHVVHHVHHHHV"
V_OBS=tuple(i for i,c in enumerate(BASELINE) if c=="V")
FEATURE_NAMES=(
    "small_component_density",
    "small_component_instability_ratio",
    "mid_component_density",
    "perimeter_w2",
)

def load_buildings():
    s12=json.loads(RUN12.read_text())
    rows=[]
    by={r["name"]:r for r in s12["regions"]}
    for i in range(1,13):
        r=by[f"building_{i:02d}"]
        w,h=r["shape"]
        area=float(w*h)
        small=float(r["stable_small_component_median"])
        small_mad=float(r["stable_small_component_mad"])
        mid=float(r["stable_mid_component_median"])
        rows.append({
            "id":i,
            "label":BASELINE[i-1],
            "area":area,
            "small_component_density":small/area*10000.0,
            "small_component_instability_ratio":small_mad/(small+1.0),
            "mid_component_density":mid/area*10000.0,
            "perimeter_w2":float(r["perimeter_fraction_t140"]["w2"]),
            "raw_small_median":small,
            "raw_small_mad":small_mad,
            "raw_mid_median":mid,
        })
    return rows

def assignment_mask(v_idx,n=12):
    m=np.zeros(n,dtype=bool)
    m[list(v_idx)]=True
    return m

def abs_mean_diff(x,mask):
    return float(abs(x[mask].mean()-x[~mask].mean()))

def zscore_matrix(X):
    mu=X.mean(axis=0)
    sd=X.std(axis=0,ddof=0)
    sd=np.where(sd<1e-12,1.0,sd)
    return (X-mu)/sd

def within_sse(Z,mask):
    total=0.0
    for g in (mask,~mask):
        Y=Z[g]
        c=Y.mean(axis=0)
        total+=float(((Y-c)**2).sum())
    return total

def centroid_distance(Z,mask):
    d=Z[mask].mean(axis=0)-Z[~mask].mean(axis=0)
    return float(np.dot(d,d))

def main():
    rows=load_buildings()
    X=np.array([[r[k] for k in FEATURE_NAMES] for r in rows],dtype=float)
    Z=zscore_matrix(X)
    obs=assignment_mask(V_OBS)

    perms=list(itertools.combinations(range(12),4))
    assert len(perms)==495

    feature_results=[]
    for j,name in enumerate(FEATURE_NAMES):
        x=X[:,j]
        observed=abs_mean_diff(x,obs)
        null=[abs_mean_diff(x,assignment_mask(p)) for p in perms]
        # Exact permutation p includes observed assignment naturally.
        p=sum(v>=observed-1e-15 for v in null)/len(null)
        feature_results.append({
            "feature":name,
            "observed_abs_mean_difference":observed,
            "H_mean":float(x[~obs].mean()),
            "V_mean":float(x[obs].mean()),
            "exact_p":float(p),
            "bonferroni_p":float(min(1.0,p*len(FEATURE_NAMES))),
            "null_median":float(np.median(null)),
            "null_p95":float(np.percentile(null,95)),
        })

    obs_sse=within_sse(Z,obs)
    obs_centroid=centroid_distance(Z,obs)
    null_sse=[]
    null_centroid=[]
    for pset in perms:
        m=assignment_mask(pset)
        null_sse.append(within_sse(Z,m))
        null_centroid.append(centroid_distance(Z,m))
    p_sse=sum(v<=obs_sse+1e-15 for v in null_sse)/len(null_sse)
    p_cent=sum(v>=obs_centroid-1e-15 for v in null_centroid)/len(null_centroid)

    bonf_hits=sum(r["bonferroni_p"]<=0.05 for r in feature_results)
    raw_hits=sum(r["exact_p"]<=0.05 for r in feature_results)
    promoted=bool(p_sse<=0.05 and p_cent<=0.05 and (bonf_hits>=1 or raw_hits>=2))

    result={
        "experiment_id":"A11-EXP-034",
        "scope":"exact permutation association between fixed H/V labels and pre-existing Stage-12 secondary-detail measurements; no secret reconstruction or private-key operations",
        "baseline":BASELINE,
        "observed_V_buildings":[i+1 for i in V_OBS],
        "features":list(FEATURE_NAMES),
        "buildings":rows,
        "permutations":len(perms),
        "feature_results":feature_results,
        "multivariate":{
            "observed_within_group_sse":obs_sse,
            "exact_p_lower_sse":float(p_sse),
            "observed_centroid_distance_sq":obs_centroid,
            "exact_p_upper_centroid_distance":float(p_cent),
        },
        "promotion_rule":"promote selector hypothesis only if BOTH multivariate exact p-values <=0.05 AND either >=1 feature survives Bonferroni or >=2 individual features have raw exact p<=0.05",
        "promoted":promoted,
        "interpretation_guard":"Association would not by itself prove intentional encoding because some secondary-detail metrics may still be influenced by hatch construction. A positive result only justifies targeted visual follow-up.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 34 — H/V selector × secondary-detail association audit",
        "",
        "**Experiment:** A11-EXP-034",
        "",
        f"- Fixed H/V sequence: `{BASELINE}`",
        f"- V buildings: **{[i+1 for i in V_OBS]}**",
        f"- Exact label permutations: **{len(perms)}**",
        "- Projection-periodicity features are excluded to avoid circularity with hatch orientation.",
        "",
        "## Per-feature exact tests",
        "",
        "| feature | H mean | V mean | abs diff | exact p | Bonferroni p |",
        "|:---|---:|---:|---:|---:|---:|",
    ]
    for r in feature_results:
        md.append(f"| {r['feature']} | {r['H_mean']:.6f} | {r['V_mean']:.6f} | {r['observed_abs_mean_difference']:.6f} | {r['exact_p']:.4f} | {r['bonferroni_p']:.4f} |")
    md += [
        "",
        "## Multivariate exact tests",
        "",
        f"- observed within-class SSE: **{obs_sse:.6f}**, exact lower-tail p = **{p_sse:.4f}**",
        f"- observed H/V centroid distance²: **{obs_centroid:.6f}**, exact upper-tail p = **{p_cent:.4f}**",
        f"- promotion rule satisfied: **{promoted}**",
        "",
        "## Interpretation",
        "",
    ]
    if promoted:
        md.append("The fixed H/V labels align with independent secondary-detail measurements more strongly than most alternative four-V assignments. This promotes H/V as a possible selector/class label and justifies targeted visual inspection of the discriminating features.")
    else:
        md.append("The fixed H/V labels do not organize the Stage-12 secondary-detail measurements strongly enough under exact permutation testing. Keep H/V as a real format-stable visual pattern, but downgrade the specific hypothesis that it selects a second channel of counted building details.")
    md += [
        "",
        "A positive association would still require visual replication because connected-component statistics can partly reflect drawing construction rather than intentional coding.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-034",
        "p_sse":p_sse,
        "p_centroid":p_cent,
        "raw_feature_hits":raw_hits,
        "bonf_feature_hits":bonf_hits,
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
