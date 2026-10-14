#!/usr/bin/env python3
"""Stage167: independent source-pixel support for pre-annotated sail footpoint x.

Stage166 quantified hypothetical +/-4px annotation ambiguity. This stage
does NOT optimize Stage165 p-values: it asks whether existing hand-placed
foot x coordinates coincide with a discriminable pencilled sloping outer edge
in the lower part of five known sail triangles. Controls precommitted.
Never derives or tests a key, phrase, wallet or code.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE152=ROOT/"analysis"/"runs"/"stage152-under-pier-closed-outline"/"result.json"
STAGE166=ROOT/"analysis"/"runs"/"stage166-sail-annotation-uncertainty"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage167-sail-footpoint-pixel-alignment"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
SITES={name:triangle for name,triangle in TRIANGLES.items() if name.startswith("sail")}
FOOT_INDEXES=(1,2)
CANDIDATE_OFFSETS=(-8,-4,0,4,8)
CONTROL_SHIFTS=(0,-8,8)
T_SAMPLES=np.linspace(.69,.96,20)
POINT_NORMALIZER=255.0
SCORE_MIN=.70
MARGIN_MIN=.15

def site_list():
    for site,triangle in SITES.items():
        for idx in FOOT_INDEXES:
            yield (site,idx,triangle[0],triangle[idx])

def scoring(frame,apex,foot,offset):
    """Source-blind repaired metric: single center pixel mean darkness.

    No hard grayscale cutoff and no dilated 3x3 any-dark corridor:
    that old corridor made all 120 known-positive synthetic source lines
    indistinguishable across adjacent 4px candidate x displacements.
    Keep the original 20 fixed ray samples, candidate offsets and gates.
    """
    x0,y0=apex
    x1,y1=foot
    x1+=offset
    darkness=[]
    for t in T_SAMPLES:
        x=int(round((1-t)*x0+t*x1))
        y=int(round((1-t)*y0+t*y1))
        darkness.append((POINT_NORMALIZER-float(frame[y,x]))/POINT_NORMALIZER)
    return float(np.mean(darkness))

def classify(frame,apex,foot):
    values=[scoring(frame,apex,foot,v) for v in CANDIDATE_OFFSETS]
    ranked=sorted(zip(values,CANDIDATE_OFFSETS),reverse=True)
    (best,shift),(second,_)=ranked[:2]
    margin=best-second
    confident=(best>=SCORE_MIN and margin>=MARGIN_MIN)
    return {"selected_offset_px":shift if confident else None,
            "confident":bool(confident),
            "top_support":round(best,6),"second_support":round(second,6),
            "support_margin":round(margin,6),
            "all_candidate_support":{str(v):round(s,6) for v,s in zip(CANDIDATE_OFFSETS,values)}}

def fake_edge(apex,foot,actual_shift):
    raw=np.full((1105,1600),255,np.uint8)
    fx,fy=foot
    cv2.line(raw,tuple(apex),(fx+actual_shift,fy),0,3,cv2.LINE_AA)
    return raw

def calibrate():
    observations=[]
    for site,idx,apex,foot in site_list():
        for true_shift in CONTROL_SHIFTS:
            encoded=variants(fake_edge(apex,foot,true_shift))
            for fmt in FORMATS:
                z=classify(encoded[fmt],apex,foot)
                passed=(z["confident"] and z["selected_offset_px"]==true_shift)
                observations.append({"site":site,"foot_index":idx,
                    "known_actual_shift":true_shift,"format":fmt,
                    "pass":bool(passed),"result":z})
    blank=np.full((1105,1600),255,np.uint8)
    neg=variants(blank)
    for site,idx,apex,foot in site_list():
        for fmt in FORMATS:
            z=classify(neg[fmt],apex,foot)
            passed=(not z["confident"])
            observations.append({"site":site,"foot_index":idx,
               "fixture":"blank","format":fmt,"pass":bool(passed),"result":z})
    return {"pass":len(observations)==160 and all(z["pass"] for z in observations),
            "cases":len(observations),
            "passed":sum(z["pass"] for z in observations),
            "failures":[z for z in observations if not z["pass"]]}

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    s152=json.loads(STAGE152.read_text())
    s166=json.loads(STAGE166.read_text())
    guards={
        "canonical_SHA":digest==SHA,
        "five_true_sail_outline_source_recovery":s152["real_sail_outlines_stable"]==5,
        "Stage152_controls_72":s152["control"]["pass"] and s152["control"]["passed_cases"]==72,
        "Stage166_16_controls":s166["controls_passed"]==s166["controls_total"]==16,
        "Stage166_hypothetical_annotation_sensitivity":s166["decision"]=="ANNOTATION_JITTER_CAN_FLIP_STAGE165_JOINT_GATE",
        "unchanged_sail_count":len(SITES)==5,
    }
    raw=np.asarray(Image.open(SOURCE).convert("L"))
    if raw.shape!=(1105,1600):raise RuntimeError("canonical geometry changed")
    ctl=calibrate()
    observations={}
    for fmt,frame in variants(raw).items():
        if fmt not in FORMATS:continue
        observations[fmt]={}
        for site,idx,apex,foot in site_list():
            key=f"{site}_{'left' if idx==1 else 'right'}"
            observations[fmt][key]=classify(frame,apex,foot)
    stable_zero=[];stable_nonzero=[];unresolved=[]
    for site,idx,apex,foot in site_list():
        key=f"{site}_{'left' if idx==1 else 'right'}"
        vals=[observations[fmt][key] for fmt in FORMATS]
        if all(v["confident"] and v["selected_offset_px"]==0 for v in vals):
            stable_zero.append(key)
        elif (all(v["confident"] for v in vals)
              and len(set(v["selected_offset_px"] for v in vals))==1):
            stable_nonzero.append({"site":key,"offset_px":vals[0]["selected_offset_px"]})
        else:
            unresolved.append(key)
    if not all(guards.values()) or not ctl["pass"]:
        verdict="CONTROL_FAILURE"
    elif len(stable_zero)>=8:
        verdict="ANNOTATED_SAIL_FEET_SLOPES_DISCRIMINABLY_ALIGNED"
    elif len(stable_nonzero)>=3:
        verdict="ANNOTATED_FOOT_SHIFT_REQUIRES_MANUAL_SOURCE_REVIEW"
    else:
        verdict="INSUFFICIENT_REAL_SOURCE_FOOTPOINT_PRECISION"
    result={
        "experiment_id":"A11-EXP-167","source_sha256":digest,
        "objective":"Independent fixed-shift lower-slope pencil edge support near previously hand-marked sail footpoint x coordinates, not vertex junction connectivity.",
        "original_immutable_sail_vertices":SITES,
        "fixed_parameters":{"offsets_px":CANDIDATE_OFFSETS,
            "fractional_distance_from_apex":T_SAMPLES.tolist(),
            "pixel_metric":"mean normalized center-pixel darkness, fixed t samples; synthetic-only repair; no hard ink cutoff",
            "min_top_score":SCORE_MIN,"min_best_second_margin":MARGIN_MIN,
            "source_formats":FORMATS},
        "prior_source_guards":guards,
        "synthetic_fixture_controls":ctl,
        "source_by_format_site":observations,
        "stable_original_offset_zero":stable_zero,
        "stable_same_nonzero_offsets":stable_nonzero,
        "source_unresolved_foot_sites":unresolved,
        "summary":{"known_foot_sites":len(list(site_list())),
            "stable_original_zero":len(stable_zero),
            "stable_same_nonzero":len(stable_nonzero),
            "unresolved":len(unresolved)},
        "decision":verdict,
        "interpretation_limit":"Edge support near an annotated diagonal does not prove pixel-precise base endpoints or any physical three-stroke junction. Heavy sail hatching, boat hull or pier rigging may confound matches. Predeclared score scanning is never used to choose widths for Stage165 p-value optimization.",
        "safety":"Only canonical original pencil pixels; no key, BIP39, wallet, address comparison or external/social search."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
       "# Stage167 — visible sail-foot diagonal alignment against 5 fixed x offsets","",
       f"- Canonical original SHA confirmed: **{digest==SHA}**",
       f"- Source and predecessor guards: **{sum(guards.values())}/{len(guards)}**",
       f"- Synthetic shifted/known and blank controls: **{ctl['passed']}/{ctl['cases']}**",
       f"- Sail footpoints with stable original 0px shift: **{len(stable_zero)}/10**",
       f"- Sail footpoints with stable alternate offset: **{len(stable_nonzero)}/10**",
       f"- Unresolved footpoints: **{len(unresolved)}/10**",
       f"- Decision: **{verdict}**","",
       "| Original sail foot | Original best offset | Top line-ink support | Margin | Four-format result |",
       "|---|---:|---:|---:|---|"]
    for site,idx,apex,foot in site_list():
        key=f"{site}_{'left' if idx==1 else 'right'}"
        s=observations["original"][key]
        label=("original0" if key in stable_zero else
               "alternate" if any(x["site"]==key for x in stable_nonzero) else
               "unresolved")
        lines.append(f"| {key} | {s['selected_offset_px']} | {s['top_support']:.2f} | {s['support_margin']:.2f} | {label} |")
    lines+=["","Source answer concerns sloping-ink alignment only; it does not locate physical footpoint junctions accurately nor derive any corrected base width. No annotated endpoints were modified to seek statistical significance.","",
            "No mnemonic, wallet, secret, off-source context or code reconstruction.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":167,"controls":f"{ctl['passed']}/{ctl['cases']}",
       "orig_aligned":len(stable_zero),"alternate":len(stable_nonzero),
       "unresolved":len(unresolved),"decision":verdict}))
if __name__=="__main__":main()
