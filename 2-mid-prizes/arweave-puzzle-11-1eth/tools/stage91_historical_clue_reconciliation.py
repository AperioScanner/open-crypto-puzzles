#!/usr/bin/env python3
"""Stage 91: historical public solver-clue reconciliation.

Public-source archival audit only. Fetches the Puzzling StackExchange thread via
the public API, fetches the HomelessPhD PZL11 dossier, inventories a predeclared
set of historical clue claims, and reconciles them against this branch's own
analysis/tools ledger.

No private-key generation, derivation, reconstruction, enumeration, verification,
or wallet access is performed.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis"/"runs"/"stage91-historical-clue-reconciliation"
OUT.mkdir(parents=True,exist_ok=True)

QUESTION_ID=97537
API="https://api.stackexchange.com/2.3"
DOSSIER="https://raw.githubusercontent.com/HomelessPhD/AR_Puzzles/main/PZL11/README.md"

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0; public archival audit)"})

CANDIDATES=[
    {
        "id":"alpha_ring_big_boat",
        "label":"alpha anomalies/ring around large boat",
        "source_patterns":[r"434 pixels",r"alpha values?.{0,80}255",r"cycle.{0,80}ship",r"ring.{0,80}alpha"],
        "coverage_patterns":[r"434 non-opaque",r"alpha channel",r"anti-aliasing halo",r"alpha.*exhausted"],
        "retire_patterns":[r"alpha channel.*exhausted",r"anti-aliasing halo",r"compositing explanation"],
        "priority":0,
    },
    {
        "id":"first_row_anomalies",
        "label":"anomalous first image row",
        "source_patterns":[r"first row",r"147 anomalous"],
        "coverage_patterns":[r"stage 7",r"stage7_",r"stage 9",r"stage9_",r"first.row.*steg",r"first_row_visual_strip"],
        "retire_patterns":[],
        "priority":0,
    },
    {
        "id":"create_modify_203_seconds",
        "label":"create/modify timestamps differ by 203 seconds",
        "source_patterns":[r"203 seconds",r"datecreate",r"datemodify",r"modification date.{0,80}203"],
        "coverage_patterns":[r"203 seconds",r"datecreate",r"datemodify"],
        "retire_patterns":[r"shared only with a sibling puzzle",r"timestamp anomaly.*shared"],
        "priority":1,
    },
    {
        "id":"five_seven_skyline_split",
        "label":"5 buildings left / 7 buildings right",
        "source_patterns":[r"5 buildings left",r"7 buildings right",r"five buildings left",r"seven buildings right"],
        "coverage_patterns":[r"5 buildings left",r"7 buildings right",r"five.seven skyline",r"5/7 skyline",r"skyline split"],
        "retire_patterns":[],
        "priority":5,
    },
    {
        "id":"pier_roman_numeral",
        "label":"pier/supports resemble X / IX / XI Roman numerals",
        "source_patterns":[r"pier.{0,120}(?:ix|xi|roman|numeral)",r"roman numeral",r"\bIX\b.{0,80}\bXI\b"],
        "coverage_patterns":[r"pier.{0,100}(?:roman|numeral|ix|xi)",r"roman numeral"],
        "retire_patterns":[],
        "priority":4,
    },
    {
        "id":"building_hv_lines",
        "label":"buildings alternate horizontal/vertical hatch directions",
        "source_patterns":[r"horizontal lines.{0,100}vertical lines",r"buildings have horizontal",r"vertical lines"],
        "coverage_patterns":[r"HHVVHHVHHHHV",r"independent H/V",r"stage 21",r"stage21_",r"format-stable visual pattern"],
        "retire_patterns":[],
        "priority":0,
    },
    {
        "id":"source_photo_hypothesis",
        "label":"sketch may derive from an identifiable source photograph",
        "source_patterns":[r"sketch derived from a photograph",r"similar kind of puzzle.{0,100}sketch",r"sailing race/event",r"photo online somewhere"],
        "coverage_patterns":[r"source photograph",r"source-photo",r"photo origin",r"image provenance.*photograph"],
        "retire_patterns":[],
        "priority":3,
    },
    {
        "id":"filename_32_bytes",
        "label":"Arweave/file identifier decodes to 32 bytes",
        "source_patterns":[r"name of the file.{0,160}32 bytes",r"base85.{0,100}32 bytes",r"decoded to 32 bytes"],
        "coverage_patterns":[r"filename.{0,100}32 bytes",r"base85",r"tx id.{0,100}32 bytes",r"transaction id.{0,100}32 bytes"],
        "retire_patterns":[],
        "priority":2,
    },
    {
        "id":"boat_counts",
        "label":"1 large boat / 5 small boats",
        "source_patterns":[r"1 big boat",r"5 small boats",r"one big boat",r"five small boats"],
        "coverage_patterns":[r"large_sailboat",r"small sail",r"stage 18",r"stage18_",r"stage 19",r"stage19_"],
        "retire_patterns":[],
        "priority":0,
    },
    {
        "id":"cryptocanvas_reverse_image",
        "label":"reverse-image search leads to CryptoCanvas/OpenSea",
        "source_patterns":[r"reverse image searched",r"cryptocanvas",r"opensea.io/collection/cryptocanvas"],
        "coverage_patterns":[r"stage 89",r"stage89_",r"stage 90",r"stage90_",r"CONFIRMED_POSTPUBLICATION_MIRROR"],
        "retire_patterns":[r"CONFIRMED_POSTPUBLICATION_MIRROR",r"post-publication mirror"],
        "priority":0,
    },
]

def strip_html(s):
    if not isinstance(s,str): return ""
    s=re.sub(r"<br\s*/?>","\n",s,flags=re.I)
    s=re.sub(r"<[^>]+>"," ",s)
    return html.unescape(re.sub(r"\s+"," ",s)).strip()

def api_get(path,params=None):
    p={"site":"puzzling","pagesize":100,"filter":"withbody"}
    if params: p.update(params)
    r=S.get(API+path,params=p,timeout=30)
    r.raise_for_status()
    return r.json(),{"url":r.url,"status":r.status_code,"bytes":len(r.content)}

def fetch_stackexchange():
    corpus=[]
    raw={}
    q,qi=api_get(f"/questions/{QUESTION_ID}")
    raw["question_fetch"]=qi
    raw["question"]=q
    for item in q.get("items",[]):
        corpus.append({"kind":"question","id":item.get("question_id"),"text":strip_html(item.get("body",""))})

    qc,qci=api_get(f"/questions/{QUESTION_ID}/comments")
    raw["question_comments_fetch"]=qci
    raw["question_comments"]=qc
    for item in qc.get("items",[]):
        corpus.append({"kind":"question_comment","id":item.get("comment_id"),"text":strip_html(item.get("body",""))})

    ans,ai=api_get(f"/questions/{QUESTION_ID}/answers")
    raw["answers_fetch"]=ai
    raw["answers"]=ans
    ids=[]
    for item in ans.get("items",[]):
        aid=item.get("answer_id")
        ids.append(aid)
        corpus.append({"kind":"answer","id":aid,"text":strip_html(item.get("body",""))})
    if ids:
        joined=";".join(str(x) for x in ids)
        ac,aci=api_get(f"/answers/{joined}/comments")
        raw["answer_comments_fetch"]=aci
        raw["answer_comments"]=ac
        for item in ac.get("items",[]):
            corpus.append({"kind":"answer_comment","id":item.get("comment_id"),"text":strip_html(item.get("body",""))})
    return corpus,raw

def fetch_dossier():
    r=S.get(DOSSIER,timeout=30)
    r.raise_for_status()
    return r.text,{"url":r.url,"status":r.status_code,"bytes":len(r.content)}

def repo_texts():
    roots=[ROOT/"analysis",ROOT/"tools",ROOT/"data",ROOT/"README.md"]
    rows=[]
    exts={".md",".json",".py",".txt",".yml",".yaml"}
    for root in roots:
        paths=[root] if root.is_file() else list(root.rglob("*"))
        for p in paths:
            if not p.is_file() or p.suffix.lower() not in exts: continue
            # Avoid Stage91's own generated results and huge non-text artifacts.
            if "stage91-historical-clue-reconciliation" in str(p): continue
            try:
                t=p.read_text(errors="ignore")
            except Exception:
                continue
            rows.append({"path":str(p.relative_to(ROOT)),"text":t})
    return rows

def pattern_hits(patterns,text):
    hits=[]
    for pat in patterns:
        m=re.search(pat,text,re.I|re.S)
        if m:
            a=max(0,m.start()-120); b=min(len(text),m.end()+160)
            hits.append({"pattern":pat,"excerpt":re.sub(r"\s+"," ",text[a:b]).strip()})
    return hits

def main():
    corpus,stackraw=fetch_stackexchange()
    dossier,dossier_info=fetch_dossier()
    source_docs=list(corpus)+[{"kind":"dossier","id":"HomelessPhD/PZL11","text":dossier}]
    repo=repo_texts()

    source_all="\n".join(x["text"] for x in source_docs)
    repo_all="\n".join(x["text"] for x in repo)

    results=[]
    for cand in CANDIDATES:
        src=pattern_hits(cand["source_patterns"],source_all)
        cover=pattern_hits(cand["coverage_patterns"],repo_all)
        retire=pattern_hits(cand["retire_patterns"],repo_all) if cand["retire_patterns"] else []

        # Find concrete repo paths, not only corpus-wide excerpts.
        path_hits=[]
        for row in repo:
            if any(re.search(p,row["text"],re.I|re.S) for p in cand["coverage_patterns"]):
                path_hits.append(row["path"])
        path_hits=path_hits[:15]

        if not src:
            status="ABSENT_FROM_FETCH"
        elif retire:
            status="RETIRED_BY_LATER_EVIDENCE"
        elif cover:
            # Objective historical claims can be present in docs without a dedicated
            # test; distinguish mentions from actual stage/tool coverage.
            stageish=any(("analysis/runs/" in p or "/tools/" in p or p.startswith("tools/")) for p in path_hits)
            status="COVERED" if stageish else "PARTIAL"
        else:
            status="UNTESTED"

        results.append({
            "id":cand["id"],
            "label":cand["label"],
            "status":status,
            "priority":cand["priority"],
            "source_hits":src[:8],
            "coverage_hits":cover[:8],
            "retirement_hits":retire[:8],
            "coverage_paths":path_hits,
        })

    promoted=sorted(
        [r for r in results if r["status"]=="UNTESTED"],
        key=lambda r:(-r["priority"],r["id"])
    )
    partial=sorted(
        [r for r in results if r["status"]=="PARTIAL"],
        key=lambda r:(-r["priority"],r["id"])
    )

    result={
        "experiment_id":"A11-EXP-091",
        "scope":"public historical solver-discussion reconciliation against branch evidence; no private-key operations",
        "sources":{
            "stackexchange_question_id":QUESTION_ID,
            "stackexchange_records":len(corpus),
            "dossier":DOSSIER,
            "dossier_fetch":dossier_info,
        },
        "candidates":results,
        "untested_ranked":[{"id":r["id"],"label":r["label"],"priority":r["priority"]} for r in promoted],
        "partial_ranked":[{"id":r["id"],"label":r["label"],"priority":r["priority"]} for r in partial],
        "decision_rule":"Only source-observed claims with no direct repository coverage are UNTESTED. RETIRED_BY_LATER_EVIDENCE outranks source novelty. Next adaptive stage should select the highest-priority objective visible/semantic UNTESTED claim, not a private-key interpretation.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    (OUT/"stackexchange-public.json").write_text(json.dumps(stackraw,indent=2,ensure_ascii=False)+"\n")

    counts={}
    for r in results: counts[r["status"]]=counts.get(r["status"],0)+1

    md=[
        "# Stage 91 — historical solver-clue reconciliation",
        "",
        "**Experiment:** A11-EXP-091",
        "",
        f"- StackExchange records recovered: **{len(corpus)}**",
        f"- Historical claims audited: **{len(results)}**",
        f"- Status counts: **{counts}**",
        "",
        "## Reconciliation",
        "",
        "| claim | status | priority | repo evidence paths |",
        "|:---|:---|---:|:---|",
    ]
    for r in sorted(results,key=lambda z:(-z["priority"],z["id"])):
        paths=", ".join(r["coverage_paths"][:4])
        md.append(f"| {r['label']} | **{r['status']}** | {r['priority']} | {paths} |")

    md += ["","## Ranked genuinely untested claims",""]
    if promoted:
        for i,r in enumerate(promoted,1):
            md.append(f"{i}. **{r['label']}** (`{r['id']}`, priority {r['priority']})")
    else:
        md.append("None.")

    md += [
        "",
        "## Interpretation",
        "",
        "This stage is a source/coverage delta audit, not a solve. It prevents recycling historical ideas already exhausted in the branch and identifies which public observations, if any, still justify a bounded visual/semantic experiment.",
        "",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-091",
        "counts":counts,
        "untested":[r["id"] for r in promoted],
        "partial":[r["id"] for r in partial],
    }))

if __name__=="__main__":
    main()
