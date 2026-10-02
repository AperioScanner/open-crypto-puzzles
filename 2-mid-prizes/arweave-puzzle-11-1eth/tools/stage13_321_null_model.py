#!/usr/bin/env python3
"""Stage 13: null-model significance of the robust 0x321 skyline marker.

Statistical, non-cryptographic analysis only.
"""
from __future__ import annotations
import itertools
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"analysis"/"runs"/"stage10-marker-robustness"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage13-321-null-model"
OUT.mkdir(parents=True,exist_ok=True)

def h2bits(seq):
    return "".join("0" if c=="H" else "1" for c in seq)

def descending_triplet(value):
    s=f"{value:03x}"
    d=[int(c,16) for c in s]
    return d[0]-1==d[1] and d[1]-1==d[2]

def ascending_triplet(value):
    s=f"{value:03x}"
    d=[int(c,16) for c in s]
    return d[0]+1==d[1] and d[1]+1==d[2]

def main():
    data=json.loads(SRC.read_text())
    seq=data["baseline_sequence"]
    bits=h2bits(seq)
    value=int(bits,2)
    ones=bits.count("1")
    n=len(bits)
    assert n==12 and value==0x321 and ones==4

    all_values=list(range(1<<n))
    fixed_count=[v for v in all_values if v.bit_count()==ones]
    desc=[v for v in all_values if descending_triplet(v)]
    asc=[v for v in all_values if ascending_triplet(v)]
    consecutive=sorted(set(desc+asc))
    desc_fixed=[v for v in fixed_count if descending_triplet(v)]
    consecutive_fixed=[v for v in fixed_count if v in consecutive]

    # Exact probabilities under transparent nulls.
    uniform_exact=1/(1<<n)
    conditional_exact=1/math.comb(n,ones)
    polarity_uniform=2/(1<<n)  # sequence or complement when H/V polarity was not pre-registered

    # Empirical Bernoulli null using the observed V rate only.
    p=ones/n
    bernoulli_exact=(p**ones)*((1-p)**(n-ones))

    result={
        "experiment_id":"A11-EXP-013",
        "scope":"null-model significance of the visual H/V marker only; no secret material",
        "sequence":seq,
        "bits":bits,
        "hex":"321",
        "n":n,
        "ones":ones,
        "null_models":{
            "uniform_exact_321":{"probability":uniform_exact,"one_in":1/uniform_exact},
            "uniform_allow_label_polarity_321_or_cde":{"probability":polarity_uniform,"one_in":1/polarity_uniform},
            "conditional_on_four_V_exact_positions":{"probability":conditional_exact,"one_in":1/conditional_exact},
            "bernoulli_p_equal_observed_V_rate":{"p_V":p,"probability_exact_pattern":bernoulli_exact,"one_in":1/bernoulli_exact},
        },
        "look_elsewhere_families":{
            "strict_descending_consecutive_hex_triplets":{"count":len(desc),"probability":len(desc)/(1<<n),"examples":[f"{v:03x}" for v in desc]},
            "ascending_or_descending_consecutive_hex_triplets":{"count":len(consecutive),"probability":len(consecutive)/(1<<n)},
            "descending_triplets_conditioned_on_four_ones":{"count":len(desc_fixed),"space":len(fixed_count),"probability":len(desc_fixed)/len(fixed_count)},
            "ascending_or_descending_conditioned_on_four_ones":{"count":len(consecutive_fixed),"space":len(fixed_count),"probability":len(consecutive_fixed)/len(fixed_count)},
        },
        "interpretation":{
            "supports":"321 is uncommon under simple random-orientation nulls and is robust under crop perturbation.",
            "does_not_support":"The calculation does not prove author intent because the skyline segmentation, binary coding, and memorable-pattern recognition were not pre-registered; look-elsewhere effects remain.",
            "next":"Treat 321 as a prioritized semantic lead, while requiring an independent visual/author clue before calling it intentional.",
        }
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    nm=result["null_models"]; le=result["look_elsewhere_families"]
    md=[
        "# Stage 13 — 0x321 null-model significance","",
        "**Experiment:** A11-EXP-013","",
        "This stage asks a narrow question: how surprising is the robust 12-building H/V sequence if building orientations were otherwise random? It is statistical only and does not touch private-key material.","",
        f"- Observed sequence: {seq}",
        f"- Binary under H=0, V=1: {bits}",
        f"- Hex: 0x{value:03x}",
        f"- V count: {ones}/{n}","",
        "## Exact null-model probabilities","",
        "| null model | probability | approximately |",
        "|:---|---:|---:|",
        f"| Uniform 12-bit sequence, exact 0x321 | {nm['uniform_exact_321']['probability']:.8f} | 1 in {nm['uniform_exact_321']['one_in']:.0f} |",
        f"| Uniform, allow H/V polarity (0x321 or 0xCDE) | {nm['uniform_allow_label_polarity_321_or_cde']['probability']:.8f} | 1 in {nm['uniform_allow_label_polarity_321_or_cde']['one_in']:.0f} |",
        f"| Condition on exactly four V buildings | {nm['conditional_on_four_V_exact_positions']['probability']:.8f} | 1 in {nm['conditional_on_four_V_exact_positions']['one_in']:.0f} |",
        f"| Bernoulli with p(V)=4/12, exact pattern | {nm['bernoulli_p_equal_observed_V_rate']['probability_exact_pattern']:.8f} | 1 in {nm['bernoulli_p_equal_observed_V_rate']['one_in']:.0f} |",
        "","## Look-elsewhere correction examples","",
        f"- There are {le['strict_descending_consecutive_hex_triplets']['count']} strict descending consecutive 3-hex-digit patterns out of 4096.",
        f"- Counting either ascending or descending consecutive triplets gives {le['ascending_or_descending_consecutive_hex_triplets']['count']} patterns out of 4096.",
        f"- Conditioned on four 1-bits, descending-triplet patterns occupy {le['descending_triplets_conditioned_on_four_ones']['count']} of {le['descending_triplets_conditioned_on_four_ones']['space']} sequences.",
        "","## Interpretation","",
        "The exact 321 pattern is uncommon under simple nulls and Stage 10 showed that the underlying H/V sequence is geometrically robust. That strengthens 321 as a lead.",
        "",
        "However, this is not a formal discovery p-value: the building segmentation, H/V coding, and recognition of a memorable hexadecimal pattern were not specified before looking at the image. A genuine second clue should independently point toward 3-2-1, ordering, countdown, selection, or a related semantic operation before 321 is treated as intentional.",
        ""
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-013","exact_uniform_one_in":nm["uniform_exact_321"]["one_in"],"conditional_one_in":nm["conditional_on_four_V_exact_positions"]["one_in"],"descending_family_count":len(desc)}))

if __name__=="__main__":
    main()
