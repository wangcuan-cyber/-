# -*- coding: utf-8 -*-
"""ASCII silhouettes of the Gemini sheet panels (front candidates + back)."""
import os
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
COLS, ROWS = 46, 40


def ascii_art(name):
    im = Image.open(os.path.join(HERE, name + ".png")).convert("RGBA")
    a = np.asarray(im)
    al = a[..., 3]
    ys, xs = np.where(al > 8)
    im = im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    g = im.resize((COLS, ROWS), Image.LANCZOS)
    arr = np.asarray(g)
    alpha = arr[..., 3]
    # colour type per cell: S=skin, D=dark(hair/cloth), L=light
    rgb = arr[..., :3].astype(np.float32)
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    r, gg, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    skin = (r > 95) & (gg > 40) & (b > 20) & (r > gg) & (r > b) & \
           (np.abs(r - gg) > 15) & ((rgb.max(axis=2) - rgb.min(axis=2)) > 15)
    print("\n===", name, "===")
    for y in range(ROWS):
        line = ""
        for x in range(COLS):
            if alpha[y, x] < 80:
                line += "."
            elif skin[y, x]:
                line += "s"
            elif lum[y, x] < 90:
                line += "#"
            elif lum[y, x] > 200:
                line += "o"
            else:
                line += "+"
        print(line)


for n in ("view1", "view2", "view4"):
    ascii_art(n)
