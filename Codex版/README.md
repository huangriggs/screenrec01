# 教學影片研習簡易版｜Codex 版

給 Windows 老師使用 Codex，從示例內容產生 CPU 編碼的教學短片。第一次準備環境需要網路，電腦可以沒有獨立 GPU。改編自 [claude-video-specs-lite](https://github.com/mathruffian-dot/claude-video-specs-lite)，保留其 MIT 授權及三類影片規範。

## 讓 Codex 幫你準備並做出第一支影片

1. 將此 GitHub 專案下載或 clone 到自己的電腦，在 Codex 開啟本資料夾。
2. 貼上以下指令，等待 Agent 執行，按 Codex 畫面提供操作授權：

> 請閱讀此資料夾的 AGENTS.md 和 README.md，幫我在本專案內建立研習影片環境，執行設備檢查，再用 CPU 重現有中文旁白的示範短片。使用本專案的 scripts/setup.ps1 -Tts；我同意下載所需工具及將範例旁白文字傳送到 Edge TTS。請不要上傳我的影片或更改我的全域設定。完成後檢查影片、字幕並告訴我儲存位置及尚需人工確認的項目。

也可自行在此資料夾的 PowerShell 執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Tts
```

首次執行會在本資料夾 `.local-tools` 和 `.venv` 下載 uv、Python 3.12、Pillow、imageio-ffmpeg、edge-tts 和 mutagen，並產生 MP4 及獨立 SRT。uv 壓縮檔有固定 SHA-256 驗證；Python 和 Python 套件由 uv 從網路取得。FFmpeg 執行檔來自 imageio-ffmpeg 的平台套件，使用 `libx264` CPU 軟體編碼。腳本不永久更改全域 PATH，`-ExecutionPolicy Bypass` 僅作用於該 PowerShell 行程。安裝過程需學校網路和相關執行權限，大小與耗時依環境而異；若被阻擋，請將錯誤交給 Codex 協助。

**本自動準備腳本僅支援 Windows x64。** 已存在的 `.venv` 會被使用而不刪除；如果損壞或無寫入權限，請先讓 Agent 診斷，不要覆蓋其他專案。ARM64、其他作業系統，請依 Python 和各工具的官方方式另行準備，尚未實測。

Edge TTS 會把**旁白文字**傳至線上服務，不傳影片；服務可用性不保證。若不想使用，省略 `-Tts` 即得到靜音版。Codex Agent 本身及首次下載亦需要網路。例子以 Windows 內建中文字型為預設；缺字型可用 `--font` 指定合法取得的字型。

## 成果與限制

- 產出位置在 `示例/輸出/`，每次以新名稱保存，不覆蓋既有影片。預設內容可編輯 [示例/認識因數.json](示例/認識因數.json)；另有比的意思範例 [示例/內容.json](示例/內容.json)。
- 有聲版的 SRT 按場景時間產生，未燒進影片，也不是精確逐字時間碼。旁白、字幕斷句、時碼及畫面仍須實際播放檢查。
- 預設「認識因數」採四場靜態圖卡，重現前次的重點與旁白，但畫面是新製圖卡，與前次上游 HTML 截圖及實作不同；也不是 HyperFrames 動畫或影片自動剪輯。
- 本機圖卡影片範例不需要 Concat MCP、字幕辨識模型和 Google Vids，這些工具須另行設定或測試。
- 低規學校電腦和所有學校網路尚未實測；不能保證三小時內完成安裝及輸出。

## 已有環境時

```powershell
.\.venv\Scripts\python.exe -X utf8 .\scripts\課前檢查.py
.\.venv\Scripts\python.exe -X utf8 .\scripts\產生示範.py --tts --config .\示例\認識因數.json --output .\示例\輸出\我的影片.mp4
```

已有錄音可改用 `--audio 旁白.wav`；長於影片的音檔會截斷，請核對聲畫。`specs/` 為上游參考；完整上游範例及工具鏈請見原倉庫，本版不提供上游 `install/` 安裝腳本。更多資訊見 [課前測試與提示詞](課前測試與提示詞.md) 和 [來源與調整](來源與調整.md)。
