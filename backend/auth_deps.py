"""FastAPI 认证依赖注入。

提供 get_current_user 依赖：解析 Bearer token → 解码 JWT → 查询数据库。

注意：python-jose 和 bcrypt 的可用性在 backend/startup.py 的
_check_dependencies() 中提前验证，服务器不会在没有认证依赖的情况下启动。
"""
from __future__ import annotations
import logging
from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError

from .config import JWT_SECRET, JWT_ALGORITHM
from .db.connection import get_db
from .db.auth_queries import get_user_by_id

log = logging.getLogger("auth")


async def get_current_user(
    authorization: str | None = Header(None, description="Bearer <JWT token>"),
    conn=Depends(get_db),
) -> dict:
    """从 Authorization 头解析 JWT 并返回当前用户。

    Header(…) 显式传参（含 description）与 Depends(get_db) 的紧凑写法并存，
    两者均为 FastAPI 惯用风格：Depends 仅需传函数引用时无需构造函数参数，
    Header 需传 (default, ...) 参数时必须显式调用。

    用法:
        @app.get("/api/auth/me")
        async def me(user: dict = Depends(get_current_user)):
            return {"ok": True, "data": user}
    """
    # ── 解析 Bearer token ──
    if not authorization:
        raise HTTPException(401, "缺少 Bearer token")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, "缺少 Bearer token")

    # ── 解码 JWT ──
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(401, "token 无效或已过期")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(401, "token 缺少 subject")

    # ── 查数据库 ──
    user = get_user_by_id(conn, int(user_id))
    if user is None:
        raise HTTPException(401, "用户不存在")

    return user
