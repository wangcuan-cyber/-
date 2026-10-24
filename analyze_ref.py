# -*- coding: utf-8 -*-
"""Analyze the Kimi reference sheet: panels, silhouettes, skin/face masses."""
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\xt621\Documents\deepseek-harness\default-workspace\kimi_ref.webp"

im = Image.open(SRC).convert("RGBA")
W, H = im.size
a = np.asarray(im)
al = a[..., 3]
print("size %dx%d  mode RGBA" % (W, H))

mask = al > 16
cols = mask.sum(axis=0)
rows = mask.sum(axis=1)
print("content columns", int((cols > 0).sum()), "content rows", int((rows > 0).sum()))

# column gaps
empty = cols <= 0
runs = []
i = 0
while i < W:
    j = i
    while j < W and empty[j] == empty[i]:
        j += 1
    runs.append((empty[i], i, j - 1, j - i))
    i = j
print("column runs (empty, x0..x1, len):")
for e, x0, x1, n in runs:
    if n >= 6:
        print("  %-5s %4d..%4d  len=%d" % ("gap" if e else "ink", x0, x1, n))

# split panels at wide empty gaps
gaps = [(x0, x1) for e, x0, x1, n in runs if e and n >= 12]
bounds = []
start = 0
for g0, g1 in gaps:
    if g0 - start > 40:
        bounds.append((start, g0 - 1))
    start = g1 + 1
if W - start > 40:
    bounds.append((start, W - 1))
print("panels:", bounds)

# skin mask (warm tones)
r = a[..., 0].astype(np.float32); g = a[..., 1].astype(np.float32); b = a[..., 2].astype(np.float32)
skin = (al > 200) & (r > 150) & (r > g + 12) & (g > b - 5) & (b > 70) & (b < 220)
print("skin px", int(skin.sum()), "frac %.4f" % (skin.sum() / max(1, (al > 200).sum())))

for pi, (x0, x1) in enumerate(bounds):
    sub = mask[:, x0:x1 + 1]
    ys, xs = np.where(sub)
    if len(xs) == 0:
        continue
    bw = xs.max() - xs.min() + 1
    bh = ys.max() - ys.min() + 1
    sk = skin[:, x0:x1 + 1]
    if sk.any():
        sy, sx = np.where(sk)
        scx = (sx.mean() + x0)
        scy = sy.mean()
        relx = (scx - (x0 + xs.min())) / bw
        print("panel %d  x %d..%d  bbox %dx%d  aspect %.3f  skin=%d  skin_cx_rel=%.2f skin_cy=%.1f"
              % (pi, x0, x1, bw, bh, bw / bh, int(sk.sum()), relx, scy))
    else:
        print("panel %d  x %d..%d  bbox %dx%d  aspect %.3f  skin=0"
              % (pi, x0, x1, bw, bh, bw / bh))

# ascii silhouette for each panel
def ascii_panel(x0, x1, width=46):
    sub = mask[:, x0:x1 + 1]
    ys, xs = np.where(sub)
    if len(xs) == 0:
        return
    y0, y1 = ys.min(), ys.max()
    sub = sub[y0:y1 + 1, xs.min():xs.max() + 1]
    h, w = sub.shape
    rows_n = max(10, int(width * h / w * 0.5))
    img = Image.fromarray((sub * 255).astype(np.uint8)).resize((width, rows_n), Image.BILINEAR)
    arr = np.asarray(img) > 80
    print("--- panel x%d..%d  ascii %dx%d" % (x0, x1, width, rows_n))
    for row in arr:
        print("".join("#" if v else "." for v in row))

for pi, (x0, x1) in enumerate(bounds):
    ascii_panel(x0, x1)
