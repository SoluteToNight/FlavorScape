"""寻味地理 Flavor 库种子数据生成器。

来源：
  - eco_geo_unit: wwf_terr_ecos_merged.shp（827 行 WWF TEOW 全域）
  - 其余业务表: backend/data/app_data.py 的导入快照
"""
from __future__ import annotations
import json
import logging
from typing import Any, Dict

import fiona
import psycopg2.extras
from shapely.geometry import shape
from shapely import wkb

from backend.config import TEOW_MERGED
from backend.data.app_data import (
    CHAPTERS as APP_CHAPTERS,
    DATA_SOURCES as APP_DATA_SOURCES,
    FLAVORS as APP_FLAVORS,
    ROUTES as APP_ROUTES,
)
from backend.data.biome_names import BIOME_MAP  # canonical source

log = logging.getLogger("seed")

DataBundle = dict[str, list[dict[str, Any]]]

# ---- ECO_NAME 中文翻译（中国区域）—— 地区名，非 biome 类型名 -----------------
ECO_NAME_CN: Dict[str, str] = {
    "Alai-Western Tian Shan steppe":                         "阿赖-西天山草原",
    "Altai alpine meadow and tundra":                        "阿尔泰山地草甸与冻原",
    "Altai montane forest and forest steppe":                "阿尔泰山地森林与森林草原",
    "Altai steppe and semi-desert":                          "阿尔泰草原与半荒漠",
    "Amur meadow steppe":                                    "阿穆尔草甸草原",
    "Central China loess plateau mixed forests":             "华中黄土高原混交林",
    "Central Tibetan Plateau alpine steppe":                 "藏中高原高寒草原",
    "Changjiang Plain evergreen forests":                    "长江平原常绿林",
    "Da Hinggan-Dzhagdy Mountains conifer forests":          "大兴安岭-扎格迪山针叶林",
    "Daba Mountains evergreen forests":                      "大巴山常绿林",
    "Eastern Gobi desert steppe":                            "东戈壁荒漠草原",
    "Eastern Himalayan alpine shrub and meadows":            "东喜马拉雅高山灌丛草甸",
    "Gobi Lakes Valley desert steppe":                       "戈壁湖谷荒漠草原",
    "Guizhou Plateau broadleaf and mixed forests":           "贵州高原阔叶混交林",
    "Hainan Island monsoon rain forests":                    "海南岛季风雨林",
    "Helanshan montane conifer forests":                     "贺兰山山地针叶林",
    "Hengduan Mountains subalpine conifer forests":          "横断山亚高山针叶林",
    "Huang He Plain mixed forests":                          "黄河平原混交林",
    "Karakoram-West Tibetan Plateau alpine steppe":          "喀喇昆仑-西青藏高原高寒草原",
    "Manchurian mixed forests":                              "满洲混交林",
    "Mongolian-Manchurian grassland":                        "蒙古-满洲草原",
    "North Tibetan Plateau-Kunlun Mountains alpine desert":  "北青藏高原-昆仑山高寒荒漠",
    "Northeast China Plain deciduous forests":               "东北平原落叶林",
    "Northeastern Himalayan subalpine conifer forests":      "东北喜马拉雅亚高山针叶林",
    "Northwestern Himalayan alpine shrub and meadows":       "西北喜马拉雅高山灌丛草甸",
    "Okhotsk-Manchurian taiga":                              "鄂霍次克-满洲泰加林",
    "Ordos Plateau steppe":                                  "鄂尔多斯高原草原",
    "Qilian Mountains conifer forests":                      "祁连山针叶林",
    "Qilian Mountains subalpine meadows":                    "祁连山亚高山草甸",
    "Qin Ling Mountains deciduous forests":                  "秦岭落叶林",
    "Sichuan Basin evergreen broadleaf forests":             "四川盆地常绿阔叶林",
    "South China-Vietnam subtropical evergreen forests":     "华南-越南亚热带常绿林",
    "South China Sea Islands":                               "南海诸岛",
    "South Taiwan monsoon rain forests":                     "南台湾季风雨林",
    "Taiwan subtropical evergreen forests":                  "台湾亚热带常绿林",
    "Taklimakan desert":                                     "塔克拉玛干荒漠",
    "Tian Shan foothill arid steppe":                        "天山山麓干旱草原",
    "Tian Shan montane conifer forests":                     "天山山地针叶林",
    "Tian Shan montane steppe and meadows":                  "天山山地草原草甸",
    "Tibetan Plateau alpine shrublands and meadows":         "青藏高原高山灌丛草甸",
    "Ussuri broadleaf and mixed forests":                    "乌苏里阔叶混交林",
    "Western Himalayan alpine shrub and Meadows":            "西喜马拉雅高山灌丛草甸",
    "Yellow Sea saline meadow":                              "黄海盐生草甸",
    "Yunnan Plateau subtropical evergreen forests":          "云南高原亚热带常绿林",
}
ECO_CN_MAP: Dict[str, str] = {
    "亚热带常绿阔叶林":       "Sichuan Basin evergreen broadleaf forests",
    "南亚热带常绿林":         "South China-Vietnam subtropical evergreen forests",
    "温带草原":               "Mongolian-Manchurian grassland",
    "温带荒漠":               "Taklimakan desert",
    "暖温带落叶阔叶林":       "Huang He Plain mixed forests",
    "中亚热带常绿林":         "Changjiang Plain evergreen forests",
    "亚热带山地植被":         "Yunnan Plateau subtropical evergreen forests",
    "南亚热带季风林":         "Hainan Island monsoon rain forests",
    "热带季雨林":             "Hainan Island monsoon rain forests",
    "亚热带山地针阔混交林":   "Hengduan Mountains subalpine conifer forests",
    "北亚热带常绿落叶混交林":  "Qin Ling Mountains deciduous forests",
    "温带针阔叶混交林":       "Manchurian mixed forests",
}

# ---- 中文原料名 → ENUM 值 ----------------------------------------------------
INGREDIENT_TYPE_MAP: Dict[str, str] = {
    "花椒": "香辛料", "朝天椒": "香辛料", "孜然": "香辛料", "葡萄干": "蔬果",
    "桂花": "香辛料", "蜜桂花": "香辛料", "陈皮": "香辛料", "大料": "香辛料",
    "辣子": "香辛料", "糟辣椒": "发酵", "木姜子": "香辛料", "青盐": "其他",
    "井盐": "其他", "蓬灰": "其他", "丁香": "香辛料", "茶叶": "香辛料",
    "牛油底料": "油脂", "羊脂": "油脂", "麻酱": "油脂",
    "白粥底": "谷物", "米酒": "发酵", "土豆": "蔬果", "粉条": "谷物",
    "牛肉": "蛋白", "毛肚": "蛋白", "鸭肠": "蛋白", "湖鸭": "蛋白",
    "文昌鸡": "蛋白", "内蒙羊脊": "蛋白", "东海带鱼": "蛋白", "三门青蟹": "蛋白",
    "小海螺": "蛋白", "稻花鱼": "蛋白", "五花肉": "蛋白", "血肠": "蛋白",
    "生猛海鲜": "蛋白", "鱼片": "蛋白", "象拔蚌": "蛋白", "烤鸭": "蛋白",
    "宣威火腿": "蛋白", "牛肉火锅": "蛋白", "东坡肉": "蛋白",
    "白萝卜": "蔬果", "玉米": "蔬果", "胡萝卜": "蔬果", "西湖莼菜": "蔬果",
    "椰青": "蔬果", "时蔬": "蔬果", "韭菜花": "蔬果", "哈密瓜": "蔬果",
    "反沙芋": "蔬果", "酸笋": "发酵", "野菌": "蔬果",
    "松茸": "蔬果", "鸡枞菌": "蔬果", "牛肝菌": "蔬果", "土鸡汤": "蛋白",
    "石屏豆腐": "发酵", "龙井茶": "香辛料",
    "郫县豆瓣": "发酵", "黄豆酱": "发酵", "沙茶酱": "发酵", "鱼露": "发酵",
    "东北酸菜": "发酵", "红酸汤": "发酵", "腐乳": "发酵",
}

ROUTE_INGREDIENT_MAP: Dict[str, str] = {
    "丝绸之路": "茶叶", "海上香料之路": "丁香", "辣椒传播路线": "朝天椒",
    "大运河·茶叶北行": "茶叶", "香料群岛东传": "丁香",
}


def make_id(prefix: str, total_len: int, idx: int) -> str:
    return prefix + str(idx).zfill(total_len - len(prefix))


def load_app_data_bundle() -> DataBundle:
    return {
        "flavors": [dict(item) for item in APP_FLAVORS],
        "routes": [dict(item) for item in APP_ROUTES],
        "chapters": [dict(item) for item in APP_CHAPTERS],
        "data_sources": [dict(item) for item in APP_DATA_SOURCES],
    }


def reset_business_tables(conn) -> None:
    """清空业务表，保留 eco_geo_unit。适合从 JSON 全量重导。"""
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                data_source,
                chapter,
                dish_lineage,
                recipe_link,
                dispersal_event,
                dish,
                ingredient_origin,
                ingredient
            RESTART IDENTITY CASCADE
            """
        )
    conn.commit()


# ============================================================================
# _seed_eco_geo_unit — 从 SHP 导入全部 827 个 WWF TEOW 生态区
# ============================================================================
def _seed_eco_geo_unit(conn) -> dict:
    """返回 {中文生态名: SHP ECO_NAME} 映射字典。"""
    if not TEOW_MERGED.exists():
        raise FileNotFoundError(f"TEOW merged SHP not found: {TEOW_MERGED}")

    rows = []
    with fiona.open(str(TEOW_MERGED)) as src:
        for feat in src:
            props = feat["properties"]
            eco_name = props["ECO_NAME"]
            eco_code = props.get("eco_code", "")
            realm    = props.get("REALM_1", "")
            biome_num = int(props.get("BIOME", 0))
            area     = props.get("area_km2")
            biome_en, biome_cn = BIOME_MAP.get(biome_num, ("Unknown", "未知"))
            eco_name_cn = ECO_NAME_CN.get(eco_name)  # 中国区域 → 中文名，其余 NULL
            geom     = shape(feat["geometry"])
            if not geom.is_valid:
                geom = geom.buffer(0)
            wkb_hex  = geom.wkb_hex

            rows.append((
                eco_name, eco_name_cn, eco_code, realm,
                biome_en, biome_cn, area,
                None, [], [], None, wkb_hex,
            ))

    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO eco_geo_unit "
            "(eco_name, eco_name_cn, eco_code, realm, biome, biome_cn, "
            " area_km2, climate, adjacent_ecos, dominant_ingredients, description, boundary) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, "
            "        ST_GeomFromWKB(decode(%s, 'hex'), 4326)) "
            "ON CONFLICT DO NOTHING",
            rows,
            page_size=200,
        )
    conn.commit()

    log.info(f"eco_geo_unit: {len(rows)} rows seeded from SHP")
    return ECO_CN_MAP


# ============================================================================
# 其余表 — 不变逻辑（仅列名从 eco_id → eco_name）
# ============================================================================
def _seed_ingredient(conn, flavors: list[dict], routes: list[dict]) -> dict:
    """返回 {ingredient_name: ingredient_id}。"""
    all_names = set()
    for f in flavors:
        all_names.update(f["ingredients"])
    for route in routes:
        ingredient_name = route.get("ingredient_name") or route.get("ingredientName")
        if ingredient_name:
            all_names.add(ingredient_name)
        elif route["name"] in ROUTE_INGREDIENT_MAP:
            all_names.add(ROUTE_INGREDIENT_MAP[route["name"]])

    name_to_tags: dict = {n: set() for n in all_names}
    for f in flavors:
        for ing in f["ingredients"]:
            name_to_tags[ing].update(f["primary"])

    name_to_id: dict = {}
    rows = []
    for i, name in enumerate(sorted(all_names), start=1):
        ing_id = make_id("ING", 8, i)
        name_to_id[name] = ing_id
        type_val = INGREDIENT_TYPE_MAP.get(name, "其他")
        tags = sorted(name_to_tags.get(name, []))
        rows.append((ing_id, name, type_val, tags))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO ingredient (ingredient_id, name, type, flavor_tags) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
            rows,
        )
    return name_to_id


def _seed_ingredient_origin(conn, eco_map, ing_map, flavors: list[dict]) -> int:
    pairs = set()
    for f in flavors:
        eco_name = f.get("eco_name") or f.get("ecoName") or eco_map.get(f["eco"])
        if not eco_name:
            continue
        for ing in f["ingredients"]:
            pairs.add((ing_map[ing], eco_name))
    rows = list(pairs)
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO ingredient_origin (ingredient_id, eco_name) "
            "VALUES (%s, %s) ON CONFLICT DO NOTHING",
            rows,
        )
    return len(rows)


def _seed_dish(conn, eco_map, flavors: list[dict]) -> dict:
    """返回 {flavor.id (来自 app_data): dish_id}。"""
    SCORE_KEYS = ["spicy", "numbing", "salty", "sour", "sweet", "umami"]
    flavor_id_to_did: dict = {}
    rows = []
    for i, f in enumerate(flavors, start=1):
        did = make_id("DSH", 12, i)
        flavor_id_to_did[f["id"]] = did
        genome = {k: v for k, v in zip(SCORE_KEYS, f["scores"])}
        lon, lat = f["coordinates"]
        eco_name = f.get("eco_name") or f.get("ecoName") or eco_map.get(f["eco"])
        rows.append((
            did,
            f["id"],
            f["city"],
            f["dish"],
            f["dish_family"],
            f["region"],
            f["eco"],
            f["cat"],
            eco_name,
            json.dumps(genome, ensure_ascii=False),
            list(f["primary"]),
            list(f["vals"]),
            f["color"],
            lon, lat,
        ))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO dish "
            "(dish_id, node_key, city_name, dish_name, dish_family, region_label, eco_label, "
            " category, eco_name, flavor_genotype, primary_labels, primary_values, color_hex, coordinates) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, "
            "        ST_SetSRID(ST_MakePoint(%s, %s), 4326)) "
            "ON CONFLICT DO NOTHING",
            rows,
        )
    return flavor_id_to_did


def _seed_recipe_link(conn, did_map, ing_map, flavors: list[dict]) -> int:
    rows = []
    for f in flavors:
        did = did_map[f["id"]]
        n = len(f["ingredients"])
        importance = round(1.0 / n, 2) if n else 0.0
        for ing_name in f["ingredients"]:
            ing_id = ing_map[ing_name]
            rows.append((did, ing_id, "主料", importance, True))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO recipe_link "
            "(dish_id, ingredient_id, role, importance, is_native) "
            "VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            rows,
        )
    return len(rows)


def _nearest_eco_name(lon, lat, eco_map, flavors: list[dict]):
    """从 FLAVORS 中找离 (lon,lat) 最近的菜，返回其 eco_name；距离过远（>10°）返回 None。"""
    best = None
    best_d = float("inf")
    for f in flavors:
        flon, flat = f["coordinates"]
        d = (flon - lon) ** 2 + (flat - lat) ** 2
        if d < best_d:
            best_d = d
            best = f.get("eco_name") or f.get("ecoName") or eco_map.get(f["eco"])
    return best if best_d < 100 else None


def _seed_dispersal_event(conn, ing_map, eco_map, routes: list[dict], flavors: list[dict]) -> int:
    rows = []
    for i, route in enumerate(routes, start=1):
        eid = make_id("EVT", 12, i)
        ing_name = route.get("ingredient_name") or route.get("ingredientName") or ROUTE_INGREDIENT_MAP.get(route["name"])
        if not ing_name:
            raise KeyError(f"Route '{route['name']}' 缺少 ingredient_name，且无默认映射。")
        ing_id = ing_map.get(ing_name)
        path = route["path"]
        from_lon, from_lat = path[0]
        to_lon, to_lat = path[-1]
        from_eco = _nearest_eco_name(from_lon, from_lat, eco_map, flavors)
        to_eco = _nearest_eco_name(to_lon, to_lat, eco_map, flavors)
        wkt_pts = ",".join(f"{x} {y}" for x, y in path)
        wkt = f"LINESTRING({wkt_pts})"
        rows.append((
            eid, route["name"], route["type"], route["color"], i,
            ing_id, from_eco, to_eco, wkt,
        ))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO dispersal_event "
            "(event_id, route_name, route_type, route_color, display_order, "
            " ingredient_id, from_eco_name, to_eco_name, route_geom) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326)) "
            "ON CONFLICT DO NOTHING",
            rows,
        )
    return len(rows)


def _seed_chapter(conn, chapters: list[dict]) -> int:
    rows = []
    for c in chapters:
        rows.append((
            c["id"], c["title"], c["date"], c["body"],
            c["cite"], c["source"], c["routeName"],
        ))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO chapter "
            "(chapter_id, title, date_label, body, cite, source, route_name) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            rows,
        )
    return len(rows)


def _seed_data_source(conn, data_sources: list[dict]) -> int:
    rows = []
    for i, ds in enumerate(data_sources, start=1):
        rows.append((i, ds["name"], ds["desc"], ds["color"], ds["url"]))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO data_source "
            "(source_id, name, description, color_hex, url) "
            "VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            rows,
        )
    return len(rows)


# ============================================================================
# 主入口
# ============================================================================
def seed_all(conn, bundle: DataBundle | None = None) -> dict:
    bundle = bundle or load_app_data_bundle()
    flavors = bundle["flavors"]
    routes = bundle["routes"]
    chapters = bundle["chapters"]
    data_sources = bundle["data_sources"]

    eco_map = _seed_eco_geo_unit(conn)
    ing_map = _seed_ingredient(conn, flavors, routes)
    n_ing_origin = _seed_ingredient_origin(conn, eco_map, ing_map, flavors)
    did_map = _seed_dish(conn, eco_map, flavors)
    n_recipe = _seed_recipe_link(conn, did_map, ing_map, flavors)
    n_disp = _seed_dispersal_event(conn, ing_map, eco_map, routes, flavors)
    n_chap = _seed_chapter(conn, chapters)
    n_sources = _seed_data_source(conn, data_sources)
    conn.commit()
    return {
        "eco_geo_unit": _count(conn, "eco_geo_unit"),
        "ingredient": len(ing_map),
        "ingredient_origin": n_ing_origin,
        "dish": len(did_map),
        "recipe_link": n_recipe,
        "dispersal_event": n_disp,
        "dish_lineage": 0,
        "chapter": n_chap,
        "data_source": n_sources,
    }


def _count(conn, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return cur.fetchone()[0]
