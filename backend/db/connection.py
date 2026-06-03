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
from psycopg2.extras import RealDictCursor
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
    """上下文管理器，用于同步脚本和 startup 中的手动查询。"""
    if _pool is None:
        init_pool()
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)


async def get_db():
    """FastAPI 依赖：从连接池获取连接，请求结束后自动归还。

    连接设置为 autocommit 模式，每个 SQL 语句自动提交。
    用法:
        @app.get("/example")
        async def example(db=Depends(get_db)):
            with db.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT ...")
                return cur.fetchall()
    """
    if _pool is None:
        init_pool()
    conn = _pool.getconn()
    conn.autocommit = True
    try:
        yield conn
    finally:
        _pool.putconn(conn)
