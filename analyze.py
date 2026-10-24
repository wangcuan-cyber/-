# -*- coding: utf-8 -*-
"""Inspect the GPT Q-sheet: figure split, bbox, symmetry, ASCII silhouette."""
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

SHEET = r"C:\Users\xt621\Documents\deepseek-harness\default-workspace\apk_work\gpt_model\ref_att.webp"


def ascii_alpha(a, cols=56, rows=34, chars=" .:-=+*#%@"):
    h, w = a.shape
    out = []
    for r in range(rows):
        y0, y1 = int(r * h / rows), max(int((r + 1) * h / rows), int(r * h / rows) + 1)
        line = []
        for c in range(cols):
            x0, x1 = int(c * w / cols), max(int((c + 1) * w / cols), int(c * w / cols) + 1)
            v = a[y0:y1, x0:x1].mean() / 255.0
            line.append(chars[min(len(chars) - 1, int(v * (len(chars) - 1) + 0.5))])
        out.append("".join(line).rstrip())
    return "\n".join(out)


def ascii_gray(rgb, cols=44, rows=30):
    g = rgb.mean(axis=2)
    return ascii_alpha(g, cols, rows)


def main():
    im = Image.open(SHEET).convert("RGBA")
    a = np.asarray(im)
    al = a[..., 3]
    m = al > 12
    print("sheet", im.size, "alpha frac %.3f" % (m.mean()))

    # column gaps -> panels
    col = m.sum(axis=0)
    thr = 3
    panels, start = [], 0
    for x in range(len(col)):
        if col[x] <= thr and start is None:
            start = x
        elif col[x] > thr and start is not None:
            if x - start > 30:
                panels.append((start, x))
            start = None
    gaps = [(p[0], p[1]) for p in panels]
    print("column gaps:", gaps)

    # split by the middle of each wide gap
    cuts = [0]
    for g0, g1 in gaps:
        if g0 > 100 and g1 < m.shape[1] - 100:
            cuts.append((g0 + g1) // 2)
    cuts.append(m.shape[1])
    print("cuts:", cuts)

    for i in range(len(cuts) - 1):
        x0, x1 = cuts[i], cuts[i + 1]
        sub = m[:, x0:x1]
        ys, xs = np.where(sub)
        if len(xs) == 0:
            continue
        bx0, bx1 = x0 + xs.min(), x0 + xs.max() + 1
        by0, by1 = ys.min(), ys.max() + 1
        fig = a[by0:by1, bx0:bx1]
        fa = fig[..., 3]
        fm = fa > 12
        # symmetry of alpha
        flip = fm[:, ::-1]
        inter = (fm & flip).sum()
        union = (fm | flip).sum()
        print("\n== figure %d  x %d..%d  bbox %dx%d  aspect %.3f  alpha-sym %.3f" % (
            i, bx0, bx1, bx1 - bx0, by1 - by0, (bx1 - bx0) / (by1 - by0), inter / max(1, union)))
        sub_rgb = fig[..., :3].astype(np.float32)
        print("mean rgb inside", sub_rgb[fm].mean(axis=0).round(0).tolist())
        print(ascii_alpha(fa, 44, 30))
        print("-- luminance --")
        print(ascii_gray(sub_rgb, 44, 30))


if __name__ == "__main__":
    main()
