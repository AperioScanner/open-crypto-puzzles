#!/usr/bin/env python3
"""A11-EXP-173: audit Stage126's actual-vs-synthetic masthead apex frame.

Original Stage126 inspects top+3..17; actual independently annotated apex is
top, but its synthetic control draws fake sail apex at top+24. This is a
source-provenance audit only; no source image pixels analyzed.
"""
import hashlib,json
from pathlib import Path
from stage126_masthead_protrusion import SITES,T0,T1
from stage153_under_pier_triangle_junctions import TRIANGLES
R=Path(__file__).resolve().parents[1]
PNG=R/"clues/arweave-puzzle-11.png"
OLD=R/"analysis/runs/stage126-masthead-protrusion/result.json"
CODE=R/"tools/stage126_masthead_protrusion.py"
OUT=R/"analysis/runs/stage173-masthead-apex-frame"
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(PNG.read_bytes()).hexdigest()
    old=json.loads(OLD.read_text())
    script=CODE.read_text()
    checks={
        "source_SHA":digest==SHA==old["canonical_sha256"],
        "archived_stage126_id":old["experiment_id"]=="A11-EXP-126",
        "five_sites":len(SITES)==len(old["sites_predeclared"])==5,
        "declared_apex_window":(T0,T1)==(3,18),
        "original_inspect_code":"y0=int(top+T0); y1=int(top+T1)" in script,
        "synthetic_tip_code":"apex=(cx,top+24)" in script,
        "synthetic_calibration":old["controls"]["passed"] and old["controls"]["passes"]==old["controls"]["cases"]==180,
        "old_original_stable_count":old["stable_site_count"]==4,
        "old_original_decision":old["decision"]=="UNIFORM_MASTHEAD_STATE",
    }
    sites=[]
    for i,(_,x,top,height,half) in enumerate(SITES):
        apex=TRIANGLES["sail"+str(i+1)][0]
        inspected=list(range(top+T0,top+T1))
        z={
          "site":i+1,"source_apex":apex,"Stage126_reference_top":top,
          "old_measured_y_interval":[min(inspected),max(inspected)+1],
          "synthetic_apex_y":top+24,
          "original_above_true_apex":sum(y<apex[1] for y in inspected),
          "synthetic_above_own_fake_apex":sum(y<top+24 for y in inspected),
          "points":len(inspected),
          "source_point_equal_to_original_apex":x==apex[0] and top==apex[1],
          "source_data_match_archive":old["sites_predeclared"][i]==list(SITES[i]),
          "historical_label":old["sites"][i]["stable_class"],
        }
        sites.append(z)
    checks["all_actual_apex_coordinates"]=all(z["source_point_equal_to_original_apex"] and z["source_data_match_archive"] for z in sites)
    checks["no_original_test_pixel_above_apex"]=all(z["original_above_true_apex"]==0 for z in sites)
    checks["all_synthetic_test_pixels_above_fake_apex"]=all(z["synthetic_above_own_fake_apex"]==15 for z in sites)
    valid=all(checks.values())
    decision="CONFIRMED_STAGE126_SOURCE_SYNTHETIC_APEX_FRAME_MISMATCH" if valid else "CENSUS_GUARD_FAILURE"
    data={"experiment_id":"A11-EXP-173","canonical_SHA_provenance_only":digest,
          "original_art_pixels_examined":False,"source_checks":checks,
          "controls_passed":sum(checks.values()),"controls_total":len(checks),
          "sites":sites,"decision":decision,
          "limit":"Four original Stage126 EXTENDED states in region BELOW real sail apex do not evidence extension ABOVE apex; no corrected real masthead pixels examined.","safety":"No wallet, key, mnemonic, address or social/external analysis"}
    (OUT/"result.json").write_text(json.dumps(data,indent=2)+"\n")
    lines=["# Stage173 — old Stage126 synthetic source-tip mismatch","",
           f"- Source SHA verified: **{digest==SHA}**",
           f"- Predeclared geometry checks: **{sum(checks.values())}/{len(checks)}**",
           f"- Old synthetic controls: **180/180**, but tested ABOVE artificially lower tip",
           "- Original source window: **0/75** total sampled rows ABOVE original true sail tip",
           "- Synthetic window: **75/75** sampled rows ABOVE synthetic artificially displaced tips",
           f"- Decision: **{decision}**","",
           "| Sail | Source true tip y | Stage126 real y rows | Synthetic fake tip y |",
           "|---|---:|---|---:|"]
    for z in sites:
        lines.append(f"| {z['site']} | {z['source_apex'][1]} | {z['old_measured_y_interval']} | {z['synthetic_apex_y']} |")
    lines+=["","The old four apparent mast extensions may reflect ordinary sail panels. This QA does not establish a new masthead pattern or hidden message. A corrected true-above-apex source test is separately required.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":173,"checks":f"{sum(checks.values())}/{len(checks)}","decision":decision}))
if __name__=="__main__":main()
