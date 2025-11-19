## 🔎 測試要點（快速理解）
- test_run_sql_fake_pymysql.py 使用 unittest 框架測試 run_sql.py。
- 測試透過在 `sys.modules["pymysql"]` 注入一個假的 `pymysql` 模組，攔截並記錄 `connect()` 與 `cursor()` 的呼叫，避免連到真實資料庫。
- 測試覆寫/還原 `os.environ`，並用 `importlib.import_module("run_sql")` 較真實地執行腳本，驗證錯誤訊息、輸出與 SQL 執行內容。
- 如果你直接執行 `python run_sql.py`，那會需要一個可連線的 MySQL (或你也可以排除/模擬連線)。

---

## ✅ 必要條件
- Python 3.x（建議 3.8+）
- 建議在虛擬環境中運行
- (選擇性) `PyMySQL`, `python-dotenv` — 測試會注入 fake 模組，但安裝依賴能保證 run_sql.py 真正執行時沒問題
- 安裝依賴檔案：requirements.txt（本專案內有 `PyMySQL` 與 `python-dotenv`）

---

## ⚙️ 在 Windows (cmd.exe) 下一步步跑測試
打開 cmd.exe，切到專案根目錄，然後依照下列步驟：

1. 移到專案目錄
```bash
cd c:\GitHub\chiisen\csv_replace_user_id
```
2. 建立 & 啟動虛擬環境（建議，不過不是必要）
```bash
python -m venv .venv
.venv\Scripts\activate
```
3. 安裝依賴
```bash
pip install -r requirements.txt
```
4. 執行測試（整個檔案）
```bash
python -m unittest -v tests.test_run_sql_fake_pymysql
```
5. 執行單一測試方法（例如測試：test_all_env_vars_present_runs_and_executes_sql）
```bash
python -m unittest tests.test_run_sql_fake_pymysql.RunSQLTests.test_all_env_vars_present_runs_and_executes_sql -v
```
6. 或使用 unittest 的 discover 來跑整個 tests 目錄：
```bash
python -m unittest discover -v tests
```
7. (可選) 使用 pytest（若安裝）
```bash
pip install pytest
pytest -q tests/test_run_sql_fake_pymysql.py
```

---

## 💡 如果你想「直接」測 run_sql.py（不是用測試）
- 直接從 cmd 設定環境變數，再執行 module：
```cmd
set DB_USER=test_user
set DB_PASS=test_pass
set DB_HOST=localhost
set DB_PORT=3306
set DB_NAME=test_db
set USER_ID=111,222
python run_sql.py
```
- 注意：直接跑會實際嘗試連線 MySQL，若你沒有 MySQL 或不想連線，請不要直接跑或改用 fake pymysql 模組。

---

## 🛠️ 常見問題 & 排錯
- 如果跑測試時出現 `RuntimeError: 缺少必要的環境變數`：
  - 該錯誤在测试 `test_missing_env_vars_raises` 中是刻意觸發的，正常。
  - 如果在其他測試出現，可能 .env 或環境變數被干擾。測試已有 setUp/tearDown 還原環境，確保你從未手動 import `run_sql` 或在全局執行時設定了其它 env。
- 若看到 `Please install PyMySQL`：
  - 安裝 `PyMySQL`（或安裝 requirements.txt）；不然 `import pymysql` 會報錯。
  - 在測試中，`pymysql` 被替換為 `FakePyMySQLModule`（用 `sys.modules` 注入），所以通常測試不會觸發此錯。
- 若 sql 目錄不存在或沒有 SQL 檔：
  - run_sql.py 會列印提示並結束（這是正常的行為）。
- 若你看到測試傳入 `conn.executed` 內沒有包含 `USER_ID` 替換後的值：
  - 檢查 `sql/*.sql` 內是否存在 token `##USER_ID##`；測試模擬會讀檔，所以在沒 SQL 文件情況下，可能不會有 statements 被執行。

---

## 🔋 測試與 CI 推薦
- 加入 pytest 與 `tox` 或 GitHub Actions workflow 可以幫助自動化測試。
- 若你在 CI 中需要用 fake DB，請使用相同的 technique（注入 fake pymysql）或用 Docker 啟動 MySQL 實例進行整合測試。

---

## 🎯 如果遇到錯誤
請把以下資訊貼上來，我可以幫你更精確排錯：
- 你執行的完整命令與回傳錯誤/輸出
- 如果測試失敗，貼上失敗的測試跟錯誤訊息（Traceback）
- 是否已在虛擬環境中安裝 requirements（及版本）

