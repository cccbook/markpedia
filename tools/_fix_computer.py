#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性修補 site/電腦/ 下既有條目：行內連結轉參考式、補連結定義、TeX 空格、佔位字元。"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "site", "電腦")

INLINE = re.compile(r"\[([^\]\[]+)\]\(([^)#]+\.md)(?:#[^)]*)?\)")
DEFS = re.compile(r"^\[([^\]]+)\]:\s*(\S+)\s*$", re.M)
MATH = re.compile(r"(?<!\$)\$([^$\n]+)\$(?!\$)")


def fix_math(text):
    out = []
    pos = 0
    for m in MATH.finditer(text):
        s, e = m.start(), m.end()
        before = text[s - 1] if s > 0 else "\n"
        after = text[e] if e < len(text) else "\n"
        chunk = text[pos:s]
        if not (before.isspace() or before == "$"):
            chunk += " "
        chunk += m.group(0)
        if not (after.isspace() or after == "$"):
            chunk += " "
        out.append(chunk)
        pos = e
    out.append(text[pos:])
    return "".join(out)


for name in sorted(os.listdir(DIR)):
    if not name.endswith(".md") or name == "README.md":
        continue
    path = os.path.join(DIR, name)
    with open(path, encoding="utf-8") as f:
        text = f.read()

    need = {}

    def repl(m):
        label, target = m.group(1), m.group(2)
        need[label] = target
        return "[" + label + "]"

    text = INLINE.sub(repl, text)
    text = fix_math(text)
    text = text.replace("U+XXXX", "U+4E00 至 U+10FFFF 區段")

    existing = dict(DEFS.findall(text))
    for label, target in need.items():
        if label not in existing:
            existing[label] = target
    if need:
        body, _, defs_part = text.partition("## 連結定義\n")
        lines = [f"[{k}]: {v}" for k, v in existing.items()]
        text = body + "## 連結定義\n" + "\n".join(lines) + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("fixed", name, "lines=", len(text.rstrip("\n").split("\n")))
