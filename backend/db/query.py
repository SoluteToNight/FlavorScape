"""业务数据查询层。

运行时数据全部来自 PostgreSQL/PostGIS。
输出对象保持前端既有 shape，避免前端组件在迁移期间联动改动。
"""
from __future__ import annotations
import json
from urllib.parse import quote

from backend.db.connection import get_conn
from backend.data.app_data import FLAVOR_MEDIA

SCORE_KEYS = ["spicy", "numbing", "salty", "sour", "sweet", "umami"]
PRIMARY_CN = {
    "spicy": "辣",
    "numbing": "麻",
    "salty": "咸",
    "sour": "酸",
    "sweet": "甜",
    "umami": "鲜",
}


def _scores_from_genome_vector(genome_vector) -> list[float]:
    genome = genome_vector or {}
    return [float(genome.get(key, 0.0) or 0.0) for key in SCORE_KEYS]


def _build_flavor_description(db_obj: dict, scores: list[float]) -> str:
    ingredients = list(db_obj.get("ingredients") or [])
    lead = "、".join(ingredients[:3]) if ingredients else "地方食材"
    score_pairs = list(zip(SCORE_KEYS, scores))
    score_pairs.sort(key=lambda item: item[1], reverse=True)
    top_labels = [PRIMARY_CN[key] for key, value in score_pairs[:2] if value > 0]
    top_text = " / ".join(top_labels) if top_labels else "复合"
    region = db_obj.get("region_label") or "地方风土"
    eco = db_obj.get("eco_label") or "自然生态"
    return f"{region}中的{eco}气候塑造出偏{top_text}的味型，常以{lead}构成核心风味。"


def _build_flavor_image(db_obj: dict) -> str:
    color = db_obj.get("color_hex") or "#E8A917"
    ingredients = list(db_obj.get("ingredients") or [])
    garnish_count = max(3, min(ingredients and len(ingredients) + 1 or 3, 5))
    garnish_svg = []
    garnish_positions = [(84, 76), (118, 90), (147, 74), (103, 99), (135, 103)]
    for idx in range(garnish_count):
        x, y = garnish_positions[idx]
        radius = 8 + (idx % 3) * 3
        opacity = 0.54 + idx * 0.08
        garnish_svg.append(
            f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}" opacity="{opacity:.2f}"/>'
        )
    garnish_markup = "".join(garnish_svg)
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="240" height="160" viewBox="0 0 240 160">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{color}" stop-opacity="0.92"/>
          <stop offset="100%" stop-color="#fff4e8" stop-opacity="1"/>
        </linearGradient>
        <radialGradient id="plate" cx="50%" cy="38%" r="62%">
          <stop offset="0%" stop-color="#fffdf9"/>
          <stop offset="72%" stop-color="#f1e6d7"/>
          <stop offset="100%" stop-color="#dbc8b0"/>
        </radialGradient>
      </defs>
      <rect width="240" height="160" rx="28" fill="url(#bg)"/>
      <circle cx="193" cy="34" r="14" fill="rgba(255,255,255,0.28)"/>
      <circle cx="51" cy="42" r="18" fill="rgba(255,255,255,0.22)"/>
      <ellipse cx="120" cy="88" rx="72" ry="38" fill="url(#plate)" opacity="0.95"/>
      <ellipse cx="120" cy="88" rx="56" ry="26" fill="{color}" opacity="0.28"/>
      {garnish_markup}
      <path d="M50 123c28-14 112-14 140 0" stroke="rgba(111,82,61,0.22)" stroke-width="4" stroke-linecap="round"/>
    </svg>
    """.strip()
    return f"data:image/svg+xml;charset=UTF-8,{quote(svg)}"


def fetch_flavors() -> list[dict]:
    """返回风味节点，shape 与原 FLAVORS 兼容。"""
    sql = """
        SELECT g.node_key,
               g.city_name,
               g.dish_name,
               g.dish_family,
               g.region_label,
               g.eco_label,
               g.eco_name AS eco_name_ref,
               g.category,
               g.primary_labels,
               g.primary_values,
               g.color_hex,
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
        ORDER BY g.genotype_id
    """
    results = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d.name for d in cur.description]
            for row in cur.fetchall():
                db_obj = dict(zip(cols, row))
                scores = _scores_from_genome_vector(db_obj["genome_vector"])
                media = FLAVOR_MEDIA.get(db_obj["node_key"], {})
                results.append({
                    "id": db_obj["node_key"],
                    "city": db_obj["city_name"],
                    "dish": db_obj["dish_name"],
                    "dish_family": db_obj["dish_family"],
                    "region": db_obj["region_label"],
                    "eco": db_obj["eco_label"],
                    "eco_name_ref": db_obj["eco_name_ref"],
                    "scores": scores,
                    "primary": list(db_obj["primary_labels"] or []),
                    "vals": [float(v) for v in (db_obj["primary_values"] or [])],
                    "color": db_obj["color_hex"],
                    "cat": db_obj["category"],
                    "ingredients": list(db_obj["ingredients"] or []),
                    "coordinates": [float(db_obj["lon"]), float(db_obj["lat"])],
                    "genome_vector": db_obj["genome_vector"],
                    "description": _build_flavor_description(db_obj, scores),
                    "bubbleImage": media.get("bubbleImage") or _build_flavor_image(db_obj),
                    "bubbleImageSource": media.get("bubbleImageSource"),
                })
    return results


def fetch_routes() -> list[dict]:
    """返回传播路径，shape 与原 ROUTES 兼容。"""
    sql = """
        SELECT d.route_name, d.route_color, d.route_type, ST_AsGeoJSON(d.route_geom) AS geojson
        FROM dispersal_event d
        ORDER BY d.display_order, d.event_id
    """
    results = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    for route_name, route_color, route_type, geojson_str in rows:
        gj = json.loads(geojson_str) if geojson_str else {}
        path = gj.get("coordinates", [])
        results.append({
            "name": route_name,
            "color": route_color,
            "type": route_type,
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


def fetch_data_sources() -> list[dict]:
    sql = """
        SELECT source_id, name, description, color_hex, url
        FROM data_source
        ORDER BY source_id
    """
    results = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            for _, name, description, color_hex, url in cur.fetchall():
                results.append({
                    "name": name,
                    "desc": description,
                    "color": color_hex,
                    "url": url,
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
    matched_nodes = set()
    matched_ecos = set()
    matched_routes = set()

    # PG tsvector search (only for queries >= 2 chars)
    if len(q) >= 2:
        with get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """SELECT DISTINCT g.node_key
                           FROM flavor_genotype g
                           WHERE to_tsvector(
                                   'simple',
                                   COALESCE(g.dish_name,'') || ' ' ||
                                   COALESCE(g.category,'') || ' ' ||
                                   COALESCE(g.city_name,'') || ' ' ||
                                   COALESCE(g.region_label,'') || ' ' ||
                                   COALESCE(g.eco_label,'') || ' ' ||
                                   COALESCE(g.dish_family,'')
                                 )
                              @@ plainto_tsquery('simple', %s)
                           LIMIT 8""",
                        (q,),
                    )
                    matched_nodes = {row[0] for row in cur.fetchall()}
                except Exception as exc:
                    log.debug("tsvector flavor search failed: %s", exc)

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

                try:
                    cur.execute(
                        """SELECT route_name
                           FROM dispersal_event
                           WHERE to_tsvector('simple', COALESCE(route_name, ''))
                              @@ plainto_tsquery('simple', %s)
                           LIMIT 8""",
                        (q,),
                    )
                    matched_routes = {row[0] for row in cur.fetchall()}
                except Exception as exc:
                    log.debug("tsvector route search failed: %s", exc)

    # Build results using DB-only data
    flavors = fetch_flavors()
    routes = fetch_routes()

    for f in flavors:
        # PG match
        hit_node = f["id"] in matched_nodes
        hit_eco  = f.get("eco_name_ref") in matched_ecos
        # Substring fallback (always active for single-char and UI fields)
        haystack = [
            f.get("city") or "",
            f.get("region") or "",
            f.get("dish") or "",
            f.get("eco") or "",
            f.get("dish_family") or "",
        ]
        primary_hit = any(q in p for p in (f.get("primary") or []))
        if hit_node or hit_eco or any(q in field for field in haystack) or primary_hit:
            results.append({
                "type": "node",
                "label": f.get("dish") or f.get("city"),
                "sub": f"{f.get('city')} · {f.get('region')}",
                "color": f.get("color"),
                "data": f,
            })

    for r in routes:
        if r["name"] in matched_routes or q in r["name"]:
            results.append({
                "type": "route",
                "label": r["name"],
                "sub": "海路传播" if r.get("type") == "sea" else "陆路传播",
                "color": r.get("color"),
                "data": r,
            })

    return results[:8]
