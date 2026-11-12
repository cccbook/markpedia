#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把行內公式統一成「$ 前有空格、$ 後有空格」，符合 GitHub MathJax 與 AGENTS.md 規範。"""
import os
import re
import sys

MATH_RE = re.compile(r"(?<!\$)\$([^$\n]+)\$(?!\$)")
FENCE_RE = re.compile(r"```.*?```", re.S)


def fix(text):
    out = []
    pos = 0
    for fence in FENCE_RE.finditer(text):
        out.append(fix_plain(text[pos:fence.start()]))
        out.append(fence.group(0))
        pos = fence.end()
    out.append(fix_plain(text[pos:]))
    return "".join(out)


def fix_plain(text):
    out = []
    pos = 0
    for m in MATH_RE.finditer(text):
        start, end = m.start(), m.end()
        before = text[start - 1] if start > 0 else " "
        after = text[end] if end < len(text) else " "
        out.append(text[pos:start])
        if before not in (" ", "\n", "\t"):
            out.append(" ")
        out.append(m.group(0))
        if after not in (" ", "\n", "\t"):
            out.append(" ")
        pos = end
    out.append(text[pos:])
    return "".join(out)


def main():
    roots = sys.argv[1:] or ["."]
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".md"):
                    continue
                p = os.path.join(dirpath, name)
                with open(p, encoding="utf-8") as f:
                    original = f.read()
                updated = fix(original)
                if updated != original:
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(updated)
                    print(f"fixed: {p}")


if __name__ == "__main__":
    main()
