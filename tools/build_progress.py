#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生 / 更新 PROGRESS.md：記錄 420 個概念的撰寫進度。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(HERE, "data"))

from concepts import DATA  # noqa: E402
from levels import LEVELS  # noqa: E402

BRANCH_ORDER = ["人", "事", "時", "地-空間", "地-自然", "物", "天", "文", "法", "商",
                "理", "工", "醫", "農", "食", "衣", "住", "行", "育", "樂"]
BRANCH_LABEL = {k: DATA[k][0] for k in DATA}


def status(concept):
    folder = os.path.join(SITE, concept)
    levels = LEVELS.get(concept, [])
    planned = [f"{concept}.md"]
    for third, fourths in levels:
        planned.append(f"{third}.md")
        planned.extend(f"{x}.md" for x in fourths)
    done = [f for f in planned if os.path.exists(os.path.join(folder, f))]
    if not done:
        return "未開始", 0, len(planned)
    if len(done) == len(planned):
        return "已完成", len(done), len(planned)
    return "撰寫中", len(done), len(planned)


def main():
    out = []
    out.append("# 撰寫進度追蹤")
    out.append("")
    out.append("> 本檔由 `tools/build_progress.py` 產生，記錄每個第二層概念的撰寫狀態。")
    out.append("> 撰寫順序：第一層分支依序推進；同一分支內依概念清單順序。")
    out.append("> 每個概念需完成：`<概念>.md` ＋ 各子分類、孫分類條目（檔名與 `tools/data/levels.py` 一致）。")
    out.append("")
    total = done = doing = 0
    for br in BRANCH_ORDER:
        concepts = [n for n, _ in DATA[br][2]]
        bdone = bdoing = 0
        out.append(f"## {BRANCH_LABEL[br]}")
        out.append("")
        out.append("| 概念 | 子分類數 | 孫分類數 | 條目數 | 進度 | 狀態 |")
        out.append("| --- | --- | --- | --- | --- | --- |")
        for c in concepts:
            st, d, t = status(c)
            total += t
            done += d
            if st == "已完成":
                bdone += t
                bdoing += 0
            elif st == "撰寫中":
                bdoing += d
            ns = len(LEVELS.get(c, []))
            ns4 = sum(len(x[1]) for x in LEVELS.get(c, []))
            out.append(f"| [{c}](site/{c}/README.md) | {ns} | {ns4} | {t} | {d}/{t} | {st} |")
        bt = sum(1 + len(LEVELS.get(c, [])) + sum(len(x[1]) for x in LEVELS.get(c, []))
                 for c in concepts)
        out.append(f"| **分支小計** |  |  | **{bt}** | **{bdone}/{bt}** |  |")
        out.append("")
    out.append("## 第一層實體條目")
    out.append("")
    out.append("| 第一層 | 實體條目數 |")
    out.append("| --- | --- |")
    etotal = 0
    for br in BRANCH_ORDER:
        folder = os.path.join(SITE, br)
        n = len([f for f in os.listdir(folder)
                 if f.endswith(".md") and f != "README.md"]) if os.path.isdir(folder) else 0
        etotal += n
        out.append(f"| {BRANCH_LABEL[br]} | {n} |")
    out.append(f"| **合計** | **{etotal}** |")
    out.append("")
    out.append("## 總計")
    out.append("")
    out.append(f"- 概念數：{len(set(n for b in BRANCH_ORDER for n, _ in DATA[b][2]))}")
    out.append(f"- 條目檔數（概念＋子分類＋孫分類）：{total}")
    out.append(f"- 已完成條目：{done}")
    out.append(f"- 完成率：{done / total * 100:.1f}%" if total else "-")
    out.append("")
    with open(os.path.join(ROOT, "PROGRESS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"PROGRESS.md updated: {done}/{total} files ({done / total * 100:.1f}%)")


if __name__ == "__main__":
    main()
