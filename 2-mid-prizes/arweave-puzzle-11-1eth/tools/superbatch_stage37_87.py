#!/usr/bin/env python3
from __future__ import annotations
import json, math, itertools
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
MANIFEST=ROOT/"analysis"/"superbatch"/"STAGE_37_86_MANIFEST.json"
OUT=ROOT/"analysis"/"runs"/"superbatch-37-87"
OUT.mkdir(parents=True,exist_ok=True)

N_WINDOW_NULL=180
N_PERM=2000
RNG=np.random.default_rng(378701)
LARGE=(44,320,359,599)

SEMANTIC={
 "first_row":(0,0,1600,48),
 "skyline":(200,0,1600,340),
 "large_sail":LARGE,
 "small_sails":(367,360,1500,480),
 "right_boats":(360,350,1500,620),
 "water":(0,620,1600,1105),
}

def load_gray():
    a=np.array(Image.open(SOURCE).convert("L"))
    if a.shape!=(1105,1600): raise SystemExit(f"unexpected image shape {a.shape}")
    return a

def lossy(gray):
    im=Image.fromarray(gray,mode="L")
    b=BytesIO(); im.save(b,format="JPEG",quality=85,optimize=False,progressive=False); b.seek(0)
    j=Image.open(b).convert("L")
    small=j.resize((1200,829),Image.Resampling.LANCZOS)
    return np.array(small.resize((1600,1105),Image.Resampling.LANCZOS))

def crop(a,box):
    x0,y0,x1,y1=map(int,box); return a[y0:y1,x0:x1]

def safe_corr(a,b):
    x=np.asarray(a,dtype=float).ravel(); y=np.asarray(b,dtype=float).ravel()
    if len(x)!=len(y) or len(x)<3 or np.std(x)<1e-12 or np.std(y)<1e-12: return 0.0
    return float(np.corrcoef(x,y)[0,1])

def edge(c):
    return cv2.Canny(c.astype(np.uint8),80,160)>0

def entropy_bits(vals,bins=32):
    h,_=np.histogram(vals,bins=bins,range=(0,256))
    p=h[h>0].astype(float); p/=p.sum()
    return float(-(p*np.log2(p)).sum()) if len(p) else 0.0

def metric(c,name):
    c=np.asarray(c,dtype=np.uint8)
    if name=="edge_density": return float(edge(c).mean())
    if name=="intensity_std": return float(c.std())
    if name=="tile_entropy_std":
        vals=[]
        for y in range(0,c.shape[0],32):
            for x in range(0,c.shape[1],32):
                t=c[y:y+32,x:x+32]
                if t.size>=128: vals.append(entropy_bits(t))
        return float(np.std(vals)) if vals else 0.0
    if name=="x_symmetry": return abs(safe_corr(c,np.fliplr(c)))
    if name=="y_symmetry": return abs(safe_corr(c,np.flipud(c)))
    if name in ("hproj_peak","vproj_peak"):
        m=(c<180).astype(float)
        p=m.sum(axis=1 if name=="hproj_peak" else 0)
        if len(p)<4 or np.std(p)<1e-12: return 0.0
        z=(p-p.mean())/(p.std()+1e-12)
        ac=np.correlate(z,z,mode="full")[len(z)-1:]
        hi=min(len(ac),max(4,len(ac)//2))
        return float(np.max(ac[2:hi])/(len(z)+1e-12)) if hi>2 else 0.0
    if name=="spectral_peak":
        x=c.astype(float)-float(c.mean())
        h,w=x.shape
        if min(h,w)<8 or np.std(x)<1e-12: return 0.0
        p=np.abs(np.fft.fftshift(np.fft.fft2(x*np.hanning(h)[:,None]*np.hanning(w)[None,:])))**2
        yy,xx=np.indices(p.shape); cy=(h-1)/2; cx=(w-1)/2
        mask=np.hypot(xx-cx,yy-cy)>=3
        v=p[mask]; med=float(np.median(v))+1e-12
        return float(np.percentile(v,99.9)/med)
    if name=="component_density":
        bw=(c<140).astype(np.uint8)
        n,lab,stats,cent=cv2.connectedComponentsWithStats(bw,8)
        count=sum(5<=int(stats[i,cv2.CC_STAT_AREA])<=500 for i in range(1,n))
        return float(count/c.size*10000)
    if name=="component_aspect_entropy":
        bw=(c<140).astype(np.uint8)
        n,lab,stats,cent=cv2.connectedComponentsWithStats(bw,8)
        ars=[]
        for i in range(1,n):
            ar=int(stats[i,cv2.CC_STAT_AREA])
            if 5<=ar<=500:
                w=max(1,int(stats[i,cv2.CC_STAT_WIDTH])); h=max(1,int(stats[i,cv2.CC_STAT_HEIGHT]))
                ars.append(np.clip(math.log2(w/h),-3,3))
        if len(ars)<3: return 0.0
        h,_=np.histogram(ars,bins=12,range=(-3,3)); p=h[h>0].astype(float); p/=p.sum()
        return float(-(p*np.log2(p)).sum())
    if name=="glyph":
        bw=(c<170).astype(np.uint8)
        n,lab,stats,cent=cv2.connectedComponentsWithStats(bw,8)
        comps=[]
        for i in range(1,n):
            x,y,w,h,area=map(int,stats[i])
            if 5<=area<=500 and 2<=w<=60 and 4<=h<=45:
                comps.append((x,y,w,h,float(cent[i,1])))
        if not comps: return 0.0
        bins={}
        for z in comps: bins.setdefault(int(z[4]//14),[]).append(z)
        best=max(bins.values(),key=len)
        if len(best)<2: return 0.0
        cov=(max(z[0]+z[2] for z in best)-min(z[0] for z in best))/c.shape[1]
        return float(len(best)*math.sqrt(max(cov,0))/(math.sqrt(len(comps)+1)))
    if name=="edge_entropy":
        gx=cv2.Sobel(c.astype(np.float32),cv2.CV_32F,1,0,ksize=3)
        gy=cv2.Sobel(c.astype(np.float32),cv2.CV_32F,0,1,ksize=3)
        mag=np.hypot(gx,gy); sel=mag>np.percentile(mag,75)
        if sel.sum()<10: return 0.0
        ang=(np.arctan2(gy[sel],gx[sel])+np.pi)%(np.pi)
        h,_=np.histogram(ang,bins=12,range=(0,np.pi)); p=h[h>0].astype(float); p/=p.sum()
        return float(-(p*np.log2(p)).sum())
    raise ValueError(name)

def random_boxes(shape,box,n,rng):
    H,W=shape; x0,y0,x1,y1=box; h=y1-y0; w=x1-x0
    out=[]
    for _ in range(n):
        x=int(rng.integers(0,max(1,W-w+1))); y=int(rng.integers(0,max(1,H-h+1)))
        out.append((x,y,x+w,y+h))
    return out

def upper_p(obs,null):
    return float((1+sum(v>=obs-1e-15 for v in null))/(1+len(null)))

def region_test(gray,gray2,box,mname,seed):
    rng=np.random.default_rng(seed)
    obs=metric(crop(gray,box),mname)
    obs2=metric(crop(gray2,box),mname)
    boxes=random_boxes(gray.shape,box,N_WINDOW_NULL,rng)
    n0=[metric(crop(gray,b),mname) for b in boxes]
    n1=[metric(crop(gray2,b),mname) for b in boxes]
    p=upper_p(obs,n0); p2=upper_p(obs2,n1)
    return {"statistic":obs,"p_value":p,"lossy_statistic":obs2,"lossy_p_value":p2,
            "robust":bool(p2<=0.10 if p<=0.10 else abs(obs2-obs)<=0.25*(abs(obs)+1e-9)),
            "null_median":float(np.median(n0))}

def reflect_stat(gray,x0,x1,kind):
    u=gray[0:320,x0:x1]
    d=np.flipud(gray[320:640,x0:x1])
    if kind=="edge":
        u=edge(u).astype(float); d=edge(d).astype(float)
    return abs(safe_corr(u,d))

def reflection_test(gray,gray2,x0,x1,kind):
    obs=reflect_stat(gray,x0,x1,kind); obs2=reflect_stat(gray2,x0,x1,kind)
    lower=gray[320:640,x0:x1].copy()
    lower2=gray2[320:640,x0:x1].copy()
    width=x1-x0
    shifts=np.unique(np.linspace(max(7,width//30),max(8,width-7),160,dtype=int))
    def null_for(g,low):
        u=g[0:320,x0:x1]
        if kind=="edge": u=edge(u).astype(float)
        vals=[]
        for s in shifts:
            d=np.flipud(np.roll(low,s,axis=1))
            if kind=="edge": d=edge(d.astype(np.uint8)).astype(float)
            vals.append(abs(safe_corr(u,d)))
        return vals
    n0=null_for(gray,lower); n1=null_for(gray2,lower2)
    p=upper_p(obs,n0); p2=upper_p(obs2,n1)
    return {"statistic":obs,"p_value":p,"lossy_statistic":obs2,"lossy_p_value":p2,
            "robust":bool((obs2>0)==(obs>0) and p2<=0.10 if p<=0.10 else abs(obs2-obs)<0.15),
            "null_median":float(np.median(n0))}

def small_sails(gray):
    r=gray[360:480,367:1550]
    bw=(r<180).astype(np.uint8)
    n,lab,stats,cent=cv2.connectedComponentsWithStats(bw,8)
    cs=[]
    for i in range(1,n):
        x,y,w,h,area=map(int,stats[i])
        if area>=60 and w>=8 and h>=8:
            cs.append({"x":x+367,"y":y+360,"w":w,"h":h,"area":area,"cx":float(cent[i,0]+367)})
    cs=sorted(cs,key=lambda z:z["area"],reverse=True)[:5]
    return sorted(cs,key=lambda z:z["cx"])

def corr_abs(a,b): return abs(safe_corr(a,b))
def ap_score(v): return corr_abs(np.arange(len(v)),v)**2 if len(v)>=3 else 0.0
def sym_score(v):
    v=np.asarray(v,float); den=np.mean(np.abs(v))+1e-9
    return float(-np.mean(np.abs(v-v[::-1]))/den)

def small_sail_test(gray,gray2,kind,seed):
    cs=small_sails(gray); cs2=small_sails(gray2)
    if len(cs)<5: return {"statistic":0.0,"p_value":1.0,"lossy_statistic":0.0,"lossy_p_value":1.0,"robust":False,"note":"<5 components"}
    w=np.array([z["w"] for z in cs],float); h=np.array([z["h"] for z in cs],float); a=np.array([z["area"] for z in cs],float); x=np.array([z["cx"] for z in cs],float)
    gaps=np.diff(x)
    def calc(kind,w,h,a,x):
        gaps=np.diff(x)
        if kind=="width_ap": return ap_score(w)
        if kind=="width_trend": return corr_abs(np.arange(5),w)
        if kind=="width_symmetry": return sym_score(w)
        if kind=="width_xcorr": return corr_abs(w,x)
        if kind=="height_xcorr": return corr_abs(h,x)
        if kind=="area_xcorr": return corr_abs(a,x)
        if kind=="width_gapcorr": return corr_abs(w[:-1],gaps)
        if kind=="area_gapcorr": return corr_abs(a[:-1],gaps)
        raise ValueError(kind)
    obs=calc(kind,w,h,a,x)
    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(N_PERM):
        perm=rng.permutation(5)
        null.append(calc(kind,w[perm],h[perm],a[perm],x))
    p=upper_p(obs,null)
    if len(cs2)>=5:
        w2=np.array([z["w"] for z in cs2],float); h2=np.array([z["h"] for z in cs2],float); a2=np.array([z["area"] for z in cs2],float); x2=np.array([z["cx"] for z in cs2],float)
        obs2=calc(kind,w2,h2,a2,x2)
    else: obs2=0.0
    return {"statistic":obs,"p_value":p,"lossy_statistic":obs2,"lossy_p_value":None,
            "robust":bool(len(cs2)==5 and abs(obs2-obs)<=0.25*(abs(obs)+0.05)),
            "components":cs,"lossy_components":cs2}

def building_arrays():
    g=json.loads(GEOM.read_text())
    bs=g["buildings"]
    width=np.array([b["x1"]-b["x0"] for b in bs],float)
    height=np.array([b["bottom_y"]-b["roof_y"] for b in bs],float)
    roof=np.array([b["roof_y"] for b in bs],float)
    area=width*height
    aspect=width/height
    return {"width":width,"height":height,"roof":roof,"area":area,"aspect":aspect}

def alternation(v):
    d=np.diff(v); s=np.sign(d); nz=s[s!=0]
    return float(np.mean(nz[1:]!=nz[:-1])) if len(nz)>1 else 0.0

def building_test(kind,seed):
    A=building_arrays()
    base,op=kind.split("_",1)
    v=A[base]
    if op=="alternation": calc=lambda z:alternation(z)
    elif op=="trend": calc=lambda z:corr_abs(z,np.arange(len(z)))
    else: raise ValueError(kind)
    obs=calc(v); rng=np.random.default_rng(seed)
    null=[calc(v[rng.permutation(len(v))]) for _ in range(N_PERM)]
    return {"statistic":obs,"p_value":upper_p(obs,null),"lossy_statistic":obs,"lossy_p_value":None,"robust":True,"null_median":float(np.median(null))}

def robustness_control(gray,gray2,kind):
    if kind=="hv":
        s31=json.loads((ROOT/"analysis"/"runs"/"stage31-format-invariance"/"result.json").read_text())
        val=float(np.mean([min(v["fourier_agreement"],v["morph_agreement"])/12 for v in s31["variants"] if v["variant"]!="original"]))
        return {"statistic":val,"p_value":None,"robust":val>=0.9,"control":True}
    if kind=="large_sail_edge":
        a=metric(crop(gray,LARGE),"edge_density"); b=metric(crop(gray2,LARGE),"edge_density")
    elif kind=="skyline_glyph":
        a=metric(crop(gray,SEMANTIC["skyline"]),"glyph"); b=metric(crop(gray2,SEMANTIC["skyline"]),"glyph")
    elif kind in ("reflection_gray","reflection_edge"):
        a=reflect_stat(gray,800,1200,"gray" if kind.endswith("gray") else "edge")
        b=reflect_stat(gray2,800,1200,"gray" if kind.endswith("gray") else "edge")
    elif kind=="small_sail_count":
        a=float(len(small_sails(gray))); b=float(len(small_sails(gray2)))
    elif kind=="large_sail_xsym":
        a=metric(crop(gray,LARGE),"x_symmetry"); b=metric(crop(gray2,LARGE),"x_symmetry")
    elif kind=="large_sail_spectral":
        a=metric(crop(gray,LARGE),"spectral_peak"); b=metric(crop(gray2,LARGE),"spectral_peak")
    else: raise ValueError(kind)
    rel=abs(b-a)/(abs(a)+1e-9)
    return {"statistic":a,"lossy_statistic":b,"relative_change":rel,"p_value":None,"robust":bool(rel<=0.30 or (kind=="small_sail_count" and a==b)),"control":True}

def bh_q(results):
    idx=[i for i,r in enumerate(results) if r.get("p_value") is not None]
    m=len(idx)
    order=sorted(idx,key=lambda i:results[i]["p_value"])
    qs=[None]*len(results); prev=1.0
    for rank_rev,i in enumerate(reversed(order),1):
        rank=m-rank_rev+1
        q=min(prev,results[i]["p_value"]*m/rank)
        qs[i]=q; prev=q
    return qs

def main():
    manifest=json.loads(MANIFEST.read_text())
    gray=load_gray(); gray2=lossy(gray)
    results=[]
    for e in manifest["experiments"]:
        stage=int(e["stage"]); method=e["method"]; seed=378700+stage
        try:
            if method.startswith("region_random_window:"):
                r=region_test(gray,gray2,LARGE,method.split(":",1)[1],seed)
            elif method.startswith("reflection_shift_null:"):
                idx=stage-47
                band=idx%4
                x0=band*400; x1=x0+400
                kind=method.rsplit(":",1)[1]
                r=reflection_test(gray,gray2,x0,x1,kind)
            elif method.startswith("small_sails_permutation:"):
                r=small_sail_test(gray,gray2,method.rsplit(":",1)[1],seed)
            elif method.startswith("building_permutation:"):
                r=building_test(method.rsplit(":",1)[1],seed)
            elif method.startswith("semantic_region_random:"):
                parts=method.split(":")
                mname=parts[1]; region=parts[2]
                r=region_test(gray,gray2,SEMANTIC[region],mname,seed)
            elif method.startswith("robustness_control:"):
                r=robustness_control(gray,gray2,method.rsplit(":",1)[1])
            else:
                raise ValueError("unknown method "+method)
            rec={**e,**r,"error":None}
        except Exception as ex:
            rec={**e,"p_value":1.0,"robust":False,"error":repr(ex)}
        results.append(rec)

    qs=bh_q(results)
    for i,r in enumerate(results):
        r["q_value"]=qs[i]
        if r.get("control"):
            r["classification"]="CONTROL_PASS" if r.get("robust") else "CONTROL_FAIL"
        elif r.get("error"):
            r["classification"]="ERROR"
        elif r["q_value"] is not None and r["q_value"]<=0.05 and r.get("robust",True):
            r["classification"]="PROMOTED"
        elif r["p_value"]<=0.05:
            r["classification"]="INTERESTING"
        else:
            r["classification"]="NULL"

        d=OUT/f"exp_{r['stage']:03d}"
        d.mkdir(parents=True,exist_ok=True)
        (d/"result.json").write_text(json.dumps(r,indent=2)+"\n")
        (d/"REPORT.md").write_text(
            f"# {r['id']} — {r['name']}\n\n"
            f"- family: **{r['family']}**\n"
            f"- method: `{r['method']}`\n"
            f"- statistic: **{r.get('statistic')}**\n"
            f"- p: **{r.get('p_value')}**\n"
            f"- q: **{r.get('q_value')}**\n"
            f"- robust: **{r.get('robust')}**\n"
            f"- classification: **{r['classification']}**\n"
            + (f"- error: `{r['error']}`\n" if r.get("error") else "")
        )

    counts={}
    fam={}
    for r in results:
        counts[r["classification"]]=counts.get(r["classification"],0)+1
        fam.setdefault(r["family"],{"count":0,"promoted":0,"interesting":0,"errors":0})
        fam[r["family"]]["count"]+=1
        fam[r["family"]]["promoted"]+=r["classification"]=="PROMOTED"
        fam[r["family"]]["interesting"]+=r["classification"]=="INTERESTING"
        fam[r["family"]]["errors"]+=r["classification"]=="ERROR"

    ranked=sorted([r for r in results if not r.get("control")],key=lambda r:(r.get("q_value",1.0),r.get("p_value",1.0),r["stage"]))
    aggregate={
      "experiment_id":"A11-EXP-087",
      "scope":"aggregate ranking of A11-EXP-037..086 with BH-FDR across non-control p-values; safe diagnostics only",
      "counts":counts,
      "family_summary":fam,
      "top20":[{k:r.get(k) for k in ("id","stage","family","name","statistic","p_value","q_value","robust","classification","error")} for r in ranked[:20]],
      "all_results":results,
      "decision_rule":"PROMOTED requires BH q<=0.05 and robustness when applicable. INTERESTING is nominal p<=0.05 but not FDR-promoted. Controls are excluded from FDR.",
    }
    (OUT/"result.json").write_text(json.dumps(aggregate,indent=2)+"\n")
    md=[
      "# A11-EXP-087 — Superbatch 37–86 aggregate",
      "",
      f"- Total subexperiments: **{len(results)}**",
      f"- FDR-tested hypotheses: **{sum(r.get('p_value') is not None and not r.get('control') for r in results)}**",
      f"- PROMOTED: **{counts.get('PROMOTED',0)}**",
      f"- INTERESTING: **{counts.get('INTERESTING',0)}**",
      f"- NULL: **{counts.get('NULL',0)}**",
      f"- CONTROL_PASS: **{counts.get('CONTROL_PASS',0)}**",
      f"- CONTROL_FAIL: **{counts.get('CONTROL_FAIL',0)}**",
      f"- ERROR: **{counts.get('ERROR',0)}**",
      "",
      "## Family summary","",
      "| family | n | promoted | interesting | errors |","|:---|---:|---:|---:|---:|"
    ]
    for k,v in sorted(fam.items()):
        md.append(f"| {k} | {v['count']} | {v['promoted']} | {v['interesting']} | {v['errors']} |")
    md += ["","## Top ranked non-control experiments","",
           "| id | family | name | p | q | robust | class |","|:---|:---|:---|---:|---:|:---:|:---|"]
    for r in ranked[:20]:
        md.append(f"| {r['id']} | {r['family']} | {r['name']} | {r.get('p_value',1):.6f} | {r.get('q_value',1):.6f} | {r.get('robust')} | {r['classification']} |")
    md += ["","No result in this batch constitutes or reconstructs private-key material. The aggregate is for hypothesis prioritization only.",""]
    (OUT/"SUPER_REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","aggregate":"A11-EXP-087","counts":counts,"top":[(r["id"],r["p_value"],r["q_value"],r["classification"]) for r in ranked[:5]]}))

if __name__=="__main__":
    main()
