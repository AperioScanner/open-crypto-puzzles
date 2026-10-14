#!/usr/bin/env python3
"""A11-EXP-162: source-adequate version of Stage95's 16-tone giant-sail test.

The old Stage95 sail_mask is built from the known-wrong geometry.json bbox.
Stage132 verified that it omits 66.7% of actual giant sail ink.
Only the source mask is corrected. Stage95's original tone features, synthetic
controls, format transforms, and historical Puzzle5 frozen control scores
are retained. No outside research, tones-to-digits, key or wallet operations.
All thresholds/gates predeclared in analysis/STAGE_QUEUE.md.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import stage95_grayscale_16level_alphabet as stage95
from stage132_large_sail_legacy_bbox_audit import POLYGONS

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE95=ROOT/"analysis"/"runs"/"stage95-grayscale-16level-alphabet"/"result.json"
STAGE132=ROOT/"analysis"/"runs"/"stage132-large-sail-roi-coverage"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage162-full-sail-grayscale-alphabet"
OUT.mkdir(parents=True,exist_ok=True)
SOURCE_SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
INK_LEVELS=np.array([18,31,45,60,75,91,107,123,139,155,171,187,202,216,229,240],np.uint8)
ROI_EROSION=np.ones((5,5),np.uint8)
MIN_REAL_FOREGROUND=1500

def full_sail_mask(shape):
    mask=np.zeros(shape,np.uint8)
    cv2.fillPoly(mask,[np.array(POLYGONS["large_sail"],np.int32)],255)
    return cv2.erode(mask,ROI_EROSION,iterations=1)>0

def read_score(image,mask):
    vals=stage95.foreground_values(image,mask.astype(np.uint8))
    result=stage95.analyze_vals(vals)
    return {"n":result["n"],"score":result["score"],"k16":result["k16"]}

def masked_fixture(mask,kind):
    img=np.full(mask.shape,255,np.uint8)
    yy,xx=np.indices(mask.shape)
    if kind=="16_discrete":
        # 32px geometric patches preserve 16 known tones under 75% resize.
        indices=((xx//32)+3*(yy//32))%16
        img[mask]=INK_LEVELS[indices[mask]]
    elif kind=="smooth_gradient":
        # Continuous gray-gradient negative, same geometry and brightness span.
        xlo=int(np.where(mask)[1].min())
        xhi=int(np.where(mask)[1].max())
        ramp=18+222*(xx-xlo)/max(1,xhi-xlo)
        img[mask]=np.clip(ramp[mask],18,240).astype(np.uint8)
    else:
        raise ValueError(kind)
    return img

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if sha!=SOURCE_SHA:raise RuntimeError("Canonical image hash mismatch")
    archived=json.loads(STAGE95.read_text())
    sourceaudit=json.loads(STAGE132.read_text())
    if sourceaudit["decision"]!="LEGACY_LARGE_SAILBOAT_BBOX_INCOMPLETE":
        raise RuntimeError("Verified Stage132 ROI defect absent")
    if not archived["detector_valid"]:
        raise RuntimeError("Stage95 archived calibrated detector invalid")
    image=np.asarray(Image.open(PNG).convert("L"))
    if image.shape!=(1105,1600):raise RuntimeError("Canonical image geometry mismatch")
    fullmask=full_sail_mask(image.shape)
    oldmask=stage95.sail_mask(image.shape)>0
    archived_region=archived["regions"]["large_sail"]["variants"]
    vreal=stage95.make_variants(image)

    old={}
    full={}
    for fmt in FORMATS:
        old_score=read_score(vreal[fmt],oldmask)
        full_score=read_score(vreal[fmt],fullmask)
        old_expected=float(archived_region[fmt]["target_score"])
        old[fmt]={"score":old_score["score"],"expected":old_expected,
                  "absolute_delta":abs(old_score["score"]-old_expected),
                  "samples":old_score["n"],
                  "pass":abs(old_score["score"]-old_expected)<=0.01}
        full[fmt]=full_score

    # Replay the ORIGINAL Stage95 known synthetic positive/negative benchmark.
    pos_frames=stage95.make_variants(stage95.synthetic_positive())
    neg_frames=stage95.make_variants(stage95.synthetic_negative())
    control_replay={}
    for fmt in FORMATS:
        pm=np.ones(pos_frames[fmt].shape,np.uint8)
        nm=np.ones(neg_frames[fmt].shape,np.uint8)
        p=read_score(pos_frames[fmt],pm)["score"]
        n=read_score(neg_frames[fmt],nm)["score"]
        expected_p=float(archived["positive_scores"][fmt])
        expected_n=float(archived["negative_scores"][fmt])
        control_replay[fmt]={"positive_score":p,"negative_score":n,
           "archived_positive":expected_p,"archived_negative":expected_n,
           "positive_replay_pass":abs(p-expected_p)<=0.02,
           "negative_replay_pass":abs(n-expected_n)<=0.02,
           "calibrated_separation_pass":p>=0.68 and p>=n+0.18}

    # Extra source-shape positive/negative fixtures; no target-dependent choices.
    fixtures={}
    for kind in ("16_discrete","smooth_gradient"):
        fframes=stage95.make_variants(masked_fixture(fullmask,kind))
        fixtures[kind]={fmt:read_score(fframes[fmt],fullmask) for fmt in FORMATS}
    shape_controls={}
    for fmt in FORMATS:
        p=fixtures["16_discrete"][fmt]["score"]
        n=fixtures["smooth_gradient"][fmt]["score"]
        shape_controls[fmt]={"discrete_positive_score":p,
             "smooth_negative_score":n,
             "pass":bool(p is not None and n is not None and
                         p>=0.65 and p>=n+0.15)}

    source_n_ok=all(full[fmt]["n"]>=MIN_REAL_FOREGROUND for fmt in FORMATS)
    checks={
        "canonical_sha_verified":sha==SOURCE_SHA,
        "old_legacy_sail_replay":{fmt:old[fmt]["pass"] for fmt in FORMATS},
        "synthetic_original_positive_replay":{fmt:control_replay[fmt]["positive_replay_pass"] for fmt in FORMATS},
        "synthetic_original_negative_replay":{fmt:control_replay[fmt]["negative_replay_pass"] for fmt in FORMATS},
        "original_synthetic_separation":{fmt:control_replay[fmt]["calibrated_separation_pass"] for fmt in FORMATS},
        "new_polygon_control_separation":{fmt:shape_controls[fmt]["pass"] for fmt in FORMATS},
        "corrected_source_sample_sufficient":source_n_ok,
    }
    passes=sum(bool(x) for k,v in checks.items() for x in (v.values() if isinstance(v,dict) else [v]))
    cases=sum(len(v) if isinstance(v,dict) else 1 for v in checks.values())
    controls={"pass":passes==cases==22,"passed":passes,"cases":cases,"checks":checks}

    variants={}
    near=beating=occupancy=0
    for fmt in FORMATS:
        r=full[fmt]
        score=r["score"]
        prior_pos=float(archived["positive_scores"][fmt])
        prior_neg=float(archived["negative_scores"][fmt])
        prior_author=float(archived["puzzle5_scores"][fmt])
        ratio=((score-prior_neg)/(prior_pos-prior_neg)) if score is not None and prior_pos>prior_neg else None
        near_match=ratio is not None and ratio>=0.65
        above_author=score is not None and score>=prior_author+0.08
        k16=r["k16"] or {}
        occupied=(k16.get("occupied_modes_ge_0p3pct",0)>=14)
        near+=int(near_match);beating+=int(above_author);occupancy+=int(occupied)
        variants[fmt]={"sampled_sail_ink_pixels":r["n"],"corrected_score":score,
            "legacy_stage95_score":old[fmt]["score"],
            "positive_similarity_against_archived_anchors":ratio,
            "beating_archived_puzzle5":bool(above_author),
            "close_to_positive":bool(near_match),
            "occupied_ge_0p3pct":k16.get("occupied_modes_ge_0p3pct"),
            "modes_occupancy_ok":bool(occupied),
            "rmse_normalized":k16.get("rmse_normalized"),
            "mode_concentration_pm2":k16.get("mode_concentration_pm2")}
    promoted=(near>=3 and beating>=3 and occupancy>=3)
    if not controls["pass"]:
        verdict="CONTROL_FAILURE"
    elif promoted:
        verdict="CORRECTED_LARGE_SAIL_TONAL_STRUCTURE_NEEDS_VISUAL_REVIEW"
    elif near<=1:
        verdict="NO_ROBUST_FULL_SAIL_16_TONE_ALPHABET"
    else:
        verdict="CORRECTED_FULL_SAIL_TONAL_INCONCLUSIVE"
    result={
       "experiment_id":"A11-EXP-162","canonical_sha256":sha,
       "source_defect":"Stage95 sail_mask used old truncated large_sailboat bbox documented by Stage132",
       "full_sail_vertices":POLYGONS["large_sail"],
       "full_sail_erosion_5x5_once":True,
       "original_stage95_sail_replay":old,
       "archived_Stage95_synthetic_controls":control_replay,
       "corrected_polygon_controls":shape_controls,
       "controls":controls,
       "source_by_format":variants,
       "positive_comparator_close_variants":near,
       "author_style_control_beaten_variants":beating,
       "occupied_14_modes_variants":occupancy,
       "decision":verdict,
       "scope_limit":"Only Stage95 legacy LARGE SAIL ROI corrected, not the jetty, skyline or whole-frame metrics. Archived Puzzle5 scores reused without accessing external media; grayscale mode inference is not a code or proof of authorship.",
       "safety":"No wallet, address, key, BIP39, textual payload derivation or social/web research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
       "# Stage162 — complete giant sail 16-gray-mode audit after old Stage95 ROI defect","",
       f"- Canonical SHA verified: **{sha==SOURCE_SHA}**",
       f"- Stage95 original legacy large sail replay + archived original controls + polygon controls: **{passes}/{cases}**",
       f"- Corrected large sail has >=1500 ink samples in all source versions: **{source_n_ok}**",
       f"- Corrected full-sail samples near 16-tone artificial positive: **{near}/4**",
       f"- Corrected full-sail scores stronger than archived Puzzle5 reference: **{beating}/4**",
       f"- Corrected full-sail mode occupancy >=14: **{occupancy}/4**",
       f"- Decision: **{verdict}**","",
       "| Variant | old Stage95 ROI score | full corrected source score | normalized positive similarity |",
       "|---|---:|---:|---:|"
    ]
    for fmt in FORMATS:
        q=variants[fmt]
        lines.append(f"| {fmt} | {q['legacy_stage95_score']:.4f} | {q['corrected_score']:.4f} | {q['positive_similarity_against_archived_anchors']:.4f} |")
    lines+=["","The artificial gray-mode calibration and archived author-style benchmark retain Stage95's original limits. A corrected source negative covers this exact full sail shape and 16-gray-mode criterion, NOT hidden keys or arbitrary text/tonal carriers.","",
            "No secret codes, private keys or wallet operations; no external sources fetched.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":162,"controls":f"{passes}/{cases}",
            "near_positive":near,"beating_author":beating,
            "occupancy":occupancy,"decision":verdict}))
if __name__=="__main__":main()
