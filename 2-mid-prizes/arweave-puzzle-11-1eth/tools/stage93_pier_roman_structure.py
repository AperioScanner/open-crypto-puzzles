#!/usr/bin/env python3
"""Stage 93: pier/support Roman-numeral structure audit.

Tests the last genuinely untested historical visual claim identified by corrected
Stage 91: the pier/support geometry may visibly form X, IX, or XI.

Safe scope only. This stage evaluates visible line geometry and never generates,
derives, reconstructs, enumerates, or verifies candidate private keys.

Predeclared target ROI:
  x=900..1320, y=510..830

Predeclared templates:
  X  = crossing long opposite-slope diagonals
  IX = X plus adjacent near-vertical long stroke to the left
  XI = X plus adjacent near-vertical long stroke to the right

The target is compared with nuisance-matched same-size windows and replicated
after JPEG85 + 0.75x down/up resampling. Synthetic X/IX/XI controls validate the
detector.
"""
from __future__ import annotations

import io, json, math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage93-pier-roman-structure"
OUT.mkdir(parents=True,exist_ok=True)

ROI=(900,510,1320,830)
W=ROI[2]-ROI[0]
H=ROI[3]-ROI[1]

CONFIGS=(
    {"name":"c50_150_h35","canny":(50,150),"hough":35,"minlen":55,"gap":14},
    {"name":"c65_165_h40","canny":(65,165),"hough":40,"minlen":60,"gap":12},
    {"name":"c80_180_h45","canny":(80,180),"hough":45,"minlen":65,"gap":10},
    {"name":"c95_195_h50","canny":(95,195),"hough":50,"minlen":70,"gap":10},
    {"name":"c110_210_h55","canny":(110,210),"hough":55,"minlen":75,"gap":8},
)
GRID_STEP=70
MATCHED_K=55

def load_gray():
    a=np.array(Image.open(SOURCE).convert("L"))
    if a.shape!=(1105,1600):
        raise SystemExit(f"unexpected shape {a.shape}")
    return a

def lossy(gray):
    im=Image.fromarray(gray,mode="L")
    b=io.BytesIO()
    im.save(b,format="JPEG",quality=85,optimize=False,progressive=False)
    b.seek(0)
    j=Image.open(b).convert("L")
    small=j.resize((1200,829),Image.Resampling.LANCZOS)
    return np.array(small.resize((1600,1105),Image.Resampling.LANCZOS))

def crop(a,box):
    x0,y0,x1,y1=map(int,box)
    return a[y0:y1,x0:x1]

def seg_angle(x1,y1,x2,y2):
    ang=math.degrees(math.atan2(y2-y1,x2-x1))
    while ang>90: ang-=180
    while ang<=-90: ang+=180
    return ang

def detect_lines(c,config):
    edges=cv2.Canny(c,config["canny"][0],config["canny"][1])
    raw=cv2.HoughLinesP(
        edges,1,np.pi/180,threshold=config["hough"],
        minLineLength=config["minlen"],maxLineGap=config["gap"]
    )
    rows=[]
    if raw is None:
        return rows,edges
    # OpenCV 4 commonly returns (N,1,4); OpenCV 5 may return (N,4).
    # Normalize both layouts before iterating.
    for z in np.asarray(raw).reshape(-1,4):
        x1,y1,x2,y2=map(float,z)
        length=float(math.hypot(x2-x1,y2-y1))
        ang=seg_angle(x1,y1,x2,y2)
        mx=(x1+x2)/2; my=(y1+y2)/2
        rows.append({"x1":x1,"y1":y1,"x2":x2,"y2":y2,"length":length,"angle":ang,"mx":mx,"my":my})
    # Greedy near-duplicate suppression by midpoint/angle; keep longest first.
    keep=[]
    for r in sorted(rows,key=lambda q:q["length"],reverse=True):
        dup=False
        for k in keep:
            da=abs(r["angle"]-k["angle"])
            da=min(da,180-da)
            dm=math.hypot(r["mx"]-k["mx"],r["my"]-k["my"])
            if da<=6 and dm<=22:
                dup=True; break
        if not dup:
            keep.append(r)
    return keep,edges

def line_intersection(a,b):
    x1,y1,x2,y2=a["x1"],a["y1"],a["x2"],a["y2"]
    x3,y3,x4,y4=b["x1"],b["y1"],b["x2"],b["y2"]
    den=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    if abs(den)<1e-9:
        return None
    px=((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/den
    py=((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/den
    def within(x,y,r):
        pad=0.08*r["length"]
        return (min(r["x1"],r["x2"])-pad<=x<=max(r["x1"],r["x2"])+pad and
                min(r["y1"],r["y2"])-pad<=y<=max(r["y1"],r["y2"])+pad)
    if not within(px,py,a) or not within(px,py,b):
        return None
    return float(px),float(py)

def x_candidates(lines):
    pos=[r for r in lines if 22<=r["angle"]<=75 and r["length"]>=65]
    neg=[r for r in lines if -75<=r["angle"]<=-22 and r["length"]>=65]
    out=[]
    diag=math.hypot(W,H)
    for a in pos:
        for b in neg:
            inter=line_intersection(a,b)
            if inter is None: continue
            x,y=inter
            if not (0.06*W<=x<=0.94*W and 0.06*H<=y<=0.94*H):
                continue
            separation=abs(a["angle"]-b["angle"])
            if separation<45: continue
            balance=min(a["length"],b["length"])/max(a["length"],b["length"])
            length_score=min(1.0,(a["length"]+b["length"])/(0.85*diag))
            angle_score=min(1.0,separation/90.0)
            center_dist=math.hypot((x-W/2)/(W/2),(y-H/2)/(H/2))
            center_score=max(0.35,1.0-0.25*center_dist)
            score=float(balance*length_score*angle_score*center_score)
            out.append({"a":a,"b":b,"x":x,"y":y,"score":score})
    return sorted(out,key=lambda z:z["score"],reverse=True)

def verticals(lines):
    return [r for r in lines if abs(r["angle"])>=72 and r["length"]>=60]

def template_scores(lines):
    xs=x_candidates(lines)
    vs=verticals(lines)
    best={"X":0.0,"IX":0.0,"XI":0.0}
    details={"X":None,"IX":None,"XI":None}
    for xrec in xs[:12]:
        xscore=xrec["score"]
        if xscore>best["X"]:
            best["X"]=xscore; details["X"]=xrec
        for v in vs:
            dx=v["mx"]-xrec["x"]
            dy=abs(v["my"]-xrec["y"])
            if abs(dx)<24 or abs(dx)>0.42*W: continue
            if dy>0.42*H: continue
            proximity=max(0.0,1.0-abs(dx)/(0.42*W))
            yalign=max(0.0,1.0-dy/(0.42*H))
            vlen=min(1.0,v["length"]/(0.42*H))
            combo=float(xscore*(0.55+0.45*proximity)*(0.60+0.40*yalign)*(0.65+0.35*vlen))
            label="IX" if dx<0 else "XI"
            if combo>best[label]:
                best[label]=combo
                details[label]={"x":xrec,"vertical":v,"dx":dx,"score":combo}
    return best,details

def nuisance(c,lines):
    ink=float((c<200).mean())
    edge=float((cv2.Canny(c,65,165)>0).mean())
    long_count=float(len([r for r in lines if r["length"]>=70]))
    return np.array([ink,edge,long_count],dtype=float)

def eval_crop(c):
    per=[]
    for cfg in CONFIGS:
        lines,edges=detect_lines(c,cfg)
        scores,details=template_scores(lines)
        label=max(scores,key=scores.get)
        per.append({
            "config":cfg["name"],
            "line_count":len(lines),
            "scores":scores,
            "winner":label,
            "winner_score":float(scores[label]),
            "details":details,
        })
    family_best=max((r["winner_score"] for r in per),default=0.0)
    labels=[r["winner"] for r in per if r["winner_score"]>0]
    dominant=max(set(labels),key=labels.count) if labels else None
    support=labels.count(dominant) if dominant else 0
    return {"per_config":per,"family_best":float(family_best),"dominant":dominant,"support":support}

def boxes(shape):
    HH,WW=shape
    out=[]
    for y in range(0,HH-H+1,GRID_STEP):
        for x in range(0,WW-W+1,GRID_STEP):
            b=(x,y,x+W,y+H)
            # Exclude target and close-overlap neighborhoods.
            ix=max(0,min(b[2],ROI[2])-max(b[0],ROI[0]))
            iy=max(0,min(b[3],ROI[3])-max(b[1],ROI[1]))
            overlap=ix*iy/(W*H)
            if overlap>0.05: continue
            out.append(b)
    return out

def matched_nulls(gray):
    target=crop(gray,ROI)
    l0,_=detect_lines(target,CONFIGS[1])
    nt=nuisance(target,l0)
    bs=boxes(gray.shape)
    ns=[]
    for b in bs:
        cc=crop(gray,b)
        ll,_=detect_lines(cc,CONFIGS[1])
        ns.append(nuisance(cc,ll))
    N=np.stack(ns)
    sd=N.std(axis=0)
    sd=np.where(sd<1e-9,1.0,sd)
    dist=np.sqrt(np.sum(((N-nt)/sd)**2,axis=1))
    order=np.argsort(dist)[:MATCHED_K]
    return [bs[int(i)] for i in order],nt

def empirical_p(obs,null):
    return float((1+sum(v>=obs-1e-12 for v in null))/(1+len(null)))

def synthetic(label):
    im=np.full((H,W),255,np.uint8)
    # Stable central X.
    cv2.line(im,(145,75),(270,250),0,8,cv2.LINE_AA)
    cv2.line(im,(275,75),(145,250),0,8,cv2.LINE_AA)
    if label=="IX":
        cv2.line(im,(95,70),(95,255),0,8,cv2.LINE_AA)
    if label=="XI":
        cv2.line(im,(325,70),(325,255),0,8,cv2.LINE_AA)
    return im

def control_result(label):
    e=eval_crop(synthetic(label))
    # For IX/XI, require intended composite score to beat bare X. For X, X only.
    scores=np.mean([[r["scores"][k] for r in e["per_config"]] for k in ("X","IX","XI")],axis=1)
    m={"X":float(scores[0]),"IX":float(scores[1]),"XI":float(scores[2])}
    if label=="X":
        passed=m["X"]>0.35
    else:
        passed=m[label]>0.30 and m[label]>=0.75*m["X"]
    return {"label":label,"mean_scores":m,"passed":bool(passed),"evaluation":e}

def draw_overlay(c,ev,path):
    im=cv2.cvtColor(c,cv2.COLOR_GRAY2BGR)
    # Use config with highest winning score.
    rec=max(ev["per_config"],key=lambda r:r["winner_score"])
    cfg=next(x for x in CONFIGS if x["name"]==rec["config"])
    lines,_=detect_lines(c,cfg)
    for r in lines:
        cv2.line(im,(round(r["x1"]),round(r["y1"])),(round(r["x2"]),round(r["y2"])),(0,0,0),2)
    cv2.imwrite(str(path),im)

def main():
    gray=load_gray()
    gray2=lossy(gray)
    target=crop(gray,ROI)
    target2=crop(gray2,ROI)

    ev0=eval_crop(target)
    ev1=eval_crop(target2)
    matched,nt=matched_nulls(gray)
    null=[]
    for b in matched:
        ev=eval_crop(crop(gray,b))
        null.append({"box":list(b),"family_best":ev["family_best"],"dominant":ev["dominant"],"support":ev["support"]})
    p=empirical_p(ev0["family_best"],[r["family_best"] for r in null])

    controls=[control_result(x) for x in ("X","IX","XI")]
    controls_pass=all(x["passed"] for x in controls)

    same_template=bool(ev0["dominant"] and ev0["dominant"]==ev1["dominant"])
    stable_support=bool(ev0["support"]>=3 and ev1["support"]>=3)
    # With 55 matched windows, minimum attainable p is 1/56=.0179, so use 0.02.
    promoted=bool(controls_pass and same_template and stable_support and p<=0.02 and ev0["family_best"]>=0.30)

    result={
        "experiment_id":"A11-EXP-093",
        "scope":"predeclared pier/support ROI X/IX/XI structural audit; no private-key operations",
        "roi":list(ROI),
        "configs":list(CONFIGS),
        "original":ev0,
        "lossy":ev1,
        "matched_null_windows":len(null),
        "target_nuisance":{"ink200":float(nt[0]),"edge_density":float(nt[1]),"long_line_count":float(nt[2])},
        "null_family_best_median":float(np.median([r["family_best"] for r in null])),
        "null_family_best_max":float(np.max([r["family_best"] for r in null])),
        "familywise_empirical_p":p,
        "synthetic_controls":controls,
        "controls_pass":controls_pass,
        "same_template_after_lossy":same_template,
        "stable_support":stable_support,
        "promotion_rule":"all X/IX/XI synthetic controls pass; same dominant template original/lossy; dominant support>=3 configs in both; familywise p<=0.02; target family score>=0.30",
        "promoted":promoted,
        "interpretation_guard":"Promotion means only that Roman-like line geometry is unusually explicit/stable. It does not justify converting the shape into secret material.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    draw_overlay(target,ev0,OUT/"pier-lines-original.png")
    draw_overlay(target2,ev1,OUT/"pier-lines-lossy.png")
    Image.fromarray(target).save(OUT/"pier-roi-original.png")

    md=[
        "# Stage 93 — pier Roman-numeral structure audit",
        "",
        "**Experiment:** A11-EXP-093",
        "",
        f"- ROI: **{ROI}**",
        f"- original dominant template: **{ev0['dominant']}** ({ev0['support']}/{len(CONFIGS)} configs)",
        f"- lossy dominant template: **{ev1['dominant']}** ({ev1['support']}/{len(CONFIGS)} configs)",
        f"- original family-best score: **{ev0['family_best']:.6f}**",
        f"- matched-null median: **{np.median([r['family_best'] for r in null]):.6f}**",
        f"- matched-null max: **{np.max([r['family_best'] for r in null]):.6f}**",
        f"- familywise empirical p: **{p:.6f}**",
        f"- synthetic controls all pass: **{controls_pass}**",
        f"- promotion rule satisfied: **{promoted}**",
        "",
        "## Synthetic controls",
        "",
        "| control | passed | mean X | mean IX | mean XI |",
        "|:---|:---:|---:|---:|---:|",
    ]
    for r in controls:
        m=r["mean_scores"]
        md.append(f"| {r['label']} | {r['passed']} | {m['X']:.4f} | {m['IX']:.4f} | {m['XI']:.4f} |")

    md += ["","## Per-config target results","",
           "| config | winner | score | X | IX | XI | lines |",
           "|:---|:---:|---:|---:|---:|---:|---:|"]
    for r in ev0["per_config"]:
        s=r["scores"]
        md.append(f"| {r['config']} | {r['winner']} | {r['winner_score']:.4f} | {s['X']:.4f} | {s['IX']:.4f} | {s['XI']:.4f} | {r['line_count']} |")

    md += ["","## Interpretation",""]
    if promoted:
        md.append("The pier/support region contains an unusually stable Roman-like line structure relative to matched scene windows, and it survives lossy conversion. This promotes the *visual structure only* for semantic interpretation in the next adaptive stage.")
    else:
        md.append("The historical X/IX/XI reading does not meet the predeclared uniqueness/stability gate. Retire this Roman-numeral hypothesis rather than building further interpretations from it.")
    md += ["","No private-key material was generated, reconstructed or tested.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-093","dominant":ev0["dominant"],"p":p,"controls_pass":controls_pass,"promoted":promoted}))

if __name__=="__main__":
    main()
