# -*- coding: utf-8 -*-
"""Per-panel analysis: symmetry, silhouette, ASCII preview, palette."""
import os
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

SHEET = "ref_att.webp"
PANELS = [(0, 899), (899, 1715), (1715, 2559)]
CHARS = " .:-=+*#%@"

im = Image.open(SHEET).convert("RGBA")
a = np.asarray(im)
al = a[..., 3].astype(np.float32) / 255.0
rgb = a[..., :3].astype(np.float32)


def ascii_of(mask, w=44):
    h = mask.shape[0]
    hh = max(1, int(round(w * h / mask.shape[1] * 0.5)))
    img = Image.fromarray((mask * 255).astype(np.uint8)).resize((w, hh), Image.BOX)
    m = np.asarray(img).astype(np.float32) / 255.0
    return ["".join(CHARS[min(len(CHARS) - 1, int(v * (len(CHARS) - 1) + 0.5))] for v in row) for row in m]


def hue_name(c):
    r, g, b = c
    mx, mn = max(c), min(c)
    if mx < 45:
        return "black"
    if mn > 225:
        return "white"
    if mx - mn < 22:
        return "grey"
    if r >= g and r >= b:
        return "red" if g < b + 20 else "orange/yellow"
    if g >= r and g >= b:
        return "green"
    if b >= r and b >= g:
        return "blue" if r < g else "violet"
    return "?"


for i, (x0, x1) in enumerate(PANELS):
    al_p = al[:, x0:x1]
    m = al_p > 0.35
    if m.sum() == 0:
        continue
    ys, xs = np.where(m)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    w = bx1 - bx0 + 1
    h = by1 - by0 + 1
    print("\n=== panel %d  x %d..%d ===" % (i, x0, x1))
    print("bbox w=%d h=%d  w/h=%.3f  cx=%.1f  ink %.3f" % (w, h, w / h, (bx0 + bx1) / 2 + x0, m.mean()))

    crop = al_p[by0:by1 + 1, bx0:bx1 + 1]
    flipped = crop[:, ::-1]
    lo = min(crop.shape[1], flipped.shape[1])
    sym = 1.0 - np.abs(crop[:, :lo] - flipped[:, :lo]).mean()
    print("horizontal symmetry %.3f" % sym)

    # width profile in 10 vertical bands
    rows = crop > 0.35
    prof = [rows[int(k * rows.shape[0] / 10):int((k + 1) * rows.shape[0] / 10)].sum(axis=1).mean() / w for k in range(10)]
    print("width bands:", " ".join("%.2f" % v for v in prof))

    # palette of the solid core
    core = crop > 0.9
    cols = rgb[by0:by1 + 1, bx0:bx1 + 1][core]
    if len(cols):
        q = (cols // 24 * 24).astype(np.int32)
        uniq, cnt = np.unique(q, axis=0, return_counts=True)
        order = np.argsort(cnt)[::-1][:6]
        print("core palette:", ", ".join("#%02x%02x%02x %s %.2f" % (
            uniq[j][0], uniq[j][1], uniq[j][2], hue_name(tuple(uniq[j])), cnt[j] / cnt.sum()) for j in order))

    for line in ascii_of(crop, 40):
        print("   |" + line + "|")
