#!/usr/bin/env python3
"""Stage 115: Tiamat Reddit-inspiration candidate audit.

Primary author evidence:
Tiamat told Arweave's official Community Spotlight (2019-10-10) that he liked
tangible puzzles, then saw a Bitcoin puzzle on Reddit and realized the permaweb
was a good immutable place to store puzzles.

This stage does not guess a private key or decode Puzzle #11. It only asks:
1. Which known Reddit Bitcoin-puzzle candidates are chronologically possible?
2. Can one be identified as the exact inspiration?
3. Which construction traits are shared by all top pre-launch candidates and
   therefore safe to use only as a broad design-family prior?

No private-key generation, derivation, reconstruction, enumeration,
verification, or wallet access is performed.
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import date

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"clues"/"tiamat-reddit-inspiration-candidates.json"
AUTHOR_POSTS=ROOT/"clues"/"author-posts.md"
OUT=ROOT/"analysis"/"runs"/"stage115-tiamat-reddit-inspiration"
OUT.mkdir(parents=True,exist_ok=True)

TRAITS=(
    "image_based",
    "funded_crypto_reward",
    "key_or_wallet_unlock",
    "multi_step",
    "visible_semantic",
    "exact_pixel_dependency",
    "format_fragility_discussed",
    "brute_force_component",
    "public_solution_or_detailed_hints",
)

POSITIVE_TRAITS=(
    "image_based",
    "funded_crypto_reward",
    "key_or_wallet_unlock",
    "multi_step",
    "visible_semantic",
    "public_solution_or_detailed_hints",
)

DIRECT_TERMS=("8kk0pa","8krbd3","cryptogreetings","koljBmHs")

def parse_date(s):
    if not s:
        return None
    return date.fromisoformat(s[:10])

def candidate_score(c):
    # Score only broad construction overlap, not fragile carrier tricks.
    return sum(bool(c.get(t)) for t in POSITIVE_TRAITS)

def main():
    data=json.loads(SRC.read_text())
    primary=data["primary_interview"]
    cutoff=parse_date(primary["first_arweave_puzzle_cutoff"])
    if cutoff is None:
        raise SystemExit("missing chronology cutoff")

    candidates=[]
    for c in data["candidates"]:
        d=parse_date(c.get("date"))
        if c.get("chronology")=="pre_series":
            possible=True
        elif d is not None:
            possible=d<cutoff
        else:
            possible=False

        row=dict(c)
        row["chronologically_possible"]=bool(possible)
        row["score"]=candidate_score(c) if possible else None
        candidates.append(row)

    pre=[x for x in candidates if x["chronologically_possible"]]
    if not pre:
        raise SystemExit("no pre-launch candidates")

    top_score=max(x["score"] for x in pre)
    top=[x for x in pre if x["score"]==top_score]

    # Direct author-link search is deliberately constrained to author-source
    # material, not planning docs or this candidate snapshot.
    author_blob=AUTHOR_POSTS.read_text(errors="replace")
    direct_hits=[t for t in DIRECT_TERMS if t.lower() in author_blob.lower()]
    direct_link=bool(direct_hits)

    # Exact identity can only be promoted with direct author linkage and a
    # unique evidence lead >=2 points over the runner-up.
    ranked=sorted(pre,key=lambda x:(-x["score"],x["id"]))
    lead=(ranked[0]["score"]-ranked[1]["score"]) if len(ranked)>1 else ranked[0]["score"]
    exact_identified=bool(direct_link and len(top)==1 and lead>=2)

    # Shared family traits are intersection across all top pre-launch
    # candidates. These are design priors only.
    shared=[]
    for t in TRAITS:
        if all(bool(x.get(t)) for x in top):
            shared.append(t)

    family_prior=[
        t for t in shared
        if t in ("image_based","funded_crypto_reward","key_or_wallet_unlock",
                 "multi_step","visible_semantic","public_solution_or_detailed_hints")
    ]

    chronology_excluded=[
        {"id":x["id"],"date":x.get("date"),"title":x.get("title")}
        for x in candidates if not x["chronologically_possible"]
    ]

    result={
        "experiment_id":"A11-EXP-115",
        "scope":"author-interview chronology + fixed Reddit Bitcoin-puzzle candidate comparison; no Puzzle #11 decoding and no private-key operations",
        "primary_interview":{
            "url":primary["url"],
            "published":primary["published"],
            "first_series_cutoff":primary["first_arweave_puzzle_cutoff"],
            "statement_summary":primary["quote_summary"],
        },
        "candidate_count":len(candidates),
        "prelaunch_candidate_count":len(pre),
        "prelaunch_ranked":[
            {
                "id":x["id"],
                "title":x["title"],
                "date":x.get("date"),
                "publication_bound":x.get("publication_bound"),
                "score":x["score"],
            }
            for x in ranked
        ],
        "postlaunch_excluded":chronology_excluded,
        "top_candidate_ids":[x["id"] for x in top],
        "top_score":top_score,
        "score_lead_over_runner_up":lead,
        "direct_tiamat_reference_hits":direct_hits,
        "direct_tiamat_link":direct_link,
        "exact_inspiration_identified":exact_identified,
        "shared_top_candidate_traits":shared,
        "promoted_family_prior":family_prior,
        "decision":"EXACT_INSPIRATION_IDENTIFIED" if exact_identified else "EXACT_IDENTITY_UNRESOLVED_FAMILY_PRIOR_ONLY",
        "interpretation_guard":"Shared traits are only a broad author-inspiration family prior. Candidate-specific tricks must not be transferred to Puzzle #11 without independent evidence.",
        "safety_guard":"No private key or ordered secret candidate is generated, reconstructed, enumerated, or verified.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 115 — Tiamat Reddit-inspiration candidate audit",
        "",
        "**Experiment:** A11-EXP-115",
        "",
        f"- pre-launch candidates: **{len(pre)}**",
        f"- top candidates: **{', '.join(x['id'] for x in top)}**",
        f"- direct Tiamat candidate reference: **{direct_link}**",
        f"- exact inspiration identified: **{exact_identified}**",
        f"- decision: **{result['decision']}**",
        "",
        "## Chronologically possible candidates",
        "",
        "| candidate | title | score |",
        "|:---|:---|---:|",
    ]
    for x in ranked:
        md.append(f"| {x['id']} | {x['title'].replace('|','/')} | {x['score']} |")

    md += [
        "",
        "## Safe shared family prior",
        "",
    ]
    if family_prior:
        for t in family_prior:
            md.append(f"- {t}")
    else:
        md.append("None.")

    md += [
        "",
        "## Interpretation",
        "",
    ]
    if exact_identified:
        md.append("A unique candidate has both a material evidence lead and a direct Tiamat reference. The exact inspiration is promoted for contextual mechanism comparison only.")
    else:
        md.append("Chronology narrows the plausible inspiration family, but there is no direct Tiamat link that identifies one exact Reddit puzzle. Do not transfer candidate-specific tricks. Only traits shared by all top pre-launch candidates are retained as a broad design prior.")

    md += [
        "",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-115",
        "prelaunch":len(pre),
        "top":[x["id"] for x in top],
        "direct_link":direct_link,
        "exact_identified":exact_identified,
        "family_prior":family_prior,
    }))

if __name__=="__main__":
    main()
