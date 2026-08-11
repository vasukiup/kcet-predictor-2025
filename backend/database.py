# =======================================================
# Copyright (c) 2026 Vasuki Upadhya. All rights reserved.
# Author: Vasuki Upadhya (vasuki.upadhya@gmail.com)
# Application: KEA Seat Matrix & Prediction Portal
# =======================================================
"""
Database Connection Utility for PostgreSQL pooling.
"""
import os
from contextlib import contextmanager

# Inline load dotenv variables before connection pool initialization
def _load_dotenv():
    env_path = os.path.join("backend", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
_load_dotenv()
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

# Connection configuration
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "kcet")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")

# Initialize connection pool
try:
    connection_pool = ThreadedConnectionPool(
        minconn=2,
        maxconn=20,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("PostgreSQL ThreadedConnectionPool initialized successfully.")
    
    # Run dynamic schema alterations to support credentials and profiles
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password TEXT;")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS rank INTEGER;")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS category TEXT;")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS region TEXT;")
        conn.commit()
        print("Database schema auto-migration check completed successfully.")
    except Exception as migration_error:
        conn.rollback()
        print(f"Database migration check failed: {migration_error}")
    finally:
        connection_pool.putconn(conn)
except Exception as e:
    print(f"Error initializing PostgreSQL Connection Pool: {e}")
    connection_pool = None

@contextmanager
def get_db_cursor():
    """
    Context manager to yield a psycopg2 cursor from the connection pool.
    Auto-commits transactions or rolls back on exception.
    """
    if connection_pool is None:
        raise RuntimeError("PostgreSQL Connection Pool is not initialized.")
    
    conn = connection_pool.getconn()
    try:
        # Use RealDictCursor so queries return dictionary-like row objects
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            yield cursor
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        connection_pool.putconn(conn)
