#!/usr/bin/env python3
"""Stage 94: large-sail stroke-orientation carrier-capacity audit.

Safe scope: tests whether the visible large sail contains a robust discrete
stroke-orientation carrier compatible with 64 visible hex symbols or 256 binary
symbols. It measures only counts, orientation-class balance/separation, and
cross-format robustness. It never persists or prints the target sail's ordered
orientation sequence and performs no private-key operations.
"""
from __future__ import annotations
import io, json, math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage94-large-sail-stroke-carrier"
OUT.mkdir(parents=True,exist_ok=True)

THRESHOLDS=(110,135,160,185,210)
TARGET_COUNTS=((64,8),(256,16))

def load_gray():
    a=np.array(Image.open(SOURCE).convert("L"))
    if a.shape!=(1105,1600):
        raise SystemExit(f"unexpected image shape {a.shape}")
    return a

def variants(gray):
    out={"original":gray}
    for q in (85,70):
        b=io.BytesIO()
        Image.fromarray(gray).save(b,format="JPEG",quality=q,optimize=False,progressive=False)
        b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("L"))
    small=Image.fromarray(gray).resize((1200,829),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(small.resize((1600,1105),Image.Resampling.LANCZOS))
    return out

def sail_roi(gray):
    g=json.loads(GEOM.read_text())
    b=g["large_sailboat"]
    x0,y0,x1,y1=map(int,(b["x0"],b["y0"],b["x1"],b["y1"]))
    # Exclude the hull: keep the upper 74% of the measured boat box.
    ys=y0
    ye=y0+int(round((y1-y0)*0.74))
    c=gray[ys:ye,x0:x1]
    h,w=c.shape
    mask=np.zeros((h,w),np.uint8)
    pts=np.array([
        [int(round(0.48*w)),6],
        [8,h-5],
        [w-8,h-5],
    ],np.int32)
    cv2.fillConvexPoly(mask,pts,1)
    return c,mask,{"box":[x0,ys,x1,ye],"triangle":pts.tolist()}

def skeletonize(binary):
    img=(binary>0).astype(np.uint8)*255
    skel=np.zeros_like(img)
    element=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    while True:
        eroded=cv2.erode(img,element)
        opened=cv2.dilate(eroded,element)
        temp=cv2.subtract(img,opened)
        skel=cv2.bitwise_or(skel,temp)
        img=eroded
        if cv2.countNonZero(img)==0:
            break
    return skel

def angle_norm(x1,y1,x2,y2):
    a=math.degrees(math.atan2(y2-y1,x2-x1))
    while a>90: a-=180
    while a<=-90: a+=180
    return float(a)

def angle_diff(a,b):
    d=abs(a-b)
    return min(d,180-d)

def detect_segments(c,mask,thr):
    bw=((c<thr)&(mask>0)).astype(np.uint8)*255
    # Very small close joins pencil fragments but does not merge neighboring strokes.
    bw=cv2.morphologyEx(bw,cv2.MORPH_CLOSE,np.ones((2,2),np.uint8),iterations=1)
    sk=skeletonize(bw)
    raw=cv2.HoughLinesP(sk,1,np.pi/180,threshold=10,minLineLength=12,maxLineGap=4)
    segs=[]
    if raw is None:
        return segs
    for z in np.asarray(raw).reshape(-1,4):
        x1,y1,x2,y2=map(float,z)
        ln=math.hypot(x2-x1,y2-y1)
        if ln<12: continue
        mx=(x1+x2)/2; my=(y1+y2)/2
        xi=min(mask.shape[1]-1,max(0,int(round(mx))))
        yi=min(mask.shape[0]-1,max(0,int(round(my))))
        if mask[yi,xi]==0: continue
        segs.append({
            "mx":float(mx),"my":float(my),"length":float(ln),
            "angle":angle_norm(x1,y1,x2,y2),
        })
    # Deduplicate multiple Hough fragments describing the same centerline.
    keep=[]
    for s in sorted(segs,key=lambda x:x["length"],reverse=True):
        if any(
            math.hypot(s["mx"]-k["mx"],s["my"]-k["my"])<=9
            and angle_diff(s["angle"],k["angle"])<=8
            for k in keep
        ):
            continue
        keep.append(s)
    return keep

def track_across_thresholds(c,mask):
    clusters=[]
    for ti,thr in enumerate(THRESHOLDS):
        segs=detect_segments(c,mask,thr)
        for s in segs:
            best=None; bd=None
            for cl in clusters:
                # Only one observation per threshold per track.
                if ti in cl["threshold_ids"]: continue
                mx=np.median([x["mx"] for x in cl["items"]])
                my=np.median([x["my"] for x in cl["items"]])
                an=np.median([x["angle"] for x in cl["items"]])
                d=math.hypot(s["mx"]-mx,s["my"]-my)
                ad=angle_diff(s["angle"],an)
                score=d+1.5*ad
                if d<=14 and ad<=11 and (bd is None or score<bd):
                    best=cl; bd=score
            if best is None:
                best={"items":[],"threshold_ids":set()}
                clusters.append(best)
            best["items"].append(s)
            best["threshold_ids"].add(ti)
    tracks=[]
    for cl in clusters:
        if len(cl["threshold_ids"])<3: continue
        items=cl["items"]
        tracks.append({
            "support":len(cl["threshold_ids"]),
            "mx":float(np.median([x["mx"] for x in items])),
            "my":float(np.median([x["my"] for x in items])),
            "length":float(np.median([x["length"] for x in items])),
            "angle":float(np.median([x["angle"] for x in items])),
        })
    # Final dedupe after threshold tracking.
    out=[]
    for s in sorted(tracks,key=lambda x:(-x["support"],-x["length"])):
        if any(
            math.hypot(s["mx"]-k["mx"],s["my"]-k["my"])<=10
            and angle_diff(s["angle"],k["angle"])<=9
            for k in out
        ):
            continue
        out.append(s)
    return out

def summarize(tracks):
    # Binary-capable strokes are slanted enough to have a stable sign but are
    # not nearly horizontal. Near-perfect verticals are excluded because their
    # sign is numerically unstable under tiny perturbations.
    cls=[t for t in tracks if 18<=abs(t["angle"])<=86]
    pos=[t for t in cls if t["angle"]>0]
    neg=[t for t in cls if t["angle"]<0]
    n=len(cls)
    balance=float(min(len(pos),len(neg))/n) if n else 0.0
    if pos and neg:
        sep=float(abs(np.median([x["angle"] for x in pos])-np.median([x["angle"] for x in neg])))
    else:
        sep=0.0
    nearest=min(
        ({"target":target,"delta":abs(n-target),"tolerance":tol} for target,tol in TARGET_COUNTS),
        key=lambda x:x["delta"]
    )
    return {
        "stable_tracks":len(tracks),
        "classifiable_tracks":n,
        "positive_orientation_tracks":len(pos),
        "negative_orientation_tracks":len(neg),
        "minority_fraction":balance,
        "orientation_median_separation_deg":sep,
        "nearest_target_count":nearest,
    }

def cross_agreement(base,other):
    base=[t for t in base if 18<=abs(t["angle"])<=86]
    oth=[t for t in other if 18<=abs(t["angle"])<=86]
    if not base: return {"matched_fraction":0.0,"same_sign_fraction":0.0,"matched":0}
    used=set(); matched=0; same=0
    for a in base:
        best=None; bs=None
        for j,b in enumerate(oth):
            if j in used: continue
            d=math.hypot(a["mx"]-b["mx"],a["my"]-b["my"])
            ad=angle_diff(a["angle"],b["angle"])
            score=d+1.2*ad
            if d<=16 and ad<=14 and (bs is None or score<bs):
                best=j; bs=score
        if best is not None:
            used.add(best); matched+=1
            if (a["angle"]>0)==(oth[best]["angle"]>0):
                same+=1
    return {
        "matched":matched,
        "matched_fraction":float(matched/len(base)),
        "same_sign_fraction":float(same/max(1,matched)),
    }

def synthetic_image(shape,mask,count):
    h,w=shape
    im=np.full((h,w),255,np.uint8)
    # Place count strokes on a deterministic triangular lattice. Candidate
    # positions are well separated; pick evenly across the lattice.
    positions=[]
    for y in np.linspace(int(0.28*h),int(0.90*h),14):
        frac=(y-6)/max(1,(h-11-6))
        half=max(14,int(frac*(w*0.45)))
        cx=int(0.48*w)
        for x in np.linspace(cx-half+10,cx+half-10,18):
            xi=int(round(x)); yi=int(round(y))
            if 0<=xi<w and 0<=yi<h and mask[yi,xi]>0:
                positions.append((xi,yi))
    if len(positions)<count:
        raise RuntimeError(f"not enough synthetic positions: {len(positions)} for {count}")
    idx=np.linspace(0,len(positions)-1,count,dtype=int)
    chosen=[positions[int(i)] for i in idx]
    made=0
    for i,(x,y) in enumerate(chosen):
        sign=1 if (i%2==0) else -1
        dx=6; dy=16
        if sign>0:
            p1=(x-dx,y-dy//2); p2=(x+dx,y+dy//2)
        else:
            p1=(x-dx,y+dy//2); p2=(x+dx,y-dy//2)
        if min(p1[0],p2[0])<0 or max(p1[0],p2[0])>=w or min(p1[1],p2[1])<0 or max(p1[1],p2[1])>=h:
            continue
        cv2.line(im,p1,p2,0,1,cv2.LINE_AA)
        made+=1
    return im,made

def roi_variants(im):
    out={"original":im}
    for q in (85,70):
        b=io.BytesIO()
        Image.fromarray(im).save(b,format="JPEG",quality=q,optimize=False,progressive=False)
        b.seek(0)
        out[f"jpeg{q}"]=np.array(Image.open(b).convert("L"))
    h,w=im.shape
    small=Image.fromarray(im).resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    out["down75_up"]=np.array(small.resize((w,h),Image.Resampling.LANCZOS))
    return out

def synthetic_calibration(shape,mask):
    controls={}
    for count in (16,32,64,96):
        im,made=synthetic_image(shape,mask,count)
        vr={}
        for name,a in roi_variants(im).items():
            tr=track_across_thresholds(a,mask)
            vr[name]=summarize(tr)
        detected=np.array([vr[k]["classifiable_tracks"] for k in vr],dtype=float)
        controls[str(count)]={
            "drawn_strokes":made,
            "variants":vr,
            "mean_detected":float(detected.mean()),
            "min_detected":int(detected.min()),
            "max_detected":int(detected.max()),
            "cv":float(detected.std()/detected.mean()) if detected.mean()>0 else 999.0,
        }

    drawn=np.array([16,32,64,96],dtype=float)
    detected=np.array([controls[str(x)]["mean_detected"] for x in (16,32,64,96)],dtype=float)
    corr=float(np.corrcoef(drawn,detected)[0,1]) if detected.std()>1e-9 else 0.0
    monotonic=bool(np.all(np.diff(detected)>0))

    c64=controls["64"]
    # Calibration gate: detector must respond monotonically and recover at least
    # half of a 64-stroke carrier in every format variant.
    passed=bool(monotonic and corr>=0.95 and c64["min_detected"]>=32 and c64["cv"]<=0.25)

    return {
        "controls":controls,
        "detected_vs_drawn_pearson":corr,
        "strictly_monotonic":monotonic,
        "passed":passed,
    }

def main():
    gray=load_gray()
    vv=variants(gray)
    rows={}
    tracks={}
    geom=None
    for name,a in vv.items():
        c,m,g=sail_roi(a)
        geom=g
        tr=track_across_thresholds(c,m)
        tracks[name]=tr
        rows[name]=summarize(tr)

    base=tracks["original"]
    agreements={}
    for name,tr in tracks.items():
        if name=="original": continue
        agreements[name]=cross_agreement(base,tr)

    c0,m0,_=sail_roi(gray)
    calibration=synthetic_calibration(c0.shape,m0)

    counts=np.array([rows[k]["classifiable_tracks"] for k in rows],dtype=float)
    mean_count=float(counts.mean()) if len(counts) else 0.0
    cv=float(counts.std()/mean_count) if mean_count>0 else 999.0

    # Compare target detector output to detector output on canonical synthetic
    # carrier sizes instead of assuming perfect count recovery.
    compatible=[]
    for target,_tol in TARGET_COUNTS:
        if str(target) not in calibration["controls"]:
            continue
        ctrl=calibration["controls"][str(target)]
        lo=max(1,math.floor(ctrl["min_detected"]*0.75))
        hi=math.ceil(ctrl["max_detected"]*1.25)
        if all(lo<=rows[k]["classifiable_tracks"]<=hi for k in rows):
            compatible.append({
                "target":target,
                "calibrated_detected_range":[lo,hi],
                "control_min":ctrl["min_detected"],
                "control_max":ctrl["max_detected"],
            })

    orient_ok=all(
        rows[k]["minority_fraction"]>=0.20
        and rows[k]["orientation_median_separation_deg"]>=35
        for k in rows
    )
    agree_ok=all(
        v["matched_fraction"]>=0.55 and v["same_sign_fraction"]>=0.90
        for v in agreements.values()
    )
    promoted=bool(calibration["passed"] and compatible and cv<=0.15 and orient_ok and agree_ok)

    result={
        "experiment_id":"A11-EXP-094",
        "scope":"large-sail visible stroke carrier-capacity/robustness audit; no ordered target orientation sequence is persisted; no private-key operations",
        "sail_geometry":geom,
        "thresholds":list(THRESHOLDS),
        "target_representation_counts":[{"count":x,"tolerance":t} for x,t in TARGET_COUNTS],
        "variants":rows,
        "cross_variant_agreement":agreements,
        "classifiable_count_cv":cv,
        "compatible_target_counts":compatible,
        "orientation_structure_ok":orient_ok,
        "cross_variant_agreement_ok":agree_ok,
        "synthetic_calibration":calibration,
        "promotion_rule":"multi-count synthetic calibration passes; all target variants lie within calibrated detector-output range for 64 or 256 one-stroke-per-symbol carriers; count CV<=0.15; minority orientation fraction>=0.20; median sign-class separation>=35deg; cross-variant match>=0.55 and same-sign>=0.90",
        "promoted":promoted,
        "privacy_guard":"Ordered target stroke orientations are intentionally not written to artifacts.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    md=[
        "# Stage 94 — large-sail stroke-orientation carrier-capacity audit",
        "",
        "**Experiment:** A11-EXP-094",
        "",
        f"- synthetic multi-count detector calibration: **{calibration['passed']}**",
        f"- calibration monotonic / Pearson: **{calibration['strictly_monotonic']} / {calibration['detected_vs_drawn_pearson']:.4f}**",
        f"- calibrated compatible representation counts: **{compatible}**",
        f"- classifiable-count CV: **{cv:.4f}**",
        f"- orientation structure gate: **{orient_ok}**",
        f"- cross-variant agreement gate: **{agree_ok}**",
        f"- promotion rule satisfied: **{promoted}**",
        "",
        "## Detector calibration",
        "",
        "| drawn strokes | mean detected | min | max | CV |",
        "|---:|---:|---:|---:|---:|",
    ]
    for n in (16,32,64,96):
        cc=calibration["controls"][str(n)]
        md.append(f"| {n} | {cc['mean_detected']:.2f} | {cc['min_detected']} | {cc['max_detected']} | {cc['cv']:.3f} |")
    md += [
        "",
        "## Variant summaries",
        "",
        "| variant | stable tracks | classifiable | + | - | minority frac | angle separation | nearest canonical count |",
        "|:---|---:|---:|---:|---:|---:|---:|:---|",
    ]
    for name,r in rows.items():
        nt=r["nearest_target_count"]
        md.append(
            f"| {name} | {r['stable_tracks']} | {r['classifiable_tracks']} | "
            f"{r['positive_orientation_tracks']} | {r['negative_orientation_tracks']} | "
            f"{r['minority_fraction']:.3f} | {r['orientation_median_separation_deg']:.1f} | "
            f"{nt['target']} (delta {nt['delta']}) |"
        )
    md += ["","## Cross-format agreement","",
           "| variant vs original | matched fraction | same-sign among matches |",
           "|:---|---:|---:|"]
    for name,r in agreements.items():
        md.append(f"| {name} | {r['matched_fraction']:.3f} | {r['same_sign_fraction']:.3f} |")
    md += [
        "",
        "## Interpretation",
        "",
    ]
    if promoted:
        md.append("The large sail contains a robust discrete two-orientation stroke population whose count is compatible with a canonical key representation size across lossy variants. This promotes stroke ordering/grouping as the next mechanism question, without emitting the target orientation sequence.")
    else:
        md.append("The large sail does not satisfy the predeclared count + binary-orientation + cross-format robustness requirements for a natural 64-symbol or 256-symbol visible stroke carrier. Retire this carrier family rather than decoding an unstable stroke sequence.")
    md += [
        "",
        "The ordered target stroke-orientation sequence is deliberately not stored or printed.",
        "No private-key material was generated, reconstructed or tested.",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok","experiment_id":"A11-EXP-094",
        "control_pass":calibration["passed"],
        "compatible":compatible,
        "cv":cv,
        "orient_ok":orient_ok,
        "agreement_ok":agree_ok,
        "promoted":promoted,
    }))

if __name__=="__main__":
    main()
