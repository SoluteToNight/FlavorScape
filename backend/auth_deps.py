"""FastAPI 认证依赖注入。

提供 get_current_user 依赖：解析 Bearer token → 解码 JWT → 查询数据库。
"""
from __future__ import annotations
import logging
from fastapi import Header, HTTPException, Depends

from .config import JWT_SECRET, JWT_ALGORITHM
from .db.connection import get_db
from .db.auth_queries import get_user_by_id

log = logging.getLogger("auth")

try:
    from jose import jwt, JWTError
except ImportError:
    jwt = None  # type: ignore
    JWTError = Exception


async def get_current_user(
    authorization: str = Header(..., description="Bearer <JWT token>"),
    conn=Depends(get_db),
) -> dict:
    """从 Authorization 头解析 JWT 并返回当前用户。

    用法:
        @app.get("/api/auth/me")
        async def me(user: dict = Depends(get_current_user)):
            return {"ok": True, "data": user}
    """
    if jwt is None:
        raise HTTPException(500, "JWT 库未安装（python-jose）")

    # ── 解析 Bearer token ──
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
