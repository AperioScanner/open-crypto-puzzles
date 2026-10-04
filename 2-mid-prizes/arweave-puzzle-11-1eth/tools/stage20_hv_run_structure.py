#!/usr/bin/env python3
"""Stage 20: exact run-structure audit of the 12-building H/V sequence.

Non-cryptographic. Conditions on the already-observed composition (8 H, 4 V) and
enumerates all C(12,4)=495 sequences to test whether the observed run structure is
unusually simple/organized, independent of the post-hoc hexadecimal 0x321 reading.
"""
from __future__ import annotations
import itertools, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis"/"runs"/"stage20-hv-run-structure"
OUT.mkdir(parents=True,exist_ok=True)

OBS="HHVVHHVHHHHV"

def metrics(s):
    runs=[]
    cur=s[0]; n=1
    transitions=0
    for ch in s[1:]:
        if ch==cur:
            n+=1
        else:
            runs.append((cur,n))
            cur=ch; n=1
            transitions+=1
    runs.append((cur,n))
    h_runs=[n for c,n in runs if c=="H"]
    v_runs=[n for c,n in runs if c=="V"]
    rev=s[::-1]
    comp="".join("V" if c=="H" else "H" for c in s)
    return {
        "run_count":len(runs),
        "transition_count":transitions,
        "run_lengths":[n for _,n in runs],
        "run_types":[c for c,_ in runs],
        "longest_H_run":max(h_runs),
        "longest_V_run":max(v_runs),
        "hamming_to_reverse":sum(a!=b for a,b in zip(s,rev)),
        "hamming_to_complement":sum(a!=b for a,b in zip(s,comp)),
        "alternation_matches":sum(s[i]!=s[i-1] for i in range(1,len(s))),
    }

def all_conditioned():
    out=[]
    for vs in itertools.combinations(range(12),4):
        a=["H"]*12
        for i in vs: a[i]="V"
        out.append("".join(a))
    return out

def tail_prob(values, obs, direction):
    if direction=="le":
        return sum(v<=obs for v in values)/len(values)
    return sum(v>=obs for v in values)/len(values)

def main():
    seqs=all_conditioned()
    obs=metrics(OBS)
    ms=[metrics(s) for s in seqs]

    tests={
      "run_count":{"observed":obs["run_count"],"lower_tail_p":tail_prob([m["run_count"] for m in ms],obs["run_count"],"le")},
      "longest_H_run":{"observed":obs["longest_H_run"],"upper_tail_p":tail_prob([m["longest_H_run"] for m in ms],obs["longest_H_run"],"ge")},
      "longest_V_run":{"observed":obs["longest_V_run"],"upper_tail_p":tail_prob([m["longest_V_run"] for m in ms],obs["longest_V_run"],"ge")},
      "transition_count":{"observed":obs["transition_count"],"lower_tail_p":tail_prob([m["transition_count"] for m in ms],obs["transition_count"],"le")},
      "hamming_to_reverse":{"observed":obs["hamming_to_reverse"],"lower_tail_p":tail_prob([m["hamming_to_reverse"] for m in ms],obs["hamming_to_reverse"],"le")},
    }

    # Pre-registered composite notion of visibly simple block structure:
    # no more runs than observed AND at least as long an H block.
    composite=sum(
        (m["run_count"]<=obs["run_count"] and m["longest_H_run"]>=obs["longest_H_run"])
        for m in ms
    )/len(ms)

    exact_same_run_lengths=sum(m["run_lengths"]==obs["run_lengths"] for m in ms)

    result={
      "experiment_id":"A11-EXP-020",
      "scope":"exact enumeration of all 12-position H/V strings with exactly four V labels; run/symmetry structure only; no private-key operations",
      "observed_sequence":OBS,
      "observed_metrics":obs,
      "conditioned_universe_size":len(seqs),
      "tests":tests,
      "composite_simple_block_probability":composite,
      "same_run_length_pattern_count":exact_same_run_lengths,
      "same_run_length_pattern_probability":exact_same_run_lengths/len(ms),
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
      "# Stage 20 — exact H/V run-structure audit","",
      "**Experiment:** A11-EXP-020","",
      f"Observed sequence: `{OBS}`",
      f"Observed run lengths: `{obs['run_lengths']}` ({obs['run_count']} runs; longest H={obs['longest_H_run']}, longest V={obs['longest_V_run']}).",
      f"Conditioned null: all {len(seqs)} sequences with exactly 8 H and 4 V.","",
      "| metric | observed | exact tail probability |",
      "|:---|---:|---:|",
      f"| run count (low = blockier) | {obs['run_count']} | {tests['run_count']['lower_tail_p']:.4f} |",
      f"| longest H run | {obs['longest_H_run']} | {tests['longest_H_run']['upper_tail_p']:.4f} |",
      f"| longest V run | {obs['longest_V_run']} | {tests['longest_V_run']['upper_tail_p']:.4f} |",
      f"| transition count (low = blockier) | {obs['transition_count']} | {tests['transition_count']['lower_tail_p']:.4f} |",
      f"| Hamming distance to reverse (low = symmetric) | {obs['hamming_to_reverse']} | {tests['hamming_to_reverse']['lower_tail_p']:.4f} |",
      "",
      f"- Composite blockiness probability (runs <= observed AND longest-H >= observed): **{composite:.4f}**",
      f"- Exact same run-length pattern count: **{exact_same_run_lengths}/{len(ms)} = {exact_same_run_lengths/len(ms):.4f}**","",
      "## Interpretation",""
    ]
    if composite<0.05:
        md.append("The H/V sequence has unusually blocky run structure under the composition-conditioned null. That supports treating the orientation arrangement itself as non-random, independent of the hexadecimal 321 label.")
    else:
        md.append("The H/V sequence is not unusually blocky under the composition-conditioned null. This weakens the idea that the arrangement itself carries an obvious low-complexity code; the robust orientation pattern may still be deliberate, but its run structure is not exceptional.")
    md += ["","This stage deliberately ignores the 0x321 representation and tests only the H/V arrangement itself.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-020","composite_p":composite,"same_runs_p":exact_same_run_lengths/len(ms)}))

if __name__=="__main__": main()
