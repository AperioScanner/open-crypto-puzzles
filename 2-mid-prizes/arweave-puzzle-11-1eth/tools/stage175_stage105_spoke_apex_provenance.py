#!/usr/bin/env python3
"""A11-EXP-175: source-metadata audit of old Stage105 false apex anchors.

Stage105's own synthetic count fixtures failed. This audit reads archived
results, immutable Stage153 real sail apex coordinates, and confirmed
Stage164 crop-coverage report. SHA-checks canonical original PNG but DOES
NOT analyze the original image pixels or derive any hidden numeric codes.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
OLD=ROOT/"analysis"/"runs"/"stage105-small-sail-spoke-count"/"result.json"
NEW164=ROOT/"analysis"/"runs"/"stage164-stage112-sail-coverage"/"result.json"
CODE105=ROOT/"tools"/"stage105_small_sail_spoke_count.py"
CODE153=ROOT/"tools"/"stage153_under_pier_triangle_junctions.py"
OUT=ROOT/"analysis"/"runs"/"stage175-stage105-apex-audit"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
EXPECTED_APICES=((1042,448),(1148,433),(1282,411),(1372,397),(1490,357))
MAX_APEX_OFFSET=8

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    old=json.loads(OLD.read_text())
    newer=json.loads(NEW164.read_text())
    a=CODE105.read_text()
    b=CODE153.read_text()
    old_ann=old["synthetic_annulus_counts"]
    old_scan=old["synthetic_scanline_counts"]
    strictly_increasing=lambda xs:all(x<y for x,y in zip(xs,xs[1:]))
    checks={
        "original_SHA":sha==SHA,
        "legacy_Stage105_id":old["experiment_id"]=="A11-EXP-105",
        "legacy_Stage105_fixed_5_centers":old["detected_centers"]==[1042,1148,1282,1372,1490],
        "legacy_Stage105_y345_to_500_source":'SEARCH=(900,345,1585,500)' in a,
        "legacy_Stage105_apex_from_dark_upper_crop":
            'ys,xs=np.where(bw[:int(0.70*h),xa:xb])' in a,
        "legacy_Stage105_five_site_count":len(old["sails"])==5,
        "old_Stage105_failed_controls":not old["controls_pass"] and not old["promoted"],
        "old_3_to_7_annulus_replay":old_ann==[3,4,3,3,2],
        "old_3_to_7_scanline_replay":old_scan==[3,4,5,6,2],
        "old_both_synthetic_sequences_nonmonotone":
           not strictly_increasing(old_ann) and not strictly_increasing(old_scan),
        "independent_Stage153_reference_has_apexes":
           all(f'"sail{i}":(({x},{y}),' in "".join(b.split()) for i,(x,y) in enumerate(EXPECTED_APICES,1)),
        "confirmed_Stage164_crop_source_loss":
           newer["decision"]=="STAGE112_UPPER_SAIL_CROPS_MATERIALLY_INCOMPLETE"
           and newer["materially_incomplete_true_sails"]==3
           and newer["synthetic_controls"]["pass"],
    }
    records=[]
    for i,(site,apex) in enumerate(zip(old["sails"],EXPECTED_APICES),1):
        x0,y0,x1,y1=site["box"]
        ox,oy=site["variants"]["original"]["annulus"]["apex"]
        old_global=(float(x0+ox),float(y0+oy))
        dist=float(math.hypot(old_global[0]-apex[0],old_global[1]-apex[1]))
        geom=newer["fixed_geometry"]["sail"+str(i)]
        rows={"sail_index":i,"known_true_tip_xy":list(apex),
              "old_crop":site["box"],"old_apex_within_crop":[ox,oy],
              "old_estimated_global_apex_xy":list(old_global),
              "true_apex_distance_px":round(dist,3),
              "displacement_at_least_8px":dist>=MAX_APEX_OFFSET,
              "Stage164_percent_real_mask_area_cut_below_or_outside_box":round(
                    100*geom["geometric_omission"]["omitted_area_fraction"],2),
              "Stage105_spoke_count_reported":site["count"],
              "Stage105_count_stable_original":site["stable"]}
        records.append(rows)
        checks[f"Stage105_box_equals_Stage164_original_box_sail{i}"]=(
            site["box"]==geom["original_stage112_crop"])
    bad=sum(r["displacement_at_least_8px"] for r in records)
    checks["at_least_three_source_apices_wrong_by_8px"]=bad>=3
    valid=all(checks.values())
    decision=("CONFIRMED_STAGE105_UNCALIBRATED_AND_WRONG_APEX_SOURCE" if valid else
              "CONTROL_FAILURE")
    result={
       "experiment_id":"A11-EXP-175","source_sha256":sha,
       "original_artwork_pixels_examined":False,
       "hypothesis":"Stage105's local upper-crop dark-pixel apex does not reproduce the five authentic independently fixed small-sail tips; synthetic spoke counts were already nonmonotone.",
       "guards":checks,"controls_passed":sum(checks.values()),
       "controls_total":len(checks),"legacy_synthetic_annulus":old_ann,
       "legacy_synthetic_scanline":old_scan,"legacy_controls_pass":old["controls_pass"],
       "bad_apex_locations_at_least_8px":bad,
       "per_sail_apex_and_crop_data":records,"decision":decision,
       "scope_limit":"An observed wrong local anchor and failed synthetic 3..7 calibration invalidate old Stage105 inferred spoke count sequence, not all possible visible lines in real sails. No source content was re-tested.",
       "safety":"No wallet, addresses, key derivation, BIP39, OCR, social/external research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage175 — Stage105 old source apex and synthetic-control defect","",
      f"- Canonical PNG SHA provenance: **{sha==SHA}**",
      f"- Exact source/result guards: **{sum(checks.values())}/{len(checks)}**",
      f"- Stage105 false apex positions ≥8 px from Stage153 true reference: **{bad}/5**",
      f"- Stage105 original synthetic 3..7 spoke annulus counts: **{old_ann}** (NOT monotonic)",
      f"- Stage105 original synthetic 3..7 scanline counts: **{old_scan}** (NOT monotonic)",
      f"- Stage164 independently verified ≥20% real source ink omitted by old boxes: **{newer['materially_incomplete_true_sails']}/5**",
      f"- Decision: **{decision}**","",
      "| Sail | True tip | Stage105 inferred tip | Distance (px) | Missing cropped area |",
      "|---|---|---|---:|---:|"]
    for row in records:
        lines.append(f"| {row['sail_index']} | {row['known_true_tip_xy']} | {row['old_estimated_global_apex_xy']} | {row['true_apex_distance_px']:.1f} | {row['Stage164_percent_real_mask_area_cut_below_or_outside_box']:.1f}% |")
    lines+=["","Stage105 had failed its OWN synthetic controls; no source-confirmed counted spoke pattern was ever established by that stage. This is a metadata/geometry QA, not a new spoke count or cryptographic clue.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":175,"controls":f"{sum(checks.values())}/{len(checks)}",
      "bad_apex_8px":bad,"decision":decision}))
if __name__=="__main__":main()
