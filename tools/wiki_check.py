#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批次查證中文／英文維基百科條名是否存在。

用法：
    python3 tools/wiki_check.py 候選檔.json [輸出檔.json]

候選檔格式：
    {"條目名.md": {"zh": ["候選條名", ...], "en": ["候選條名", ...]}, ...}

輸出：每個條目的 zh/en 候選與「正式條名」（canonical），供寫入連結時使用。
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://{lang}.wikipedia.org/w/api.php?action=query&format=json&redirects=1&titles={titles}"
UA = {"User-Agent": "markpedia-encyclopedia/1.0 (offline build script)"}
CHUNK = 40


def fetch(lang, titles):
    q = urllib.parse.quote("|".join(titles).replace(" ", "_"), safe="")
    url = API.format(lang=lang, titles=q)
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or attempt == 5:
                raise
            time.sleep(5 * (attempt + 1))
    return {}


def resolve_all(lang, all_titles):
    found = {}
    titles = list(dict.fromkeys(all_titles))
    for i in range(0, len(titles), CHUNK):
        chunk = titles[i:i + CHUNK]
        data = fetch(lang, chunk)
        query = data.get("query", {})
        alias = {}
        for x in query.get("normalized", []) + query.get("redirects", []):
            alias[x["from"]] = x["to"]
        for p in query.get("pages", {}).values():
            if "missing" in p:
                continue
            title = p["title"]
            found.setdefault(title, title)
            for src, dst in alias.items():
                if dst == title:
                    found[src] = title
        time.sleep(2)
    return found


def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    zh_all, en_all = [], []
    for name, cand in data.items():
        zh_all += cand.get("zh", [])
        en_all += cand.get("en", [])
    zh_map = resolve_all("zh", zh_all)
    en_map = resolve_all("en", en_all)

    result = {}
    for name, cand in data.items():
        zh_disp = zh_canon = en_disp = en_canon = None
        for c in cand.get("zh", []):
            if c in zh_map:
                zh_disp, zh_canon = c, zh_map[c]
                break
        for c in cand.get("en", []):
            if c in en_map:
                en_disp, en_canon = c, en_map[c]
                break
        result[name] = {"zh_disp": zh_disp, "zh_canon": zh_canon,
                        "en_disp": en_disp, "en_canon": en_canon}
        flag = "" if (zh_canon or en_canon) else "   ← 兩者皆無"
        print(f"{name}: zh={zh_canon} | en={en_canon}{flag}")
    if len(sys.argv) > 2:
        json.dump(result, open(sys.argv[2], "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
