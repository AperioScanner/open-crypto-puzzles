#!/usr/bin/env python3
"""Stage 36: multiscale visual-reveal audit of the large sailboat.

Safe, non-cryptographic diagnostic. The goal is to test a long-standing community
hypothesis that the dense large sailboat may conceal human-visible text or another
secondary pattern. This stage does not OCR, decode secret material, or construct
private-key candidates.

It applies a fixed family of visual transforms to the measured large-sailboat bbox and
three same-size scene controls, ranks only generic glyph-line connected-component
structure, repeats after JPEG85+resampling, and saves contact sheets for direct review.
"""
from __future__ import annotations
import io, json, math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
GEOM=ROOT/"data"/"geometry.json"
OUT=ROOT/"analysis"/"runs"/"stage36-large-boat-visual-reveal"
OUT.mkdir(parents=True,exist_ok=True)

# Large sailboat is 315x279. Controls are predeclared same-size regions.
REGIONS={
    "large_sailboat":(44,320,359,599),
    "skyline_control":(884,20,1199,299),
    "jetty_control":(1000,360,1315,639),
    "water_control":(400,500,715,779),
}
THRESHOLDS=(80,110,140,170,200,230,245)
BANDS=((0,63),(64,127),(128,191),(192,223),(224,239),(240,247),(248,254))
DOGS=((1.0,3.0),(2.0,6.0),(4.0,12.0))

def load_gray():
    return np.array(Image.open(SOURCE).convert("L"))

def jpeg85_resample(gray):
    im=Image.fromarray(gray,mode="L")
    buf=io.BytesIO()
    im.save(buf,format="JPEG",quality=85,optimize=False,progressive=False)
    buf.seek(0)
    j=Image.open(buf).convert("L")
    h,w=gray.shape
    small=j.resize((round(w*0.75),round(h*0.75)),Image.Resampling.LANCZOS)
    return np.array(small.resize((w,h),Image.Resampling.LANCZOS))

def crop(gray,box):
    x0,y0,x1,y1=box
    return gray[y0:y1,x0:x1]

def normalize_u8(x):
    x=x.astype(np.float32)
    lo=float(np.percentile(x,1))
    hi=float(np.percentile(x,99))
    if hi<=lo+1e-9:
        return np.zeros_like(x,dtype=np.uint8)
    return np.clip((x-lo)/(hi-lo)*255,0,255).astype(np.uint8)

def transform_family(c):
    out={}
    # Threshold family
    for t in THRESHOLDS:
        out[f"thr_{t}"]=((c<t).astype(np.uint8)*255)
    # Narrow grayscale bands
    for lo,hi in BANDS:
        out[f"band_{lo}_{hi}"]=(((c>=lo)&(c<=hi)).astype(np.uint8)*255)
    # Difference-of-Gaussian residuals, binarized at fixed percentile
    cf=c.astype(np.float32)
    for s1,s2 in DOGS:
        a=cv2.GaussianBlur(cf,(0,0),s1)
        b=cv2.GaussianBlur(cf,(0,0),s2)
        d=np.abs(a-b)
        q=float(np.percentile(d,85))
        out[f"dog_{int(s1)}_{int(s2)}"]=((d>=q).astype(np.uint8)*255)
    # Remove long horizontal / vertical strokes from a medium threshold mask.
    ink=((c<180).astype(np.uint8)*255)
    oh=cv2.morphologyEx(ink,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(25,1)))
    ov=cv2.morphologyEx(ink,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(1,25)))
    long=np.maximum(oh,ov)
    residual=cv2.subtract(ink,long)
    out["line_suppressed_180"]=residual
    # CLAHE reveal, followed by fixed threshold.
    clahe=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8)).apply(c)
    out["clahe_thr_128"]=((clahe<128).astype(np.uint8)*255)
    return out

def glyph_line_metrics(mask):
    # Generic text-like component diagnostic only; not OCR.
    bw=(mask>0).astype(np.uint8)
    n,lab,stats,cent=cv2.connectedComponentsWithStats(bw,8)
    comps=[]
    for i in range(1,n):
        x,y,w,h,area=map(int,stats[i])
        if not (5<=area<=500 and 2<=w<=60 and 4<=h<=45):
            continue
        ar=w/max(1,h)
        if not (0.12<=ar<=8.0):
            continue
        comps.append((x,y,w,h,area,float(cent[i,0]),float(cent[i,1])))
    if not comps:
        return {
            "eligible_components":0,
            "max_aligned_count":0,
            "alignment_score":0.0,
            "aligned_x_coverage":0.0,
        }
    # Fixed 14-px y-center bins approximate a text baseline band without fitting to data.
    bins={}
    for c in comps:
        key=int(c[6]//14)
        bins.setdefault(key,[]).append(c)
    best=max(bins.values(),key=lambda z:len(z))
    xs=[c[0] for c in best]
    xe=[c[0]+c[2] for c in best]
    coverage=(max(xe)-min(xs))/mask.shape[1] if len(best)>=2 else 0.0
    score=(len(best)*math.sqrt(max(coverage,1e-9)))/math.sqrt(len(comps)+1.0)
    return {
        "eligible_components":len(comps),
        "max_aligned_count":len(best),
        "alignment_score":float(score),
        "aligned_x_coverage":float(coverage),
    }

def analyze(gray):
    by_region={}
    for rname,box in REGIONS.items():
        c=crop(gray,box)
        tf=transform_family(c)
        by_region[rname]={}
        for name,mask in tf.items():
            by_region[rname][name]={
                "metrics":glyph_line_metrics(mask),
                "mask":mask,
            }
    return by_region

def score_table(analysis):
    names=sorted(next(iter(analysis.values())).keys())
    rows=[]
    for name in names:
        vals=[]
        for rname in REGIONS:
            m=analysis[rname][name]["metrics"]
            vals.append((rname,m["alignment_score"]))
        vals_sorted=sorted(vals,key=lambda z:z[1],reverse=True)
        target=dict(vals)["large_sailboat"]
        rank=1+sum(v>target+1e-12 for _,v in vals)
        control_max=max(v for r,v in vals if r!="large_sailboat")
        rows.append({
            "transform":name,
            "target_score":float(target),
            "target_rank":int(rank),
            "control_max_score":float(control_max),
            "target_minus_control_max":float(target-control_max),
            "region_scores":{r:float(v) for r,v in vals},
        })
    return rows

def render_mask(mask,size=(315,279)):
    im=Image.fromarray(255-mask).convert("L")
    return im.resize(size,Image.Resampling.NEAREST)

def target_contact(analysis,score_rows,filename):
    ordered=sorted(score_rows,key=lambda r:(r["target_rank"],-r["target_minus_control_max"],r["transform"]))
    cols=4
    tile_w,tile_h=330,315
    rows_n=math.ceil(len(ordered)/cols)
    sheet=Image.new("L",(cols*tile_w,rows_n*tile_h),255)
    draw=ImageDraw.Draw(sheet)
    for i,r in enumerate(ordered):
        rr=i//cols; cc=i%cols
        x=cc*tile_w; y=rr*tile_h
        mask=analysis["large_sailboat"][r["transform"]]["mask"]
        im=render_mask(mask,(315,279))
        sheet.paste(im,(x,y))
        draw.text((x+4,y+282),f"{r['transform']} rank={r['target_rank']} d={r['target_minus_control_max']:.2f}",fill=0)
    sheet.save(OUT/filename)

def comparison_sheet(analysis,score_rows,filename):
    top=sorted(score_rows,key=lambda r:r["target_minus_control_max"],reverse=True)[:8]
    region_names=list(REGIONS.keys())
    cell_w,cell_h=250,245
    label_h=22
    sheet=Image.new("L",(len(region_names)*cell_w,len(top)*(cell_h+label_h)),255)
    draw=ImageDraw.Draw(sheet)
    for ri,row in enumerate(top):
        y=ri*(cell_h+label_h)
        for ci,rname in enumerate(region_names):
            x=ci*cell_w
            mask=analysis[rname][row["transform"]]["mask"]
            im=render_mask(mask,(cell_w,cell_h))
            sheet.paste(im,(x,y))
            if ri==0:
                draw.text((x+4,y+2),rname,fill=0)
        draw.text((4,y+cell_h+2),f"{row['transform']} target-control={row['target_minus_control_max']:.3f}",fill=0)
    sheet.save(OUT/filename)

def main():
    geom=json.loads(GEOM.read_text())
    measured=geom["large_sailboat"]
    measured_box=(measured["x0"],measured["y0"],measured["x1"],measured["y1"])
    if measured_box!=REGIONS["large_sailboat"]:
        raise SystemExit(f"large-sailboat bbox mismatch: {measured_box}")

    original=load_gray()
    transformed=jpeg85_resample(original)
    a0=analyze(original)
    a1=analyze(transformed)
    s0=score_table(a0)
    s1=score_table(a1)
    map1={r["transform"]:r for r in s1}

    target_rank1=sum(r["target_rank"]==1 for r in s0)
    target_rank1_lossy=sum(r["target_rank"]==1 for r in s1)
    replicated_rank1=sum(r["target_rank"]==1 and map1[r["transform"]]["target_rank"]==1 for r in s0)

    # Family-level counts reduce over-reading multiple thresholds from one family.
    def fam(name):
        if name.startswith("thr_"): return "threshold"
        if name.startswith("band_"): return "intensity_band"
        if name.startswith("dog_"): return "dog"
        if name.startswith("line_"): return "line_suppression"
        if name.startswith("clahe_"): return "clahe"
        return "other"
    fams={}
    for r in s0:
        f=fam(r["transform"])
        fams.setdefault(f,{"original_rank1":0,"replicated_rank1":0,"n":0})
        fams[f]["n"]+=1
        if r["target_rank"]==1:
            fams[f]["original_rank1"]+=1
        if r["target_rank"]==1 and map1[r["transform"]]["target_rank"]==1:
            fams[f]["replicated_rank1"]+=1

    manual_review_priority=bool(
        sum(v["replicated_rank1"]>0 for v in fams.values())>=2
        and replicated_rank1>=3
    )

    result={
        "experiment_id":"A11-EXP-036",
        "scope":"visual-reveal diagnostics on large sailboat versus fixed same-size scene controls; no OCR, payload decoding, or private-key operations",
        "regions":{k:list(v) for k,v in REGIONS.items()},
        "transforms":len(s0),
        "original_scores":s0,
        "lossy_scores":s1,
        "family_summary":fams,
        "target_rank1_original":target_rank1,
        "target_rank1_lossy":target_rank1_lossy,
        "replicated_target_rank1":replicated_rank1,
        "manual_review_priority_rule":"priority if >=2 transform families each contain a target-rank1 result that remains rank1 after JPEG85+resampling, and >=3 individual transforms replicate rank1",
        "manual_review_priority":manual_review_priority,
        "artifacts":[
            "large-boat-contact-original.png",
            "large-boat-contact-lossy.png",
            "top-comparison-original.png",
            "top-comparison-lossy.png",
        ],
        "interpretation_guard":"The component metric is only a ranking heuristic. Any positive signal requires direct visual inspection; it does not demonstrate readable text or secret material.",
    }
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")

    target_contact(a0,s0,"large-boat-contact-original.png")
    target_contact(a1,s1,"large-boat-contact-lossy.png")
    comparison_sheet(a0,s0,"top-comparison-original.png")
    comparison_sheet(a1,s1,"top-comparison-lossy.png")

    top=sorted(s0,key=lambda r:r["target_minus_control_max"],reverse=True)[:12]
    md=[
        "# Stage 36 — large-sailboat multiscale visual-reveal audit",
        "",
        "**Experiment:** A11-EXP-036",
        "",
        f"- Fixed transforms: **{len(s0)}**",
        f"- Target rank-1 transforms, original: **{target_rank1}**",
        f"- Target rank-1 transforms, lossy: **{target_rank1_lossy}**",
        f"- Rank-1 transforms replicated before/after lossy conversion: **{replicated_rank1}**",
        f"- Manual-review priority rule: **{manual_review_priority}**",
        "",
        "## Family summary",
        "",
        "| family | transforms | original rank1 | replicated rank1 |",
        "|:---|---:|---:|---:|",
    ]
    for k,v in sorted(fams.items()):
        md.append(f"| {k} | {v['n']} | {v['original_rank1']} | {v['replicated_rank1']} |")
    md += [
        "",
        "## Strongest target-vs-control rankings",
        "",
        "| transform | target rank | target score | max control | difference | lossy rank |",
        "|:---|---:|---:|---:|---:|---:|",
    ]
    for r in top:
        md.append(f"| {r['transform']} | {r['target_rank']} | {r['target_score']:.4f} | {r['control_max_score']:.4f} | {r['target_minus_control_max']:.4f} | {map1[r['transform']]['target_rank']} |")
    md += [
        "",
        "## Interpretation",
        "",
        "This is a reveal-and-ranking stage, not a text decoder. Connected-component alignment can be produced by ordinary drawing strokes, so the decisive next step—if the target is consistently unusual—is direct visual review of the generated contact sheets and only then a narrower predeclared follow-up.",
        "",
        "Artifacts:",
        "- `large-boat-contact-original.png`",
        "- `large-boat-contact-lossy.png`",
        "- `top-comparison-original.png`",
        "- `top-comparison-lossy.png`",
        "",
    ]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({
        "status":"ok",
        "experiment_id":"A11-EXP-036",
        "rank1_original":target_rank1,
        "rank1_lossy":target_rank1_lossy,
        "replicated_rank1":replicated_rank1,
        "manual_review_priority":manual_review_priority,
    }))

if __name__=="__main__":
    main()
