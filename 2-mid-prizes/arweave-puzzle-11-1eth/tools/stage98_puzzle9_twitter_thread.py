#!/usr/bin/env python3
"""Stage 98: Puzzle #9 primary Twitter-thread reconstruction.

Safe public archival research only.

Seed: the primary-verified Wayback snapshot of the author's 2020-06-14 status
1272111084867129344 ("The puzzle required 4 steps...").

This stage reconstructs a bounded neighborhood of contemporaneous archived
Twitter statuses to see whether the author or solvers named any concrete solve
step. It does not infer a mechanism merely from visible image content.

No private-key generation, derivation, enumeration, reconstruction,
verification, or wallet access is performed.
"""
from __future__ import annotations

import concurrent.futures
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT=Path(__file__).resolve().parents[1]
RUN97=ROOT/"analysis"/"runs"/"stage97-puzzle9-semantic-anchors"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage98-puzzle9-twitter-thread"
OUT.mkdir(parents=True,exist_ok=True)

SEED_ID="1272111084867129344"
SEED_URL=f"https://twitter.com/ArweaveP/status/{SEED_ID}"
CDX="https://web.archive.org/cdx/search/cdx"
DOSSIERS=[
    "https://raw.githubusercontent.com/itsnex1s/crypto-puzzle-list/main/unsolved/arweave-puzzle-11-1eth.md",
    "https://raw.githubusercontent.com/itsnex1s/crypto-puzzle-list/main/unsolved/arweave-puzzle-3-1000ar.md",
]
DATE_FROM="20200608"
DATE_TO="20200615"
MAX_ARCHIVED_STATUSES=28
MAX_LINKED_IDS=18

GENERIC_TERMS=("puzzle","solver","solve","brute","step","dai","100 dai","silent")
MECHANISM_TERMS=("bird","birds","color","colour","clock","april","1984","twelve","13","12:05","quote","orwell","date","tree","parrot","order","sequence","read","extract","pixel","palette")

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; ArweavePuzzleResearch/1.0; public archival thread audit)"})

def clean_text(s):
    if not isinstance(s,str): return ""
    s=html.unescape(s)
    s=re.sub(r"<script\b[^>]*>.*?</script>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<style\b[^>]*>.*?</style>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",s).strip()

def get_text(url,timeout=16):
    r=S.get(url,timeout=timeout,allow_redirects=True)
    r.raise_for_status()
    return r.text,{"url":r.url,"status":r.status_code,"bytes":len(r.content)}

def cdx(url,from_=None,to=None,limit=100):
    params={
        "url":url,
        "output":"json",
        "filter":"statuscode:200",
        "fl":"timestamp,original,statuscode,digest",
        "collapse":"digest",
        "limit":str(limit),
    }
    if from_: params["from"]=from_
    if to: params["to"]=to
    try:
        r=S.get(CDX,params=params,timeout=20)
        r.raise_for_status()
        j=r.json()
        if not isinstance(j,list) or len(j)<2:
            return [],{"url":r.url,"rows":0}
        hdr=j[0]
        rows=[dict(zip(hdr,x)) for x in j[1:]]
        return rows,{"url":r.url,"rows":len(rows)}
    except Exception as e:
        return [],{"error":repr(e),"query":params}

def parse_status_html(raw,url):
    out={"snapshot_url":url}
    # Meta/title is usually the cleanest preserved tweet text in old Twitter HTML.
    title_m=re.search(r"<title[^>]*>(.*?)</title>",raw,re.I|re.S)
    title=html.unescape(re.sub(r"\s+"," ",title_m.group(1))).strip() if title_m else ""
    out["title"]=title

    desc=[]
    for pat in (
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']',
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description["\']',
    ):
        desc.extend(re.findall(pat,raw,re.I|re.S))
    out["descriptions"]=[html.unescape(re.sub(r"\s+"," ",x)).strip() for x in desc[:4]]

    body=clean_text(raw)
    # Keep a bounded text projection for audit.
    out["text_projection"]=body[:16000]

    ids=re.findall(r'(?:twitter\.com|x\.com)/([A-Za-z0-9_]+)/status/(\d+)',raw,re.I)
    out["linked_statuses"]=[{"handle":h,"id":sid} for h,sid in dict.fromkeys(ids)]

    fields={}
    for key,pat in (
        ("conversation_id",r'data-conversation-id=["\'](\d+)'),
        ("item_id",r'data-item-id=["\'](\d+)'),
        ("in_reply_to_status_id",r'data-in-reply-to-status-id=["\'](\d+)'),
        ("screen_name",r'data-screen-name=["\']([^"\']+)'),
    ):
        m=re.search(pat,raw,re.I)
        fields[key]=m.group(1) if m else None
    out.update(fields)

    # Infer tweet text from title first, stripping standard suffixes.
    text=title
    text=re.sub(r"^.*? on Twitter:\s*[“\"']?","",text,flags=re.I)
    text=re.sub(r"[”\"']?\s*/\s*Twitter\s*$","",text,flags=re.I)
    out["tweet_text_guess"]=text.strip()

    low=(title+" "+" ".join(out["descriptions"])+" "+body[:6000]).lower()
    out["generic_terms"]=[x for x in GENERIC_TERMS if x in low]
    out["mechanism_terms"]=[x for x in MECHANISM_TERMS if x in low]
    out["mentions_puzzle9"]=bool(re.search(r"puzzle\s*#?\s*9|100\s*dai",low))
    return out

def snapshot_for_row(row):
    ts=row.get("timestamp"); orig=row.get("original")
    if not ts or not orig: return None
    snap=f"https://web.archive.org/web/{ts}id_/{orig}"
    try:
        raw,info=get_text(snap,timeout=14)
        rec=parse_status_html(raw,info["url"])
        rec["timestamp"]=ts
        rec["original_url"]=orig
        rec["fetch"]=info
        return rec
    except Exception as e:
        return {"timestamp":ts,"original_url":orig,"snapshot_url":snap,"error":repr(e)}

def fetch_exact_status(handle,sid):
    url=f"https://twitter.com/{handle}/status/{sid}"
    rows,meta=cdx(url,from_="2020",to="2022",limit=8)
    if not rows and handle.lower()!="arweavep":
        rows2,meta2=cdx(f"https://twitter.com/ArweaveP/status/{sid}",from_="2020",to="2022",limit=8)
        if rows2:
            rows=rows2; meta=meta2
    rec=snapshot_for_row(rows[0]) if rows else None
    return {"handle":handle,"id":sid,"cdx":meta,"record":rec}

def dossier_context():
    rows=[]
    status_refs={}
    for url in DOSSIERS:
        rec={"url":url}
        try:
            t,info=get_text(url,timeout=18)
            rec["fetch"]=info
            low=t.lower()
            i=low.find("the puzzle required 4 steps")
            if i>=0:
                rec["four_step_context"]=re.sub(r"\s+"," ",t[max(0,i-1600):i+2600])
            refs=re.findall(r'https?://twitter\.com/([A-Za-z0-9_]+)/status/(\d+)',t,re.I)
            for h,sid in refs:
                status_refs[sid]=h
            rec["twitter_status_refs"]=len(refs)
        except Exception as e:
            rec["error"]=repr(e)
        rows.append(rec)
    return rows,status_refs

def main():
    r97=json.loads(RUN97.read_text())

    seed_snapshot=None
    for src in r97.get("source_records",[]):
        if src.get("kind")=="wayback" and src.get("verified"):
            seed_snapshot=src.get("snapshot")
            break

    if not seed_snapshot:
        rows,_=cdx(SEED_URL,from_="2020",to="2022",limit=10)
        if rows:
            seed_snapshot=f"https://web.archive.org/web/{rows[0]['timestamp']}id_/{rows[0]['original']}"
    if not seed_snapshot:
        raise SystemExit("verified seed snapshot unavailable")

    seed_raw,seed_fetch=get_text(seed_snapshot,timeout=20)
    seed=parse_status_html(seed_raw,seed_fetch["url"])
    seed["id"]=SEED_ID
    seed["fetch"]=seed_fetch

    dossiers,dossier_refs=dossier_context()

    # Discover archived ArweaveP statuses from the week around the #9 solve.
    week_rows,week_meta=cdx(
        "https://twitter.com/ArweaveP/status/*",
        from_=DATE_FROM,to=DATE_TO,limit=120
    )
    # Some CDX installations canonicalize lowercase handle separately.
    lower_rows,lower_meta=cdx(
        "https://twitter.com/arweavep/status/*",
        from_=DATE_FROM,to=DATE_TO,limit=120
    )
    dedup={}
    for row in week_rows+lower_rows:
        m=re.search(r"/status/(\d+)",row.get("original",""))
        if not m: continue
        sid=m.group(1)
        dedup.setdefault(sid,row)
    week_selected=list(dedup.values())[:MAX_ARCHIVED_STATUSES]

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        week_records=[x for x in ex.map(snapshot_for_row,week_selected) if x]

    # Seed-linked statuses + dossier-referenced statuses are higher-value.
    linked={}
    for x in seed.get("linked_statuses",[]):
        if x["id"]!=SEED_ID:
            linked[x["id"]]=x["handle"]
    if seed.get("in_reply_to_status_id"):
        linked[seed["in_reply_to_status_id"]]="ArweaveP"
    for sid,h in dossier_refs.items():
        if sid!=SEED_ID:
            linked.setdefault(sid,h)

    # Prioritize IDs numerically near seed, which often captures same thread.
    seed_n=int(SEED_ID)
    linked_items=sorted(linked.items(),key=lambda kv:abs(int(kv[0])-seed_n))[:MAX_LINKED_IDS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        linked_records=list(ex.map(lambda kv:fetch_exact_status(kv[1],kv[0]),linked_items))

    # Merge primary records by status id.
    primary={}
    primary[SEED_ID]=seed
    for rec in week_records:
        m=re.search(r"/status/(\d+)",rec.get("original_url",""))
        if m and not rec.get("error"):
            primary.setdefault(m.group(1),rec)
    for item in linked_records:
        rec=item.get("record")
        if rec and not rec.get("error"):
            primary.setdefault(item["id"],rec)

    # Identify relevant primary statuses conservatively.
    relevant=[]
    mechanism_specific=[]
    solve_context=[]
    for sid,rec in primary.items():
        generic=rec.get("generic_terms",[])
        mech=rec.get("mechanism_terms",[])
        p9=rec.get("mentions_puzzle9",False)
        if sid==SEED_ID or generic or p9 or mech:
            row={
                "id":sid,
                "title":rec.get("title"),
                "tweet_text_guess":rec.get("tweet_text_guess"),
                "timestamp":rec.get("timestamp"),
                "screen_name":rec.get("screen_name"),
                "conversation_id":rec.get("conversation_id"),
                "in_reply_to_status_id":rec.get("in_reply_to_status_id"),
                "generic_terms":generic,
                "mechanism_terms":mech,
                "mentions_puzzle9":p9,
                "snapshot_url":rec.get("snapshot_url"),
            }
            if mech:
                row["classification"]="MECHANISM_SPECIFIC_PRIMARY"
                mechanism_specific.append(row)
            else:
                row["classification"]="SOLVE_CONTEXT_PRIMARY"
                solve_context.append(row)
            relevant.append(row)

    # Guard: generic HTML/nav words such as "read" should not alone count as a
    # mechanism discovery. Require a mechanism term in the tweet title/description
    # projection, not just the full page shell.
    true_mech=[]
    for row in mechanism_specific:
        rec=primary[row["id"]]
        clean_primary=(rec.get("title","")+" "+" ".join(rec.get("descriptions",[]))).lower()
        terms=[t for t in MECHANISM_TERMS if t in clean_primary]
        if terms:
            row["mechanism_terms_primary_text"]=terms
            true_mech.append(row)
        else:
            row["classification"]="SOLVE_CONTEXT_PRIMARY"

    # A concrete new mechanism is promoted only if a non-seed primary status
    # explicitly names a visual/semantic step term.
    promoted_terms=sorted(set(
        t for row in true_mech if row["id"]!=SEED_ID
        for t in row.get("mechanism_terms_primary_text",[])
        if t not in ("13",)
    ))

    result={
        "experiment_id":"A11-EXP-098",
        "scope":"bounded primary archival reconstruction around Puzzle #9 solve; no private-key operations",
        "seed_status":{
            "id":SEED_ID,
            "snapshot":seed_snapshot,
            "title":seed.get("title"),
            "conversation_id":seed.get("conversation_id"),
            "in_reply_to_status_id":seed.get("in_reply_to_status_id"),
            "linked_status_count":len(seed.get("linked_statuses",[])),
        },
        "week_cdx":{
            "uppercase":week_meta,
            "lowercase":lower_meta,
            "unique_status_rows":len(dedup),
            "snapshots_attempted":len(week_selected),
        },
        "dossiers":dossiers,
        "linked_status_fetches":linked_records,
        "primary_status_count":len(primary),
        "relevant_primary_statuses":sorted(relevant,key=lambda x:(x.get("timestamp") or "",x["id"])),
        "mechanism_specific_primary_statuses":true_mech,
        "solve_context_primary_count":sum(1 for x in relevant if x.get("classification")=="SOLVE_CONTEXT_PRIMARY"),
        "promoted_mechanism_terms":promoted_terms,
        "decision":"MECHANISM_SPECIFIC_PRIMARY" if promoted_terms else "NO_NEW_MECHANISM",
        "interpretation_guard":"Only explicit mechanism terms in archived primary tweet title/description text can be promoted. Image-derived interpretations and secondary dossiers are context only.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    md=[
        "# Stage 98 — Puzzle #9 primary Twitter-thread reconstruction",
        "",
        "**Experiment:** A11-EXP-098",
        "",
        f"- seed snapshot: **{seed_snapshot}**",
        f"- seed conversation id: **{seed.get('conversation_id')}**",
        f"- seed reply-parent id: **{seed.get('in_reply_to_status_id')}**",
        f"- unique @ArweaveP CDX status rows in solve week: **{len(dedup)}**",
        f"- primary statuses recovered/parsed: **{len(primary)}**",
        f"- relevant primary statuses: **{len(relevant)}**",
        f"- primary statuses with explicit mechanism terms: **{len(true_mech)}**",
        f"- promoted mechanism terms: **{promoted_terms}**",
        f"- decision: **{result['decision']}**",
        "",
        "## Relevant primary statuses",
        "",
        "| id | class | timestamp | mechanism terms | title/text |",
        "|:---|:---|:---|:---|:---|",
    ]
    for row in sorted(relevant,key=lambda x:(x.get("timestamp") or "",x["id"])):
        title=(row.get("tweet_text_guess") or row.get("title") or "").replace("|","\\|")[:500]
        terms=",".join(row.get("mechanism_terms_primary_text") or row.get("mechanism_terms") or [])
        md.append(f"| {row['id']} | {row.get('classification')} | {row.get('timestamp') or ''} | {terms} | {title} |")

    md += ["","## Interpretation",""]
    if promoted_terms:
        md.append("At least one adjacent primary archived status names concrete mechanism language beyond the generic four-step/bruteforce statement. The next stage should test only those explicit terms against Puzzle #11.")
    else:
        md.append("The recovered primary neighborhood provides solve context but no concrete step names beyond the verified four-step/bruteforce statement. Do not invent a #9 solution from the birds/quote/date. Carry forward only the multi-step image-only prior.")

    md += [
        "",
        "No candidate secret material was produced or checked.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-098",
        "primary_statuses":len(primary),
        "relevant":len(relevant),
        "promoted_terms":promoted_terms,
        "decision":result["decision"],
    }))

if __name__=="__main__":
    main()
