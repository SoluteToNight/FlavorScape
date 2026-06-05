"""
FlavorScape FastAPI backend.

Dev command:
  .venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

# PostgreSQL can ship an old proj.db that conflicts with rasterio. Prefer the
# rasterio-bundled PROJ data when it exists in the local virtual environment.
_venv_site = Path(__file__).resolve().parents[1] / ".venv" / "Lib" / "site-packages"
_proj_data = _venv_site / "rasterio" / "proj_data"
if _proj_data.exists():
    os.environ["PROJ_LIB"] = str(_proj_data)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from .config import CORS_ORIGINS
from .db.connection import close_pool, init_pool
from .routers import api, assets, tiles
from .routers.auth import router as auth_router
from .routers.ingredient_spread import router as ingredient_router
from .routers.studio import router as studio_router
from .startup import load_ecoregions_from_db, run_startup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s - %(message)s",
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


def _ensure_user_tables():
    from backend.db.auth_queries import create_user_table
    from backend.db.connection import get_conn
    from backend.db.studio_queries import create_studio_project_table

    with get_conn() as conn:
        create_user_table(conn)
        create_studio_project_table(conn)
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("=" * 60)
    log.info("FlavorScape API starting up")
    log.info("=" * 60)

    loop = asyncio.get_running_loop()
    await _timed_async("startup data preparation", loop.run_in_executor(None, run_startup))
    _timed_sync("PostgreSQL pool init", init_pool)
    _timed_sync("user tables check", _ensure_user_tables)
    _timed_sync("ecoregions load", load_ecoregions_from_db)

    log.info("PostgreSQL connection pool initialized.")
    yield
    close_pool()
    log.info("Server shutting down.")


app = FastAPI(
    title="FlavorScape API",
    description="FlavorScape backend: business data, raster tiles, vector layers, auth, and Studio APIs.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api.router)
app.include_router(assets.router)
app.include_router(tiles.router)
app.include_router(ingredient_router)
app.include_router(auth_router)
app.include_router(studio_router)

_static_dir = Path(__file__).resolve().parent / "static" / "uploads"
if _static_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(_static_dir)), name="uploads")


@app.get("/health")
async def health():
    from .config import RASTER_TIF
    from .startup import vector_data

    return {
        "status": "ok",
        "raster_ready": RASTER_TIF.exists(),
        "vector_layers": list(vector_data.keys()),
    }
