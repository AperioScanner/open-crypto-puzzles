#!/usr/bin/env python3
"""Stage 117: author-series reuse of the Stage-116 shared grammar.

Input:
- Stage 116 shared operations.
- Stage 11 solved Arweave-puzzle mechanism catalog.

Goal:
Determine which inspiration-family operations also recur in Tiamat's own solved
Arweave puzzles. Promotion requires at least two supporting mechanisms across at
least two distinct solved puzzles.

Safe public-mechanism analysis only. No secret/key generation, derivation,
reconstruction, enumeration, verification, or wallet access.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STAGE11=ROOT/"analysis"/"runs"/"stage11-solved-puzzle-grammar"/"result.json"
STAGE116=ROOT/"analysis"/"runs"/"stage116-inspiration-grammar-intersection"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage117-author-series-grammar-reuse"
OUT.mkdir(parents=True,exist_ok=True)

CLASS_SUPPORT={
    "visible_text_or_symbol_reading":{
        "medium-translation",
        "small-detail-counting",
        "symbol-identification",
        "secondary-detail-rebus",
        "sequence-pattern",
        "visual-number-extraction",
    },
    "ordering_or_traversal":{
        "sequence-pattern",
    },
    "cross_domain_conversion":{
        "medium-translation",
        "cultural-reference",
        "symbol-identification",
        "franchise-reference",
        "secondary-detail-rebus",
        "art-reference",
        "reference-to-number",
        "technical-context",
        "literature-reference",
        "cross-domain-reference",
        "biographical-rebus",
    },
}

EXPECTED_SHARED={
    "visible_text_or_symbol_reading",
    "ordering_or_traversal",
    "cross_domain_conversion",
}

def synthetic_control():
    fake=[
        {"puzzle":1,"class":"A"},
        {"puzzle":2,"class":"A"},
        {"puzzle":2,"class":"B"},
    ]
    support={"op":{"A"},"weak":{"B"}}
    out={}
    for op,classes in support.items():
        hits=[m for m in fake if m["class"] in classes]
        puzzles=sorted(set(m["puzzle"] for m in hits))
        out[op]=(len(hits),len(puzzles),len(hits)>=2 and len(puzzles)>=2)
    return out["op"]==(2,2,True) and out["weak"]==(1,1,False)

def main():
    s11=json.loads(STAGE11.read_text())
    s116=json.loads(STAGE116.read_text())

    shared=set(s116.get("shared_confirmed_operations",[]))
    mechanisms=s11.get("mechanisms",[])

    validation_errors=[]
    if not s116.get("source_control_pass"):
        validation_errors.append("stage116_source_control_not_passed")
    if shared!=EXPECTED_SHARED:
        validation_errors.append(f"unexpected_stage116_shared_operations:{sorted(shared)}")
    if len(mechanisms)!=18:
        validation_errors.append(f"unexpected_stage11_mechanism_count:{len(mechanisms)}")
    if set(CLASS_SUPPORT)!=EXPECTED_SHARED:
        validation_errors.append("mapping_does_not_cover_exact_stage116_shared_set")
    for m in mechanisms:
        if "puzzle" not in m or "class" not in m or "evidence" not in m:
            validation_errors.append("stage11_mechanism_missing_required_field")
            break

    synth=synthetic_control()
    if not synth:
        validation_errors.append("synthetic_control_failed")

    rows={}
    promoted=[]
    weak=[]
    for op in sorted(shared):
        classes=CLASS_SUPPORT[op]
        hits=[
            {
                "puzzle":m["puzzle"],
                "class":m["class"],
                "answer_type":"numeric" if str(m.get("answer","")).isdigit() else "non_numeric",
            }
            for m in mechanisms if m["class"] in classes
        ]
        puzzles=sorted(set(x["puzzle"] for x in hits))
        ok=bool(len(hits)>=2 and len(puzzles)>=2)
        rows[op]={
            "supporting_mechanism_count":len(hits),
            "supporting_puzzles":puzzles,
            "supporting_classes":sorted(set(x["class"] for x in hits)),
            "support_examples":hits,
            "author_series_recurrent":ok,
        }
        (promoted if ok else weak).append(op)

    source_control=not validation_errors
    if not source_control:
        decision="IMPLEMENTATION_OR_SOURCE_FAILURE"
        promoted=[]
        weak=sorted(shared)
    elif promoted:
        decision="AUTHOR_SERIES_INTERSECTION"
    else:
        decision="NO_RECURRENT_AUTHOR_SERIES_OVERLAP"

    result={
        "experiment_id":"A11-EXP-117",
        "scope":"recurrent support for Stage-116 inspiration-grammar operations in Stage-11 solved Arweave mechanisms; no Puzzle #11 decoding",
        "stage116_shared_operations":sorted(shared),
        "predeclared_class_support":{k:sorted(v) for k,v in CLASS_SUPPORT.items()},
        "synthetic_control_pass":synth,
        "validation_errors":validation_errors,
        "source_control_pass":source_control,
        "operation_results":rows,
        "promoted_recurrent_operations":promoted,
        "weak_or_nonrecurrent_operations":weak,
        "decision":decision,
        "promotion_rule":"operation must have >=2 Stage-11 supporting mechanisms occurring across >=2 distinct solved Arweave puzzles; mapping is predeclared and conservative",
        "interpretation_guard":"Promotion establishes only an author-series design prior. It does not prove Puzzle #11 uses the operation or identify any payload.",
        "safety_guard":"No private key, ordered secret candidate, derivation, verification, or wallet access is performed.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 117 — reuse of the shared inspiration grammar in solved Arweave puzzles",
        "",
        "**Experiment:** A11-EXP-117",
        "",
        f"- synthetic control: **{synth}**",
        f"- source/schema control: **{source_control}**",
        f"- promoted recurrent operations: **{len(promoted)}**",
        f"- decision: **{decision}**",
        "",
        "| operation | mechanisms | solved puzzles | recurrent |",
        "|:---|---:|:---|:---:|",
    ]
    for op in sorted(rows):
        r=rows[op]
        md.append(
            f"| {op} | {r['supporting_mechanism_count']} | "
            f"{','.join(map(str,r['supporting_puzzles'])) or '-'} | "
            f"{r['author_series_recurrent']} |"
        )

    md += ["","## Promoted author-series prior",""]
    if promoted:
        for op in promoted:
            md.append(f"- **{op}**")
    else:
        md.append("None.")

    md += ["","## Interpretation",""]
    if not source_control:
        md.append("The source/mapping controls failed. Repair Stage 117 under the same number before interpretation.")
    elif promoted:
        md.append("Only the operations above are supported both by the plausible pre-launch inspiration family and recurrently across Tiamat's own solved Arweave puzzles. These may guide one future Puzzle #11 structural test; weak/single-puzzle operations must not be promoted.")
    else:
        md.append("The Stage-116 inspiration grammar does not recur broadly enough in Tiamat's solved series to sharpen the Puzzle #11 prior.")

    md += [
        "",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-117",
        "source_control":source_control,
        "promoted":promoted,
        "weak":weak,
        "decision":decision,
    }))

if __name__=="__main__":
    main()
