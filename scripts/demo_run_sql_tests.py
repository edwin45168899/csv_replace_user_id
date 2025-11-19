import io
import os
import sys
import importlib
import contextlib
import types
from pathlib import Path

# Ensure project repository root is on sys.path to allow importing run_sql module
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


class FakeCursor:
    def __init__(self, executed):
        self.executed = executed

    def execute(self, stmt):
        self.executed.append(stmt)

    def fetchone(self):
        return ("8.0.33",)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, connect_kwargs, executed_container):
        self.connect_kwargs = connect_kwargs
        self.executed = executed_container

    def cursor(self):
        return FakeCursor(self.executed)

    def commit(self):
        pass

    def close(self):
        pass


class FakePyMySQLModule(types.ModuleType):
    def __init__(self):
        super().__init__("pymysql")
        self.connect_calls = []
        self._last_connection = None
        self.MySQLError = Exception

    def connect(self, *args, **kwargs):
        self.connect_calls.append(kwargs.copy())
        conn = FakeConnection(kwargs.copy(), [])
        self._last_connection = conn
        return conn


def scenario_missing_env():
    print("\n=== Scenario 1: Missing env vars (should raise RuntimeError) ===")
    # ensure required env vars are empty
    required = ["DB_USER", "DB_PASS", "DB_HOST", "DB_PORT", "DB_NAME", "USER_ID"]
    for k in required:
        os.environ.pop(k, None)
        os.environ[k] = ""

    fake_pymysql = FakePyMySQLModule()
    sys.modules["pymysql"] = fake_pymysql
    sys.modules.pop("run_sql", None)

    buff = io.StringIO()
    try:
        with contextlib.redirect_stdout(buff):
            importlib.import_module("run_sql")
    except RuntimeError as e:
        print("Caught RuntimeError as expected:", e)
        print("Captured stdout:")
        print(buff.getvalue())
        return True
    except Exception as e:
        print("Unexpected exception:", type(e).__name__, e)
        return False

    print("No RuntimeError raised, test failed. Captured stdout:")
    print(buff.getvalue())
    return False


def scenario_all_env_vars():
    print("\n=== Scenario 2: All env vars present (should run) ===")
    # set env vars
    os.environ["DB_USER"] = "test_user"
    os.environ["DB_PASS"] = "test_pass"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "3306"
    os.environ["DB_NAME"] = "test_db"
    os.environ["USER_ID"] = "111,222"

    fake_pymysql = FakePyMySQLModule()
    sys.modules["pymysql"] = fake_pymysql
    sys.modules.pop("run_sql", None)

    buff = io.StringIO()
    try:
        with contextlib.redirect_stdout(buff):
            importlib.import_module("run_sql")
    except Exception as e:
        print("Script raised unexpected exception:", e)
        print(buff.getvalue())
        return False

    out = buff.getvalue()
    print("Captured stdout:")
    print(out)

    # validate connect calls and executed statements
    calls = fake_pymysql.connect_calls
    print("pymysql.connect calls:", calls)
    if not calls or len(calls) < 2:
        print("Not enough connect calls recorded")
        return False

    if calls[-1].get("db") != os.environ["DB_NAME"]:
        print("DB_NAME not used on second connection")
        return False

    conn = fake_pymysql._last_connection
    if not conn or not conn.executed:
        print("No SQL statements captured by fake connection")
        return False

    print("Number of captured SQL statements:", len(conn.executed))
    print("First executed statement preview:", conn.executed[0][:120].replace('\n', ' '))
    if any("111" in s or "222" in s for s in conn.executed):
        print("USER_ID token was replaced in executed statements.")
    else:
        print("No USER_ID token found in executed statements.")
        return False

    return True


if __name__ == "__main__":
    ok1 = scenario_missing_env()
    ok2 = scenario_all_env_vars()
    print("\nSummary: scenario_missing_env ->", ok1, "; scenario_all_env_vars ->", ok2)
    sys.exit(0 if (ok1 and ok2) else 1)
