#!/usr/bin/env python3
"""A11-EXP-141: mirror-copied pencil strokes inside the correctly located hull.

The historical Stage40 'large-boat x-symmetry' used a rectangle that Stage132
proved contained ZERO hull ink. This controlled test examines the actual
large-boat hull, not the sail, using the immutable Stage132 hull polygon.

Natural bilateral HULL SHAPE alone cannot be interpreted as a code. Test the
more specific hypothesis of intentionally copied INTERNAL pencil strokes:
both upper and lower interior bands, blurred grayscale and high-pass stroke
fingerprints, fixed mirror axis with NO axis fitting or lateral search.

No secret candidates, private keys, mnemonic, address or wallet operations.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage132_large_sail_legacy_bbox_audit import POLYGONS

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage141-corrected-hull-bilateral-strokes"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
AXIS_X=275
MIN_OFFSET=12
MAX_OFFSET=180
BANDS=(("upper_hull",803,855),("lower_hull",859,921))
EDGE_EROSION=7
INK_CUTOFF=175
MIN_INK_DENSITY=.075
MIN_MASK_PAIRS=550
MIN_SMOOTH_CORR=.72
MIN_DETAIL_CORR=.56

def paired_mask():
    raw=np.zeros((1105,1600),np.uint8)
    cv2.fillPoly(raw,[np.asarray(POLYGONS["large_hull"],np.int32)],1)
    mask=cv2.erode(raw,np.ones((EDGE_EROSION,EDGE_EROSION),np.uint8),iterations=1)
    return mask.astype(bool)

MASK=paired_mask()
L_SLICE=slice(AXIS_X-MAX_OFFSET,AXIS_X-MIN_OFFSET)
R_SLICE=slice(AXIS_X+MIN_OFFSET+1,AXIS_X+MAX_OFFSET+1)

def pearson(a,b,m):
    x=a[m].astype(np.float64);y=b[m].astype(np.float64)
    x-=x.mean(); y-=y.mean()
    den=float(np.linalg.norm(x)*np.linalg.norm(y))
    return float(np.dot(x,y)/den) if den>1e-9 else 0.

def measure(img):
    ink=(255-img.astype(np.float32))/255.
    smooth=cv2.GaussianBlur(ink,(0,0),1.4)
    detail=ink-cv2.GaussianBlur(ink,(0,0),4.0)
    readings={}
    for name,y0,y1 in BANDS:
        paired=(MASK[y0:y1,L_SLICE] &
                np.fliplr(MASK[y0:y1,R_SLICE]))
        count=int(paired.sum())
        a=img[y0:y1,L_SLICE]
        b=np.fliplr(img[y0:y1,R_SLICE])
        dens=(float((a[paired]<INK_CUTOFF).mean()) if count else 0.,
              float((b[paired]<INK_CUTOFF).mean()) if count else 0.)
        valid=count>=MIN_MASK_PAIRS and min(dens)>=MIN_INK_DENSITY
        ms=pearson(smooth[y0:y1,L_SLICE],
                   np.fliplr(smooth[y0:y1,R_SLICE]),paired) if valid else None
        md=pearson(detail[y0:y1,L_SLICE],
                   np.fliplr(detail[y0:y1,R_SLICE]),paired) if valid else None
        match=bool(valid and ms>=MIN_SMOOTH_CORR and md>=MIN_DETAIL_CORR)
        readings[name]={
            "paired_mask_pixels":count,
            "left_ink_density":round(dens[0],5),
            "right_ink_density":round(dens[1],5),
            "coverage_valid":bool(valid),
            "smoothed_ink_corr":round(ms,6) if ms is not None else None,
            "stroke_detail_corr":round(md,6) if md is not None else None,
            "copied_stroke_match":match,
        }
    return readings

def draw_left(img,seed):
    rng=np.random.default_rng(seed)
    for _,start,end in BANDS:
        for _ in range(120):
            x=int(rng.integers(100,258))
            y=int(rng.integers(start+4,end-4))
            dx=int(rng.integers(-13,14))
            dy=int(rng.integers(-15,16))
            x2=int(np.clip(x+dx,100,258))
            y2=int(np.clip(y+dy,start+2,end-3))
            cv2.line(img,(x,y),(x2,y2),0,int(rng.integers(1,3)),cv2.LINE_AA)

def draw_right_independent(img,seed):
    rng=np.random.default_rng(seed)
    for _,start,end in BANDS:
        for _ in range(120):
            x=int(rng.integers(292,450))
            y=int(rng.integers(start+4,end-4))
            dx=int(rng.integers(-13,14))
            dy=int(rng.integers(-15,16))
            x2=int(np.clip(x+dx,292,450))
            y2=int(np.clip(y+dy,start+2,end-3))
            cv2.line(img,(x,y),(x2,y2),0,int(rng.integers(1,3)),cv2.LINE_AA)

def synthetic(mirrored):
    img=np.full((1105,1600),255,np.uint8)
    draw_left(img,141)
    if mirrored:
        # Precise pixel-level copy about fixed X=275 only; avoids generating
        # symmetrical hull geometry as a bogus interior-stroke positive.
        img[:,AXIS_X+1:2*AXIS_X+1]=np.fliplr(img[:,:AXIS_X])
    else:
        draw_right_independent(img,501)
    return img

def control_suite():
    pos={v:measure(a) for v,a in variants(synthetic(True)).items()
         if v in FORMATS}
    neg={v:measure(a) for v,a in variants(synthetic(False)).items()
         if v in FORMATS}
    pos_pass=sum(all(z["coverage_valid"] and z["copied_stroke_match"]
                     for z in pos[v].values()) for v in FORMATS)
    neg_pass=sum(all(z["coverage_valid"] and not z["copied_stroke_match"]
                     for z in neg[v].values()) for v in FORMATS)
    return {
        "pass":bool(pos_pass==len(FORMATS) and neg_pass==len(FORMATS)),
        "positive_full_format_passes":pos_pass,
        "negative_full_format_passes":neg_pass,
        "cases":len(FORMATS)*len(BANDS)*2,
        "positive":pos,"negative":neg,
    }

def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=SHA:raise SystemExit("Canonical image SHA mismatch")
    gray=np.asarray(Image.open(SOURCE).convert("L"))
    if gray.shape!=(1105,1600):raise SystemExit("Canonical dimensions changed")
    controls=control_suite()
    measurements={v:measure(a) for v,a in variants(gray).items()
                  if v in FORMATS}
    all_covered=all(all(z["coverage_valid"] for z in measurements[v].values())
                    for v in FORMATS)
    all_mirror=all(all(z["copied_stroke_match"] for z in measurements[v].values())
                   for v in FORMATS)
    decision=("CONTROL_FAILURE" if not controls["pass"] else
              "INSUFFICIENT_CORRECTED_HULL_COVERAGE" if not all_covered else
              "REPLICATED_MIRRORED_HULL_STROKE_FINGERPRINT_NEEDS_REVIEW"
              if all_mirror else "NO_EXACT_MIRRORED_HULL_STROKE_FINGERPRINT")
    report={
        "experiment_id":"A11-EXP-141",
        "hypothesis":"the actual complete hull's interior pencil stroke fingerprint is deliberately mirrored across the central keel rather than independently drawn freehand",
        "evidence":"Stage132 validated that the old large_sailboat bbox misses 100% of the hull; Stage40's earlier boat symmetry audit used the defective ROI",
        "scope":"unchanged Stage132 hull polygon, fixed x-axis 275; two nonoverlapping interior y bands; lowpass grayscale and highpass pencil strokes; four source variants",
        "source_sha256":sha,
        "source_geometry":{"hull_polygon":POLYGONS["large_hull"],
            "mirror_x":AXIS_X,"x_offsets":[MIN_OFFSET,MAX_OFFSET],
            "y_bands":[list(x) for x in BANDS]},
        "thresholds":{"min_mask_pixels":MIN_MASK_PAIRS,
            "min_ink_density":MIN_INK_DENSITY,
            "min_smooth_ink_correlation":MIN_SMOOTH_CORR,
            "min_detail_correlation":MIN_DETAIL_CORR},
        "controls":controls,
        "real":measurements,
        "all_real_source_adequate":all_covered,
        "all_real_exact_mirror_fingerprint":all_mirror,
        "decision":decision,
        "interpretation_guard":"A positive is a repeated drawing fingerprint, not a secret; a negative excludes only exact central mirror of internal hull pencil strokes, not approximate bilateral boat shape or symbolic design.",
        "safety_guard":"No key, BIP39, mnemonic, wallet, address or off-image access."
    }
    (OUT/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    lines=[
        "# Stage141 — complete large-hull bilateral pencil-stroke fingerprint",
        "",
        f"- Original image hash checked: **{sha==SHA}**",
        f"- Synthetic mirrored positive control: **{controls['positive_full_format_passes']}/4**",
        f"- Synthetic same-shape independent redraw negative: **{controls['negative_full_format_passes']}/4**",
        f"- Real corrected hull source adequate: **{all_covered}**",
        f"- Exact copied pencil strokes replicated in both bands: **{all_mirror}**",
        f"- Decision: **{decision}**",
        "",
        "| format | upper detail corr | lower detail corr | upper ink corr | lower ink corr |",
        "|---|---:|---:|---:|---:|"
    ]
    for v in FORMATS:
        a=measurements[v]["upper_hull"]
        b=measurements[v]["lower_hull"]
        lines.append(f"| {v} | {a['stroke_detail_corr']} | {b['stroke_detail_corr']} | {a['smoothed_ink_corr']} | {b['smoothed_ink_corr']} |")
    lines+=["","## Interpretation",""]
    if not controls["pass"]:
        lines.append("Synthetic calibration failed. Repair Stage141; do not interpret source.")
    elif not all_covered:
        lines.append("Source-region ink is inadequate for the fixed mirrored hull bands; inconclusive.")
    elif all_mirror:
        lines.append("Source supports mirrored internal strokes; independent review is needed before discussing artist intent.")
    else:
        lines.append("No exact mirrored hull-pencil template at the corrected location, despite positive controls. Ordinary approximate hull symmetry is not ruled out.")
    lines+=["","No mnemonic, key or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":141,"controls":controls["pass"],
                      "coverage":all_covered,"mirrored":all_mirror,
                      "decision":decision}))

if __name__=="__main__":
    main()
