#!/usr/bin/env python3
"""A11-EXP-138 — Stage35 building-reflection audit with ALL 12 real buildings.

Stage35 excluded buildings 1 and 2 because the old, incorrect large-boat
rectangle (x44..359,y320..599) overlapped their reflection band. Stage132
showed that rectangle cropped the wrong part of the boat; the manually
registered genuine large sail starts at y398, BEYOND Stage35's y330..360 band.

This repeats the original Stage35 Sobel and Fourier orientation measures,
same H/V labels, same 10% x-inner margins and reflection band, now on all 12
buildings. Exact permutation null considers C(12,4)=495 V-label choices.
Controls are clearly oriented V/H artificial reflections, inverse-reflection
nulls and exact numerical reproduction of Stage35's original 3..12 readings.

No BIP39, key derivation, wallet checks, decoded phrases or off-image sources.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from stage112_corrected_sail_width_progression import variants
from stage35_building_reflection_coupling import (
    BASELINE, REFLECTION_Y0, REFLECTION_Y1, INNER_FRAC,
    sobel_anisotropy, fourier_anisotropy,
)

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
STAGE35=ROOT/"analysis"/"runs"/"stage35-building-reflection-coupling"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage138-all-building-reflection-recheck"
OUT.mkdir(parents=True, exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
ALL_IDS=tuple(range(1,13))
V_IDS=tuple(i for i,c in enumerate(BASELINE,1) if c=="V")
assert len(ALL_IDS)==12 and len(V_IDS)==4 and len(BASELINE)==12
N_PERM=495
METHODS=("sobel","fourier")
MAX_P_ONE_SIDED=.025  # Stage35's two-method Bonferroni 0.05 gate.
MIN_NEW_CROP_MEAN_DARKNESS=2.0
MIN_PER_METHOD_SIGN=0.0
MAX_OLD_SOURCE_ERROR=1e-6
SAIL_START_Y=398  # Minimum registered vertex y, from verified Stage132 polygon.

def crop_for_building(im,b):
    x0,x1=int(b["x0"]),int(b["x1"])
    margin=max(2,int(round((x1-x0)*INNER_FRAC)))
    xa,xb=x0+margin,x1-margin
    a=im[REFLECTION_Y0:REFLECTION_Y1,xa:xb]
    if a.shape[0]!=(REFLECTION_Y1-REFLECTION_Y0) or a.shape[1]<15:
        raise RuntimeError("Building aperture invalid")
    return a,(xa,REFLECTION_Y0,xb,REFLECTION_Y1)

def measure(im,geom):
    rows=[]
    for b in geom["buildings"]:
        bid=int(b["id"])
        if bid<1 or bid>12:raise RuntimeError("Unexpected building ID")
        crop,box=crop_for_building(im,b)
        rows.append({
            "id":bid,"label":BASELINE[bid-1],
            "aperture":list(box),
            "sobel":float(sobel_anisotropy(crop)),
            "fourier":float(fourier_anisotropy(crop)),
            "mean_darkness":float(255-crop.mean()),
        })
    if tuple(x["id"] for x in rows)!=ALL_IDS:raise RuntimeError("Building order drift")
    return rows

def exact_permutation(rows,method):
    vals=np.array([r[method] for r in rows],dtype=np.float64)
    lab=np.array([r["label"]=="V" for r in rows],bool)
    observed=float(vals[lab].mean()-vals[~lab].mean())
    null=[]
    for subset in itertools.combinations(range(12),4):
        selector=np.zeros(12,bool)
        selector[list(subset)]=True
        null.append(float(vals[selector].mean()-vals[~selector].mean()))
    n=np.asarray(null,dtype=np.float64)
    assert n.size==N_PERM
    return {
        "observed_V_minus_H":round(observed,9),
        "exact_one_sided_p":round(float(np.mean(n>=observed-1e-12)),8),
        "exact_two_sided_p":round(float(np.mean(abs(n)>=abs(observed)-1e-12)),8),
        "H_mean":round(float(vals[~lab].mean()),9),
        "V_mean":round(float(vals[lab].mean()),9),
    }

def test_group(rows):
    return {m:exact_permutation(rows,m) for m in METHODS}

def success(tests):
    return all(tests[m]["observed_V_minus_H"]>MIN_PER_METHOD_SIGN
               and tests[m]["exact_one_sided_p"]<=MAX_P_ONE_SIDED
               for m in METHODS)

def synthetic_scene(geom,opposite=False):
    im=np.full((1105,1600),255,np.uint8)
    for b in geom["buildings"]:
        n=int(b["id"])
        cropped,(xa,ya,xb,yb)=crop_for_building(im,b)
        label=BASELINE[n-1]
        vertical=(label=="V") != opposite
        if vertical:
            for xx in range(xa+5,xb-5,8):
                cv2.line(im,(xx,ya+1),(xx,yb-2),0,2,cv2.LINE_AA)
        else:
            for yy in range(ya+4,yb-3,6):
                cv2.line(im,(xa+2,yy),(xb-3,yy),0,2,cv2.LINE_AA)
    return im

def controls(geom,prev,orig_rows):
    # Verify this script reproduces every original Stage35 3..12 metric.
    prior_rows={int(r["id"]):r for r in prev["original_rows"]}
    reproduction=[]
    for r in orig_rows[2:]:
        old=prior_rows[r["id"]]
        residual=max(abs(r[k]-old[k]) for k in ("sobel","fourier","mean_darkness"))
        reproduction.append({"id":r["id"],"maximum_numerical_difference":residual})
    old_pass=all(x["maximum_numerical_difference"]<=MAX_OLD_SOURCE_ERROR for x in reproduction)
    src=SAIL_START_Y>=REFLECTION_Y1
    synthetic_results={}
    for typ in ("positive","reversed_negative"):
        fake=synthetic_scene(geom,opposite=(typ=="reversed_negative"))
        transformed=variants(fake)
        synthetic_results[typ]={v:test_group(measure(transformed[v],geom))
                                for v in FORMATS}
    pos=all(success(synthetic_results["positive"][v]) for v in FORMATS)
    neg=all(not success(synthetic_results["reversed_negative"][v])
            and all(synthetic_results["reversed_negative"][v][m]
                    ["observed_V_minus_H"]<0 for m in METHODS)
            for v in FORMATS)
    return {
        "pass":bool(old_pass and src and pos and neg),
        "cases":8,
        "stage35_numerical_reproduction_pass":old_pass,
        "stage35_reproduction":reproduction,
        "corrected_sail_starts_below_reflection_band":src,
        "corrected_min_sail_y":SAIL_START_Y,
        "first_two_buildings_legacy_exclusion_invalid":src,
        "synthetic_orientation_positive_pass":pos,
        "reversed_orientation_negative_pass":neg,
        "synthetic_tests":synthetic_results,
    }

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=SHA:raise SystemExit("Wrong canonical PNG")
    image=np.asarray(Image.open(PNG).convert("L"))
    if image.shape!=(1105,1600):raise SystemExit("Unexpected dimensions")
    geom=json.loads(GEOM.read_text())
    previous=json.loads(STAGE35.read_text())
    frames=variants(image)
    rows={v:measure(frames[v],geom) for v in FORMATS}
    calibr=controls(geom,previous,rows["original"])
    source_by_variant={
        v:{str(r["id"]):round(r["mean_darkness"],6) for r in rows[v][:2]}
        for v in FORMATS
    }
    covered=all(rows[v][j]["mean_darkness"]>=MIN_NEW_CROP_MEAN_DARKNESS
                for v in FORMATS for j in (0,1))
    tests={v:test_group(rows[v]) for v in FORMATS}
    positive=all(success(tests[v]) for v in FORMATS)
    decision=(
        "CONTROL_FAILURE" if not calibr["pass"] else
        "INSUFFICIENT_BUILDING_1_2_REFLECTION_INK" if not covered else
        "FULL_12_BUILDING_REFLECTION_ASSOCIATION_REQUIRES_REVIEW" if positive else
        "NO_REPLICATED_ALL_12_REFLECTION_ASSOCIATION"
    )
    result={
        "experiment_id":"A11-EXP-138",
        "hypothesis":"the Stage35 H/V-to-reflection comparison may have excluded relevant first-two buildings only because the large-sail geometry was incorrectly localized",
        "evidence":"Stage132 verified the legacy large_sailboat bbox was wrong; real sail apex y>=398, below Stage35's y330..360 reflection band.",
        "scope":"all 12 legacy building x spans with Stage35 unchanged Sobel/Fourier measures, unchanged y330..360 / 10% inner x, all 4 formats and exact 4-of-12 label permutations",
        "canonical_sha256":digest,
        "H_V_labels":BASELINE,
        "expected_exact_permutations":N_PERM,
        "buildings_included":list(ALL_IDS),
        "newly_included_buildings":[1,2],
        "stage35_original_exclusion_reason":"large sailboat overlaps first two below-skyline reflection apertures",
        "actual_registered_sail_top_y":SAIL_START_Y,
        "reflection_band":[REFLECTION_Y0,REFLECTION_Y1],
        "control":calibr,
        "new_reflection_aperture_darkness":source_by_variant,
        "new_regions_adequate":covered,
        "by_format":tests,
        "real_original_rows":rows["original"],
        "real_significant_all_formats":positive,
        "decision":decision,
        "thresholds":{"min_new_crop_mean_darkness":MIN_NEW_CROP_MEAN_DARKNESS,
                      "min_positive_V_H_difference":MIN_PER_METHOD_SIGN,
                      "bonferroni_corrected_one_sided_p_max":MAX_P_ONE_SIDED},
        "interpretation_guard":"A potential coupling requires independent inspection and does not establish an encoded message. A negative retires ONLY this specific 12-building y330-360 Sobel/Fourier coupling; the standalone H/V observation remains valid.",
        "safety":"No secret phrases, crypto keys, wallet, Twitter/social sources or content decoding."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
       "# Stage 138 — source-corrected all-12-building reflection audit","",
       f"- Image SHA256 correct: **{digest==SHA}**",
       f"- Legacy Stage35 original 10-row reproduction: **{calibr['stage35_numerical_reproduction_pass']}**",
       f"- Synthetic positive/reversal negative controls: **{calibr['synthetic_orientation_positive_pass']} / {calibr['reversed_orientation_negative_pass']}**",
       f"- Two newly included reflection crops have adequate ink: **{covered}**",
       f"- Reproduced V/H orientation association 4/4 formats: **{positive}**",
       f"- Decision: **{decision}**","",
       "| variant | Sobel V-H | Sobel p | Fourier V-H | Fourier p |",
       "|---|---:|---:|---:|---:|",
    ]
    for v in FORMATS:
        s=tests[v]["sobel"];f=tests[v]["fourier"]
        lines.append(f"| {v} | {s['observed_V_minus_H']:+.4f} | {s['exact_one_sided_p']:.4f} | {f['observed_V_minus_H']:+.4f} | {f['exact_one_sided_p']:.4f} |")
    lines+=["","## Interpretation",""]
    if not calibr["pass"]:
        lines.append("Control or Stage35 replication failure. Repair Stage138; no source conclusion.")
    elif not covered:
        lines.append("First two newly included reflection bands are too weak. The expanded 12-building test is inconclusive, not a negative.")
    elif positive:
        lines.append("An H/V-reflection relation persists across both estimators and formats; independent visual review is required, not a key interpretation.")
    else:
        lines.append("The previously excluded first two buildings were restored, but no robust positive coupling across all twelve was found. Retire only this direct reflection-orientation criterion.")
    lines+=["","No key, mnemonic or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":138,"controls":calibr["pass"],
                      "coverage":covered,"positive":positive,"decision":decision}))

if __name__=="__main__":
    main()
