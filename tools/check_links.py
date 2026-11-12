#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""百科全書連結與格式檢查器。

用法：
    python3 tools/check_links.py              # 檢查全站
    python3 tools/check_links.py 邏輯學        # 僅檢查某概念資料夾
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def planned_articles():
    """讀取 tools/data/levels.py，回傳預留但尚未撰寫的條目路徑集合。"""
    path = os.path.join(ROOT, "tools", "data", "levels.py")
    if not os.path.exists(path):
        return set()
    import importlib.util
    spec = importlib.util.spec_from_file_location("levels_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = set()
    for concept, levels in getattr(mod, "LEVELS", {}).items():
        for third, fourths in levels:
            out.add(f"{concept}/{third}.md")
            for f in fourths:
                out.add(f"{concept}/{f}.md")
    return out


PLANNED = planned_articles()

DEFS_RE = re.compile(r"^\[([^\]]+)\]:\s*(\S+)\s*$", re.M)
INLINE_RE = re.compile(r"\[([^\]\[]+)\]\(([^)#]+\.md)(?:#[^)]*)?\)")
USE_RE = re.compile(r"\[([^\]\[]+)\](?!\()")
PLACEHOLDER_RE = re.compile(r"TODO|待撰寫|待補|XXX|FIXME")
MIN_LINES = 100


def strip_math(text):
    """移除 $$ 區塊與 $...$ 行內公式，避免誤判方括號與空格規則。"""
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    return re.sub(r"\$[^$\n]*\$", " ", text)


def check_file(path):
    problems = []
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    rel_dir = os.path.dirname(os.path.relpath(path, ROOT))
    is_entry = (
        os.path.basename(path) == "README.md" and os.path.abspath(path) != os.path.join(ROOT, "README.md")
    ) or (
        rel_dir in ("", ".") and os.path.basename(path) not in ("README.md", "prompts.md", "AGENTS.md")
    )
    defs = dict(DEFS_RE.findall(raw))
    body = DEFS_RE.sub("", raw)
    plain = re.sub(r"```.*?```", " ", strip_math(body), flags=re.S)
    plain = re.sub(r"`[^`\n]*`", " ", plain)
    used = set(USE_RE.findall(plain))

    for label in sorted(used - set(defs)):
        problems.append(f"缺少連結定義：[{label}]")
    for label in sorted(set(defs) - used):
        problems.append(f"未使用的連結定義：[{label}]")

    base = os.path.dirname(path)
    for label, target in defs.items():
        if target.startswith(("http://", "https://", "#")):
            continue
        rel_target = os.path.relpath(os.path.normpath(os.path.join(base, target)), ROOT)
        if not os.path.exists(os.path.normpath(os.path.join(base, target))) and rel_target not in PLANNED:
            problems.append(f"連結目標不存在：[{label}] -> {target}")

    for match in INLINE_RE.finditer(body):
        problems.append(f"請改用參考式連結：[{match.group(1)}]({match.group(2)})")

    if PLACEHOLDER_RE.search(plain):
        problems.append("含佔位文字（TODO／待撰寫／待補）")

    if not is_entry and "對應維基百科" not in raw:
        problems.append("缺少對應維基百科連結")

    lines = raw.rstrip("\n").split("\n")
    if len(lines) < MIN_LINES and not is_entry:
        problems.append(f"行數不足：{len(lines)} < {MIN_LINES}")

    # TeX 行內公式的 $ 前後需有空格
    for m in re.finditer(r"(?<!\$)\$([^$\n]+)\$(?!\$)", raw):
        start = m.start()
        end = m.end()
        before = raw[start - 1] if start > 0 else "\n"
        after = raw[end] if end < len(raw) else "\n"
        if not (before.isspace() or before == "$") or not (after.isspace() or after == "$"):
            problems.append(f"TeX 的 $ 前後需有空格：{m.group(0)[:40]!r}")
            break

    # README.md 僅可含表格與連結定義
    if is_entry:
        text = plain
        in_front = False
        for line in text.split("\n"):
            s = line.strip()
            if s == "---":
                in_front = not in_front
                continue
            if in_front or not s:
                continue
            if s.startswith("#"):
                continue
            if s.startswith(">"):
                continue
            if s.startswith("|") or s.startswith("---") or s.startswith("["):
                continue
            problems.append(f"分類入口頁只允許表格與連結定義：{s[:40]}")

    return problems


def main():
    targets = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            p = os.path.join(ROOT, arg)
            if os.path.isdir(p):
                targets.append(p)
            elif os.path.isfile(p):
                targets.append(os.path.dirname(p))
            else:
                targets.append(p)
    else:
        targets.append(ROOT)

    total = 0
    for target in targets:
        if not os.path.exists(target):
            print(f"找不到路徑：{target}")
            continue
        for dirpath, _dirnames, filenames in os.walk(target):
            for name in sorted(filenames):
                if not name.endswith(".md"):
                    continue
                if name in ("prompts.md", "AGENTS.md"):
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, ROOT)
                issues = check_file(path)
                if issues:
                    total += len(issues)
                    print(f"\n[{rel}]")
                    for issue in issues:
                        print(f"  - {issue}")

    print(f"\n檢查完成，共 {total} 項問題。")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
