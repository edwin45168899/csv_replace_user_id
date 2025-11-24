import os
import sys
import glob
import re
from pathlib import Path
from datetime import datetime, timedelta, date as datetime_date


def get_custom_week_number(date):
    # 找到該年的第一個星期日
    first_day_of_year = datetime_date(date.year, 1, 1)
    # 計算第一個星期日是哪一天
    days_to_first_sunday = (6 - first_day_of_year.weekday()) % 7  # weekday: 0=Mon, 6=Sun
    first_sunday = first_day_of_year + timedelta(days=days_to_first_sunday)
    
    # 計算從第一個星期日到當前日期的天數
    days_since_first_sunday = (date - first_sunday).days
    
    # 週數 = 天數 // 7 + 1
    if days_since_first_sunday >= 0:
        week_num = (days_since_first_sunday // 7) + 1
    else:
        # 如果日期在第一個星期日前，使用上一年的週數（這裡簡化，實際可能需要調整）
        week_num = 52  # 或計算上一年
    
    return week_num

"""使用環境變數 (Environment Variables) 連線至 MySQL 並顯示 MySQL 版本。

使用的環境變數 (Environment Variables)：
 - DB_USER (必要)
 - DB_PASS (必要)
 - DB_HOST (選用，預設為 localhost)
 - DB_PORT (選用，預設為 3306)

選用：安裝 python-dotenv 以自動載入 .env 檔案：
  pip install python-dotenv
"""

# 選用：若已安裝 python-dotenv 且存在 .env 檔案，則載入 .env
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv is not None:
    # 若 .env 不存在，此處將不會執行任何動作且不報錯
    load_dotenv()

# 注意：下方將讀取必要的環境變數 (Environment Variables) 並驗證是否皆已設定

required = ["DB_USER", "DB_PASS", "DB_HOST", "DB_PORT", "DB_NAME", "USER_ID"]
missing = [v for v in required if v not in os.environ or not os.environ[v].strip()]
if missing:
    raise RuntimeError(f"缺少必要的環境變數: {', '.join(missing)}。請在 .env 或環境變數中設定它們。")

# 使用 os.environ[] (確保變數存在) 並去除空白字元 (Whitespace)
user = os.environ["DB_USER"].strip()
password = os.environ["DB_PASS"].strip()
host = os.environ["DB_HOST"].strip()
port_raw = os.environ["DB_PORT"].strip()
try:
    port = int(port_raw)
except Exception:
    raise RuntimeError("DB_PORT 必須是一個整數，例如 3306")
db = os.environ["DB_NAME"].strip()
user_id = os.environ["USER_ID"].strip()

try:
    import pymysql
except Exception:
    raise RuntimeError("請先安裝 PyMySQL：pip install pymysql")

print(f"host: {host}:{port}, db: {db}, 使用者: {user}, 密碼長度: {len(password)} (不會顯示密碼內容)")

try:
    conn = pymysql.connect(host=host, port=port, user=user, password=password)
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        if version:
            print(f"MySQL 版本: {version[0]}")
        else:
            print("無法取得 MySQL 版本")
    # 接著執行 ./sql 目錄下的所有 SQL 檔案
    script_dir = Path(__file__).resolve().parent
    sql_dir = script_dir / "sql"
    if not sql_dir.exists():
        print(f"沒有找到 sql 目錄: {sql_dir}")
        sys.exit(0)

    # user_id 已從上方環境變數 (Environment Variables) 讀取 (必要)

    sql_files = sorted(glob.glob(str(sql_dir / "*.sql")))
    if not sql_files:
        print("找不到 SQL 檔案 (*.sql) 在 ./sql 目錄，沒有要執行的檔案")
        sys.exit(0)

    # db 為必要且已在上方驗證。若您希望從 SQL USE 語句 (Statements) 自動偵測，
    # 請移除程式碼中的限制並重新啟用偵測功能。

    # 重新建立 DB 連線以執行語句 (Statements) (使用 autocommit=False)
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, autocommit=False)
    try:
        with conn.cursor() as cursor:
            for idx, sql_file in enumerate(sql_files, start=1):
                # 在日誌 (Logs) 中包含目前檔案索引 / 總數
                print(f"執行 SQL 檔案 ({idx}/{len(sql_files)}): {sql_file}")
                with open(sql_file, "r", encoding="utf-8") as f:
                    raw_sql = f.read()

                # 替換代碼 (Token) ##USER_ID##
                sql_text = raw_sql.replace("##USER_ID##", user_id)
                
                # 算出今年的年份                
                current_year = datetime.now().year
                sql_text = sql_text.replace("##YEAR##", str(current_year))
                
                # 計算出今天的年月日，格式為 YYYY-MM-DD
                today_str = datetime.now().strftime("%Y-%m-%d")
                sql_text = sql_text.replace("##TODAY##", today_str)

                # 計算出今天第幾周
                now = datetime.now()
                current_week = get_custom_week_number(now.date())
                sql_text = sql_text.replace("##WEEK##", str(current_week))

                print(f"  計算出 ##YEAR## => {current_year} , ##TODAY## => {today_str} , ##WEEK## => {current_week} ")

                # 以分號 (Semicolon) 分割語句 (Statements)。這是一個簡單的方法，
                # 對於字串常值 (String Literals) 中包含分號的情況可能會失敗，但對一般 SQL 檔案已足夠。
                statements = [s.strip() for s in sql_text.split(";") if s.strip()]
                print(f"  取得 {len(statements)} 條 SQL 語句 (Statements)，準備執行...")
                for i, stmt in enumerate(statements, start=1):
                    try:
                        # 若存在 DELIMITER 行則略過
                        if re.match(r"^DELIMITER\b", stmt, flags=re.IGNORECASE):
                            continue
                        #cursor.execute(stmt)
                    except pymysql.MySQLError as e:
                        print(f"    在檔案 ({idx}/{len(sql_files)}) {sql_file} 的語句 (Statement) #{i} 發生錯誤: {e}")
                        raise
                conn.commit()
                print(f"  已成功執行並 commit 檔案 ({idx}/{len(sql_files)}): {sql_file}")
    finally:
        conn.close()
except pymysql.MySQLError as e:
    print(f"host: {host}:{port}, 連線 MySQL 失敗: {e}")
    sys.exit(1)


