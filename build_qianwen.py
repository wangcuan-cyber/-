# -*- coding: utf-8 -*-
"""Build the 千问AI娘 APK: copy decoded project -> swap new-model frames ->
re-brand (package, app name, crop boxes) -> build launcher icon from the
character model -> apktool build -> zipalign + sign.
Run from apk_work:  python build_qianwen.py
"""
import os, shutil, subprocess, sys

W = os.path.dirname(os.path.abspath(__file__))
JAVA = '"C:\\Program Files\\Java\\jdk-9.0.1\\bin\\java.exe"'
APKTOOL = os.path.join(W, "tools", "apktool.jar")
SIGNER = os.path.join(W, "tools", "uber-apk-signer.jar")
SRC_PROJ = os.path.join(W, "apk_full")
DST_PROJ = os.path.join(W, "app_qianwen")
FRAMES = os.path.join(W, "build_chibi", "frames_front")
STATS = os.path.join(FRAMES, "stats.json")
UNSIGNED = os.path.join(W, "unsigned_qianwen.apk")
OUTDIR = os.path.join(W, "sign_qianwen")


def run(cmd, env_extra=None, **kw):
    print("+ " + cmd, flush=True)
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(cmd, shell=True, cwd=W, env=env, capture_output=True,
                       text=True, **kw)
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    if out:
        print(out[-2500:])
    if err:
        print("[stderr] " + err[-1500:], file=sys.stderr)
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

    # 2. swap the frame folders with the new character model
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
    r = subprocess.run([sys.executable, os.path.join(W, "rebrand_qianwen.py"), DST_PROJ],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    print(r.stdout)
    if r.returncode:
        print(r.stderr)
        sys.exit(1)

    # 4. launcher icon from the adopted character model image
    icon_dst = os.path.join(DST_PROJ, "res", "drawable-nodpi", "pet_icon.png")
    r = subprocess.run([sys.executable, os.path.join(W, "make_icon_blue.py"), icon_dst],
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
        print("sign_qianwen/%s %d bytes" % (f, os.path.getsize(os.path.join(OUTDIR, f))))


if __name__ == '__main__':
    main()
