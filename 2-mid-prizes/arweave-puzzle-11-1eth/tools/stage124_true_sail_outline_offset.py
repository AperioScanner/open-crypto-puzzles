#!/usr/bin/env python3
"""A11-EXP-124 — five true small sails' mast-to-outline offset (visual only).

Independent of old Stage 102's Hough/Sobel hatch direction: that Stage used the
wrong object set via Stage 19 (spurious x~675 and omitted x~1490). This audit
uses all five true small sail apex sites, and asks whether triangular OUTLINE
bases systematically offset left/right relative to their apices, or whether
the apparent sides are ordinary perspective/drawing variation.

All sites, thresholds, control shapes, and stopping rules are preregistered.
This program does not derive or check mnemonic phrases, keys or wallet assets.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage124-true-sail-outline-offset"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
# Stage 122's manually checked sail apex sites: x, y, apparent sail height/half-width.
# The old Stage 102 invalid object set is NOT reused.
SITES=(
    ("small_1",1042,448,98,35),
    ("small_2",1148,433,99,38),
    ("small_3",1282,411,103,44),
    ("small_4",1372,397,101,42),
    ("small_5",1490,357,106,47),
)
VARIANTS=("original","jpeg85","jpeg70","down75_up")
THRESHOLD=175
WEDGE_SEARCH_FRACTION=.56
MIN_ROW_SUPPORT=.55
LEAD_GATE=.28
NEUTRAL_GATE=.16
CONTROL_BASE_OFFSET=.65

def analyze_one(gray,site,mode):
    name,cx,top,h,half=site
    if mode=="ink":
        measure=gray < THRESHOLD
    elif mode=="edge":
        measure=cv2.Canny(gray,60,150)>0
    else:
        raise ValueError(mode)
    observed=[]
    valid_rows=0
    total_rows=0
    for y in range(top+int(.39*h),top+int(.73*h)):
        total_rows+=1
        t=(y-(top+3))/max(1,h-3)
        predleft=cx-half*t
        predright=cx+half*t
        band=max(8,int(round(WEDGE_SEARCH_FRACTION*half)))
        vals=[]
        for pred,left in ((predleft,True),(predright,False)):
            xa=max(0,int(round(pred-band)))
            xb=min(gray.shape[1],int(round(pred+band+1)))
            loc=np.flatnonzero(measure[y,xa:xb])
            if not len(loc):
                vals.append(None)
                continue
            # Envelope edge of a triangular sail: not a shading histogram.
            val=(loc[0] if left else loc[-1])+xa
            vals.append(float(val))
        if None in vals:
            continue
        L,R=vals
        if not .45*2*half*t <= R-L <= 2.35*2*half*t:
            continue
        # Project the envelope midpoint at depth t back to the base.
        est=((L+R)*.5-cx)/max(t,.15)/half
        observed.append(float(est))
        valid_rows+=1
    enough=total_rows>0 and valid_rows/total_rows>=MIN_ROW_SUPPORT
    val=float(np.median(observed)) if observed and enough else None
    return {
        "method":mode,"valid_rows":valid_rows,"total_rows":total_rows,
        "support":round(valid_rows/max(1,total_rows),4),
        "normalized_base_offset":round(val,5) if val is not None else None,
        "valid":bool(enough),
    }

def draw_control(site,kind):
    _,cx,top,h,half=site
    a=np.full((1105,1600),255,np.uint8)
    off={"L":-CONTROL_BASE_OFFSET,"N":0.,"R":CONTROL_BASE_OFFSET}[kind]*half
    apex=(cx,top+3)
    left=(int(round(cx-half+off)),top+h-4)
    right=(int(round(cx+half+off)),top+h-4)
    cv2.line(a,apex,left,0,2,cv2.LINE_AA)
    cv2.line(a,apex,right,0,2,cv2.LINE_AA)
    cv2.line(a,left,right,0,2,cv2.LINE_AA)
    # Seeded interior hatching: a distracting texture, not a second outline.
    rng=np.random.default_rng(120000+cx+{"L":1,"N":2,"R":3}[kind])
    for i in range(9):
        fraction=float(rng.uniform(.18,.80))
        tx=(1-fraction)*apex[0]+fraction*(
            left[0]*(i/8)+right[0]*(1-i/8))
        ty=(1-fraction)*apex[1]+fraction*(top+h-4)
        cv2.line(a,(int(round(tx)),int(round(ty))),
                 (int(round(tx+rng.uniform(-5,5))),int(round(ty+rng.uniform(6,17)))),
                 0,1,cv2.LINE_AA)
    return a

def controls():
    cases=[]
    failures=[]
    for site in SITES:
        for kind in ("L","N","R"):
            transformed=variants(draw_control(site,kind))
            for name in VARIANTS:
                for mode in ("ink","edge"):
                    score=analyze_one(transformed[name],site,mode)
                    x=score["normalized_base_offset"]
                    expected=kind
                    cls=("?" if x is None else
                         "L" if x<=-LEAD_GATE else
                         "R" if x>=LEAD_GATE else
                         "N" if abs(x)<=NEUTRAL_GATE else "?")
                    accepted=score["valid"] and cls==expected
                    row={"site":site[0],"expected":expected,"variant":name,
                         "method":mode,"observed":cls,"score":x,"passed":bool(accepted)}
                    cases.append(row)
                    if not accepted:
                        failures.append(row)
    return {"case_count":len(cases),"passes":len(cases)-len(failures),
            "passed":len(failures)==0,"failures":failures[:35],
            "sample_cases":cases[:12]}

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:
        raise SystemExit("canonical image hash mismatch")
    img=np.array(Image.open(SOURCE).convert("L"))
    if img.shape!=(1105,1600):
        raise SystemExit("canonical dimensions differ")
    calibration=controls()
    altered=variants(img)
    sites=[]
    for site in SITES:
        per={}
        values=[]
        for name in VARIANTS:
            per[name]={mode:analyze_one(altered[name],site,mode)
                       for mode in ("ink","edge")}
            values.extend([per[name][m]["normalized_base_offset"]
                           for m in ("ink","edge")])
        all_valid=all(x is not None for x in values)
        valid_class=("?" if not all_valid else
                     "L" if max(values)<=-LEAD_GATE else
                     "R" if min(values)>=LEAD_GATE else
                     "N" if max(abs(v) for v in values)<=NEUTRAL_GATE else "?")
        sites.append({
            "sail":site[0],"apex_site":[site[1],site[2]],
            "apparent_height":site[3],"half_base_width":site[4],
            "variants":per,"range":[round(min(values),5),round(max(values),5)]
            if all_valid else None,
            "stable_class":valid_class if valid_class!="?" else None,
        })
    leaning=[x["stable_class"] for x in sites if x["stable_class"] in ("L","R")]
    allstable=sum(x["stable_class"] is not None for x in sites)
    mixed=len(leaning)>=4 and set(leaning)=={"L","R"} and allstable>=4
    decision=("CONTROL_FAILURE" if not calibration["passed"] else
              "MIXED_OUTLINE_OFFSETS_REQUIRING_REVIEW" if mixed else
              "NO_FIVE_SAIL_OUTLINE_OFFSET_CODE" if allstable>=4 else
              "INSUFFICIENT_REAL_OUTLINE_COVERAGE")
    result={
        "experiment_id":"A11-EXP-124",
        "hypothesis":"the five true triangular sails have robustly mixed outline base-center offsets relative to their apices, unlike simple perspective/shading",
        "evidence":"Visible five separate small triangle outlines; Stage 102 tracked a wrong fifth sail, a documented object-association defect.",
        "scope":"fixed five true sail sites, two simple outline-envelope detectors across 4 image variants; not hatch orientation, widths, internal stroke counts or secrets",
        "canonical_sha256":digest,
        "sites_predeclared":[list(x) for x in SITES],
        "thresholds":{"ink":THRESHOLD,"lead_fraction":LEAD_GATE,
                      "neutral_fraction":NEUTRAL_GATE,"min_row_support":MIN_ROW_SUPPORT,
                      "wedge_search_fraction":WEDGE_SEARCH_FRACTION},
        "controls":calibration,
        "real_sites":sites,
        "stable_site_count":allstable,
        "signed_leaning_site_count":len(leaning),
        "both_signs":set(leaning)=={"L","R"},
        "promoted":bool(calibration["passed"] and mixed),
        "decision":decision,
        "coverage_guard":"A synthetic control failure invalidates any real inference; insufficient real-site outline support remains INCONCLUSIVE. Only fixed apex-to-base offset, not the meaning of sails or other codes.",
        "security_guard":"Only public image features. No private key, mnemonic, candidate word, Ethereum address or wallet operations.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
        "# Stage 124 — true-five-sail outline base-offset audit","",
        "- Corrects documented object-association error of old Stage 102 without reusing its hatch-orientation metric.",
        f"- Canonical image verified: **{digest==SHA}**",
        f"- Synthetic controls: **{calibration['passes']}/{calibration['case_count']}**",
        f"- Stable real sites: **{allstable}/5**",
        f"- Strongly signed offsets: **{len(leaning)}/5**",
        f"- Decision: **{decision}**","",
        "| sail | geometric lean class | range over 2 methods × 4 variants |",
        "|:---|:---:|:---|",
    ]
    for x in sites:
        lines.append(f"| {x['sail']} | {x['stable_class'] or '?'} | {x['range']} |")
    lines+=["","## Interpretation",""]
    if not calibration["passed"]:
        lines.append("Synthetic controls failed. Do not interpret real findings; repair this same stage.")
    elif decision=="INSUFFICIENT_REAL_OUTLINE_COVERAGE":
        lines.append("Too few individually resolved triangle outlines for the preregistered two-method decision. Inconclusive, not a negative.")
    elif mixed:
        lines.append("Mixed left/right outline offsets are visually measurable on correct objects. Confirm source pixels independently before inferring intention or symbolism.")
    else:
        lines.append("No four-of-five consistent and mixed outline-base-offset pattern. Retire only this fixed apex-to-base geometry discriminator.")
    lines+=["","No secret, key, BIP39 or wallet activity.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"experiment_id":"A11-EXP-124",
                      "controls_pass":calibration["passed"],"stable_sites":allstable,
                      "decision":decision}))
if __name__=="__main__":
    main()
