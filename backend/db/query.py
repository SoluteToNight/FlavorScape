"""业务数据查询层。

输出对象保持与原 app_data.py 中 FLAVORS/ROUTES/CHAPTERS 同结构，使前端无需改动。
核心数据来自 DB；UI 展示元数据（city/color/region/primary/vals/dish_family/id）
从 app_data.py 注入合并 —— 这部分是纯展示属性，不属于 ER 图数据建模范围。
"""
from __future__ import annotations
import json

from backend.db.connection import get_conn
from backend.data.app_data import FLAVORS, ROUTES


# UI 元数据反查索引（dish 名 → 原 FLAVOR 对象 / 路线名 → 原 ROUTE 对象）
_UI_BY_DISH = {f["dish"]: f for f in FLAVORS}
_UI_BY_ROUTE_NAME = {r["name"]: r for r in ROUTES}
_ROUTE_NAMES_IN_ORDER = [r["name"] for r in ROUTES]


def fetch_flavors() -> list[dict]:
    """组装与原 FLAVORS 同结构的列表。"""
    sql = """
        SELECT g.dish_name,
               g.category,
               e.eco_name,
               ST_X(g.coordinates) AS lon,
               ST_Y(g.coordinates) AS lat,
               g.genome_vector,
               (
                   SELECT array_agg(i.name ORDER BY i.name)
                   FROM recipe_link rl
                   JOIN ingredient i ON i.ingredient_id = rl.ingredient_id
                   WHERE rl.genotype_id = g.genotype_id
               ) AS ingredients
        FROM flavor_genotype g
        JOIN eco_geo_unit e ON e.eco_name = g.eco_name
        ORDER BY g.genotype_id
    """
    results = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d.name for d in cur.description]
            for row in cur.fetchall():
                db_obj = dict(zip(cols, row))
                ui = _UI_BY_DISH.get(db_obj["dish_name"], {})
                results.append({
                    "id": ui.get("id"),
                    "city": ui.get("city"),
                    "dish": db_obj["dish_name"],
                    "dish_family": ui.get("dish_family"),
                    "region": ui.get("region"),
                    "eco": db_obj["eco_name"],
                    "scores": ui.get("scores"),
                    "primary": ui.get("primary"),
                    "vals": ui.get("vals"),
                    "color": ui.get("color"),
                    "cat": db_obj["category"],
                    "ingredients": list(db_obj["ingredients"] or []),
                    "coordinates": [float(db_obj["lon"]), float(db_obj["lat"])],
                    "genome_vector": db_obj["genome_vector"],
                })
    return results


def fetch_routes() -> list[dict]:
    """组装与原 ROUTES 同结构的列表。

    路径几何来自 DB LineString，UI 元数据（name/color/type）按 event_id 顺序
    与 app_data.ROUTES 顺序一致（seed 时按 enumerate 顺序生成 EVT 编号）。
    """
    sql = """
        SELECT d.event_id, ST_AsGeoJSON(d.route_geom) AS geojson
        FROM dispersal_event d
        ORDER BY d.event_id
    """
    results = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    for idx, (event_id, geojson_str) in enumerate(rows):
        gj = json.loads(geojson_str) if geojson_str else {}
        path = gj.get("coordinates", [])
        if idx < len(_ROUTE_NAMES_IN_ORDER):
            ui = _UI_BY_ROUTE_NAME[_ROUTE_NAMES_IN_ORDER[idx]]
        else:
            ui = {}
        results.append({
            "name": ui.get("name", event_id.strip()),
            "color": ui.get("color", "#888"),
            "type": ui.get("type", "land"),
            "path": path,
        })
    return results


def fetch_chapters() -> list[dict]:
    sql = """
        SELECT chapter_id, title, date_label, body, cite, source, route_name
        FROM chapter
        ORDER BY chapter_id
    """
    results = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            for cid, title, dt, body, cite, source, route_name in cur.fetchall():
                results.append({
                    "id": cid,
                    "title": title,
                    "date": dt,
                    "body": body,
                    "cite": cite,
                    "source": source,
                    "routeName": route_name,
                })
    return results


def search(q: str) -> list[dict]:
    """全文搜索 flavors + ecoregions + routes。

    PG tsvector 优先；查询失败或短于 2 字符时回退 ILIKE substring。
    """
    import logging
    log = logging.getLogger("search")
    q = q.strip()
    if not q:
        return []

    results = []
    matched_dishes = set()
    matched_ecos = set()

    # PG tsvector search (only for queries >= 2 chars)
    if len(q) >= 2:
        with get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """SELECT DISTINCT g.dish_name
                           FROM flavor_genotype g
                           WHERE to_tsvector('simple', COALESCE(g.dish_name,'') || ' ' || COALESCE(g.category,''))
                              @@ plainto_tsquery('simple', %s)
                           LIMIT 8""",
                        (q,),
                    )
                    matched_dishes = {row[0] for row in cur.fetchall()}
                except Exception as exc:
                    log.debug("tsvector dish search failed: %s", exc)

                try:
                    cur.execute(
                        """SELECT eco_name FROM eco_geo_unit
                           WHERE to_tsvector('simple',
                                 COALESCE(eco_name,'') || ' ' ||
                                 COALESCE(eco_name_cn,'') || ' ' ||
                                 COALESCE(biome_cn,''))
                              @@ plainto_tsquery('simple', %s)
                           LIMIT 16""",
                        (q,),
                    )
                    matched_ecos = {row[0] for row in cur.fetchall()}
                except Exception as exc:
                    log.debug("tsvector eco search failed: %s", exc)

    # Build results using already-fetched data + UI metadata merge
    flavors = fetch_flavors()
    routes = fetch_routes()

    for f in flavors:
        # PG match
        hit_dish = f["dish"] in matched_dishes
        hit_eco  = f["eco"] in matched_ecos
        # Substring fallback (always active for single-char and UI fields)
        haystack = [
            f.get("city") or "",
            f.get("region") or "",
            f.get("dish") or "",
            f.get("dish_family") or "",
        ]
        primary_hit = any(q in p for p in (f.get("primary") or []))
        if hit_dish or hit_eco or any(q in field for field in haystack) or primary_hit:
            results.append({
                "type": "node",
                "label": f.get("dish") or f.get("city"),
                "sub": f"{f.get('city')} · {f.get('region')}",
                "color": f.get("color"),
                "data": f,
            })

    for r in routes:
        if q in r["name"]:
            results.append({
                "type": "route",
                "label": r["name"],
                "sub": "海路传播" if r.get("type") == "sea" else "陆路传播",
                "color": r.get("color"),
                "data": r,
            })

    return results[:8]
