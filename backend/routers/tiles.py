import asyncio
import io
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response

from ..config import RASTER_TIF, TILE_CACHE_SIZE
from ..db.connection import get_conn
from ..startup import vector_data
from ..tile_cache import tile_cache

log = logging.getLogger("tiles")
router = APIRouter(prefix="/tiles", tags=["tiles"])

# Thread pool for blocking rasterio / rio-tiler calls
_pool = ThreadPoolExecutor(max_workers=6, thread_name_prefix="tile-worker")

# Match MapLibre's native tile grid to reduce the number of raster requests.
RASTER_TILE_SIZE = 512

# Transparent 1×1 PNG fallback (for out-of-bounds tiles)
_EMPTY_TILE: bytes | None = None


def _make_empty_tile() -> bytes:
    from PIL import Image

    img = Image.new("RGBA", (RASTER_TILE_SIZE, RASTER_TILE_SIZE), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _render_tile_sync(z: int, x: int, y: int) -> bytes:
    """
    Blocking: fetch from cache → render with rio-tiler → store in cache.
    Runs inside a thread pool so it never blocks the event loop.
    """
    global _EMPTY_TILE
    tiles_per_axis = 1 << z

    if y < 0 or y >= tiles_per_axis:
        if _EMPTY_TILE is None:
            _EMPTY_TILE = _make_empty_tile()
        return _EMPTY_TILE

    x = x % tiles_per_axis

    cached = tile_cache.get(z, x, y)
    if cached is not None:
        return cached

    try:
        from rio_tiler.errors import TileOutsideBounds
        from rio_tiler.io import Reader  # rio-tiler ≥ 5.0 (COGReader alias)

        with Reader(str(RASTER_TIF)) as cog:
            img = cog.tile(x, y, z, tilesize=RASTER_TILE_SIZE)
            # HYP is RGB (3-band), render as PNG
            content = img.render(img_format="PNG")

    except TileOutsideBounds:
        if _EMPTY_TILE is None:
            _EMPTY_TILE = _make_empty_tile()
        return _EMPTY_TILE
    except Exception as exc:
        log.warning(f"Tile render failed {z}/{x}/{y}: {exc}")
        if _EMPTY_TILE is None:
            _EMPTY_TILE = _make_empty_tile()
        return _EMPTY_TILE

    tile_cache.set(z, x, y, content)
    return content


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

    loop = asyncio.get_running_loop()
    content = await loop.run_in_executor(_pool, _render_tile_sync, z, x, y)

    return Response(
        content,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Tile-Size": str(RASTER_TILE_SIZE),
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
        "vector_layers": list(vector_data.keys()),
        "tile_cache": {
            "size": tile_cache.size,
            "max": TILE_CACHE_SIZE,
            "hit_rate": f"{tile_cache.hit_rate:.2%}",
        },
    }
