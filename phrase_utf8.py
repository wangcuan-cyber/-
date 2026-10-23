# -*- coding: utf-8 -*-
import zipfile, json
apk = ("C:\\Users\\xt621\\Desktop\\" + "\u65b0\u5efa\u6587\u4ef6\u5939" + " (2)\\Claude桌宠.apk")
z = zipfile.ZipFile(apk)
man = json.loads(z.read("assets/pet/manifest.json"))
with open(r"C:\Users\xt621\Documents\deepseek-harness\default-workspace\claude_pet\phrases_utf8.txt", "w", encoding="utf-8") as f:
    f.write(json.dumps(man["phrases"], ensure_ascii=False, indent=2))
print("wrote phrases_utf8.txt")
print("raw repr:", json.dumps(man["phrases"], ensure_ascii=False))
