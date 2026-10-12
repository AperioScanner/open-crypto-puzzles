#!/usr/bin/env python3
"""Stage 114: reconstruct the original Puzzle #9 Reddit discussion.

Primary target:
  https://www.reddit.com/r/ethtrader/comments/ersf73
  "100 DAI hidden in this image" (2020-01-21)

Purpose:
- recover contemporaneous pre-solve mechanism discussion absent from the
  Twitter-focused Stages 96-98;
- distinguish OP/author replies from community speculation;
- separate pre-solve from post-solve comments after the 2020-06-08 sweep;
- identify only corroborated mechanism evidence.

Safe archival scope only. No private-key generation, derivation,
reconstruction, enumeration, verification, or wallet access.
"""
from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis"/"runs"/"stage114-puzzle9-reddit-thread"
OUT.mkdir(parents=True,exist_ok=True)
SNAPSHOT=ROOT/"clues"/"puzzle9-reddit-thread-public-snapshot.json"

THREAD_ID="ersf73"
THREAD_URL=f"https://www.reddit.com/r/ethtrader/comments/{THREAD_ID}"
EXPECTED_ARWEAVE="1--NRFY3naNwTlxBSRjzDPNUq-Cn1yLG2RmgGHZem9c"
SOLVE_TS=datetime(2020,6,8,6,36,33,tzinfo=timezone.utc).timestamp()
UA="Mozilla/5.0 arweave-puzzle-research/1.0"

TERMS={
    "date_time":[r"05[\s,./:-]*04",r"2012",r"13[:\s]*00",r"thirteen",r"clock",r"date",r"time"],
    "birds_colors":[r"bird",r"orange",r"green",r"yellow",r"red",r"blue",r"facing",r"left",r"right",r"angle"],
    "literary":[r"orwell",r"1984",r"bright cold day",r"winston"],
    "lines_geometry":[r"invisible",r"\b9\s+lines?\b",r"lines?",r"angle",r"leaf",r"leaves"],
    "stego_pixel":[r"least significant",r"\blsb\b",r"stegan",r"pixel",r"bit"],
    "solve_status":[r"solved",r"solve",r"decrypt",r"got it",r"claim",r"winner"],
}

def fetch(url,timeout=22):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json,text/html;q=0.9,*/*;q=0.8"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read(),dict(r.headers),r.geturl()

def flatten_reddit(children,out,parent=None):
    for child in children or []:
        if child.get("kind")!="t1":
            continue
        d=child.get("data",{})
        row={
            "id":d.get("id"),
            "parent_id":d.get("parent_id") or parent,
            "author":d.get("author"),
            "body":d.get("body") or "",
            "created_utc":d.get("created_utc"),
            "score":d.get("score"),
            "permalink":d.get("permalink"),
        }
        out.append(row)
        rep=d.get("replies")
        if isinstance(rep,dict):
            flatten_reddit(rep.get("data",{}).get("children",[]),out,row["id"])

def verified_snapshot():
    """Load the controller-verified canonical Reddit snapshot.

    GitHub-hosted runners can be blocked by Reddit/Wayback even when the
    canonical page is publicly retrievable. The checked-in snapshot records
    only public mechanism-relevant comments and stable comment IDs verified
    against the canonical Reddit HTML. This is a source-recovery fallback, not
    a claim that the comments are author clues.
    """
    try:
        s=json.loads(SNAPSHOT.read_text())
        if s.get("thread_id")!=THREAD_ID:
            raise ValueError("snapshot thread id mismatch")
        comments=[]
        for x in s.get("comments",[]):
            comments.append({
                "id":x.get("id"),
                "parent_id":None,
                "author":x.get("author"),
                "body":x.get("body") or "",
                "created_utc":None,
                "score":None,
                "permalink":f"/r/ethtrader/comments/{THREAD_ID}/comment/{x.get('id')}/",
                "phase":x.get("phase"),
            })
        return {
            "ok":True,
            "source_mode":"verified_public_snapshot",
            "source_url":s.get("canonical_url"),
            "submission":{
                "id":THREAD_ID,
                "title":s.get("title"),
                "author":s.get("author"),
                "created_utc":None,
                "url":s.get("arweave_url"),
                "selftext":s.get("arweave_url") or "",
                "permalink":f"/r/ethtrader/comments/{THREAD_ID}/",
            },
            "comments":comments,
            "snapshot_verified_at":s.get("verified_at_utc"),
        }
    except Exception as e:
        return {"ok":False,"error":f"{type(e).__name__}: {e}","comments":[]}

def reddit_json():
    urls=[
        THREAD_URL+".json?raw_json=1&limit=500",
        "https://old.reddit.com/r/ethtrader/comments/ersf73/.json?raw_json=1&limit=500",
        "https://www.reddit.com/comments/ersf73.json?raw_json=1&limit=500",
    ]
    errors=[]
    for url in urls:
        try:
            raw,headers,final=fetch(url)
            data=json.loads(raw.decode("utf-8","replace"))
            sub=data[0]["data"]["children"][0]["data"]
            comments=[]
            flatten_reddit(data[1]["data"]["children"],comments)
            return {
                "ok":True,
                "source_url":final,
                "submission":{
                    "id":sub.get("id"),
                    "title":sub.get("title"),
                    "author":sub.get("author"),
                    "created_utc":sub.get("created_utc"),
                    "url":sub.get("url"),
                    "selftext":sub.get("selftext") or "",
                    "permalink":sub.get("permalink"),
                },
                "comments":comments,
            }
        except Exception as e:
            errors.append(f"{url}: {type(e).__name__}: {e}")
    return {"ok":False,"errors":errors,"comments":[]}

def wayback_snapshots():
    cdx=(
        "https://web.archive.org/cdx/search/cdx?"
        +urllib.parse.urlencode({
            "url":"www.reddit.com/r/ethtrader/comments/ersf73*",
            "output":"json",
            "filter":"statuscode:200",
            "collapse":"digest",
            "from":"2020",
            "to":"2021",
        })
    )
    try:
        raw,_,_=fetch(cdx,25)
        rows=json.loads(raw.decode("utf-8","replace"))
        if not rows or len(rows)<2:
            return {"ok":False,"snapshots":[],"error":"no CDX rows"}
        header=rows[0]
        items=[dict(zip(header,r)) for r in rows[1:]]
        # At most 6 snapshots spread across archive order.
        if len(items)>6:
            idx=np.linspace(0,len(items)-1,6).round().astype(int).tolist()
            items=[items[i] for i in sorted(set(idx))]
        return {"ok":True,"snapshots":items}
    except Exception as e:
        return {"ok":False,"snapshots":[],"error":f"{type(e).__name__}: {e}"}

def categories(body):
    b=body.lower()
    hits=[]
    for cat,patterns in TERMS.items():
        if any(re.search(p,b,re.I) for p in patterns):
            hits.append(cat)
    return hits

def iso(ts):
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(float(ts),tz=timezone.utc).isoformat()
    except Exception:
        return None

def clean_text(s,maxlen=1200):
    s=html.unescape(s or "")
    s=re.sub(r"\s+"," ",s).strip()
    return s[:maxlen]

def main():
    live=reddit_json()
    if live.get("ok"):
        rj=live
        rj["source_mode"]="live_reddit_json"
    else:
        rj=verified_snapshot()
        rj["live_reddit_errors"]=live.get("errors",[])
    wb=wayback_snapshots()

    submission=rj.get("submission") or {}
    comments=rj.get("comments",[])
    op=submission.get("author")

    relevant=[]
    for c in comments:
        body=clean_text(c.get("body"))
        cats=categories(body)
        if not cats:
            continue
        ts=c.get("created_utc")
        phase=c.get("phase") or ("post_solve" if ts and float(ts)>=SOLVE_TS else "pre_solve")
        relevant.append({
            "id":c.get("id"),
            "parent_id":c.get("parent_id"),
            "author":c.get("author"),
            "is_op":bool(op and c.get("author")==op),
            "phase":phase,
            "created_utc":ts,
            "created_iso":iso(ts),
            "score":c.get("score"),
            "categories":cats,
            "body":body,
            "permalink":c.get("permalink"),
        })

    op_mechanism=[
        x for x in relevant
        if x["is_op"] and any(cat!="solve_status" for cat in x["categories"])
    ]

    # A strong community path must span at least 3 independent mechanism
    # categories and have same-author post-solve corroboration.
    by_author={}
    for x in relevant:
        a=x.get("author")
        if not a or a in ("[deleted]","AutoModerator"):
            continue
        by_author.setdefault(a,[]).append(x)

    corroborated=[]
    mechanism_cats={"date_time","birds_colors","literary","lines_geometry","stego_pixel"}
    for author,rows in by_author.items():
        pre=[x for x in rows if x["phase"]=="pre_solve"]
        post=[x for x in rows if x["phase"]=="post_solve"]
        for x in pre:
            cats=set(x["categories"]) & mechanism_cats
            if len(cats)>=3 and any("solve_status" in y["categories"] for y in post):
                corroborated.append({
                    "author":author,
                    "pre_comment_id":x["id"],
                    "pre_categories":sorted(cats),
                    "post_comment_ids":[y["id"] for y in post if "solve_status" in y["categories"]],
                })

    title_ok="100 dai hidden in this image" in (submission.get("title") or "").lower()
    url_blob=" ".join([
        submission.get("url") or "",
        submission.get("selftext") or "",
        json.dumps([x.get("body","") for x in comments[:200]])
    ])
    arweave_ok=EXPECTED_ARWEAVE in url_blob
    source_control=bool(rj.get("ok") and title_ok and arweave_ok and len(comments)>=6)

    promoted=bool(source_control and (op_mechanism or corroborated))
    decision=(
        "PRIMARY_AUTHOR_MECHANISM" if op_mechanism
        else "CORROBORATED_COMMUNITY_PATH" if corroborated
        else "NO_CORROBORATED_MECHANISM"
    )

    # Save bounded public archival material only.
    result={
        "experiment_id":"A11-EXP-114",
        "scope":"reconstruction of original Puzzle #9 Reddit discussion and mechanism-evidence classification; no private-key operations",
        "thread_url":THREAD_URL,
        "source_recovered":bool(rj.get("ok")),
        "source_mode":rj.get("source_mode"),
        "reddit_source_url":rj.get("source_url"),
        "live_reddit_json_ok":bool(live.get("ok")),
        "live_reddit_errors":live.get("errors",[]),
        "snapshot_verified_at":rj.get("snapshot_verified_at"),
        "submission":{
            "title":submission.get("title"),
            "author":submission.get("author"),
            "created_iso":iso(submission.get("created_utc")),
            "url":submission.get("url"),
        },
        "comment_count":len(comments),
        "relevant_comment_count":len(relevant),
        "pre_solve_relevant":sum(x["phase"]=="pre_solve" for x in relevant),
        "post_solve_relevant":sum(x["phase"]=="post_solve" for x in relevant),
        "op_mechanism_comment_ids":[x["id"] for x in op_mechanism],
        "corroborated_paths":corroborated,
        "wayback_cdx_ok":bool(wb.get("ok")),
        "wayback_snapshot_count":len(wb.get("snapshots",[])),
        "wayback_snapshots":[
            {"timestamp":x.get("timestamp"),"original":x.get("original"),"digest":x.get("digest")}
            for x in wb.get("snapshots",[])
        ],
        "source_control":{
            "source_recovered":bool(rj.get("ok")),
            "source_mode":rj.get("source_mode"),
            "title_ok":title_ok,
            "arweave_tx_ok":arweave_ok,
            "passed":source_control,
        },
        "decision":decision,
        "promoted":promoted,
        "promotion_rule":"source control passes and either a mechanism-specific OP/author reply exists or a pre-solve >=3-category community path is independently corroborated by a same-author post-solve solve-status comment",
        "interpretation_guard":"Uncorroborated Reddit comments remain community hypotheses, not author clues or proven Puzzle #9 steps.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    (OUT/"relevant-comments.json").write_text(json.dumps(relevant,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 114 — original Puzzle #9 Reddit-thread reconstruction",
        "",
        "**Experiment:** A11-EXP-114",
        "",
        f"- source recovered: **{rj.get('ok',False)}** ({rj.get('source_mode')})",
        f"- source control passed: **{source_control}**",
        f"- thread author/OP: **{op}**",
        f"- comments recovered: **{len(comments)}**",
        f"- mechanism-relevant comments: **{len(relevant)}**",
        f"- relevant pre-solve / post-solve: **{sum(x['phase']=='pre_solve' for x in relevant)} / {sum(x['phase']=='post_solve' for x in relevant)}**",
        f"- mechanism-specific OP replies: **{len(op_mechanism)}**",
        f"- corroborated community paths: **{len(corroborated)}**",
        f"- Wayback CDX snapshots indexed: **{len(wb.get('snapshots',[]))}**",
        f"- decision: **{decision}**",
        f"- promoted: **{promoted}**",
        "",
        "## Relevant public comments",
        "",
        "| date | author | OP | phase | categories | excerpt |",
        "|:---|:---|:---:|:---|:---|:---|",
    ]
    for x in relevant[:80]:
        excerpt=x["body"].replace("|","\\|")[:220]
        md.append(
            f"| {x['created_iso'] or ''} | {x['author'] or ''} | {x['is_op']} | "
            f"{x['phase']} | {','.join(x['categories'])} | {excerpt} |"
        )

    md += ["","## Interpretation",""]
    if not source_control:
        md.append("The primary thread could not be recovered with the expected title, Arweave link, and minimum verified comment set. Stage 114 is an implementation/source-recovery failure and must be repaired before interpretation.")
    elif op_mechanism:
        md.append("At least one mechanism-specific OP reply was recovered. Treat it as new primary evidence and reconcile it against Puzzle #11 only after contextual review.")
    elif corroborated:
        md.append("A concrete pre-solve community path has same-author post-solve corroboration. It is stronger than ordinary speculation but still requires manual contextual review before transferring any mechanism to Puzzle #11.")
    else:
        md.append("The thread provides contemporaneous community hypotheses but no author-confirmed or independently corroborated solve path. Record the ideas as historical context only; do not promote them as Puzzle #9 mechanism evidence.")

    md += [
        "",
        "No candidate private key was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-114",
        "source_control":source_control,
        "comments":len(comments),
        "relevant":len(relevant),
        "op_mechanism":len(op_mechanism),
        "corroborated":len(corroborated),
        "decision":decision,
        "promoted":promoted,
    }))

if __name__=="__main__":
    # numpy is imported lazily here only for optional Wayback sampling.
    import numpy as np
    main()
