#!/usr/bin/env python3
"""A11-EXP-161: synthetic-only audit of the Stage12 period-lag estimator.

Stage159's synthetic stripe-period12 fixture at width3 selected lag36, then
a width5 fixture selected lag12. The Stage12 score can exceed 1 because
its globally standardized autocovariance is divided by overlap length.
This fixture-only audit tests both already registered source-geometry masks,
without inspecting canonical source pixels or inferring any secret.
All gates preregistered in analysis/STAGE_QUEUE.md before this script.
"""
from __future__ import annotations
import hashlib,json,math
from collections import defaultdict
from pathlib import Path

import numpy as np

from stage12_count_perimeter import projection_periodicity
from stage112_corrected_sail_width_progression import variants
from stage157_corrected_sail_projection_provenance import build_mask as small_mask
from stage159_full_boat_projection_provenance import masks_and_box as large_mask

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
PRIOR157=ROOT/"analysis"/"runs"/"stage157-corrected-sail-projection"/"result.json"
PRIOR159=ROOT/"analysis"/"runs"/"stage159-full-boat-projection"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage161-projection-harmonic-audit"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
FORMATS=("original","jpeg85","jpeg70","down75_up")
THRESHOLDS=(110,140,170)
STRIPE_WIDTHS=(2,3,4,5)
PERIOD=12
MIN_DARK=200
MIN_PERIODS=8

def source_provenance_only():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA:raise RuntimeError("Original PNG checksum changed")
    s157=json.loads(PRIOR157.read_text())
    s159=json.loads(PRIOR159.read_text())
    ok=(
        s157.get("source_sha256")==SHA
        and s159.get("original_sha256")==SHA
        and s157.get("decision")=="SOURCE_LAG3_COMPATIBLE_WITH_SILHOUETTE"
        and s159.get("decision")=="SOURCE_LAG3_COMPATIBLE_WITH_FULL_BOAT_SILHOUETTE"
        and s157.get("synthetic_controls",{}).get("passed")==24
        and s159.get("controls",{}).get("passed")==24
    )
    return {"pass":bool(ok),"original_sha256":digest,
            "archived_stage157_decision":s157.get("decision"),
            "archived_stage159_decision":s159.get("decision")}

def masks():
    sm,sm_box=small_mask((1105,1600))
    lg,lg_box=large_mask((1105,1600))
    return {
       "true_five_small_sails":{"mask":sm,"bbox":sm_box},
       "true_large_sail_and_hull":{"mask":lg,"bbox":lg_box}
    }

def fixture(mask,kind):
    out=np.full(mask.shape,255,np.uint8)
    if kind=="filled":
        out[mask]=0
    else:
        w=int(kind.split("_")[-1])
        yy,xx=np.indices(mask.shape)
        out[mask & (xx%PERIOD<w)]=0
    return out

def occupied_periods(frame,mask):
    _,xx=np.nonzero((frame<110)&mask)
    return int(np.unique(xx//PERIOD).size)

def legacy_overlap_score(image,threshold,lag):
    series=(image<threshold).astype(float).sum(axis=0)
    n=len(series)
    if lag>=n or not n:return None
    sd=float(np.std(series))
    if sd<1e-12:return None
    q=(series-np.mean(series))/(sd+1e-12)
    return float(np.dot(q[:n-lag],q[lag:])/(n-lag)) if lag else float(np.dot(q,q)/n)

def bounded_pearson_score(image,threshold,lag):
    series=(image<threshold).astype(float).sum(axis=0)
    if lag>=len(series):return None
    x,y=series[:-lag],series[lag:]
    if len(x)<3 or float(np.std(x))<1e-10 or float(np.std(y))<1e-10:
        return None
    return float(np.corrcoef(x,y)[0,1])

def main():
    provenance=source_provenance_only()
    allmasks=masks()
    records=[]
    for site,m in allmasks.items():
        shape_mask=m["mask"]
        for kind in ("filled",)+tuple(f"stripe_width_{w}" for w in STRIPE_WIDTHS):
            original=fixture(shape_mask,kind)
            if kind=="filled":
                needed_periods=None
            else:
                needed_periods=occupied_periods(original,shape_mask)
            for fmt,frame in variants(original).items():
                if fmt not in FORMATS:continue
                for t in THRESHOLDS:
                    pix=int(np.count_nonzero((frame<t)&shape_mask))
                    reading=projection_periodicity(frame,t)["x"]
                    lag=reading["best_lag"]
                    curr=float(reading["score"])
                    sample={
                        "site":site,"kind":kind,"format":fmt,"threshold":t,
                        "mask_area":int(shape_mask.sum()),
                        "dark_pixels":pix,"occupied_distinct_periods":needed_periods,
                        "legacy_best_lag":lag,"legacy_best_score":round(curr,9),
                        "legacy_lag12_score":round(legacy_overlap_score(frame,t,12),9),
                        "bounded_two_window_pearson_lag12":None
                    }
                    pc=bounded_pearson_score(frame,t,12)
                    if pc is not None:sample["bounded_two_window_pearson_lag12"]=round(pc,9)
                    sample["fixture_integrity"]=bool(
                        pix>=MIN_DARK
                        and (kind=="filled" or needed_periods>=MIN_PERIODS)
                    )
                    records.append(sample)
    if len(records)!=120:raise RuntimeError(f"Fixture count changed {len(records)}")
    flat=[x for x in records if x["kind"]=="filled"]
    period=[x for x in records if x["kind"]!="filled"]
    gate={
       "source_provenance":provenance,
       "total_fixtures":len(records),
       "expected_fixtures":120,
       "fixture_integrity_passed":sum(x["fixture_integrity"] for x in records),
       "flat_lag3_passed":sum(x["legacy_best_lag"]==3 for x in flat),
       "flat_total":len(flat),
       "pass":bool(provenance["pass"] and all(x["fixture_integrity"] for x in records)
                  and len(flat)==24 and all(x["legacy_best_lag"]==3 for x in flat))
    }
    harmonics=[x for x in period if x["legacy_best_lag"] is not None
               and x["legacy_best_lag"]%PERIOD==0
               and x["legacy_best_lag"]>=2*PERIOD]
    fundamental=[x for x in period if x["legacy_best_lag"]==PERIOD]
    outside=[x for x in period if x not in harmonics and x not in fundamental]
    scores_above1=[x for x in records if x["legacy_best_score"]>1+1e-7]
    if not gate["pass"]:
        decision="CONTROL_FAILURE"
    elif harmonics:
        decision="HARMONIC_FUNDAMENTAL_NONIDENTIFIABILITY_CONFIRMED"
    elif len(fundamental)==len(period)==96:
        decision="PERIOD12_FUNDAMENTAL_RECOVERED_IN_FIXED_FIXTURES"
    else:
        decision="PERIOD12_ESTIMATOR_UNRELIABLE_IN_FIXED_FIXTURES"
    by_kind={}
    for name in ("filled",)+tuple(f"stripe_width_{w}" for w in STRIPE_WIDTHS):
        z=[r for r in records if r["kind"]==name]
        hist={}
        for r in z:
            k=str(r["legacy_best_lag"])
            hist[k]=hist.get(k,0)+1
        by_kind[name]={"total":len(z),"best_lag_histogram":hist,
                       "above_1_scores":sum(x["legacy_best_score"]>1+1e-7 for x in z)}
    result={
       "experiment_id":"A11-EXP-161",
       "research_scope":"synthetic-only Stage12 detector audit after Stage159 known period12->lag36",
       "canonical_source_pixels_used":False,
       "only_source_metadata_verified":provenance,
       "fixed_masks":{k:{"fixed_crop_bbox":list(v["bbox"]),"pixels_in_mask":int(v["mask"].sum())}
                      for k,v in allmasks.items()},
       "fixed_case_design":{"sites":list(allmasks),"formats":FORMATS,"thresholds":THRESHOLDS,
                            "stripe_period":PERIOD,"stripe_widths":STRIPE_WIDTHS,
                            "minimum_dark_pixels":MIN_DARK,"minimum_occupied_periods":MIN_PERIODS},
       "controls":gate,
       "total_periodic_cases":len(period),
       "fundamental_lag12_cases":len(fundamental),
       "harmonic_lag24_or_more_cases":len(harmonics),
       "non_period_multiple_cases":len(outside),
       "any_stage12_score_gt1":bool(scores_above1),
       "above_one_scores_count":len(scores_above1),
       "by_fixture_kind":by_kind,
       "samples":records,
       "decision":decision,
       "interpretation_limit":"The old Stage12 overlap-normalized statistic may select a valid higher harmonic of a fundamental period and can exceed one. This is a synthetic method audit only, not new original-image evidence; lag3 on real and filled silhouette remains a short-lag shape comparison, not a code.",
       "safety":"No key, BIP39, wallet/address comparison or off-image research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    report=[
      "# Stage161 — synthetic-only audit of Stage12 projection harmonics","",
      f"- Original source SHA provenance (no real pixels measured): **{provenance['pass']}**",
      f"- Synthetic fixture integrity: **{gate['fixture_integrity_passed']}/120**",
      f"- Flat-shape expected x lag3: **{gate['flat_lag3_passed']}/24**",
      f"- Period12 stripe cases best x-lag exactly12: **{len(fundamental)}/96**",
      f"- Period12 stripe cases best x-lag 24/36/etc (valid higher harmonics): **{len(harmonics)}/96**",
      f"- Period12 stripe cases whose best lag is NOT a multiple of12: **{len(outside)}/96**",
      f"- Stage12 normalized scores greater than 1: **{len(scores_above1)}/120**",
      f"- Decision: **{decision}**","",
      "| Synthetic family | Cases | Best-lag histogram | Scores over 1 |",
      "|---|---:|---|---:|"]
    for name,r in by_kind.items():
        report.append(f"| {name} | {r['total']} | {r['best_lag_histogram']} | {r['above_1_scores']} |")
    report+=["","The old Stage12 method is a globally standardized overlap-normalized autocovariance, NOT a bounded Pearson correlation at each lag. A source with period12 may have strong higher harmonics, making an unqualified best-lag-as-fundamental reading unreliable. Source pixel interpretation is NOT updated by this synthetic-only calibration.",
       "","No new message, key or intentionally coded source feature established.",""]
    (OUT/"REPORT.md").write_text("\n".join(report))
    print(json.dumps({"stage":161,"control_pass":gate["pass"],
       "period12_lag12":len(fundamental),"harmonic":len(harmonics),
       "outside_period_family":len(outside),"score_above1":len(scores_above1),
       "decision":decision}))
if __name__=="__main__":
    main()
