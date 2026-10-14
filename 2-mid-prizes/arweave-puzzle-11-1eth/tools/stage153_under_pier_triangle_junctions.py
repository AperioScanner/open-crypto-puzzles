#!/usr/bin/env python3
"""Stage153: independent vertex-junction continuity audit of under-pier triangle.

Stage152 validated dark ink along three interpolated edges, but this does NOT
prove those strokes physically connect at the triangle vertices: crossing
dock ropes can match each line independently. Test source vertex connectivity
within *fixed* 13px disk and exact Stage152 source vertices, including five
positive bona-fide sail shapes. Four independent re-encodings and positive
closed vs small disconnected corner gaps synthetic controls must all pass.

No key, BIP39, wallet, secret, external source or guessed symbol.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from stage112_corrected_sail_width_progression import variants

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage153-under-pier-vertex-connectivity"
OUT.mkdir(parents=True,exist_ok=True)
SHA="c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
TRIANGLES={
 "sail1":((1042,448),(1007,546),(1077,546)),
 "sail2":((1148,433),(1110,532),(1186,532)),
 "sail3":((1282,411),(1238,514),(1326,514)),
 "sail4":((1372,397),(1330,498),(1414,498)),
 "sail5":((1490,357),(1443,463),(1537,463)),
 "under_pier":((1052,633),(1052,778),(1280,714)),
}
RADIUS=13
DARK=175
MAX_GAP_PIXELS=2
MIN_VERTEX_CONNECTED=3
NEAR_EDGE_MIN=6
FORMATS=("original","jpeg85","jpeg70","down75_up")

def vertex_connected(gray,v,a,b):
    """Check both inward adjacent edge arms enter the same ink component.

    Local connected-component labels alone may be confounded by pier hatching;
    report occupancy and anchor-to-arm contacts, never interpret a label as a
    unique authored closed shape.
    """
    x,y=v
    xmin=max(0,x-RADIUS);ymin=max(0,y-RADIUS)
    xmax=min(gray.shape[1],x+RADIUS+1)
    ymax=min(gray.shape[0],y+RADIUS+1)
    sub=(gray[ymin:ymax,xmin:xmax]<DARK).astype(np.uint8)
    # Tiny one-pixel antialias gaps are repaired at fixed <=2px only.
    sub=cv2.morphologyEx(sub,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    count,lab,_,_=cv2.connectedComponentsWithStats(sub,8)
    contacts=[]
    for target in (a,b):
        tx,ty=target
        vec=np.array([tx-x,ty-y],float)
        norm=np.linalg.norm(vec)
        if norm==0:return {"pass":False,"reason":"zero edge"}
        ux,uy=vec/norm
        pixels=[]
        for t in range(NEAR_EDGE_MIN,RADIUS-1):
            px=x+int(round(ux*t))-xmin
            py=y+int(round(uy*t))-ymin
            for yy in range(py-1,py+2):
                for xx in range(px-1,px+2):
                    if 0<=yy<lab.shape[0] and 0<=xx<lab.shape[1] and lab[yy,xx]>0:
                        pixels.append(int(lab[yy,xx]))
        contacts.append(set(pixels))
    common=contacts[0]&contacts[1]
    return {"pass":bool(common),"component_count":int(count-1),
            "contacted_common":len(common),"arm_contacts":[len(c) for c in contacts]}

def measure(img,points):
    v=list(points)
    corners=[]
    for i in range(3):
        corners.append(vertex_connected(img,v[i],v[(i+1)%3],v[(i+2)%3]))
    return {"corners":corners,"all_three_connected":all(z["pass"] for z in corners)}

def fake(points,connected):
    a=np.full((1105,1600),255,np.uint8)
    for i in range(3):
        x0,y0=points[i];x1,y1=points[(i+1)%3]
        p=np.array([x0,y0],float);q=np.array([x1,y1],float)
        v=(q-p)/np.linalg.norm(q-p)
        inset=0 if connected else 19
        x,y=np.round(p+v*inset).astype(int)
        xx,yy=np.round(q-v*inset).astype(int)
        cv2.line(a,(int(x),int(y)),(int(xx),int(yy)),0,2,cv2.LINE_AA)
    return a

def controls():
    pass_cases=0; cases=0;examples={}
    for kind,expected in (("closed",True),("open_corners",False)):
        for site,points in TRIANGLES.items():
            frames=variants(fake(points,expected))
            for fmt in FORMATS:
                actual=measure(frames[fmt],points)["all_three_connected"]
                passed=actual==expected
                pass_cases+=int(passed);cases+=1
                examples[f"{kind}:{site}:{fmt}"]=actual
    return {"pass":pass_cases==cases,"passed":pass_cases,
            "cases":cases,"observations":examples}

def main():
    checksum=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if checksum!=SHA:raise SystemExit("canonical SHA mismatch")
    img=np.asarray(Image.open(SOURCE).convert("L"))
    if img.shape!=(1105,1600):raise SystemExit("unexpected source size")
    ctl=controls()
    data={fmt:{site:measure(frame,p) for site,p in TRIANGLES.items()}
          for fmt,frame in variants(img).items() if fmt in FORMATS}
    real_positive=sum(all(data[fmt][site]["all_three_connected"] for fmt in FORMATS)
        for site in list(TRIANGLES)[:5])
    candidate=all(data[fmt]["under_pier"]["all_three_connected"] for fmt in FORMATS)
    decision=("CONTROL_FAILURE" if not ctl["pass"] else
        "INSUFFICIENT_KNOWN_SAIL_JUNCTION_RECOVERY" if real_positive<4 else
        "UNDER_PIER_THREE_CORNERS_CONTIGUOUS_NEEDS_VISUAL_REVIEW" if candidate else
        "UNDER_PIER_EDGES_NOT_CONNECTED_AT_ALL_VERTICES")
    result={"experiment_id":"A11-EXP-153","sha256":checksum,
       "hypothesis":"all three Stage152 ink-supported edges meet as continuous ink at the specified under-pier triangle corners, rather than independent crossed pier strokes",
       "sites":TRIANGLES,
       "gates":{"radius":RADIUS,"threshold":DARK,"closing":3,
         "sample_arm_range_px":[NEAR_EDGE_MIN,RADIUS-2],"min_real_sails":4},
       "controls":ctl,"real":data,"real_positive_sails":real_positive,
       "under_pier_3_junctions_stable":candidate,"decision":decision,
       "scope_limit":"Local connected ink can join incidentally via pier beams; any positive requires adversarial manual inspection and does not prove a sail or intentional symbol.",
       "safety":"Canonical source pixels only; no wallets, private keys, phrase candidates or external search."}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    report=[f"# Stage153 — three-corner ink connectivity beneath pier","",
       f"- Controls: **{ctl['passed']}/{ctl['cases']}**",
       f"- True-sail three-corner recovery: **{real_positive}/5**",
       f"- Under-pier all corners connected in four formats: **{candidate}**",
       f"- Decision: **{decision}**","",
       "Crossing strokes may connect incidentally, so this is not evidence of an additional ship or hidden code.",
       "No key, mnemonic, wallet or external sources."]
    (OUT/"REPORT.md").write_text("\n".join(report)+"\n")
    print(json.dumps({"stage":153,"controls":ctl["pass"],"sails":real_positive,"candidate":candidate,"decision":decision}))
if __name__=="__main__":main()
