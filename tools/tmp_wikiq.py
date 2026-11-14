#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys, time, urllib.parse, urllib.request

API = "https://{lang}.wikipedia.org/w/api.php?action=query&format=json&redirects=1&titles={titles}"
UA = {"User-Agent": "markpedia-encyclopedia/1.0 (offline build script)"}

def fetch(lang, titles):
    q = urllib.parse.quote("|".join(titles).replace(" ", "_"), safe="")
    for attempt in range(8):
        try:
            req = urllib.request.Request(API.format(lang=lang, titles=q), headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(8 * (attempt + 1))
    return {}

def resolve(lang, titles):
    found = {}
    titles = list(dict.fromkeys(titles))
    for i in range(0, len(titles), 15):
        data = fetch(lang, titles[i:i+15])
        q = data.get("query", {})
        alias = {}
        for x in q.get("normalized", []) + q.get("redirects", []):
            alias[x["from"]] = x["to"]
        for p in q.get("pages", {}).values():
            if "missing" in p:
                continue
            found.setdefault(p["title"], p["title"])
            for s, d in alias.items():
                if d == p["title"]:
                    found[s] = p["title"]
        time.sleep(3)
    return found

data = json.load(open(sys.argv[1], encoding="utf-8"))
zh_all, en_all = [], []
for v in data.values():
    zh_all += v.get("zh", [])
    en_all += v.get("en", [])
zh_map = resolve("zh", zh_all)
en_map = resolve("en", en_all)
res = {}
for name, cand in data.items():
    zd = zc = ed = ec = None
    for c in cand.get("zh", []):
        if c in zh_map:
            zd, zc = c, zh_map[c]; break
    for c in cand.get("en", []):
        if c in en_map:
            ed, ec = c, en_map[c]; break
    res[name] = {"zh_disp": zd, "zh_canon": zc, "en_disp": ed, "en_canon": ec}
    print(f"{name}: zh={zc} | en={ec}" + ("" if (zc or ec) else "   ← 兩者皆無"))
if len(sys.argv) > 2:
    json.dump(res, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
