#!/usr/bin/env python3
"""A11-EXP-143 — are mirrored, 90°-rotated skyline gaps chess-specific?

A user manually duplicated/flipped and rotated the canonical drawing, then
traced two stepped WHITE gaps in red as resembling a chess king and queen.

Newly mirrored bilateral symmetry is *by construction*: treating it as
independent source evidence would be an error. This image-only analysis
reconstructs the transformation with the canonical PNG; uses the 12 already
measured building roofs to explain two distinct stepped blank-space profiles;
and tests how commonly two generic widening, pedestal-like silhouettes arise
when the roof levels are permuted within the 7-building/5-building clusters.

A semantic 'king' requires an unmistakable cross-like finial; a 'queen'
requires a crown with multiple points. Generic stepped flared profiles do not
identify these chess-piece classes, even when conspicuously symmetric.

No words, key candidates, wallets, addresses, BIP39 or off-image research.
This tests ONLY whether the observed white shapes are independently drawn.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage143-mirrored-skyline-chess"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
W=552
H=800
CANVAS_WIDTH=2*W
SPLIT=(5,7)
TOP_IDS=(12,11,10,9,8,7,6)
BOTTOM_IDS=(5,4,3,2,1)
REQUIRED_ROOF_OBSERVATIONS=11
ROOF_Y_TOL=25
INK_THRESHOLD=175
MIN_SKYLINE_ROOF_LINE_DENSITY=.075
BASE_NECK_RATIO=1.30 # predeclared generic 'pedestal flare'; NOT a chess metric
MAX_REAR_1PX_WIDTH=.01
NULL_DISPLAY_SEED=143
NULL_DISPLAY_COUNT=6

def ordered_groups(geom):
    by={int(b["id"]):b for b in geom["buildings"]}
    if sorted(by)!=list(range(1,13)):
        raise RuntimeError("12 measured building anchors are missing")
    top=[by[i] for i in TOP_IDS]
    bottom=[by[i] for i in BOTTOM_IDS]
    assert len(top)==7 and len(bottom)==5
    return top,bottom

def source_roof_test(gray,geom):
    """Independent source-pixel ink within the registered roof-y neighborhood.

    It does NOT trace an imaginary chess contour and does not infer any
    artificial king/queen crown marker. Local roof bands must genuinely have
    detectable dark line segments, independent of mirrored rendering.
    """
    results=[]
    for building in geom["buildings"]:
        ident=int(building["id"])
        x0=int(building["x0"]);x1=int(building["x1"])
        y=int(building["roof_y"])
        xa=x0+int(round((x1-x0)*.15))
        xb=x1-int(round((x1-x0)*.15))
        ya=max(0,y-ROOF_Y_TOL);yb=min(gray.shape[0],y+ROOF_Y_TOL+1)
        patch=gray[ya:yb,xa:xb]
        if patch.size==0:raise RuntimeError("empty roof proof aperture")
        scores=(patch<INK_THRESHOLD).mean(axis=1)
        best_idx=int(np.argmax(scores))
        roof_observed=ya+best_idx
        best_score=float(scores[best_idx])
        valid=bool(best_score>=MIN_SKYLINE_ROOF_LINE_DENSITY
                   and abs(roof_observed-y)<=ROOF_Y_TOL)
        results.append({
          "building_id":ident,"registered_y":y,
          "strongest_ink_row_y":roof_observed,
          "strongest_ink_coverage":round(best_score,6),
          "adequate_roof_line":valid,
        })
    return results

def mirrored_image(gray):
    # Rotating the source 90° counterclockwise, THEN left-right flipping
    # produces the left panel of the user's rotation/mirror construction.
    # Facing an exact horizontal mirror creates the opposite panel.
    left=cv2.flip(cv2.rotate(gray,cv2.ROTATE_90_COUNTERCLOCKWISE),1)
    left=cv2.resize(left,(W,H),interpolation=cv2.INTER_AREA)
    right=np.fliplr(left)
    joined=np.hstack([left,right])
    # Because same bitmap is reflected, symmetry is an ARTIFICIAL identity.
    equality=float(np.mean(joined[:,:W]==np.fliplr(joined[:,W:])))
    return joined,equality

def fixed_skyline_mask(geom,top_roofs=None,bottom_roofs=None):
    """Create a no-pen-stroke silhouette from rooftop heights alone.

    Exact original building x spans remain in place. Roof values are
    optionally permuted inside the original two clusters for controls.
    Their 90°/mirror construction is identical to the user's technique.
    """
    top,bottom=ordered_groups(geom)
    mapping={int(b["id"]):int(b["roof_y"]) for b in geom["buildings"]}
    if top_roofs is not None:
        mapping.update({int(b["id"]):int(y) for b,y in zip(top,top_roofs)})
    if bottom_roofs is not None:
        mapping.update({int(b["id"]):int(y) for b,y in zip(bottom,bottom_roofs)})
    a=np.full((H,CANVAS_WIDTH),255,np.uint8)
    for b in geom["buildings"]:
        id_=int(b["id"])
        # Source x maps to rotated y after 90° and a factor of ~0.5.
        row0=max(0,int(np.floor((1600-int(b["x1"]))*H/1600)))
        row1=min(H,int(np.ceil((1600-int(b["x0"]))*H/1600)))
        # Source y maps inward from the pair's center seam.
        roof=int(mapping[id_])
        bottom=int(b["bottom_y"])
        inner=max(0,int(round(W*(1-roof/1105.))))
        outer=max(0,int(round(W*(1-bottom/1105.))))
        if row1>row0 and inner>outer:
            a[row0:row1,outer:inner]=45
            a[row0:row1,CANVAS_WIDTH-inner:CANVAS_WIDTH-outer]=45
    return a

def heights(group):
    return [int(b["roof_y"]) for b in group]

def flare_profile(roofline):
    # In the 90° rotated mirrored composition, source building order is
    # reversed (rightmost building maps to top of screenshot). Broadening
    # from HEAD toward BASE is proportional to last/first registered roof-y.
    ratio=float(roofline[-1]/max(1,roofline[0]))
    return {"source_head_gap_half":roofline[0],
            "source_base_gap_half":roofline[-1],
            "base_to_head_width_ratio":round(ratio,6),
            "generic_pedestal_flare":bool(ratio>=BASE_NECK_RATIO),
            "step_levels":len(set(roofline))}

def exact_generic_flare_frequency(roofline):
    # Only the first and last of a permutation matter to this deliberately
    # simple, GENUINELY generic neck/flared-base criterion. Enumerate exact
    # distinct ordered endpoint assignments, not a cherry-picked best reorder.
    count=0;total=0
    for i,a in enumerate(roofline):
        for j,b in enumerate(roofline):
            if i==j:continue
            total+=1
            if b/a>=BASE_NECK_RATIO:count+=1
    return {"qualifying_endpoint_assignments":count,
            "all_endpoint_assignments":total,
            "null_frequency":round(count/total,7)}

def synthetic_control():
    # Positive: a priori tapered stepped cartoon silhouette, with a wide base
    # and narrow head. Negative: flat-topped rectangle, no pedestal profile.
    strong=[35,150,60,180]
    flat=[100,100,100,100]
    ps=flare_profile(strong)
    ns=flare_profile(flat)
    return {
        "pass":bool(ps["generic_pedestal_flare"]
                    and ps["step_levels"]>=3
                    and not ns["generic_pedestal_flare"]
                    and ns["step_levels"]==1),
        "stepped_positive":ps,
        "uniform_rectangle_negative":ns
    }

def save_contacts(img,geometry,top_roof,bottom_roof):
    # Actual canonical picture mirrored; the red tracing from user screenshot
    # is not introduced into source and no user annotations are interpreted
    # as a genuine preexisting mark.
    screenshot,_=mirrored_image(img)
    Image.fromarray(screenshot).save(OUT/"canonical-rotated-mirror-pair.png")

    ideal=fixed_skyline_mask(geometry)
    Image.fromarray(ideal).save(OUT/"geometry-only-stepped-voids.png")

    rng=np.random.default_rng(NULL_DISPLAY_SEED)
    thumb_w=300;thumb_h=218
    sheet=Image.new("RGB",(thumb_w*4,thumb_h*2),"white")
    draw=ImageDraw.Draw(sheet)
    variants_show=[("original roof order",None,None)]
    for i in range(NULL_DISPLAY_COUNT):
        a=rng.permutation(top_roof).tolist()
        b=rng.permutation(bottom_roof).tolist()
        variants_show.append((f"shuffled skylines {i+1}",a,b))
    for i,(name,a,b) in enumerate(variants_show):
        mask=fixed_skyline_mask(geometry,top_roofs=a,bottom_roofs=b)
        tile=Image.fromarray(mask).convert("RGB").resize((thumb_w-12,thumb_h-26))
        x=(i%4)*thumb_w+6;y=(i//4)*thumb_h+6
        sheet.paste(tile,(x,y+22))
        draw.text((x,y+3),name,fill=(0,0,0))
    sheet.save(OUT/"six-randomized-skyline-mirror-controls.png")

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Canonical image SHA mismatch")
    image=np.asarray(Image.open(SOURCE).convert("L"))
    if image.shape!=(1105,1600):raise RuntimeError("Unexpected dimensions")
    geometry=json.loads(GEOM.read_text())
    fixture=synthetic_control()
    groups=ordered_groups(geometry)
    top_roof=heights(groups[0]); bottom_roof=heights(groups[1])
    rendered={}
    for mode,variant in variants(image).items():
        if mode not in FORMATS:continue
        test=source_roof_test(variant,geometry)
        m,sym=mirrored_image(variant)
        rendered[mode]={
            "roofline_confirmation":sum(x["adequate_roof_line"] for x in test),
            "observed_roof_lines":test,
            "forced_mirror_pixel_equality":sym,
        }
    source_ok=all(r["roofline_confirmation"]>=REQUIRED_ROOF_OBSERVATIONS
                  for r in rendered.values())
    sym_ok=all(abs(r["forced_mirror_pixel_equality"]-1.)<=1e-12
               for r in rendered.values())
    top=flare_profile(top_roof)
    bottom=flare_profile(bottom_roof)
    ptop=exact_generic_flare_frequency(top_roof)
    pbot=exact_generic_flare_frequency(bottom_roof)
    joint=ptop["null_frequency"]*pbot["null_frequency"]

    # The observed pair has symmetric pedestal-like steps by CONSTRUCTION.
    # This is not a classifier for KING or QUEEN. Crown/cross features remain
    # visually ambiguous and must not be inferred from traced red outlines.
    decision=("CONTROL_FAILURE" if not fixture["pass"] or not sym_ok else
              "INSUFFICIENT_SKYLINE_ROOF_CONFIRMATION" if not source_ok else
              "MIRROR_GENERATES_GENERIC_PIECE_LIKE_NEGATIVE_SPACE")
    result={
        "experiment_id":"A11-EXP-143",
        "hypothesis":"the two apparent king/queen white shapes in a 90-degree rotated/mirrored pair are induced by stepped two-cluster skyline roofs and reflection, rather than independently drawn chess symbols",
        "evidence":"User rotated/duplicated the image and traced central white spaces in red. Original canonical scene contains five buildings at left (IDs 1-5), seven at right (6-12) separated by open x~782..884. Mirror symmetry is artificially constructed.",
        "scope":"fixed geometry.json building boxes, two reversed skyline groups, 90° plus horizontal mirror, original/JPEG85/JPEG70/downsample; no OCR, no key material",
        "canonical_sha256":digest,
        "mirror_transformation":"left = horizontal_flip(rotate_original_90_degrees_CCW); right = horizontal_flip(left), then concatenate",
        "registered_top_cluster_ids":list(TOP_IDS),
        "registered_bottom_cluster_ids":list(BOTTOM_IDS),
        "top_roof_heights_pixels":top_roof,
        "bottom_roof_heights_pixels":bottom_roof,
        "binary_king_queen_specificity":"NOT ESTABLISHED: visual resemblance in manually outlined whitespace is not evidence of a unique cross finial or multi-pointed crown. Do not assign identities as confirmed labels.",
        "control":fixture,
        "source_variants":rendered,
        "source_validated":source_ok,
        "symmetry_constructed_not_in_source":sym_ok,
        "two_generic_profiles":{"top_seven_buildings":top,
                                "bottom_five_buildings":bottom},
        "null_test":{
            "method":"exact permutation endpoint ratios within each of the two original building clusters; fixed threshold base_width/head_width >=1.30, NOT chess-specific",
            "top_cluster":ptop,"bottom_cluster":pbot,
            "both_generic_pedestals_frequency":round(joint,7),
            "posthoc_caveat":"This generic pedestal criterion was selected after seeing the montage; frequency is illustrative, not an author-intent p-value, and multiple image manipulations were tried."
        },
        "decision":decision,
        "scope_limit":"Any rectangular city skyline mirrored in this way is axis-symmetric and stair-stepped. A distinctive king/queen identification needs independent crown/cross features visible in the unmanipulated source and an adversarial human-blind comparison; neither is established here.",
        "safety":"No generated, derived or verified BIP39 words/private keys, account/wallet operations, search outside the image or secret candidates."
    }
    save_contacts(image,geometry,top_roof,bottom_roof)
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    report=[
      "# Stage143 — are the white king/queen shapes mirror-made skylines?",
      "",
      f"- Canonical source verified: **{digest==SHA}**",
      f"- Synthetic stepped-profile vs flat-profile controls: **{fixture['pass']}**",
      f"- Forced left/right symmetry in 4 image formats: **{sym_ok}**",
      f"- Original roofline source pixels confirmed: **{min(r['roofline_confirmation'] for r in rendered.values())}/12** (minimum across four formats)",
      f"- Upper white void skyline group: **7 buildings** (IDs 12–6)",
      f"- Lower white void skyline group: **5 buildings** (IDs 5–1)",
      f"- Upper gap base/head widening: **{top['base_to_head_width_ratio']:.2f}×**",
      f"- Lower gap base/head widening: **{bottom['base_to_head_width_ratio']:.2f}×**",
      f"- Generic widening pedestal pair among exact roof-endpoint permutations: **{joint:.1%}** (descriptive post-hoc, not a true chess-significance p-value)",
      f"- Decision: **{decision}**",
      "",
      "## Interpretation",
      "",
      "The user-created mirror supplies **bilateral symmetry automatically**. The two separated skyline building groups supply two naturally stepped negative-space silhouettes, which may resemble chess pieces, vases or trophies. No independently drawn, unambiguous king cross or queen's multi-pointed crown has been established in the original picture.",
      "",
      "A fair next test, if a distinctive crown/cross appears under another manipulation, should be preregistered against unrelated reflected skylines and examined blind. Do not treat the hand-traced contour or repeated trials as independent evidence.",
      "",
      "Artifacts: canonical-rotated-mirror-pair.png, geometry-only-stepped-voids.png, six-randomized-skyline-mirror-controls.png.",
      "No wallet or private-key material.",""
    ]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":143,"source":source_ok,
        "mirror_by_construction":sym_ok,"controls":fixture["pass"],
        "generic_flare_null_rate":round(joint,7),
        "decision":decision}))

if __name__=="__main__":
    main()
