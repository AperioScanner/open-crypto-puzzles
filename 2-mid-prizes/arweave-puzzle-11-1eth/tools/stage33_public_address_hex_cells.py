#!/usr/bin/env python3
"""Stage 33: 40-hex-digit coarse-cell known-answer probe.

Safe scope: compare coarse visible image features against the already-public
40-hex-digit Ethereum escrow address. No private-key generation, derivation,
reconstruction, enumeration, or wallet verification occurs.

Motivation:
- source width = 1600 px
- published address = 40 hexadecimal digits
- exact partition = 40 vertical cells x 40 px
- Stage 31 favors format-invariant visual features
"""
from __future__ import annotations
import io, json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage33-public-address-hex-cells"
OUT.mkdir(parents=True,exist_ok=True)

ADDRESS_HEX="FF2142E98E09b5344994F9bEB9C56C95506B9F17".lower()
TARGET=np.array([int(c,16) for c in ADDRESS_HEX],dtype=np.uint8)
CELL_W=40
N_NULL=10000

BANDS={
    "full":(0,1105),
    "upper_skyline":(0,320),
    "boats_mid":(320,620),
    "lower_water":(620,1105),
}
FEATURES=(
    "mean_darkness",
    "ink250",
    "ink220",
    "ink180",
    "vertical_change",
    "horizontal_change",
)
QUANTIZERS=("minmax16","rank16")

BITCOUNT=np.array([bin(i).count("1") for i in range(16)],dtype=np.uint8)

def load_gray():
    a=np.array(Image.open(SOURCE).convert("L"))
    if a.shape!=(1105,1600):
        raise SystemExit(f"unexpected image shape {a.shape}")
    return a

def jpeg85_resample(gray):
    im=Image.fromarray(gray,mode="L")
    buf=io.BytesIO()
    im.save(buf,format="JPEG",quality=85,optimize=False,progressive=False)
    buf.seek(0)
    j=Image.open(buf).convert("L")
    small=j.resize((1200,829),Image.Resampling.LANCZOS)
    back=small.resize((1600,1105),Image.Resampling.LANCZOS)
    return np.array(back)

def cells(gray,y0,y1):
    r=gray[y0:y1,:]
    return r.reshape(r.shape[0],40,CELL_W).transpose(1,0,2)

def feature_vector(gray,y0,y1,name):
    c=cells(gray,y0,y1).astype(np.int16)
    if name=="mean_darkness":
        return 255.0-c.mean(axis=(1,2))
    if name=="ink250":
        return (c<250).mean(axis=(1,2))
    if name=="ink220":
        return (c<220).mean(axis=(1,2))
    if name=="ink180":
        return (c<180).mean(axis=(1,2))
    if name=="vertical_change":
        return np.abs(np.diff(c,axis=2)).mean(axis=(1,2))
    if name=="horizontal_change":
        return np.abs(np.diff(c,axis=1)).mean(axis=(1,2))
    raise ValueError(name)

def quantize(v,method):
    v=np.asarray(v,dtype=float)
    if method=="minmax16":
        lo=float(v.min()); hi=float(v.max())
        if hi<=lo:
            return np.zeros(len(v),dtype=np.uint8)
        q=np.rint((v-lo)/(hi-lo)*15.0)
        return np.clip(q,0,15).astype(np.uint8)
    if method=="rank16":
        # stable ranks with x-index tie break; 40 ranks mapped to 16 ordinal bins.
        order=np.lexsort((np.arange(len(v)),v))
        ranks=np.empty(len(v),dtype=int)
        ranks[order]=np.arange(len(v))
        return np.floor(ranks*16/len(v)).astype(np.uint8)
    raise ValueError(method)

def make_candidates(gray):
    out=[]
    for band,(y0,y1) in BANDS.items():
        for feat in FEATURES:
            v=feature_vector(gray,y0,y1,feat)
            for quant in QUANTIZERS:
                q=quantize(v,quant)
                for polarity in ("direct","inverted"):
                    seq=q if polarity=="direct" else (15-q)
                    out.append({
                        "band":band,
                        "feature":feat,
                        "quantizer":quant,
                        "polarity":polarity,
                        "sequence":seq.astype(np.uint8),
                    })
    return out

def candidate_key(c,direction):
    return (c["band"],c["feature"],c["quantizer"],c["polarity"],direction)

def evaluate(cands,target):
    rows=[]
    for c in cands:
        for direction in ("left_to_right","right_to_left"):
            s=c["sequence"] if direction=="left_to_right" else c["sequence"][::-1]
            exact=int(np.sum(s==target))
            bit_h=int(BITCOUNT[np.bitwise_xor(s,target)].sum())
            rows.append({
                "band":c["band"],
                "feature":c["feature"],
                "quantizer":c["quantizer"],
                "polarity":c["polarity"],
                "direction":direction,
                "exact_digit_matches":exact,
                "digit_mismatches":40-exact,
                "nibble_bit_hamming":bit_h,
                "sequence_hex":"".join(format(int(x),"x") for x in s),
            })
    rows.sort(key=lambda x:(-x["exact_digit_matches"],x["nibble_bit_hamming"],x["band"],x["feature"],x["quantizer"],x["polarity"],x["direction"]))
    return rows

def main():
    original=load_gray()
    transformed=jpeg85_resample(original)
    c0=make_candidates(original)
    c1=make_candidates(transformed)
    e0=evaluate(c0,TARGET)
    e1=evaluate(c1,TARGET)

    tmap={(x["band"],x["feature"],x["quantizer"],x["polarity"],x["direction"]):x for x in e1}
    cmap={}
    for c in c1:
        cmap[(c["band"],c["feature"],c["quantizer"],c["polarity"])]=c["sequence"]

    # attach transformed target metrics and same-family self stability
    orig_cfg_map={(c["band"],c["feature"],c["quantizer"],c["polarity"]):c["sequence"] for c in c0}
    for x in e0:
        k=(x["band"],x["feature"],x["quantizer"],x["polarity"],x["direction"])
        tx=tmap[k]
        x["transformed_exact_digit_matches"]=tx["exact_digit_matches"]
        x["transformed_nibble_bit_hamming"]=tx["nibble_bit_hamming"]
        base=(x["band"],x["feature"],x["quantizer"],x["polarity"])
        a=orig_cfg_map[base]
        b=cmap[base]
        if x["direction"]=="right_to_left":
            a=a[::-1]; b=b[::-1]
        x["self_stable_digits"]=int(np.sum(a==b))

    best=e0[0]

    # Familywise null: preserve the exact public-address digit multiset by permutation.
    # This tests whether any candidate in the predeclared family matches the *ordering*
    # unusually well, rather than benefiting from address digit frequencies.
    cand_matrix=[]
    for c in c0:
        for direction in ("left_to_right","right_to_left"):
            s=c["sequence"] if direction=="left_to_right" else c["sequence"][::-1]
            cand_matrix.append(s)
    M=np.stack(cand_matrix,axis=0)

    rng=np.random.default_rng(3301)
    null_best_exact=np.empty(N_NULL,dtype=np.int16)
    null_best_bith=np.empty(N_NULL,dtype=np.int16)
    for i in range(N_NULL):
        t=rng.permutation(TARGET)
        exact=np.sum(M==t[None,:],axis=1)
        xor=np.bitwise_xor(M,t[None,:])
        bith=BITCOUNT[xor].sum(axis=1)
        null_best_exact[i]=int(exact.max())
        null_best_bith[i]=int(bith.min())

    p_exact=(1+int(np.sum(null_best_exact>=best["exact_digit_matches"])))/(N_NULL+1)
    p_bith=(1+int(np.sum(null_best_bith<=best["nibble_bit_hamming"])))/(N_NULL+1)

    lossy_target_ok=best["transformed_exact_digit_matches"]>=best["exact_digit_matches"]-2
    self_stable=best["self_stable_digits"]>=34
    promoted=bool(p_exact<0.01 and p_bith<0.01 and lossy_target_ok and self_stable)

    result={
        "experiment_id":"A11-EXP-033",
        "scope":"known public 40-hex-digit address vs coarse visible 40px cells; no private-key operations",
        "address_hex":ADDRESS_HEX,
        "image_width":1600,
        "hex_digits":40,
        "cell_width_px":CELL_W,
        "bands":BANDS,
        "features":list(FEATURES),
        "quantizers":list(QUANTIZERS),
        "candidate_sequences":len(c0),
        "evaluated_with_directions":len(e0),
        "null_permutations":N_NULL,
        "best_original":best,
        "familywise_empirical_p":{
            "exact_digit_matches_upper":p_exact,
            "nibble_bit_hamming_lower":p_bith,
        },
        "null_summary":{
            "best_exact_median":float(np.median(null_best_exact)),
            "best_exact_p99":float(np.percentile(null_best_exact,99)),
            "best_exact_max":int(null_best_exact.max()),
            "best_bith_median":float(np.median(null_best_bith)),
            "best_bith_p01":float(np.percentile(null_best_bith,1)),
            "best_bith_min":int(null_best_bith.min()),
        },
        "lossy_target_replication_ok":bool(lossy_target_ok),
        "same_family_self_stable":bool(self_stable),
        "promotion_rule":"p_exact<0.01 AND p_bit_hamming<0.01 AND transformed target matches within 2 digits of original AND >=34/40 extracted digits remain identical after JPEG85+resampling",
        "promoted":promoted,
        "top10":e0[:10],
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 33 — public-address 40×40px hex-cell probe",
        "",
        "**Experiment:** A11-EXP-033",
        "",
        f"- Image width: **1600 px = 40 hex digits × 40 px**",
        f"- Candidate sequences: **{len(c0)}**, evaluated with directions: **{len(e0)}**",
        f"- Null permutations preserving address digit multiset: **{N_NULL}**",
        "",
        "## Best result",
        "",
        f"- band: **{best['band']}**",
        f"- feature: **{best['feature']}**",
        f"- quantizer: **{best['quantizer']}**",
        f"- polarity: **{best['polarity']}**",
        f"- direction: **{best['direction']}**",
        f"- exact hex-digit matches: **{best['exact_digit_matches']}/40**",
        f"- nibble-bit Hamming: **{best['nibble_bit_hamming']}/160**",
        f"- familywise p(exact): **{p_exact:.6f}**",
        f"- familywise p(bit-Hamming): **{p_bith:.6f}**",
        f"- transformed exact matches: **{best['transformed_exact_digit_matches']}/40**",
        f"- same-family extracted digits stable after lossy transform: **{best['self_stable_digits']}/40**",
        f"- promotion rule: **{promoted}**",
        "",
        "## Top candidates",
        "",
        "| rank | band | feature | quantizer | polarity | direction | exact | bit-H | lossy exact | stable |",
        "|---:|:---|:---|:---|:---|:---|---:|---:|---:|---:|",
    ]
    for i,x in enumerate(e0[:10],1):
        md.append(f"| {i} | {x['band']} | {x['feature']} | {x['quantizer']} | {x['polarity']} | {x['direction']} | {x['exact_digit_matches']} | {x['nibble_bit_hamming']} | {x['transformed_exact_digit_matches']} | {x['self_stable_digits']} |")
    md += [
        "",
        "## Interpretation",
        "",
        "A positive result would identify a coarse format-robust mapping to the already-public address. A negative result retires only the exact 40 vertical × 40px hex-cell family; it does not rule out object-based, symbolic, textual, or other semantic encodings of the public address.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-033",
        "exact":best["exact_digit_matches"],
        "bit_hamming":best["nibble_bit_hamming"],
        "p_exact":p_exact,
        "p_bith":p_bith,
        "stable":best["self_stable_digits"],
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
