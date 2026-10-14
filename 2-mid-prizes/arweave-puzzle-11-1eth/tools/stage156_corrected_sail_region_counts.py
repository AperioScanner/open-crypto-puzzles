#!/usr/bin/env python3
"""Stage156: narrowly repair the *small-sails region* coverage of old Stage15.

Test original component-size bins and fixed five thresholds on the already
registered real five sail polygons, with fully witnessed 321/123 controls.
This does not revive Stage22's retired hex321 intent claim. No keys/wallets.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import cv2
import numpy as np
from stage112_corrected_sail_width_progression import variants
from stage153_under_pier_triangle_junctions import TRIANGLES
from stage15_semantic_321_counts import THRESHOLDS, TARGETS, band_counts

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR=ROOT/"analysis"/"runs"/"stage15-semantic-321-counts"/"result.json"
STAGE155=ROOT/"analysis"/"runs"/"stage155-small-sail-band-audit"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage156-corrected-sail-counts"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
SITES={name:verts for name,verts in TRIANGLES.items() if name.startswith("sail")}

def mask_union(shape):
    result=np.zeros(shape,np.uint8)
    individual={}
    for name,poly in SITES.items():
        a=np.zeros(shape,np.uint8)
        cv2.fillPoly(a,[np.array(poly,np.int32)],255)
        a=cv2.erode(a,np.ones((5,5),np.uint8),iterations=1)
        individual[name]=a>0
        result=np.maximum(result,a)
    return result>0,individual

def masked(gray,mask):
    c=gray.copy()
    c[~mask]=255
    return c

def make_fixture(kind,union,individual):
    a=np.full(union.shape,255,np.uint8)
    if kind in ("321","123"):
        if kind=="321":
            for x,y in ((1042,485),(1028,525),(1056,525)):
                cv2.circle(a,(x,y),4,0,-1)
            for x,y in ((1148,495),(1282,480)):
                cv2.ellipse(a,(x,y),(11,11),0,0,360,0,-1)
            a[individual["sail5"]]=0
        else:
            for name in ("sail1","sail4","sail5"):
                a[individual[name]]=0
            cv2.circle(a,(1148,459),4,0,-1)
            for x,y in ((1148,497),(1282,480)):
                cv2.ellipse(a,(x,y),(11,11),0,0,360,0,-1)
    elif kind=="negative_five_large":
        a[union]=0
    else:raise ValueError(kind)
    return masked(a,union)

def controls(union,individual):
    results=[]; passed=0
    for kind in ("321","123","negative_five_large"):
        frames=variants(make_fixture(kind,union,individual))
        for fmt in FORMATS:
            for t in THRESHOLDS:
                measured=tuple(band_counts(masked(frames[fmt],union),t))
                expected={"321":(3,2,1),"123":(1,2,3)}.get(kind)
                ok=(measured==expected if expected else measured not in TARGETS)
                passed+=int(ok)
                results.append({"kind":kind,"variant":fmt,"threshold":t,
                    "measured":list(measured),"passed":bool(ok)})
    return {"passed":passed,"cases":len(results),"pass":passed==len(results)==60,
            "failures":[x for x in results if not x["passed"]]}

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Original SHA mismatch")
    prior=json.loads(PRIOR.read_text())
    prior155=json.loads(STAGE155.read_text())
    if prior155["decision"]!="LEGACY_SMALL_SAIL_BAND_MATERIALLY_TRUNCATES_TRUE_SAILS":
        raise RuntimeError("Stage155 calibration decision not available")
    gray=cv2.imread(str(PNG),cv2.IMREAD_UNCHANGED)
    gray=gray[:,:,0] if gray.ndim==3 else gray
    if gray.shape!=(1105,1600):raise RuntimeError("image dimensions")
    if tuple(THRESHOLDS)!=(80,110,140,170,200):
        raise RuntimeError("historical threshold list differs")
    old=[tuple(band_counts(gray[360:480,:],t)) for t in THRESHOLDS]
    old_record=next(r for r in prior["regions"] if r["region"]=="small_sails_full_band")
    expected=[tuple(c["small_mid_large"]) for c in old_record["counts_by_threshold"]]
    replay=sum(a==b for a,b in zip(old,expected))
    union,indiv=mask_union(gray.shape)
    controls_out=controls(union,indiv)
    by_variant={}
    for name,frame in variants(gray).items():
        if name in FORMATS:
            m=masked(frame,union)
            series=[list(band_counts(m,t)) for t in THRESHOLDS]
            exact={tag:sum(tuple(z)==tpl for z in series)
                   for tpl,tag in TARGETS.items()}
            by_variant[name]={"source_counts":dict(zip(map(str,THRESHOLDS),series)),
                "exact_threshold_matches":exact,
                "promoted_any":bool(max(exact.values())>=4)}
    stable=all(z["promoted_any"] for z in by_variant.values())
    decision=("CONTROL_FAILURE" if not controls_out["pass"]
        else "HISTORICAL_REPLAY_FAILURE" if replay!=5
        else "CORRECTED_SAIL_COUNT_SIGNATURE_REQUIRES_SOURCE_REVIEW" if stable
        else "NO_STABLE_FULL_SAIL_COUNT_CORROBORATION")
    result={"experiment_id":"A11-EXP-156","sha256":digest,
        "source_provenance":"Stage155 confirmed obsolete band; corrected masks from Stage153 five true polygons",
        "legacy_stage15_replay_passed":replay,"legacy_stage15_replay_total":5,
        "legacy_stage15_old_counts":[list(z) for z in old],
        "original_stage15_promoted_count":len(prior["promoted"]),
        "synthetic_controls":controls_out,
        "original_bands":{"thresholds":THRESHOLDS,
                          "small":[3,200],"medium":[201,2000],"large":[2001,None]},
        "fixed_masks":{"sites":SITES,"erode_px":5,"total_area":int(union.sum())},
        "by_variant":by_variant,"all_formats_source_promoted":stable,
        "decision":decision,
        "interpretation_limit":"Single corrected subset re-test after a known source defect. A numeric count match could be accidental; it would not establish an intentional code, and old Stage15 other regions remain unchanged.",
        "safety":"Non-cryptographic only; no private key, mnemonic, candidate, wallet, or address computation."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage156 — Stage15 historical small-sails ROI repair","",
      f"- Canonical image hash verified: **{digest==SHA}**",
      f"- Exact historical 5/5 count replay: **{replay}/5**",
      f"- Synthetic controlled 321/123/negative counts: **{controls_out['passed']}/{controls_out['cases']}**",
      f"- Corrected five true sail polygons area: **{int(union.sum())} px**",
      f"- Stable 321 or 123 across all original+lossy variants: **{stable}**",
      f"- Decision: **{decision}**","",
      "| Threshold | old y=360..480 (all x) | corrected five true sails (original) |",
      "|---:|---|---|"]
    for t,old_counts in zip(THRESHOLDS,old):
        lines.append(f"| {t} | {list(old_counts)} | {by_variant['original']['source_counts'][str(t)]} |")
    lines+=["","No other Stage15 region re-tested; the old whole-skyline hexadecimal 321 interpretation was already downgraded. All source polygons, thresholds and controls fixed before this stage.","",
      "This does not decode a secret or imply wallet access.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":156,"controls":f"{controls_out['passed']}/{controls_out['cases']}",
      "old_replay":replay,"stable":stable,"decision":decision}))
if __name__=="__main__":main()
