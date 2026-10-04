#!/usr/bin/env python3
"""Stage 26: 2-D autocorrelation and Fourier diagnostics for bitplanes/residuals."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"clues"/"arweave-puzzle-11.png"
OUT=ROOT/"analysis"/"runs"/"stage26-spectral-bitplanes"
OUT.mkdir(parents=True,exist_ok=True)

def top_lags_1d(v,maxlag=128):
    x=v.astype(np.float64)
    x-=x.mean()
    den=float(np.dot(x,x))+1e-12
    out=[]
    for lag in range(1,min(maxlag+1,len(x))):
        c=float(np.dot(x[:-lag],x[lag:])/den)
        out.append((lag,c))
    return sorted(out,key=lambda z:abs(z[1]),reverse=True)[:10]

def spectral(arr):
    x=arr.astype(np.float64)
    x-=x.mean()
    H,W=x.shape
    wy=np.hanning(H)[:,None]; wx=np.hanning(W)[None,:]
    p=np.abs(np.fft.fftshift(np.fft.fft2(x*wy*wx)))**2
    cy,cx=H//2,W//2
    yy,xx=np.indices(p.shape)
    r=np.hypot(xx-cx,yy-cy)
    valid=r>=3
    vals=p[valid]
    med=float(np.median(vals))+1e-12
    q=float(np.percentile(vals,99.9))
    peak=float(vals.max())
    idx=np.unravel_index(np.argmax(np.where(valid,p,-1)),p.shape)
    dy=int(idx[0]-cy); dx=int(idx[1]-cx)
    row=arr.mean(axis=0)
    col=arr.mean(axis=1)
    return {
      "peak_over_median":peak/med,
      "p999_over_median":q/med,
      "peak_frequency_offset":[dx,dy],
      "row_projection_top_lags":top_lags_1d(row),
      "col_projection_top_lags":top_lags_1d(col),
    }

def main():
    a=np.array(Image.open(SOURCE))
    L=a[:,:,0]; A=a[:,:,1]
    planes=[]
    for ch,arr,bits in (("L",L,range(4)),("A",A,range(2))):
        for bit in bits:
            b=((arr>>bit)&1).astype(np.float32)
            planes.append({"channel":ch,"bit":bit,"spectral":spectral(b)})
    # residual low3 value map
    low3=(L&7).astype(np.float32)/7.0
    residual=spectral(low3)
    result={"experiment_id":"A11-EXP-026","scope":"2-D Fourier and 1-D projection autocorrelation diagnostics only; no payload reconstruction or private-key operations","bitplanes":planes,"low3_residual":residual}
    (OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    md=["# Stage 26 — spectral and autocorrelation diagnostics","",
        "**Experiment:** A11-EXP-026","",
        "| channel | bit | peak/median | p99.9/median | peak dx,dy | top row lag | top col lag |",
        "|:---:|---:|---:|---:|:---:|:---|:---|"]
    for p in planes:
        s=p["spectral"]
        md.append(f"| {p['channel']} | {p['bit']} | {s['peak_over_median']:.1f} | {s['p999_over_median']:.1f} | {tuple(s['peak_frequency_offset'])} | {s['row_projection_top_lags'][0]} | {s['col_projection_top_lags'][0]} |")
    md += ["","## Low-3 residual","",f"- peak/median: {residual['peak_over_median']:.1f}",f"- peak frequency offset: {tuple(residual['peak_frequency_offset'])}",
           f"- strongest row lags: {residual['row_projection_top_lags'][:5]}",f"- strongest column lags: {residual['col_projection_top_lags'][:5]}","",
           "## Interpretation","",
           "Strong spectral or lag peaks identify periodic/tiled structure worth localizing, but drawing strokes, scan/render artifacts and image dimensions can also create them. Peaks are leads only when they are unusual across multiple related planes or align with independent spatial anomalies.",""]
    (OUT/"REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status":"ok","experiment_id":"A11-EXP-026","planes":len(planes)}))

if __name__=="__main__": main()
