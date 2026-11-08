# Antigravity 教學影片研習簡易版

這是 [claude-video-specs-lite](https://github.com/mathruffian-dot/claude-video-specs-lite) 的**本機工作區改編版**，針對一般中小學教師、Windows 與沒有獨立 GPU 的情境調整。上游仍保留三類：活動紀錄、教學影片、社群科普。此處保留 MIT 授權，完整上游資料可至原倉庫查閱。

本版的示範以 **Python + Pillow + FFmpeg CPU 軟體編碼**製作五場分數短片，提供可修改 JSON、圖片、MP4 和分場字幕初稿。它是簡化驗證，並非原倉庫 HTML／Playwright 動畫管線的替代證明。可依下列提示請 Agent 建立工作區專用環境；不保證每台學校設備都能順利下載或執行。

## 給教師：開啟與第一句話

1. 在 Antigravity 開啟**這個資料夾本身**作為 workspace。開啟新對話或重新載入後，請 Agent 讀本目錄 `AGENTS.md`；具體版本的自動載入情況請依其介面確認。
2. 貼上「課前測試提示詞.md」中的指令，讓 Agent 建立隔離環境、檢查設備並產出有聲示例；若網路或校內政策阻擋，Agent 會回報原因。課前只測設備和操作，不考學科知識。
3. 想產生正式教學片，可請 Agent 依 `規範/02-教學影片.md` 編寫分鏡、示意、旁白與字幕，再輸出並檢查。

## 自動建立環境並重現短片

請把本資料夾作為 Antigravity 工作區，貼上 [課前測試提示詞](課前測試提示詞.md) 的內容。也可在工作區 PowerShell 執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\工具\setup.ps1 -Tts
```

腳本會在此資料夾的 `.local-tools` 下載並驗證固定版本的 uv；用 uv 將 Python 3.12、快取及虛擬環境 `.venv` 放在工作區，安裝 Pillow、edge-tts、mutagen 及含 FFmpeg 的 imageio-ffmpeg 套件。不需電腦原本安裝 Python 或 FFmpeg，不更改 Windows 永久 PATH 或全域 Python。先需要網路、下載空間、Windows x64 和可用的繁體中文字型；若下載受到學校政策、網路或防毒限制，須依其規範排除。`-Tts` 會把**範例旁白文字**送至 Edge TTS 線上服務，並在 `成果/` 內建立不覆寫的資料夾，輸出五場有聲 MP4、旁白稿及 SRT 初稿。這不需要付費 API 金鑰，但不能保證服務可用。

如暫時不能使用線上旁白，移除 `-Tts` 即可產出靜音示範。安裝及首次下載仍需網路；已安裝環境後，是否離線執行會受既有依賴與快取影響。檢查輸出影片的畫面和聲音；SRT 以場景估時，未燒進影片，請校對後使用。不要將 `.local-tools`、`.venv`、`成果` 或個人影片上傳 GitHub。

## 已有 Python 和 FFmpeg 時手動執行

Windows PowerShell，在本資料夾執行：

```powershell
python -X utf8 .\工具\檢查設備.py
python -X utf8 .\工具\製作示範.py --output .\成果\第一次示範
```

第二個指令產出**靜音示範**，顯示 `分數相加.json` 的五個場景，並留下旁白稿和按場景估時的字幕初稿。輸出目錄必須是新資料夾或空資料夾，避免覆寫。字幕是腳本預計顯示時間，並非語音辨識。

如要中文旁白，安裝 `edge-tts` 並有網路時可另選新的輸出資料夾：

```powershell
python -X utf8 .\工具\製作示範.py --tts --output .\成果\有旁白示範
```

`--tts` 使用 Edge TTS 線上服務，將 JSON 的旁白文字傳送至服務；本工作區不要求付費 API Key，但不能保證服務或網路永遠可用。字幕是場景估時，須聽審時間與唸法。範例影片沒有燒入字幕，`.srt` 與 MP4 分開保存；可在支援 SRT 的播放或剪輯工具中使用。無網路時不要執行 `--tts`，可先使用靜音版或由 Agent 協助加入已準備好的配音。

如果工具缺少，基本示範需 Python、Pillow、FFmpeg、可顯示繁體中文的本機字型；語音示例另需 `edge-tts` 與 `mutagen`。有授權及可用網路時，Agent 可在隔離虛擬環境中準備 Python 套件。不要因為缺元件自動修改全機設定。

## 三類影片與外部工具

| 類型 | 建議用途 | 快速入口 |
|---|---|---|
| 教學影片 | 一個概念、一個例子、一個練習 | `規範/02-教學影片.md` |
| 活動紀錄 | 研習、校園活動照片及聲音 | `規範/01-活動紀錄.md` |
| 社群科普 | 清楚解釋一個知識問題 | `規範/03-社群科普.md` |

`示範/分數相加.json` 可複製修改，`title`、`detail`、`narration` 的文字需配合受眾與內容校對；其中 `quarters` 是此四等分示例的繪圖參數，不適用所有學科，可以移除。單場標題和內容欄限單行，過長時程式會提示縮短。例子使用靜態圖卡與場景切換，並非全功能動畫製作器。

既有影片剪輯與全新影片製作是兩條工作路線。要用 Concat MCP，請先核實連線，見 `選配/Concat-MCP.md`；沒有 MCP 可由教師在剪輯工具手動操作。Google Vids 匯入 SRT 可作備援，但各帳號和播放器表現需現場驗證。

## 已做與待確認

- 本版的程式依賴 CPU 軟體編碼，可用於設備煙霧測試；低規學校電腦和 Antigravity IDE 的整體流程**尚未實測**。
- [上游原始資料](https://github.com/mathruffian-dot/claude-video-specs-lite)僅作原版參考；原 README 的 clone 範例指向非 lite 原專案，請不要依此當成本版網址執行一鍵安裝。
- 詳見 `來源與測試.md`，其中區分本機程式測試與原版、其他設備尚未驗證的部分。

官方文件：[Antigravity 規則](https://antigravity.google/docs/rules-workflows?tab=ide)、[MCP](https://antigravity.google/docs/mcp)。
