#!/usr/bin/env python3
"""A11-EXP-178: can free-floating diagonal sail hatching mimic eight radial peaks?

All synthetic, on the two pre-existing real eight-peak sail geometries.
Unlike Stage176's horizontal-only negative controls, these fixtures use
disconnected short tilted pencil hatches in the ORIGINAL lower-body sample
window, with no intended interior ray connected to the apex. Reuses the
UNMODIFIED Stage176 profile_read and Stage177 upper_read functions. Source
PNG is checked for SHA only; no source artwork pixel is read.
Preregistered on analysis/STAGE_QUEUE.md before implementation.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np

from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES
from stage176_true_sail_radial_profile import profile_read, draw_synthetic
from stage177_eight_lower_peaks_upper_continuation import upper_read

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"clues"/"arweave-puzzle-11.png"
PRE176=ROOT/"analysis"/"runs"/"stage176-true-sail-radial-profile"/"result.json"
PRE177=ROOT/"analysis"/"runs"/"stage177-eight-peak-upper-continuation"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage178-dense-hatch-false-peaks"
OUT.mkdir(parents=True,exist_ok=True)

SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
SHAPE=(1105,1600)
SITES=("sail1","sail2")
FORMATS=("original","jpeg85","jpeg70","down75_up")
FAMILIES=("short_left_diagonal","short_mixed_diagonal")
SEEDS=tuple(range(17801,17809))
STROKE_COUNTS={"short_left_diagonal":60,"short_mixed_diagonal":100}

def paper_point(poly,u,t):
    apex,left,right=(np.asarray(x,float) for x in poly)
    base=(1-u)*left+u*right
    return apex*(1-t)+t*base

def pix(pt):
    return tuple(np.rint(pt).astype(int))

def fake_hatch(poly,family,seed):
    """Seeded source-independent finite short lines, NEVER apex-launched."""
    rng=np.random.default_rng(seed)
    frame=np.full(SHAPE,255,np.uint8)
    a,l,r=(np.asarray(x,float) for x in poly)
    for p,q in ((a,l),(a,r),(l,r)):
        cv2.line(frame,pix(p),pix(q),0,2,cv2.LINE_AA)
    n=STROKE_COUNTS[family]
    coords=[]
    for _ in range(n):
        t0=float(rng.uniform(.70,.82))
        t1=t0+float(rng.uniform(.035,.09))
        u0=float(rng.uniform(.10,.90))
        amp=float(rng.uniform(.025,.09))
        if family=="short_left_diagonal":
            du=-amp
        else:
            du=amp if int(rng.integers(0,2)) else -amp
        u1=float(np.clip(u0+du,.08,.92))
        cv2.line(frame,pix(paper_point(poly,u0,t0)),
                 pix(paper_point(poly,u1,t1)),0,1,cv2.LINE_AA)
        coords.append((t0,t1,u0,u1))
    geomvalid=bool(all(.70<=t0<=.82 and .735<=t1<=.91 and
                       .08<=u0<=.92 and .08<=u1<=.92
                       for t0,t1,u0,u1 in coords))
    return frame,geomvalid

def calibration():
    cases=[]
    for site in SITES:
        poly=TRIANGLES[site]
        for family in ("eight_connected","horizontal_only","blank"):
            if family=="eight_connected":
                scene=draw_synthetic(poly,8,"rays_only")
            elif family=="horizontal_only":
                scene=draw_synthetic(poly,0,"horizontal_only")
            else:
                scene=np.full(SHAPE,255,np.uint8)
            for fmt,frame in variants(scene).items():
                if fmt not in FORMATS:
                    continue
                z=profile_read(frame,poly)
                if family=="eight_connected":
                    upper=upper_read(frame,poly,z["peak_u"]) if z["count"]==8 else None
                    good=(z["count"]==8 and upper is not None and upper["count"]==8)
                else:
                    upper=None
                    good=(z["count"]==0)
                cases.append({
                    "site":site,"kind":family,"format":fmt,
                    "expected_lower":8 if family=="eight_connected" else 0,
                    "measured_lower":z["count"],
                    "measured_upper_eight":upper["count"] if upper else None,
                    "pass":bool(good)
                })
    return {
        "pass":len(cases)==24 and all(x["pass"] for x in cases),
        "passed":sum(x["pass"] for x in cases),
        "cases":len(cases),
        "failures":[x for x in cases if not x["pass"]]
    }

def main():
    sha=hashlib.sha256(SRC.read_bytes()).hexdigest()
    older176=json.loads(PRE176.read_text())
    older177=json.loads(PRE177.read_text())
    guards={
      "canonical_sha_provenance_only":sha==SHA,
      "Stage176_source_sha":older176["canonical_sha256"]==SHA,
      "Stage176_synthetic_240_known_controls":older176["controls"]["pass"] and older176["controls"]["passed"]==240,
      "Stage176_source_18_of_20_adequate":older176["adequate_real_site_format_count"]==18,
      "Stage176_source_8_peaks_both_sails_in_four_formats":all(
          older176["source_by_format_sail"][fmt][site]["count"]==8 and
          older176["source_by_format_sail"][fmt][site]["adequate"]
          for fmt in FORMATS for site in SITES),
      "Stage177_source_sha":older177["canonical_source_sha256"]==SHA,
      "Stage177_independent_24_controls":older177["calibration"]["pass"] and older177["calibration"]["passed"]==24,
      "Stage177_6_source_guards":all(older177["archived_source_preconditions"].values()),
      "Stage177_real_upper_8_not_confirmed":older177["decision"]=="INCONCLUSIVE_UPPER_TRACE_CORROBORATION",
      "exact_2_sites_and_8_frozen_seeds":len(SITES)==2 and SEEDS==tuple(range(17801,17809)),
    }
    control=calibration()
    responses=[]
    scene_records=[]
    for site in SITES:
        poly=TRIANGLES[site]
        for family in FAMILIES:
            for seed in SEEDS:
                scene,geomvalid=fake_hatch(poly,family,seed)
                res=[]
                for fmt,frame in variants(scene).items():
                    if fmt not in FORMATS:continue
                    z=profile_read(frame,poly)
                    upper=upper_read(frame,poly,z["peak_u"]) if z["count"]==8 else None
                    rec={
                        "site":site,"family":family,"seed":seed,
                        "format":fmt,"known_placed_interior_apex_rays":0,
                        "known_disconnected_hatches":STROKE_COUNTS[family],
                        "synthetic_coordinate_integrity":geomvalid,
                        "lower_count":z["count"],
                        "lower_adequate":z["adequate"],
                        "lower_ink_occupancy":z["ink_occupancy"],
                        "eight_peaks":z["count"]==8,
                        "upper_qualified_if_eight":upper["count"] if upper else None,
                        "upper_flank_dark_if_eight":upper["mean_flank_darkness"] if upper else None,
                    }
                    res.append(rec);responses.append(rec)
                stable=all(x["eight_peaks"] and x["lower_adequate"] for x in res)
                scene_records.append({
                    "site":site,"family":family,"seed":seed,"drawn_hatches":STROKE_COUNTS[family],
                    "geometry_valid":geomvalid,"four_formats":len(res)==4,
                    "stable_eight_peaks_adequate":stable,
                    "counts_by_format":{r["format"]:r["lower_count"] for r in res},
                    "adequate_by_format":{r["format"]:r["lower_adequate"] for r in res},
                    "upper_supported_if_eight_by_format":{
                        r["format"]:r["upper_qualified_if_eight"] for r in res}
                })
    checks={**guards,
            "24_of_24_independent_clean_reference_controls":control["pass"],
            "128_disconnected_diagonal_fixture_results":len(responses)==128,
            "32_unique_textured_source_blind_scenes":len(scene_records)==32,
            "every_hatch_starts_below_apex":all(x["geometry_valid"] for x in scene_records),
            "four_source_renderings_for_each_fixture":all(x["four_formats"] for x in scene_records)}
    can_interpret=all(checks.values())
    mimics=[x for x in scene_records if x["stable_eight_peaks_adequate"]]
    decision=("CONTROL_FAILURE" if not can_interpret else
              "SOURCE_BLIND_HATCHES_CAN_MIMIC_EIGHT_LOWER_PEAKS" if mimics else
              "NO_EIGHT_MIMIC_IN_FIXED_HATCH_FIXTURES")
    by_family={
      family:{
        "scenes":sum(x["family"]==family for x in scene_records),
        "stable_8_adequate":sum(x["family"]==family and x["stable_eight_peaks_adequate"]
                                  for x in scene_records),
        "min_count_original":min(x["counts_by_format"]["original"]
               for x in scene_records if x["family"]==family),
        "max_count_original":max(x["counts_by_format"]["original"]
               for x in scene_records if x["family"]==family)
      } for family in FAMILIES
    }
    data={
       "experiment_id":"A11-EXP-178","canonical_sha_provenance_only":sha,
       "source_pixels_examined":False,
       "source_motivation":"Actual sail1/2 lower profile has 8 stable peaks but real upper continuation fails Stage177; synthetic prior hard negatives had horizontal-only or radial lower stubs, unlike apparent dense diagonal interior texture.",
       "registered_generator":{"sites":SITES,"families":FAMILIES,
           "seeds":SEEDS,"n_strokes":STROKE_COUNTS,"hatch_t_start":[.70,.82],
           "hatch_t_length":[.035,.09],"hatch_u_start":[.10,.90],
           "hatch_u_step_absolute":[.025,.09],"hatch_u_clip":[.08,.92],
           "stroke_px":1,"sail_outline_px":2},
       "source_and_fixture_guards":checks,
       "guards_passed":sum(checks.values()),"guards_total":len(checks),
       "known_calibration":control,
       "adversarial_cases":responses,"per_independent_synthetic_scene":scene_records,
       "by_texture_family":by_family,
       "stable_eight_peaks_with_no_apex_rays_n":len(mimics),
       "stable_eight_peak_scene_descriptions":mimics,
       "decision":decision,
       "limit":"Known-truth RANDOM short disconnected scribbles are NOT representative statistical samples of all artistic hatching. Eight lower peaks may be artifactual even if no selected synthetic scene mimics them; Stage177 upper continuity remains uncorroborated. Same source-format renderings are stability checks, NOT independent source artworks. No actual image-derived private data.",
       "safety":"Only source SHA and controlled synthetic geometry; no mnemonic, wallet, private key, address, social site or decoded phrase."
    }
    (OUT/"result.json").write_text(json.dumps(data,indent=2)+"\n")
    lines=[
      "# Stage178 — adversarial short slanted pencil hatches versus radial eight-peak counter","",
      f"- Canonical original SHA provenance only: **{sha==SHA}**",
      f"- Stage175–177 and generator integrity gates: **{sum(checks.values())}/{len(checks)}**",
      f"- Known connected-eight/horizontal-only/white regression fixtures: **{control['passed']}/{control['cases']}**",
      f"- Two sites × two texture families × eight predetermined seeds × four formats: **{len(responses)}** measurements",
      f"- Distinct known NON-apex-ray textures that mimic eligible eight peaks in all four formats: **{len(mimics)}/{len(scene_records)}**",
      f"- Scientific decision: **{decision}**","",
      "| Known disconnected hatch family | Independent synthetic scenes | Stable eligible eight-peak counterexample | Original count range |",
      "|---|---:|---:|---|"
    ]
    for family,r in by_family.items():
        lines.append(f"| {family} | {r['scenes']} | {r['stable_8_adequate']} | {r['min_count_original']}–{r['max_count_original']} |")
    lines+=["","Every negative scene contains only short disconnected lower sail pencil hatches, no intentionally apex-connected INTERIOR radial ray. A measured eight is not proof the real puzzle contains the same texture. No thresholds, source windows or success criteria changed after the outcome.","",
       "Historical Stage176/177 original-source observations are preserved; no numeric decoding or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":178,"guards":f"{sum(checks.values())}/{len(checks)}",
      "controls":f"{control['passed']}/{control['cases']}",
      "mimic_scenes":len(mimics),"decision":decision}))
if __name__=="__main__":
    main()
