#!/usr/bin/env python3
"""Stage 116: strict mechanism-grammar intersection of Tiamat inspiration candidates.

Consumes:
- Stage 115 top candidate IDs;
- checked public-source mechanism summaries for those candidates.

The experiment promotes only operations independently marked CONFIRMED in every
top candidate. Candidate-specific operations remain non-transferable.

Safe archival analysis only. No private-key generation, derivation,
reconstruction, enumeration, verification, or wallet access.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GRAMMAR=ROOT/"clues"/"tiamat-inspiration-solution-grammar.json"
STAGE115=ROOT/"analysis"/"runs"/"stage115-tiamat-reddit-inspiration"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage116-inspiration-grammar-intersection"
OUT.mkdir(parents=True,exist_ok=True)

ALLOWED_STATUS={"confirmed","not_confirmed"}
BASE58_SECRET_RE=re.compile(r"(?<![1-9A-HJ-NP-Za-km-z])[5KL][1-9A-HJ-NP-Za-km-z]{50,51}(?![1-9A-HJ-NP-Za-km-z])")
HEX64_RE=re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")

def intersection(candidates,vocabulary):
    by_candidate={}
    for cid,c in candidates.items():
        rows=c["evidence"]
        by_candidate[cid]={r["operation"]:r["status"] for r in rows}
    shared=[
        op for op in vocabulary
        if all(by_candidate[cid].get(op)=="confirmed" for cid in sorted(candidates))
    ]
    specific={}
    for op in vocabulary:
        yes=[cid for cid in sorted(candidates) if by_candidate[cid].get(op)=="confirmed"]
        if 0<len(yes)<len(candidates):
            specific[op]=yes
    return shared,specific

def synthetic_control():
    vocab=["shared","only_a","only_b","unknown"]
    cands={
        "A":{"evidence":[
            {"operation":"shared","status":"confirmed"},
            {"operation":"only_a","status":"confirmed"},
            {"operation":"only_b","status":"not_confirmed"},
            {"operation":"unknown","status":"not_confirmed"},
        ]},
        "B":{"evidence":[
            {"operation":"shared","status":"confirmed"},
            {"operation":"only_a","status":"not_confirmed"},
            {"operation":"only_b","status":"confirmed"},
            {"operation":"unknown","status":"not_confirmed"},
        ]},
    }
    shared,specific=intersection(cands,vocab)
    return bool(shared==["shared"] and specific=={"only_a":["A"],"only_b":["B"]})

def validate(grammar,stage115):
    errors=[]
    vocab=grammar.get("vocabulary",[])
    candidates=grammar.get("candidates",{})
    top=stage115.get("top_candidate_ids",[])

    if len(vocab)!=len(set(vocab)) or not vocab:
        errors.append("vocabulary_not_unique")
    if sorted(candidates)!=sorted(top):
        errors.append("candidate_ids_do_not_match_stage115_top")

    for cid in sorted(candidates):
        rows=candidates[cid].get("evidence",[])
        ops=[r.get("operation") for r in rows]
        if Counter(ops)!=Counter(vocab):
            errors.append(f"{cid}:operation_coverage_mismatch")
        for r in rows:
            if r.get("status") not in ALLOWED_STATUS:
                errors.append(f"{cid}:{r.get('operation')}:bad_status")
            if not r.get("authority"):
                errors.append(f"{cid}:{r.get('operation')}:missing_authority")
            if not r.get("summary"):
                errors.append(f"{cid}:{r.get('operation')}:missing_summary")

    blob=json.dumps(grammar,ensure_ascii=False)
    if BASE58_SECRET_RE.search(blob):
        errors.append("secret_like_base58_material_present")
    if HEX64_RE.search(blob):
        errors.append("secret_like_hex64_material_present")

    return errors

def main():
    grammar=json.loads(GRAMMAR.read_text())
    stage115=json.loads(STAGE115.read_text())

    synth_pass=synthetic_control()
    errors=validate(grammar,stage115)
    source_control=bool(synth_pass and not errors)

    top_ids=stage115.get("top_candidate_ids",[])
    cands={cid:grammar["candidates"][cid] for cid in top_ids if cid in grammar.get("candidates",{})}

    shared,specific=intersection(cands,grammar["vocabulary"]) if source_control else ([],{})

    # "not_confirmed" never becomes "absent"; it is simply excluded from the
    # positive intersection.
    if not source_control:
        decision="IMPLEMENTATION_OR_SOURCE_FAILURE"
    elif not shared:
        decision="NO_NARROW_INTERSECTION"
    elif len(shared)<=5:
        decision="NARROW_SHARED_GRAMMAR"
    else:
        decision="BROAD_INTERSECTION_ONLY"

    # The exact-pixel operation is deliberately not promoted by negative
    # inference. Only confirmed-in-both operations appear in shared.
    result={
        "experiment_id":"A11-EXP-116",
        "scope":"strict intersection of confirmed public-source mechanism operations across Stage-115 top inspiration candidates; no Puzzle #11 secret decoding",
        "top_candidate_ids":top_ids,
        "vocabulary":grammar.get("vocabulary",[]),
        "synthetic_intersection_control_pass":synth_pass,
        "validation_errors":errors,
        "source_control_pass":source_control,
        "shared_confirmed_operations":shared,
        "candidate_specific_confirmed_operations":specific,
        "shared_count":len(shared),
        "decision":decision,
        "promoted":bool(source_control and 0<len(shared)<=5),
        "promotion_rule":"operation must be marked confirmed in every Stage-115 top candidate; not_confirmed is never treated as absence; source schema and synthetic intersection control must pass",
        "interpretation_guard":"The shared operations are only an author-inspiration family prior. They do not establish that Puzzle #11 uses any candidate-specific mechanism or reveal any secret material.",
        "safety_guard":"No private key, candidate key string, ordered secret, derivation, wallet verification, or wallet access is performed.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 116 — shared solution grammar of Tiamat inspiration candidates",
        "",
        "**Experiment:** A11-EXP-116",
        "",
        f"- top candidates: **{', '.join(top_ids)}**",
        f"- synthetic intersection control: **{synth_pass}**",
        f"- source/schema control: **{source_control}**",
        f"- shared confirmed operations: **{len(shared)}**",
        f"- decision: **{decision}**",
        f"- promoted as family prior: **{result['promoted']}**",
        "",
        "## Strict intersection",
        "",
    ]
    if shared:
        for op in shared:
            md.append(f"- **{op}**")
    else:
        md.append("None.")

    md += ["","## Candidate-specific confirmed operations",""]
    if specific:
        for op,ids in specific.items():
            md.append(f"- **{op}** — {', '.join(ids)} only")
    else:
        md.append("None.")

    md += ["","## Interpretation",""]
    if not source_control:
        md.append("The grammar/source controls failed. Repair Stage 116 under the same stage number before interpreting the result.")
    elif result["promoted"]:
        md.append("A narrow set of concrete operations is independently evidenced in both plausible pre-launch inspiration puzzles. Only this intersection may guide one future Puzzle #11 structural test; candidate-specific tricks remain blocked.")
    elif not shared:
        md.append("The two plausible inspiration puzzles share only the broad Stage-115 construction family, not a narrower confirmed decoding operation. Do not force a mechanism transfer.")
    else:
        md.append("The intersection is too broad to sharpen the prior beyond Stage 115.")

    md += [
        "",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-116",
        "source_control":source_control,
        "shared":shared,
        "decision":decision,
        "promoted":result["promoted"],
    }))

if __name__=="__main__":
    main()
