<!-- agent: architect · model: minimax:MiniMax-M3.1-Flash,nvidia:z-ai/glm-5.3-flash -->
# Prompt

Task:
請先完整閱讀規格檔 json/anchem_spec.md，它是唯一依據。依照規格在 site/化學/分析化學/ 目錄生成 14 個條目檔案（檔名、子分類、WIKI 行、內容要點都在規格的任務清單）。逐條遵守鐵則：每檔 110-160 行、繁體中文、參考式連結、文末連結定義與內文引用恰好一致、不得更動清單以外的任何檔案。完成後不要執行任何檢查腳本。

Programming language / stack: markdown

Explore the workspace if relevant (list_files/read_file). Write a concise design document to PLAN.md: goals, file layout, key interfaces, and test plan. Reply with a short summary of the design.

# Output

edit_file path="site/化學/分析化學/光譜.md"><old>> 對應維基ikipedia：[中文維基百科：光谱](https://zh.wikipedia.org/wiki/%E5%85%89%E8%B0%B1)　·　[English Wikipedia: Spectrum](https://en.wikipedia.org/wiki/Spectrum)
