"""
寻味地理 — FastAPI 后端
Usage:
  cd Food
  uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
from pathlib import Path

# Fix PROJ library conflict: PostgreSQL 16 ships an old proj.db that breaks rasterio.
# Force rasterio to use its own bundled PROJ data directory.
_venv_site = Path(__file__).resolve().parents[1] / ".venv" / "Lib" / "site-packages"
_proj_data = _venv_site / "rasterio" / "proj_data"
if _proj_data.exists():
    os.environ["PROJ_LIB"] = str(_proj_data)

import logging
import asyncio
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .config import CORS_ORIGINS
from .db.connection import init_pool, close_pool
from .routers import api, tiles
from .routers.ingredient_spread import router as ingredient_router
from .routers.auth import router as auth_router
from .startup import run_startup, load_ecoregions_from_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("main")


async def _timed_async(label: str, awaitable):
    started = perf_counter()
    log.info("%s started.", label)
    result = await awaitable
    log.info("%s finished in %.1f ms.", label, (perf_counter() - started) * 1000)
    return result


def _timed_sync(label: str, fn):
    started = perf_counter()
    log.info("%s started.", label)
    result = fn()
    log.info("%s finished in %.1f ms.", label, (perf_counter() - started) * 1000)
    return result


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("═" * 60)
    log.info("  寻味地理 API  —  starting up")
    log.info("═" * 60)
    # Run blocking startup (extract TIF + load shapefiles) in thread pool
    loop = asyncio.get_running_loop()
    await _timed_async("startup data preparation", loop.run_in_executor(None, run_startup))
    _timed_sync("PostgreSQL pool init", init_pool)
    # 确保认证表存在（幂等建表，首次启动时创建 app_user）
    from backend.db.connection import get_conn
    from backend.db.auth_queries import create_user_table
    def _ensure_auth_table():
        with get_conn() as conn:
            create_user_table(conn)
    _timed_sync("auth table check", _ensure_auth_table)
    _timed_sync("ecoregions load", load_ecoregions_from_db)
    log.info("PostgreSQL connection pool initialized.")
    yield
    close_pool()
    log.info("Server shutting down.")


app = FastAPI(
    title="寻味地理 API",
    description="风味博物志后端：业务数据 + Natural Earth 底图瓦片 + WWF TEOW 生态区边界",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(api.router)
app.include_router(tiles.router)
app.include_router(ingredient_router)
app.include_router(auth_router)


@app.get("/health")
async def health():
    from .startup import vector_data
    from .config import RASTER_TIF
    return {
        "status": "ok",
        "raster_ready": RASTER_TIF.exists(),
        "vector_layers": list(vector_data.keys()),
    }
