#!/usr/bin/env python3
"""A11-EXP-163 — immutable scope audit of historical superbatch 37-87.

Only reads published repository code/manifest/reports and SHA-verifies the
canonical PNG. Proves which tests depended on the already-rejected old ROI
without rerunning old p-values, changing stats or assigning a new secret.
Precommitted classification rules are in analysis/STAGE_QUEUE.md.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
SCRIPT=ROOT/"tools"/"superbatch_stage37_87.py"
MANIFEST=ROOT/"analysis"/"superbatch"/"STAGE_37_86_MANIFEST.json"
RESULT87=ROOT/"analysis"/"runs"/"superbatch-37-87"/"result.json"
RESULT88=ROOT/"analysis"/"runs"/"stage88-superbatch-survivor-replication"/"result.json"
RESULT112=ROOT/"analysis"/"runs"/"stage112-corrected-sail-width-progression"/"result.json"
RESULT132=ROOT/"analysis"/"runs"/"stage132-large-sail-roi-coverage"/"result.json"
RESULT155=ROOT/"analysis"/"runs"/"stage155-small-sail-band-audit"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage163-superbatch-source-provenance"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"

def load(p):return json.loads(p.read_text())
def impact(row):
    """Pure classification, fixed BEFORE examining historical p-values."""
    m=row["method"]
    if m.startswith("region_random_window:"):
        return "old_large_sail_bbox"
    if m.startswith("small_sails_permutation:"):
        return "old_small_sails_strip_and_identity"
    if m.startswith("semantic_region_random:"):
        region=m.rsplit(":",1)[-1]
        if region=="large_sail":return "old_large_sail_bbox"
        if region=="small_sails":return "old_small_sails_strip_and_identity"
    if m=="robustness_control:small_sail_count":
        return "old_small_sails_strip_and_identity"
    if m in ("robustness_control:large_sail_edge",
             "robustness_control:large_sail_xsym",
             "robustness_control:large_sail_spectral"):
        return "old_large_sail_bbox"
    return None

def main():
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    manifest=load(MANIFEST)
    archive=load(RESULT87)
    replication=load(RESULT88)
    s112=load(RESULT112)
    s132=load(RESULT132)
    s155=load(RESULT155)
    source=SCRIPT.read_text()
    compact="".join(source.split())
    expected_source=(
       "LARGE=(44,320,359,599)" in compact
       and '"small_sails":(367,360,1500,480)' in compact
       and "r=gray[360:480,367:1550]" in compact
       and 'ifmethod.startswith("region_random_window:"):' in compact
       and 'elifmethod.startswith("small_sails_permutation:"):' in compact
    )
    srcvalid=(
       digest==SHA
       and s132["decision"]=="LEGACY_LARGE_SAILBOAT_BBOX_INCOMPLETE"
       and s155["decision"]=="LEGACY_SMALL_SAIL_BAND_MATERIALLY_TRUNCATES_TRUE_SAILS"
       and s112["detected_centers"]["original"]==[1042,1148,1282,1372,1490]
       and bool(s112["stage19_defect"])
    )
    man=manifest["experiments"]
    arc=archive["all_results"]
    expect=list(range(37,87))
    mani_ids=[r["stage"] for r in man]
    archived_ids=[r["stage"] for r in arc]
    methods_match=all(a["method"]==b["method"] and a["id"]==b["id"]
                  for a,b in zip(man,arc))
    analytic=[r for r in man if not r["control"]]
    controls=[r for r in man if r["control"]]
    historic_consistent=(
       len(man)==len(arc)==50 and len(set(mani_ids))==50
       and sorted(mani_ids)==sorted(archived_ids)==expect
       and methods_match
       and len(analytic)==42 and len(controls)==8
       and archive["counts"].get("PROMOTED",0)==0
       and archive["counts"].get("INTERESTING",0)==3
    )
    rows=[]
    for row,record in zip(man,arc):
        classification=impact(row)
        rows.append({
            "stage":row["stage"],"id":row["id"],
            "method":row["method"],"control":bool(row["control"]),
            "family":row["family"],"direct_legacy_dependency":classification,
            "archived_classification":record["classification"],
            "original_reported_p":record.get("p_value"),
            "original_reported_q":record.get("q_value"),
        })
    affected=[r for r in rows if r["direct_legacy_dependency"]]
    affect_anal=[r for r in affected if not r["control"]]
    affect_ctrl=[r for r in affected if r["control"]]
    impacted=[r["stage"] for r in affected]
    declared=list(range(37,47))+list(range(55,63))+[73,74,80,84,85,86]
    impact_right=(sorted(impacted)==sorted(declared)
        and len(affected)==24 and len(affect_anal)==20
        and len(affect_ctrl)==4)
    candidates={int(r["candidate"].split("-")[-1]):r for r in replication["candidates"]}
    nominal_replay=(set(candidates)=={43,50,61}
                     and impact(man[43-37])=="old_large_sail_bbox"
                     and impact(man[61-37])=="old_small_sails_strip_and_identity"
                     and impact(man[50-37]) is None
                     and replication["confirmed_count"]==0)
    coverage_check=(
        s132["real_pass_cases"]==s132["real_total_cases"]==12
        and s155["materially_truncated_sails"]==4
        and s155["synthetic_controls"]["passed"]==40
    )
    checks={
       "canonical_SHA":digest==SHA,
       "source_script_expected_old_ROI":bool(expected_source),
       "source_geometry_prior_decisions":bool(srcvalid),
       "manifest_archived_50_and_42_8":bool(historic_consistent),
       "expected_24_direct_dependencies":bool(impact_right),
       "nominal_replication_scope_43_61_but_not50":bool(nominal_replay),
       "earlier_audits_quantified_source_coverage":bool(coverage_check),
    }
    validated=all(checks.values())
    decision=("VERIFIED_LEGACY_SUPERBATCH_OBJECT_CROP_SCOPE_DEFECT"
        if validated else "CONTROL_FAILURE")
    impacted_nominals=[r for r in rows if r["archived_classification"]=="INTERESTING" and r["direct_legacy_dependency"]]
    result={
       "experiment_id":"A11-EXP-163","source_sha256":digest,
       "scope":"static source-dependency census, NO hypothesis retest or new p-values",
       "direct_checks":checks,"controls_pass":validated,
       "direct_legacy_source_tests":len(affected),
       "direct_legacy_analytic_tests":len(affect_anal),
       "direct_legacy_controls":len(affect_ctrl),
       "counts":{"all":len(rows),"hypotheses":len(analytic),"controls":len(controls)},
       "affected_stage_ids":sorted(impacted),
       "nominal_findings_directly_affected":[r["id"] for r in impacted_nominals],
       "nominal_findings_unaffected_by_these_explicit_ROI_references":["A11-EXP-050"],
       "affected_control_ids":[r["id"] for r in affect_ctrl],
       "by_row":rows,"decision":decision,
       "scope_limit":"The published q and p values remain the original old-footprint test outputs; this audit does not correct them, rerun their families or claim a new significant signal. Other footprint limitations remain possible. The lack of promoted old tests is factual for that old scope only.",
       "safety":"Read-only source and manifest metadata, canonical PNG only SHA; no cryptographic candidate, wallet, social/external research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=[
      "# Stage163 — fixed original superbatch object ROI dependency audit","",
      f"- Canonical SHA verified: **{checks['canonical_SHA']}**",
      f"- Predeclared source / manifest / replication guards: **{sum(checks.values())}/{len(checks)}**",
      f"- Old superbatch directly using demonstrated bad source regions: **{len(affected)}/50**",
      f"- Affected source-scope tests: **{len(affect_anal)}/42**",
      f"- Affected historical source-scope controls: **{len(affect_ctrl)}/8**",
      f"- Old nominal uncorrected source-dependent results: **{[r['id'] for r in impacted_nominals]}**",
      f"- Stage88 failed original-scope replication also depends on bad ROIs for 43,61: **{nominal_replay}**",
      f"- Decision: **{decision}**","",
      "| Group | Directly affected old stages | Footprint defect |",
      "|---|---|---|",
      "| Main giant sail metrics | 37–46, 73 and controls 80,85,86 | Stage132 incomplete large_sailboat box |",
      "| Five small sail metrics | 55–62, 74 and control 84 | Stage155 truncated y strip; Stage112 false object set |",
      "",
      "NOTE: Stage87's 42 original BH-FDR results and Stage88's old-scope p-values were NOT recomputed. No result is promoted by this provenance audit. Unaffected means only NOT in the two exact dependency categories; it is not proof of perfect localization.","",
      "No keys, wallets, guesses, phrases or outside source searches.",""
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"stage":163,"checks":f"{sum(checks.values())}/{len(checks)}",
       "affected":len(affected),"tested":len(affect_anal),"controls":len(affect_ctrl),
       "decision":decision}))
if __name__=="__main__":
    main()
