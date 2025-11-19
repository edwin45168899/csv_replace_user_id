import io
import os
import sys
import importlib
import contextlib
import types
import unittest


class FakeCursor:
    def __init__(self, executed):
        self.executed = executed

    def execute(self, stmt):
        # collect executed statements
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
        # commit is a no-op for the fake connection
        pass

    def close(self):
        # close is a no-op
        pass


class FakePyMySQLModule(types.ModuleType):
    def __init__(self):
        super().__init__("pymysql")
        self.connect_calls = []
        self._last_connection = None
        self.MySQLError = Exception

    def connect(self, *args, **kwargs):
        # record calls and return a fake connection object
        self.connect_calls.append(kwargs.copy())
        executed = []
        conn = FakeConnection(kwargs.copy(), executed)
        self._last_connection = conn
        return conn


class RunSQLTests(unittest.TestCase):
    def setUp(self):
        # snapshot environment and sys.modules
        self._env_snapshot = os.environ.copy()
        self._modules_snapshot = sys.modules.copy()

        # build fake pymysql module and register it
        self.fake_pymysql = FakePyMySQLModule()
        sys.modules["pymysql"] = self.fake_pymysql

        # ensure module not already imported by name 'run_sql'
        sys.modules.pop("run_sql", None)

    def tearDown(self):
        # restore environment and sys.modules
        os.environ.clear()
        os.environ.update(self._env_snapshot)

        sys.modules.clear()
        sys.modules.update(self._modules_snapshot)

    def _remove_env_vars(self, keys):
        for k in keys:
            os.environ.pop(k, None)

    def test_missing_env_vars_raises(self):
        """
        Missing env vars should cause a RuntimeError listing all missing vars
        """
        required = ["DB_USER", "DB_PASS", "DB_HOST", "DB_PORT", "DB_NAME", "USER_ID"]
        # Ensure values are either absent or empty -> treated as missing by run_sql
        for k in required:
            os.environ.pop(k, None)
            os.environ[k] = ""

        # ensure run_sql not present and import fails with RuntimeError
        sys.modules.pop("run_sql", None)
        buff = io.StringIO()
        with self.assertRaises(RuntimeError) as cm:
            with contextlib.redirect_stdout(buff):
                importlib.import_module("run_sql")

        msg = str(cm.exception)
        # message is in Chinese and should list the missing variables
        self.assertIn("缺少必要的環境變數", msg)
        for key in required:
            self.assertIn(key, msg)

    def test_all_env_vars_present_runs_and_executes_sql(self):
        """
        When all env vars are present, the script should import and execute SQL statements
        using the DB_NAME from environment variables.
        """
        # set all env vars
        os.environ["DB_USER"] = "test_user"
        os.environ["DB_PASS"] = "test_pass"
        os.environ["DB_HOST"] = "localhost"
        os.environ["DB_PORT"] = "3306"
        os.environ["DB_NAME"] = "test_db"
        os.environ["USER_ID"] = "111,222"

        sys.modules.pop("run_sql", None)
        buff = io.StringIO()
        with contextlib.redirect_stdout(buff):
            # import the run_sql script which triggers execution
            importlib.import_module("run_sql")

        output = buff.getvalue()

        # Verify output includes the DB_NAME usage print (host/port info)
        self.assertIn("host: localhost:3306,", output)

        # There should be at least two connection calls: one to get version, one to execute statements
        self.assertGreaterEqual(len(self.fake_pymysql.connect_calls), 2)

        # The last connection call must contain db set to our DB_NAME
        last = self.fake_pymysql.connect_calls[-1]
        self.assertEqual(last.get("db"), "test_db")

        # The executed SQL statements should contain the replaced USER_ID token
        conn = self.fake_pymysql._last_connection
        if conn is None:
            self.fail("No database connection was established")
        executed_statements = conn.executed
        self.assertTrue(len(executed_statements) >= 1)
        # assert a replacement occurred with value '111' or '222'
        has_user_id = any(("111" in stmt) or ("222" in stmt) for stmt in executed_statements)
        self.assertTrue(has_user_id)


if __name__ == "__main__":
    unittest.main()
