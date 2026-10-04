#!/usr/bin/env python3
"""Stage 32: coarse 160-stripe known-answer probe using the public escrow address.

Safe scope: compare visible coarse image features against the already-public 160-bit
Ethereum address. No private-key generation, derivation, reconstruction, enumeration,
or wallet verification occurs.

Rationale:
- image width = 1600 px
- public address = 160 bits
- natural partition = 160 vertical cells x 10 px
- author said the public address is also included somewhere in the image
- Stage 31 strongly favors format-invariant visual structure over exact low bits
"""
from __future__ import annotations
import io, json, math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage32-public-address-stripes"
OUT.mkdir(parents=True,exist_ok=True)

ADDRESS_HEX="FF2142E98E09b5344994F9bEB9C56C95506B9F17"
TARGET=np.array([int(b) for h in ADDRESS_HEX.lower() for b in f"{int(h,16):04b}"],dtype=np.uint8)
K=int(TARGET.sum())
N_NULL=20000
CELL_W=10
BANDS={
    "full":(0,1105),
    "upper_skyline":(0,320),
    "boats_mid":(320,620),
    "lower_water":(620,1105),
}
FEATURES=("mean_darkness","ink250","ink220","ink180","vertical_change")

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

def feature_vector(gray,y0,y1,name):
    r=gray[y0:y1,:]
    cells=r.reshape(r.shape[0],160,CELL_W).transpose(1,0,2)  # 160 x H x 10
    if name=="mean_darkness":
        return 255.0-cells.mean(axis=(1,2))
    if name=="ink250":
        return (cells<250).mean(axis=(1,2))
    if name=="ink220":
        return (cells<220).mean(axis=(1,2))
    if name=="ink180":
        return (cells<180).mean(axis=(1,2))
    if name=="vertical_change":
        # visible vertical texture/edge activity inside each 10px stripe
        d=np.abs(np.diff(cells.astype(np.int16),axis=2))
        return d.mean(axis=(1,2))
    raise ValueError(name)

def topk_bits(v,k=K):
    # deterministic tie break by x index
    order=np.lexsort((np.arange(len(v)), -v))
    out=np.zeros(len(v),dtype=np.uint8)
    out[order[:k]]=1
    return out

def bottomk_bits(v,k=K):
    order=np.lexsort((np.arange(len(v)), v))
    out=np.zeros(len(v),dtype=np.uint8)
    out[order[:k]]=1
    return out

def ham(a,b):
    return int(np.sum(a!=b))

def target_conventions(t):
    # Only physically natural left-to-right / right-to-left reading.
    return {"left_to_right":t, "right_to_left":t[::-1]}

def candidate_family(gray):
    rows=[]
    for band,(y0,y1) in BANDS.items():
        for feature in FEATURES:
            v=feature_vector(gray,y0,y1,feature)
            for polarity,bits in (("high_is_1",topk_bits(v)),("low_is_1",bottomk_bits(v))):
                rows.append({
                    "band":band,
                    "feature":feature,
                    "polarity":polarity,
                    "bits":bits,
                    "feature_vector":v,
                })
    return rows

def evaluate(cands,target):
    convs=target_conventions(target)
    out=[]
    for c in cands:
        for direction,t in convs.items():
            d=ham(c["bits"],t)
            out.append({
                "band":c["band"],
                "feature":c["feature"],
                "polarity":c["polarity"],
                "direction":direction,
                "hamming":d,
                "matches":160-d,
                "match_fraction":(160-d)/160.0,
                "candidate_bits":"".join(map(str,c["bits"].tolist())),
            })
    return sorted(out,key=lambda x:(x["hamming"],x["band"],x["feature"],x["polarity"],x["direction"]))

def null_best_dist(cands,rng):
    # same target one-count, same family, same reading-direction look-elsewhere
    idx=rng.choice(160,size=K,replace=False)
    t=np.zeros(160,dtype=np.uint8)
    t[idx]=1
    return evaluate(cands,t)[0]["hamming"]

def main():
    original=load_gray()
    transformed=jpeg85_resample(original)

    c0=candidate_family(original)
    c1=candidate_family(transformed)
    e0=evaluate(c0,TARGET)
    e1=evaluate(c1,TARGET)

    # map transformed result by exact family key
    tmap={(x["band"],x["feature"],x["polarity"],x["direction"]):x for x in e1}
    for x in e0:
        k=(x["band"],x["feature"],x["polarity"],x["direction"])
        x["transformed_hamming"]=tmap[k]["hamming"]
        x["transformed_match_fraction"]=tmap[k]["match_fraction"]

    best=e0[0]
    best_key=(best["band"],best["feature"],best["polarity"],best["direction"])
    best_trans=tmap[best_key]

    rng=np.random.default_rng(3201)
    null=np.array([null_best_dist(c0,rng) for _ in range(N_NULL)],dtype=int)
    p=(1+int(np.sum(null<=best["hamming"])))/(N_NULL+1)

    # replicate requirement: same preselected family member remains within +4 bits after lossy transform
    replicated=(best_trans["hamming"]<=best["hamming"]+4)

    result={
        "experiment_id":"A11-EXP-032",
        "scope":"known public 160-bit address vs coarse visible 10px vertical-stripe features; no private-key operations",
        "address_hex":ADDRESS_HEX,
        "address_bits":160,
        "address_ones":K,
        "image_width":1600,
        "cell_width_px":CELL_W,
        "bands":BANDS,
        "features":list(FEATURES),
        "candidate_sequences":len(c0),
        "evaluated_with_directions":len(e0),
        "null_targets":N_NULL,
        "best_original":best,
        "same_family_after_jpeg85_resample":best_trans,
        "empirical_familywise_p":p,
        "null_best_hamming_median":float(np.median(null)),
        "null_best_hamming_p01":float(np.percentile(null,1)),
        "null_best_hamming_min":int(null.min()),
        "replicated_after_lossy_transform":bool(replicated),
        "promotion_rule":"promote only if familywise p < 0.01 AND the same family member reproduces within +4 Hamming bits after JPEG85+0.75x resampling roundtrip",
        "promoted":bool(p<0.01 and replicated),
        "top10":e0[:10],
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 32 — public-address coarse-stripe known-answer probe",
        "",
        "**Experiment:** A11-EXP-032",
        "",
        f"- Public address bits: **160**, ones: **{K}**",
        f"- Image width: **1600 px = 160 × 10 px**",
        f"- Predeclared candidate sequences: **{len(c0)}**; with two reading directions: **{len(e0)}**",
        f"- Same-balance null targets: **{N_NULL}**",
        "",
        "## Best result",
        "",
        f"- band: **{best['band']}**",
        f"- feature: **{best['feature']}**",
        f"- polarity: **{best['polarity']}**",
        f"- direction: **{best['direction']}**",
        f"- Hamming distance: **{best['hamming']}/160** ({best['matches']} matches)",
        f"- familywise empirical p: **{p:.6f}**",
        f"- same-family transformed Hamming: **{best_trans['hamming']}/160**",
        f"- lossy replication rule: **{replicated}**",
        f"- promotion rule satisfied: **{result['promoted']}**",
        "",
        "## Top candidates",
        "",
        "| rank | band | feature | polarity | direction | Hamming | lossy Hamming |",
        "|---:|:---|:---|:---|:---|---:|---:|",
    ]
    for i,x in enumerate(e0[:10],1):
        md.append(f"| {i} | {x['band']} | {x['feature']} | {x['polarity']} | {x['direction']} | {x['hamming']} | {x['transformed_hamming']} |")
    md += [
        "",
        "## Interpretation",
        "",
        "A positive result would identify a simple, format-robust visual mechanism that reproduces a known public value already stated by the author to be present in the image. A negative result retires only this exact 160 vertical × 10px family; it does not rule out other visual encodings of the public address.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-032",
        "best_hamming":best["hamming"],
        "transformed_hamming":best_trans["hamming"],
        "p":p,
        "promoted":result["promoted"],
    }))

if __name__=="__main__":
    main()
