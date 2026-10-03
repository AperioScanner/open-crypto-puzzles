#!/usr/bin/env python3
"""Stage 16: audit the coding-choice strength of reading the skyline H/V bits as 0x321.

Non-cryptographic. This experiment evaluates two issues:
1) whether the building geometry naturally supports a 4+4+4 grouping;
2) how much the apparent 321 surprise weakens after common representation and transform choices.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage16-321-coding-audit"
OUT.mkdir(parents=True,exist_ok=True)

OBS_BITS="001100100001"

def transforms(bits):
    rev=bits[::-1]
    comp="".join("1" if b=="0" else "0" for b in bits)
    return {
        "identity":bits,
        "reverse":rev,
        "complement":comp,
        "reverse_complement":comp[::-1],
    }

def reps(bits):
    n=int(bits,2)
    return {
        "hex3":format(n,"03x"),
        "oct4":format(n,"04o"),
        "dec":str(n),
        "bin12":bits,
    }

def has_321_or_123(s):
    s=s.lower()
    return ("321" in s) or ("123" in s)

def any_common_hit(bits):
    hits=[]
    for tname,tbits in transforms(bits).items():
        for rname,val in reps(tbits).items():
            if rname=="bin12":
                continue
            if has_321_or_123(val):
                hits.append({"transform":tname,"representation":rname,"value":val})
    return hits

def geometry_grouping():
    g=json.loads(GEOM.read_text())
    bs=g["buildings"]
    gaps=[]
    for a,b in zip(bs[:-1],bs[1:]):
        gaps.append(int(b["x0"]-a["x1"]))
    ranked=sorted(enumerate(gaps, start=1), key=lambda x:x[1], reverse=True)
    median=sorted(gaps)[len(gaps)//2]
    after4=gaps[3]
    after8=gaps[7]
    max_gap=max(gaps)
    return {
        "gaps_after_buildings_px":gaps,
        "ranked_gaps":[{"after_building":i,"gap_px":gap} for i,gap in ranked],
        "median_gap_px":median,
        "largest_gap_px":max_gap,
        "gap_after_4_px":after4,
        "gap_after_8_px":after8,
        "four_four_four_boundaries_are_largest": set([4,8]).issubset(set(i for i,_ in ranked[:2])),
        "largest_boundary_after_building":ranked[0][0],
    }

def main():
    obs_hits=any_common_hit(OBS_BITS)
    universe=0
    hit_count=0
    exact_identity_hex_321=0
    examples=[]
    for n in range(4096):
        bits=format(n,"012b")
        universe+=1
        hits=any_common_hit(bits)
        if hits:
            hit_count+=1
            if len(examples)<12:
                examples.append({"bits":bits,"hits":hits[:4]})
        if format(n,"03x")=="321":
            exact_identity_hex_321+=1

    geom=geometry_grouping()
    result={
        "experiment_id":"A11-EXP-016",
        "scope":"coding-choice/look-elsewhere audit only; no private-key operations",
        "observed_bits":OBS_BITS,
        "observed_identity_hex":format(int(OBS_BITS,2),"03x"),
        "observed_common_hits":obs_hits,
        "uniform_12bit_universe":universe,
        "exact_identity_hex_321_count":exact_identity_hex_321,
        "exact_identity_hex_321_probability":exact_identity_hex_321/universe,
        "any_321_or_123_under_common_choices_count":hit_count,
        "any_321_or_123_under_common_choices_probability":hit_count/universe,
        "common_choices":{
            "transforms":["identity","reverse","complement","reverse_complement"],
            "representations":["hex3","oct4","dec"],
            "pattern_rule":"contains 321 or 123",
        },
        "geometry_grouping":geom,
        "examples":examples,
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 16 — 0x321 coding-choice audit",
        "",
        "**Experiment:** A11-EXP-016",
        "",
        "This stage asks whether the robust 12-bit H/V sequence has strong evidence for the specific hexadecimal reading 0x321, rather than merely being a stable binary pattern.",
        "",
        "## Representation look-elsewhere",
        "",
        f"- Exact identity hexadecimal 321 under a fixed 12-bit null: 1/{universe} = {1/universe:.6f}.",
        f"- Allowing identity/reverse/complement/reverse-complement and common hex/octal/decimal representations, the fraction containing 321 or 123 is {hit_count}/{universe} = {hit_count/universe:.6f}.",
        f"- Observed sequence common-choice hits: {obs_hits}",
        "",
        "## Does the skyline support 4+4+4 grouping?",
        "",
        f"- Building gaps (after buildings 1..11): {geom['gaps_after_buildings_px']}",
        f"- Gap after building 4: {geom['gap_after_4_px']} px",
        f"- Gap after building 8: {geom['gap_after_8_px']} px",
        f"- Largest gap: {geom['largest_gap_px']} px after building {geom['largest_boundary_after_building']}",
        f"- Are 4 and 8 the two strongest geometric boundaries? {geom['four_four_four_boundaries_are_largest']}",
        "",
        "## Interpretation",
        "",
    ]
    if geom["four_four_four_boundaries_are_largest"]:
        md.append("The image geometry independently supports splitting the 12 buildings into three groups of four, which strengthens the three-hex-digit reading.")
    else:
        md.append("The image geometry does not independently support the 4+4+4 split needed for three hexadecimal nibbles. Therefore 0x321 should be treated as a post-hoc encoding candidate, not yet as an author-intended instruction.")
    md += [
        "",
        "The broader representation probability quantifies the look-elsewhere penalty: a memorable 321/123 appearance becomes less surprising once common reversals/complements and bases are allowed.",
        "This does not invalidate the robust H/V structure itself; it only audits the evidential weight of naming that structure 0x321.",
        ""
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-016",
        "observed_hex":result["observed_identity_hex"],
        "look_elsewhere_probability":result["any_321_or_123_under_common_choices_probability"],
        "four_four_four_supported":geom["four_four_four_boundaries_are_largest"],
        "largest_gap_after":geom["largest_boundary_after_building"],
    }))

if __name__=="__main__":
    main()
