#!/usr/bin/env python3
"""A11-EXP-154: exterior continuation of ink strokes at two lower corners.

Unlike Stage152 perimeter support and inconclusive Stage153 near-vertex
component connectivity, this measures only *outside* the pre-annotated
triangle, 20-56 px beyond its lower vertices. Precommitted gates are
in analysis/STAGE_QUEUE.md, before this code or workflow were created.
A positive is drawing-geometry evidence, not interpretation of author
intent, a sixth sail, a secret, or any cryptographic payload.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/"clues"/"arweave-puzzle-11.png"
OUT = ROOT/"analysis"/"runs"/"stage154-under-pier-outward-continuations"
OUT.mkdir(parents=True, exist_ok=True)
SHA = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"

FORMATS = ("original","jpeg85","jpeg70","down75_up")
T_SAMPLES = tuple(range(20,57,2))  # 19 precommitted exterior points
HALF_WIDTH = 4
FLANK_OFFSET = 12
DARK = 185
MIN_DARK_SUPPORT = 0.68
MIN_ON_FLANK_CONTRAST = 0.35
MIN_CONSECUTIVE = 8
MIN_REAL_NEGATIVE = 4
KINDS = ("triangle_only","one_slope","transverse_crossbars",
         "flanking_parallel","both_slopes","both_bases")
POSITIVE_KINDS = ("both_slopes","both_bases")

def lower_rays(points):
    """Each of two non-apical vertices has two outward incident rays."""
    p = [np.array(z,dtype=float) for z in points]
    rays = []
    for i in (1,2):
        other = [j for j in (0,1,2) if j!=i]
        for j in other:
            v = p[i]-p[j]
            norm = float(np.linalg.norm(v))
            if not norm: raise ValueError("duplicate vertices")
            rays.append((i,j,p[i],v/norm))
    return rays

def occupancy(gray, origin, direction, t, cross_offset):
    normal = np.array([-direction[1],direction[0]],dtype=float)
    at = origin+float(t)*direction+float(cross_offset)*normal
    occupied=False
    for ds in range(-HALF_WIDTH,HALF_WIDTH+1):
        x,y = np.rint(at + ds*normal).astype(int)
        if 0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]:
            if gray[y,x] < DARK:
                occupied=True
                break
    return occupied

def max_streak(values):
    cur=best=0
    for x in values:
        cur=cur+1 if x else 0
        best=max(best,cur)
    return best

def ray_measure(gray, origin, direction):
    on=[occupancy(gray,origin,direction,t,0) for t in T_SAMPLES]
    left=[occupancy(gray,origin,direction,t,-FLANK_OFFSET) for t in T_SAMPLES]
    right=[occupancy(gray,origin,direction,t,FLANK_OFFSET) for t in T_SAMPLES]
    support=float(np.mean(on))
    flanks=float((np.mean(left)+np.mean(right))/2)
    delta=support-flanks
    run=max_streak(on)
    passed=(support>=MIN_DARK_SUPPORT and
            delta>=MIN_ON_FLANK_CONTRAST and
            run>=MIN_CONSECUTIVE)
    return {"continues":bool(passed),"dark_support":round(support,4),
            "flank_support":round(flanks,4),"on_flank_contrast":round(delta,4),
            "longest_run_samples":run}

def measure(gray, poly):
    rays={}
    for i,j,origin,u in lower_rays(poly):
        rays[f"vertex{i+1}_away_from_{j+1}"]=ray_measure(gray,origin,u)
    paired=(any(rays[f"vertex2_away_from_{j}"]["continues"] for j in (1,3))
        and any(rays[f"vertex3_away_from_{j}"]["continues"] for j in (1,2)))
    return {"paired_lower_vertex_continuations":bool(paired),"rays":rays}

def line(gray, a, b, thickness=3):
    pa=tuple(int(round(v)) for v in a)
    pb=tuple(int(round(v)) for v in b)
    cv2.line(gray,pa,pb,0,thickness,cv2.LINE_AA)

def fixture(poly,kind):
    canvas=np.full((1105,1600),255,np.uint8)
    p=[np.array(v,float) for v in poly]
    for i in range(3):
        line(canvas,p[i],p[(i+1)%3])
    rays=lower_rays(poly)
    for i,j,origin,u in rays:
        # Only slope rays (away from apex, j=0), or base rays (j in 1/2).
        should_continue=(
          kind=="both_slopes" and j==0 or
          kind=="both_bases" and j!=0 or
          kind=="one_slope" and i==1 and j==0
        )
        if should_continue:
            line(canvas,origin,origin+u*62)
        if kind=="flanking_parallel" and j==0:
            normal=np.array([-u[1],u[0]])
            for sign in (-1,1):
                a=origin+u*14+normal*(sign*FLANK_OFFSET)
                b=origin+u*65+normal*(sign*FLANK_OFFSET)
                line(canvas,a,b,2)
        if kind=="transverse_crossbars" and j==0:
            normal=np.array([-u[1],u[0]])
            for t in (28,48):
                mid=origin+u*t
                line(canvas,mid-normal*13,mid+normal*13,2)
    return canvas

def synthetic_controls():
    passed=0; total=0; invalid=[]
    for site,poly in TRIANGLES.items():
        for kind in KINDS:
            frames=variants(fixture(poly,kind))
            expected=kind in POSITIVE_KINDS
            for fmt in FORMATS:
                actual=measure(frames[fmt],poly)["paired_lower_vertex_continuations"]
                correct=(actual==expected)
                passed+=int(correct);total+=1
                if not correct:
                    invalid.append({"site":site,"kind":kind,"variant":fmt,
                                    "expected":expected,"measured":actual})
    return {"pass":passed==total==144,"passed":passed,
            "cases":total,"failures":invalid}

def source_contact_sheet(gray):
    """Raw original + SEPARATE illustrated geometry. Not independent evidence."""
    x0,y0,x1,y1=900,580,1400,920
    crop=gray[y0:y1,x0:x1]
    raw=cv2.cvtColor(crop,cv2.COLOR_GRAY2BGR)
    overlay=raw.copy()
    poly=TRIANGLES["under_pier"]
    points=[(int(x-x0),int(y-y0)) for x,y in poly]
    for i in range(3):
        cv2.line(overlay,points[i],points[(i+1)%3],(20,150,220),1)
    colors=[(0,0,255),(0,155,50),(130,0,155),(20,80,200)]
    for color,(_,_,origin,u) in zip(colors,lower_rays(poly)):
        a=(int(round(origin[0]-x0+u[0]*20)),
           int(round(origin[1]-y0+u[1]*20)))
        b=(int(round(origin[0]-x0+u[0]*56)),
           int(round(origin[1]-y0+u[1]*56)))
        cv2.line(overlay,a,b,color,2,cv2.LINE_AA)
    h,w=raw.shape[:2]
    combined=np.full((h+30,2*w,3),255,np.uint8)
    combined[30:,0:w]=raw
    combined[30:,w:2*w]=overlay
    cv2.putText(combined,"CANONICAL RAW CROP",(12,21),
                cv2.FONT_HERSHEY_SIMPLEX,.56,(0,0,0),1,cv2.LINE_AA)
    cv2.putText(combined,"GUIDES ONLY: 4 EXTERIOR RAYS",(w+12,21),
                cv2.FONT_HERSHEY_SIMPLEX,.52,(0,0,0),1,cv2.LINE_AA)
    cv2.imwrite(str(OUT/"source-exterior-guide.png"),combined)

def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=SHA:raise RuntimeError("Canonical source SHA mismatch")
    gray=np.asarray(Image.open(SOURCE).convert("L"))
    if gray.shape!=(1105,1600):raise RuntimeError("Canonical size mismatch")
    controls=synthetic_controls()
    frames=variants(gray)
    source={form:{name:measure(frames[form],poly)
        for name,poly in TRIANGLES.items()} for form in FORMATS}
    stable={name:all(source[form][name]["paired_lower_vertex_continuations"]
          for form in FORMATS) for name in TRIANGLES}
    # Reject if any of the five true sail sites is stable paired continuation;
    # predeclared at least FOUR of the five must be stable non-continuations.
    known_negative=sum(not stable[name] for name in list(TRIANGLES)[:5])
    candidate=bool(stable["under_pier"])
    if not controls["pass"]:
        verdict="CONTROL_FAILURE"
    elif known_negative<MIN_REAL_NEGATIVE:
        verdict="INSUFFICIENT_REAL_SAIL_NEGATIVE_SEPARATION"
    elif candidate:
        verdict="UNDER_PIER_OUTWARD_CONTINUATION_SUPPORTS_DOCK_GEOMETRY_REVIEW"
    else:
        verdict="NO_STABLE_PAIRED_OUTWARD_CONTINUATION_AT_FIXED_RAYS"
    result={"experiment_id":"A11-EXP-154","sha256":sha,
        "hypothesis":"Under-pier triangular negative space may be bounded by continuing dock braces/rigging, with ink segments projecting beyond both lower vertices, unlike bounded lower sail sides.",
        "source_sites":TRIANGLES,
        "fixed_gates":{"samples_px":list(T_SAMPLES),"cross_section_half_width_px":HALF_WIDTH,
           "flank_offset_px":FLANK_OFFSET,"gray_less_than":DARK,
           "min_ray_support":MIN_DARK_SUPPORT,
           "min_on_flank_contrast":MIN_ON_FLANK_CONTRAST,
           "min_consecutive_samples":MIN_CONSECUTIVE,
           "min_known_sails_negative":MIN_REAL_NEGATIVE},
        "controls":controls,"by_variant":source,
        "stable_paired_by_site":stable,"real_sail_negative_count":known_negative,
        "under_pier_paired_stable":candidate,"decision":verdict,
        "interpretation_limit":"Ink following a projected ray need not be the same physical trace; nearby dock hatching may mimic a continuation. Lossy variants test stability of one source, not independent replication. A positive does not establish hidden content, a sixth sail or author intent.",
        "safety":"No mnemonic, secret, cryptographic key, wallet, address comparisons, social investigation or OCR."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    source_contact_sheet(gray)
    lines=["# Stage154 — outward continuation of lines beyond lower vertices","",
           f"- Canonical PNG SHA verified: **{sha==SHA}**",
           f"- Synthetic fixture controls: **{controls['passed']}/{controls['cases']}**",
           f"- Known genuine sails WITHOUT stable paired continuations: **{known_negative}/5** (requires >=4).",
           f"- Under-pier paired lower-corner continuation: **{candidate}**.",
           f"- Scientific decision: **{verdict}**.","",
           "| Region | paired original | JPEG85 | JPEG70 | resized | stable all 4 |",
           "|---|---|---|---|---|---|"]
    for site in TRIANGLES:
        vals=[source[fmt][site]["paired_lower_vertex_continuations"] for fmt in FORMATS]
        lines.append("| "+site+" | "+" | ".join(map(str,vals))+
                     f" | {stable[site]} |")
    lines.extend(["","## Original source: four predeclared exterior rays",""])
    for i,j,_,_ in lower_rays(TRIANGLES["under_pier"]):
        name=f"vertex{i+1}_away_from_{j+1}"
        v=source["original"]["under_pier"]["rays"][name]
        lines.append(f"- {name}: dark={v['dark_support']:.3f}, flank={v['flank_support']:.3f}, contrast={v['on_flank_contrast']:.3f}, run={v['longest_run_samples']}, passes={v['continues']}")
    lines+=["","## Interpretation guardrails","",
      "Measures line continuation OUTSIDE the original candidate's bottom corners, not vertex connectivity (Stage153), edge presence (Stage152), or sail interior density (Stage151).",
      "The image source is one drawing, JPEG variants are stability checks, and line support may be produced by crossings or independent dock strokes. A positive only warrants manual geometric review.",
      "source-exterior-guide.png shows raw crop separately from overlay; guides are not source ink.",
      "No keys, BIP39, addresses, wallet actions, OCR, external/social investigation.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":154,"controls":f"{controls['passed']}/{controls['cases']}",
       "known_sail_negative":known_negative,"candidate":candidate,"decision":verdict}))
if __name__=="__main__":
    main()
