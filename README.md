# csv_replace_user_id

## 專案介紹
歡迎使用本專案！😊  
本工具專為批次替換 CSV 檔案中的 `user_id` 欄位而設計，協助您輕鬆處理資料轉換。🚀

![130To234ByEli](./images/130To234ByEli.png)

## 環境需求
- Python 3.8.0

⚠️ **注意**：執行 `run_sql.py` 前，請確保已設定以下環境變數：
`DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `USER_ID`。  
若缺少任一變數，程式將會中止並顯示錯誤訊息。

---

## 使用情境

**情境說明**：  
當您需要將正式環境的統計資料安全地轉移至測試環境時，本工具能協助您完成以下流程：📊

1. **匯出**：將正式環境資料匯出為 CSV 格式。📤

   ![234_export](./images/234_export.png)

2. **轉換**：使用 `replace_id.py` 將 CSV 中的 `user_id` 轉換為測試環境對應的 ID。🔄

3. **匯入**：將處理後的 CSV 檔案匯入測試環境的 MySQL 資料庫。✅

   ![234_import](./images/234_import.png)

**簡單又高效！** 🎉  
確保資料遷移過程順利無誤，讓您的工作更加輕鬆愉快！🌟

## 選擇 Python 直譯器
在 VS Code 中按下 `Ctrl + Shift + P` 選擇 Python 直譯器：  
![python-01](./images/python-01.png)

---

![python-02](./images/python-02.png)

---

## 使用說明

### 1. 批次處理所有 CSV 檔案
掃描當前目錄下所有 CSV 檔案並進行處理：
```bash
python replace_id.py
```
> 若未指定檔案名稱，程式將自動掃描目錄下所有的 `*.csv` 檔案（自動略過 `*-out.csv`）。

### 2. 處理指定 CSV 檔案
您可以指定一個或多個檔案進行處理：
```bash
python replace_id.py activity_day_202511181636.csv file_info_202511171011.csv
```
> 程式會建立一個輸出資料夾（例如 `202511181701`），並將處理後的 `*-out.csv` 檔案存放在其中。

---

### 3. 執行 SQL 指令
批次執行 SQL 檔案：
```bash
python run_sql.py
```

## 資料庫連線設定

### 使用 .env 檔案（推薦）
安裝 `python-dotenv` 以讀取 `.env` 設定檔：
```bash
pip install python-dotenv
```
您可以參考 [.env.simple](.env.simple) 範例檔案。  
若不熟悉 `.env`，請參考文件：[env](./docs/env.md)

**`.env` 範例內容**：
```dotenv
DB_USER=my_user
DB_PASS=my_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=your_database_name
```

**執行步驟**：
```cmd
pip install -r requirements.txt
python run_sql.py
```

### 使用環境變數（不使用 .env）
若不想使用 `.env`，也可直接在命令列設定環境變數：
```cmd
set DB_USER=my_user
set DB_PASS=my_password
set DB_NAME=your_database_name
python run_sql.py
```

> 程式會嘗試連線 MySQL 並顯示版本號；若連線失敗，將顯示錯誤資訊並中止程式。

### 自動替換 SQL 內的 USER_ID
`run_sql.py` 會自動搜尋 `./sql` 資料夾，並依字母順序讀取所有 `*.sql` 檔案。  
在執行前，程式會將 SQL 檔中的 `##USER_ID##` 替換為 `.env` 或環境變數中設定的 `USER_ID` 值。每個 SQL 檔案執行完畢後會自動 Commit。

> **注意**：
> 1. 目前 SQL 指令以分號 `;` 進行分割。若您的 SQL 內容較為複雜（例如字串中包含分號），請務必先進行測試。
> 2. 請務必設定 `DB_NAME`，`run_sql.py` 不會自動偵測資料庫；若未設定，程式將會中止。

---

## 測試與驗證
### ✅ 檢查測試檔案與邏輯
如需完整、可執行的測試步驟（含故障排除與進階選項），請參考：[test](./docs/test.md)

### 如何取得原始資料
- [統計要匯出的所有統計資料](./docs/get_data.md)
- [統計要匯出的統計資料筆數](./docs/get_data_count.md)

## 常見問題與故障排除

### 連線失敗紀錄
**情境**：設定 `DB_HOST=192.168.1.234` 時發生連線錯誤。
```bash
host: 192.168.1.234:3306, 連線 MySQL 失敗: (1130, "Host '192.168.1.45' is not allowed to connect to this MySQL server")
```
**解決方案**：
改用 `DB_HOST=127.0.0.1`，並透過 SSH Tunnel 連線：
```bash
ssh -L 3306:192.168.1.234:3306 root@234
```
建立通道後，即可正常執行 `run_sql.py`。
```
