#!/usr/bin/env python3
"""A11-EXP-174: Stage126 corrected true-ABOVE-tip masthead ink measurement.

Stage173 proved Stage126 calibrated above synthetic tip at top+24, but
measured below original true tip top. Rather than changing any ink/edge
classifier, shift its input virtual site top by exactly -24 in BOTH original
and synthetic cases, so its existing y top+3..top+17 is really 21..6 px
ABOVE source tip, matching synthetic wedge tip. Full original Stage126
calibration 180/180 mandatory before reading any actual source ink.
This tests above-tip VERTICAL INK only, not proven mast attachment or code.
"""
import hashlib,json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from stage112_corrected_sail_width_progression import variants
from stage126_masthead_protrusion import (
    SITES,FORMATS,X_JITTER,T0,T1,INK_CUTOFF,
    BIN_MIN_ROWS,EDGE_MIN_ROWS,MIN_CONTIGUOUS,ABSENCE_MAX_ROWS,
    inspect,synthetic)
from stage153_under_pier_triangle_junctions import TRIANGLES

ROOT=Path(__file__).resolve().parents[1]
PNG=ROOT/"clues"/"arweave-puzzle-11.png"
STAGE126=ROOT/"analysis"/"runs"/"stage126-masthead-protrusion"/"result.json"
STAGE173=ROOT/"analysis"/"runs"/"stage173-masthead-apex-frame"/"result.json"
OUT=ROOT/"analysis"/"runs"/"stage174-true-apex-masthead"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
SHIFT=-24
EXPECTED=[448,433,411,397,357]

def real_frame(site):
    name,x,top,height,half=site
    return (name,x,top+SHIFT,height,half)

def calibration(sites):
    rows=[]
    for old_site,fixed in zip(SITES,sites):
        for kind in ("extension","absent","side_decoy"):
            truth="EXTENDED" if kind=="extension" else "ABSENT"
            frames=variants(synthetic(fixed,kind))
            for fmt in FORMATS:
                for dx in X_JITTER:
                    result=inspect(frames[fmt],fixed,dx)
                    rows.append({"site":old_site[0],"synthetic":kind,"format":fmt,
                         "x_jitter":dx,"expected":truth,
                         "measured":result["classification"],
                         "pass":result["classification"]==truth})
    return {"passed":sum(z["pass"] for z in rows),"cases":len(rows),
            "pass":len(rows)==180 and all(z["pass"] for z in rows),
            "failures":[z for z in rows if not z["pass"]]}

def main():
    sha=hashlib.sha256(PNG.read_bytes()).hexdigest()
    prior126=json.loads(STAGE126.read_text())
    prior173=json.loads(STAGE173.read_text())
    fixed=[real_frame(s) for s in SITES]
    guards={
        "original_SHA":sha==SHA,
        "Stage173_source_frame_defect_verified":
           prior173["decision"]=="CONFIRMED_STAGE126_SOURCE_SYNTHETIC_APEX_FRAME_MISMATCH",
        "Stage173_structural_12":prior173["controls_passed"]==prior173["controls_total"]==12,
        "Stage126_180_historical_calibration":prior126["controls"]["passed"] and prior126["controls"]["passes"]==180,
        "all_five_apex_locations_match":all(
           (x,top)==TRIANGLES["sail"+str(i+1)][0]
           for i,(name,x,top,height,half) in enumerate(SITES)),
        "all_15_rows_above_true_apex":all(
           fixed[i][2]+T0 < fixed[i][2]+T1 <= SITES[i][2]
           for i in range(5)),
        "fixed_shift_24px":all(f[2]==s[2]-24 for f,s in zip(fixed,SITES)),
        "unchanged_old_five_stroke_gates":(T0,T1,INK_CUTOFF,BIN_MIN_ROWS,EDGE_MIN_ROWS,MIN_CONTIGUOUS,ABSENCE_MAX_ROWS)==(3,18,175,10,9,8,3),
        "original_x_jitter_three":tuple(X_JITTER)==(-2,0,2),
    }
    controls=calibration(fixed)
    if all(guards.values()) and controls["pass"]:
        original=np.asarray(Image.open(PNG).convert("L"))
        if original.shape!=(1105,1600):raise RuntimeError("Canonical dimensions changed")
        ff=variants(original)
        observed=[]
        for i,(unshifted,s) in enumerate(zip(SITES,fixed)):
            rr=[]
            for fmt in FORMATS:
                for dx in X_JITTER:
                    v=inspect(ff[fmt],s,dx)
                    rr.append({"format":fmt,"dx":dx,**v})
            classes=[x["classification"] for x in rr]
            stable=classes[0] if len(set(classes))==1 and classes[0]!="?" else None
            observed.append({"original_site":unshifted,"corrected_virtual_site":s,
                "source_window_y":[s[2]+T0,s[2]+T1],
                "stable_label":stable,"measurements":rr})
        stable=[v["stable_label"] for v in observed if v["stable_label"]]
        mixed=len(stable)>=4 and len(set(stable))==2
        uniform=len(stable)>=4 and len(set(stable))==1
        if mixed:decision="MIXED_TRUE_APEX_UPPER_MARKS_REQUIRE_MANUAL_REVIEW"
        elif uniform:decision="UNIFORM_TRUE_APEX_UPPER_INK_STATE"
        else:decision="INCONCLUSIVE_TRUE_APEX_MASTHEAD_COVERAGE"
        # Raw copy contact, fixed same 5 centers & original y ranges,
        # highlighting the ABOVE-apex region in separate guide copies.
        sheet=np.full((5*135,2*230,3),255,np.uint8)
        for i,row in enumerate(observed):
            _,x,top,h,half=SITES[i]
            x0,x1=x-35,x+36
            y0,y1=top-36,top+6
            raw=original[y0:y1,x0:x1]
            rawrgb=cv2.cvtColor(raw,cv2.COLOR_GRAY2BGR)
            annotation=rawrgb.copy()
            cv2.rectangle(annotation,(35-5,15),(35+5,30),(0,0,210),1)
            rawbig=cv2.resize(rawrgb,(213,126),interpolation=cv2.INTER_NEAREST)
            annbig=cv2.resize(annotation,(213,126),interpolation=cv2.INTER_NEAREST)
            sheet[i*135:i*135+126,:213]=rawbig
            sheet[i*135:i*135+126,230:443]=annbig
        cv2.imwrite(str(OUT/"five-apex-source-window-crops.png"),sheet)
    else:
        observed=[]
        stable=[];mixed=False;uniform=False
        decision="CONTROL_FAILURE"
    result={
      "experiment_id":"A11-EXP-174","source_SHA256":sha,
      "source_defect":"Stage173 shows old Stage126 original windows below actual tips while its synthetic windows were above artificially shifted tips.",
      "correction":"Pass virtual site top = source original top-24 to unchanged Stage126 inspect and synthetic functions, aligning synthetic and actual apex at same y",
      "true_original_apex_y":[s[2] for s in SITES],
      "source_frame_guards":guards,"source_guards_passed":sum(guards.values()),
      "source_guards_total":len(guards),
      "reframed_synthetic_controls":controls,
      "real_source_above_apex":observed,"stable_sites":len(stable),
      "mixed_known_states":mixed,"uniform_known_states":uniform,
      "decision":decision,
      "scope_limit":"Centered ink above apex may be unrelated/disconnected pencil marks; stable EXTENDED means only Stage126's fixed vertical-ink/edge rule, not physically connected mast extension or code.",
      "safety":"Image only; no private-key, mnemonic, address, wallet or social/outside research."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Stage174 — actual ABOVE-tip pencil/masthead ink on five true sails","",
       f"- Source SHA correct: **{sha==SHA}**",
       f"- Original/Synthetic apex coordinate guards: **{sum(guards.values())}/{len(guards)}**",
       f"- Original Stage126 positive/absent/side-decoy reframe controls: **{controls['passed']}/{controls['cases']}**",
       f"- Stable SOURCE above-tip ink classifications: **{len(stable)}/5**",
       f"- Two distinct stable states: **{mixed}**",
       f"- Decision: **{decision}**","",
       "| True sail | Source true tip y | Fixed ABOVE-tip y interval | Stable above-tip ink |",
       "|---|---:|---|---|"]
    for i,s in enumerate(SITES):
        z=observed[i] if observed else None
        lines.append(f"| sail{i+1} | {s[2]} | {[s[2]-21,s[2]-6]} | {(z['stable_label'] if z else None) or '?'} |")
    lines+=["","This corrects a source-frame BUG in Stage126 but does not itself prove any line is a physically attached masthead. Compare the raw unannotated left vs guided right crops before claiming intent or patterned markers. If source states are unstable, do not interpret as all absent.","",
            "No key, mnemonic, address or wallet search.",""]
    (OUT/"REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"stage":174,"controls":f"{controls['passed']}/{controls['cases']}",
       "site_labels":[(i+1,v["stable_label"]) for i,v in enumerate(observed)],
       "decision":decision}))
if __name__=="__main__":
    main()
