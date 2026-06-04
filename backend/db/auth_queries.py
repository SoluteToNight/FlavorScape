"""用户认证相关数据库查询。

所有函数接收 psycopg2 connection + cursor 参数，
由调用方通过 get_conn() 或 get_db() 提供连接。
"""
from __future__ import annotations
import logging
from psycopg2.extras import RealDictCursor

log = logging.getLogger("auth")


def create_user_table(conn) -> None:
    """首次运行时自动建表（IF NOT EXISTS，幂等安全）。"""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_user (
                id          SERIAL PRIMARY KEY,
                username    VARCHAR(64)  NOT NULL UNIQUE,
                password    VARCHAR(256) NOT NULL,
                created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
            )
        """)
    log.info("app_user 表已就绪")


def create_user(conn, username: str, hashed_password: str) -> dict | None:
    """创建新用户，返回用户 dict（不含密码）。用户名重复返回 None。

    调用方提供的 conn 应为 autocommit 模式，INSERT 自动提交。
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(
                "INSERT INTO app_user (username, password) VALUES (%s, %s) RETURNING id, username, created_at",
                (username, hashed_password),
            )
            return dict(cur.fetchone())
        except Exception as e:
            # 唯一约束冲突 → None；其他错误记录日志
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                return None
            log.error("create_user 失败: %s", e)
            raise


def get_user_by_username(conn, username: str) -> dict | None:
    """按用户名查询，返回完整行（含 password hash）。"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, username, password, created_at FROM app_user WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_user_by_id(conn, user_id: int) -> dict | None:
    """按 ID 查询，返回用户 dict（不含密码）。"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, username, created_at FROM app_user WHERE id = %s",
            (user_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None
