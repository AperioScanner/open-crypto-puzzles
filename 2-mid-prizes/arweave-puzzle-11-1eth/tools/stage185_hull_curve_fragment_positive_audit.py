#!/usr/bin/env python3
"""A11-EXP-185 — source-blind positive recovery for curved and fragmented hull pencil lines.

Independent source observation: actual five small-boat hulls have bowed and short,
broken strokes. Historical Stage127 positive controls were only four long,
straight lines per hull. This tests the unchanged detector on stylized nonstraight
known-positive controls. Do not read original image pixels or infer any puzzle code.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from stage127_hull_waterline_slope import (
    SITES, FORMATS, METHODS, synthetic, classify_scene
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"analysis/runs/stage185-hull-curvature-calibration"
OUT.mkdir(parents=True,exist_ok=True)
PNG = ROOT/"clues/arweave-puzzle-11.png"
OLD127 = ROOT/"analysis/runs/stage127-hull-waterline-slope/result.json"
SHA = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
CLASSES = ("UP_RIGHT","LEVEL","DOWN_RIGHT")
NUISANCES = ("curved","broken","curved_broken")
SLOPES = {"UP_RIGHT":-0.26,"LEVEL":0.0,"DOWN_RIGHT":0.26}
OFFSETS = (6,10,15,20)
BOW_AMPLITUDE = 6.0
INK_SPAN = 20
GAP_SPAN = 8
STRIPE_THICKNESS = 2

def a_stroke_points(left,right,mid,by,off,slope,nu):
    points=[]
    for x in range(left,right+1):
        normalized=2*(x-mid)/(right-left)
        bow=BOW_AMPLITUDE*normalized**2 if nu in ("curved","curved_broken") else 0
        y=int(round(by+off+slope*(x-mid)+bow))
        points.append((x,y))
    return points

def draw_one_stroke(image,points,nu):
    if nu=="curved":
        pieces=[points]
    else:
        pieces=[]
        for k in range(0,len(points),INK_SPAN+GAP_SPAN):
            part=points[k:k+INK_SPAN]
            if len(part)>=2:
                pieces.append(part)
    made=0
    all_in=True
    for part in pieces:
        all_in=all_in and all(0<=x<1600 and 0<=y<1105 for x,y in part)
        if not all_in:continue
        cv2.polylines(image,[np.asarray(part,np.int32)],False,0,STRIPE_THICKNESS,cv2.LINE_AA)
        made+=1
    return made,all_in

def source_blind_scene(class_label,nu):
    img=np.full((1105,1600),255,np.uint8)
    checks=[]
    for name,cx,top,h,half in SITES:
        by=top+h
        sail=[(cx,top+8),(cx-half,by-9),(cx+half,by-9)]
        # Exact old Stage127 sail outline, unchanged.
        cv2.line(img,sail[0],sail[1],0,2,cv2.LINE_AA)
        cv2.line(img,sail[0],sail[2],0,2,cv2.LINE_AA)
        cv2.line(img,sail[1],sail[2],0,1,cv2.LINE_AA)
        left=cx-half-11
        right=cx+half+11
        mid=(left+right)/2
        true_slope=SLOPES[class_label]
        individually_detectable=[]
        endpoint_in_frame=True
        for off in OFFSETS:
            pts=a_stroke_points(left,right,mid,by,off,true_slope,nu)
            separate=np.full((1105,1600),255,np.uint8)
            made,inside=draw_one_stroke(separate,pts,nu)
            _,inside_actual=draw_one_stroke(img,pts,nu)
            endpoint_in_frame=endpoint_in_frame and inside and inside_actual
            # Independently verify raster support for each drawn line;
            # adjacent strokes may merge into a single connected component.
            component_num,_=cv2.connectedComponents((separate<245).astype(np.uint8),8)
            individually_detectable.append(made>=1 and component_num>=2
                                           and np.count_nonzero(separate<245)>=10)
        checks.append({"site":name,
                       "four_individually_rendered_hull_strokes":sum(individually_detectable),
                       ">=two_nonempty_stroke_components_or_contours":
                           sum(individually_detectable)>=2,
                       "all_endpoints_in_frame":endpoint_in_frame})
    return img,checks

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    old=json.loads(OLD127.read_text())
    checks={
        "canonical_sha_provenance_only":digest==SHA,
        "stage127_archived_source_abstention":old["decision"]=="INSUFFICIENT_HULL_ISOLATION" and old["stable_sites"]==0,
        "stage127_archived_calibration":old["controls"]["pass"] and old["controls"]["positive_mixed_pass"] and old["controls"]["negative_level_with_decoy_pass"],
        "frozen_original_stage127_geometry":old["hull_sites"]==[list(x) for x in SITES],
        "four_formats_and_two_methods_unchanged":len(FORMATS)==4 and set(FORMATS)=={"original","jpeg85","jpeg70","down75_up"} and len(METHODS)==2,
    }
    clsmap={s[0]:c for s,c in zip(SITES,("DOWN_RIGHT","UP_RIGHT","DOWN_RIGHT","UP_RIGHT","LEVEL"))}
    neutral={s[0]:"LEVEL" for s in SITES}
    clean=classify_scene(synthetic(clsmap))
    level=classify_scene(synthetic(neutral,decoy=True))
    blank=classify_scene(np.full((1105,1600),255,np.uint8))
    checks["clean_known_mixed_5_of_5"]=all(x["stable_class"]==clsmap[x["site"]] for x in clean)
    checks["clean_known_level_decoy_5_of_5"]=all(x["stable_class"]=="LEVEL" for x in level)
    checks["source_blind_blank_0_of_5"]=all(x["stable_class"] is None for x in blank)
    rows=[]
    for nuisance in NUISANCES:
        for cls in CLASSES:
            art,drawchecks=source_blind_scene(cls,nuisance)
            checks[f"{nuisance}_{cls}_5_sail_hull_sites_drawn"]=len(drawchecks)==5
            checks[f"{nuisance}_{cls}_real_strokes_present"] = all(x["four_individually_rendered_hull_strokes"]>=2 for x in drawchecks)
            checks[f"{nuisance}_{cls}_contours_present"] = all(x[">=two_nonempty_stroke_components_or_contours"] for x in drawchecks)
            checks[f"{nuisance}_{cls}_in_image"]=all(x["all_endpoints_in_frame"] for x in drawchecks)
            cases=classify_scene(art)
            correct=sum(x["stable_class"]==cls for x in cases)
            wrong=sum(x["stable_class"] is not None and x["stable_class"]!=cls for x in cases)
            rows.append({"nuisance":nuisance,"known_true_class":cls,"correct_stable":correct,
                 "wrong_stable":wrong,"abstained":5-correct-wrong,
                 "known_5_site_results":[{"site":x["site"],"stable":x["stable_class"]} for x in cases]})
    checks={k:bool(v) for k,v in checks.items()}
    qa=all(checks.values())
    full_recovery=all(row["correct_stable"]>=4 for row in rows)
    decision = ("CONTROL_FAILURE" if not qa else
        "STAGE127_SOURCE_LIKE_POSITIVE_RECOVERY_ADEQUATE" if full_recovery else
        "STAGE127_SOURCE_LIKE_POSITIVE_RECOVERY_INADEQUATE")
    result={
        "experiment_id":"A11-EXP-185","canonical_sha256_provenance_only":digest,
        "original_artwork_pixels_read":False,
        "question":"Can Stage127 old detector recover stylized curved/broken 5-small-boat hull positives, unlike its idealized straight-line controls?",
        "families":list(NUISANCES),"classes":list(CLASSES),
        "bow_amplitude_px":BOW_AMPLITUDE,"broken_ink_span_px":INK_SPAN,
        "broken_gap_span_px":GAP_SPAN,"line_thickness_px":STRIPE_THICKNESS,
        "unchanged_old_gate_slope_sign":0.12,
        "qa_checks":checks,"qa_passed":sum(checks.values()),"qa_total":len(checks),
        "known_fixture_results":rows,"strict_positive_recovery_all_nine_scenes":full_recovery,
        "decision":decision,
        "scientific_scope":"Synthetic diagnostic of Stage127 instrument only; no claim that any natural hull carries information or that the drawing is solved.",
        "safety":"No natural pixel inspection, secret-key enumeration, BIP39, wallet, public-address testing or social research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
        "# Stage185 — Stage127 curved/broken hull source-blind calibration",
        "",
        f"- Original PNG SHA provenance correct: **{digest==SHA}**",
        f"- QA: **{sum(checks.values())}/{len(checks)}**",
        f"- New synthetic source-like fixture scenes: **{len(rows)}** (5 hulls per scene)",
        f"- Instrument recovery all nine scenes >=4/5: **{full_recovery}**",
        f"- Decision: **{decision}**",
        "",
        "| Controlled hull stroke style | True hull line sign | Correct stable / 5 | Wrong / 5 | Abstained / 5 |",
        "|---|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(f"| {row['nuisance']} | {row['known_true_class']} | {row['correct_stable']} | {row['wrong_stable']} | {row['abstained']} |")
    lines+=["","The test runs on invented white synthetic scenes only. A detector failure means its old real-source abstention cannot exclude true hull-slope variation. A positive source-like control would still NOT establish author intent or any code. Unmodified original Stage127 files remain archived."]
    (OUT/"REPORT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"stage":185,"qa":f"{sum(checks.values())}/{len(checks)}",
                       "all_nine_source_like_pass":full_recovery,"decision":decision}))
    if not qa: raise SystemExit("CONTROL_FAILURE (repair this Stage only)")
if __name__=="__main__":
    main()
