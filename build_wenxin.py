# -*- coding: utf-8 -*-
"""Build 文心一言桌宠.apk: 肥鱼.apk model -> 文心一言 character, rebrand, icon, sign.

  1. copy the decoded apktool project (apk_full, from 肥鱼.apk)
  2. swap assets/pet/clips/* with the generated 文心一言 frames
  3. rebrand package -> com.wenxin.pet, app name -> 文心一言桌宠
  4. launcher icon from the model front view
  5. apktool build, zipalign + sign, deliver to Desktop\桌宠软件\文心一言桌宠.apk
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = r"C:\Users\xt621\Documents\deepseek-harness\default-workspace"
APK_WORK = os.path.join(WS, "apk_work")
JAVA = r'"C:\Program Files\Java\jdk-9.0.1\bin\java.exe"'
APKTOOL = os.path.join(APK_WORK, "tools", "apktool.jar")
SIGNER = os.path.join(APK_WORK, "tools", "uber-apk-signer.jar")
SRC_PROJ = os.path.join(APK_WORK, "apk_full")
DST_PROJ = os.path.join(APK_WORK, "app_wenxin")
FRAMES = os.path.join(HERE, "frames")
STATS = os.path.join(FRAMES, "stats.json")
REBRAND = os.path.join(HERE, "rebrand_wenxin.py")
MAKE_ICON = os.path.join(HERE, "make_icon_wenxin.py")
UNSIGNED = os.path.join(HERE, "unsigned_wenxin.apk")
OUTDIR = os.path.join(HERE, "sign_wenxin")
DESKTOP = r"C:\Users\xt621\Desktop\桌宠软件"
FINAL = os.path.join(DESKTOP, "文心一言桌宠.apk")


def run(cmd, **kw):
    print("+ " + cmd, flush=True)
    r = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, **kw)
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    if out:
        print(out[-5000:])
    if err:
        print("[stderr] " + err[-3000:], file=sys.stderr)
    if r.returncode != 0:
        print("FAILED rc=%d" % r.returncode, file=sys.stderr)
        sys.exit(r.returncode)
    return r


def main():
    # 1. fresh decoded project
    if os.path.isdir(DST_PROJ):
        shutil.rmtree(DST_PROJ)
    print("copying decoded project ...", flush=True)
    shutil.copytree(SRC_PROJ, DST_PROJ, symlinks=False)

    # 2. swap the frame folders with the generated 文心一言 frames
    root = os.path.join(DST_PROJ, "assets", "pet", "clips")
    for cid in sorted(os.listdir(root)):
        d = os.path.join(root, cid)
        if not os.path.isdir(d):
            continue
        src = os.path.join(FRAMES, cid)
        if not os.path.isdir(src):
            print("!! missing generated clip", cid)
            continue
        shutil.rmtree(d)
        shutil.copytree(src, d)
        print("swapped", cid, len(os.listdir(d)), "frames")

    # 3. rebrand: package id, app name, manifest crop boxes from stats
    print("rebranding ...", flush=True)
    env = os.environ.copy()
    env["STATS"] = STATS
    r = subprocess.run([sys.executable, REBRAND, DST_PROJ],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    print(r.stdout)
    if r.returncode:
        print(r.stderr)
        sys.exit(1)

    # 4. launcher icon from the model front view
    icon_dst = os.path.join(DST_PROJ, "res", "drawable-nodpi", "pet_icon.png")
    r = subprocess.run([sys.executable, MAKE_ICON, icon_dst],
                       capture_output=True, text=True, encoding="utf-8")
    print(r.stdout, r.stderr)

    # 5. apktool build
    if os.path.exists(UNSIGNED):
        os.remove(UNSIGNED)
    run('%s -Xmx4g -jar %s b -f %s -o %s' % (JAVA, APKTOOL, DST_PROJ, UNSIGNED))

    # 6. zipalign + sign (debug key; v2/v3 verified)
    if os.path.isdir(OUTDIR):
        for f in os.listdir(OUTDIR):
            os.remove(os.path.join(OUTDIR, f))
    run('%s -jar %s -a %s --allowResign -o %s' % (JAVA, SIGNER, UNSIGNED, OUTDIR))

    for f in sorted(os.listdir(OUTDIR)):
        p = os.path.join(OUTDIR, f)
        print("sign_wenxin/%s %d bytes" % (f, os.path.getsize(p)))
        if f.endswith(".apk") and not f.endswith(".idsig"):
            shutil.copy2(p, FINAL)
            print("delivered", FINAL, os.path.getsize(FINAL), "bytes")


if __name__ == '__main__':
    main()
