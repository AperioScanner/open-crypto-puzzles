#!/usr/bin/env python3
from __future__ import annotations
import itertools, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage17-orientation-geometry-independence"
OUT.mkdir(parents=True,exist_ok=True)

SEQ="HHVVHHVHHHHV"
V_IDX={i for i,c in enumerate(SEQ) if c=="V"}

def mean(xs): return sum(xs)/len(xs)
def diff(vals, idx):
    a=[v for i,v in enumerate(vals) if i in idx]
    b=[v for i,v in enumerate(vals) if i not in idx]
    return mean(a)-mean(b)

def two_sided_perm(vals, obs_idx):
    obs=abs(diff(vals,obs_idx))
    combos=list(itertools.combinations(range(len(vals)),len(obs_idx)))
    ds=[abs(diff(vals,set(c))) for c in combos]
    ge=sum(d>=obs-1e-12 for d in ds)
    return {"observed_abs_mean_difference":obs,"exact_two_sided_p":ge/len(ds),"permutations":len(ds)}

def auc(vals, labels):
    pairs=0; wins=0.0
    for i,v in enumerate(vals):
        for j,u in enumerate(vals):
            if labels[i]==1 and labels[j]==0:
                pairs+=1
                if v>u: wins+=1
                elif v==u: wins+=0.5
    return wins/pairs if pairs else 0.5

def main():
    g=json.loads(GEOM.read_text())
    bs=g["buildings"]
    labels=[1 if c=="V" else 0 for c in SEQ]
    feats={
      "width":[b["x1"]-b["x0"] for b in bs],
      "height":[b["bottom_y"]-b["roof_y"] for b in bs],
      "aspect_width_over_height":[(b["x1"]-b["x0"])/(b["bottom_y"]-b["roof_y"]) for b in bs],
      "roof_y":[b["roof_y"] for b in bs],
      "x_center":[(b["x0"]+b["x1"])/2 for b in bs],
      "area":[(b["x1"]-b["x0"])*(b["bottom_y"]-b["roof_y"]) for b in bs],
    }
    results={}
    for name,vals in feats.items():
        t=two_sided_perm(vals,V_IDX)
        raw_auc=auc(vals,labels)
        t["auc_V_greater"]=raw_auc
        t["best_direction_auc"]=max(raw_auc,1-raw_auc)
        t["values"]=vals
        results[name]=t
    ranked=sorted(results.items(),key=lambda kv:kv[1]["exact_two_sided_p"])
    minp=ranked[0][1]["exact_two_sided_p"]
    bonf=min(1.0,minp*len(results))
    result={
      "experiment_id":"A11-EXP-017",
      "scope":"fixed H/V skyline labels versus measured building geometry; exact permutation tests only; no private-key operations",
      "sequence":SEQ,
      "vertical_buildings":[i+1 for i in sorted(V_IDX)],
      "features":results,
      "smallest_raw_p_feature":ranked[0][0],
      "smallest_raw_p":minp,
      "bonferroni_over_6_features":bonf,
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=["# Stage 17 — is hatch orientation explained by building geometry?","",
        "**Experiment:** A11-EXP-017","",
        f"Fixed skyline sequence: {SEQ}; vertical-hatched buildings: {[i+1 for i in sorted(V_IDX)]}.",
        "All p-values are exact over the 495 possible placements of four V labels among 12 buildings.","",
        "| feature | abs mean difference (V-H) | exact two-sided p | best-direction AUC |",
        "|:---|---:|---:|---:|"]
    for name,r in ranked:
        md.append(f"| {name} | {r['observed_abs_mean_difference']:.4f} | {r['exact_two_sided_p']:.4f} | {r['best_direction_auc']:.3f} |")
    md += ["",f"- Smallest raw p: **{minp:.4f}** ({ranked[0][0]})",
           f"- Bonferroni correction across 6 pre-defined features: **{bonf:.4f}**","",
           "## Interpretation",""]
    if bonf<0.05:
        md.append("At least one simple geometric feature predicts H/V orientation after correction. This supports an artistic/structural explanation and weakens the hatch pattern as an independent encoded marker.")
    else:
        md.append("No tested simple geometric feature predicts H/V orientation at corrected 5% significance. This argues against the easiest shape/position explanation, while still not proving intentional encoding.")
    md += ["","This test addresses the H/V structure itself, not whether the post-hoc hexadecimal reading 0x321 is correct.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-017","min_feature":ranked[0][0],"min_p":minp,"bonferroni":bonf}))

if __name__=="__main__": main()
