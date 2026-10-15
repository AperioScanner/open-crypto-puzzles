#!/usr/bin/env python3
"""A11-EXP-180 — cross-sail normalized positional identity of archived eight peaks.

Question DIFFERENT from Stage120's 2D copied pencil motif null: whether the
SAME ordered eight normalized u intensity-profile positions occur in BOTH
source sail1 and sail2, each already stable through source re-encodings.
This is a bounded archived data audit, no pixel reading or secret search.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"clues"/"arweave-puzzle-11.png"
OLD176=ROOT/"analysis"/"runs"/"stage176-true-sail-radial-profile"/"result.json"
OLD177=ROOT/"analysis"/"runs"/"stage177-eight-peak-upper-continuation"/"result.json"
OLD179=ROOT/"analysis"/"runs"/"stage179-eight-peak-identity"/"result.json"
OLD120=ROOT/"analysis"/"runs"/"stage120-sail-motif-reuse"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage180-cross-sail-eight-profile"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
STEP=(.92-.08)/128
EPS=.00002
TOL=STEP*3+EPS
WIDTHS=(70,76)

def compare_positions(a,b):
    x=np.asarray(a,float)
    y=np.asarray(b,float)
    if len(x)!=8 or len(y)!=8:
        return None
    if np.any(np.diff(x)<=0) or np.any(np.diff(y)<=0):
        return None
    gaps=np.abs(x-y)
    n=int(np.count_nonzero(gaps<=TOL))
    return {"ordered_positions_compared":8,
            "matching_positions_3bins":n,
            "all8_match":bool(n==8),
            "max_normalized_u_delta":round(float(np.max(gaps)),7),
            "mean_normalized_u_delta":round(float(np.mean(gaps)),7),
            "max_projected_shift_sail1_px":round(float(np.max(gaps)*WIDTHS[0]),4),
            "max_projected_shift_sail2_px":round(float(np.max(gaps)*WIDTHS[1]),4),
            "eight_ordered_du":[round(float(z),7) for z in gaps]}

def reference_controls():
    x=np.linspace(.15,.85,8)
    cases=[]
    for role in ("A-vs-B","B-vs-A"):
        for k in range(6):
            for sign in (-1,1):
                y=x+sign*k*STEP
                z=compare_positions(x,y) if role=="A-vs-B" else compare_positions(y,x)
                expected=(k<=3)
                good=(z is not None and z["all8_match"]==expected)
                cases.append({"role":role,"signed_shift_bins":k*sign,
                              "expected_all8":expected,"measured_all8":z["all8_match"] if z else None,
                              "pass":bool(good)})
    return {"pass":len(cases)==24 and all(z["pass"] for z in cases),
            "cases":len(cases),"passed":sum(z["pass"] for z in cases),
            "failures":[z for z in cases if not z["pass"]]}

def main():
    sha=hashlib.sha256(SRC.read_bytes()).hexdigest()
    a176=json.loads(OLD176.read_text())
    a177=json.loads(OLD177.read_text())
    a179=json.loads(OLD179.read_text())
    a120=json.loads(OLD120.read_text())
    gates={
      "source_sha_provenance":sha==SHA,
      "Stage176_source_sha_and_240_controls":
          a176["canonical_sha256"]==SHA and a176["controls"]["pass"] and a176["controls"]["passed"]==240,
      "Stage176_two_eight_peak_source_sails":
          all(a176["source_by_format_sail"][fmt][site]["count"]==8
             and a176["source_by_format_sail"][fmt][site]["adequate"]
             and len(a176["source_by_format_sail"][fmt][site]["peak_u"])==8
             for site in ("sail1","sail2") for fmt in FORMATS),
      "Stage177_24_controls_but_not_eight_continuity":
          a177["calibration"]["pass"] and a177["calibration"]["passed"]==24
          and a177["decision"]=="INCONCLUSIVE_UPPER_TRACE_CORROBORATION",
      "Stage179_15_source_archive_guards":
          a179["checks_passed"]==a179["checks_total"]==15,
      "Stage179_24_numeric_reference_controls":
          a179["known_positional_controls"]["pass"]
          and a179["known_positional_controls"]["passed"]==24,
      "Stage179_both_sail_peak_positions_stable_within_encodings":
          a179["decision"]=="BOTH_EIGHT_PEAK_SETS_POSITIONALLY_STABLE"
          and set(a179["stable_eight_peak_sites"])=={"sail1","sail2"},
      "Stage120_no_copied_2D_penstrokes_remains_valid":
          a120["canonical_sha256"]==SHA and
          a120["decision"]=="NO_EXACT_STROKE_TEMPLATE_REUSE"
          and a120["controls"]["controls_pass"],
      "Stage179_frozen_grid":
          abs(a179["fixed_grid"]["normalized_u_tolerance"]-TOL)<1.e-11
    }
    reference=reference_controls()
    per_format={}
    for fmt in FORMATS:
        a=a176["source_by_format_sail"][fmt]["sail1"]["peak_u"]
        b=a176["source_by_format_sail"][fmt]["sail2"]["peak_u"]
        z=compare_positions(a,b)
        per_format[fmt]={"sail1_eight_u":a,"sail2_eight_u":b,"comparison":z}
    gates["24_known_shift_reference_controls"]=reference["pass"]
    gates["archived_peak_vectors_are_ordered_and_eight"]=all(
        per_format[fmt]["comparison"] is not None for fmt in FORMATS)
    controls_ok=all(gates.values())
    same=all(per_format[fmt]["comparison"]["all8_match"]
             for fmt in FORMATS if per_format[fmt]["comparison"])
    verdict=("CONTROL_FAILURE" if not controls_ok else
             "CROSS_SAIL_EIGHT_1D_PROFILE_POSITIONS_MATCH" if same else
             "NO_CROSS_SAIL_EIGHT_1D_POSITION_STENCIL_AT_FIXED_TOLERANCE")
    data={
       "experiment_id":"A11-EXP-180","canonical_source_sha256_provenance_only":sha,
       "original_artwork_pixels_examined":False,
       "hypothesis":"Two source selected stable-eight lower ink profiles may replicate each other's eight normalized ridge positions, distinct from exact copied 2D pen pixels.",
       "historical_comparison_scope":"Only sail1 vs sail2 and archived Stage176 8 normalized u values; Stage120 2D motif-reuse null remains valid.",
       "fixed_tolerance":{"grid_step":STEP,"three_grid_bins_plus_archive_rounding_epsilon":TOL,
             "ordered_peak_matching_only":True,"n_peak_matches_required":8,
             "no_global_translation_rotation_flip_or_rescale":True},
       "precommitted_checks":gates,"checks_passed":sum(gates.values()),
       "checks_total":len(gates),"numeric_controls":reference,
       "source_one_d_profile_comparisons":per_format,
       "source_all_four_eight_positions_aligned":same,
       "decision":verdict,
       "interpretation_limit":"Pair was selected after both were noticed to have eight stable peaks. Even a matching profile would only describe two shading patterns from the SAME source drawing, not independent authorship proof, physical apex rays, p-value, key or intentionally encoded message. A negative excludes only direct unshifted same-index matching at the preregistered precision.",
       "safety":"No private key, BIP39, address/wallet checking, OCR or off-image/social investigation."
    }
    (OUT/"result.json").write_text(json.dumps(data,indent=2)+"\n")
    lines=[
       "# Stage180 — direct same-position eight lower ink-ridge profile, sail1 vs sail2","",
       f"- Canonical SHA provenance: **{sha==SHA}**",
       f"- Source/archive and known position controls: **{sum(gates.values())}/{len(gates)}**",
       f"- Synthetic exact known in/out-of-tolerance cases: **{reference['passed']}/{reference['cases']}**",
       f"- Direct 8/8 ridge-position matches in ALL four source encodings: **{same}**",
       f"- Decision: **{verdict}**","",
       "| Format | Same normalized ridge positions / 8 | Max normalized positional shift |",
       "|---|---:|---:|"
    ]
    for fmt in FORMATS:
        z=per_format[fmt]["comparison"]
        lines.append(f"| {fmt} | {z['matching_positions_3bins']} | {z['max_normalized_u_delta']:.5f} |")
    lines+=["","Stage120's source finding of no exact copied graphic 2D strokes is NOT contradicted by any direct 1D profile-position result. Both sails were selected because they had count eight; this test cannot establish independently authored symbols or ray connectivity. No secret material generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":180,"guards":f"{sum(gates.values())}/{len(gates)}",
        "reference":f"{reference['passed']}/{reference['cases']}",
        "match":same,"decision":verdict}))
if __name__=="__main__":main()
