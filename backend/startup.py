"""
启动任务：从 data/extracted/ 读取已解压文件，加载矢量图层到内存。
若文件尚未解压，则自动从 ZIP 解压（首次运行时触发）。
"""

import json
import logging
import os
import zipfile
from pathlib import Path
from typing import Any

from .config import (
    DATA_DIR, EXTRACTED_DIR,
    RASTER_ZIP, RASTER_ZIP_ENTRY, RASTER_TIF, RASTER_COG,
    PHYSICAL_ZIP, TEOW_ZIP, TEOW_SHP, TEOW_WGS84,
)

log = logging.getLogger("startup")

vector_data: dict[str, Any] = {}

BIOME_NAMES = {
    1: "热带湿润阔叶林", 2: "热带干旱阔叶林", 3: "热带和亚热带针叶林",
    4: "温带阔叶混交林", 5: "温带针叶林",   6: "北方针叶林（泰加林）",
    7: "热带稀树草原",   8: "温带草原与灌丛", 9: "洪泛草原与稀树草原",
    10: "山地草甸与灌丛", 11: "苔原",        12: "地中海型森林与灌丛",
    13: "沙漠与干旱灌丛", 14: "红树林",
    98: "岩石与冰川",    99: "水体",
}

SHP_EXTS = [".shp", ".dbf", ".shx", ".prj", ".cpg"]


# ─────────────────────────────────────────────────────────────────────────────
# 解压辅助
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_raster() -> None:
    if RASTER_TIF.exists():
        log.info(f"raster ready: {RASTER_TIF} ({RASTER_TIF.stat().st_size / 1e6:.0f} MB)")
        return
    if not RASTER_ZIP.exists():
        log.error(f"raster ZIP not found: {RASTER_ZIP}")
        return
    # COG not found — extract strip-based TIF from ZIP as fallback, then warn
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    strip_tif = EXTRACTED_DIR / RASTER_ZIP_ENTRY
    if not strip_tif.exists():
        log.info(f"Extracting raster from ZIP ({RASTER_ZIP.stat().st_size / 1e6:.0f} MB)…")
        with zipfile.ZipFile(RASTER_ZIP) as zf:
            total = zf.getinfo(RASTER_ZIP_ENTRY).file_size
            with zf.open(RASTER_ZIP_ENTRY) as src, open(strip_tif, "wb") as dst:
                written, chunk = 0, 8 * 1024 * 1024
                while buf := src.read(chunk):
                    dst.write(buf)
                    written += len(buf)
                    if int(written / total * 10) > int((written - len(buf)) / total * 10):
                        log.info(f"  {written / total * 100:.0f}%")
        log.info("Raster extraction complete.")
    if not RASTER_TIF.exists():
        log.warning(f"COG raster ({RASTER_COG.name}) not found — generate it with:")
        log.warning(f"  gdal_translate {strip_tif} {RASTER_COG} -of COG -co COMPRESS=DEFLATE")


def _ensure_physical_shp(name: str) -> Path | None:
    """Return path to extracted SHP, extracting from ZIP if necessary."""
    shp = EXTRACTED_DIR / (name + ".shp")
    if shp.exists():
        return shp
    if not PHYSICAL_ZIP.exists():
        log.warning(f"Physical ZIP not found: {PHYSICAL_ZIP}")
        return None
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    log.info(f"Extracting {name}.shp from ZIP…")
    with zipfile.ZipFile(PHYSICAL_ZIP) as zf:
        znames = set(zf.namelist())
        for ext in SHP_EXTS:
            fname = name + ext
            if fname in znames:
                zf.extract(fname, EXTRACTED_DIR)
    return shp if shp.exists() else None


def _ensure_teow_shp() -> Path | None:
    shp = EXTRACTED_DIR / "wwf_terr_ecos.shp"
    if shp.exists():
        return shp
    if not TEOW_ZIP.exists():
        log.warning(f"TEOW ZIP not found: {TEOW_ZIP}")
        return None
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    log.info("Extracting wwf_terr_ecos.shp from ZIP…")
    with zipfile.ZipFile(TEOW_ZIP) as zf:
        base = TEOW_SHP.replace(".shp", "")
        for ext in SHP_EXTS:
            fname = base + ext
            if fname in zf.namelist():
                data = zf.read(fname)
                (EXTRACTED_DIR / ("wwf_terr_ecos" + ext)).write_bytes(data)
    return shp if shp.exists() else None


# ─────────────────────────────────────────────────────────────────────────────
# 矢量加载
# ─────────────────────────────────────────────────────────────────────────────

def _load_shp(shp_path: Path, tolerance: float, keep_props: list[str] | None = None) -> dict:
    """Load shapefile (must already be in EPSG:4326), simplify, return GeoJSON."""
    import fiona
    from shapely.geometry import mapping, shape

    features = []
    with fiona.open(str(shp_path)) as src:
        for feat in src:
            try:
                geom = shape(feat["geometry"])
                if not geom.is_valid:
                    geom = geom.buffer(0)
                simplified = geom.simplify(tolerance, preserve_topology=True)
                if simplified.is_empty:
                    continue
                props = {}
                if keep_props:
                    raw = feat.get("properties") or {}
                    for k in keep_props:
                        props[k] = raw.get(k)
                features.append({
                    "type": "Feature",
                    "geometry": mapping(simplified),
                    "properties": props,
                })
            except Exception as exc:
                log.debug(f"feature skipped: {exc}")

    return {"type": "FeatureCollection", "features": features}


def load_vector_layers() -> None:
    global vector_data

    # Physical layers
    phys = [
        ("ne_10m_coastline",              "coastline",  0.05, None),
        ("ne_10m_rivers_lake_centerlines", "rivers",    0.08, None),
        ("ne_10m_land",                    "land",      0.08, None),
    ]
    for name, key, tol, props in phys:
        shp = _ensure_physical_shp(name)
        if not shp:
            continue
        log.info(f"Loading [{key}] from {shp.name} (tol={tol}°)…")
        gc = _load_shp(shp, tol, props)
        vector_data[key] = gc
        log.info(f"  {key}: {len(gc['features'])} features")

    # TEOW ecoregions (L1) — loaded from PostgreSQL after init_pool()
    # See load_ecoregions_from_db() called in main.py lifespan


# ─────────────────────────────────────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────────────────────────────────────

def run_startup() -> None:
    _ensure_raster()
    load_vector_layers()
    log.info("✓ Startup complete (ecoregions deferred to DB).")


def load_ecoregions_from_db() -> None:
    """从 PostgreSQL 加载生态区边界到内存 vector_data["ecoregions"]。

    ST_Simplify(tolerance=0.08°) 预简化几何，减少内存和传输体积。
    必须在 init_pool() 之后调用。
    """
    import json as _json
    from backend.db.connection import get_conn

    BIOME_NAMES_REVERSE = {v: k for k, v in BIOME_NAMES.items()}

    sql = """
        SELECT eco_name, eco_name_cn, eco_code, realm, biome, biome_cn,
               ST_AsGeoJSON(ST_Simplify(boundary, 0.08)) AS geojson
        FROM eco_geo_unit
        WHERE boundary IS NOT NULL
    """
    features = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            for eco_name, eco_name_cn, eco_code, realm, biome, biome_cn, geojson_str in cur:
                if not geojson_str:
                    continue
                gj = _json.loads(geojson_str)
                features.append({
                    "type": "Feature",
                    "geometry": gj,
                    "properties": {
                        "eco_name": eco_name,
                        "eco_name_cn": eco_name_cn or "",
                        "eco_code": eco_code or "",
                        "realm": realm or "",
                        "biome": biome or "",
                        "biome_cn": biome_cn or "",
                    },
                })
    vector_data["ecoregions"] = {
        "type": "FeatureCollection",
        "features": features,
    }
    log.info(f"ecoregions loaded from DB: {len(features)} features")
