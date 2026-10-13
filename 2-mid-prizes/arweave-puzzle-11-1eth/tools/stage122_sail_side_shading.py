#!/usr/bin/env python3
"""Stage 122 — image-only six-sail left/right ink-polarity control audit.

Image-specific question: Do the large triangular sail and five smaller triangular
sails carry a stable, nontrivial *mixed* pattern of left/right shading, or only
ordinary one-sided sketch shading? This is not a sail-width, stroke-count,
sail-lean, exact template-matching, watermark, or secret-key test.

All 6 geometry anchors and classification thresholds are fixed below *before*
reading the image. Coordinates are approximate visual annotations; results only
apply to the listed triangular interiors and explicitly test their adequacy.

No mnemonics, private keys, address checks, wallet access, or hidden text.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "clues" / "arweave-puzzle-11.png"
OUT = ROOT / "analysis" / "runs" / "stage122-sail-side-shading"
OUT.mkdir(parents=True, exist_ok=True)

EXPECTED_SHA = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
LABELS = ("original", "jpeg85", "jpeg70", "down75_up")
# name, mast-x, visible apex-y, tip-to-base height, full half-width at base.
# Precommitted manually located, conservative wedge sites in the original 1600x1105 PNG.
SITES = (
    ("large",   241, 326, 200, 156),
    ("small_1", 1042, 448,  98,  35),
    ("small_2", 1148, 433,  99,  38),
    ("small_3", 1282, 411, 103,  44),
    ("small_4", 1372, 397, 101,  42),
    ("small_5", 1490, 357, 106,  47),
)
INK_CUTOFF = 175
ABS_CONTRAST_GATE = 0.14
RAW_CONTRAST_GATE = 0.13
MAX_NEUTRAL_ABS = 0.14
MIN_PIXELS_PER_WEDGE = 80
MIN_COMBINED_INTERIOR_INK = 0.055

def get_patch_and_masks(arr, site):
    _,cx,top,height,half = site
    h,w = arr.shape
    x0=max(0, cx-int(1.9*half)-9)
    x1=min(w, cx+int(1.9*half)+10)
    y0=max(0,top)
    y1=min(h,top+height)
    if x1<=x0 or y1<=y0:
        raise ValueError("Empty ROI: "+str(site))
    c=arr[y0:y1,x0:x1]
    yy,xx=np.indices(c.shape)
    dy=(yy+y0-top).astype(np.float32)/float(height)
    dx=(xx+x0-cx).astype(np.float32)
    active=(dy>=0.29)&(dy<=0.79)
    local_half=np.maximum(dy*float(half), 1)
    distance=np.abs(dx)
    interior=active & (distance>=.19*local_half) & (distance<=.79*local_half)
    outer=active & (distance>=1.13*local_half) & (distance<=1.64*local_half)
    m={
        "inner_left": interior & (dx<0),
        "inner_right":interior & (dx>0),
        "outer_left":outer & (dx<0),
        "outer_right":outer & (dx>0),
    }
    return c,m

def ratios_and_metric(arr,site):
    c,m=get_patch_and_masks(arr,site)
    dark=c<INK_CUTOFF
    samples={k:int(mask.sum()) for k,mask in m.items()}
    rats={k:float(dark[mask].mean()) if samples[k] else 0.0 for k,mask in m.items()}
    raw=rats["inner_right"]-rats["inner_left"]
    exterior=rats["outer_right"]-rats["outer_left"]
    # Stage 122 repair: exterior wedges intersect the neighboring sailboats/pier.
    # Visually confirmed in mask-contact.png. Retain outside data for QC only.
    corrected=raw
    sample_ok=min(samples.values())>=MIN_PIXELS_PER_WEDGE
    interior_ink=(rats["inner_left"]+rats["inner_right"])/2
    valid=bool(sample_ok and interior_ink>=MIN_COMBINED_INTERIOR_INK)
    return {
        "samples":samples,
        "ratios":{k:round(v,6) for k,v in rats.items()},
        "raw_contrast":round(float(raw),6),
        "outside_contrast":round(float(exterior),6),
        "corrected_contrast":round(float(corrected),6),
        "mean_inside_dark":round(float(interior_ink),6),
        "coverage_valid":valid,
    }

def synthetic(site,polarity,seed):
    """Uniform-area synthetic left/right ink controls with untouched sidebands."""
    _,cx,top,height,half=site
    # Use exactly the same area/coordinates as the real image.
    arr=np.full((1105,1600),255,np.uint8)
    _,m=get_patch_and_masks(arr,site)
    x0=max(0,cx-int(1.9*half)-9)
    x1=min(1600,cx+int(1.9*half)+10)
    patch=arr[top:top+height,x0:x1]
    rng=np.random.default_rng(seed)
    p={"right":(.12,.76),"left":(.76,.12),"neutral":(.38,.38)}
    leftp,rightp=p[polarity]
    for key,prob in (
        ("inner_left",leftp),("inner_right",rightp),
        ("outer_left",.12),("outer_right",.12),
    ):
        inds=np.where(m[key])
        n=len(inds[0])
        if n:
            strokes=rng.random(n)<prob
            patch[inds[0][strokes],inds[1][strokes]]=0
    return arr

def control_suite():
    # Controls are scored at same exact site coordinates through all four
    # lossy transforms. An exact neutral pair must not be promoted as coding.
    seen=[]
    failures=[]
    for i,site in enumerate(SITES):
        for polarity in ("right","left","neutral"):
            synth=synthetic(site,polarity,seed=122000+i*11+("right","left","neutral").index(polarity))
            synthetic_variants=variants(synth)
            all_scores=[]
            for v in LABELS:
                arr=synthetic_variants[v]
                score=ratios_and_metric(arr,site)
                all_scores.append(score["corrected_contrast"])
                if not score["coverage_valid"]:
                    failures.append([site[0],polarity,v,"coverage"])
                elif polarity=="right" and score["corrected_contrast"]<ABS_CONTRAST_GATE+.08:
                    failures.append([site[0],polarity,v,"right_missing"])
                elif polarity=="left" and score["corrected_contrast"]>-(ABS_CONTRAST_GATE+.08):
                    failures.append([site[0],polarity,v,"left_missing"])
                elif polarity=="neutral" and abs(score["corrected_contrast"])>MAX_NEUTRAL_ABS:
                    failures.append([site[0],polarity,v,"neutral_false_positive"])
            seen.append({
                "site":site[0],"control":polarity,
                "min_corrected":round(float(min(all_scores)),6),
                "max_corrected":round(float(max(all_scores)),6),
            })
    return {"cases":len(seen)*len(LABELS),"controls":seen,
            "failures":failures,"passed":len(failures)==0}


def save_site_contact(gray,rows):
    """Save mask contact sheet to check the exact actual image regions."""
    from PIL import ImageDraw
    width,height=470,326
    contact=Image.new("RGB",(width*3,height*2),"white")
    d=ImageDraw.Draw(contact)
    index={x["site"]:x for x in rows}
    for i,site in enumerate(SITES):
        c,m=get_patch_and_masks(gray,site)
        im=np.repeat(c[:,:,None],3,axis=2).astype(np.float32)
        for key,color in (
            ("outer_left",(255,220,0)),("outer_right",(255,220,0)),
            ("inner_left",(30,160,250)),("inner_right",(240,70,130)),
        ):
            mask=m[key]
            im[mask]=im[mask]*.68+np.asarray(color)*.32
        im=Image.fromarray(np.clip(im,0,255).astype(np.uint8))
        scale=min((width-24)/im.width,(height-70)/im.height)
        im=im.resize((int(im.width*scale),int(im.height*scale)),Image.Resampling.NEAREST)
        x=i%3*width
        y=i//3*height
        row=index[site[0]]["per_variant"]["original"]
        d.text((x+10,y+7),site[0]+"  left=blue right=pink outside=yellow",fill=(0,0,0))
        d.text((x+10,y+24),f"raw {row['raw_contrast']:+.3f}; exterior {row['outside_contrast']:+.3f}",fill=(0,0,0))
        contact.paste(im,(x+10,y+48))
    contact.save(OUT/"mask-contact.png")


def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=EXPECTED_SHA:
        raise SystemExit("canonical SHA256 mismatch")
    gray=np.array(Image.open(SOURCE).convert("L"))
    if gray.shape!=(1105,1600):
        raise SystemExit("wrong canonical dimensions")
    controls=control_suite()

    vv=variants(gray)
    rows=[]
    robust=[]
    for site in SITES:
        per={label:ratios_and_metric(vv[label],site) for label in LABELS}
        values=[per[k]["corrected_contrast"] for k in LABELS]
        raws=[per[k]["raw_contrast"] for k in LABELS]
        coverage=all(per[k]["coverage_valid"] for k in LABELS)
        polarity=("R" if min(values)>=ABS_CONTRAST_GATE
                  and min(raws)>=RAW_CONTRAST_GATE else
                  "L" if max(values)<=-ABS_CONTRAST_GATE
                  and max(raws)<=-RAW_CONTRAST_GATE else "?")
        stable=bool(coverage and polarity!="?")
        if stable: robust.append(polarity)
        rows.append({
            "site":site[0],"geometry":list(site[1:]),
            "per_variant":per,"coverage_valid":coverage,
            "stable_polarity":polarity if stable else None,
            "mean_corrected":round(float(np.mean(values)),6),
            "range_corrected":[round(float(min(values)),6),round(float(max(values)),6)],
        })

    nontrivial=(len(robust)>=5 and len(set(robust))==2)
    decision=("CONTROL_FAILURE" if not controls["passed"] else
              "NONTRIVIAL_MIXED_SIDE_SHADING" if nontrivial else
              "UNIFORM_SIDE_SHADING" if len(robust)>=5 and len(set(robust))==1 else
              "NO_STABLE_SIX_SAIL_SIDE_PATTERN")
    promoted=bool(controls["passed"] and nontrivial)
    result={
        "experiment_id":"A11-EXP-122",
        "date":"2026-10-13",
        "hypothesis":"six sail triangles may show a deliberate alternating left/right ink-fill polarity rather than one natural common light-direction convention",
        "evidence":"The canonical scene has one large sail and five smaller, each with visibly hatched and unhatched triangular sectors.",
        "scope":"predeclared symmetric triangular interior wedges, without contaminated outside subtraction, four re-encoding variants; image only",
        "canonical_sha256":sha,
        "anchors_predeclared":[list(x) for x in SITES],
        "controls":controls,
        "raw_ink_threshold":INK_CUTOFF,
        "corrected_contrast_gate":ABS_CONTRAST_GATE,
        "method_repair":"Exterior sidebands cross other objects: leave them diagnostic only; keep fixed inner wedges and original thresholds.",
        "raw_contrast_gate":RAW_CONTRAST_GATE,
        "sites":rows,
        "valid_stable_sites":len(robust),
        "distinct_stable_polarity_count":len(set(robust)),
        "promoted":promoted,
        "decision":decision,
        "coverage_limit":"Approximate fixed visual anchor sites, not semantic sail segmentation. Even a stable mixed pattern does not identify an encoding, word, key, or intentionally placed clue.",
        "safety_guard":"No secret/key/mnemonic enumeration, derivation, validation, wallet calls or transaction operations.",
    }
    save_site_contact(gray,rows)
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
        "# Stage 122 — image-only six-sail signed shading asymmetry",
        "",
        "- Input: canonical 1600x1105 image; SHA256 verified.",
        "- Repair: external reference zones intersect other objects and were excluded from scoring.",
        f"- Synthetic paired dark-side / neutral controls: **{controls['cases']}**, pass=**{controls['passed']}**",
        f"- Stable, image-supported signed sides: **{len(robust)}/6**",
        f"- Nontrivial mixed sides: **{nontrivial}**",
        f"- Decision: **{decision}**",
        "",
        "| sail | right−left INNER contrast (original) | coverage | stable side |",
        "|---|---:|:---:|:---:|",
    ]
    for x in rows:
        o=x["per_variant"]["original"]
        lines.append(f"| {x['site']} | {o['corrected_contrast']:+.3f} | {x['coverage_valid']} | {x['stable_polarity'] or '?'} |")
    lines += ["","## Interpretation",""]
    if not controls["passed"]:
        lines.append("Control failure; this stage cannot be interpreted. Repair Stage 122 without moving on.")
    elif promoted:
        lines.append("The fixed sail wedges show a nontrivial left/right shading mix across at least five objects. This is a *visual observation only* requiring an independent geometric measurement before any interpretation.")
    elif decision=="UNIFORM_SIDE_SHADING":
        lines.append("The detectable sail wedges share one signed side: consistent with ordinary illustration/shading, not a nontrivial alternating side-code.")
    else:
        lines.append("No reproducible multistate left/right shading pattern meets the predeclared gate. Retire only this fixed wedge/contrast mechanism.")
    lines += ["","No private keys, mnemonics, secret candidates or address checks were performed.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"experiment_id":"A11-EXP-122",
        "controls_pass":controls["passed"],"stable_sites":len(robust),
        "decision":decision}))

if __name__=="__main__":
    main()
