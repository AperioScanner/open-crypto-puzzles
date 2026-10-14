#!/usr/bin/env python3
"""A11-EXP-139 — source-adequacy audit of Stage138 all-building reflections.

Stage138 correctly restored buildings 1 and 2, but its archived table shows
two OTHER building reflection apertures (#6 and #11) have almost no visible
ink (mean darkness 0.40 and 0.83), whereas the new regions alone received a
>=2.0 darkness gate. Because the original measurement was a comparison
between *drawn reflection strokes*, blank regions should not contribute
orientation estimates.

This audits that coverage inconsistency under the exact SAME threshold (2.0)
already registered for Stage138's new windows, applied uniformly to all 12.
It never tunes the darkness threshold based on p-values or sign directions.

For each of original/JPEG85/JPEG70/downsample:
- measure Stage138's unchanged Sobel and Fourier y330:360 scores;
- retain the source windows passing the unmodified >=2.0 ink-darkness gate;
- compute exact conditional 4-V label tests over the remaining visible windows.
- record source coverage and outcome; NEVER secret keys, words or wallets.

Positive controls: synthetic 12-building V/H reflection with the two known
low-coverage apertures deliberately blanked, all lossy formats.
Negative controls: inverted synthetic reflections with the same blanks.
Stage138's original per-building measured values must reproduce exactly.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage138_corrected_all_building_reflections import (
    BASELINE, FORMATS, METHODS, measure, synthetic_scene,
    crop_for_building, SHA, MIN_NEW_CROP_MEAN_DARKNESS,
    MAX_P_ONE_SIDED
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOMETRY=ROOT/"data"/"geometry.json"
PREVIOUS=ROOT/"analysis"/"runs"/"stage138-all-building-reflection-recheck"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage139-reflection-coverage-audit"
OUT.mkdir(parents=True,exist_ok=True)

# Unchanged Stage138 threshold and exact same two-method Bonferroni gate.
MIN_DARKNESS=float(MIN_NEW_CROP_MEAN_DARKNESS)
P_GATE=float(MAX_P_ONE_SIDED)
MIN_VALID_BUILDINGS=8
MIN_VALID_V=3
MIN_VALID_H=4
MAX_PREVIOUS_DRIFT=1e-7
SYNTHETIC_MISSING=(6,11) # Independently observed Stage138 near-empty apertures.

def filter_rows(rows):
    usable=[r for r in rows if r["mean_darkness"]>=MIN_DARKNESS]
    bad=[r["id"] for r in rows if r["mean_darkness"]<MIN_DARKNESS]
    nv=sum(r["label"]=="V" for r in usable)
    nh=sum(r["label"]=="H" for r in usable)
    okay=(len(usable)>=MIN_VALID_BUILDINGS
          and nv>=MIN_VALID_V
          and nh>=MIN_VALID_H)
    return usable,bad,okay,nv,nh

def exact_difference(rows,method):
    vals=np.asarray([r[method] for r in rows],dtype=np.float64)
    labels=np.asarray([r["label"]=="V" for r in rows],dtype=bool)
    total=int(len(rows))
    nV=int(labels.sum())
    nH=total-nV
    if not nV or not nH:
        return {"valid":False,"reason":"no class balance"}
    observed=float(vals[labels].mean()-vals[~labels].mean())
    null=[]
    for ids in itertools.combinations(range(total),nV):
        mask=np.zeros(total,dtype=bool)
        mask[list(ids)]=True
        null.append(float(vals[mask].mean()-vals[~mask].mean()))
    null=np.asarray(null,dtype=float)
    p=float(np.mean(null>=observed-1e-12))
    return {
        "valid":True,
        "V_minus_H":round(observed,9),
        "one_sided_exact_p":round(p,8),
        "exact_assignments":int(len(null)),
        "V_mean":round(float(vals[labels].mean()),9),
        "H_mean":round(float(vals[~labels].mean()),9),
    }

def analyze(rows):
    good,bad,valid,nv,nh=filter_rows(rows)
    checks={m:exact_difference(good,m) for m in METHODS} if valid else {}
    positive=bool(valid and all(
        checks[m]["V_minus_H"]>0
        and checks[m]["one_sided_exact_p"]<=P_GATE
        for m in METHODS
    ))
    return {
        "retained_building_ids":[r["id"] for r in good],
        "excluded_low_ink_ids":bad,
        "retained_count":len(good),
        "retained_V_count":nv,
        "retained_H_count":nh,
        "adequate":valid,
        "per_method":checks,
        "strong_orientation_coupling":positive,
        "darkness_by_building":{str(r["id"]):round(r["mean_darkness"],6)
                                for r in rows},
    }

def synthetic_with_blanks(geom,reverse):
    img=synthetic_scene(geom,opposite=reverse)
    for bid in SYNTHETIC_MISSING:
        b=geom["buildings"][bid-1]
        _,(x0,y0,x1,y1)=crop_for_building(img,b)
        # Margin protects fully white source control from JPEG ringing.
        cv2.rectangle(img,(x0-6,y0-7),(x1+6,y1+7),
                      (255,),thickness=-1)
    return img

def calibration(geom,real_original,old):
    prev=old["real_original_rows"]
    numerics=("sobel","fourier","mean_darkness")
    source_reproduction=all(
        a["id"]==b["id"]
        and all(abs(a[k]-b[k])<=MAX_PREVIOUS_DRIFT for k in numerics)
        for a,b in zip(real_original,prev)
    ) and len(real_original)==len(prev)

    positive={}
    negative={}
    for kind,reverse,dest in (
        ("positive",False,positive),
        ("negative",True,negative)
    ):
        im=synthetic_with_blanks(geom,reverse)
        for name,img in variants(im).items():
            if name in FORMATS:
                dest[name]=analyze(measure(img,geom))

    correct_positive=all(
        z["adequate"]
        and z["excluded_low_ink_ids"]==list(SYNTHETIC_MISSING)
        and z["strong_orientation_coupling"]
        and z["retained_V_count"]==4
        and z["retained_H_count"]==6
        for z in positive.values()
    )
    correct_negative=all(
        z["adequate"]
        and z["excluded_low_ink_ids"]==list(SYNTHETIC_MISSING)
        and not z["strong_orientation_coupling"]
        and all(z["per_method"][m]["V_minus_H"]<0 for m in METHODS)
        for z in negative.values()
    )
    return {
        "pass":bool(source_reproduction and correct_positive and correct_negative),
        "source_reproduced":source_reproduction,
        "positive_pass":correct_positive,
        "negative_pass":correct_negative,
        "cases":8,
        "synthetic_missing_ids":list(SYNTHETIC_MISSING),
        "positive":positive,
        "negative":negative,
    }

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Canonical image hash mismatch")
    image=np.asarray(Image.open(SOURCE).convert("L"))
    if image.shape!=(1105,1600):raise RuntimeError("Dimensions changed")
    geometry=json.loads(GEOMETRY.read_text())
    previous=json.loads(PREVIOUS.read_text())
    if previous["canonical_sha256"]!=digest or not previous["control"]["pass"]:
        raise RuntimeError("Stage138 input provenance failed")
    img_variants=variants(image)
    rows={name:measure(img_variants[name],geometry) for name in FORMATS}
    control=calibration(geometry,rows["original"],previous)
    results={name:analyze(rows[name]) for name in FORMATS}
    adequately_covered=all(z["adequate"] for z in results.values())
    excluded_sets=[tuple(z["excluded_low_ink_ids"]) for z in results.values()]
    consistent_exclusions=len(set(excluded_sets))==1
    strong=all(z["strong_orientation_coupling"] for z in results.values())
    decision=(
        "CONTROL_FAILURE" if not control["pass"] else
        "INSUFFICIENT_REFLECTION_SOURCE_COVERAGE"
        if not adequately_covered or not consistent_exclusions else
        "COVERAGE_GATED_REFLECTION_RELATION_REQUIRES_REVIEW"
        if strong else
        "NO_COVERAGE_GATED_REFLECTION_RELATION"
    )
    payload={
        "experiment_id":"A11-EXP-139",
        "hypothesis":"Stage138 may have relied on blank building reflection apertures. Uniformly gate all 12 using the SAME pre-existing mean-darkness>=2.0 standard to avoid noise-defined orientation effects.",
        "basis":"Stage138 observed building #6 mean darkness 0.40 and #11 0.831; the original Stage138 coverage gate was only applied to newly restored buildings 1 and 2.",
        "scope":"all 12 unchanged building positions, same y330..360 reflection band, same Stage35/138 Sobel/Fourier; uniform source coverage screen across four image variants",
        "canonical_sha256":digest,
        "preregistered_thresholds":{"minimum_mean_darkness":MIN_DARKNESS,
          "one_sided_exact_p_max_per_method":P_GATE,
          "min_valid_buildings":MIN_VALID_BUILDINGS,"min_V":MIN_VALID_V,
          "min_H":MIN_VALID_H},
        "controls":control,
        "source_coverage_adequate":adequately_covered,
        "excluded_source_sets_consistent":consistent_exclusions,
        "by_variant":results,
        "all_replicated_significance":strong,
        "decision":decision,
        "limits":"Coverage gating was motivated by Stage138 diagnostics, not a pre-Stage138 independent hypothesis. Multiple prior tests mean any apparent positive must be independently validated, not treated as a nominal p-value finding. Rejection is only for this fixed source-adequate reflection association.",
        "safety_guard":"No private keys, wallets, mnemonic strings, addresses, candidate generation or social-site research."
    }
    (OUT/"result.json").write_text(json.dumps(payload,indent=2)+"\n")
    lines=[
        "# Stage139 — uniform ink-coverage audit of all-building reflection test",
        "",
        f"- Canonical SHA256 verified: **{digest==SHA}**",
        f"- Stage138 exact numerical reproduction: **{control['source_reproduced']}**",
        f"- Synthetic V/H and reversed negative calibration: **{control['positive_pass']} / {control['negative_pass']}**",
        f"- Source-adequate image variants: **{sum(z['adequate'] for z in results.values())}/4**",
        f"- Excluded near-blank buildings are consistent across formats: **{consistent_exclusions}**",
        f"- Both methods pass 4/4: **{strong}**",
        f"- Decision: **{decision}**","",
        "| variant | excluded for low ink | Sobel p | Fourier p |",
        "|---|---|---:|---:|",
    ]
    for fmt in FORMATS:
        z=results[fmt]
        sb=z["per_method"].get("sobel",{})
        ft=z["per_method"].get("fourier",{})
        lines.append(f"| {fmt} | {z['excluded_low_ink_ids']} | {sb.get('one_sided_exact_p','?')} | {ft.get('one_sided_exact_p','?')} |")
    lines+=["","## Interpretation",""]
    if not control["pass"]:
        lines.append("Controls failed. Repair Stage139; no inference about image.")
    elif not adequately_covered or not consistent_exclusions:
        lines.append("The 12-building reflection cohort cannot be evaluated consistently due to low source ink. Inconclusive.")
    elif strong:
        lines.append("Gating the truly blank apertures produced a replicated reflection association, but this is exploratory until confirmed independently; no encryption/cipher interpretation.")
    else:
        lines.append("No replicated direct building H/V-to-reflection orientation relation after applying the SAME minimum source ink threshold to all 12 apertures. The facade H/V observation itself is unaffected.")
    lines+=["","No key, mnemonic, address or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":139,"controls":control["pass"],
      "coverage":adequately_covered,"excluded":excluded_sets,
      "decision":decision}))

if __name__=="__main__":
    main()
