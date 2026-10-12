#!/usr/bin/env python3
"""Stage 118: exact two-cell Braille audit of the 12-building H/V sequence.

Safe structural/semantic experiment only.

Observed stable sequence:
    HHVVHHVHHHHV

Stage 117 independently promoted visible-symbol reading + cross-domain conversion
as recurrent author-series operations. Twelve binary symbols fit exactly two
standard 6-dot Braille cells, so this stage tests only that one mapping family.

No private-key generation, derivation, reconstruction, enumeration,
verification, or wallet access is performed.
"""
from __future__ import annotations

import itertools
import json
from math import comb
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis"/"runs"/"stage118-two-cell-braille"
OUT.mkdir(parents=True,exist_ok=True)

SEQ="HHVVHHVHHHHV"

# Standard English Braille letters by raised-dot set.
LETTERS={
    "A":{1},"B":{1,2},"C":{1,4},"D":{1,4,5},"E":{1,5},
    "F":{1,2,4},"G":{1,2,4,5},"H":{1,2,5},"I":{2,4},"J":{2,4,5},
    "K":{1,3},"L":{1,2,3},"M":{1,3,4},"N":{1,3,4,5},"O":{1,3,5},
    "P":{1,2,3,4},"Q":{1,2,3,4,5},"R":{1,2,3,5},"S":{2,3,4},"T":{2,3,4,5},
    "U":{1,3,6},"V":{1,2,3,6},"W":{2,4,5,6},"X":{1,3,4,6},
    "Y":{1,3,4,5,6},"Z":{1,3,5,6},
}
DOTS_TO_LETTER={tuple(sorted(v)):k for k,v in LETTERS.items()}

READINGS=(
    ("ltr_H_raised",False,"H"),
    ("ltr_V_raised",False,"V"),
    ("rtl_H_raised",True,"H"),
    ("rtl_V_raised",True,"V"),
)

def decode_cell(cell,raised_symbol):
    dots={i+1 for i,ch in enumerate(cell) if ch==raised_symbol}
    return DOTS_TO_LETTER.get(tuple(sorted(dots)))

def decode(seq,reverse,raised_symbol):
    s=seq[::-1] if reverse else seq
    a=decode_cell(s[:6],raised_symbol)
    b=decode_cell(s[6:],raised_symbol)
    return {
        "cell1_dots":[i+1 for i,ch in enumerate(s[:6]) if ch==raised_symbol],
        "cell2_dots":[i+1 for i,ch in enumerate(s[6:]) if ch==raised_symbol],
        "cell1_letter":a,
        "cell2_letter":b,
        "both_letters":bool(a and b),
        "decoded_pair":(a or "?")+(b or "?"),
    }

def evaluate(seq):
    out={}
    any_two=False
    for name,rev,raised in READINGS:
        r=decode(seq,rev,raised)
        out[name]=r
        any_two=any_two or r["both_letters"]
    return out,any_two

def encode_pair(pair,raised_symbol="H"):
    # Standard dot numbering order 1..6; unraised is the other symbol.
    off="V" if raised_symbol=="H" else "H"
    s=""
    for ch in pair:
        dots=LETTERS[ch]
        s+="".join(raised_symbol if i in dots else off for i in range(1,7))
    return s

def main():
    # Synthetic positive control: encode/decode a fixed known pair.
    control_pair="AR"
    encoded=encode_pair(control_pair,"H")
    ctrl=decode(encoded,False,"H")
    control_pass=(ctrl["decoded_pair"]==control_pair and ctrl["both_letters"])

    observed,observed_any=evaluate(SEQ)

    # Count-matched exact null: observed has 8 H and 4 V.
    h_count=SEQ.count("H")
    null_total=0
    null_any=0
    for hpos in itertools.combinations(range(12),h_count):
        s=["V"]*12
        for i in hpos:
            s[i]="H"
        s="".join(s)
        _,ok=evaluate(s)
        null_total+=1
        null_any+=int(ok)

    p_familywise=(null_any/null_total) if null_total else 1.0
    promoted=bool(control_pass and observed_any and p_familywise<=0.05)

    result={
        "experiment_id":"A11-EXP-118",
        "scope":"exact standard-Braille 6+6 audit of fixed 12-building H/V sequence; no sliding windows or arbitrary code sweep",
        "sequence":SEQ,
        "symbol_counts":{"H":SEQ.count("H"),"V":SEQ.count("V")},
        "readings":observed,
        "positive_control":{
            "pair":control_pair,
            "encoded":encoded,
            "decoded":ctrl,
            "passed":control_pass,
        },
        "count_matched_null":{
            "total_sequences":null_total,
            "expected_total":comb(12,h_count),
            "sequences_with_any_two_letter_reading":null_any,
            "familywise_probability":p_familywise,
        },
        "any_two_letter_reading":observed_any,
        "promotion_rule":"positive control passes; at least one of exactly four standard direction/polarity readings yields two alphabetic Braille letters; count-matched familywise probability <=0.05",
        "promoted":promoted,
        "interpretation_guard":"A positive result would only support a standard two-cell Braille reading of the visible H/V sequence, not any secret/key derivation.",
        "safety_guard":"No secret candidate is generated, derived or verified.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 118 — exact two-cell Braille audit",
        "",
        "**Experiment:** A11-EXP-118",
        "",
        f"- sequence: **{SEQ}**",
        f"- positive control pass: **{control_pass}**",
        f"- any observed two-letter reading: **{observed_any}**",
        f"- count-matched familywise probability: **{p_familywise:.6f}** ({null_any}/{null_total})",
        f"- promoted: **{promoted}**",
        "",
        "| reading | cell 1 dots | cell 2 dots | decoded | both letters |",
        "|:---|:---|:---|:---:|:---:|",
    ]
    for name,r in observed.items():
        md.append(
            f"| {name} | {r['cell1_dots']} | {r['cell2_dots']} | "
            f"{r['decoded_pair']} | {r['both_letters']} |"
        )
    md += ["","## Interpretation",""]
    if promoted:
        md.append("The fixed H/V sequence supports an exceptional standard two-cell Braille reading under the predeclared mappings. This would justify a narrowly targeted semantic follow-up.")
    else:
        md.append("The fixed H/V sequence does not support an exceptional two-cell standard Braille reading. Retire Braille and do not expand this negative into arbitrary binary alphabets.")
    md += ["","No private-key material was generated or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))

    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-118",
        "control_pass":control_pass,
        "any_two_letters":observed_any,
        "familywise_p":p_familywise,
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
