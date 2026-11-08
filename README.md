# 教師 AI 影片工作坊：Codex × Antigravity

這份工作包協助使用 Windows 電腦的老師，透過 Codex 或 Google Antigravity（AGY）建立本機工作環境，製作簡短的教學示範影片。依本機條件以 CPU 軟體編碼，不要求獨立 GPU。

## 第一次使用：將以下指令貼給你的 Agent

```text
請下載 https://github.com/mathruffian-dot/teacher-video-workshop，
在我的 Windows 電腦開啟這個工作資料夾，讀取根目錄的 AGENTS.md 和 README.md。
我是使用 Codex／Antigravity（請保留我使用的那一個）。
請依對應資料夾的說明檢查設備，在這個專案中建立隔離的環境，
安裝製作示範所需要的套件，接著產出教學示範影片及可修改的材料。
可以使用網路下載必要依賴和產生示範旁白；不要修改我的其他專案或全域設定。
完成後告訴我成果的位置，並說明是否成功，以及需要我播放檢查的地方。
```

已下載專案時，請在 Codex 或 Antigravity **開啟整個專案資料夾**，再貼上提示詞。如果 Agent 有執行命令的權限提示，請檢查內容後依介面操作。學校電腦可能有下載、安裝或網路限制。

## 選擇你的 Agent

| 你使用的工具 | 入口 | 範例 |
|---|---|---|
| Codex | [Codex 工作包](Codex版/README.md) | 教學圖卡，可製作影片與旁白 |
| Google Antigravity（AGY） | [Antigravity 工作包](Antigravity版/README.md) | 分數相加教學圖卡，可選擇中文旁白 |

兩個工作包各自帶有檢查設備及製作示範的說明，也保留可修改的教學內容。請依所用工作包的文件進行；兩個示範的內容及功能不完全相同。

## 使用前請知道

- 此專案製作的是**從文字與圖卡產生短片**的示範；將現有影片自動去除停頓、在 Concat 繼續剪輯，是另一條工作流程，不會因安裝本工作包就自動完成。
- 初次下載套件及使用 Agent 需網路；選用 Edge TTS 時，旁白文字會傳送至線上語音服務。不要將個資或不適合上傳的內容用於線上旁白。服務或校園網路可能無法使用。
- 不需要付費 API 金鑰才能執行工作包的靜音示範；所使用的 Agent 服務本身可能需要帳號、方案或網路。沒有 GPU 不等於一定適合每一台電腦，速度和相容性請課前實測。
- 影片與字幕仍需老師檢查內容、發音、斷句與時間點；生成影片後請播放再用於教學。工作包不是評量學生的測驗。

## 出處與授權

本工作包改編自 [claude-video-specs-lite](https://github.com/mathruffian-dot/claude-video-specs-lite)，保留上游 MIT 授權及部分規範；完整原始資料請至上游倉庫查閱。亦參考 [claude-motion-explainer](https://github.com/mathruffian-dot/claude-motion-explainer) 的分鏡和檢查觀念。詳見各工作包的來源說明。第三方套件、字型與線上服務各自有授權和使用條件。
