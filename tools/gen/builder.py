# -*- coding: utf-8 -*-
import re
from urllib.parse import quote

CROSS = {
    "人工智慧": "../人工智慧/README.md",
    "自動控制": "../自動控制/README.md",
    "機器人學": "../機器人學/README.md",
    "機械工程": "../機械工程/README.md",
    "電機工程": "../電機工程/README.md",
    "精密儀器": "../精密儀器/README.md",
    "醫療器材": "../醫療器材/README.md",
    "智慧家庭": "../智慧家庭/README.md",
    "演算法": "../演算法/README.md",
    "車輛工程": "../車輛工程/README.md",
    "航空工程": "../航空工程/README.md",
    "程式設計": "../程式設計/README.md",
    "資料科學": "../資料科學/README.md",
    "半導體": "../半導體/README.md",
    "自動駕駛": "../自動駕駛/README.md",
    "汽車工業": "../汽車工業/README.md",
    "鐵路": "../鐵路/README.md",
    "計算機網路": "../計算機網路/README.md",
    "材料工程": "../材料工程/README.md",
    "工": "../工/README.md",
    "建模方法": "../自動控制/建模方法.md",
    "狀態回授": "../自動控制/狀態回授.md",
    "控制器設計": "../自動控制/控制器設計.md",
    "回授": "../自動控制/回授.md",
    "PID": "../自動控制/PID.md",
    "強化學習": "../機器人學/強化學習.md",
}

ENT = {
    "維納": "../人/數學家/維納.md",
    "奈奎斯特": "../人/工程師/奈奎斯特.md",
    "詹姆斯·瓦特": "../人/工程師/詹姆斯·瓦特.md",
    "沃克·伊文思": "../人/工程師/沃克·伊文思.md",
    "恩格爾鮑特": "../人/工程師/恩格爾鮑特.md",
    "梅特羅波利斯": "../人/物理學家/梅特羅波利斯.md",
    "狄克斯特拉": "../人/工程師/狄克斯特拉.md",
    "1948年": "../時/1948年.md",
    "1961年": "../時/1961年.md",
    "1788年": "../時/1788年.md",
    "機器人": "../物/機器人.md",
    "工業機器人": "../物/工業機器人.md",
    "陀螺儀": "../物/陀螺儀.md",
    "伺服馬達": "../物/伺服馬達.md",
}

REF_RE = re.compile(r"\[([^\]\n]+)\](?![\(:])")


def wiki_line(zh, en):
    """zh: (canonical, display) or None; en: str or None."""
    parts = []
    if zh:
        canon, disp = zh
        parts.append("[中文維基百科：%s](https://zh.wikipedia.org/wiki/%s)" % (disp, quote(canon)))
    else:
        parts.append("中文維基百科無對應條目")
    if en:
        parts.append("[English Wikipedia: %s](https://en.wikipedia.org/wiki/%s)" % (en, quote(en.replace(" ", "_"))))
    return "> 對應維基百科：" + "　·　".join(parts)


def resolve(ref, local):
    if ref in local:
        return local[ref]
    if ref in CROSS:
        return CROSS[ref]
    if ref in ENT:
        return ENT[ref]
    raise KeyError("未定義的連結：%s" % ref)


def gather_defs(body_lines, local):
    defs = []
    seen = set()
    in_mermaid = False
    in_defs = False
    for ln in body_lines:
        s = ln.strip()
        if s.startswith("```"):
            in_mermaid = not in_mermaid
            continue
        if s == "## 連結定義":
            in_defs = True
        if in_defs or in_mermaid:
            continue
        for m in REF_RE.finditer(ln):
            ref = m.group(1)
            if ref not in seen:
                seen.add(ref)
                defs.append((ref, resolve(ref, local)))
    return defs


def build_page(fname, tags, title, belong, wline, body_sections, local, min_lines=100):
    lines = []
    lines.append("---")
    lines.append("title: %s" % title)
    lines.append("tags:")
    for t in tags:
        lines.append("  - %s" % t)
    lines.append("status: 初稿")
    lines.append("---")
    lines.append("")
    lines.append("# %s" % title)
    lines.append("")
    lines.append(belong)
    lines.append("")
    lines.append(wline)
    lines.append("")
    for sec in body_sections:
        lines.extend(sec)
        lines.append("")
    defs = gather_defs(lines, local)
    lines.append("## 連結定義")
    lines.append("")
    for ref, path in defs:
        lines.append("[%s]: %s" % (ref, path))
    lines.append("")
    if len(lines) < min_lines:
        raise AssertionError("%s 只有 %d 行（少於 %d）" % (fname, len(lines), min_lines))
    return lines


def sec_heading(h):
    return ["## %s" % h]


def bullets(items):
    return ["- %s" % i for i in items]


def paras(items):
    return list(items)


def numbered(items):
    return ["%d. %s" % (i + 1, s) for i, s in enumerate(items)]


def table_kids(kids):
    out = ["| 孫分類 | 狀態 |", "| --- | --- |"]
    for k in kids:
        out.append("| [%s] | 初稿 |" % k)
    return out


def mermaid(lines_in):
    return ["```mermaid"] + ["graph TD"] + lines_in + ["```"]
