# 🌦️ LINE 天氣查詢機器人（LINE Weather Bot）

本專案為一個整合 LINE Messaging API、Google Sheets 與[中央氣象署](https://www.cwa.gov.tw/V8/C/)資料的 **天氣查詢聊天機器人**，可部署至 Google Cloud Run。使用者可透過 LINE 對話快速查詢各縣市的今日、明日或一週天氣預報。

---
## 🧩 功能特色

- Quick Reply 快速查詢：依區域 → 縣市 → 日期選擇
- 即時讀取 Google Sheets 的天氣資料(資料爬蟲程式來自[中央氣象署天氣資料自動擷取器](https://github.com/blueskycm/taiwan-weather-crawler))
- 支援今日 / 明日 / 一週預報
- 今日查詢依台灣日期，從該縣市當日有效預報中選擇最新紀錄；可使用前一天抓取的預報，並顯示資料寫入時間（台灣時間）。
- 圖示化顯示天氣描述、體感、紫外線指數
- 部署於 Google Cloud Run，支援擴充與穩定運行

---
## 📱 快速加入 LINE 天氣機器人
掃描下方 QR Code 立即體驗 ⬇️

[![加入LINE天氣機器人](line_qrcode.png)](https://lin.ee/eDmDfiq)

---
## 📂 專案架構
```plaintext
├── main.py # Flask 主程式，處理 LINE Webhook 與訊息邏輯
├── utils
│   └── sheets.py # 從 Google Sheets，取得天氣資訊
├── Dockerfile # 建立 Docker 映像用
├── .env.yaml # Cloud Run 環境變數檔（部署用）
├── .env # 本地測試用的環境變數檔
├── requirements.txt # Python 套件需求
└── README.md
```

---
## 🖥️ 本地開發與測試

### 1. 安裝所需套件

```bash
pip install -r requirements.txt
```
### 2. 建立 .env 檔案
```ini
CHANNEL_SECRET=你的LINE_CHANNEL_SECRET
CHANNEL_ACCESS_TOKEN=你的LINE_CHANNEL_ACCESS_TOKEN
GOOGLE_SHEET_ID=你的 Google Sheets ID
GOOGLE_CREDENTIALS_JSON={"type": "..."}  # 攤平成一行的 service account json 字串
```
### 3. 本地啟動
```bash
python main.py
```
### 4. ngrok 測試 LINE Webhook
```bash
ngrok http 8080
```
並將 Webhook 設定為：
```ini
https://xxxxx.ngrok.io/callback
```
---
## ☁️ Google Cloud Run 部署步驟
### 1. 準備 .env.yaml
```yaml
CHANNEL_SECRET: "你的LINE_CHANNEL_SECRET"
CHANNEL_ACCESS_TOKEN: "你的LINE_CHANNEL_ACCESS_TOKEN"
GOOGLE_SHEET_ID: "你的 Google Sheets ID"
GOOGLE_CREDENTIALS_JSON: '{"type": "..."}'  # 攤平成一行 JSON 字串
```
### 2. 建立 Docker Build
```bash
gcloud run deploy line-weather-bot \
  --project=你的PROJECT_ID \
  --region=asia-east1 \
  --source=. \
  --allow-unauthenticated \
  --env-vars-file=.env.yaml
```

---
## 📌 注意事項
- Google Sheets 權限需設為「允許 Service Account 讀取」
- .env 供本地測試，.env.yaml 用於 Cloud Run 部署
- 若有更新請重新 build 並部署
- 2026-10-26：今日查詢修正已部署至 `trn3-466407` / `asia-east1` / `line-weather-bot`，版本 `line-weather-bot-00005-hmw`。正式表清晨 05:00 唯讀情境檢查及 webhook 空事件測試（HTTP 200）通過。

---
## 📝 授權與貢獻
此專案僅供學習與展示用途，如需商用請自行擴充與保護安全驗證。

---
## 📬 聯絡方式
- 作者：陳宗葆
- Email：blueskycm@gmail.com