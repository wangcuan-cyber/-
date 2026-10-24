# -*- coding: utf-8 -*-
"""Erode the lineart away and report the remaining compact dark blobs (eyes)."""
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

SHEET = r"C:\Users\xt621\Desktop\桌宠软件\11个AI娘（Q版）\CC鲸鱼娘.png"
im = Image.open(SHEET).convert("RGBA")
PANELS = [(0, 659), (685, 1207), (1237, 1855)]


def label(mask):
    h, w = mask.shape
    seen = np.zeros_like(mask, bool)
    out = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                q = deque([(y, x)])
                seen[y, x] = True
                pix = []
                while q:
                    cy, cx = q.popleft()
                    pix.append((cy, cx))
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((ny, nx))
                ys = [p[0] for p in pix]
                xs = [p[1] for p in pix]
                out.append((len(pix), min(ys), max(ys), min(xs), max(xs)))
    return out


for i, (x0, x1) in enumerate(PANELS):
    p = im.crop((x0, 0, x1 + 1, im.size[1])).convert("RGBA")
    a = np.asarray(p)
    al = a[..., 3]
    ys, xs = np.where(al > 40)
    p = p.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    h = p.size[1]
    head = p.crop((0, 0, p.size[0], int(h * 0.45)))
    small = head.resize((head.size[0] // 4, head.size[1] // 4), Image.LANCZOS)
    sa = np.asarray(small).astype(int)
    lum = sa[..., :3] @ np.array([0.299, 0.587, 0.114])
    dark = (lum < 85) & (sa[..., 3] > 200)
    m = Image.fromarray((dark * 255).astype(np.uint8))
    for _ in range(2):
        m = m.filter(ImageFilter.MinFilter(3))
    dm = np.asarray(m) > 128
    comps = sorted(label(dm), reverse=True)[:6]
    print("panel", i, "head", head.size, "small", small.size, "dark frac %.3f" % dark.mean())
    for area, y0, y1, xa, xb in comps:
        print("   blob area %5d  bbox x %3d..%3d y %3d..%3d  w %2d h %2d  aspect %.2f" % (
            area, xa * 4, xb * 4, y0 * 4, y1 * 4, (xb - xa + 1) * 4, (y1 - y0 + 1) * 4,
            (xb - xa + 1) / max(1, (y1 - y0 + 1))))
