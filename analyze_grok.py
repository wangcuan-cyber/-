# -*- coding: utf-8 -*-
"""Analyze the Grok character sheet: panel split, alignment, background."""
import numpy as np
from PIL import Image

SHEET = r"C:\Users\xt621\Desktop\桌宠软件\retouch_2026102411124249.png"
img = Image.open(SHEET).convert("RGBA")
a = np.asarray(img)
print("sheet size:", img.size, a.shape)

# background estimate from the 4 corners
h, w = a.shape[:2]
corners = [a[2,2], a[2,w-3], a[h-3,2], a[h-3,w-3], a[h//2,2], a[2,w//2]]
for c in corners:
    print("corner px:", c)

# column profile: find gaps (columns where alpha is uniformly 0 or bg)
alpha = a[..., 3]
col_nonzero = (alpha > 16).sum(axis=0)
row_nonzero = (alpha > 16).sum(axis=1)
cols = np.where(col_nonzero > 0)[0]
rows = np.where(row_nonzero > 0)[0]
print("content x range:", cols.min(), cols.max(), "y range:", rows.min(), rows.max())

# detect vertical gaps between panels: columns with few opaque pixels between content bands
gap_cols = [x for x in range(cols.min(), cols.max()+1) if col_nonzero[x] < h * 0.001]
# cluster gap columns
gaps = []
if gap_cols:
    start = gap_cols[0]; prev = gap_cols[0]
    for x in gap_cols[1:]:
        if x - prev > 10:
            gaps.append((start, prev)); start = x
        prev = x
    gaps.append((start, prev))
print("vertical gaps (x):", gaps)

gap_rows = [y for y in range(rows.min(), rows.max()+1) if row_nonzero[y] < w * 0.001]
gaps_h = []
if gap_rows:
    start = gap_rows[0]; prev = gap_rows[0]
    for y in gap_rows[1:]:
        if y - prev > 10:
            gaps_h.append((start, prev)); start = y
        prev = y
    gaps_h.append((start, prev))
print("horizontal gaps (y):", gaps_h)

# panel bounds
xs = [0] + [g[1]+1 for g in gaps] + [w]
ys = [0] + [g[1]+1 for g in gaps_h] + [h]
panels = []
for yi in range(len(ys)-1):
    for xi in range(len(xs)-1):
        panels.append((xi, yi, xs[xi], xs[xi+1], ys[yi], ys[yi+1]))
print("panels:", panels)
for (xi, yi, x0, x1, y0, y1) in panels:
    sub = a[y0:y1, x0:x1]
    alpha2 = sub[..., 3]
    nz = np.where(alpha2 > 16)
    print("panel %d (%d,%d): size %dx%d, content bbox x[%d,%d] y[%d,%d]" % (
        yi*2+xi, x0, y0, x1-x0, y1-y0,
        nz[1].min()+x0, nz[1].max()+x0, nz[0].min()+y0, nz[0].max()+y0))

# save panel crops for inspection
for (xi, yi, x0, x1, y0, y1) in panels:
    crop = img.crop((x0, y0, x1, y1))
    crop.save(r"C:\Users\xt621\Documents\deepseek-harness\default-workspace\apk_work\grok_panel_%d_%d.png" % (yi, xi))
    print("saved panel", yi, xi, crop.size)
