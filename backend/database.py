# =======================================================
# Copyright (c) 2026 Vasuki Upadhya. All rights reserved.
# Author: Vasuki Upadhya (vasuki.upadhya@gmail.com)
# Application: KEA Seat Matrix & Prediction Portal
# =======================================================
"""
Database Connection Utility with PostgreSQL pooling and lock-free SQLite (kcet.db WAL mode) fallback.
"""
import os
import sys
import sqlite3
import traceback
from contextlib import contextmanager

try:
    import psycopg2
    from psycopg2.pool import ThreadedConnectionPool
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

connection_pool = None

def _load_dotenv():
    env_path = os.path.join("backend", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

def init_connection_pool():
    global connection_pool
    if not PSYCOPG2_AVAILABLE:
        return None
    if connection_pool is not None and not getattr(connection_pool, "closed", False):
        return connection_pool
        
    _load_dotenv()
    
    in_docker = os.path.exists("/.dockerenv")
    if in_docker:
        primary_host = os.environ.get("DB_HOST", "db")
        primary_port = os.environ.get("DB_PORT", "5432")
    else:
        env_host = os.environ.get("DB_HOST", "127.0.0.1")
        primary_host = "127.0.0.1" if env_host == "db" else env_host
        primary_port = os.environ.get("DB_PORT", "5433")

    db_name = os.environ.get("DB_NAME", "kcet")
    db_user = os.environ.get("DB_USER", "postgres")
    db_pass = os.environ.get("DB_PASSWORD", "postgres")

    hosts_to_try = [
        (primary_host, primary_port),
        ("127.0.0.1", "5433"),
        ("localhost", "5433"),
        ("127.0.0.1", "5432"),
        ("localhost", "5432")
    ]
    if in_docker:
        hosts_to_try.insert(0, ("db", "5432"))
    
    seen = set()
    unique_hosts = []
    for h, p in hosts_to_try:
        if (h, p) not in seen:
            seen.add((h, p))
            unique_hosts.append((h, p))

    last_error = None
    for h, p in unique_hosts:
        try:
            pool = ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                host=h,
                port=int(p),
                database=db_name,
                user=db_user,
                password=db_pass
            )
            connection_pool = pool
            print(f"PostgreSQL ThreadedConnectionPool initialized successfully on {h}:{p}.", flush=True)
            
            # Auto-migration check
            conn = pool.getconn()
            try:
                if conn.closed == 0:
                    with conn.cursor() as cur:
                        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password TEXT;")
                        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS rank INTEGER;")
                        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS category TEXT;")
                        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS region TEXT;")
                    conn.commit()
                    print("Database schema auto-migration check completed successfully.", flush=True)
            except Exception as migration_error:
                conn.rollback()
                print(f"Database migration check failed: {migration_error}", flush=True)
            finally:
                if conn and conn.closed == 0:
                    pool.putconn(conn)
                
            return connection_pool
        except Exception as e:
            last_error = e

    connection_pool = None
    return None

def _get_healthy_pg_connection(pool):
    global connection_pool
    for _ in range(3):
        conn = None
        try:
            if getattr(pool, "closed", False):
                connection_pool = None
                pool = init_connection_pool()
                if pool is None:
                    return None
            conn = pool.getconn()
            if conn.closed != 0:
                pool.putconn(conn, close=True)
                continue
            with conn.cursor() as test_cur:
                test_cur.execute("SELECT 1;")
            return conn
        except Exception:
            if conn:
                try:
                    pool.putconn(conn, close=True)
                except Exception:
                    pass

    connection_pool = None
    pool = init_connection_pool()
    if pool:
        try:
            return pool.getconn()
        except Exception:
            pass
    return None

# Attempt module-level eager initialization
init_connection_pool()

class SQLiteDictCursorAdapter:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self.cursor.row_factory = sqlite3.Row

    def execute(self, query, vars=None):
        sqlite_query = query
        has_returning = "RETURNING id" in sqlite_query
        if has_returning:
            sqlite_query = sqlite_query.replace("RETURNING id", "")
            
        sqlite_query = sqlite_query.replace("%s", "?")
        if vars:
            self.cursor.execute(sqlite_query, vars)
        else:
            self.cursor.execute(sqlite_query)
            
        if has_returning:
            self._last_id = self.cursor.lastrowid
        return self

    def fetchone(self):
        if hasattr(self, "_last_id") and self._last_id is not None:
            lid = self._last_id
            self._last_id = None
            return {"id": lid}
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def __getattr__(self, name):
        return getattr(self.cursor, name)

def _get_sqlite_connection():
    sqlite_path = os.path.join("backend", "kcet.db")
    conn = sqlite3.connect(sqlite_path, timeout=30.0, check_same_thread=False)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
    except Exception:
        pass
    return conn

@contextmanager
def get_db_cursor():
    """
    Context manager yielding a database cursor.
    Uses PostgreSQL connection pool if available; falls back to WAL-mode SQLite (backend/kcet.db) seamlessly.
    """
    global connection_pool
    pool = init_connection_pool()
    pg_conn = None
    if pool:
        pg_conn = _get_healthy_pg_connection(pool)

    if pg_conn:
        try:
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                yield cursor
                pg_conn.commit()
        except (psycopg2.InterfaceError, psycopg2.OperationalError) as net_err:
            if pg_conn:
                try:
                    pg_conn.rollback()
                except Exception:
                    pass
                try:
                    pool.putconn(pg_conn, close=True)
                except Exception:
                    pass
                pg_conn = None
            connection_pool = None
            # Fallback to WAL SQLite on network drop
            with _get_sqlite_connection() as s_conn:
                s_cursor = SQLiteDictCursorAdapter(s_conn)
                yield s_cursor
                s_conn.commit()
        except Exception as e:
            if pg_conn:
                try:
                    pg_conn.rollback()
                except Exception:
                    pass
            raise e
        finally:
            if pg_conn and pg_conn.closed == 0:
                try:
                    pool.putconn(pg_conn)
                except Exception:
                    pass
    else:
        # Lock-free SQLite Fallback
        with _get_sqlite_connection() as s_conn:
            s_cursor = SQLiteDictCursorAdapter(s_conn)
            try:
                yield s_cursor
                s_conn.commit()
            except Exception as e:
                s_conn.rollback()
                raise e
