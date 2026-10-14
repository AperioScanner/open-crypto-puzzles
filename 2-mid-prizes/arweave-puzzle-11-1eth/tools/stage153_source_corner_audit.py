#!/usr/bin/env python3
"""Stage153 real-source corner diagnostic ONLY, no retuning or classification.

Preregistered diagnostic: inspect all 18 unchanged Stage153 vertex positions
in the canonical PNG; generate raw-pixel and guide-overlay pairs and report
distance of visible ink to the straight nominal arms at t=6..11 px.
Use the old 48/48 and 2/5 classifier and decision unchanged.
No candidate optimization, new Stage, words, private keys or wallets.
"""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stage153_under_pier_triangle_junctions import TRIANGLES, SOURCE, OUT, SHA, DARK, RADIUS

HALF = 33
MAG = 3
THUMB = (2 * HALF + 1) * MAG
PW, PH = THUMB * 2 + 55, THUMB + 82

def nearest_ink(gray, vertex, other, threshold):
    unit = np.array(other, float)-np.array(vertex, float)
    unit /= np.linalg.norm(unit)
    distances = []
    for t in range(6, 12):
        px,py = np.array(vertex,float)+t*unit
        ix,iy = int(round(px)),int(round(py))
        x0,x1=max(0,ix-9),min(gray.shape[1],ix+10)
        y0,y1=max(0,iy-9),min(gray.shape[0],iy+10)
        ys,xs=np.where(gray[y0:y1,x0:x1]<threshold)
        if len(xs):
            distances.append(float(np.sqrt((xs+x0-px)**2+(ys+y0-py)**2).min()))
        else:
            distances.append(10.0)
    return {"median_px":round(float(np.median(distances)),2),
            "within_1_5px":sum(d<=1.5 for d in distances),
            "six_distances_px":[round(d,2) for d in distances]}

def write_text(canvas, value, x,y):
    cv2.putText(canvas,value,(x,y),cv2.FONT_HERSHEY_SIMPLEX,.42,
                (0,0,0),1,cv2.LINE_AA)

def main():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest!=SHA: raise RuntimeError("Canonical image SHA mismatch")
    gray=np.asarray(Image.open(SOURCE).convert("L"))
    if gray.shape!=(1105,1600):raise RuntimeError("Image geometry mismatch")
    prior=json.loads((OUT/"result.json").read_text())
    if prior["sha256"]!=SHA or prior["experiment_id"]!="A11-EXP-153":
        raise RuntimeError("Stage153 baseline missing")
    canvas=np.full((len(TRIANGLES)*PH,3*PW,3),255,np.uint8)
    observations={}
    failures=[]
    for r,(site,polygon) in enumerate(TRIANGLES.items()):
        observations[site]=[]
        points=list(polygon)
        for col,v in enumerate(points):
            arms=(points[(col+1)%3],points[(col+2)%3])
            baseline=prior["real"]["original"][site]["corners"][col]
            measurements=[nearest_ink(gray,v,a,DARK) for a in arms]
            gray215=[nearest_ink(gray,v,a,215) for a in arms]
            record={"vertex":v,"stage153_baseline":baseline,
                    "nominal_arm_175":measurements,
                    "nominal_arm_215_descriptive_only":gray215}
            observations[site].append(record)
            if not baseline["pass"]:
                failures.append((site,col+1,v,baseline["arm_contacts"],
                                 [m["median_px"] for m in measurements]))
            x,y=v
            crop=gray[y-HALF:y+HALF+1,x-HALF:x+HALF+1]
            assert crop.shape==(2*HALF+1,2*HALF+1)
            raw=cv2.cvtColor(cv2.resize(crop,(THUMB,THUMB),interpolation=cv2.INTER_NEAREST),cv2.COLOR_GRAY2BGR)
            guide=raw.copy()
            center=HALF*MAG
            for a,color in zip(arms,((0,90,245),(10,170,15))):
                unit=np.array(a,float)-np.array(v,float)
                unit/=np.linalg.norm(unit)
                end=(int(round(center+RADIUS*MAG*unit[0])),
                     int(round(center+RADIUS*MAG*unit[1])))
                cv2.line(guide,(center,center),end,color,1,cv2.LINE_AA)
            cv2.drawMarker(guide,(center,center),(180,0,180),cv2.MARKER_CROSS,9,1)
            top,left=r*PH,col*PW
            write_text(canvas,f"{site} corner {col+1} {v}",left+6,top+17)
            write_text(canvas,"BASELINE "+("PASS" if baseline["pass"] else "FAIL"),left+6,top+34)
            canvas[top+42:top+42+THUMB,left+6:left+6+THUMB]=raw
            canvas[top+42:top+42+THUMB,left+THUMB+25:left+2*THUMB+25]=guide
            da=[m["median_px"] for m in measurements]
            write_text(canvas,f"Ideal arm distances: {da[0]} / {da[1]} px",left+6,top+THUMB+62)
    assert cv2.imwrite(str(OUT/"source-corner-audit.png"),canvas)
    data={"experiment_id":"A11-EXP-153-source-audit","source_sha256":digest,
          "stage153_decision_unchanged":prior["decision"],
          "stage153_original_positive_recovery_unchanged":prior["real_positive_sails"],
          "method":"raw nearest-neighbour 67x67 corner crops, two nominal-line guide copies, 6-11px arm ink distance at gray<175 and diagnostic gray<215",
          "no_reclassification":True,"observations":observations}
    (OUT/"source-audit.json").write_text(json.dumps(data,indent=2)+"\n")
    lines=["# Stage153 source-corner audit — diagnostics, NOT a new Stage","",
      "- Canonical SHA-256 verified: "+digest,
      "- Original Stage153 decision unchanged: "+prior["decision"],
      f"- Original synthetic controls: {prior['controls']['passed']}/{prior['controls']['cases']}.",
      f"- Original full 3-corner recovery on five known sails: {prior['real_positive_sails']}/5.",
      "- source-corner-audit.png: left crop = raw unedited pixel enlargement; right = separate arm-guide overlay.",
      "- Distances are descriptions of alignment, not new gates, and DO NOT validate connectivity.",
      "- Applying gray<215 is diagnostic only; the original gray<175 classifier is not changed.","",
      "| Original failing corner | Fixed vertex | Arm labels found | Median nearest ink to ideal arms px |",
      "|---|---|---|---|"]
    for site,k,v,c,dist in failures:
        lines.append(f"| {site} #{k} | {v} | {c} | {dist[0]:.2f} / {dist[1]:.2f} |")
    lines+=["","Interpretation limit: imperfect annotated vertices, sparse or curved pencil lines, faint ink, and genuinely disconnected lines can produce the same missing contact. Human comparison with source crops is required. A filled triangular sail is not automatically a perfectly joined three-edge outline.","",
       "No relaxed gates, new decoded message, key, mnemonic, wallet or external research.",""]
    (OUT/"SOURCE_AUDIT.md").write_text("\n".join(lines))
    print(json.dumps({"source_sha_ok":True,"unchanged_real_sails":prior["real_positive_sails"],
          "failed_real_sail_corners":sum(1 for site,k,v,c,d in failures if site!="under_pier"),
          "failed_under_pier_corners":sum(1 for site,k,v,c,d in failures if site=="under_pier")}))
if __name__=="__main__":
    main()
