#!/usr/bin/env python3
"""Stage 5: robust visual-structure analysis of Puzzle #11."""
from __future__ import annotations
import json, math
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage5-visual-structure"
OUT.mkdir(parents=True,exist_ok=True)

def angle_class(dx,dy):
    ang=abs(math.degrees(math.atan2(dy,dx))) % 180
    if ang>90: ang=180-ang
    if ang <= 22.5: return "H"
    if ang >= 67.5: return "V"
    return "D"

def crop_inner(gray,b):
    x0,x1,y0,y1=b["x0"],b["x1"],b["roof_y"],b["bottom_y"]
    w=x1-x0; h=y1-y0
    mx=max(5,int(w*0.12)); my=max(6,int(h*0.12))
    xa=min(x1-2,x0+mx); xb=max(xa+2,x1-mx)
    ya=min(y1-2,y0+my); yb=max(ya+2,y1-my)
    return gray[ya:yb,xa:xb],(xa,ya,xb,yb)

def sobel_measure(crop):
    x=cv2.GaussianBlur(crop,(3,3),0)
    gx=cv2.Sobel(x,cv2.CV_64F,1,0,ksize=3)
    gy=cv2.Sobel(x,cv2.CV_64F,0,1,ksize=3)
    ex=float(np.mean(np.abs(gx)))
    ey=float(np.mean(np.abs(gy)))
    score=(ex-ey)/(ex+ey+1e-12)
    cls="V" if score>0.06 else ("H" if score<-0.06 else "M")
    return {"vertical_edge_energy":ex,"horizontal_edge_energy":ey,"vh_score":score,"class":cls}

def hough_measure(crop,canny1,canny2,hough_threshold,min_frac,gap):
    edges=cv2.Canny(crop,canny1,canny2,L2gradient=True)
    minlen=max(8,int(min(crop.shape[:2])*min_frac))
    lines=cv2.HoughLinesP(edges,1,np.pi/180,hough_threshold,minLineLength=minlen,maxLineGap=gap)
    sums={"H":0.0,"V":0.0,"D":0.0}; counts={"H":0,"V":0,"D":0}
    if lines is not None:
        for ln in np.asarray(lines).reshape(-1,4):
            x1,y1,x2,y2=map(int,ln)
            dx=x2-x1; dy=y2-y1
            length=math.hypot(dx,dy)
            c=angle_class(dx,dy)
            sums[c]+=length; counts[c]+=1
    hv=sums["H"]+sums["V"]
    score=(sums["V"]-sums["H"])/(hv+1e-12)
    cls="V" if score>0.10 else ("H" if score<-0.10 else "M")
    return {"lengths":sums,"counts":counts,"vh_score":score,"class":cls,"edge_pixels":int(np.count_nonzero(edges))}

def bits_to_hex(classes,h_zero=True):
    if any(c not in ("H","V") for c in classes): return None
    bits="".join(("0" if c=="H" else "1") if h_zero else ("1" if c=="H" else "0") for c in classes)
    return {"bits":bits,"hex":format(int(bits,2),"03x"),"int":int(bits,2)}

def main():
    geom=json.loads(GEOM.read_text())
    img=cv2.imread(str(SOURCE),cv2.IMREAD_UNCHANGED)
    if img is None: raise SystemExit("image load failed")
    gray=img[:,:,0] if len(img.shape)==3 else img
    if gray.shape!=(1105,1600): raise SystemExit(f"unexpected gray shape {gray.shape}")

    configs=[
      (35,100,14,0.10,3),
      (45,120,16,0.12,4),
      (55,140,18,0.14,5),
      (70,170,20,0.16,6),
      (90,200,22,0.18,7),
    ]
    rows=[]; stable=[]
    annotated=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)

    for b in geom["buildings"]:
        crop,inner=crop_inner(gray,b)
        sob=sobel_measure(crop)
        hs=[hough_measure(crop,*cfg) for cfg in configs]
        votes=[sob["class"]]+[x["class"] for x in hs]
        h=votes.count("H"); v=votes.count("V")
        cls="H" if h>v else ("V" if v>h else "M")
        confidence=max(h,v)/len(votes)
        stable.append(cls)
        row={
          "id":b["id"],"bbox":[b["x0"],b["roof_y"],b["x1"],b["bottom_y"]],
          "inner_bbox":list(inner),"sobel":sob,"hough":hs,
          "votes":votes,"class":cls,"vote_confidence":confidence,
        }
        rows.append(row)
        x0,y0,x1,y1=inner
        label=f"{b['id']}:{cls} {confidence:.2f}"
        cv2.rectangle(annotated,(x0,y0),(x1,y1),(0,0,0),1)
        cv2.putText(annotated,label,(x0,max(16,y0-4)),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,255,255),3,cv2.LINE_AA)
        cv2.putText(annotated,label,(x0,max(16,y0-4)),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,0,0),1,cv2.LINE_AA)

    mappings={"H0_V1":bits_to_hex(stable,True),"H1_V0":bits_to_hex(stable,False)}

    robustness=[]
    for thr in (80,100,120,140,160,180,200,220):
        seq=[]
        for b in geom["buildings"]:
            crop,_=crop_inner(gray,b)
            bw=np.where(crop<thr,0,255).astype(np.uint8)
            seq.append(sobel_measure(bw)["class"])
        robustness.append({"threshold":thr,"classes":"".join(seq)})

    result={
      "image_shape":[int(gray.shape[1]),int(gray.shape[0])],
      "building_classes":"".join(stable),
      "mappings":mappings,
      "buildings":rows,
      "threshold_robustness":robustness,
      "interpretation_note":"A structured bit pattern is a lead only; it is not evidence of the private key without an exact target-address derivation."
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    cv2.imwrite(str(OUT/"buildings-orientation.png"),annotated)

    md=["# Stage 5 — robust visual structure","",
        "The 12 building interiors were classified independently with Sobel orientation energy and five Hough-line parameter sets.","",
        "| id | class | confidence | Sobel V-H score | Hough classes |",
        "|---:|:---:|---:|---:|:---|"]
    for r in rows:
        md.append(f"| {r['id']} | {r['class']} | {r['vote_confidence']:.3f} | {r['sobel']['vh_score']:.4f} | {''.join(x['class'] for x in r['hough'])} |")
    md += ["",
      "Stable orientation sequence: "+''.join(stable),
      "H=0, V=1: "+json.dumps(mappings["H0_V1"]),
      "H=1, V=0: "+json.dumps(mappings["H1_V0"]),
      "",
      "## Threshold robustness",""]
    for r in robustness:
        md.append(f"- threshold {r['threshold']}: {r['classes']}")
    md += ["",
      "A pattern stable across independent estimators and thresholds is worth following because it is visually preserved by ordinary re-encoding, consistent with the author's 'format does not matter' hint. It is not a solution by itself.",
      ""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","classes":"".join(stable),"mappings":mappings}))

if __name__=="__main__":
    main()
