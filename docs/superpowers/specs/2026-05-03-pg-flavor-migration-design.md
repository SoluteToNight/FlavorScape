# PostgreSQL 数据迁移设计 —— 寻味地理 Flavor 库

**日期：** 2026-05-03
**目标库：** `Flavor`（PostgreSQL 16 + PostGIS，本地 `postgres@localhost:5432`，pgAdmin 服务器组 `Test`）
**作用域：** 建表 + 索引 + 种子数据填充（不改后端业务路由）

---

## 1. 总体架构

```
backend/
└── db/                          ← 新增目录
    ├── __init__.py
    ├── schema.sql               ← DDL：扩展、6 表 + 1 关联表、索引、ENUM
    ├── seed.py                  ← 种子数据生成与 INSERT 主逻辑
    └── run_migration.py         ← 入口脚本：load .env → exec DDL → seed → verify
.env                              ← DATABASE_URL=...（不进 git）
.env.example                     ← 占位模板，进 git
```

**运行命令：**
```
.venv/Scripts/python.exe -m backend.db.run_migration
```

**数据流：** `.env` → psycopg2 连接 → 执行 `schema.sql`（DROP-CREATE）→ 调用 `seed.py:seed_all(conn)` → commit → `verify(conn)` 输出回显。

**依赖增量（追加到 `backend/requirements.txt`）：**
- `psycopg2-binary>=2.9`
- `python-dotenv>=1.0`

---

## 2. Schema（schema.sql）

> **以 ER 图为准** —— 已与《数据库方案.md》原始描述对照，剔除 ER 图中未出现的字段：
> - `eco_geo_unit.geom` 删除（ER 图未画）
> - `ingredient.origin_ecos` 删除（ER 图未画，改用关联表实现 M:N "原产于"）
> - `dispersal_event.time_label` / `vehicle` 删除（ER 图未画）
> - `flavor_genotype.eco_id` **保留**（ER 图字段列表未画但 R1 关系必需，FK 是物理实现细节）

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TYPE ingredient_type AS ENUM ('香辛料','油脂','谷物','蛋白','蔬果','发酵','其他');

-- 1. EcoGeoUnit
CREATE TABLE eco_geo_unit (
    eco_id          CHAR(10) PRIMARY KEY,
    name            VARCHAR(80) NOT NULL,
    climate         JSONB,
    adjacent_ecos   TEXT[]
);

-- 2. Ingredient
CREATE TABLE ingredient (
    ingredient_id   CHAR(8)  PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    type            ingredient_type NOT NULL,
    flavor_tags     TEXT[]
);

-- 2'. 关联表：Ingredient ⇄ EcoGeoUnit（M:N "原产于"）
CREATE TABLE ingredient_origin (
    ingredient_id   CHAR(8)  REFERENCES ingredient(ingredient_id),
    eco_id          CHAR(10) REFERENCES eco_geo_unit(eco_id),
    PRIMARY KEY (ingredient_id, eco_id)
);

-- 3. FlavorGenotype
CREATE TABLE flavor_genotype (
    genotype_id     CHAR(12) PRIMARY KEY,
    dish_name       VARCHAR(50) NOT NULL,
    category        VARCHAR(30),
    eco_id          CHAR(10) REFERENCES eco_geo_unit(eco_id),
    genome_vector   JSONB,
    coordinates     GEOMETRY(Point, 4326)
);

-- 4. DispersalEvent
CREATE TABLE dispersal_event (
    event_id        CHAR(12) PRIMARY KEY,
    ingredient_id   CHAR(8)  REFERENCES ingredient(ingredient_id),
    from_eco_id     CHAR(10) REFERENCES eco_geo_unit(eco_id),
    to_eco_id       CHAR(10) REFERENCES eco_geo_unit(eco_id),
    route_geom      GEOMETRY(LineString, 4326)
);

-- 5. RecipeLink
CREATE TABLE recipe_link (
    genotype_id     CHAR(12) REFERENCES flavor_genotype(genotype_id),
    ingredient_id   CHAR(8)  REFERENCES ingredient(ingredient_id),
    role            VARCHAR(20),
    importance      NUMERIC(3,2) CHECK (importance BETWEEN 0 AND 1),
    is_native       BOOLEAN,
    PRIMARY KEY (genotype_id, ingredient_id)
);

-- 6. GenotypeLineage
CREATE TABLE genotype_lineage (
    ancestor_id     CHAR(12) REFERENCES flavor_genotype(genotype_id),
    descendant_id   CHAR(12) REFERENCES flavor_genotype(genotype_id),
    mutation_desc   TEXT,
    PRIMARY KEY (ancestor_id, descendant_id)
);
```

**索引：**
```sql
-- GiST（空间）
CREATE INDEX idx_genotype_coord  ON flavor_genotype USING GIST (coordinates);
CREATE INDEX idx_dispersal_route ON dispersal_event USING GIST (route_geom);

-- GIN（JSONB / TEXT[]）
CREATE INDEX idx_eco_climate     ON eco_geo_unit    USING GIN (climate);
CREATE INDEX idx_eco_adjacent    ON eco_geo_unit    USING GIN (adjacent_ecos);
CREATE INDEX idx_genotype_genome ON flavor_genotype USING GIN (genome_vector);
CREATE INDEX idx_ingredient_tag  ON ingredient      USING GIN (flavor_tags);

-- B-Tree（外键）
CREATE INDEX idx_genotype_eco    ON flavor_genotype  (eco_id);
CREATE INDEX idx_dispersal_ing   ON dispersal_event  (ingredient_id);
CREATE INDEX idx_dispersal_from  ON dispersal_event  (from_eco_id);
CREATE INDEX idx_dispersal_to    ON dispersal_event  (to_eco_id);
CREATE INDEX idx_recipe_ing      ON recipe_link      (ingredient_id);
CREATE INDEX idx_ing_origin_eco  ON ingredient_origin (eco_id);
```

---

## 3. 种子数据映射

| 目标表 | 来源 | 映射要点 |
|---|---|---|
| `eco_geo_unit` | `FLAVORS[].eco` 去重 | `eco_id` = `ECO` + 7 位序号；`climate` = 占位 dict（biome 类型从中文名推断）；`adjacent_ecos` = `[]` |
| `ingredient` | `FLAVORS[].ingredients` 全集去重 + 补造（茶叶、丁香） | `ingredient_id` = `ING` + 5 位序号；`type` 按硬编码字典映射到 ENUM；`flavor_tags` = 出现菜品的 primary 标签合并去重 |
| `ingredient_origin` | `FLAVORS` × ingredients 展开 | `(ingredient_id, FLAVORS[].eco 对应 eco_id)` 双键 |
| `flavor_genotype` | `FLAVORS` 17 条 | `genome_vector` = `{spicy,numbing,salty,sour,sweet,umami}` 6 维 JSONB；`coordinates` = `ST_SetSRID(ST_MakePoint(lon,lat),4326)` |
| `recipe_link` | `FLAVORS` × ingredients | `role`=`'主料'`；`importance`=1.0/N；`is_native` 由 ingredient 的 origin 集是否含该菜 eco 推算 |
| `dispersal_event` | `ROUTES` 5 条 | `ingredient_id` 手工映射（辣椒传播→朝天椒、大运河·茶叶北行→茶叶、丝绸之路→茶叶、海上香料之路→丁香、香料群岛东传→丁香）；`from/to_eco_id` 由 path 起止点最近的 flavor_genotype 反推；`route_geom`=LineString |
| `genotype_lineage` | 无源 | 留空 0 行 |

**特殊处理：**
- "茶叶""丁香"在 `app_data.py` 中不存在但被 dispersal_event 引用 → seed.py 预先补造 2 条占位 ingredient。
- ROUTES path 起止点远离任何 FLAVOR（如丝绸之路终点伊斯坦布尔）→ from/to_eco_id NULL。
- ingredient 类型字典覆盖 50 余种现有原料；未识别归 `'其他'`。

---

## 4. 错误处理与可重入

- `schema.sql` 顶部 `DROP TABLE IF EXISTS ... CASCADE` 与 `DROP TYPE IF EXISTS ingredient_type` —— 开发期任意次重跑无副作用。
- `seed.py` 单事务包裹所有 INSERT，失败 rollback。
- 所有 INSERT 加 `ON CONFLICT DO NOTHING`，二次跑不报错。
- `run_migration.py` 启动校验：`.env` 缺失或 `DATABASE_URL` 未设 → 立刻退出，提示用户 `cp .env.example .env`。
- 连接失败 / `psycopg2.OperationalError` → 友好诊断（host/port/user/db）。

---

## 5. 验证

`run_migration.py` 末尾内置 `verify(conn)`：

1. 各表 `SELECT COUNT(*)`，与预期区间对比，超出告警（不阻塞）：

   ```
   eco_geo_unit:        10–15
   ingredient:          45–60
   ingredient_origin:   50–90
   flavor_genotype:     17
   recipe_link:         50–80
   dispersal_event:     5
   genotype_lineage:    0
   ```

2. 空间健全性：
   - `SELECT ST_AsText(coordinates) FROM flavor_genotype LIMIT 1` —— 校验 POINT 文本
   - `SELECT ST_Length(route_geom) FROM dispersal_event LIMIT 1` —— 路径长度可计算
3. `SELECT indexname FROM pg_indexes WHERE schemaname='public'` —— 确认所有 13 条索引落地。

---

## 6. 范围外（明确不做）

- 后端 `routers/api.py` 业务路由仍读 `app_data.py` 硬编码，不改造为 ORM/SQL。
- MVT 直出视图（《方案》§五）暂不创建，需待 EcoGeoUnit 引入几何后再评估。
- Alembic / 版本化迁移基础设施暂不引入。
- TEOW shapefile 不再作为本次种子数据来源（因 ER 图无 geom 字段）。
