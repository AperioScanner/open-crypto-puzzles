#!/usr/bin/env python3
from __future__ import annotations
import itertools, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage18-small-sail-width-sequence"
OUT.mkdir(parents=True,exist_ok=True)

def ap_error(a,b,c):
    return abs((b-a)-(c-b))

def main():
    g=json.loads(GEOM.read_text())
    widths=list(map(int,g["small_sail_widths_left_to_right_px"]))
    obs=tuple(widths[:3])
    obs_err=ap_error(*obs)
    obs_step=((obs[1]-obs[0])+(obs[2]-obs[1]))/2
    perms=list(itertools.permutations(widths))
    exact=sum(ap_error(*p[:3])==0 for p in perms)
    as_good=sum(ap_error(*p[:3])<=obs_err for p in perms)
    mod26=[w%26 for w in widths]
    first3_same_mod=(mod26[0]==mod26[1]==mod26[2])
    same_mod_perms=sum((p[0]%26)==(p[1]%26)==(p[2]%26) for p in perms)
    result={
      "experiment_id":"A11-EXP-018",
      "scope":"pre-existing left-to-right small-sail widths only; arithmetic progression and modulo-26 diagnostics; no private-key operations",
      "widths_left_to_right_px":widths,
      "first_three":list(obs),
      "first_three_differences":[obs[1]-obs[0],obs[2]-obs[1]],
      "first_three_ap_error":obs_err,
      "first_three_mean_step":obs_step,
      "all_permutations":len(perms),
      "permutations_with_exact_AP_first3":exact,
      "exact_AP_permutation_probability":exact/len(perms),
      "permutations_at_least_as_good":as_good,
      "mod26":mod26,
      "first_three_same_mod26":first3_same_mod,
      "permutations_with_same_mod26_first3":same_mod_perms,
      "same_mod26_permutation_probability":same_mod_perms/len(perms),
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=[
      "# Stage 18 — small-sail width sequence",
      "",
      "**Experiment:** A11-EXP-018",
      "",
      f"Previously measured left-to-right sail widths: {widths} px.",
      f"First three differences: {result['first_three_differences']} px.",
      f"Exact arithmetic progression among the first three: {obs_err==0}; step = {obs_step:g} px.",
      f"Among all {len(perms)} permutations of the same five widths, {exact} place an exact arithmetic-progression triple first ({exact/len(perms):.4f}).",
      f"Widths modulo 26: {mod26}; first three share the same residue: {first3_same_mod}.",
      "",
      "## Interpretation",
      "",
      "The first three left-to-right sail widths form an exact arithmetic progression with step 26 in the existing geometry measurement. This is a bounded secondary visual lead because left-to-right order was fixed before this test.",
      "However, the widths were produced by an earlier automated measurement and their per-sail x positions were explicitly described as less reliable. Therefore this result is not promoted as an author clue until the widths are re-measured robustly across thresholds or by an independent segmentation method.",
      "The modulo-26 observation is descriptive only and is not treated as an alphabet encoding.",
      ""
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-018","widths":widths,"exact_ap":obs_err==0,"step":obs_step,"perm_p":exact/len(perms)}))

if __name__=="__main__": main()
