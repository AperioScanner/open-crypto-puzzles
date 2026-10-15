#!/usr/bin/env python3
"""A11-EXP-177: independent upper-region evidence for two eight-peak lower sail profiles.

Stage176 found stable eight lower-depth intensity peaks on real sail1/sail2,
outside the original n3..7 synthetic calibration. Here the lower-peaks'
SAVED u locations are projected into a disjoint earlier upper 0.49..0.69
trapezoid. Positive source-blind controls are genuine eight apex rays; hard
negatives have identical eight lower rays but NO eight upper connections
(with/without crossbars). A high contrast upper trace is NOT proof of physical
connection or an authored count. All gates preregistered in STAGE_QUEUE.md.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES
from stage176_true_sail_radial_profile import profile_read,draw_synthetic

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE175=ROOT/"analysis"/"runs"/"stage175-stage105-apex-audit"/"result.json"
STAGE176=ROOT/"analysis"/"runs"/"stage176-true-sail-radial-profile"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage177-eight-peak-upper-continuation"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
SITES=("sail1","sail2")
FORMATS=("original","jpeg85","jpeg70","down75_up")
TS=np.linspace(.49,.69,28)
FLANK_DU=.055
SUPPORT_MIN=.70
CONTRAST_MIN=.20
MAX_SOURCE_FLANK_DARK=.90
MIN_UPPER_PEAKS=6
LOWER_CUTOFF_T=.72
HATCH_CROSSBARS=(.51,.59,.66)

def poly_point(poly,u,t):
    a,l,r=[np.asarray(z,float) for z in poly]
    foot=l*(1-u)+r*u
    return a*(1-t)+foot*t

def ray_dark(frame,poly,u):
    pts=np.asarray([poly_point(poly,u,t) for t in TS],np.float32)
    xs=pts[:,0][None,:];ys=pts[:,1][None,:]
    gray=cv2.remap(frame,xs,ys,cv2.INTER_LINEAR)[0].astype(float)
    return float(np.mean((255-gray)/255.0))

def upper_read(frame,poly,peak_us):
    values=[]
    for u in peak_us:
        center=ray_dark(frame,poly,u)
        left=ray_dark(frame,poly,u-FLANK_DU)
        right=ray_dark(frame,poly,u+FLANK_DU)
        flank=(left+right)/2
        contrast=center-flank
        qualifies=center>=SUPPORT_MIN and contrast>=CONTRAST_MIN
        values.append({"u":round(float(u),5),"upper_ink":round(center,5),
             "flank_ink":round(flank,5),
             "upper_vs_flank":round(contrast,5),
             "qualifies":bool(qualifies)})
    return {"count":sum(x["qualifies"] for x in values),
            "expected_eight":len(peak_us)==8,
            "mean_flank_darkness":round(float(np.mean([x["flank_ink"] for x in values])),5),
            "per_ridge":values}

def fake_eight(poly,kind):
    if kind=="connected":
        return draw_synthetic(poly,8,"rays_only")
    a,l,r=(np.asarray(z,float) for z in poly)
    im=np.full((1105,1600),255,np.uint8)
    def pt(v):return tuple(np.rint(v).astype(int))
    for x,y in ((a,l),(a,r),(l,r)):
        cv2.line(im,pt(x),pt(y),0,2,cv2.LINE_AA)
    for i in range(8):
        u=(i+1)/9
        foot=l*(1-u)+r*u
        begin=a*(1-LOWER_CUTOFF_T)+foot*LOWER_CUTOFF_T
        cv2.line(im,pt(begin),pt(foot),0,2,cv2.LINE_AA)
    if kind=="stub_with_hatches":
        for t in HATCH_CROSSBARS:
            x=a*(1-t)+l*t;y=a*(1-t)+r*t
            cv2.line(im,pt(x),pt(y),0,1,cv2.LINE_AA)
    elif kind!="stubs_only":
        raise ValueError("Unknown fixture "+kind)
    return im

def fixture_controls():
    rows=[]
    for site in SITES:
        poly=TRIANGLES[site]
        for kind in ("connected","stubs_only","stub_with_hatches"):
            frames=variants(fake_eight(poly,kind))
            for fmt in FORMATS:
                z=profile_read(frames[fmt],poly)
                upper=(upper_read(frames[fmt],poly,z["peak_u"]) if z["count"]==8
                    else {"count":None,"expected_eight":False})
                correct=(z["count"]==8 and (
                    upper["count"]==8 if kind=="connected" else
                    upper["count"] is not None and upper["count"]<=2))
                rows.append({"site":site,"kind":kind,"format":fmt,
                   "known_lower_ray_stubs":8,
                   "lower_peaks_measured":z["count"],
                   "upper_qualifying_ridges":upper["count"],
                   "pass":bool(correct)})
    return {"pass":len(rows)==24 and all(z["pass"] for z in rows),
            "passed":sum(z["pass"] for z in rows),
            "cases":len(rows),
            "failures":[z for z in rows if not z["pass"]]}

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    a175=json.loads(STAGE175.read_text())
    a176=json.loads(STAGE176.read_text())
    guards={
      "canonical_SHA":digest==SHA,
      "prior_Stage175_known_invalid_apex":a175["decision"]=="CONFIRMED_STAGE105_UNCALIBRATED_AND_WRONG_APEX_SOURCE",
      "prior_Stage176_SHA":a176["canonical_sha256"]==SHA,
      "prior_Stage176_240_synthetic_controls":a176["controls"]["pass"] and a176["controls"]["passed"]==240,
      "Stage176_decision_known_insufficient_coverage":a176["decision"]=="INSUFFICIENT_REAL_SAIL_PROFILE_COVERAGE",
      "two_fixed_independent_real_peak_sites":all(
          a176["source_by_format_sail"][fmt][site]["count"]==8 and
          a176["source_by_format_sail"][fmt][site]["adequate"] and
          len(a176["source_by_format_sail"][fmt][site]["peak_u"])==8
          for site in SITES for fmt in FORMATS),
    }
    fixtures=fixture_controls()
    outcomes={}
    adequate=False
    if all(guards.values()) and fixtures["pass"]:
        original=np.asarray(Image.open(PNG).convert("L"))
        if original.shape!=(1105,1600):raise RuntimeError("PNG geometry changed")
        frames=variants(original)
        outcomes={fmt:{site:upper_read(frames[fmt],TRIANGLES[site],
             a176["source_by_format_sail"][fmt][site]["peak_u"])
              for site in SITES} for fmt in FORMATS}
        adequate=all(outcomes[fmt][site]["mean_flank_darkness"]<MAX_SOURCE_FLANK_DARK
             for site in SITES for fmt in FORMATS)
        supported=all(outcomes[fmt][site]["count"]>=MIN_UPPER_PEAKS
             for site in SITES for fmt in FORMATS)
        low=all(outcomes[fmt][site]["count"]<=2 for site in SITES for fmt in FORMATS)
        if not adequate:
            decision="SOURCE_UPPER_AREA_TOO_HATCHED"
        elif supported:
            decision="UPPER_TRACE_SUPPORT_COMPATIBLE_WITH_EIGHT_PENCIL_RAYS"
        elif low:
            decision="NO_UPPER_SUPPORT_FOR_LOWER_EIGHT_PEAKS"
        else:
            decision="INCONCLUSIVE_UPPER_TRACE_CORROBORATION"
    else:
        decision="CONTROL_FAILURE"
    result={
      "experiment_id":"A11-EXP-177","canonical_source_sha256":digest,
      "hypothesis":"Two true sails' eight stable lower-depth ink-profile peaks may or may not persist in a separate upper source trapezoid, distinguishing genuine radial strokes from local lower hatches.",
      "sites":SITES,"original_immutable_source_vertices":{k:TRIANGLES[k] for k in SITES},
      "calibration":fixtures,"archived_source_preconditions":guards,
      "fixed_test":{"upper_ts_start_end":[float(TS[0]),float(TS[-1])],
        "rows":len(TS),"flank_du":FLANK_DU,
        "center_min":SUPPORT_MIN,"contrast_min":CONTRAST_MIN,
        "max_mean_flank_ink":MAX_SOURCE_FLANK_DARK,
        "min_supported_out_of_8":MIN_UPPER_PEAKS},
      "upper_source_results":outcomes,
      "source_flank_adequate":adequate,
      "decision":decision,
      "scope_limit":"Upper path ink is neither proven connected to apex nor a uniquely authored eight-ray drawing. The eight peak positions are SOURCE-SELECTED by prior Stage176 and provide no independent hypothesis testing p-value. Four image re-encodings share one original.",
      "safety":"No mnemonic, private key, public address/wallet testing, new semantic decoding or outside/social research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage177 — disjoint upper-source test of two eight-peak lower sail profiles","",
      f"- Original PNG SHA correct: **{digest==SHA}**",
      f"- Stage175/176 source scope guards: **{sum(guards.values())}/{len(guards)}**",
      f"- Known connected-eight versus 8 lower-only-with/without-hatches controls: **{fixtures['passed']}/{fixtures['cases']}**",
      f"- Real flank saturation guard: **{adequate}**",
      f"- Decision: **{decision}**","",
      "| Sail | Original supported upper ridges of 8 | JPEG85 | JPEG70 | Resize |",
      "|---|---:|---:|---:|---:|"]
    for site in SITES:
        cs=[outcomes[fmt][site]["count"] if fmt in outcomes else None for fmt in FORMATS]
        lines.append(f"| {site} | {cs[0]} | {cs[1]} | {cs[2]} | {cs[3]} |")
    lines+=["","This new upper-image region was fixed before evaluation. Apparent pencil support does not independently certify apex connection or any secret encoding. No source-guided pixel threshold tuning or wallet/key operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":177,"controls":f"{fixtures['passed']}/{fixtures['cases']}",
       "adequate":adequate,
       "original_sail1":outcomes.get("original",{}).get("sail1",{}).get("count"),
       "original_sail2":outcomes.get("original",{}).get("sail2",{}).get("count"),
       "decision":decision}))
if __name__=="__main__":main()
