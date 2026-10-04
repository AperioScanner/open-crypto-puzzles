#!/usr/bin/env python3
"""Stage 35: skyline-building ↔ water-reflection orientation coupling audit.

Safe, non-cryptographic experiment. Tests whether the fixed H/V building labels are
associated with the orientation of reflection strokes directly below the skyline.

Predeclared scope:
- buildings 3..12 only (1..2 excluded because the large sailboat overlaps their
  below-skyline region);
- reflection band y=330..360, ending before the known small-sails band y=360..480;
- inner 10% of each building x-span;
- two independent orientation measures: Sobel and Fourier anisotropy;
- exact 4-of-10 permutation tests;
- lossy-format replication using JPEG85 + 0.75x down/up resampling.
"""
from __future__ import annotations
import io, itertools, json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage35-building-reflection-coupling"
OUT.mkdir(parents=True,exist_ok=True)

BASELINE="HHVVHHVHHHHV"
ELIGIBLE_IDS=tuple(range(3,13))
REFLECTION_Y0=330
REFLECTION_Y1=360
INNER_FRAC=0.10

def load_gray():
    return np.array(Image.open(SOURCE).convert("L"))

def jpeg85_resample(gray):
    im=Image.fromarray(gray,mode="L")
    buf=io.BytesIO()
    im.save(buf,format="JPEG",quality=85,optimize=False,progressive=False)
    buf.seek(0)
    j=Image.open(buf).convert("L")
    h,w=gray.shape
    small=j.resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    return np.array(small.resize((w,h),Image.Resampling.LANCZOS))

def sobel_anisotropy(crop):
    x=crop.astype(np.float32)
    gx=cv2.Sobel(x,cv2.CV_32F,1,0,ksize=3)
    gy=cv2.Sobel(x,cv2.CV_32F,0,1,ksize=3)
    ex=float(np.mean(gx*gx))
    ey=float(np.mean(gy*gy))
    # Positive = more vertical spatial stroke energy.
    return (ex-ey)/(ex+ey+1e-12)

def fourier_anisotropy(crop):
    x=crop.astype(np.float64)
    x-=x.mean()
    h,w=x.shape
    if min(h,w)<8 or np.std(x)<1e-9:
        return 0.0
    wy=np.hanning(h)[:,None]
    wx=np.hanning(w)[None,:]
    p=np.abs(np.fft.fftshift(np.fft.fft2(x*wy*wx)))**2
    yy,xx=np.indices(p.shape)
    cy=(h-1)/2
    cx=(w-1)/2
    dx=xx-cx
    dy=yy-cy
    r=np.hypot(dx,dy)
    valid=(r>=2)&(r<=0.45*min(h,w))
    # Energy near horizontal frequency axis corresponds to vertical spatial strokes.
    near_h=valid&(np.abs(dy)<=0.40*np.maximum(np.abs(dx),1e-9))
    near_v=valid&(np.abs(dx)<=0.40*np.maximum(np.abs(dy),1e-9))
    eh=float(p[near_h].sum())
    ev=float(p[near_v].sum())
    return (eh-ev)/(eh+ev+1e-12)

def rows_for_image(gray,geom):
    rows=[]
    for bid in ELIGIBLE_IDS:
        b=geom["buildings"][bid-1]
        x0,x1=int(b["x0"]),int(b["x1"])
        m=max(2,int(round((x1-x0)*INNER_FRAC)))
        xa,xb=x0+m,x1-m
        crop=gray[REFLECTION_Y0:REFLECTION_Y1,xa:xb]
        rows.append({
            "id":bid,
            "label":BASELINE[bid-1],
            "bbox":[xa,REFLECTION_Y0,xb,REFLECTION_Y1],
            "sobel":float(sobel_anisotropy(crop)),
            "fourier":float(fourier_anisotropy(crop)),
            "mean_darkness":float(255.0-crop.mean()),
        })
    return rows

def mask_for_v(v_ids):
    ids=np.array(ELIGIBLE_IDS)
    return np.isin(ids,np.array(v_ids))

def signed_mean_diff(vals,v_ids):
    m=mask_for_v(v_ids)
    return float(vals[m].mean()-vals[~m].mean())

def exact_test(vals,observed_v_ids):
    obs=signed_mean_diff(vals,observed_v_ids)
    combos=list(itertools.combinations(ELIGIBLE_IDS,4))
    null=np.array([signed_mean_diff(vals,c) for c in combos],dtype=float)
    p_upper=float(np.mean(null>=obs-1e-15))
    p_two=float(np.mean(np.abs(null)>=abs(obs)-1e-15))
    return {
        "observed_V_minus_H":obs,
        "exact_upper_p":p_upper,
        "exact_two_sided_p":p_two,
        "null_median":float(np.median(null)),
        "null_p95":float(np.percentile(null,95)),
        "null_min":float(null.min()),
        "null_max":float(null.max()),
    }

def analyze(rows):
    obs_v=tuple(r["id"] for r in rows if r["label"]=="V")
    out={}
    for method in ("sobel","fourier"):
        vals=np.array([r[method] for r in rows],dtype=float)
        out[method]=exact_test(vals,obs_v)
        out[method]["H_mean"]=float(np.mean([r[method] for r in rows if r["label"]=="H"]))
        out[method]["V_mean"]=float(np.mean([r[method] for r in rows if r["label"]=="V"]))
    return out

def main():
    geom=json.loads(GEOM.read_text())
    original=load_gray()
    transformed=jpeg85_resample(original)

    orig_rows=rows_for_image(original,geom)
    trans_rows=rows_for_image(transformed,geom)
    orig=analyze(orig_rows)
    trans=analyze(trans_rows)

    for method in ("sobel","fourier"):
        orig[method]["bonferroni_upper_p"]=min(1.0,orig[method]["exact_upper_p"]*2.0)

    positive_orig=all(orig[m]["observed_V_minus_H"]>0 for m in ("sobel","fourier"))
    positive_trans=all(trans[m]["observed_V_minus_H"]>0 for m in ("sobel","fourier"))
    significant=all(orig[m]["bonferroni_upper_p"]<=0.05 for m in ("sobel","fourier"))
    promoted=bool(positive_orig and positive_trans and significant)

    result={
        "experiment_id":"A11-EXP-035",
        "scope":"scene-level association between fixed building H/V labels and directly underlying reflection orientation; no private-key operations",
        "baseline":BASELINE,
        "eligible_buildings":list(ELIGIBLE_IDS),
        "excluded_buildings":[1,2],
        "exclusion_reason":"large sailboat bbox overlaps their below-skyline reflection region",
        "reflection_band_y":[REFLECTION_Y0,REFLECTION_Y1],
        "inner_x_fraction":INNER_FRAC,
        "permutations":210,
        "original_rows":orig_rows,
        "transformed_rows":trans_rows,
        "original_tests":orig,
        "transformed_tests":trans,
        "promotion_rule":"both methods must have positive V-minus-H association, both Bonferroni-corrected one-sided exact p<=0.05 on original, and both association signs must remain positive after JPEG85+0.75x resampling",
        "promoted":promoted,
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 35 — building ↔ water-reflection orientation coupling",
        "",
        "**Experiment:** A11-EXP-035",
        "",
        f"- Eligible buildings: **{list(ELIGIBLE_IDS)}**",
        "- Buildings 1–2 excluded a priori because the large sailboat overlaps their below-skyline region.",
        f"- Fixed reflection band: **y={REFLECTION_Y0}..{REFLECTION_Y1}**",
        "- Exact four-V assignments among 10 buildings: **210**",
        "",
        "## Original image",
        "",
        "| method | H mean | V mean | V-H | one-sided exact p | Bonferroni p | two-sided p |",
        "|:---|---:|---:|---:|---:|---:|---:|",
    ]
    for m in ("sobel","fourier"):
        r=orig[m]
        md.append(f"| {m} | {r['H_mean']:.6f} | {r['V_mean']:.6f} | {r['observed_V_minus_H']:.6f} | {r['exact_upper_p']:.4f} | {r['bonferroni_upper_p']:.4f} | {r['exact_two_sided_p']:.4f} |")
    md += [
        "",
        "## JPEG85 + resampling replication",
        "",
        "| method | H mean | V mean | V-H | one-sided exact p |",
        "|:---|---:|---:|---:|---:|",
    ]
    for m in ("sobel","fourier"):
        r=trans[m]
        md.append(f"| {m} | {r['H_mean']:.6f} | {r['V_mean']:.6f} | {r['observed_V_minus_H']:.6f} | {r['exact_upper_p']:.4f} |")
    md += [
        "",
        f"- promotion rule satisfied: **{promoted}**",
        "",
        "## Interpretation",
        "",
    ]
    if promoted:
        md.append("The V-labeled buildings have unusually more vertical-oriented reflection signal directly beneath them under both independent measures, and the sign survives lossy conversion. This promotes H/V as a scene-level relation worthy of targeted semantic follow-up.")
    else:
        md.append("The fixed H/V labels do not show a sufficiently strong, replicated same-orientation coupling to the directly underlying water-reflection strokes. Keep H/V as a real standalone visual clue, but retire this straightforward building↔reflection orientation hypothesis.")
    md += [
        "",
        "This test does not evaluate arbitrary mirrored crops, offsets, or pixel-level transforms; it only evaluates the predeclared human-visible scene relation.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-035",
        "sobel_p":orig["sobel"]["exact_upper_p"],
        "fourier_p":orig["fourier"]["exact_upper_p"],
        "sobel_diff":orig["sobel"]["observed_V_minus_H"],
        "fourier_diff":orig["fourier"]["observed_V_minus_H"],
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
