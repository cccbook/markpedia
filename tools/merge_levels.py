#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把新的第三／四層分類片段合併進 tools/data/levels.py。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = os.path.join(HERE, "data", "levels.py")


def merge(fragment_files):
    frag = ""
    for f in fragment_files:
        path = f if os.path.isabs(f) else os.path.join(HERE, f)
        frag += open(path, encoding="utf-8").read()
    s = open(LEVELS, encoding="utf-8").read()
    s = s.replace("\n}\n", "\n" + frag.rstrip() + "\n}\n")
    open(LEVELS, "w", encoding="utf-8").write(s)
    sys.path.insert(0, os.path.join(HERE, "data"))
    import importlib
    import levels
    importlib.reload(levels)
    print("concepts:", len(levels.LEVELS))


if __name__ == "__main__":
    merge(sys.argv[1:])
