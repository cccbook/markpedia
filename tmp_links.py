#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把檔案中的 [[ZH:canon|text]] / [[EN:canon|text]] 標記換成維基百科連結。"""
import re
import sys
import urllib.parse

def enc(title):
    t = title.replace(" ", "_")
    return urllib.parse.quote(t, safe="")

def repl(m):
    lang, canon, text = m.group(1), m.group(2), m.group(3)
    url = f"https://{'zh' if lang == 'ZH' else 'en'}.wikipedia.org/wiki/{enc(canon)}"
    label = ("中文維基百科：" if lang == "ZH" else "English Wikipedia: ") + text
    return f"[{label}]({url})"

for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as f:
        s = f.read()
    s2 = re.sub(r"\[\[(ZH|EN):([^\]|]+)\|([^\]]+)\]\]", repl, s)
    if s2 != s:
        with open(path, "w", encoding="utf-8") as f:
            f.write(s2)
        print("updated", path)
