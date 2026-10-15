#!/usr/bin/env python3
"""A11-EXP-179: source-archive eight-peak SPATIAL IDENTITY, not just peak count.

Stage176 reported stable count 8 for sail1/sail2 across four reencodings.
Stage177 independently projected EACH variant's own selected u peaks into
upper sail space but had never established that those peaks matched across
versions. This stage compares frozen archived positions with a precommitted
3-grid-bin tolerance and +/- fixed rounding epsilon. No PNG pixels are read:
canonical image hash is only a provenance check. No source thresholds, ROI,
retuning, numerals, secrets, addresses, keys, mnemonics or wallets.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR176=ROOT/"analysis"/"runs"/"stage176-true-sail-radial-profile"/"result.json"
PRIOR177=ROOT/"analysis"/"runs"/"stage177-eight-peak-upper-continuation"/"result.json"
PRIOR178=ROOT/"analysis"/"runs"/"stage178-dense-hatch-false-peaks"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage179-eight-peak-identity"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
SITES=("sail1","sail2")
STEP=(.92-.08)/128.
EPS=.00002
TOL=3*STEP+EPS
BASE_WIDTHS={"sail1":70,"sail2":76}
OFFSETS=(0,1,2,3,4,5)
SIGNS=(-1,+1)

def positional(original,other,base_width):
    a=np.asarray(original,float)
    b=np.asarray(other,float)
    if a.size!=8 or b.size!=8:return None
    delta=np.abs(a-b)
    return {
       "eight_ordered_comparisons":len(delta),
       "matches_within_3_grid_indices":int(np.count_nonzero(delta<=TOL)),
       "all_eight_same_peak_within_tolerance":bool(np.all(delta<=TOL)),
       "maximum_normalized_u_shift":round(float(np.max(delta)),7),
       "mean_normalized_u_shift":round(float(np.mean(delta)),7),
       "max_base_projected_px_shift":round(float(np.max(delta)*base_width),4),
       "per_peak_abs_du":[round(float(x),7) for x in delta],
    }

def pure_numeric_controls():
    baseseq=np.linspace(.15,.85,8)
    cases=[]
    for site in SITES:
        for n in OFFSETS:
            for sign in SIGNS:
                fake=baseseq+sign*n*STEP
                reading=positional(baseseq,fake,BASE_WIDTHS[site])
                expected=n<=3
                passed=reading["all_eight_same_peak_within_tolerance"]==expected
                cases.append({
                    "site":site,"injected_shift_in_grid_bins":int(sign*n),
                    "expected_all_eight_pass":bool(expected),
                    "observed_all_eight_pass":reading["all_eight_same_peak_within_tolerance"],
                    "correct":bool(passed)
                })
    return {"pass":len(cases)==24 and all(x["correct"] for x in cases),
        "passed":sum(x["correct"] for x in cases),
        "cases":len(cases),
        "failures":[x for x in cases if not x["correct"]]}

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    s176=json.loads(PRIOR176.read_text())
    s177=json.loads(PRIOR177.read_text())
    s178=json.loads(PRIOR178.read_text())
    guards={
        "canonical_SHA_only":digest==SHA,
        "Stage176_source_SHA":s176["canonical_sha256"]==SHA,
        "Stage176_240_calibrated_fixtures":s176["controls"]["pass"] and s176["controls"]["passed"]==240,
        "Stage176_18_of_20_adequate":s176["adequate_real_site_format_count"]==18,
        "Stage176_two_eight_peaks_in_all_four_formats":all(
            s176["source_by_format_sail"][fmt][site]["count"]==8 and
            s176["source_by_format_sail"][fmt][site]["adequate"] and
            len(s176["source_by_format_sail"][fmt][site]["peak_u"])==8
            for site in SITES for fmt in FORMATS),
        "Stage176_original_grid_129_t72_87":
            s176["fixed_method"]["x_columns"]==129
            and all(abs(float(a)-float(b))<1e-10 for a,b in
              zip(s176["fixed_method"]["u_limits"],[.08,.92])),
        "Stage177_original_source_SHA":s177["canonical_source_sha256"]==SHA,
        "Stage177_24_calibrated_known_eight_fixtures":s177["calibration"]["pass"] and s177["calibration"]["passed"]==24,
        "Stage177_no_eight_upper_ray_confirmation":s177["decision"]=="INCONCLUSIVE_UPPER_TRACE_CORROBORATION",
        "Stage178_source_blind_controls":s178["guards_passed"]==s178["guards_total"]==15
            and s178["known_calibration"]["passed"]==24 and
            s178["stable_eight_peaks_with_no_apex_rays_n"]==0,
        "frozen_true_sail_geometry":all(
            abs(TRIANGLES[site][2][0]-TRIANGLES[site][1][0])==BASE_WIDTHS[site]
            for site in SITES),
        "quantized_three_u_bins_plus_rounding_tol":
            abs(STEP-(.92-.08)/128)<1e-12 and EPS==.00002
    }
    calibration=pure_numeric_controls()
    results={}
    stable_sites=[]
    for site in SITES:
        base=s176["source_by_format_sail"]["original"][site]["peak_u"]
        comparisons={}
        for fmt in FORMATS:
            peaks=s176["source_by_format_sail"][fmt][site]["peak_u"]
            reading=positional(base,peaks,BASE_WIDTHS[site])
            comparisons[fmt]=reading
        site_stable=all(reading is not None and
               reading["all_eight_same_peak_within_tolerance"]
               for reading in comparisons.values())
        results[site]={
          "original_eight_normalized_u":base,
          "by_format":comparisons,
          "all_four_formats_same_eight_positions":bool(site_stable),
          "source_reference_type":"Stage176 archived peaks, not new image pixels"
        }
        if site_stable:stable_sites.append(site)
    checks={**guards,
       "24_of_24_known_offset_numeric_controls":calibration["pass"],
       "original_8_peak_list_each_site":all(len(results[site]["original_eight_normalized_u"])==8 for site in SITES),
       "all_per_format_comparisons_well_defined":all(
           results[site]["by_format"][fmt] is not None
           for site in SITES for fmt in FORMATS)}
    ok=all(checks.values())
    stable_count=len(stable_sites)
    decision=("CONTROL_FAILURE" if not ok else
      "BOTH_EIGHT_PEAK_SETS_POSITIONALLY_STABLE" if stable_count==2 else
      "ONE_EIGHT_PEAK_SET_UNSTABLE" if stable_count==1 else
      "BOTH_EIGHT_PEAK_SETS_POSITIONALLY_UNSTABLE")
    data={
      "experiment_id":"A11-EXP-179","canonical_SHA256_provenance_only":digest,
      "original_source_pixel_reads":False,
      "hypothesis":"An unchanged peak COUNT of 8 over lossy encodings may not identify the same eight original source ink ridge POSITIONS; Stage177 implicitly compared variant-specific independently selected peaks.",
      "fixed_sites":SITES,
      "source_of_frozen_peak_locations":"Stage176 archived peak_u lists by source format and true sail",
      "fixed_grid":{"u_start":.08,"u_end":.92,"grid_columns":129,
                    "grid_step_u":STEP,
                    "max_positional_shift_grid_bins":3,
                    "archive_5_decimal_rounding_epsilon":EPS,
                    "normalized_u_tolerance":TOL},
      "source_and_numerical_guards":checks,
      "checks_passed":sum(checks.values()),"checks_total":len(checks),
      "known_positional_controls":calibration,
      "per_sail_archived_peak_matches":results,
      "stable_eight_peak_position_site_count":stable_count,
      "stable_eight_peak_sites":stable_sites,
      "decision":decision,
      "interpretation_limit":"This tests positional reproducibility in ONE original PNG, not physical ray connectivity, no independent art or author intention. A failure of predeclared 3-bin matching does not prove the same peaks could not be recognized under a differently justified criterion. Numeric 8 from same source is not a secret digit.",
      "safety":"Read-only existing source arrays and PNG SHA, no private key, mnemonic, address check, wallet access, OCR or off-image/social research."}
    (OUT/"result.json").write_text(json.dumps(data,indent=2)+"\n")
    lines=[
      "# Stage179 — do the eight Stage176 pencil peaks stay in the same POSITIONS?","",
      f"- Source PNG SHA provenance (no pixel reading): **{digest==SHA}**",
      f"- Predeclared Stage176–178 and numerical checks: **{sum(checks.values())}/{len(checks)}**",
      f"- Pure known position-jitter positive/negative controls: **{calibration['passed']}/{calibration['cases']}**",
      f"- Original image source sail regions retaining all eight positions across formats: **{stable_count}/2**",
      f"- Decision: **{decision}**","",
      "| Sail | Original eight-peak count | JPEG85 matched positions / 8 | JPEG70 matched / 8 | Resampled matched / 8 |",
      "|---|---:|---:|---:|---:|"
    ]
    for site in SITES:
        z=results[site]["by_format"]
        lines.append(
            f"| {site} | 8 | {z['jpeg85']['matches_within_3_grid_indices']} | "
            f"{z['jpeg70']['matches_within_3_grid_indices']} | "
            f"{z['down75_up']['matches_within_3_grid_indices']} |")
    lines+=["","The same eight peaks were NOT assumed to be the same eight *drawn* rays without positional matching. JPEGs are transformed from one source, not independent illustrations. Stage177 disjoint upper-region support remains unconfirmed in the image, so neither positional stability nor numeric count establishes an encoding.","",
       "No source pixel modifications, no numeric decoding, no key/mnemonic/wallet operations.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":179,"controls":f"{sum(checks.values())}/{len(checks)}",
         "numeric":f"{calibration['passed']}/{calibration['cases']}",
         "sites_stable":stable_count,"decision":decision}))
if __name__=="__main__":main()
