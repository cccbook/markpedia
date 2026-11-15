# -*- coding: utf-8 -*-
import json, os, subprocess, sys, urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (kind, folder, filename, concept, parent_header, children, zh, en, extra_prompt)
SPECS = []

def sub(concept, name, zh, en, children, extra=""):
    SPECS.append(dict(kind="sub", concept=concept, name=name, zh=zh, en=en, children=children, extra=extra))

# ---------- 世界史 ----------
sub("世界史", "全球史觀", "全球史", "Global history", [], )
sub("世界史", "世界體系", "世界體系理論", "World-systems theory", [])
sub("世界史", "全球史與交流史", "全球史", "Global history", [])
sub("世界史", "比較史學", "比較史學", "Comparative history", [])
sub("世界史", "古代與中世紀", "古代史", "Ancient history", [])
sub("世界史", "上古文明", "古代文明", "Ancient civilization", [])
sub("世界史", "古典帝國", "帝國", "Empire", [])
sub("世界史", "中世紀歐亞", "中世紀", "Middle Ages", [])
sub("世界史", "現代史", "現代史", "Modern history", [])
sub("世界史", "兩次大戰", "世界大戰", "World war", [])
sub("世界史", "冷戰", "冷戰", "Cold War", [])
sub("世界史", "去殖民化", "非殖民化", "Decolonization", [])
sub("世界史", "全球化", "全球化", "Globalization", [])
sub("世界史", "跨文化比較", "比較史學", "Comparative history", [])
sub("世界史", "比較方法", "比較史學", "Comparative history", [])
sub("世界史", "同步史觀", "全球史", "Global history", [])
sub("世界史", "路徑差異", "路徑依賴", "Path dependence", [])

# ---------- 國別史 ----------
sub("國別史", "中國史", "中國歷史", "History of China",
    ["先秦", "秦漢至隋唐", "宋元明清", "近現代"])
sub("國別史", "先秦", "先秦", "Pre-Qin", [])
sub("國別史", "秦漢至隋唐", "秦朝", "Qin dynasty", [])
sub("國別史", "宋元明清", "宋朝", "Song dynasty", [])
sub("國別史", "近現代", "中國近代史", "Modern Chinese history", [])
sub("國別史", "日本史", "日本歷史", "History of Japan",
    ["古代", "武家政權", "江戶", "近代"])
sub("國別史", "古代", "彌生時代", "Yayoi period", [])
sub("國別史", "武家政權", "幕府", "Shogunate", [])
sub("國別史", "江戶", "江戶時代", "Edo period", [])
sub("國別史", "近代", "日本近代史", "History of Japan", [])
sub("國別史", "歐洲史", "歐洲歷史", "History of Europe",
    ["希臘羅馬", "中世紀王國", "近代國家", "歐盟"])
sub("國別史", "希臘羅馬", "古希臘", "Ancient Greece", [])
sub("國別史", "中世紀王國", "中世紀", "Middle Ages", [])
sub("國別史", "近代國家", "民族國家", "Nation state", [])
sub("國別史", "歐盟", "歐洲聯盟", "European Union", [])
sub("國別史", "美國史", "美國歷史", "History of the United States",
    ["殖民地時期", "獨立與憲法", "內戰", "20世紀"])
sub("國別史", "殖民地時期", "十三殖民地", "Thirteen Colonies", [])
sub("國別史", "獨立與憲法", "美國獨立戰爭", "American Revolutionary War", [])
sub("國別史", "內戰", "南北戰爭", "American Civil War", [])
sub("國別史", "20世紀", "20世紀美國", "United States in the 20th century", [])
sub("國別史", "其他地區史", "世界史", "World history",
    ["南亞", "中東", "非洲", "拉丁美洲"])
sub("國別史", "南亞", "南亞歷史", "History of South Asia", [])
sub("國別史", "中東", "中東歷史", "History of the Middle East", [])
sub("國別史", "非洲", "非洲歷史", "History of Africa", [])
sub("國別史", "拉丁美洲", "拉丁美洲歷史", "History of Latin America", [])

CONCEPTS = [
    dict(name="世界史", zh="世界历史", en="Universal history", subs=["全球史觀", "古代與中世紀", "近代史", "現代史", "跨文化比較", "歷史學家"]),
    dict(name="國別史", zh="國別史", en="National history", subs=["中國史", "日本史", "歐洲史", "美國史", "其他地區史"]),
]

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "candidates":
        cands = {}
        for s in SPECS:
            cands[s["name"] + ".md"] = {"zh": [s["zh"]], "en": [s["en"]]}
        for c in CONCEPTS:
            cands[c["name"] + ".md"] = {"zh": [c["zh"]], "en": [c["en"]]}
        with open("/tmp/wiki_cands.json", "w") as f:
            json.dump(cands, f, ensure_ascii=False, indent=1)
        print("wrote", len(cands))
    elif mode == "gen":
        # one agge call per file: python3 gen.py gen1 <index>
        idx = int(sys.argv[2])
        if idx < len(CONCEPTS):
            c = CONCEPTS[idx]
            print(build_concept_prompt(c))
        else:
            s = SPECS[idx - len(CONCEPTS)]
            print(build_sub_prompt(s))

def build_sub_prompt(s):
    ch = s["children"]
    return f"""請以繁體中文撰寫維基百科風格的歷史條目本文（主題：{s['zh']}／{s['en']}，檔名：{s['name']}）。規則：
- 不得使用任何 Markdown 連結（不要出現 [文字](網址) 或 [文字]），一律純文字。
- 不得使用數學公式、TeX、$ 符號、mermaid。
- 不得出現 frontmatter、# 一級標題、「隸屬」、「對應維基百科」、「## 連結定義」。
- 歷史年份必須正確、具體（含西元/西元前）。
- 章節順序與格式嚴格如下：
1. 開頭：兩段定義段落（這是什麼、為何需要它、涵蓋的時間與空間範圍），共約 12 行。
2. ## 技術與理論的關聯：6 個列點，每點 2 至 3 句。
3. ## 大事年表：一個 Markdown 表格（| 年份 | 事件 |），表頭後 10 行資料，事件含具體年份與人物。
4. ## 範例：兩段，含具體人物、年份與事件的逐步說明。
5. ## 前因後果：編號清單 6 點，說明此概念的出現背景、解決的瓶頸與後續影響。
6. ## 與相鄰分類的關聯：3 個列點，純文字提及相鄰領域。
7. ## 容易混淆之處：3 個列點。
8. ## 技術要點：6 個列點，每點 2 句。
9. ## 常見的論爭：3 個列點，每點 2 至 3 句。
10. ## 延伸閱讀：3 個列點，寫書名（書名號《》）與作者，不用連結。
總行數不得少於 120 行。直接輸出 Markdown，不要任何說明前後綴。"""

def build_concept_prompt(c):
    subs = "、".join(c["subs"])
    return f"""請以繁體中文撰寫維基百科風格的學科概覽條目本文（主題：{c['zh']}／{c['en']}）。規則：
- 不得使用任何 Markdown 連結，一律純文字。
- 不得使用數學公式、TeX、$、mermaid。
- 不得出現 frontmatter、# 一級標題、「隸屬」、「對應維基百科」、「## 連結定義」。
- 年份必須正確具體。總行數不得少於 120 行。
- 章節順序嚴格如下：
1. 開頭：三段定義段落（這個概念是什麼、解決什麼問題、與相鄰學科的關係），約 15 行。
2. ## 核心問題：兩段 + 4 個列點。
3. ## 因果鏈：編號清單 6 步，每步一行半到兩行，講清楚瓶頸與解法。
4. ## 子分類的定位與相互驅動：以下每個子分類各寫一段（各 5 行以上），說明它做什麼、與其他子分類如何互相推動：{subs}。
5. ## 大事年表：表格（| 年份 | 事件 |）10 行資料。
6. ## 範例：兩段具體事件與年份。
7. ## 容易混淆之處：4 個列點。
8. ## 延伸閱讀：3 個列點（書名號《》與作者）。
直接輸出 Markdown，不要任何說明前後綴。"""
