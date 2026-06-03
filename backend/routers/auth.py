"""认证路由：注册 / 登录 / 当前用户。

前缀 /api/auth，所有端点返回统一格式 {ok, data|error}。
"""
from __future__ import annotations
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from ..db.connection import get_db
from ..db.auth_queries import create_user_table, create_user, get_user_by_username
from ..auth_deps import get_current_user

log = logging.getLogger("auth")

try:
    import bcrypt
    from jose import jwt
except ImportError:
    bcrypt = None  # type: ignore
    jwt = None  # type: ignore

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _ensure_table(conn) -> None:
    """幂等建表（首次请求触发）。"""
    create_user_table(conn)


# ── Pydantic models ──────────────────────────────────────────────────────────────

class AuthRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=32, description="用户名 2-32 字符")
    password: str = Field(..., min_length=4, max_length=128, description="密码 ≥4 字符")


# ── Helpers ──────────────────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """bcrypt 哈希，返回字符串。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    """验证密码与哈希是否匹配。"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def _make_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _user_response(user: dict, token: str) -> dict:
    return {"ok": True, "data": {"token": token, "user": user}}


# ── Endpoints ────────────────────────────────────────────────────────────────────

@router.post("/register")
async def register(body: AuthRequest, conn=Depends(get_db)):
    """注册新用户。用户名唯一，密码 bcrypt 哈希。"""
    _ensure_table(conn)

    existing = get_user_by_username(conn, body.username)
    if existing:
        return {"ok": False, "error": "用户名已被注册"}

    hashed = _hash_password(body.password)
    user = create_user(conn, body.username, hashed)
    if user is None:
        return {"ok": False, "error": "注册失败，请稍后重试"}

    token = _make_token(user["id"])
    log.info("新用户注册: %s (id=%d)", body.username, user["id"])
    return _user_response(user, token)


@router.post("/login")
async def login(body: AuthRequest, conn=Depends(get_db)):
    """用户名 + 密码登录，返回 JWT token。"""
    _ensure_table(conn)

    row = get_user_by_username(conn, body.username)
    if row is None:
        return {"ok": False, "error": "用户名或密码错误"}

    if not _verify_password(body.password, row["password"]):
        return {"ok": False, "error": "用户名或密码错误"}

    user = {"id": row["id"], "username": row["username"], "created_at": str(row["created_at"])}
    token = _make_token(user["id"])
    log.info("用户登录: %s", body.username)
    return _user_response(user, token)


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    """返回当前登录用户信息（需 Bearer token）。"""
    return {"ok": True, "data": {"user": user}}
