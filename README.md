# csv_replace_user_id

## 介紹
歡迎使用這個專案！😊

這個工具專門用來處理 CSV 檔案中的 user_id 欄位替換。🚀

![130To234ByEli](./images/130To234ByEli.png)

## 環境配置
- Python 3.8.0

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

