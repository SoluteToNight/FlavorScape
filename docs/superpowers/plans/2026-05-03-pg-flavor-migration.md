# PostgreSQL Flavor 库迁移 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在本地 PostgreSQL（pgAdmin 服务器组 Test，库名 Flavor）建立寻味地理数据模型 6 张实体表 + 1 张 M:N 关联表，并从 `backend/data/app_data.py` 派生种子数据灌入。

**Architecture:** 单一 Python 入口 `run_migration.py` 加载 `.env`、执行 `schema.sql`（DROP-CREATE）、调用 `seed.py:seed_all(conn)` 灌库、调用 `verify(conn)` 自动校验各表行数与空间字段。所有 SQL 走 psycopg2，单事务，失败回滚。

**Tech Stack:** PostgreSQL 16 + PostGIS, psycopg2-binary, python-dotenv, 现有 `.venv`（Python 3.12）。

---

## File Structure

| 路径 | 责任 |
|---|---|
| `backend/db/__init__.py` | 空，使 db 成为子包 |
| `backend/db/schema.sql` | DDL：扩展、ENUM、6 表 + 关联表、13 索引 |
| `backend/db/seed.py` | 从 app_data.py 派生记录、批量 INSERT |
| `backend/db/run_migration.py` | 主入口：load env → exec DDL → seed → verify |
| `.env.example` | DATABASE_URL 占位模板 |
| `.env` | 实际凭证（本地，不进 git） |
| `backend/requirements.txt` | 追加 psycopg2-binary、python-dotenv |

---

## Task 1：追加依赖并安装

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: 追加两行依赖到 backend/requirements.txt 末尾**

```
psycopg2-binary>=2.9
python-dotenv>=1.0
```

- [ ] **Step 2: 安装到 .venv**

Run:
```
uv pip install --python .venv/Scripts/python.exe psycopg2-binary python-dotenv
```

Expected: `Installed N packages` 且无报错。

- [ ] **Step 3: 校验导入**

Run:
```
.venv/Scripts/python.exe -c "import psycopg2, dotenv; print(psycopg2.__version__, dotenv.__name__)"
```

Expected: 输出版本号与 `dotenv`，无 ImportError。

---

## Task 2：环境配置文件

**Files:**
- Create: `.env.example`
- Create: `.env`

- [ ] **Step 1: 写 .env.example**

```
# PostgreSQL 连接（pgAdmin: Test 服务器组 → Flavor 数据库）
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/Flavor
```

- [ ] **Step 2: 写 .env（实际密码，已确认 nemo20041212）**

```
DATABASE_URL=postgresql://postgres:nemo20041212@localhost:5432/Flavor
```

- [ ] **Step 3: 校验 .env 不会进 git**

Run: `cat .gitignore`
确认 `.env` 已被忽略（项目 .gitignore 已包含 `.env`）。若未包含，追加 `.env` 一行。

---

## Task 3：编写 schema.sql

**Files:**
- Create: `backend/db/__init__.py`（空文件）
- Create: `backend/db/schema.sql`

- [ ] **Step 1: 创建空 __init__.py**

```python
```
（空文件即可）

- [ ] **Step 2: 写 schema.sql 完整内容**

```sql
-- 寻味地理 Flavor 库 schema
-- 与 ER 图严格对齐：EcoGeoUnit 无 geom；Ingredient 无 origin_ecos（用关联表）；
-- DispersalEvent 无 time_label/vehicle。
-- 开发期 DROP-CREATE 模式，可任意次重跑。

DROP TABLE IF EXISTS genotype_lineage CASCADE;
DROP TABLE IF EXISTS recipe_link CASCADE;
DROP TABLE IF EXISTS dispersal_event CASCADE;
DROP TABLE IF EXISTS flavor_genotype CASCADE;
DROP TABLE IF EXISTS ingredient_origin CASCADE;
DROP TABLE IF EXISTS ingredient CASCADE;
DROP TABLE IF EXISTS eco_geo_unit CASCADE;
DROP TYPE  IF EXISTS ingredient_type CASCADE;

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TYPE ingredient_type AS ENUM ('香辛料','油脂','谷物','蛋白','蔬果','发酵','其他');

CREATE TABLE eco_geo_unit (
    eco_id          CHAR(10) PRIMARY KEY,
    name            VARCHAR(80) NOT NULL,
    climate         JSONB,
    adjacent_ecos   TEXT[]
);

CREATE TABLE ingredient (
    ingredient_id   CHAR(8)  PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    type            ingredient_type NOT NULL,
    flavor_tags     TEXT[]
);

CREATE TABLE ingredient_origin (
    ingredient_id   CHAR(8)  REFERENCES ingredient(ingredient_id),
    eco_id          CHAR(10) REFERENCES eco_geo_unit(eco_id),
    PRIMARY KEY (ingredient_id, eco_id)
);

CREATE TABLE flavor_genotype (
    genotype_id     CHAR(12) PRIMARY KEY,
    dish_name       VARCHAR(50) NOT NULL,
    category        VARCHAR(30),
    eco_id          CHAR(10) REFERENCES eco_geo_unit(eco_id),
    genome_vector   JSONB,
    coordinates     GEOMETRY(Point, 4326)
);

CREATE TABLE dispersal_event (
    event_id        CHAR(12) PRIMARY KEY,
    ingredient_id   CHAR(8)  REFERENCES ingredient(ingredient_id),
    from_eco_id     CHAR(10) REFERENCES eco_geo_unit(eco_id),
    to_eco_id       CHAR(10) REFERENCES eco_geo_unit(eco_id),
    route_geom      GEOMETRY(LineString, 4326)
);

CREATE TABLE recipe_link (
    genotype_id     CHAR(12) REFERENCES flavor_genotype(genotype_id),
    ingredient_id   CHAR(8)  REFERENCES ingredient(ingredient_id),
    role            VARCHAR(20),
    importance      NUMERIC(3,2) CHECK (importance BETWEEN 0 AND 1),
    is_native       BOOLEAN,
    PRIMARY KEY (genotype_id, ingredient_id)
);

CREATE TABLE genotype_lineage (
    ancestor_id     CHAR(12) REFERENCES flavor_genotype(genotype_id),
    descendant_id   CHAR(12) REFERENCES flavor_genotype(genotype_id),
    mutation_desc   TEXT,
    PRIMARY KEY (ancestor_id, descendant_id)
);

-- GiST 空间索引
CREATE INDEX idx_genotype_coord  ON flavor_genotype USING GIST (coordinates);
CREATE INDEX idx_dispersal_route ON dispersal_event USING GIST (route_geom);

-- GIN（JSONB / 数组）索引
CREATE INDEX idx_eco_climate     ON eco_geo_unit    USING GIN (climate);
CREATE INDEX idx_eco_adjacent    ON eco_geo_unit    USING GIN (adjacent_ecos);
CREATE INDEX idx_genotype_genome ON flavor_genotype USING GIN (genome_vector);
CREATE INDEX idx_ingredient_tag  ON ingredient      USING GIN (flavor_tags);

-- B-Tree 外键索引
CREATE INDEX idx_genotype_eco    ON flavor_genotype  (eco_id);
CREATE INDEX idx_dispersal_ing   ON dispersal_event  (ingredient_id);
CREATE INDEX idx_dispersal_from  ON dispersal_event  (from_eco_id);
CREATE INDEX idx_dispersal_to    ON dispersal_event  (to_eco_id);
CREATE INDEX idx_recipe_ing      ON recipe_link      (ingredient_id);
CREATE INDEX idx_ing_origin_eco  ON ingredient_origin (eco_id);
```

---

## Task 4：编写 seed.py —— 派生数据 + 批量 INSERT

**Files:**
- Create: `backend/db/seed.py`

整个 seed.py 一次性写出。结构：
1. 顶部常量：`INGREDIENT_TYPE_MAP`（中文原料名 → ENUM 值）、`ROUTE_INGREDIENT_MAP`、`ECO_CLIMATE_HINT`
2. `seed_all(conn)`：按依赖顺序串联各 `_seed_*` 函数，返回 row count dict
3. 各表对应的 `_seed_xxx(conn) -> int`

- [ ] **Step 1: 写完整 backend/db/seed.py**

```python
"""寻味地理 Flavor 库种子数据生成器。

来源：backend/data/app_data.py 的 FLAVORS / ROUTES。
派生表 7 张：eco_geo_unit, ingredient, ingredient_origin, flavor_genotype,
recipe_link, dispersal_event（5 行）, genotype_lineage（保持空）。
"""
from __future__ import annotations
import json
from typing import Dict
import psycopg2.extras

from backend.data.app_data import FLAVORS, ROUTES


# ---- 中文原料名 → ENUM 值 ----------------------------------------------------
INGREDIENT_TYPE_MAP: Dict[str, str] = {
    # 香辛料
    "花椒": "香辛料", "朝天椒": "香辛料", "孜然": "香辛料", "葡萄干": "蔬果",
    "桂花": "香辛料", "蜜桂花": "香辛料", "陈皮": "香辛料", "大料": "香辛料",
    "辣子": "香辛料", "糟辣椒": "发酵", "木姜子": "香辛料", "青盐": "其他",
    "井盐": "其他", "蓬灰": "其他", "丁香": "香辛料", "茶叶": "香辛料",
    # 油脂
    "牛油底料": "油脂", "羊脂": "油脂", "麻酱": "油脂",
    # 谷物
    "白粥底": "谷物", "米酒": "发酵", "土豆": "蔬果", "粉条": "谷物",
    # 蛋白
    "牛肉": "蛋白", "毛肚": "蛋白", "鸭肠": "蛋白", "湖鸭": "蛋白",
    "文昌鸡": "蛋白", "内蒙羊脊": "蛋白", "东海带鱼": "蛋白", "三门青蟹": "蛋白",
    "小海螺": "蛋白", "稻花鱼": "蛋白", "五花肉": "蛋白", "血肠": "蛋白",
    "生猛海鲜": "蛋白", "鱼片": "蛋白", "象拔蚌": "蛋白", "烤鸭": "蛋白",
    "宣威火腿": "蛋白", "牛肉火锅": "蛋白", "东坡肉": "蛋白",
    # 蔬果
    "白萝卜": "蔬果", "玉米": "蔬果", "胡萝卜": "蔬果", "西湖莼菜": "蔬果",
    "椰青": "蔬果", "时蔬": "蔬果", "韭菜花": "蔬果", "哈密瓜": "蔬果",
    "反沙芋": "蔬果", "酸笋": "发酵", "野菌": "蔬果",
    "松茸": "蔬果", "鸡枞菌": "蔬果", "牛肝菌": "蔬果", "土鸡汤": "蛋白",
    "石屏豆腐": "发酵", "龙井茶": "香辛料",
    # 发酵
    "郫县豆瓣": "发酵", "黄豆酱": "发酵", "沙茶酱": "发酵", "鱼露": "发酵",
    "东北酸菜": "发酵", "红酸汤": "发酵", "腐乳": "发酵",
}


# ---- 路线 → 代表 ingredient 名（缺失时种子时补造）-------------------------
ROUTE_INGREDIENT_MAP: Dict[str, str] = {
    "丝绸之路": "茶叶",
    "海上香料之路": "丁香",
    "辣椒传播路线": "朝天椒",
    "大运河·茶叶北行": "茶叶",
    "香料群岛东传": "丁香",
}


# ---- 中文 eco 名 → climate JSONB 占位 ---------------------------------------
def climate_hint(eco_name: str) -> dict:
    """根据中文生态名推断粗略气候 metadata。"""
    if "热带" in eco_name and "亚" not in eco_name:
        return {"biome": "热带", "humidity": "湿润"}
    if "亚热带" in eco_name:
        return {"biome": "亚热带", "humidity": "湿润"}
    if "温带" in eco_name and "草原" in eco_name:
        return {"biome": "温带", "humidity": "半干旱"}
    if "温带" in eco_name and "荒漠" in eco_name:
        return {"biome": "温带", "humidity": "干旱"}
    if "针阔" in eco_name:
        return {"biome": "温带", "humidity": "湿润"}
    if "落叶" in eco_name:
        return {"biome": "暖温带", "humidity": "半湿润"}
    if "山地" in eco_name:
        return {"biome": "山地", "humidity": "湿润"}
    return {"biome": "未分类"}


# ---- 工具：生成定长 ID -------------------------------------------------------
def make_id(prefix: str, total_len: int, idx: int) -> str:
    return prefix + str(idx).zfill(total_len - len(prefix))


# ============================================================================
# 各表 seed
# ============================================================================
def _seed_eco_geo_unit(conn) -> dict:
    """返回 {eco_name: eco_id} 映射，供后续表使用。"""
    eco_names = sorted({f["eco"] for f in FLAVORS})
    name_to_id: dict = {}
    rows = []
    for i, name in enumerate(eco_names, start=1):
        eco_id = make_id("ECO", 10, i)
        name_to_id[name] = eco_id
        rows.append((eco_id, name, json.dumps(climate_hint(name)), []))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO eco_geo_unit (eco_id, name, climate, adjacent_ecos) "
            "VALUES (%s, %s, %s::jsonb, %s) ON CONFLICT DO NOTHING",
            rows,
        )
    return name_to_id


def _seed_ingredient(conn) -> dict:
    """返回 {ingredient_name: ingredient_id}。"""
    # 收集 FLAVORS 中所有原料 + ROUTE 引用的"茶叶""丁香"
    all_names = set()
    for f in FLAVORS:
        all_names.update(f["ingredients"])
    all_names.update(ROUTE_INGREDIENT_MAP.values())

    # 每个原料聚合 flavor_tags（出现在哪些菜中，把那些菜的 primary 合并）
    name_to_tags: dict = {n: set() for n in all_names}
    for f in FLAVORS:
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


def _seed_ingredient_origin(conn, eco_map, ing_map) -> int:
    pairs = set()
    for f in FLAVORS:
        eco_id = eco_map[f["eco"]]
        for ing in f["ingredients"]:
            pairs.add((ing_map[ing], eco_id))
    rows = list(pairs)
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO ingredient_origin (ingredient_id, eco_id) "
            "VALUES (%s, %s) ON CONFLICT DO NOTHING",
            rows,
        )
    return len(rows)


def _seed_flavor_genotype(conn, eco_map) -> dict:
    """返回 {flavor.id (来自 app_data): genotype_id}。"""
    SCORE_KEYS = ["spicy", "numbing", "salty", "sour", "sweet", "umami"]
    flavor_id_to_gid: dict = {}
    rows = []
    for i, f in enumerate(FLAVORS, start=1):
        gid = make_id("GEN", 12, i)
        flavor_id_to_gid[f["id"]] = gid
        genome = {k: v for k, v in zip(SCORE_KEYS, f["scores"])}
        lon, lat = f["coordinates"]
        rows.append((
            gid, f["dish"], f["cat"], eco_map[f["eco"]],
            json.dumps(genome, ensure_ascii=False),
            lon, lat,
        ))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO flavor_genotype "
            "(genotype_id, dish_name, category, eco_id, genome_vector, coordinates) "
            "VALUES (%s, %s, %s, %s, %s::jsonb, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) "
            "ON CONFLICT DO NOTHING",
            rows,
        )
    return flavor_id_to_gid


def _seed_recipe_link(conn, gid_map, ing_map, eco_map) -> int:
    rows = []
    for f in FLAVORS:
        gid = gid_map[f["id"]]
        eco_id = eco_map[f["eco"]]
        n = len(f["ingredients"])
        importance = round(1.0 / n, 2) if n else 0.0
        for ing_name in f["ingredients"]:
            ing_id = ing_map[ing_name]
            # is_native: ingredient origin 集是否含该菜 eco（自定义为 True，因为
            # ingredient_origin 在上一步就是这样建的）
            rows.append((gid, ing_id, "主料", importance, True))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO recipe_link "
            "(genotype_id, ingredient_id, role, importance, is_native) "
            "VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            rows,
        )
    return len(rows)


def _nearest_eco_id(lon, lat, gid_map, eco_map):
    """从 FLAVORS 中找离 (lon,lat) 最近的菜，返回其 eco_id；无则 None。"""
    best = None
    best_d = float("inf")
    for f in FLAVORS:
        flon, flat = f["coordinates"]
        d = (flon - lon) ** 2 + (flat - lat) ** 2
        if d < best_d:
            best_d = d
            best = eco_map[f["eco"]]
    # 仅在距离 < ~10° (约 1100 km) 时返回，避免给海外端点强行配国内 eco
    return best if best_d < 100 else None


def _seed_dispersal_event(conn, ing_map, eco_map, gid_map) -> int:
    rows = []
    for i, route in enumerate(ROUTES, start=1):
        eid = make_id("EVT", 12, i)
        ing_name = ROUTE_INGREDIENT_MAP[route["name"]]
        ing_id = ing_map.get(ing_name)
        path = route["path"]
        from_lon, from_lat = path[0]
        to_lon, to_lat = path[-1]
        from_eco = _nearest_eco_id(from_lon, from_lat, gid_map, eco_map)
        to_eco = _nearest_eco_id(to_lon, to_lat, gid_map, eco_map)
        # LineString WKT
        wkt_pts = ",".join(f"{x} {y}" for x, y in path)
        wkt = f"LINESTRING({wkt_pts})"
        rows.append((eid, ing_id, from_eco, to_eco, wkt))
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(
            cur,
            "INSERT INTO dispersal_event "
            "(event_id, ingredient_id, from_eco_id, to_eco_id, route_geom) "
            "VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 4326)) "
            "ON CONFLICT DO NOTHING",
            rows,
        )
    return len(rows)


# ============================================================================
# 主入口
# ============================================================================
def seed_all(conn) -> dict:
    eco_map = _seed_eco_geo_unit(conn)
    ing_map = _seed_ingredient(conn)
    n_ing_origin = _seed_ingredient_origin(conn, eco_map, ing_map)
    gid_map = _seed_flavor_genotype(conn, eco_map)
    n_recipe = _seed_recipe_link(conn, gid_map, ing_map, eco_map)
    n_disp = _seed_dispersal_event(conn, ing_map, eco_map, gid_map)
    return {
        "eco_geo_unit": len(eco_map),
        "ingredient": len(ing_map),
        "ingredient_origin": n_ing_origin,
        "flavor_genotype": len(gid_map),
        "recipe_link": n_recipe,
        "dispersal_event": n_disp,
        "genotype_lineage": 0,
    }
```

---

## Task 5：编写 run_migration.py

**Files:**
- Create: `backend/db/run_migration.py`

- [ ] **Step 1: 写完整 backend/db/run_migration.py**

```python
"""寻味地理 Flavor 库迁移入口。

用法：
    .venv/Scripts/python.exe -m backend.db.run_migration
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from backend.db.seed import seed_all


HERE = Path(__file__).resolve().parent
SCHEMA_SQL = HERE / "schema.sql"


# 预期行数区间（low, high）。超出告警，不阻塞。
EXPECTED_COUNTS = {
    "eco_geo_unit":      (10, 20),
    "ingredient":        (45, 80),
    "ingredient_origin": (50, 120),
    "flavor_genotype":   (17, 17),
    "recipe_link":       (50, 100),
    "dispersal_event":   (5, 5),
    "genotype_lineage":  (0, 0),
}


def load_database_url() -> str:
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        print("[ERROR] DATABASE_URL 未在 .env 中设置。", file=sys.stderr)
        print("        请 cp .env.example .env 并填入实际密码。", file=sys.stderr)
        sys.exit(1)
    return url


def execute_schema(conn):
    sql = SCHEMA_SQL.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    print(f"[OK] schema.sql 执行完成（{SCHEMA_SQL}）")


def verify(conn):
    print("\n=== verify ===")
    with conn.cursor() as cur:
        for table, (lo, hi) in EXPECTED_COUNTS.items():
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            n = cur.fetchone()[0]
            mark = "✓" if lo <= n <= hi else "⚠"
            print(f"  {mark} {table}: {n} (expect {lo}–{hi})")
        # 空间健全性
        cur.execute(
            "SELECT ST_AsText(coordinates) FROM flavor_genotype "
            "WHERE coordinates IS NOT NULL LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            print(f"  ✓ POINT sample: {row[0]}")
        cur.execute(
            "SELECT ST_Length(route_geom) FROM dispersal_event "
            "WHERE route_geom IS NOT NULL LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            print(f"  ✓ LineString length sample: {row[0]:.2f}°")
        # 索引数
        cur.execute(
            "SELECT COUNT(*) FROM pg_indexes "
            "WHERE schemaname='public' AND indexname LIKE 'idx_%'"
        )
        n_idx = cur.fetchone()[0]
        print(f"  {'✓' if n_idx >= 12 else '⚠'} indexes: {n_idx} (expect ≥12)")


def main():
    url = load_database_url()
    print(f"[INFO] 连接到 {url.rsplit('@', 1)[-1]}")
    try:
        conn = psycopg2.connect(url)
    except psycopg2.OperationalError as e:
        print(f"[ERROR] 连接失败：{e}", file=sys.stderr)
        print("        检查：服务是否启动？库 Flavor 是否已创建？密码是否正确？",
              file=sys.stderr)
        sys.exit(2)

    try:
        with conn:  # 单事务包裹（异常 rollback，正常 commit）
            execute_schema(conn)
            counts = seed_all(conn)
        print(f"[OK] 种子数据写入：{counts}")
        verify(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
```

---

## Task 6：实跑迁移并校验

**Files:** 无修改，仅运行。

- [ ] **Step 1: 确认 PostgreSQL 服务在跑、Flavor 库已建**

Run（PowerShell 或 bash）:
```
.venv/Scripts/python.exe -c "import psycopg2; psycopg2.connect('postgresql://postgres:nemo20041212@localhost:5432/Flavor').close(); print('OK')"
```

Expected: 输出 `OK`。
若报 `database "Flavor" does not exist` → 用户在 pgAdmin 中先建 Flavor 库；
若报 `password authentication failed` → 校对 .env 密码。

- [ ] **Step 2: 跑迁移**

Run:
```
.venv/Scripts/python.exe -m backend.db.run_migration
```

Expected 输出大致：
```
[INFO] 连接到 localhost:5432/Flavor
[OK] schema.sql 执行完成（...）
[OK] 种子数据写入：{'eco_geo_unit': 13, 'ingredient': ~52, ...}
=== verify ===
  ✓ eco_geo_unit: 13 (expect 10–20)
  ✓ ingredient: 52 (expect 45–80)
  ✓ ingredient_origin: 76 (expect 50–120)
  ✓ flavor_genotype: 17 (expect 17–17)
  ✓ recipe_link: 68 (expect 50–100)
  ✓ dispersal_event: 5 (expect 5–5)
  ✓ genotype_lineage: 0 (expect 0–0)
  ✓ POINT sample: POINT(104.1 30.7)
  ✓ LineString length sample: 95.xx°
  ✓ indexes: 12 (expect ≥12)
```

- [ ] **Step 3: 二次重跑测试可重入性**

Run 同样的命令再跑一次。Expected: 输出与第一次相同（DROP-CREATE 后重新灌库），无报错。

---

## Self-Review

- ✅ Spec §1 总体架构 → Task 3/4/5 落地 backend/db/* 三文件
- ✅ Spec §2 schema → Task 3 完整 schema.sql
- ✅ Spec §3 种子映射 → Task 4 各 _seed_* 函数（eco / ingredient / ingredient_origin / genotype / recipe_link / dispersal_event / lineage 留空）
- ✅ Spec §4 错误处理 → Task 5：DROP-CREATE、`with conn` 单事务、`ON CONFLICT DO NOTHING`、缺失 .env 退出、OperationalError 友好诊断
- ✅ Spec §5 验证 → Task 5 verify() + Task 6 实跑校验
- ✅ 类型一致：所有 ID 长度对齐 schema 类型（ECO+7=10、ING+5=8、GEN+9=12、EVT+9=12）

无占位符，无 TBD，所有文件路径明确。
