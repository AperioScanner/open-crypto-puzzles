#!/usr/bin/env python3
"""Stage 22: deterministic synthesis and stop rule for the visual 0x321 hypothesis."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNS=ROOT/"analysis"/"runs"
OUT=RUNS/"stage22-321-stop-rule"
OUT.mkdir(parents=True,exist_ok=True)

def load(stage):
    return json.loads((RUNS/stage/"result.json").read_text())

def main():
    s10=load("stage10-marker-robustness")
    s13=load("stage13-321-null-model")
    s15=load("stage15-semantic-321-counts")
    s16=load("stage16-321-coding-audit")
    s17=load("stage17-orientation-geometry-independence")
    s20=load("stage20-hv-run-structure")
    s21=load("stage21-independent-hv-classifiers")

    hv_stable=bool(s10["margin_robustness"] and min(x["exact_sequence_fraction"] for x in s10["jitter_robustness"])>=0.80)
    hv_replicated=bool(s21["replicated"])
    simple_geometry_explains=bool(s17["bonferroni_over_6_features"]<0.05)
    count_corroboration=bool(len(s15["promoted"])>0)
    grouping_supported=bool(s16["geometry_grouping"]["four_four_four_boundaries_are_largest"])
    look_elsewhere=float(s16["any_321_or_123_under_common_choices_probability"])
    run_exceptional=bool(s20["composite_simple_block_probability"]<0.05)

    retain_hv=hv_stable and hv_replicated and not simple_geometry_explains
    retire_hex=(not count_corroboration) and (not grouping_supported) and look_elsewhere>=0.05 and (not run_exceptional)

    verdict={
      "experiment_id":"A11-EXP-022",
      "scope":"deterministic evidence synthesis for visual H/V versus hexadecimal 0x321 interpretation; no private-key operations",
      "evidence":{
        "hv_crop_stable":hv_stable,
        "hv_independently_replicated":hv_replicated,
        "simple_geometry_explains_hv":simple_geometry_explains,
        "independent_321_count_corroboration":count_corroboration,
        "geometry_supports_4_4_4_hex_grouping":grouping_supported,
        "common_choice_321_123_probability":look_elsewhere,
        "run_structure_exceptional":run_exceptional,
      },
      "hv_texture_verdict":"RETAIN_AS_VISUAL_LEAD" if retain_hv else "DOWNGRADE",
      "hex_0x321_verdict":"RETIRE_AS_PRIMARY" if retire_hex else "RETAIN_FOR_REVIEW",
      "continue_to_bit_steganalysis":True,
      "stop_rule":"Retire hexadecimal 0x321 as primary if there is no independent 321 count corroboration, no natural 4+4+4 geometry, common-choice look-elsewhere probability >=5%, and H/V run structure is not exceptional.",
    }
    (OUT/"result.json").write_text(json.dumps(verdict,indent=2)+"\n")
    md=["# Stage 22 — visual 321 evidence synthesis and stop rule","",
        "**Experiment:** A11-EXP-022","",
        "This stage does not invent a new transform. It applies the pre-declared stop rule to the completed 321 evidence.","",
        f"- H/V crop stability: **{hv_stable}**",
        f"- Independent H/V classifier replication: **{hv_replicated}**",
        f"- Simple building geometry explains H/V: **{simple_geometry_explains}**",
        f"- Independent 321/123 count corroboration: **{count_corroboration}**",
        f"- Natural 4+4+4 geometry for hexadecimal grouping: **{grouping_supported}**",
        f"- Common representation/transform 321-or-123 probability: **{look_elsewhere:.4f}**",
        f"- H/V run structure exceptional: **{run_exceptional}**","",
        f"## H/V texture verdict: **{verdict['hv_texture_verdict']}**",
        f"## Hexadecimal 0x321 verdict: **{verdict['hex_0x321_verdict']}**","",
        "The robust H/V texture can remain a visual clue even if naming it 0x321 is retired. The research now pivots to statistical bit-level steganalysis as planned.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-022","hv":verdict["hv_texture_verdict"],"hex321":verdict["hex_0x321_verdict"],"continue_to_bits":True}))

if __name__=="__main__": main()
