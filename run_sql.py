import os
import sys
import glob
import re
from pathlib import Path

"""Connect to MySQL using environment variables and show MySQL version.

Environment variables used:
 - DB_USER (required)
 - DB_PASS (required)
 - DB_HOST (optional, defaults to localhost)
 - DB_PORT (optional, defaults to 3306)

Optional: install python-dotenv to load a .env file automatically:
  pip install python-dotenv
"""

# Optional: load .env if python-dotenv is installed and a .env file exists
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv is not None:
    # This will silently do nothing if .env doesn't exist
    load_dotenv()

# Note: we will read required env vars below and validate all are present

required = ["DB_USER", "DB_PASS", "DB_HOST", "DB_PORT", "DB_NAME", "USER_ID"]
missing = [v for v in required if v not in os.environ or not os.environ[v].strip()]
if missing:
    raise RuntimeError(f"缺少必要的環境變數: {', '.join(missing)}。請在 .env 或環境變數中設定它們。")

# use os.environ[] (guaranteed present) and strip whitespace
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
    raise RuntimeError("Please install PyMySQL first: pip install pymysql")

print(f"host: {host}:{port}, 使用者: {user}, 密碼長度: {len(password)} (不會顯示密碼內容)")

try:
    conn = pymysql.connect(host=host, port=port, user=user, password=password)
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        if version:
            print(f"MySQL 版本: {version[0]}")
        else:
            print("無法取得 MySQL 版本")
    # proceed to execute all sql files under ./sql
    script_dir = Path(__file__).resolve().parent
    sql_dir = script_dir / "sql"
    if not sql_dir.exists():
        print(f"沒有找到 sql 目錄: {sql_dir}")
        sys.exit(0)

    # user_id already read from environment above (required)

    sql_files = sorted(glob.glob(str(sql_dir / "*.sql")))
    if not sql_files:
        print("找不到 SQL 檔案 (*.sql) 在 ./sql 目錄，沒有要執行的檔案")
        sys.exit(0)

    # db is required and validated above. If you want automatic detection from SQL USE statements,
    # remove the requirement in the code and re-enable detection.

    # Re-open DB connection for executing statements (use autocommit=False)
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, autocommit=False)
    try:
        with conn.cursor() as cursor:
            for sql_file in sql_files:
                print(f"執行 SQL 檔案: {sql_file}")
                with open(sql_file, "r", encoding="utf-8") as f:
                    raw_sql = f.read()

                # Replace token ##USER_ID##
                sql_text = raw_sql.replace("##USER_ID##", user_id)

                # Split statements by semicolon. This is a simple approach and may
                # fail for semicolons in string literals, but is sufficient for regular SQL files.
                statements = [s.strip() for s in sql_text.split(";") if s.strip()]
                print(f"  取得 {len(statements)} SQL statements，準備執行...")
                for i, stmt in enumerate(statements, start=1):
                    try:
                        # Skip DELIMITER lines if present
                        if re.match(r"^DELIMITER\b", stmt, flags=re.IGNORECASE):
                            continue
                        cursor.execute(stmt)
                    except pymysql.MySQLError as e:
                        print(f"    在檔案 {sql_file} 的 statement #{i} 發生錯誤: {e}")
                        raise
                conn.commit()
                print(f"  已成功執行並 commit 檔案: {sql_file}")
    finally:
        conn.close()
except pymysql.MySQLError as e:
    print(f"host: {host}:{port}, 連線 MySQL 失敗: {e}")
    sys.exit(1)


