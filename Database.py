import os
import getpass
import sqlite3
import psycopg2
from typing import Optional
from psycopg2 import OperationalError

def load_env_file(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)

def get_streamlit_secret(*keys):
    try:
        import streamlit as st
        value = st.secrets
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                try:
                    value = value[key]
                except Exception:
                    value = getattr(value, key, None)
            if value is None:
                return None
        return value
    except Exception:
        return None

def _resolve_database_url():
    return (
        os.getenv("DATABASE_URL")
        or os.getenv("NEON_DATABASE_URL")
        or get_streamlit_secret("DATABASE_URL")
        or get_streamlit_secret("NEON_DATABASE_URL")
        or get_streamlit_secret("postgres", "url")
    )

def running_on_streamlit_cloud():
    return os.path.exists("/mount/src") or bool(os.getenv("STREAMLIT_CLOUD"))

# --- SQLite fallback ---
class _SQLiteCursorWrapper:
    def __init__(self, cur):
        self._cur = cur
    def _convert_params(self, params):
        if not params:
            return params
        converted = []
        for p in params:
            # sqlite3 doesn't support Decimal - convert to float/str
            if p.__class__.__name__ == "Decimal":
                converted.append(float(p))
            else:
                converted.append(p)
        return tuple(converted)
    def execute(self, query, params=None):
        if not isinstance(query, str):
            query = str(query)
        q = query
        # Translate Postgres -> SQLite
        q = q.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        q = q.replace("%s", "?")
        q = q.replace(" ILIKE ", " LIKE ")
        if "setval" in q.lower():
            return self
        if params is None:
            params = ()
        else:
            params = self._convert_params(params)
        try:
            if params:
                return self._cur.execute(q, params)
            else:
                return self._cur.execute(q)
        except sqlite3.OperationalError as e:
            if "RETURNING" in q:
                base_q = q.split("RETURNING")[0].strip()
                if params:
                    self._cur.execute(base_q, params)
                else:
                    self._cur.execute(base_q)
                self._cur._fake_lastrowid = self._cur.lastrowid
                return self
            raise
    def fetchone(self):
        if hasattr(self._cur, "_fake_lastrowid"):
            return (self._cur._fake_lastrowid,)
        return self._cur.fetchone()
    def fetchall(self):
        return self._cur.fetchall()
    def close(self):
        return self._cur.close()
    def __getattr__(self, name):
        return getattr(self._cur, name)

class _SQLiteConnectionWrapper:
    def __init__(self, sqlite_conn):
        self._conn = sqlite_conn
        self.autocommit = True
        self.closed = 0
        self.is_sqlite = True
    def cursor(self, *a, **kw):
        return _SQLiteCursorWrapper(self._conn.cursor())
    def commit(self):
        try:
            return self._conn.commit()
        except Exception:
            pass
    def rollback(self):
        try:
            return self._conn.rollback()
        except Exception:
            pass
    def close(self):
        self.closed = 1
        return self._conn.close()
    def __getattr__(self, name):
        return getattr(self._conn, name)

def _get_sqlite_connection():
    db_path = "/tmp/bank_demo.db" if running_on_streamlit_cloud() else os.path.join(os.path.dirname(__file__), "bank_demo.db")
    db_path = os.getenv("SQLITE_PATH") or db_path
    try:
        os.makedirs(os.path.dirname(os.path.abspath(db_path)) if os.path.dirname(db_path) else ".", exist_ok=True)
    except Exception:
        pass
    raw = sqlite3.connect(db_path, check_same_thread=False)
    raw.row_factory = None
    try:
        raw.execute("PRAGMA foreign_keys = ON;")
    except Exception:
        pass
    wrapper = _SQLiteConnectionWrapper(raw)
    print(f"SQLite fallback active: {db_path} (set DATABASE_URL for Postgres)")
    return wrapper

def connect_to_database() -> Optional[psycopg2.extensions.connection]:
    load_env_file()
    database_url = _resolve_database_url()
    if database_url:
        try:
            conn = psycopg2.connect(database_url)
            conn.autocommit = True
            print("Connected to PostgreSQL via DATABASE_URL!")
            return conn
        except Exception as error:
            print(f"Error connecting via DATABASE_URL ({error}), trying SQLite fallback")
    host = (
        get_streamlit_secret("PGHOST")
        or get_streamlit_secret("postgres", "host")
        or os.getenv("PGHOST", "localhost")
    )
    database = (
        get_streamlit_secret("PGDATABASE")
        or get_streamlit_secret("postgres", "database")
        or os.getenv("PGDATABASE", "BankData")
    )
    user = (
        get_streamlit_secret("PGUSER")
        or get_streamlit_secret("postgres", "user")
        or os.getenv("PGUSER", "yashodip")
    )
    port = (
        get_streamlit_secret("PGPORT")
        or get_streamlit_secret("postgres", "port")
        or os.getenv("PGPORT", "5432")
    )
    password = (
        get_streamlit_secret("PGPASSWORD")
        or get_streamlit_secret("postgres", "password")
        or os.getenv("PGPASSWORD", "1234")
    )
    if running_on_streamlit_cloud() and host == "localhost":
        print("No DATABASE_URL on Cloud - using SQLite fallback for always-on")
        return _get_sqlite_connection()
    try:
        connection = psycopg2.connect(host=host, port=port, database=database, user=user, password=password)
        connection.autocommit = True
        print("Connected to PostgreSQL database!")
        return connection
    except Exception as error:
        print(f"Error connecting to PostgreSQL ({error}), using SQLite fallback")
        return _get_sqlite_connection()

def get_connection():
    return connect_to_database()

try:
    conn = connect_to_database()
except Exception as e:
    print(f"Database init warning: {e}")
    try:
        conn = _get_sqlite_connection()
    except Exception:
        conn = None

if __name__ == "__main__":
    c = connect_to_database()
    if c:
        c.close()
        print("Connection closed.")
    else:
        print("No connection — check env/secrets.")
