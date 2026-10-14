#!/usr/bin/env python3
"""Stage 137 — large boat hull-to-wake visual reflection audit (image-only).

Stage132 established the old "large_sailboat" box never included its hull.
The later Stage135 apparent hatch-direction coding was explained by ordinary
left/right shading in Stage136. A distinct, physically grounded source-image
question remains: Is the DRAWN full hull mirrored into the water ripples below?

Unlike Stages35 and 47–54 skyline/building reflection diagnostics, this fixed
test compares the actual x=15..535 large hull at y=818..938 with the nearby
lower wake at y=942..1062. It uses blurred grayscale ink and edge structure
in four format variants, plus exactly predeclared lateral-shift nulls.

Positive reflected-hull and negative independently drawn wake controls must
pass before any interpretation. Results are texture statistics, NEVER key or
mnemonic material; nothing encoded or interpreted as a secret.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage137-large-hull-wake-reflection"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")

# 520×120 = matched image apertures; fixed after visual source inspection.
X0,X1=15,535
HULL_Y0,HULL_Y1=818,938
WAKE_Y0,WAKE_Y1=942,1062
HEIGHT=HULL_Y1-HULL_Y0
WIDTH=X1-X0
assert HEIGHT==WAKE_Y1-WAKE_Y0
INK_THR=175
SHIFT_NULL=(-130,-80,80,130)
MIN_HULL_DENSITY=.08
MIN_WAKE_DENSITY=.04
MIN_RAW_CORR=.73
MIN_EDGE_CORR=.57
MIN_SHIFT_GAIN=.19
MAX_NEGATIVE_RAW=.42
MAX_NEGATIVE_EDGE=.42

def windows(gray):
    hull=gray[HULL_Y0:HULL_Y1,X0:X1]
    wake=gray[WAKE_Y0:WAKE_Y1,X0:X1]
    if hull.shape!=(HEIGHT,WIDTH) or wake.shape!=(HEIGHT,WIDTH):
        raise ValueError("source cutouts outside 1600x1105 canvas")
    return hull,wake

def channels(a):
    """Two independent representations, with low-frequency pencil smoothing."""
    ink=(a<INK_THR).astype(np.float32)
    smooth=cv2.GaussianBlur(ink,(0,0),3.2)
    canny=cv2.Canny(a,45,115)
    edge=cv2.GaussianBlur((canny>0).astype(np.float32),(0,0),4)
    return {"ink":smooth,"edge":edge}

def pearson(x,y):
    xf=x.ravel().astype(np.float64)
    yf=y.ravel().astype(np.float64)
    xf-=xf.mean()
    yf-=yf.mean()
    den=np.linalg.norm(xf)*np.linalg.norm(yf)
    return float(np.dot(xf,yf)/den) if den>1e-10 else 0.

def shift_with_blank(im,offset):
    result=np.zeros_like(im)
    if offset>0:
        result[:,offset:]=im[:,:-offset]
    elif offset<0:
        result[:,:offset]=im[:,-offset:]
    else:
        result[:]=im
    return result

def measure(gray):
    a,b=windows(gray)
    a=np.flipud(a)
    features_a=channels(a)
    features_b=channels(b)
    corr={k:pearson(features_a[k],features_b[k]) for k in ("ink","edge")}
    nulls={k:[pearson(features_a[k],shift_with_blank(features_b[k],s))
              for s in SHIFT_NULL] for k in ("ink","edge")}
    gains={k:corr[k]-max(nulls[k]) for k in ("ink","edge")}
    densities={"hull":float(np.mean(a<INK_THR)),
               "wake":float(np.mean(b<INK_THR))}
    valid=bool(densities["hull"]>=MIN_HULL_DENSITY
               and densities["wake"]>=MIN_WAKE_DENSITY)
    accepted=bool(valid
       and corr["ink"]>=MIN_RAW_CORR
       and corr["edge"]>=MIN_EDGE_CORR
       and all(gains[k]>=MIN_SHIFT_GAIN for k in ("ink","edge")))
    return {
        "density":{k:round(v,5) for k,v in densities.items()},
        "raw_correlations":{k:round(v,6) for k,v in corr.items()},
        "shift_null_max":{k:round(max(v),6) for k,v in nulls.items()},
        "improvement_over_shifted_wake":{k:round(v,6) for k,v in gains.items()},
        "valid_source_coverage":valid,
        "strong_mirror_match":accepted,
    }

def draw_pencil(h,w,seed):
    rng=np.random.default_rng(seed)
    img=np.full((h,w),255,np.uint8)
    # Multiple short independently located pencil strokes, not a straight
    # horizon/rectangle, to exercise both grayscale and edge channels.
    for _ in range(130):
        x=int(rng.integers(18,w-50))
        y=int(rng.integers(15,h-18))
        dx=int(rng.integers(12,52))
        dy=int(rng.integers(-12,13))
        cv2.line(img,(x,y),(x+dx,int(np.clip(y+dy,0,h-1))),
                 0,int(rng.integers(1,3)),cv2.LINE_AA)
    return img

def synthetic(mirror):
    img=np.full((1105,1600),255,np.uint8)
    hull=draw_pencil(HEIGHT,WIDTH,137)
    wake=np.flipud(hull.copy()) if mirror else draw_pencil(HEIGHT,WIDTH,271)
    img[HULL_Y0:HULL_Y1,X0:X1]=hull
    img[WAKE_Y0:WAKE_Y1,X0:X1]=wake
    return img

def control_suite():
    same=variants(synthetic(True))
    independent=variants(synthetic(False))
    positives={v:measure(same[v]) for v in FORMATS}
    negatives={v:measure(independent[v]) for v in FORMATS}
    positive_pass=all(positives[v]["strong_mirror_match"] for v in FORMATS)
    negative_pass=all(
        not negatives[v]["strong_mirror_match"]
        and negatives[v]["raw_correlations"]["ink"]<=MAX_NEGATIVE_RAW
        and negatives[v]["raw_correlations"]["edge"]<=MAX_NEGATIVE_EDGE
        for v in FORMATS
    )
    return {
        "pass":bool(positive_pass and negative_pass),
        "positive_pass":positive_pass,
        "negative_pass":negative_pass,
        "cases":8,
        "positive":positives,
        "negative":negatives,
    }

def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=SHA:raise SystemExit("canonical hash mismatch")
    gray=np.asarray(Image.open(SOURCE).convert("L"))
    if gray.shape!=(1105,1600):raise SystemExit("Wrong source image size")
    controls=control_suite()
    measurements={v:measure(img) for v,img in variants(gray).items()
                  if v in FORMATS}
    covered=all(measurements[v]["valid_source_coverage"] for v in FORMATS)
    mirrored=all(measurements[v]["strong_mirror_match"] for v in FORMATS)
    decision=("CONTROL_FAILURE" if not controls["pass"] else
              "INSUFFICIENT_HULL_WAKE_SOURCE" if not covered else
              "HULL_WAKE_MIRROR_CANDIDATE_REQUIRES_REVIEW" if mirrored else
              "NO_EXACT_LARGE_HULL_WAKE_MIRROR")
    result={
        "experiment_id":"A11-EXP-137",
        "hypothesis":"actual whole-boat hull pencilling is reproduced with vertical mirror symmetry in the wake below, instead of merely loosely sketched water",
        "reason":"Stage132 discovered all large-hull ink was omitted by the former large_sailboat ROI. This target was not covered by prior skyline reflection studies.",
        "scope":"fixed full-large-hull and lower wake apertures, non-secret blended ink/edge statistics over four image formats; ±80/130px lateral-shift nulls",
        "canonical_sha256":sha,
        "source_apertures":{"x":[X0,X1],"hull_y":[HULL_Y0,HULL_Y1],
                            "wake_y":[WAKE_Y0,WAKE_Y1]},
        "gates":{"min_ink_corr":MIN_RAW_CORR,"min_edge_corr":MIN_EDGE_CORR,
                 "min_shift_improvement":MIN_SHIFT_GAIN,
                 "min_hull_density":MIN_HULL_DENSITY,
                 "min_wake_density":MIN_WAKE_DENSITY,
                 "lateral_nulls":list(SHIFT_NULL)},
        "controls":controls,"real":measurements,
        "all_source_coverage":covered,"all_mirror_matches":mirrored,
        "decision":decision,
        "interpretation_guard":"A mirror match is visual structure, not steganographic information. A negative retires only direct large-hull-to-wake vertical reflected patch alignment at these fixed apertures.",
        "safety_guard":"No private keys, mnemonic words, codes, wallet operations or social research.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage 137 — visible large hull ↔ wake mirrored reflection","",
           f"- Canonical image verified: **{sha==SHA}**",
           f"- Synthetic reflected/not-reflected controls: **{controls['pass']}**",
           f"- Real aperture source coverage: **{covered}**",
           f"- Full four-variant mirrored support: **{mirrored}**",
           f"- Decision: **{decision}**","",
           "| variant | mirrored ink corr | mirrored edge corr | ink gain vs shift null |",
           "|---|---:|---:|---:|"]
    for v in FORMATS:
        m=measurements[v]
        lines.append(f"| {v} | {m['raw_correlations']['ink']:.3f} | {m['raw_correlations']['edge']:.3f} | {m['improvement_over_shifted_wake']['ink']:.3f} |")
    lines+=["","## Interpretation",""]
    if not controls["pass"]:
        lines.append("Controls failed; repair this SAME Stage137, do not interpret real image.")
    elif not covered:
        lines.append("The two fixed source regions have insufficient visible ink to evaluate reflection. Inconclusive.")
    elif mirrored:
        lines.append("A mirrored hull/wake texture was repeated across four image formats, but independent visual/source verification is required before attributing meaning.")
    else:
        lines.append("No source-robust direct reflected pencil-template relation between the large hull and wake under two metrics. This cannot rule out semantic artistic reflections.")
    lines+=["","No secrets, keys, BIP39 or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":137,"controls":controls["pass"],
                      "covered":covered,"mirrored":mirrored,
                      "decision":decision}))

if __name__=="__main__":
    main()
