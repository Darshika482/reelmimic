---
name: app-walkthrough
engine: hyperframes
medium: 2d-vector
priority: 58
---
# 手機 App 完整功能導覽（旁白 + 手機外框截圖，一章一個功能）

## 辨識特徵
- 畫面：手機外框裡的真實 App 截圖（滑入切換、慢速捲動），左側章節編號 + 標題 + 逐條亮起的重點
- 剪接：跟著旁白一章一章走，每章 2–5 張截圖，章與章之間交叉淡化；片長通常 3–6 分鐘
- 聲音：全程旁白（TTS 或真人），音樂可有可無
- 文字：章節標題、重點條列、跟旁白同步的字幕（片語級）

## 製作預設
- 16:9、1920×1080、30fps；片長由旁白決定（約 170 字/分鐘的 Kokoro 語速）
- 範例專案：`docs/examples/app-walkthrough/`（script.json → 截圖 → TTS → build.py → render）
- 截圖：用 Playwright 開 App（手機 viewport 390×844、deviceScaleFactor 2），灌一個「示範店」的假資料再逐頁拍；名字、電話全部虛構
- 旁白：`npx hyperframes tts <txt> -v af_heart`（需要 `pip install kokoro-onnx soundfile`）；每章一個 wav，build.py 用 silencedetect 把字幕對齊到真實停頓
- 字型：Montserrat（標題、內文）+ EB Garamond（章節眉標），兩者都是 HyperFrames 內建，雲端也能渲染

## 已知的坑
- 使用者要求不露出 App 名稱時：DOM 文字可在截圖前用 init script 清掉，但 **PDF 預覽是畫在 canvas 上的**、檔名與 WhatsApp 文字是程式產生的——要在 Playwright 用 `context.route` 改寫 dev server 回傳的 JS 字串才清得乾淨。每張截圖前都檢查 `innerText` 有沒有殘留。
- 雲端環境擋 OpenStreetMap 圖磚（403），地圖選點畫面會是空白，不要拿來當截圖。
- 手機外框的瀏海會蓋住 App 頂端（離線橫幅、標題列）；改用一條獨立的狀態列，截圖放在它下面。截圖的慢速捲動幅度要小（≤ 25px），不然頂端的重要訊息會被捲走。
- 字幕片語太短會被 `check` 的 line_unread 擋下：把短片語和相鄰片語合併，每章最後一句延長到下一章旁白開始前。
- 在儀表板按返回會跳出「關閉 App？」對話框擋住點擊——每組截圖用一個全新的瀏覽器開始。
- 雲端渲染時 headless Chrome 連不到 cdn.jsdelivr.net（snapshot 會過、render 才失敗：`Cannot read properties of null (reading 'timeline')`）——GSAP 用 `npm pack gsap@3.15.0` 取出 `gsap.min.js` 放進 `video/assets/`，以本機路徑載入。
