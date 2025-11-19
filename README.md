# csv_replace_user_id

## 介紹
歡迎使用這個專案！😊  

這個工具專門用來處理 CSV 檔案中的 user_id 欄位替換。🚀  

![130To234ByEli](./images/130To234ByEli.png)

## 環境配置
- Python 3.8.0

⚠️ 注意：`run_sql.py` 需要以下環境變數都已設定才能執行：`DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `USER_ID`。  
若任一變數缺失，程式會中止並顯示錯誤。  

---

## 說明

想像一下，你有正式環境的統計資料，想要安全地轉移到測試環境中。📊  

 
首先，將正式環境的資料匯出為 CSV 格式。📤  

![234_export](./images/234_export.png)

然後，使用我們的 `replace_id.py` Python 程式，輕鬆將正式環境的 user_id 轉換成測試環境的 user_id。🔄  

最後，再將更新後的 CSV 檔案匯入到測試環境的 MySQL 資料庫中。✅  

![234_import](./images/234_import.png)

簡單又高效！🎉  

確保替換過程順利無誤，讓你的資料遷移變得輕鬆愉快！🌟  

## 選擇 Python 的執行版本
按下 `ctrl + shift + p`  
![python-01](./images/python-01.png)

---

![python-02](./images/python-02.png)

---

## 掃描目錄處理所有 CSV：
```bash
python replace_id.py
```
當 input_filename 為 None 時，掃描腳本所在目錄的 *.csv 檔案（會跳過 *-out.csv）。  

## 只處理指定 CSV（多個檔案）：
```bash
python replace_id.py activity_day_202511181636.csv file_info_202511171011.csv
```
會建立輸出資料夾（例如 202511181701）並在裡面放上 *-out.csv 檔案。  

---

## 一次執行多個 SQL 指令:
```bash
python run_sql.py
```

## 要從外部取得 MySQL 的帳密
安裝 `pip install python-dotenv` 可以讀取 `.env` 檔案  
參考環境變數設定 [.env.simple](.env.simple) 檔案內容  
沒用過 .env 你可以參考文件: [env](./docs/env.md)  

### 範例
如果你使用 `.env` 檔案，內容像下面這樣：  
```dotenv
DB_USER=my_user
DB_PASS=my_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=your_database_name
```

在 Windows (cmd.exe) 下執行：  
```cmd
pip install -r requirements.txt
python run_sql.py
```

若不想使用 `.env`，可以直接在命令列先設定環境變數再執行：  
```cmd
set DB_USER=my_user
set DB_PASS=my_password
set DB_NAME=your_database_name
python run_sql.py
```

程式會嘗試連線 MySQL 並顯示 MySQL 版本號；若無法連線，會顯示錯誤資訊並以非零碼退出。  

### 自動替換 SQL 內的 USER_ID
`run_sql.py` 會搜尋專案內的 `./sql` 資料夾，依字母順序讀取所有 `*.sql` 檔案；  
在執行前會把 SQL 檔中的文字 `##USER_ID##` 以 `.env` 或環境變數 `USER_ID` 的值替換再執行。每個 SQL 檔案會在執行後 commit。  

注意：目前採用簡單的 `;` 分割 SQL 指令，若 SQL 裡有比較複雜的內容（例如在字串內有分號），請特別注意或先做測試。  

請務必在 `.env` 或環境變數中設定 `DB_NAME`，`run_sql.py` 不會自動從 SQL 檔中偵測要執行的資料庫；若未設定 `DB_NAME`，程式會立即中止並提示設定。  

---

## ✅ 如何檢查測試檔案與 run_sql.py 的邏輯，接下來提供完整、可執行的測試步驟（含故障排除與進階選項）。
參考: [test](./docs/test.md)  

## 如何取得原始資料
[統計要匯出的所有統計資料](./docs/get_data.md)  
[統計要匯出的統計資料筆數](./docs/get_data_count.md)  
