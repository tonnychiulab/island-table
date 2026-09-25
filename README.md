# 島嶼餐桌 · 藍鵲播種

靜態網頁教室小遊戲。老師用瀏覽器打開並投影（版面 1280×720）。無建置步驟、無 npm、無音效。藍鵲一局凍結；另有三關（五色鳥、台灣獼猴、寬尾鳳蝶）只從老師頁開啟。

## 線上

部署後老師開啟：

https://island-table-r050.onrender.com

| 關卡 | 網址 |
| --- | --- |
| 藍鵲播種 | https://island-table-r050.onrender.com/ |
| 五色鳥 | https://island-table-r050.onrender.com/barbet |
| 台灣獼猴 | https://island-table-r050.onrender.com/macaque |
| 寬尾鳳蝶 | https://island-table-r050.onrender.com/butterfly |

老師備課頁（遊戲頁**沒有**連到這裡；關卡連結只在本頁）：

https://island-table-r050.onrender.com/teacher

## 本機遊玩

用任何靜態伺服器開 `site/`，或直接用瀏覽器打開對應 `index.html`。

範例（Python）：

```bash
cd site
python -m http.server 8080
```

然後開啟 http://localhost:8080/（藍鵲）、`/barbet/`、`/macaque/`、`/butterfly/`。

老師頁：http://localhost:8080/teacher/

## 怎麼玩（藍鵲）

1. 路線從**藍鵲**開始（不可點）。
2. 點**山蘇**、**愛玉**（必要），可選點**黑熊**或**鍋**（不要兩個都點）。
3. 按**出發**。
4. **重來**可在出發前清空路線。成功後按**再玩一次**、失敗後按**再試一次**給下一組。

三關新地圖：動物為起點（不可點）；點正確植物（綠）；避開錯誤目標（棕）；判定規則見 `docs/SDD-taiwan-field-guide.md` 第 7.1a 節。

## 部署

- 公開 GitHub 儲存庫名稱：`island-table`
- 授權：MIT（Copyright (c) 2026 島嶼餐桌）
- 瀏覽器分頁圖示 `site/favicon.svg` 為原創幾何標記（藍圓，對應藍鵲節點色），非物種插圖、非 Kenney 素材；同樣適用 MIT（Copyright (c) 2026 島嶼餐桌）。
- Render 靜態站：見 `render.yaml`
  - 發布目錄：`site/`
  - 無 build command、無環境變數
  - 推送 `main` 自動部署
- `docs/` 不發布

## 檔案

| 路徑 | 說明 |
| --- | --- |
| `site/index.html` | 藍鵲播種（孩子頁，凍結） |
| `site/barbet/index.html` | 五色鳥關 |
| `site/macaque/index.html` | 台灣獼猴關 |
| `site/butterfly/index.html` | 寬尾鳳蝶關 |
| `site/favicon.svg` | 分頁圖示（原創幾何標記） |
| `site/teacher/index.html` | 老師頁（含關卡連結） |
| `docs/` | 設計文件（不進靜態站） |
| `render.yaml` | Render 靜態站設定 |
