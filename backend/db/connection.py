"""PostgreSQL 连接池。

模块级单例 ThreadedConnectionPool，FastAPI 多线程 worker 安全。
启动时由 main.py 的 lifespan 调用 init_pool()，关闭时调用 close_pool()。
"""
from __future__ import annotations
import os
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from psycopg2 import pool as _pg_pool
from dotenv import load_dotenv


_pool: _pg_pool.ThreadedConnectionPool | None = None


def init_pool(min_conn: int = 1, max_conn: int = 4) -> None:
    global _pool
    if _pool is not None:
        return
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL 未在 .env 中设置")
    _pool = _pg_pool.ThreadedConnectionPool(min_conn, max_conn, dsn=url)


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def get_conn():
    if _pool is None:
        init_pool()
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)
