#!/usr/bin/env python3
"""Stage171: synthetic-only adjacent-boat strokes threaten outer-edge detector.

The Stage169 classifier was validated on isolated clean sail wedges, but
the original ink contains neighboring boat hulls/rigging near the tested
sail boundaries. Add THREE predeclared distinct exterior nuisance shapes
to known-truth synthetic filled and hatched sail silhouettes and score using
UNMODIFIED Stage169 compare_two. No actual source drawing pixels evaluated.
No codes, key derivation, wallet, BIP39 or outside research.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path

import cv2
import numpy as np

from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES
from stage169_sail_outer_flank_contrast import (
    SOURCE_SITES, FORMATS, compare_two, artificial_scene, run_fixture_controls
)

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"clues"/"arweave-puzzle-11.png"
S169=ROOT/"analysis"/"runs"/"stage169-sail-outer-flank-contrast"/"result.json"
S170=ROOT/"analysis"/"runs"/"stage170-flank-pixel-provenance"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage171-neighbor-boat-confounds"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
NUISANCES=("outside_parallel_11","outside_cross_20_to_4","outside_gray_boat_wedge")
TEST_KIND="gray_fill_with_internal_decoy"

def site_key(name,index):
    return name+("_left" if index==1 else "_right")

def truepoint(apex,foot,truth,t,outward,sign):
    """Continuous source-free synthetic ink landmark on true sloping guide."""
    x0,y0=apex
    x1,y1=foot
    return (float(x0+t*(x1+truth-x0)+sign*outward),
            float(y0+t*(y1-y0)))

def pt(v):
    return tuple(int(round(x)) for x in v)

def add_neighbor_strokes(blank_filled,apex,foot,truth,sign,kind):
    out=blank_filled.copy()
    if kind=="outside_parallel_11":
        p=truepoint(apex,foot,truth,.60,11,sign)
        q=truepoint(apex,foot,truth,1.0,11,sign)
        cv2.line(out,pt(p),pt(q),0,4,cv2.LINE_AA)
    elif kind=="outside_cross_20_to_4":
        p=truepoint(apex,foot,truth,.60,20,sign)
        q=truepoint(apex,foot,truth,1.0,4,sign)
        cv2.line(out,pt(p),pt(q),0,5,cv2.LINE_AA)
    elif kind=="outside_gray_boat_wedge":
        verts=[
            truepoint(apex,foot,truth,.67,6,sign),
            truepoint(apex,foot,truth,.67,24,sign),
            truepoint(apex,foot,truth,1.0,25,sign),
            truepoint(apex,foot,truth,1.0,6,sign)
        ]
        cv2.fillPoly(out,[np.array([pt(v) for v in verts],np.int32)],70,
                    lineType=cv2.LINE_8)
    else:
        raise ValueError("Predeclared nuisance unknown: "+kind)
    return out

def compare_specific(frame,apex,foot,inward,sign):
    result=compare_two(frame,apex,foot,inward,sign)
    return result

def main():
    canonical=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
    older=json.loads(S169.read_text())
    reviewed=json.loads(S170.read_text())
    expected_sites=(("sail2",2,-8),("sail3",1,8),
                    ("sail4",2,-8),("sail5",2,-8))
    controls_prior=run_fixture_controls()
    guards={
      "original_SHA_provenance_only":canonical==SHA,
      "Stage169_SHA":older["canonical_source_sha256"]==SHA,
      "Stage169_prior_synthetic_128":older["synthetic_source_independent_controls"]["pass"]
             and older["synthetic_source_independent_controls"]["passed"]==128,
      "independently_replayed_original_synthetics_128":controls_prior["pass"]
             and controls_prior["passed"]==128,
      "Stage169_source_registry_6":all(older["predecessor_and_fixed_site_guards"].values()),
      "Stage170_original_pixel_15":reviewed["checks_passed"]==reviewed["checks_total"]==15,
      "four_immutable_source_sites":tuple(SOURCE_SITES)==expected_sites,
      "two_alternatives_per_site":all(dx!=0 for _,_,dx in SOURCE_SITES),
      "only_3_fixed_nuisances":len(NUISANCES)==3,
    }
    baseline=[]
    adversarial=[]
    changes={}
    integrity={"clean_base_truth":True,"added_nonwhite_exterior":True}
    for site,index,inward in SOURCE_SITES:
        key=site_key(site,index)
        apex,foot=TRIANGLES[site][0],TRIANGLES[site][index]
        sign=1 if index==2 else -1
        for true_dx in (0,inward):
            raw_clean=artificial_scene(apex,foot,true_dx,sign,TEST_KIND)
            frames_clean=variants(raw_clean)
            measures_clean={}
            for fmt in FORMATS:
                reading=compare_specific(frames_clean[fmt],apex,foot,inward,sign)
                ok=reading["confident"] and reading["selected_dx"]==true_dx
                baseline.append({"site":key,"known_true_dx":true_dx,"format":fmt,
                                 "correct":bool(ok),"measured":reading})
                measures_clean[fmt]=reading
            for kind in NUISANCES:
                altered=add_neighbor_strokes(raw_clean,apex,foot,true_dx,sign,kind)
                changed=int(np.count_nonzero(raw_clean!=altered))
                integrity["added_nonwhite_exterior"] &= changed>0
                perturb=variants(altered)
                changes_key=kind
                if changes_key not in changes:changes[changes_key]=[]
                for fmt in FORMATS:
                    observed=compare_specific(perturb[fmt],apex,foot,inward,sign)
                    chosen=observed["selected_dx"]
                    correct=bool(observed["confident"] and chosen==true_dx)
                    wrong=bool(observed["confident"] and chosen!=true_dx)
                    unresolved=not observed["confident"]
                    actual_true_key=("original_dx0" if true_dx==0
                          else "inward_candidate_dx"+str(inward))
                    clean_out=measures_clean[fmt][actual_true_key]["outside"]
                    modified_out=observed[actual_true_key]["outside"]
                    outside_increase=float(modified_out-clean_out)
                    changes[changes_key].append(outside_increase)
                    adversarial.append({
                        "site":key,"true_dx":true_dx,"nuisance":kind,
                        "format":fmt,"changed_original_synthetic_ink_pixels":changed,
                        "outside_darkness_added_at_true_edge":round(outside_increase,7),
                        "correct":correct,"wrong_accepted":wrong,"unresolved":unresolved,
                        "measurement":observed})
    assert len(baseline)==32 and len(adversarial)==96
    # Four "synthetic source variants" are derived from ONE controlled scene each.
    # These are stability checks, not independent probabilities.
    integrity["clean_base_truth"]=all(r["correct"] for r in baseline)
    per_type={}
    for kind in NUISANCES:
        rr=[r for r in adversarial if r["nuisance"]==kind]
        impact=[v for v in changes[kind] if v>=.05]
        per_type[kind]={
          "known_outer_scenes":len(rr),
          "correct":sum(r["correct"] for r in rr),
          "wrong_accepted":sum(r["wrong_accepted"] for r in rr),
          "unresolved":sum(r["unresolved"] for r in rr),
          "outside_dark_increase_at_true_edge_at_least_005":len(impact),
          "largest_outside_dark_increase":round(max(changes[kind]),6),
        }
    # Preregistered: at least one scene in ORIGINAL variant must have meaningful
    # exterior-flank contamination for every family; mere drawn ink is not enough.
    integrity["all_3_nuisances_reach_fixed_outside_probe"]=all(
        any(r["format"]=="original"
            and r["outside_darkness_added_at_true_edge"]>=.05
            for r in adversarial if r["nuisance"]==kind)
        for kind in NUISANCES)
    checks={**guards,
      "32_clean_known_edge_fixture_replay":integrity["clean_base_truth"],
      "96_synthetic_adversarial_scene_integrity":integrity["added_nonwhite_exterior"]
          and len(adversarial)==96,
      "all_3_nuisance_classes_hit_true_edge_flank":integrity[
           "all_3_nuisances_reach_fixed_outside_probe"]}
    stable_wrong=[]
    stable_unresolved=[]
    for site,index,inward in SOURCE_SITES:
        key=site_key(site,index)
        for true_dx in (0,inward):
            for kind in NUISANCES:
                group=[r for r in adversarial if r["site"]==key
                       and r["true_dx"]==true_dx and r["nuisance"]==kind]
                if len(group)!=4:
                    raise RuntimeError("adversarial group incomplete")
                if all(r["wrong_accepted"] for r in group):
                    stable_wrong.append({"site":key,"known_true_dx":true_dx,"nuisance":kind,
                                         "false_selected_dx":group[0]["measurement"]["selected_dx"]})
                if all(r["unresolved"] for r in group):
                    stable_unresolved.append({"site":key,"known_true_dx":true_dx,"nuisance":kind})
    if not all(checks.values()):
        decision="CONTROL_FAILURE"
    elif stable_wrong:
        decision="STAGE169_NEIGHBOR_NUISANCE_CAN_MISLOCATE_KNOWN_OUTER_EDGE"
    elif stable_unresolved or any(r["unresolved"] for r in adversarial):
        decision="STAGE169_NEIGHBOR_NUISANCE_CAUSES_CLASSIFICATION_LOSS"
    else:
        decision="STAGE169_ROBUST_ONLY_FOR_FIXED_SYNTHETIC_NEIGHBOR_SCENES"
    summary={
      "clean_known_edge_cases":len(baseline),
      "adversarial_cases":len(adversarial),
      "correct_adversarial":sum(r["correct"] for r in adversarial),
      "wrong_accepted_adversarial":sum(r["wrong_accepted"] for r in adversarial),
      "unresolved_adversarial":sum(r["unresolved"] for r in adversarial),
      "stable_wrong_across_all_four_formats":stable_wrong,
      "stable_unresolved_across_all_four_formats":stable_unresolved,
      "per_nuisance":per_type
    }
    result={
      "experiment_id":"A11-EXP-171",
      "canonical_SHA256_provenance_only":canonical,
      "source_image_pixels_reanalyzed":False,
      "test":"Unchanged Stage169 contrast scorer with fixed known-outer synthetic sailing wedge + exterior boat/hull stroke nuisances, no source data.",
      "fixed_synthetic_sites":SOURCE_SITES,
      "fixed_true_offsets":[0,"previous_registered_inward"],
      "nuisance_types":NUISANCES,
      "renderer_formats":FORMATS,
      "original_stage169_calibration":controls_prior["passed"],
      "checks":checks,"checks_passed":sum(checks.values()),
      "checks_total":len(checks),
      "clean_known_edge_tests":baseline,
      "nuisance_tests":adversarial,
      "summary":summary,
      "decision":decision,
      "interpretation_limit":"Only controlled synthetic strokes were used. False identification would demonstrate a nuisance confound in the Stage169 detector, not the actual original artist's intended edge. A no-false result cannot validate real-source positions because more complex hatching and overlapping boat artwork were not tested. No statistical p-values, author code, or wallet claims.",
      "safety":"No key, mnemonic, BIP39, address, wallet, OCR or off-image research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    rows=["# Stage171 — synthetic adjacent boat/hull dark stroke confound audit","",
       f"- Canonical PNG SHA provenance only: **{canonical==SHA}**",
       f"- Original Stage169 clean synthetic replay: **{controls_prior['passed']}/{controls_prior['cases']}**",
       f"- Structural/adversarial integrity controls: **{sum(checks.values())}/{len(checks)}**",
       f"- Clean two-true-edge controls: **{sum(r['correct'] for r in baseline)}/{len(baseline)}**",
       f"- Adversarial synthetic cases: **{len(adversarial)}**",
       f"- False source-EDGE accepted under known-wrong candidate: **{summary['wrong_accepted_adversarial']}/{len(adversarial)}**",
       f"- Correct: **{summary['correct_adversarial']}**, unresolved: **{summary['unresolved_adversarial']}**",
       f"- False edge accepted in all four formats for a precommitted scene: **{len(stable_wrong)}**",
       f"- Scientific decision: **{decision}**","",
       "| Exterior nuisance | Known cases | Correct | False edge confidently accepted | Unresolved |",
       "|---|---:|---:|---:|---:|"]
    for name,z in per_type.items():
        rows.append(f"| {name} | {z['known_outer_scenes']} | {z['correct']} | {z['wrong_accepted']} | {z['unresolved']} |")
    rows+=["","Known truth is defined by SYNTHETIC geometry; this test does not measure or reclassify any actual photo/sail pixels. The four JPEG/PNG formats are repeated transformations of the same fixture, not independent artwork. Do not feed any Stage169 inwards into Stage165 or claim a secret.",""]
    (OUT/"REPORT.md").write_text("\n".join(rows))
    print(json.dumps({"stage":171,"checks":f"{sum(checks.values())}/{len(checks)}",
      "clean":sum(r["correct"] for r in baseline),
      "adversarial":len(adversarial),
      "wrong_accepted":summary["wrong_accepted_adversarial"],
      "unresolved":summary["unresolved_adversarial"],
      "stable_wrong":len(stable_wrong),"decision":decision}))
if __name__=="__main__":main()
