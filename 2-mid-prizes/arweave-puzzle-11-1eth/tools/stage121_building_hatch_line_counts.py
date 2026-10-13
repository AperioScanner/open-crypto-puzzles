#!/usr/bin/env python3
"""Stage 121: 12-building visible hatch-line count consistency.

Image-only experiment; independent of the known H/V orientation sequence as a
symbol interpretation. Test whether each facade has a precisely repeatable
integer count of long hand-drawn shading lines, using projection runs versus
oriented morphological components across lossy image variants.

Unlike earlier facade density/tone/roof/topology tests, this checks exact
individual long-stroke counts. Counts are NOT mapped to mnemonic words,
letters, private keys, or wallet addresses.
"""
from __future__ import annotations
import hashlib,io,json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage121-building-hatch-line-counts"
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
HV="HHVVHHVHHHHV"
VARIANTS=("original","jpeg85","jpeg70","down75_up")
INK_THRESHOLD=170

def central_crop(gray,b):
    x0,x1,y0,y1=int(b["x0"]),int(b["x1"]),int(b["roof_y"]),int(b["bottom_y"])
    dx=max(3,int(round(.12*(x1-x0))))
    dy=max(4,int(round(.12*(y1-y0))))
    return gray[y0+dy:y1-dy,x0+dx:x1-dx]

def projection_count(c,orientation):
    ink=(c<INK_THRESHOLD).astype(np.uint8)
    h,w=ink.shape
    if h<12 or w<12:
        return 0
    p=ink.mean(axis=1 if orientation=="H" else 0)
    sm=np.convolve(p,[.2,.6,.2],mode="same")
    lo=float(np.percentile(sm,25));hi=float(np.percentile(sm,90))
    if hi-lo<0.035:
        return 0
    active=sm>(lo+.38*(hi-lo))
    starts=np.where(active & ~np.r_[False,active[:-1]])[0]
    ends=np.where(active & ~np.r_[active[1:],False])[0]
    return sum(int(hi-lo+1>=2) for lo,hi in zip(starts,ends))

def oriented_components(c,orientation):
    ink=(c<INK_THRESHOLD).astype(np.uint8)
    h,w=ink.shape
    span=w if orientation=="H" else h
    kernel_size=max(8,int(round(.40*span)))
    kernel=np.ones((1,kernel_size) if orientation=="H" else (kernel_size,1),np.uint8)
    opened=cv2.morphologyEx(ink,cv2.MORPH_OPEN,kernel)
    _,_,stats,_=cv2.connectedComponentsWithStats(opened,8)
    return sum(int((r[2] if orientation=="H" else r[3])>=kernel_size*.8)
               for r in stats[1:])

def count_both(c,orientation):
    return {"projection":int(projection_count(c,orientation)),
            "morphology":int(oriented_components(c,orientation))}

def synthetic(n,orientation):
    """Same style of synthetic straight hatch lines with small endpoint jitter."""
    H,W=200,128
    rng=np.random.default_rng(12+n)
    a=np.full((H,W),255,np.uint8)
    if orientation=="H":
        for y in np.linspace(15,H-16,n).round().astype(int):
            cv2.line(a,(14,y+int(rng.integers(-1,2))),
                     (W-14,y+int(rng.integers(-1,2))),0,2,cv2.LINE_AA)
    else:
        for x in np.linspace(13,W-14,n).round().astype(int):
            cv2.line(a,(x+int(rng.integers(-1,2)),15),
                     (x+int(rng.integers(-1,2)),H-15),0,2,cv2.LINE_AA)
    return a

def control_patches():
    out={}
    passes=[]
    for orientation in ("H","V"):
        for count in (5,7,10,13,16):
            patch=synthetic(count,orientation)
            observed={}
            for v,img in variants(patch).items():
                if v not in VARIANTS:
                    continue
                x=count_both(img,orientation)
                observed[v]=x
                passes.extend(abs(value-count)<=1 for value in x.values())
            out[f"{orientation}_{count}"]=observed
    dot=np.full((200,128),255,np.uint8)
    dot[30:180:16,20:110:17]=0
    blank_control={o:count_both(dot,o) for o in ("H","V")}
    passes.extend(x["morphology"]<=1 for x in blank_control.values())
    return {"synthetic_counts":out,"nonline_dot_control":blank_control,
            "cases":len(passes),"controls_pass":bool(all(passes))}

def main():
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=EXPECTED_SHA:
        raise SystemExit("Unexpected canonical image SHA256")
    base=np.array(Image.open(SOURCE).convert("L"))
    if base.shape!=(1105,1600):
        raise SystemExit("Unexpected image geometry")
    buildings=json.loads(GEOM.read_text())["buildings"]
    if len(buildings)!=12 or [x["id"] for x in buildings]!=list(range(1,13)):
        raise SystemExit("Fixed building atlas changed")
    controls=control_patches()
    images=variants(base)
    real=[]
    for b,o in zip(buildings,HV):
        values={}
        for name in VARIANTS:
            values[name]=count_both(central_crop(images[name],b),o)
        nums=[v for x in values.values() for v in x.values()]
        stable=max(nums)-min(nums)<=1 and min(nums)>=3
        median=int(round(float(np.median(nums)))) if stable else None
        real.append({"building":b["id"],"orientation":o,"counts":values,
                     "stable":stable,"stable_count":median,
                     "count_range":[min(nums),max(nums)]})
    stable=[x for x in real if x["stable"]]
    distinct=sorted({x["stable_count"] for x in stable})
    promoted=bool(controls["controls_pass"] and len(stable)>=10 and len(distinct)>=4)
    decision=("CONTROL_FAILURE" if not controls["controls_pass"] else
              "ROBUST_HATCH_COUNT_CHANNEL" if promoted else
              "NO_ROBUST_EXACT_HATCH_COUNT_CHANNEL")
    result={
        "experiment_id":"A11-EXP-121",
        "scope":"image-only per-building long hatch-line counts, not per-pixel bits or mnemonic/key guesses",
        "canonical_sha256":sha,
        "known_orientation_only_for_measurement":HV,
        "fixed_crop_margin_fraction":0.12,
        "ink_threshold":INK_THRESHOLD,
        "controls":controls,
        "building_results":real,
        "stable_buildings":len(stable),
        "distinct_stable_counts":distinct,
        "decision":decision,
        "promoted":promoted,
        "promotion_rule":"synthetic 5/7/10/13/16-stroke controls in both orientations pass ±1 for two independent estimators and four image variants; >=10/12 real buildings show exact cross-estimator and cross-variant counts within one stroke; >=4 distinct integer counts",
        "coverage_guard":"Failure retires only a precise long-hatch-count channel. Arbitrary building semantics, word interpretations, and other visual clues remain untested.",
        "safety_guard":"No keys, mnemonic words, candidate values or wallet operations generated or evaluated.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[
        "# Stage 121 — 12-building long hatch-line count audit",
        "",
        f"- Canonical image verified: **{sha==EXPECTED_SHA}**",
        f"- Synthetic controls pass: **{controls['controls_pass']}**, cases **{controls['cases']}**",
        f"- Stable building counts: **{len(stable)}/12**",
        f"- Distinct stable counts: **{distinct}**",
        f"- Decision: **{decision}**",
        "",
        "| building | hatch orientation | original projection | original morphology | range all methods/variants | stable count |",
        "|---:|:---:|---:|---:|:---:|---:|",
    ]
    for r in real:
        orig=r["counts"]["original"]
        lines.append(
            f"| {r['building']} | {r['orientation']} | {orig['projection']} | "
            f"{orig['morphology']} | {r['count_range']} | "
            f"{r['stable_count'] if r['stable'] else '?'} |"
        )
    lines+=["","## Interpretation",""]
    if not controls["controls_pass"]:
        lines.append("Synthetic controls failed; the real-image counts are not interpretable. Correct this same stage; do not promote or retire a hypothesis.")
    elif promoted:
        lines.append("A replicated multistate count channel appears in the facades. This establishes only reproducible visible stroke counts, not alphabet/word/key semantics.")
    else:
        lines.append("The 12 facades do not supply a sufficiently complete, exact and multistate set of independent long-hatch counts under calibrated controls. Retire only this direct counting mechanism.")
    lines+=["","No keys, BIP39 phrases or wallet-address checks were conducted.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":121,"controls_pass":controls["controls_pass"],
                      "stable":len(stable),"decision":decision}))

if __name__=="__main__":
    main()
