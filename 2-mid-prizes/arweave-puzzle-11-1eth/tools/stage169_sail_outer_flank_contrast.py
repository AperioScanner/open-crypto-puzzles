#!/usr/bin/env python3
"""A11-EXP-169: real sail outer silhouette vs inside diagonal hatch.

A Stage168 independently visible ambiguity: Stage167 picked three INWARD
darkest-ink diagonals which could be interior hatching. This test does NOT
reuse Stage167's dark-line objective: it compares dark pencil support INSIDE
the putative edge to light SOURCE background OUTSIDE the edge.
Exact four original source sites, two candidate rays each, synthetic 128-case
positive/negative controls, and thresholds preregistered in STAGE_QUEUE.md.
No key, wallet, BIP39, address, OCR, external or social research.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR167=ROOT/"analysis"/"runs"/"stage167-sail-footpoint-pixel-alignment"/"result.json"
PRIOR168=ROOT/"analysis"/"runs"/"stage168-sail-foot-review"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage169-sail-outer-flank-contrast"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
# Index1 is LEFT exterior x-negative, index2 is RIGHT exterior x-positive.
SOURCE_SITES=(("sail2",2,-8),("sail3",1,+8),("sail4",2,-8),("sail5",2,-8))
T_SAMPLES=np.linspace(.73,.93,22)
FLANK_OFFSETS=(5,8,11,14)
MIN_DIFFERENCE=.30
MIN_INNER=.50
MAX_OUTER=.30
MIN_MARGIN=.15
FULL_SHAPE=(1105,1600)

def site_key(site,foot_index):
    return f"{site}_{'left' if foot_index==1 else 'right'}"

def evaluate_edge(frame,apex,foot,delta,interior_sign):
    ax,ay=apex;fx,fy=foot
    inside=[];outside=[]
    for t in T_SAMPLES:
        x=int(round(ax+t*(fx+delta-ax)))
        y=int(round(ay+t*(fy-ay)))
        inside.extend((255-int(frame[y,x-interior_sign*k]))/255.
                      for k in FLANK_OFFSETS)
        outside.extend((255-int(frame[y,x+interior_sign*k]))/255.
                       for k in FLANK_OFFSETS)
    i=float(np.mean(inside));o=float(np.mean(outside))
    return {"inside":round(i,8),"outside":round(o,8),
            "contrast":round(i-o,8)}

def compare_two(frame,apex,foot,inward,sign):
    a=evaluate_edge(frame,apex,foot,0,sign)
    b=evaluate_edge(frame,apex,foot,inward,sign)
    winner=0 if a["contrast"]>=b["contrast"] else inward
    best=a if winner==0 else b
    other=b if winner==0 else a
    margin=float(best["contrast"]-other["contrast"])
    confident=(best["contrast"]>=MIN_DIFFERENCE
         and best["inside"]>=MIN_INNER
         and best["outside"]<=MAX_OUTER
         and margin>=MIN_MARGIN)
    return {"selected_dx":winner if confident else None,
        "confident":bool(confident),"best_margin":round(margin,8),
        "original_dx0":a,"inward_candidate_dx"+str(inward):b}

def artificial_scene(apex,foot,true_shift,sign,kind):
    result=np.full(FULL_SHAPE,255,np.uint8)
    fx,fy=foot
    pos=(fx+true_shift,fy)
    if kind in ("solid_fill","solid_with_internal_decoy","gray_fill_with_internal_decoy"):
        # Fixed geometric wedge, real exterior slope at true_shift:
        # fill toward the INTERIOR half-plane, away from outside-white.
        inner=(pos[0]-70*sign,fy)
        intensity=70 if kind=="gray_fill_with_internal_decoy" else 0
        cv2.fillPoly(result,[np.asarray([apex,pos,inner],np.int32)],
                    int(intensity),lineType=cv2.LINE_8)
        if "internal_decoy" in kind:
            decoy=(fx+true_shift-8*sign,fy)
            cv2.line(result,tuple(apex),decoy,0,3,cv2.LINE_AA)
    elif kind=="isolated_dark_line":
        cv2.line(result,tuple(apex),pos,0,3,cv2.LINE_AA)
    else:
        raise ValueError(kind)
    return result

def run_fixture_controls():
    cases=[]
    for site,index,inward in SOURCE_SITES:
        apex,foot=TRIANGLES[site][0],TRIANGLES[site][index]
        sign=1 if index==2 else -1
        # 4 sites x2 known true boundary x3 filled/shaded variants x4 formats =96.
        for true_dx in (0,inward):
            for kind in ("solid_fill","solid_with_internal_decoy",
                         "gray_fill_with_internal_decoy"):
                for fmt,frame in variants(
                        artificial_scene(apex,foot,true_dx,sign,kind)).items():
                    if fmt not in FORMATS:continue
                    measure=compare_two(frame,apex,foot,inward,sign)
                    passed=(measure["confident"] and measure["selected_dx"]==true_dx)
                    cases.append({"site":site_key(site,index),"kind":kind,
                        "known_true_dx":true_dx,"format":fmt,
                        "pass":bool(passed),"measurement":measure})
        # Isolated dark internal stripe is NOT a legitimate filled-sail exterior.
        for fmt,frame in variants(
            artificial_scene(apex,foot,inward,sign,"isolated_dark_line")).items():
            if fmt not in FORMATS:continue
            measure=compare_two(frame,apex,foot,inward,sign)
            cases.append({"site":site_key(site,index),"kind":"isolated_dark_line",
                "known_true_dx":None,"format":fmt,
                "pass":bool(not measure["confident"]),"measurement":measure})
    blank=np.full(FULL_SHAPE,255,np.uint8)
    rendered_blank=variants(blank)
    for site,index,inward in SOURCE_SITES:
        apex,foot=TRIANGLES[site][0],TRIANGLES[site][index]
        sign=1 if index==2 else -1
        for fmt in FORMATS:
            measure=compare_two(rendered_blank[fmt],apex,foot,inward,sign)
            cases.append({"site":site_key(site,index),"kind":"blank",
                "known_true_dx":None,"format":fmt,
                "pass":bool(not measure["confident"]),"measurement":measure})
    count=sum(1 for r in cases if r["pass"])
    return {"pass":len(cases)==128 and count==128,"passed":count,
        "cases":len(cases),
        "failures":[r for r in cases if not r["pass"]],
        "families":{kind:sum(1 for r in cases if r["kind"]==kind and r["pass"])
            for kind in ("solid_fill","solid_with_internal_decoy",
                         "gray_fill_with_internal_decoy",
                         "isolated_dark_line","blank")}}

def provenance():
    src_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    s167=json.loads(PRIOR167.read_text())
    s168=json.loads(PRIOR168.read_text())
    observed={(x["site"],x["offset_px"]) for x in
              s167["stable_same_nonzero_offsets"]}
    expected={(site_key(s,i),v) for s,i,v in SOURCE_SITES if s!="sail2"}
    controls={
        "canonical_sha":src_sha==SHA,
        "Stage167_repaired_clean_positive_controls":
           s167["synthetic_fixture_controls"]["pass"]
           and s167["synthetic_fixture_controls"]["passed"]==160,
        "Stage167_3_fixed_nonzero_sites":observed==expected,
        "Stage167_reference_original_zero":
            set(s167["stable_original_offset_zero"])=={"sail2_right"},
        "Stage168_original_crop_provenance":
            s168["decision"]=="CONTACT_SHEET_READY_FOR_MANUAL_SOURCE_REVIEW"
            and s168["controls_passed"]==s168["controls_total"]==12,
        "sites_are_original_registered_sails":
            all(s in TRIANGLES and 1<=i<=2 for s,i,_ in SOURCE_SITES)
    }
    return controls,src_sha

def main():
    guards,src_sha=provenance()
    fixtures=run_fixture_controls()
    # Interpret NO natural drawing pixels before independent fixed fixtures pass.
    if not all(guards.values()) or not fixtures["pass"]:
        decision="CONTROL_FAILURE"
        real={}
        summary={}
    else:
        source=np.asarray(Image.open(SOURCE).convert("L"))
        if source.shape!=FULL_SHAPE:
            raise RuntimeError("original-source size changed")
        real={}
        for fmt,frame in variants(source).items():
            if fmt not in FORMATS:continue
            real[fmt]={}
            for site,index,inward in SOURCE_SITES:
                k=site_key(site,index)
                apex,foot=TRIANGLES[site][0],TRIANGLES[site][index]
                sign=1 if index==2 else -1
                real[fmt][k]=compare_two(frame,apex,foot,inward,sign)
        stable_zero=[];stable_inward=[];ambiguous=[]
        for site,index,inward in SOURCE_SITES:
            k=site_key(site,index)
            samples=[real[fmt][k] for fmt in FORMATS]
            if all(r["confident"] and r["selected_dx"]==0 for r in samples):
                stable_zero.append(k)
            elif all(r["confident"] and r["selected_dx"]==inward for r in samples):
                stable_inward.append(k)
            else:
                ambiguous.append(k)
        summary={"stable_original":stable_zero,"stable_inward":stable_inward,
                 "ambiguous":ambiguous,
                 "original_count":len(stable_zero),
                 "inward_count":len(stable_inward),
                 "ambiguous_count":len(ambiguous)}
        if len(stable_zero)==4:
            decision="SOURCE_OUTER_FLANK_CONTRAST_FAVORS_ANNOTATED_ORIGINAL"
        elif len([x for x in stable_inward if x!="sail2_right"])>=2:
            decision="SOURCE_OUTER_FLANK_CONTRAST_SUPPORTS_INWARD_SHIFTS_NEEDS_HUMAN_REVIEW"
        else:
            decision="INSUFFICIENT_SOURCE_FLANK_CONTRAST"
    result={
      "experiment_id":"A11-EXP-169",
      "hypothesis":"External white-vs-internal dark pencil flank asymmetry can distinguish an outer sail edge from a dark inner hatch in four predefined source foot guides.",
      "canonical_source_sha256":src_sha,
      "predecessor_and_fixed_site_guards":guards,
      "synthetic_source_independent_controls":fixtures,
      "fixed_sites":[{"site":site_key(site,index),"apex":TRIANGLES[site][0],
             "original_foot":TRIANGLES[site][index],"inward_alternative_dx":dx}
             for site,index,dx in SOURCE_SITES],
      "fixed_parameters":{"t_start":.73,"t_end":.93,"n_t":len(T_SAMPLES),
             "inside_outside_dx_px":FLANK_OFFSETS,
             "min_score":MIN_DIFFERENCE,"min_inside_dark":MIN_INNER,
             "max_outside_dark":MAX_OUTER,"min_best_second":MIN_MARGIN,
             "format":FORMATS},
      "real_by_source_variant":real,"summary":summary,"decision":decision,
      "scope_limit":"Comparing 2 fixed slope-guide pixels flanks is not an independent real contour trace or exact source footpoint. Uncertainty near ink hatches, hull and pier remains. Do not feed source-selected offsets into Stage165 p-values or infer intentional numerals.",
      "safety":"Image only; no private key, mnemonic, wallet, address/ETH comparison, OCR or external social investigation."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage169 — source outer-edge white flank versus dark sail interior","",
       f"- Canonical SHA: **{src_sha==SHA}**",
       f"- Stage167/168 original-site and archive controls: **{sum(guards.values())}/{len(guards)}**",
       f"- Distinct clean/decoy/shaded/blank synthetic controls: **{fixtures['passed']}/{fixtures['cases']}**",
       f"- Scientific decision: **{decision}**",""]
    if real:
        lines+=["| Original site | Edge from original x0 | Edge from fixed inward alternative | Winning 4-format result |",
          "|---|---:|---:|---|"]
        for site,index,inward in SOURCE_SITES:
            k=site_key(site,index)
            p=real["original"][k]
            chosen=("original0" if k in summary["stable_original"] else
                 "inward" if k in summary["stable_inward"] else "unresolved")
            k_alt="inward_candidate_dx"+str(inward)
            lines.append(f"| {k} | {p['original_dx0']['contrast']:.3f} | {p[k_alt]['contrast']:.3f} | {chosen} |")
        lines +=["",f"- Stable original: **{summary['original_count']}/4**",
          f"- Stable inward: **{summary['inward_count']}/4**",
          f"- Unresolved: **{summary['ambiguous_count']}/4**"]
    lines+=["","A contrast preference is SOURCE evidence for a fixed geometric flank test, not proof of the exact intended sail footpoint or an authored code. No modifications to Stage165/166 width/p results.","",
            "No keys, BIP39, Ethereum addresses or wallets tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":169,"controls":f"{fixtures['passed']}/{fixtures['cases']}",
        "guard_count":f"{sum(guards.values())}/{len(guards)}",
        "summary":summary,"decision":decision}))
if __name__=="__main__":main()
