#!/usr/bin/env python3
"""A11-EXP-134 — provenance-corrected Stage 36 visual-reveal control audit.

Stage132 proved the legacy large-sail source box excluded about two thirds of
the actual drawn triangle. Stage133 verified that Stage94 structural counts
changed from 10–14 to 76–90 when measuring the full triangle.

This stage reuses *exactly* Stage36's fixed 19 visual transforms and generic
component-alignment metric, but applies them to the prior Stage132 triangle,
with three new same-sized, same-shape reference regions and 4 image variants.
It uses no OCR, guessed text, secret data, keys, mnemonics or wallets.

A detection is only a request for HUMAN visual review of the contact sheet,
never a decoded symbol or evidence that a private key was recovered.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from stage112_corrected_sail_width_progression import variants
from stage36_large_boat_visual_reveal import (
    transform_family, glyph_line_metrics
)
from stage132_large_sail_legacy_bbox_audit import POLYGONS

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage134-corrected-large-sail-visual-reveal"
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
POINTS=tuple(tuple(map(int,x)) for x in POLYGONS["large_sail"])

# Exactly one target and three equal-size, equal-shape controls. Source
# locations are fixed before scoring, not selected by similarity tests.
PADDING=4
MIN_INK_FRAC=.12
SCORE_MARGIN=.15
REQUIRED_REPLICATED=3
REQUIRED_FAMILIES=2

def geometry():
    vertices=np.asarray(POINTS,dtype=np.int32)
    x0,y0=vertices.min(axis=0)-PADDING
    x1,y1=vertices.max(axis=0)+PADDING+1
    w,h=int(x1-x0),int(y1-y0)
    inside=np.zeros((h,w),np.uint8)
    cv2.fillPoly(inside,[vertices-np.array([x0,y0],np.int32)],1)
    # Keep same aperture across all controls: removes support-size bias.
    return (int(x0),int(y0),w,h), inside.astype(bool)

def references(box):
    x0,y0,w,h=box
    return {
        "large_sail":(x0,y0),
        "right_skyline":(900,0),
        "pier_boats":(935,345),
        "open_water":(680,680),
    }

def cut_regions(gray,box,aperture):
    _,_,w,h=box
    out={}
    for name,(x,y) in references(box).items():
        piece=gray[y:y+h,x:x+w]
        if piece.shape!=(h,w):
            raise ValueError("Region outside canonical canvas: "+name)
        clean=piece.copy()
        clean[~aperture]=255
        out[name]=clean
    return out

def family(transform):
    if transform.startswith("thr_"): return "threshold"
    if transform.startswith("band_"): return "intensity_band"
    if transform.startswith("dog_"): return "difference_of_gaussians"
    if transform.startswith("line_"): return "line_suppression"
    if transform.startswith("clahe_"): return "clahe"
    return "other"

def compare(crops):
    transformed={name:transform_family(a) for name,a in crops.items()}
    names=sorted(next(iter(transformed.values())).keys())
    if len(names)!=19:
        raise RuntimeError("Stage36 transform set was unexpectedly changed")
    rows={}
    for transform in names:
        allmetrics={
            region:glyph_line_metrics(transformed[region][transform])
            for region in crops
        }
        target=allmetrics["large_sail"]
        competitors=[m["alignment_score"] for name,m in allmetrics.items()
                     if name!="large_sail"]
        gap=target["alignment_score"]-max(competitors)
        accepted=(gap>=SCORE_MARGIN
                  and target["max_aligned_count"]>=3
                  and target["aligned_x_coverage"]>=.15)
        rows[transform]={
            "family":family(transform),
            "target_score":round(float(target["alignment_score"]),6),
            "target_aligned":int(target["max_aligned_count"]),
            "target_coverage":round(float(target["aligned_x_coverage"]),6),
            "control_max":round(float(max(competitors)),6),
            "target_minus_control":round(float(gap),6),
            "target_rank":1+sum(v>target["alignment_score"]+1e-12
                                for v in competitors),
            "qualified":bool(accepted)
        }
    return rows

def summary(result_by_format):
    names=sorted(result_by_format["original"])
    replicated=[]
    for key in names:
        if all(result_by_format[v][key]["qualified"] for v in FORMATS):
            replicated.append(key)
    fams=sorted({family(t) for t in replicated})
    return {
        "transforms":len(names),
        "qualified_original":sum(x["qualified"] for x in result_by_format["original"].values()),
        "qualified_by_format":{
            v:sum(x["qualified"] for x in result_by_format[v].values())
            for v in FORMATS
        },
        "replicated_transform_count":len(replicated),
        "replicated_transforms":replicated,
        "replicated_families":fams,
        "promotion_rule_pass":len(replicated)>=REQUIRED_REPLICATED
                              and len(fams)>=REQUIRED_FAMILIES,
    }

def synth_scene(box,mask,text_is_target):
    _,_,w,h=box
    backdrop=np.full((h,w),255,np.uint8)
    regions={name:backdrop.copy() for name in references(box)}
    rng=np.random.default_rng(134)
    for name in regions:
        if (name=="large_sail")==text_is_target:
            # Four known, visible synthetic shapes ONLY for calibrating the
            # generic glyph-alignment detector; never output guessed glyphs.
            cv2.putText(regions[name],"ABCD",(130,177),
                        cv2.FONT_HERSHEY_SIMPLEX,.82,0,2,cv2.LINE_AA)
        else:
            # Diffuse non-letter pencil lines, not aligned as a word.
            for k in range(14):
                xx=int(rng.integers(58,w-58))
                yy=int(rng.integers(65,h-65))
                dy=int(rng.integers(-17,18))
                dx=int(rng.integers(-24,25))
                cv2.line(regions[name],(xx,yy),(xx+dx,yy+dy),
                         0,1,cv2.LINE_AA)
        regions[name][~mask]=255
    return regions

def fixture_variants(regions):
    group={}
    for v in FORMATS:
        patches={}
        for key,im in regions.items():
            patches[key]=variants(im)[v]
        group[v]=compare(patches)
    return summary(group)

def calibrate(box,mask):
    positive=fixture_variants(synth_scene(box,mask,True))
    negative=fixture_variants(synth_scene(box,mask,False))
    passed=bool(positive["promotion_rule_pass"]
                and not negative["promotion_rule_pass"])
    return {"pass":passed,"positive":positive,"negative":negative}

def source_ink(gray,box,mask):
    (x0,y0,w,h)=box
    roi=gray[y0:y0+h,x0:x0+w]
    ink_frac=float(np.mean(roi[mask]<170))
    return {"fraction":round(ink_frac,6),"pass":ink_frac>=MIN_INK_FRAC}

def save_visual_contact(original_crops,scored):
    # Contact sheets are for human source-image review only; never OCR the
    # rendered products and never make a key candidate from any features.
    names=sorted(scored["original"],key=lambda k:
                 scored["original"][k]["target_minus_control"],reverse=True)[:9]
    tw,th=275,232
    contact=Image.new("RGB",(tw*3,th*3),"white")
    draw=ImageDraw.Draw(contact)
    masks=transform_family(original_crops["large_sail"])
    for i,name in enumerate(names):
        visual=Image.fromarray(255-masks[name]).convert("RGB")
        visual.thumbnail((tw-12,th-38))
        x=(i%3)*tw+6;y=(i//3)*th+6
        contact.paste(visual,(x,y))
        record=scored["original"][name]
        draw.text((x,y+th-34),name+" Δ="+f"{record['target_minus_control']:+.2f}",
                  fill=(0,0,0))
    contact.save(OUT/"corrected-sail-transforms-contact.png")

    sheet=Image.new("RGB",(310*4,300),"white")
    d=ImageDraw.Draw(sheet)
    for i,(name,img) in enumerate(original_crops.items()):
        view=Image.fromarray(img).convert("RGB")
        view.thumbnail((296,270))
        x=i*310+7
        sheet.paste(view,(x,23))
        d.text((x,5),name,fill=(0,0,0))
    sheet.save(OUT/"four-source-region-contact.png")

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=EXPECTED_SHA:
        raise SystemExit("Canonical image SHA256 mismatch")
    gray=np.array(Image.open(PNG).convert("L"))
    if gray.shape!=(1105,1600):
        raise SystemExit("Canonical dimensions differ")
    box,mask=geometry()
    source=source_ink(gray,box,mask)
    calibration=calibrate(box,mask)
    vv=variants(gray)
    all_regions={}
    scores={}
    for v in FORMATS:
        crops=cut_regions(vv[v],box,mask)
        all_regions[v]=crops
        scores[v]=compare(crops)
    review=summary(scores)
    final=(
        "CONTROL_FAILURE" if not calibration["pass"] else
        "INSUFFICIENT_CORRECTED_SAIL_INK" if not source["pass"] else
        "FULL_SAIL_VISUAL_REVEAL_REQUIRES_MANUAL_REVIEW"
        if review["promotion_rule_pass"] else
        "NO_REPLICATED_CORRECTED_SAIL_GLYPH_ALIGNMENT"
    )
    result={
        "experiment_id":"A11-EXP-134",
        "date":"2026-10-13",
        "hypothesis":"Stage36's old partial-sail visual-text-like alignment ranking must be rechecked on the Stage132/133 verified complete drawn sail",
        "cause":"Stage132 found legacy ROI omitted 66.7% of sail ink; Stage133 count changed 10-14 to 76-90. No new image decoding hypothesis asserted.",
        "scope":"Stage36's original 19 transform and glyph-line component metrics, with the corrected Stage132 whole-sail polygon, same-sized same-masked three scene controls, original/JPEG85/JPEG70/resampling",
        "sha256":digest,
        "corrected_box":box,
        "source_positions":references(box),
        "stage132_polygon":list(map(list,POINTS)),
        "thresholds":{"min_score_margin":SCORE_MARGIN,
                      "min_aligned_components":3,"min_aligned_x_coverage":.15,
                      "required_replicated_transforms":REQUIRED_REPLICATED,
                      "required_distinct_transform_families":REQUIRED_FAMILIES},
        "source_control":source,
        "synthetic_text_vs_random_control":calibration,
        "by_variant":scores,
        "outcome":review,
        "decision":final,
        "scope_guard":"A positive is a generic connected-component arrangement that warrants MANUAL image inspection, not demonstrated readable glyphs, word, private key or intent; a negative affects only this registered 19-transform family.",
        "security_guard":"No OCR, guesses, private-key candidates, BIP39, Ethereum verification or off-image research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    save_visual_contact(all_regions["original"],scores)
    rows=[
       "# Stage 134 — Stage36 visual reveal re-audit on the complete sail",
       "",
       f"- Source SHA verified: **{digest==EXPECTED_SHA}**",
       f"- Corrected sail support valid: **{source['pass']}** (ink {source['fraction']:.3f})",
       f"- Synthetic text-vs-scribbles controls: **{calibration['pass']}**",
       f"- Original transform candidates: **{review['qualified_original']}/19**",
       f"- Fully replicated transform candidates: **{review['replicated_transform_count']}/19**",
       f"- Replicated independent transform families: **{len(review['replicated_families'])}**",
       f"- Decision: **{final}**",
       "",
       "## Interpretation"
    ]
    if not calibration["pass"]:
        rows.append("Synthetic controls failed: repair Stage134; no inference from the real scene.")
    elif not source["pass"]:
        rows.append("The fixed full-sail region has inadequate visible ink for this metric.")
    elif review["promotion_rule_pass"]:
        rows.append("Inspect saved contact sheet. Component alignment alone cannot demonstrate any text or secret.")
    else:
        rows.append("No calibrated, replicated line-of-glyph-components under the specific Stage36 transform family with corrected ROI and same-mask scene controls. Does not exclude other visible clue mechanisms.")
    rows+=["","Artifacts: corrected-sail-transforms-contact.png, four-source-region-contact.png",
           "No private-key, mnemonic or wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(rows))
    print(json.dumps({"experiment_id":"A11-EXP-134","controls_pass":calibration["pass"],
                     "source":source["pass"],
                     "replicated":review["replicated_transform_count"],
                     "decision":final}))

if __name__=="__main__":
    main()
