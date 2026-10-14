#!/usr/bin/env python3
"""A11-EXP-151 — test a visible hollow triangular area BELOW the right-hand pier.

The canonical drawing shows a sparsely inked triangular structure beneath
the right-hand pier, around x1050–1280/y630–780. Unlike the five true small
sails x1007–1537/y357–546, this under-pier region has no obvious densely
hatched sail panel. One newly grounded semantic question: could it be a SIXTH
small sail, or is it an unfilled support/rigging triangle?

Compare 5 fixed true-sail source polygons versus 1 *fixed candidate* triangle
using the same affine-normalized, interior-only ink density and high-frequency
pen-hatching metrics. The candidate/source vertices are held constant; no
optimizing crop, orientation, thresholds or OCR against source outcomes.

Two completely different synthetic controls, known densely hatched triangle
and just an outlined empty triangle, calibrated at ALL SIX native object
positions and all four lossiness variants. A real positive only promotes the
candidate for independent human inspection; no cipher/key interpretation.

No private key, BIP39, mnemonic, wallet, ETH address or off-image operation.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw

from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage151-under-pier-triangle"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
WIDTH=HEIGHT=128
CANON=np.float32([(64,0),(0,127),(127,127)])
# One manual, a priori under-pier candidate, five independent known sails:
OBJECTS={
 "small_sail_1":[(1042,448),(1007,546),(1077,546)],
 "small_sail_2":[(1148,433),(1110,532),(1186,532)],
 "small_sail_3":[(1282,411),(1238,514),(1326,514)],
 "small_sail_4":[(1372,397),(1330,498),(1414,498)],
 "small_sail_5":[(1490,357),(1443,463),(1537,463)],
 "under_pier_triangle":[(1052,633),(1052,778),(1280,714)]
}
KNOWN=tuple(k for k in OBJECTS if k.startswith("small_sail_"))
TARGET="under_pier_triangle"
MIN_REAL_KNOWN_SAILS=4
MIN_INNER_PIXELS=2100
INK_PIXEL_CUTOFF=175
MIN_HATCH_DENSITY=.18
MIN_DETAIL_RESIDUAL=.030
NO_HATCH_MIN_MARGIN=.0

def inner_mask():
    yy,xx=np.indices((HEIGHT,WIDTH))
    t=yy/(HEIGHT-1)
    xl=64*(1-t)
    xr=64+63*t
    return ((yy>=26)&(yy<=108)&
            (xx>=xl+9)&(xx<=xr-9)&(abs(xx-64)>=7))
INNER=inner_mask()
if np.count_nonzero(INNER)<MIN_INNER_PIXELS:
    raise RuntimeError("Interior sail mask too small")

def canonicalize(gray,points):
    p=np.float32(points)
    mapping=cv2.getAffineTransform(p,CANON)
    return cv2.warpAffine(gray,mapping,(WIDTH,HEIGHT),
        flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)

def metrics(gray,points):
    patch=canonicalize(gray,points)
    pixels=patch[INNER]
    density=float(np.mean(pixels<INK_PIXEL_CUTOFF))
    blur=cv2.GaussianBlur(patch,(0,0),2.1)
    hp=np.abs(patch.astype(np.float32)-blur.astype(np.float32))/255
    detail=float(np.mean(hp[INNER]))
    candidate=bool(density>=MIN_HATCH_DENSITY
                   and detail>=MIN_DETAIL_RESIDUAL)
    return {
        "inner_source_pixels":int(pixels.size),
        "dark_stroke_coverage":round(density,6),
        "high_frequency_pencil_detail":round(detail,6),
        "looks_like_dense_ink_sail_panel":candidate
    }

def template(hatched):
    gray=np.full((HEIGHT,WIDTH),255,np.uint8)
    pts=np.asarray(CANON,np.int32)
    cv2.polylines(gray,[pts],True,0,2,cv2.LINE_AA)
    cv2.line(gray,(64,1),(64,125),0,1,cv2.LINE_AA)
    if hatched:
        rng=np.random.default_rng(151)
        strokes=np.full_like(gray,255)
        for _ in range(145):
            y=int(rng.integers(23,113))
            t=y/127.
            left=max(6,int(64-60*t)+4)
            right=min(121,int(64+60*t)-4)
            if left>=right:continue
            x=int(rng.integers(left,right+1))
            dx=int(rng.integers(-15,16))
            dy=int(rng.integers(6,22))
            cv2.line(strokes,(x,y),
                     (int(np.clip(x+dx,0,127)),int(np.clip(y+dy,0,127))),
                     0,int(rng.integers(1,3)),cv2.LINE_AA)
        # Never insert marks outside the synthetic sail's own triangle:
        support=np.zeros_like(gray,np.uint8)
        cv2.fillConvexPoly(support,pts,1)
        gray[support>0]=np.minimum(gray[support>0],strokes[support>0])
    return gray

def synthetic_scene(hatched):
    a=np.full((1105,1600),255,np.uint8)
    t=template(hatched)
    for points in OBJECTS.values():
        m=cv2.getAffineTransform(CANON,np.float32(points))
        warped=cv2.warpAffine(t,m,(1600,1105),
          flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
        np.minimum(a,warped,out=a)
    return a

def controls():
    checks={}
    passed=0;total=0
    for setting,hatched in (("hatched_sail",True),
                            ("hollow_outline",False)):
        readings={}
        for fmt,img in variants(synthetic_scene(hatched)).items():
            if fmt not in FORMATS:continue
            for name,verts in OBJECTS.items():
                obs=metrics(img,verts)
                ok=obs["looks_like_dense_ink_sail_panel"]==hatched
                total+=1;passed+=int(ok)
                readings[f"{fmt}:{name}"]={"pass":ok,
                     "dark":obs["dark_stroke_coverage"],
                     "detail":obs["high_frequency_pencil_detail"]}
        checks[setting]=readings
    return {"pass":passed==total and total==48,
            "passed_cases":passed,"cases":total,"details":checks}

def contact(original,results):
    # Source rectangles and six normalized shapes; outlines are audit-only,
    # not edited source used by classification.
    cols=3;tw=245;th=222
    sheet=Image.new("RGB",(tw*3,th*2),"white")
    draw=ImageDraw.Draw(sheet)
    for idx,(name,pts) in enumerate(OBJECTS.items()):
        rect=canonicalize(original,pts)
        art=Image.fromarray(rect).convert("RGB").resize((198,180))
        x=idx%cols*tw+12;y=idx//cols*th+6
        sheet.paste(art,(x,y+28))
        measure=results["original"][name]
        draw.text((x,y+6),f"{name}: ink {measure['dark_stroke_coverage']:.2f}",fill=(0,0,0))
    sheet.save(OUT/"five-sails-vs-under-pier-triangle.png")

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Canonical source image mismatch")
    original=np.asarray(Image.open(PNG).convert("L"))
    if original.shape!=(1105,1600):raise RuntimeError("Unexpected image shape")
    ctl=controls()
    all_results={fmt:{name:metrics(img,pts) for name,pts in OBJECTS.items()}
                 for fmt,img in variants(original).items() if fmt in FORMATS}
    known={k:all(all_results[v][k]["looks_like_dense_ink_sail_panel"]
                 for v in FORMATS) for k in KNOWN}
    known_count=sum(known.values())
    candidate=all(all_results[v][TARGET]["looks_like_dense_ink_sail_panel"]
                  for v in FORMATS)
    decision=("CONTROL_FAILURE" if not ctl["pass"] else
              "INSUFFICIENT_POSITIVE_SAIL_SOURCE_RECOVERY"
              if known_count<MIN_REAL_KNOWN_SAILS else
              "UNDER_PIER_HATCHED_TRIANGLE_REQUIRES_MANUAL_REVIEW"
              if candidate else "NO_HATCHED_SIXTH_SAIL_UNDER_PIER")
    payload={
        "experiment_id":"A11-EXP-151",
        "hypothesis":"a visually apparent triangular structure BELOW the right pier might be an additional filled sail instead of an unhatched dock support/rigging opening",
        "scope":"one candidate under-pier triangular aperture x1052..1280/y633..778 vs five previously registered true small sails; affine-normalized fixed interior panel density and highpass pencil energy, 4 source/lossy formats",
        "original_sha256":digest,
        "source_vertices_precommitted":OBJECTS,
        "gates":{"min_dense_dark_source_fraction":MIN_HATCH_DENSITY,
                 "min_source_highpass_residual":MIN_DETAIL_RESIDUAL,
                 "min_real_positive_sails":MIN_REAL_KNOWN_SAILS,
                 "min_normalized_interior_pixels":MIN_INNER_PIXELS},
        "controls":ctl,
        "positive_five_real_sail_recovery":known,
        "positive_real_sails_stable":known_count,
        "under_pier_target_dense_sail_in_four_formats":candidate,
        "observations":all_results,
        "decision":decision,
        "limits":"This source candidate polygon was selected visually and may include mooring cables/dock cross-braces. Only dense ink-panel sail texture is tested; this does not distinguish all semantic or unfilled sails, exact triangle outline or hidden code. No p-value or author-intent inference.",
        "safety_guard":"No private keys, mnemonics, BIP39, wallet addresses, checking, derivation or off-image reference."
    }
    (OUT/"result.json").write_text(json.dumps(payload,indent=2)+"\n")
    contact(original,all_results)
    report=[
       "# Stage151 — is the underside-pier triangle another filled sail?","",
       f"- Canonical SHA verified: **{digest==SHA}**",
       f"- Filled-vs-hollow synthetic known-site controls: **{ctl['passed_cases']}/{ctl['cases']}**",
       f"- Five known genuine sail textures recovered: **{known_count}/5**",
       f"- Under-pier candidate dense-sail signature in 4 formats: **{candidate}**",
       f"- Decision: **{decision}**","",
       "| region | original ink | original pencil detail |",
       "|---|---:|---:|"
    ]
    for name in OBJECTS:
        z=all_results["original"][name]
        report.append(f"| {name} | {z['dark_stroke_coverage']:.3f} | {z['high_frequency_pencil_detail']:.3f} |")
    report+=["","## Interpretation",""]
    if not ctl["pass"]:
        report.append("Controls failed; repair Stage151 before interpreting image.")
    elif known_count<MIN_REAL_KNOWN_SAILS:
        report.append("Too few known genuine sails met the precommitted source hatch test. Inconclusive.")
    elif candidate:
        report.append("The under-pier candidate shares a dense pencil texture with known sail interiors. This warrants manual image interpretation; it does NOT identify an actual extra boat or code.")
    else:
        report.append("The under-pier triangle does not resemble a densely hatch-filled sail interior in this fixed comparison. It may be an open dock-support/rigging shape; this does not eliminate alternative artistic interpretations.")
    report+=["","Contact: five-sails-vs-under-pier-triangle.png. No secret material.",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":151,"controls":ctl["pass"],"known":known_count,
        "candidate":candidate,"decision":decision}))

if __name__=="__main__":
    main()
