# Antigravity 連接 Concat：選配流程

本版生成範例不依賴 Concat。若要讓 Agent 編輯使用者既有影片，再檢查該電腦是否已安裝 Concat、是否可由 Antigravity 使用其 MCP。單有安裝程式或設定檔，不代表已連線。

Google 官方文件說 Antigravity CLI 的工作區設定是 `.agents/mcp_config.json`；IDE 亦可在 Agent 側邊欄選 MCP Servers → Manage MCP Servers → View raw config。請依[官方 MCP 文件](https://antigravity.google/docs/mcp)及學校設備現況操作。這個資料夾**沒有**替任何老師預設 Concat 執行檔位置或修改全域 MCP 設定。

建議請 Agent 先查官方說明與實際 Concat 執行檔路徑，再依使用者授權配置限定專案寫入範圍的 `--mcp`；隨後**實際呼叫版本工具**，新建小專案、匯入短測試片、裁切、儲存與輸出。若 MCP 不可用，保留原始素材並用 Concat 的 GUI 手動完成剪輯。

先前在這台電腦驗證過 Antigravity **CLI** 以獨立設定呼叫 Concat MCP，不能推論本工作區或其他教師的 Antigravity **IDE** 已連上。Concat 0.2.9 在該機內建自動字幕曾崩潰；以外部語音轉錄後使用字幕功能的方式作備援。CapCut 內建字幕路線依使用者指示先暫停。
