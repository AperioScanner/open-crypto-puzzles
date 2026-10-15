#!/usr/bin/env python3
"""A11-EXP-176 — calibrated ray-count profile at independently verified sail apices.

Replaces Stage105's uncalibrated 3..7 radial count and grossly inaccurate
source apex estimates with a NEW simple perspective-normalized fixed row
profile. Source data is never read until 240/240 *source-blind* synthetic
rays/horizontal-only/blank positive+negative fixtures and prior provenance
pass. This count is nonsemantic image structure, never a cipher or key.
Precommitted in analysis/STAGE_QUEUE.md.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from scipy.signal import find_peaks
from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE175=ROOT/"analysis"/"runs"/"stage175-stage105-apex-audit"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage176-true-sail-radial-profile"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
SHAPE=(1105,1600)
SITES={name:points for name,points in TRIANGLES.items() if name.startswith("sail")}
FORMATS=("original","jpeg85","jpeg70","down75_up")
T_SAMPLES=np.linspace(.72,.87,35)
U_SAMPLES=np.linspace(.08,.92,129)
CROSSBARS=(.72,.77,.82,.88)
PEAK_HEIGHT=.35
PEAK_DISTANCE=8
PEAK_PROMINENCE=.25
INK_THRESHOLD=175
MIN_OCCUPANCY=.05
MAX_OCCUPANCY=.85

def profile_read(frame,polygon):
    a,l,r=(np.asarray(x,dtype=float) for x in polygon)
    rowx=[];rowy=[]
    for t in T_SAMPLES:
        start=a*(1-t)+l*t
        end=a*(1-t)+r*t
        row=np.asarray([start*(1-u)+end*u for u in U_SAMPLES])
        rowx.append(row[:,0])
        rowy.append(row[:,1])
    pix=cv2.remap(frame,np.asarray(rowx,np.float32),
        np.asarray(rowy,np.float32),cv2.INTER_LINEAR)
    profile=(255.0-pix.astype(np.float64)).mean(axis=0)/255.0
    peaks,props=find_peaks(profile,height=PEAK_HEIGHT,
         distance=PEAK_DISTANCE,prominence=PEAK_PROMINENCE)
    return {"count":int(len(peaks)),
        "ink_occupancy":round(float(np.mean(pix<INK_THRESHOLD)),6),
        "peak_u":[round(float(U_SAMPLES[x]),5) for x in peaks],
        "peak_heights":[round(float(x),5) for x in props["peak_heights"]],
        "n_samples":int(pix.size),
        "adequate":bool(MIN_OCCUPANCY<=float(np.mean(pix<INK_THRESHOLD))<=MAX_OCCUPANCY)}

def draw_synthetic(poly,n,kind):
    im=np.full(SHAPE,255,np.uint8)
    a,l,r=(np.asarray(p,float) for p in poly)
    def pt(v):return tuple(np.rint(v).astype(int))
    for end1,end2 in ((a,l),(a,r),(l,r)):
        cv2.line(im,pt(end1),pt(end2),0,2,cv2.LINE_AA)
    if kind in ("rays_only","rays_plus_horizontal"):
        for i in range(n):
            u=(i+1)/(n+1)
            foot=l*(1-u)+r*u
            cv2.line(im,pt(a),pt(foot),0,2,cv2.LINE_AA)
    if kind in ("rays_plus_horizontal","horizontal_only"):
        for t in CROSSBARS:
            lo=a*(1-t)+l*t;hi=a*(1-t)+r*t
            cv2.line(im,pt(lo),pt(hi),0,1,cv2.LINE_AA)
    if kind not in ("rays_only","rays_plus_horizontal","horizontal_only"):
        raise ValueError(kind)
    return im

def calibrate():
    cases=[]
    for site,poly in SITES.items():
        for kind in ("rays_only","rays_plus_horizontal"):
            for n in range(3,8):
                scenes=variants(draw_synthetic(poly,n,kind))
                for fmt in FORMATS:
                    actual=profile_read(scenes[fmt],poly)
                    cases.append({"site":site,"kind":kind,"known_true_rays":n,
                      "format":fmt,"observed_count":actual["count"],
                      "passed":actual["count"]==n})
        for kind in ("horizontal_only","blank"):
            scene=(draw_synthetic(poly,0,kind) if kind=="horizontal_only"
                   else np.full(SHAPE,255,np.uint8))
            for fmt,frame in variants(scene).items():
                if fmt not in FORMATS:continue
                actual=profile_read(frame,poly)
                cases.append({"site":site,"kind":kind,"known_true_rays":0,
                  "format":fmt,"observed_count":actual["count"],
                  "passed":actual["count"]==0})
    passed=sum(z["passed"] for z in cases)
    return {"pass":len(cases)==240 and passed==240,
      "passed":passed,"cases":len(cases),
      "failures":[z for z in cases if not z["passed"]]}

def main():
    digest=hashlib.sha256(SRC.read_bytes()).hexdigest()
    old=json.loads(STAGE175.read_text())
    guards={
      "canonical_SHA_provenance":digest==SHA,
      "Stage175_independent_apex_error_confirmed":
        old["decision"]=="CONFIRMED_STAGE105_UNCALIBRATED_AND_WRONG_APEX_SOURCE",
      "Stage175_18_source_guards":
        old["controls_passed"]==old["controls_total"]==18,
      "original_five_apex_geometry":
        [tuple(poly[0]) for poly in SITES.values()]
         ==[(1042,448),(1148,433),(1282,411),(1372,397),(1490,357)],
      "known_five_shapes":len(SITES)==5,
    }
    controls=calibrate()
    if not all(guards.values()) or not controls["pass"]:
        result={};stable=[];adequacy=[];decision="CONTROL_FAILURE"
    else:
        original=np.asarray(Image.open(SRC).convert("L"))
        if original.shape!=SHAPE:raise RuntimeError("Original geometry changed")
        result={
          fmt:{site:profile_read(frame,poly) for site,poly in SITES.items()}
          for fmt,frame in variants(original).items() if fmt in FORMATS}
        stable=[];adequacy=[]
        for site in SITES:
            counts=[result[fmt][site]["count"] for fmt in FORMATS]
            stable.append({"site":site,"count":counts[0] if len(set(counts))==1 else None,
                           "all_four_same":len(set(counts))==1})
            adequacy.extend(result[fmt][site]["adequate"] for fmt in FORMATS)
        known=[r["count"] for r in stable if r["count"] is not None]
        if not all(adequacy):
            decision="INSUFFICIENT_REAL_SAIL_PROFILE_COVERAGE"
        elif len(known)>=4 and all(3<=v<=7 for v in known) and len(set(known))>=2:
            decision="DISTINCT_STABLE_TRUE_SAIL_RAY_COUNTS_NEED_VISUAL_REVIEW"
        elif len(known)>=4 and (all(v==0 for v in known) or len(set(known))==1):
            decision="NO_NONTRIVIAL_STABLE_TRUE_SAIL_RAY_COUNT_PATTERN"
        else:
            decision="INCONCLUSIVE_REAL_SAIL_RAY_COUNTS"
    data={
      "experiment_id":"A11-EXP-176","canonical_sha256":digest,
      "hypothesis":"Known five true small sail triangles may carry distinct stable apex-radial ink ridges detectable after normalizing their cross-sections.",
      "source_defect_motivation":"Stage175 confirmed old Stage105 false apex coordinates 3/5 and completely failed synthetic 3..7 counts.",
      "independent_source_guards":guards,"controls":controls,
      "static_geometry":SITES,
      "fixed_method":{
        "t_rows":len(T_SAMPLES),"t_limits":[float(T_SAMPLES[0]),float(T_SAMPLES[-1])],
        "x_columns":len(U_SAMPLES),"u_limits":[float(U_SAMPLES[0]),float(U_SAMPLES[-1])],
        "resampling":"cv2.remap bilinear","measure":"mean normalized grayscale darkness",
        "find_peaks":{"height":PEAK_HEIGHT,"prominence":PEAK_PROMINENCE,"distance_samples":PEAK_DISTANCE},
        "source_min_max_dark_fraction":[MIN_OCCUPANCY,MAX_OCCUPANCY],
        "source_ink_cutoff":INK_THRESHOLD,
      },
      "source_by_format_sail":result,"per_sail_stability":stable,
      "adequate_real_site_format_count":sum(adequacy),
      "decision":decision,
      "scope_limit":"A radial ink intensity peak may be a disconnected hatch/boat stroke rather than a connected sail spoke. JPEGs are not independent artwork. This narrow countermeasure does not establish an intentionally encoded count or absence of all strokes.",
      "safety":"Image geometry and source only, no keys, private phrases, wallet or public address checks, no external research."
    }
    (OUT/"result.json").write_text(json.dumps(data,indent=2)+"\n")
    lines=["# Stage176 — corrected true-sail normalized radial ink peaks","",
      f"- Canonical SHA checked: **{digest==SHA}**",
      f"- Source and Stage175 guards: **{sum(guards.values())}/{len(guards)}**",
      f"- Synthetic known n3..n7 and horizontal-only/white controls: **{controls['passed']}/{controls['cases']}**",
      f"- Real 5 sails×4 renderings adequate ink occupancy: **{sum(adequacy)}/20**",
      f"- Scientific decision: **{decision}**","",
      "| Real sail | Original source radial peaks | JPEG85 | JPEG70 | Resized | Count stable |",
      "|---|---:|---:|---:|---:|---|"]
    for site in SITES:
        counts=[result[fmt][site]["count"] if fmt in result else None for fmt in FORMATS]
        allsame=(len(set(counts))==1)
        lines.append(f"| {site} | {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} | {allsame} |")
    lines+=["","Controls measure artificial true apex-connected rays and decoy horizontal pencil strokes. Real counts reflect only the FIXED intensity-profile peak detector, not proved connectivity or authored digit patterns. No post-source tuning or key extraction.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":176,"controls":f"{controls['passed']}/{controls['cases']}",
      "adequate":sum(adequacy),
      "stable_sails":sum(r["all_four_same"] for r in stable),
      "decision":decision}))
if __name__=="__main__":main()
