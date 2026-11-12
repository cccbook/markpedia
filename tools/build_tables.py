# -*- coding: utf-8 -*-
"""產生第一層入口頁與各概念的 README.md（統一為「子分類 | 孫分類」表格，參考式連結）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
from concepts import DATA
from levels import LEVELS
import json
import urllib.parse

TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = {}
for f in ("wiki_resolved.json", "wiki_resolved_fl.json"):
    p_ = os.path.join(REPO, "tools", f)
    if os.path.exists(p_):
        WIKI.update(json.load(open(p_, encoding="utf-8")))


def link_if_exists(label, path):
    """目標檔案存在時用參考式連結，否則以純文字呈現（尚未撰寫的條目）。"""
    return f"[{label}]" if os.path.exists(os.path.join(ROOT, path)) else label


def enc(t):
    return urllib.parse.quote(t.replace(" ", "_"), safe="")


def wiki_line(keys, disp):
    parts = []
    for k in keys:
        r = WIKI.get(k)
        if not r:
            continue
        if r["zh_canon"]:
            parts.append(f"[中文維基百科：{disp if len(keys) == 1 else r['zh_canon']}](https://zh.wikipedia.org/wiki/{enc(r['zh_canon'])})")
        if r["en_canon"]:
            parts.append(f"[English Wikipedia: {r['en_canon']}](https://en.wikipedia.org/wiki/{enc(r['en_canon'])})")
    return "> 對應維基百科：" + "　·　".join(parts)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

owners = {}
for pk, (disp, intro, subs) in DATA.items():
    for name, _ in subs:
        owners.setdefault(name, []).append(pk)

disp_of = {pk: DATA[pk][0] for pk in DATA}
short = lambda pk: pk.split("-")[0]
level_of = lambda c: LEVELS.get(c, [])

# ---------------------------------------------------------------- 概念 README
for pk, (disp, intro, subs) in DATA.items():
    for name, desc in subs:
        levels = level_of(name)
        L = []
        L.append("---")
        L.append(f"title: {name}")
        L.append("tags:")
        L.append("  - 分類/第二層")
        for p in owners[name]:
            L.append(f"  - {short(p)}")
        L.append("---")
        L.append("")
        L.append(f"# {name}")
        L.append("")
        L.append("| 子分類 | 孫分類 |")
        L.append("| --- | --- |")
        if levels:
            for sub, subsub in levels:
                cell = " · ".join(f"[{x}]" for x in subsub)
                L.append(f"| [{sub}] | {cell} |")
        else:
            L.append("| （待建立） | （待建立） |")
        L.append("")
        L.append("## 連結定義")
        L.append("")
        for sub, subsub in levels:
            L.append(f"[{sub}]: {sub}.md")
            for x in subsub:
                L.append(f"[{x}]: {x}.md")
        L.append("")
        with open(os.path.join(ROOT, name, "README.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L))

# ---------------------------------------------------------------- 第一層入口頁
groups, order = {}, []
for pk in DATA:
    s = short(pk)
    if s not in groups:
        groups[s] = []
        order.append(s)
    groups[s].append(pk)

for s in order:
    branches = groups[s]
    L = []
    L.append("---")
    L.append("tags:")
    L.append("  - 分類/第一層")
    L.append(f"  - {s}")
    L.append("---")
    L.append("")
    if len(branches) == 1:
        pk = branches[0]
        disp, intro, subs = DATA[pk]
        L.append(f"# {disp}")
        L.append("")
        L.append(f"> {intro}")
    else:
        L.append(f"# {s}")
        L.append("")
        for pk in branches:
            disp, intro, subs = DATA[pk]
            L.append(f"> **{disp}**：{intro}")
    L.append("")
    keys = [pk if "-" in pk else f"{short(pk)}.md" for pk in branches]
    L.append(wiki_line(keys, s))
    L.append("")
    L.append("## 分類表")
    L.append("")
    L.append("| 子分類 | 孫分類 |")
    L.append("| --- | --- |")
    for pk in branches:
        for name, _ in DATA[pk][2]:
            levels = level_of(name)
            if levels:
                cell = " · ".join(f"[{sub}]" for sub, _ in levels)
            else:
                cell = "（待建立）"
            L.append(f"| [{name}] | {cell} |")
    L.append("")
    L.append("## 連結定義")
    L.append("")
    for pk in branches:
        for name, _ in DATA[pk][2]:
            L.append(f"[{name}]: ../{name}/README.md")
            for sub, _ in level_of(name):
                L.append(f"[{sub}]: ../{name}/{sub}.md")
    L.append("")
    os.makedirs(os.path.join(ROOT, s), exist_ok=True)
    with open(os.path.join(ROOT, s, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))

print("rebuilt concept README.md + first-layer pages")
