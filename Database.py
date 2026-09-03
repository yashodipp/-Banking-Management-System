import os
import getpass
import psycopg2
from typing import Optional

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

def connect_to_database() -> Optional[psycopg2.extensions.connection]:
    """
    Connect to PostgreSQL. Works locally and on Streamlit Cloud.
    Returns None instead of crashing so app.py can show friendly UI.
    """
    load_env_file()

    database_url = _resolve_database_url()
    if database_url:
        try:
            conn = psycopg2.connect(database_url)
            conn.autocommit = True
            print("Connected to PostgreSQL via DATABASE_URL!")
            return conn
        except Exception as error:
            print("Error connecting via DATABASE_URL:", error)
            return None

    # Try individual secrets / env
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

    # On Streamlit Cloud localhost will never work — warn
    if os.path.exists("/mount/src") and host == "localhost":
        print(
            "WARNING: Running on Streamlit Cloud but no DATABASE_URL/pg secrets found. "
            "Set DATABASE_URL in Manage app → Settings → Secrets."
        )
        # still try localhost (will fail) but return None gracefully

    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        connection.autocommit = True
        print("Connected to PostgreSQL database!")
        return connection
    except Exception as error:
        print("Error connecting to PostgreSQL database:", error)
        return None

# For backward compat: app.py does `from Database import connect_to_database`
# Also expose `conn` helpers if needed
def get_connection():
    return connect_to_database()

# Optional global for legacy code — don't crash at import
try:
    conn = connect_to_database()
except Exception as e:
    print(f"Database init warning: {e}")
    conn = None

# Test the connection
if __name__ == "__main__":
    c = connect_to_database()
    if c:
        c.close()
        print("Connection closed.")
    else:
        print("No connection — check env/secrets.")
