# 島嶼餐桌 · 藍鵲播種

第一可玩版：靜態網頁小遊戲。老師用瀏覽器打開並投影（版面 1280×720）。無建置步驟、無 npm、無音效。

## 線上（意圖）

部署後老師開啟：

https://island-table.onrender.com

老師備課頁（遊戲頁**沒有**連到這裡）：

https://island-table.onrender.com/teacher

## 本機遊玩

用任何靜態伺服器開 `site/`，或直接用瀏覽器打開 `site/index.html`。

範例（Python）：

```bash
cd site
python -m http.server 8080
```

然後開啟 http://localhost:8080/

老師頁：http://localhost:8080/teacher/

## 怎麼玩

1. 路線從**藍鵲**開始（不可點）。
2. 點**山蘇**、**愛玉**（必要），可選點**黑熊**或**鍋**（不要兩個都點）。
3. 按**出發**。
4. **重來**可在出發前清空路線。成功後按**再玩一次**、失敗後按**再試一次**給下一組。

## 部署

- 公開 GitHub 儲存庫名稱：`island-table`
- 授權：MIT（Copyright (c) 2026 島嶼餐桌）
- Render 靜態站：見 `render.yaml`
  - 發布目錄：`site/`
  - 無 build command、無環境變數
  - 推送 `main` 自動部署
- `docs/` 不發布

## 檔案

| 路徑 | 說明 |
| --- | --- |
| `site/index.html` | 遊戲（孩子頁） |
| `site/teacher/index.html` | 老師頁 |
| `docs/` | 設計文件（不進靜態站） |
| `render.yaml` | Render 靜態站設定 |
