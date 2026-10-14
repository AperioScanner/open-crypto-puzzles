#!/usr/bin/env python3
"""A11-EXP-172: fixed synthetic outside-neighbor grayscale dose response.

Stage171 demonstrated that three strongly dark synthetic neighboring boats
could cause Stage169's otherwise 128/128-calibrated outer-edge detector to
abstain in every known-truth case. This isolates just the previously specified
4px outside-parallel boat line at x+11 of TRUE outer slope and varies its
FIXED grayscale intensity; no new target image pixels, codes or tuning.
All design parameters and outcome gates preregistered in STAGE_QUEUE.md.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES
from stage169_sail_outer_flank_contrast import (
    SOURCE_SITES,FORMATS,compare_two,artificial_scene
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE169=ROOT/"analysis"/"runs"/"stage169-sail-outer-flank-contrast"/"result.json"
STAGE171=ROOT/"analysis"/"runs"/"stage171-neighbor-boat-confounds"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage172-neighbor-grayscale-dose"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
LEVELS=(255,240,210,180,170,150,120,90,60,30,0)
P_TRUE=".60..1.00"
NUISANCE_OFFSET=11
NUISANCE_THICKNESS=4
FIXTURE="gray_fill_with_internal_decoy"

def label(site,index):return site+("_left" if index==1 else "_right")

def point(apex,foot,true_dx,t,sign,outward=11):
    ax,ay=apex;fx,fy=foot
    return (int(round(ax+t*(fx+true_dx-ax)+sign*outward)),
            int(round(ay+t*(fy-ay))))

def neighbor_scene(base,apex,foot,true_dx,sign,graylevel):
    z=base.copy()
    # Same precommitted 4px parallel shape as Stage171; 255 means absent.
    p=point(apex,foot,true_dx,.60,sign)
    q=point(apex,foot,true_dx,1.0,sign)
    cv2.line(z,p,q,int(graylevel),NUISANCE_THICKNESS,cv2.LINE_AA)
    return z

def main():
    checksum=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    prev169=json.loads(STAGE169.read_text())
    prev171=json.loads(STAGE171.read_text())
    checks={
      "canonical_sha_provenance_only":checksum==SHA,
      "Stage169_source_sha":prev169["canonical_source_sha256"]==SHA,
      "Stage169_128_synthetic_calibration":prev169["synthetic_source_independent_controls"]["pass"]
              and prev169["synthetic_source_independent_controls"]["passed"]==128,
      "Stage171_prior_full_controls":prev171["checks_passed"]==prev171["checks_total"]==12,
      "Stage171_known_neighbor_darkness_abstention":
          prev171["decision"]=="STAGE169_NEIGHBOR_NUISANCE_CAUSES_CLASSIFICATION_LOSS",
      "Stage171_clean_scenarios_32":
          prev171["summary"]["clean_known_edge_cases"]==32,
      "Stage171_black_parallel_unresolved_32":
          prev171["summary"]["per_nuisance"]["outside_parallel_11"]["unresolved"]==32,
      "unchanged_four_registered_sites":len(SOURCE_SITES)==4,
      "fixed_11_grayscale_intensities":len(LEVELS)==11,
    }
    rows=[];groups=[];sloped_scenes=0
    for site,index,inward in SOURCE_SITES:
        k=label(site,index)
        apex,foot=TRIANGLES[site][0],TRIANGLES[site][index]
        sign=1 if index==2 else -1
        for truth in (0,inward):
            base=artificial_scene(apex,foot,truth,sign,FIXTURE)
            data=[]
            for level in LEVELS:
                sloped_scenes+=1
                scene=neighbor_scene(base,apex,foot,truth,sign,level)
                frames=variants(scene)
                for fmt in FORMATS:
                    z=compare_two(frames[fmt],apex,foot,inward,sign)
                    correct=bool(z["confident"] and z["selected_dx"]==truth)
                    false=bool(z["confident"] and z["selected_dx"]!=truth)
                    uncertain=bool(not z["confident"])
                    truth_key=("original_dx0" if truth==0 else "inward_candidate_dx"+str(inward))
                    rows.append({
                       "site":k,"known_true_dx":truth,"line_graylevel":level,
                       "format":fmt,"correct":correct,
                       "wrong_accepted":false,"unresolved":uncertain,
                       "true_edge_outside_gray_darkness":z[truth_key]["outside"],
                       "true_edge_inside_gray_darkness":z[truth_key]["inside"],
                       "measurement":z,
                    })
                    data.append(rows[-1])
            g=[r for r in rows if r["site"]==k and r["known_true_dx"]==truth]
            group_by_level={int(level):[r for r in g if r["line_graylevel"]==level]
                            for level in LEVELS}
            first_loss=next((level for level in LEVELS[1:]
                if all(r["unresolved"] for r in group_by_level[level])),None)
            source_base=[r for r in group_by_level[255] if r["format"]=="original"][0]
            source_black=[r for r in group_by_level[0] if r["format"]=="original"][0]
            raw_black_increase=float(source_black["true_edge_outside_gray_darkness"]
                 - source_base["true_edge_outside_gray_darkness"])
            gray_trend=[all(r["correct"] for r in group_by_level[v]) for v in LEVELS]
            # monotone confidence: once classification lost, it should not recover
            had_loss=False
            violations=0
            for recovered in gray_trend:
                if had_loss and recovered: violations+=1
                if not recovered:had_loss=True
            groups.append({"site":k,"true_dx":truth,
                "first_all_four_formats_unresolved_graylevel":first_loss,
                "black_vs_white_outside_darkness_increase_original":round(raw_black_increase,6),
                "monotonicity_violations":violations,
                "correct_by_intensity_all_four_formats":dict(zip(map(str,LEVELS),gray_trend))})
    assert len(groups)==8
    checks["exact_352_cases"]=len(rows)==352 and sloped_scenes==88
    white=[r for r in rows if r["line_graylevel"]==255]
    black=[r for r in rows if r["line_graylevel"]==0]
    checks["32_white_no_stroke_true_edge_controls"]=len(white)==32 and all(r["correct"] for r in white)
    checks["32_black_stroke_abstention_replay"]=len(black)==32 and all(r["unresolved"] for r in black)
    checks["32_black_stroke_affects_outside_probe"]=all(
       (next(r["true_edge_outside_gray_darkness"] for r in black
             if r["site"]==v["site"] and r["known_true_dx"]==v["true_dx"] and r["format"]==fmt)
       -next(r["true_edge_outside_gray_darkness"] for r in white
             if r["site"]==v["site"] and r["known_true_dx"]==v["true_dx"] and r["format"]==fmt))>=.05
        for v in groups for fmt in FORMATS)
    checks_pass=all(checks.values())
    mild=[]
    strong=[]
    for g in groups:
        level=g["first_all_four_formats_unresolved_graylevel"]
        if level is not None:
            (mild if level>=170 else strong).append(g)
    if not checks_pass:
        decision="CONTROL_FAILURE"
    elif mild:
        decision="MILD_NEIGHBOR_GRAY_CAN_CAUSE_ABSTENTION"
    elif strong:
        decision="STRONGER_EXTERIOR_STROKE_REQUIRED_IN_FIXED_FIXTURES"
    else:
        decision="FIXED_PARALLEL_STROKE_DOSE_RESPONSE_INCONCLUSIVE"
    perlevel={}
    for level in LEVELS:
        subset=[r for r in rows if r["line_graylevel"]==level]
        perlevel[str(level)]={
            "cases":len(subset),"correct":sum(r["correct"] for r in subset),
            "unresolved":sum(r["unresolved"] for r in subset),
            "wrong_confidently_accepted":sum(r["wrong_accepted"] for r in subset),
        }
    false_all=[r for r in rows if r["wrong_accepted"]]
    result={
      "experiment_id":"A11-EXP-172",
      "canonical_sha_provenance_only":checksum,
      "canonical_artwork_pixels_analyzed":False,
      "source":"Unchanged Stage169 synthetic gray-filled outer-edge geometry + Stage171 precommitted 4px outside parallel black-stroke coordinates; only synthetic line intensity varies.",
      "fixed_levels":LEVELS,"fixed_stage171_parallel_stroke_px":NUISANCE_OFFSET,
      "fixed_stage171_parallel_stroke_thickness_px":NUISANCE_THICKNESS,
      "geometry_set":[(s,i,dx) for s,i,dx in SOURCE_SITES],
      "formats":FORMATS,
      "controls":checks,"controls_passed":sum(checks.values()),"controls_total":len(checks),
      "all_case_outcomes":rows,"per_grayscale_level":perlevel,
      "by_site_known_outer":groups,
      "n_groups_first_abstention_at_gray_ge_170":len(mild),
      "n_groups_first_abstention_at_gray_lt_170":len(strong),
      "n_wrong_confidently_accepted":len(false_all),
      "n_monotonicity_violations":sum(g["monotonicity_violations"] for g in groups),
      "decision":decision,
      "scope_limit":"Intensity ramp affects SINGLE synthetic outside-parallel black/gray stroke on gray-filled sail wedge; a given grayscale step is NOT calibrated to the complex full original drawing's measured background texture. No true real sail pixels or endpoints were reestimated. Four lossy renderings share one scene per group; not independent trials.",
      "safety":"No cryptographic key, BIP39, public address, wallet, off-image or social research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    report=["# Stage172 — source-blind gray-strength dose response for neighboring boat strokes","",
       f"- Canonical SHA provenance verified: **{checksum==SHA}**",
       f"- Structural/known-truth controls: **{sum(checks.values())}/{len(checks)}**",
       f"- Original known-outer synthetic scenes × gray-levels × formats: **{len(rows)}**",
       f"- Site/truth groups losing confidence at first gray >=170: **{len(mild)}/8**",
       f"- Site/truth groups requiring gray <170: **{len(strong)}/8**",
       f"- Wrong confidently accepted boundaries (all levels): **{len(false_all)}**",
       f"- Scientific decision: **{decision}**","",
       "| External line gray | Correct of 32 | Unresolved of 32 | False accepted |",
       "|---:|---:|---:|---:|"]
    for level in LEVELS:
        r=perlevel[str(level)]
        report.append(f"| {level} | {r['correct']} | {r['unresolved']} | {r['wrong_confidently_accepted']} |")
    report+=["","For transparency, 255 is an invisible line (clean reference) and 0 is black (Stage171 severe interference). Darker line intensity is synthetic, not a fitted estimate of neighboring boat/shade darkness in the real source. A failure only diagnoses the Stage169 CLASSIFIER confidence under this controlled nuisance; it does not choose exact outer sail feet or validate the puzzle code.","",
              "No private keys or wallets assessed.",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":172,
       "controls":f"{sum(checks.values())}/{len(checks)}",
       "mild":len(mild),"strong":len(strong),
       "wrong":len(false_all),"decision":decision}))
if __name__=="__main__":
    main()
