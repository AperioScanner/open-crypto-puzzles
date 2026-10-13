#!/usr/bin/env python3
"""A11-EXP-130 — independently test left/right sail-panel hatch orientations.

Stage129 repaired a defective Hough detector (60/60 controls) but its full-sail
Sobel sign was near zero on each real sail, while signed raw-ink directional-lag
scores sometimes had high amplitude. One bounded follow-up asks whether opposite
hatch directions in the two panels cancel out when a whole sail is measured.

This experiment does not decode words, keys, addresses or wallet material.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from stage112_corrected_sail_width_progression import variants
from stage129_corrected_sail_hatch_direction import (
    SITES, MODES, CLASS_GATE, EXPECTED_SHA,
    get_patch, mask_for_shape, sobel_score, diagonal_lag_score, control_patch
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage130-two-panel-sail-hatching"
OUT.mkdir(parents=True,exist_ok=True)

# Fixed sign gate reused from Stage129 without post hoc relaxation.
SIGN_GATE=CLASS_GATE
PATTERNS=(
    ("L_POS_R_NEG","POS","NEG"),
    ("L_NEG_R_POS","NEG","POS"),
    ("BOTH_POS","POS","POS"),
    ("BOTH_NEG","NEG","NEG"),
    ("BOTH_HORIZONTAL","NEUTRAL","NEUTRAL"),
)
MAX_ACCEPTED_PANELS=10
REQUIRED_STABLE_SAILS=4

def panel_masks(shape,half):
    base=mask_for_shape(shape,half)
    x=np.arange(shape[1])[None,:]
    mid=(shape[1]-1)/2
    return ((base*(x<mid)).astype(np.uint8),
            (base*(x>mid)).astype(np.uint8))

def classify_panel(image,mask):
    # Sobel: local gradient tangents. Lag: grayscale paired-pixel dependence.
    s=sobel_score(image,mask)
    t=diagonal_lag_score(image,mask)
    sv=s["score"];tv=t["score"]
    cls=None
    if sv is not None and tv is not None:
        if sv>=SIGN_GATE and tv>=SIGN_GATE:cls="POS"
        elif sv<=-SIGN_GATE and tv<=-SIGN_GATE:cls="NEG"
    return {
        "classification":cls,
        "sobel_score":sv,
        "lag_score":tv,
        "sobel_energy":s["energy"],
        "lag_pair_min":t["pair_min"],
        "pixels":int(mask.sum()),
    }

def inspect(image,half):
    masks=panel_masks(image.shape,half)
    return {
        "left":classify_panel(image,masks[0]),
        "right":classify_panel(image,masks[1]),
    }

def synthetic_pair(site,left,right):
    la=control_patch(site,left)
    ra=control_patch(site,right)
    m_left,m_right=panel_masks(la.shape,site[4])
    img=np.full_like(la,255)
    img[m_left>0]=la[m_left>0]
    img[m_right>0]=ra[m_right>0]
    return img

def controls():
    cases=[]
    failures=[]
    for site in SITES:
        for name,left,right in PATTERNS:
            fake=synthetic_pair(site,left,right)
            altered=variants(fake)
            expected_left=None if left=="NEUTRAL" else left
            expected_right=None if right=="NEUTRAL" else right
            for v in MODES:
                a=inspect(altered[v],site[4])
                found=(a["left"]["classification"],a["right"]["classification"])
                target=(expected_left,expected_right)
                ok=(found==target)
                x={"site":site[0],"pattern":name,"format":v,
                   "found":list(found),"expected":list(target),"pass":ok}
                cases.append(x)
                if not ok:failures.append(x)
    return {
        "passed":not failures,
        "cases":len(cases),
        "passed_cases":len(cases)-len(failures),
        "failures":failures[:35],
        "patterns":{name:sum(x["pass"] for x in cases if x["pattern"]==name)
                    for name,_,_ in PATTERNS},
    }

def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=EXPECTED_SHA:
        raise SystemExit("canonical image SHA256 does not match")
    original=np.array(Image.open(SOURCE).convert("L"))
    if original.shape!=(1105,1600):
        raise SystemExit("canonical image dimensions do not match")

    ctl=controls()
    formats=variants(original)
    per_sail=[]
    classified=0
    opposite=[]
    for site in SITES:
        observations={}
        pairs=[]
        for v in MODES:
            patch=get_patch(formats[v],site)
            measured=inspect(patch,site[4])
            observations[v]=measured
            pairs.append((measured["left"]["classification"],
                          measured["right"]["classification"]))
        pair=pairs[0] if pairs[0][0] and pairs[0][1] and len(set(pairs))==1 else None
        if pair:
            classified+=1
            if pair in (("POS","NEG"),("NEG","POS")):
                opposite.append({"site":site[0],"pair":list(pair)})
        per_sail.append({
            "sail":site[0],
            "stable_pair":list(pair) if pair else None,
            "formats":observations,
        })

    # A mere consistent opposite left/right panel pattern can be natural
    # triangular hatching. Promotion as a *mixed across-object* visual lead
    # requires BOTH opposite sign-orders across >=4 fully classified sails.
    sufficient=classified>=REQUIRED_STABLE_SAILS
    both_orders=len({tuple(x["pair"]) for x in opposite})==2
    candidate=bool(sufficient and len(opposite)>=4 and both_orders)
    decision=(
        "CONTROL_FAILURE" if not ctl["passed"] else
        "INSUFFICIENT_PANEL_COVERAGE" if not sufficient else
        "MIXED_PANEL_HATCH_ORDERS_REQUIRING_REVIEW" if candidate else
        "NO_MIXED_SAIL_PANEL_HATCH_ORDER"
    )
    result={
        "experiment_id":"A11-EXP-130",
        "date":"2026-10-13",
        "hypothesis":"whole-sail orientation cancels because two internal sail panels carry opposed diagonal pencil hatching, potentially with distinct left/right sign-order across five sails",
        "evidence":"Stage129 real whole-sail Sobel scores cluster near zero while independent signed lag-scores differ; visible small sails have distinct half-panels separated by the mast",
        "scope":"same five corrected real sail interiors, split into fixed left/right panel masks; gradient and independent raw-ink lag; four image formats; image-only",
        "canonical_sha256":sha,
        "gates":{"sign_threshold":SIGN_GATE,"min_stable_sails":REQUIRED_STABLE_SAILS,
                 "opposite_order_sails_required":4,
                 "both_opposite_orders_required":True},
        "controls":ctl,
        "sails":per_sail,
        "stable_sail_pairs":classified,
        "opposite_pairs":opposite,
        "both_orders":both_orders,
        "promoted":bool(ctl["passed"] and candidate),
        "decision":decision,
        "coverage_limit":"Unclassified real panels remain inconclusive. A uniform V-shaped shading geometry is not a code. This measures only hatch angles, not density/widths/keys.",
        "safety":"Reads public canonical image only; no mnemonic words, private keys, address checks, wallet access or social research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    rows=[
        "# Stage 130 — two-panel diagonal hatch-direction test",
        "",
        f"- Canonical image SHA verified: **{sha==EXPECTED_SHA}**",
        f"- Synthetic mixed/identical/neutral control cases: **{ctl['passed_cases']}/{ctl['cases']}**",
        f"- Stable real sail pairs: **{classified}/5**",
        f"- Opposite-signed real panel pairs: **{len(opposite)}/5**",
        f"- Both left/right sign orders: **{both_orders}**",
        f"- Decision: **{decision}**",
        "",
        "| sail | stable left/right orientation |",
        "|:---|:---|"
    ]
    for p in per_sail:
        rows.append(f"| {p['sail']} | {p['stable_pair'] or '?'} |")
    rows+=["","## Interpretation",""]
    if not ctl["passed"]:
        rows.append("Controls failed. Do not classify real image; repair Stage130.")
    elif not sufficient:
        rows.append("Too few real pairs are stable across methods and re-encodings. Inconclusive, not a new coding negative.")
    elif candidate:
        rows.append("Opposite panel signs occur in both orders; requires independent manual source review, not a cipher or mnemonic interpretation.")
    else:
        rows.append("No stable mixed left/right sign-order signal. Uniform or natural triangular hatching is not a demonstrated encoding.")
    rows+=["","No secret material was derived, generated, or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(rows))
    print(json.dumps({"stage":130,"controls":ctl["passed"],
                      "control_cases":ctl["cases"],
                      "stable_sails":classified,"decision":decision}))

if __name__=="__main__":
    main()
