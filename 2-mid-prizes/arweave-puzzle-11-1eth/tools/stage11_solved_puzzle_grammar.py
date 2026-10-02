#!/usr/bin/env python3
"""Stage 11: reconstruct solved-puzzle design grammar relevant to Puzzle #11.

Public-source, non-cryptographic research only. This stage does not generate, derive,
reconstruct, enumerate, or verify any private-key candidate.
"""
from __future__ import annotations
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "runs" / "stage11-solved-puzzle-grammar"
OUT.mkdir(parents=True, exist_ok=True)
AUTHOR_REPORT = ROOT / "analysis" / "runs" / "stage4-author-archive" / "REPORT.md"

SOURCES = {
    "PZL5": "https://raw.githubusercontent.com/HomelessPhD/AR_Puzzles/main/PZL5/README.md",
    "PZL7": "https://raw.githubusercontent.com/HomelessPhD/AR_Puzzles/main/PZL7/README.md",
    "PZL8": "https://raw.githubusercontent.com/HomelessPhD/AR_Puzzles/main/PZL8/README.md",
}

MECHANISMS = [
    {"puzzle":5,"answer":"*","class":"medium-translation","evidence":"author hint: x on paper = what on computer?","lesson":"translate a familiar mark between physical and technical contexts"},
    {"puzzle":5,"answer":"48","class":"small-detail-counting","evidence":"four groups / eight grass blades under the mushroom","lesson":"count small visual sub-elements rather than naming the main object"},
    {"puzzle":5,"answer":"GCE","class":"cultural-reference","evidence":"moon/music image resolved through Moonlight Sonata / note context","lesson":"a picture can point to an external cultural reference and then a compact token"},
    {"puzzle":5,"answer":"Eris","class":"symbol-identification","evidence":"drawn glyph interpreted as the Eris symbol","lesson":"identify an exact symbol rather than use a generic visual label"},
    {"puzzle":5,"answer":"Umber","class":"franchise-reference","evidence":"author hint for GoT fans; heraldic/tree context","lesson":"external fictional context can disambiguate an otherwise generic drawing"},
    {"puzzle":5,"answer":"Castle","class":"secondary-detail-rebus","evidence":"tiny O-O marks on a log resolve to the chess term Castle","lesson":"the intended clue can be a secondary drawn detail, not the dominant object"},
    {"puzzle":5,"answer":"Picasso","class":"art-reference","evidence":"dove image points to Picasso's Dove of Peace","lesson":"visual resemblance can encode the creator/title, not the literal object"},
    {"puzzle":7,"answer":"Vivaldi","class":"cultural-reference","evidence":"four seasonal tree states plus V* hint","lesson":"combine image semantics with a small textual constraint"},
    {"puzzle":7,"answer":"227","class":"reference-to-number","evidence":"Life of Pi clue chain resolves to a numeric fact","lesson":"semantic identification can terminate in a number rather than a word"},
    {"puzzle":7,"answer":"Permanent","class":"technical-context","evidence":"object plus Arweave/permanence context","lesson":"overall platform/environment can be part of the clue"},
    {"puzzle":7,"answer":"Arnheim","class":"literature-reference","evidence":"visual/literary context","lesson":"literature and named works are recurring disambiguators"},
    {"puzzle":7,"answer":"Bulgakov","class":"literature-reference","evidence":"Behemoth clue chain to Master and Margarita author","lesson":"the final token can be one semantic hop away from the pictured/hinted entity"},
    {"puzzle":7,"answer":"1157","class":"sequence-pattern","evidence":"number/year series interpreted through eclipse context","lesson":"a visible numeric sequence can encode a rule and demand continuation"},
    {"puzzle":7,"answer":"Ulysses","class":"cross-domain-reference","evidence":"squirrel clue resolves through Flora & Ulysses / 2014 Newbery context","lesson":"apparently unrelated visual details can point to a named cultural object"},
    {"puzzle":7,"answer":"143176176209","class":"visual-number-extraction","evidence":"final pictured pattern resolves to a long numeric token","lesson":"literal numeric extraction is used when the image supplies a structured numeric cue"},
    {"puzzle":8,"answer":"Rasputin","class":"biographical-rebus","evidence":"story/image of a famous death","lesson":"identify the famous person implied by a narrative scene"},
    {"puzzle":8,"answer":"Wilhelm","class":"biographical-rebus","evidence":"historical death/context chain","lesson":"historical biography may supply the intended compact name"},
    {"puzzle":8,"answer":"Alekhine","class":"biographical-rebus","evidence":"chess/history death context","lesson":"recognition of a person from contextual facts can be the entire mechanism"},
]

AUTHOR_PATTERNS = [
    ("look_solved", r"Look at the solved puzzles"),
    ("format_invariant", r"format does not matter"),
    ("alternative_storage", r"alternative forms of storing a private key"),
    ("overall_picture", r"overall picture"),
    ("visual_context", r"visual context"),
    ("overall_environment", r"overall environment"),
    ("perimeter", r"Hint: perimeter"),
    ("no_programming", r"no programming required"),
    ("simple_math", r"2\+2=4"),
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"arweave11-stage11-research"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def extract_markers(text):
    out=[]
    for line in text.splitlines():
        if re.search(r"CORRECT (KEY VALUE|SOLUTION)", line, re.I):
            out.append(re.sub(r"\s+", " ", line.strip()))
    return out

def main():
    fetched={}
    for name,url in SOURCES.items():
        text=fetch(url)
        fetched[name]={"url":url,"bytes":len(text.encode()),"solution_markers":extract_markers(text)}

    author=AUTHOR_REPORT.read_text(encoding="utf-8")
    author_hits={name:bool(re.search(pattern,author,re.I)) for name,pattern in AUTHOR_PATTERNS}

    classes={}
    for item in MECHANISMS:
        classes[item["class"]]=classes.get(item["class"],0)+1

    semantic_classes={
        "medium-translation","cultural-reference","symbol-identification","franchise-reference",
        "secondary-detail-rebus","art-reference","technical-context","literature-reference",
        "cross-domain-reference","biographical-rebus"
    }
    numeric_classes={"small-detail-counting","sequence-pattern","visual-number-extraction","reference-to-number"}
    high_level={
        "semantic_or_contextual":sum(v for k,v in classes.items() if k in semantic_classes),
        "count_or_sequence":sum(v for k,v in classes.items() if k in numeric_classes),
    }

    implications=[
        {"rank":1,"claim":"Treat 321 first as a human-readable instruction/semantic clue, not as raw payload.","basis":"Solved examples are dominated by semantic rebuses, contextual interpretation, and tiny deliberate visual details."},
        {"rank":2,"claim":"Inspect secondary details around buildings and boats, not only dominant skyline shapes.","basis":"Puzzle #5 Castle came from tiny O-O marks on a log; #5 also used grass-blade counting."},
        {"rank":3,"claim":"Test order, count, perimeter, and environment readings of 3-2-1.","basis":"The author repeatedly used ordering, counting, perimeter, visual context, and overall-environment hints in the series."},
        {"rank":4,"claim":"Prefer clues that survive re-encoding and remain human-visible.","basis":"For #11 the author said format does not matter; the stable hatch-direction marker survives ordinary visual perturbation."},
    ]

    result={
        "experiment_id":"A11-EXP-011",
        "scope":"public solved-puzzle grammar reconstruction; no private-key generation or verification",
        "sources":fetched,
        "author_hint_presence":author_hits,
        "mechanisms":MECHANISMS,
        "class_counts":classes,
        "high_level_counts":high_level,
        "implications_for_puzzle11":implications,
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")

    md=[
        "# Stage 11 — solved-puzzle design grammar","",
        "**Experiment:** A11-EXP-011","",
        "This is public-source, non-cryptographic research. It does not generate, derive, reconstruct, enumerate, or verify private-key candidates.","",
        "## Why this stage exists","",
        "While discussing Puzzle #11 on 2020-04-23, the author explicitly told a solver to look at the solved puzzles. The same public archive also preserves the #11 hints that format does not matter and that the image demonstrates an alternative way of storing a private key. The goal here is therefore to learn the author's clue-design habits rather than continue treating every pixel transform as equally likely.","",
        "## Recovered solved-puzzle grammar","",
        "| puzzle | public solved token | mechanism | design lesson |",
        "|---:|:---|:---|:---|",
    ]
    for x in MECHANISMS:
        md.append(f"| #{x['puzzle']} | {x['answer']} | {x['class']} | {x['lesson']} |")
    md += ["","## Mechanism counts",""]
    for k,v in sorted(classes.items(),key=lambda kv:(-kv[1],kv[0])):
        md.append(f"- {k}: {v}")
    md += [
        "",
        f"- Broadly semantic/contextual examples: **{high_level['semantic_or_contextual']}**",
        f"- Counting/sequence/numeric-extraction examples: **{high_level['count_or_sequence']}**",
        "","## Implications for Puzzle #11","",
    ]
    for x in implications:
        md.append(f"{x['rank']}. **{x['claim']}** — {x['basis']}")
    md += [
        "","## Working conclusion","",
        "The solved-sibling evidence materially shifts the research priority toward human-readable semantics and deliberate secondary details. The robust skyline 0x321 marker should therefore be treated first as an instruction such as ordering, counting, or selection rather than as raw secret material. This does not prove that 321 is intentional; it defines the next bounded visual tests.",
        "","## Source checks","",
    ]
    for name,data in fetched.items():
        md.append(f"- {name}: {data['url']} — {len(data['solution_markers'])} explicit solved-value markers parsed.")
    (OUT/"REPORT.md").write_text("\n".join(md),encoding="utf-8")
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-011","mechanisms":len(MECHANISMS),"semantic_contextual":high_level["semantic_or_contextual"],"count_sequence":high_level["count_or_sequence"],"author_hint_presence":author_hits}))

if __name__=="__main__":
    main()
