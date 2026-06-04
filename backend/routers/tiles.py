import asyncio
import io
import logging
import sqlite3
import threading
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response

from ..config import MBTILES_PATH, RASTER_TIF, TILE_CACHE_SIZE, TILE_SIZE
from ..db.connection import get_conn
from ..startup import vector_data
from ..tile_cache import tile_cache

log = logging.getLogger("tiles")
router = APIRouter(prefix="/tiles", tags=["tiles"])

# Thread pool for blocking rasterio / rio-tiler calls
_pool = ThreadPoolExecutor(max_workers=6, thread_name_prefix="tile-worker")

# Transparent 1×1 PNG fallback (for out-of-bounds tiles)
_EMPTY_TILE: bytes | None = None
_reader_local = threading.local()


def _make_empty_tile() -> bytes:
    from PIL import Image

    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _read_mbtiles_sync(z: int, x: int, y: int) -> tuple[bytes, str] | None:
    """Try to read a tile from the pre-sliced MBTiles database.

    MBTiles uses TMS row numbering (Y=0 at the bottom), while our API uses
    XYZ (Y=0 at the top).  The conversion is ``tms_y = (1 << z) - 1 - y``.
    Returns ``(tile_data, "mbtiles")`` on success, ``None`` if the tile
    doesn't exist or the MBTiles file is missing.
    """
    if not MBTILES_PATH.exists():
        return None

    tms_y = (1 << z) - 1 - y
    conn = None
    try:
        conn = sqlite3.connect(str(MBTILES_PATH))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
            (z, x, tms_y),
        ).fetchone()
        if row is not None:
            return row[0], "mbtiles"
    except Exception:
        # If anything goes wrong with MBTiles, silently fall back to COG.
        log.debug("MBTiles read failed %s/%s/%s", z, x, y, exc_info=True)
    finally:
        if conn is not None:
            conn.close()
    return None


def _get_reader():
    reader = getattr(_reader_local, "reader", None)
    if reader is None:
        from rio_tiler.io import Reader

        reader = Reader(str(RASTER_TIF))
        _reader_local.reader = reader
    return reader


def _render_tile_sync(z: int, x: int, y: int) -> tuple[bytes, str, float]:
    """
    Blocking: MBTiles → cache → COG+rio-tiler → store in cache.
    Runs inside a thread pool so it never blocks the event loop.
    """
    global _EMPTY_TILE

    cached = tile_cache.get(z, x, y)
    if cached is not None:
        return cached, "hit", 0.0

    started = perf_counter()

    # ── 1. Try pre-sliced MBTiles (fast path) ──────────────────────────
    mbtiles_result = _read_mbtiles_sync(z, x, y)
    if mbtiles_result is not None:
        content, source = mbtiles_result
        tile_cache.set(z, x, y, content)
        return content, source, perf_counter() - started

    # ── 2. Fall back to COG + rio-tiler (slow path) ──────────────────
    try:
        from rio_tiler.errors import TileOutsideBounds

        cog = _get_reader()
        img = cog.tile(x, y, z, tilesize=TILE_SIZE)
        # HYP is RGB (3-band), render as PNG
        content = img.render(img_format="PNG")

    except TileOutsideBounds:
        if _EMPTY_TILE is None:
            _EMPTY_TILE = _make_empty_tile()
        return _EMPTY_TILE, "outside", perf_counter() - started
    except Exception as exc:
        log.warning(f"Tile render failed {z}/{x}/{y}: {exc}")
        if _EMPTY_TILE is None:
            _EMPTY_TILE = _make_empty_tile()
        return _EMPTY_TILE, "error", perf_counter() - started

    tile_cache.set(z, x, y, content)
    return content, "cog-miss", perf_counter() - started


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/raster/{z}/{x}/{y}.png", response_class=Response)
async def raster_tile(z: int, x: int, y: int):
    """Serve XYZ raster tiles from the Natural Earth HYP GeoTIFF."""
    if not RASTER_TIF.exists():
        raise HTTPException(503, "Raster not yet extracted — server is still starting up.")
    if not (0 <= z <= 10):
        raise HTTPException(400, "Zoom level must be 0–10.")

    started = perf_counter()
    loop = asyncio.get_running_loop()
    content, cache_status, render_seconds = await loop.run_in_executor(_pool, _render_tile_sync, z, x, y)
    total_seconds = perf_counter() - started
    if cache_status != "hit" or total_seconds >= 0.25:
        log.info(
            "raster tile %s/%s/%s %s render=%.1fms total=%.1fms bytes=%s cache=%s/%s hit_rate=%s",
            z, x, y, cache_status, render_seconds * 1000, total_seconds * 1000,
            len(content), tile_cache.size, TILE_CACHE_SIZE, f"{tile_cache.hit_rate:.2%}",
        )

    return Response(
        content,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Cache": cache_status,
            "X-Cache-Size": str(tile_cache.size),
            "X-Cache-HitRate": f"{tile_cache.hit_rate:.2%}",
        },
    )


@router.get("/mvt/{z}/{x}/{y}.pbf", response_class=Response)
async def mvt_tile(z: int, x: int, y: int):
    """Serve L1 ecoregion boundaries as MVT (Mapbox Vector Tile)."""
    sql = """
        SELECT ST_AsMVT(tile, 'ecoregions', 4096, 'geom')
        FROM (
            SELECT eco_name, eco_name_cn, biome_cn, realm, eco_code,
                   ST_AsMVTGeom(
                       ST_Simplify(boundary, 0.02),
                       ST_TileEnvelope(%s, %s, %s),
                       4096, 256, true
                   ) AS geom
            FROM eco_geo_unit
            WHERE boundary IS NOT NULL
              AND ST_Intersects(boundary, ST_TileEnvelope(%s, %s, %s))
            LIMIT 200
        ) AS tile
        WHERE geom IS NOT NULL
    """
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (z, x, y, z, x, y))
                row = cur.fetchone()
        if row and row[0]:
            return Response(row[0], media_type="application/vnd.mapbox-vector-tile",
                            headers={"Cache-Control": "public, max-age=3600"})
        return Response(b"", media_type="application/vnd.mapbox-vector-tile")
    except Exception as exc:
        log.warning(f"MVT tile failed {z}/{x}/{y}: {exc}")
        return Response(b"", media_type="application/vnd.mapbox-vector-tile")


@router.get("/vector/{layer}")
async def vector_layer(layer: str):
    """Serve a vector layer as GeoJSON FeatureCollection.
    Available layers: coastline, rivers, land, ecoregions
    """
    if layer not in vector_data:
        available = list(vector_data.keys())
        raise HTTPException(
            404,
            f"Layer '{layer}' not found. "
            f"{'Available: ' + str(available) if available else 'No layers loaded yet.'}"
        )
    return JSONResponse(
        content=vector_data[layer],
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/vector")
async def list_layers():
    return {
        "layers": {
            name: len(gc.get("features", []))
            for name, gc in vector_data.items()
        }
    }


@router.get("/status")
async def tiles_status():
    return {
        "raster_ready": RASTER_TIF.exists(),
        "raster_source": "mbtiles" if MBTILES_PATH.exists() else "cog",
        "mbtiles": {
            "path": str(MBTILES_PATH),
            "available": MBTILES_PATH.exists(),
            "size_mb": round(MBTILES_PATH.stat().st_size / (1024 * 1024), 1) if MBTILES_PATH.exists() else None,
        },
        "vector_layers": list(vector_data.keys()),
        "tile_cache": {
            "size": tile_cache.size,
            "max": TILE_CACHE_SIZE,
            "hit_rate": f"{tile_cache.hit_rate:.2%}",
            "tile_size": TILE_SIZE,
        },
    }
