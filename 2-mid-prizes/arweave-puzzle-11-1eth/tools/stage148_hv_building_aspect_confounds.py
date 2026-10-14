#!/usr/bin/env python3
"""A11-EXP-148 — does naturally drawn BUILDING GEOMETRY explain H/V hatch labels?

Unlike the many now-closed user-mirrored silhouettes, the original skyline's
stable 12 labels H H V V H H V H H H H V (H=0,V=1 => visually 0x321)
are genuine independent source ink observations. Before promoting them as
an encoded instruction, test the mundane art explanation that hatching
direction was determined by the dimensions of its building.

Exactly four predeclared non-key explanatory features:
  facade width, facade height, height/width, facade area.
Exact C(12,4)=495 permutations preserve four V and eight H buildings.
A max-absolute-standardized-difference null adjusts for inspecting these
four correlated features jointly; use a TWO-SIDED familywise p<=.05 gate.

The source H/V sequence is recomputed on the canonical PNG and three lossy
renderings with Stage10's original inner-crop/Sobel procedure. All roof source
locations are validated by Stage143's independent roof-row pixel check.
Synthetic wide-V, tall-V and geometry-invariant cases verify the exact test.

Result tests a SOURCE style confound only; even a negative does not establish
intent, data encoding, 321 significance, a private key, or a mnemonic.
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
from stage143_mirrored_skyline_chess_shapes import source_roof_test

ROOT=Path(__file__).resolve().parents[1]
IMAGE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOMETRY=ROOT/"data"/"geometry.json"
STAGE10=ROOT/"analysis"/"runs"/"stage10-marker-robustness"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage148-hv-building-shape-confound"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
EXPECTED="HHVVHHVHHHHV"
FORMATS=("original","jpeg85","jpeg70","down75_up")
PREDICTORS=("facade_width","facade_height","height_to_width_ratio","facade_area")
NUM_V=4
NUM_BUILDINGS=12
CLASS_SCORE_CUTOFF=.06
INNER_MARGIN=.12
MIN_ROOF_PIXELS=12
P_FWER_CUTOFF=.05

def feature_matrix(buildings):
    rows=[]
    for b in buildings:
        w=int(b["x1"])-int(b["x0"])
        h=int(b["bottom_y"])-int(b["roof_y"])
        if min(w,h)<=0:raise RuntimeError("Invalid building dimensions")
        rows.append([w,h,float(h/w),w*h])
    return np.asarray(rows,dtype=float)

def bitmap_labels(gray,buildings):
    labels=[]
    scores=[]
    for b in buildings:
        x0,x1,y0,y1=[int(b[k]) for k in ("x0","x1","roof_y","bottom_y")]
        w=x1-x0;h=y1-y0
        mx=max(5,int(w*INNER_MARGIN))
        my=max(6,int(h*INNER_MARGIN))
        patch=gray[y0+my:y1-my,x0+mx:x1-mx]
        if min(patch.shape)<12:
            raise RuntimeError("Bounding box too narrow for building")
        patch=cv2.GaussianBlur(patch,(3,3),0)
        gx=cv2.Sobel(patch,cv2.CV_64F,1,0,ksize=3)
        gy=cv2.Sobel(patch,cv2.CV_64F,0,1,ksize=3)
        ex=float(np.mean(np.abs(gx)))
        ey=float(np.mean(np.abs(gy)))
        score=(ex-ey)/(ex+ey+1e-12)
        labels.append("V" if score>CLASS_SCORE_CUTOFF else
                      "H" if score<-CLASS_SCORE_CUTOFF else "M")
        scores.append(round(score,7))
    return "".join(labels),scores

def all_null_assignments(X,labels):
    if X.shape!=(NUM_BUILDINGS,len(PREDICTORS)):
        raise RuntimeError("Wrong feature matrix dimensions")
    observed=np.asarray([c=="V" for c in labels],dtype=bool)
    if int(observed.sum())!=NUM_V:
        raise RuntimeError("Unexpected V count")
    perms=np.array(list(itertools.combinations(range(NUM_BUILDINGS),NUM_V)),dtype=int)
    if perms.shape!=(495,4):
        raise RuntimeError("Expected exactly C(12,4) assignments")
    masks=np.zeros((len(perms),NUM_BUILDINGS),dtype=bool)
    masks[np.arange(len(perms))[:,None],perms]=True
    # 4 V versus 8 H conditional null with row assignments fixed.
    vmean=(masks.astype(float)@X)/NUM_V
    hmean=((~masks).astype(float)@X)/(NUM_BUILDINGS-NUM_V)
    differences=vmean-hmean
    null_std=differences.std(axis=0)
    z=differences/np.where(null_std>1e-12,null_std,1.0)
    z[:,null_std<=1e-12]=0.0
    obs_v=X[observed].mean(axis=0)
    obs_h=X[~observed].mean(axis=0)
    obs_diff=obs_v-obs_h
    obs_z=np.divide(obs_diff,null_std,
                    out=np.zeros_like(obs_diff,dtype=float),where=null_std>1e-12)
    max_score=float(np.max(np.abs(obs_z)))
    null_max=np.max(np.abs(z),axis=1)
    pmax=float(np.mean(null_max>=max_score-1e-10))
    p_each=[
        float(np.mean(np.abs(z[:,i])>=abs(obs_z[i])-1e-10))
        for i in range(len(PREDICTORS))
    ]
    return {
       "observed_H_mean":{p:round(float(x),6) for p,x in zip(PREDICTORS,obs_h)},
       "observed_V_mean":{p:round(float(x),6) for p,x in zip(PREDICTORS,obs_v)},
       "V_minus_H":{p:round(float(x),6) for p,x in zip(PREDICTORS,obs_diff)},
       "standardized_difference":{p:round(float(x),6) for p,x in zip(PREDICTORS,obs_z)},
       "exact_two_sided_per_feature_p":{p:round(float(x),8) for p,x in zip(PREDICTORS,p_each)},
       "max_standardized_feature_difference":round(max_score,6),
       "familywise_exact_permutation_p":round(pmax,8),
       "permutations":len(perms),
       "geometry_association_familywise":bool(pmax<=P_FWER_CUTOFF),
    }

def synthetic_controls():
    # H groups remain narrow; V group much wider (positive),
    # or much taller (second positive). All identical (negative).
    widths=np.array([50,55,60,65,70,75,80,85,140,150,160,170],float)
    heights=np.full(NUM_BUILDINGS,130.,float)
    heights_alt=np.array([100,105,110,115,120,125,130,135,220,230,240,250],float)
    uniform=np.full(NUM_BUILDINGS,100.,float)
    def compose(w,h):
        return np.column_stack([w,h,h/w,w*h])
    labels="H"*8+"V"*4
    wides=all_null_assignments(compose(widths,heights),labels)
    tall=all_null_assignments(compose(np.full(12,100.),heights_alt),labels)
    plain=all_null_assignments(compose(uniform,uniform),labels)
    good=(wides["geometry_association_familywise"]
          and tall["geometry_association_familywise"]
          and not plain["geometry_association_familywise"]
          and plain["familywise_exact_permutation_p"]==1.0)
    return {
       "pass":bool(good),
       "wide_facades_positive_p":wides["familywise_exact_permutation_p"],
       "tall_facades_positive_p":tall["familywise_exact_permutation_p"],
       "all_equal_null_p":plain["familywise_exact_permutation_p"],
       "cases":3,
    }

def source_validation(original,buildings,prior):
    verified={}
    for form,image in variants(original).items():
        if form not in FORMATS:continue
        seq,scores=bitmap_labels(image,buildings)
        roof_checks=source_roof_test(image,{"buildings":buildings})
        verified[form]={
            "observed_HV_labels":seq,
            "matches_stage10":seq==EXPECTED,
            "roofline_pixels_supported":int(sum(r["adequate_roof_line"] for r in roof_checks)),
            "orientation_scores":scores
        }
    matched=all(row["matches_stage10"] and row["roofline_pixels_supported"]>=MIN_ROOF_PIXELS
                for row in verified.values())
    prior_ok=(prior["baseline_sequence"]==EXPECTED
              and prior["baseline_mapping_H0_V1"]["hex"]=="321")
    return matched and prior_ok,verified

def main():
    digest=hashlib.sha256(IMAGE.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Canonical source checksum mismatch")
    gray=np.asarray(Image.open(IMAGE).convert("L"))
    if gray.shape!=(1105,1600):raise RuntimeError("Wrong source dimensions")
    geom=json.loads(GEOMETRY.read_text())
    prior=json.loads(STAGE10.read_text())
    buildings=geom["buildings"]
    if len(buildings)!=NUM_BUILDINGS or [b["id"] for b in buildings]!=list(range(1,13)):
        raise RuntimeError("Building order drift")
    controls=synthetic_controls()
    source_ok,per_format=source_validation(gray,buildings,prior)
    actual=all_null_assignments(feature_matrix(buildings),EXPECTED)
    decision=(
        "CONTROL_FAILURE" if not controls["pass"] else
        "H_V_IMAGE_SOURCE_REPRODUCTION_FAILURE" if not source_ok else
        "BUILDING_GEOMETRY_CORRELATES_WITH_HV"
        if actual["geometry_association_familywise"] else
        "NO_SIMPLE_BUILDING_SHAPE_EXPLANATION_FOR_HV"
    )
    result={
       "experiment_id":"A11-EXP-148",
       "question":"Does ordinary skyline building width/height/aspect/area explain the stable H/V pencil-hatching sequence instead of independent intentional binary marks?",
       "motivation":"The source H/V marker is robust, unlike user-generated mirrored chess/needle illusions. Test a plausible ordinary-art confound before treating the 0x321 visual reading as author intent.",
       "scope":"12 canonical facade geometry annotations plus Stage10 source-verified H/V orientations; exact C(12,4) conditional permutations; joint max-standardized-statistic multiple-feature protection; 4 image variants for source only.",
       "sha256":digest,
       "baseline_sequence":EXPECTED,
       "predictors":list(PREDICTORS),
       "controls":controls,
       "source_replicated_in_four_formats":source_ok,
       "source_variants":per_format,
       "shape_permutation_test":actual,
       "decision":decision,
       "interpretation_limit":"A positive says common building proportions may explain painting direction, not intentional bits. A negative says these four mundane shape covariates alone do NOT account for V vs H, but DOES NOT establish that 001100100001 / 0x321 was intended as an instruction. Multiple prior puzzle hypotheses remain unadjusted.",
       "safety":"Public original image and geometry only; no private-key generation, BIP39, wallets, addresses, transactions or external clues."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
       "# Stage148 — H/V city-building hatching versus ordinary shape proportion",
       "",
       f"- Original PNG verified: **{digest==SHA}**",
       f"- Synthetic wide/tall/invariant permutation controls: **{controls['pass']}**",
       f"- 12-building H/V source labels and roof pixels reproduced across 4 formats: **{source_ok}**",
       f"- Familywise exact shape association p: **{actual['familywise_exact_permutation_p']:.6f}**",
       f"- Decision: **{decision}**","",
       "| visible shape predictor | V–H mean | exact two-sided p |",
       "|---|---:|---:|"
    ]
    for name in PREDICTORS:
        lines.append(f"| {name} | {actual['V_minus_H'][name]:+.3f} | {actual['exact_two_sided_per_feature_p'][name]:.4f} |")
    lines+=["","## Interpretation",""]
    if not controls["pass"] or not source_ok:
        lines.append("Synthetic controls or original source H/V validation failed: repair Stage148.")
    elif actual["geometry_association_familywise"]:
        lines.append("H/V fill directions associate with ordinary building dimensions in this fixed family; compare to natural drawing choices before claiming intentional coding.")
    else:
        lines.append("No strong link between the 4 precommitted ordinary building shape dimensions and H/V hatching. The source pattern remains a visual observation but is NOT validated as a coded 321 instruction.")
    lines+=["","No keys, mnemonic words or wallets were accessed or produced.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":148,"controls":controls["pass"],
                      "source":source_ok,
                      "p_fwer":actual["familywise_exact_permutation_p"],
                      "decision":decision}))

if __name__=="__main__":main()
