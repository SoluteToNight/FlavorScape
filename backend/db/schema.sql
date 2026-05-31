-- 寻味地理 Flavor 库 schema
-- EcoGeoUnit 现含 boundary GEOMETRY + 827 行 WWF TEOW 生态区
-- 开发期 DROP-CREATE 模式，可任意次重跑。

DROP TABLE IF EXISTS data_source CASCADE;
DROP TABLE IF EXISTS chapter CASCADE;
DROP TABLE IF EXISTS dish_lineage CASCADE;
DROP TABLE IF EXISTS recipe_link CASCADE;
DROP TABLE IF EXISTS dispersal_event CASCADE;
DROP TABLE IF EXISTS dish CASCADE;
DROP TABLE IF EXISTS ingredient_origin CASCADE;
DROP TABLE IF EXISTS ingredient CASCADE;
DROP TABLE IF EXISTS eco_geo_unit CASCADE;
DROP TYPE  IF EXISTS ingredient_type CASCADE;

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TYPE ingredient_type AS ENUM ('香辛料','油脂','谷物','蛋白','蔬果','发酵','其他');

-- ============================================================================
-- 生态地理单元（827 行，WWF TEOW 全域）
-- ============================================================================
CREATE TABLE eco_geo_unit (
    eco_name            VARCHAR(150) PRIMARY KEY,          -- SHP ECO_NAME
    eco_name_cn         VARCHAR(100),                      -- 中文名（暂留空）
    eco_code            VARCHAR(20),                       -- SHP eco_code, e.g. "AA0101"
    realm               VARCHAR(20),                       -- SHP REALM_1, e.g. "Palearctic"
    biome               VARCHAR(80),                       -- BIOME 查表英文名
    biome_cn            VARCHAR(30),                       -- BIOME 查表中文名
    area_km2            NUMERIC,                           -- SHP area_km2
    climate             JSONB,                             -- 气候属性（暂 NULL）
    adjacent_ecos       TEXT[],                            -- 相邻生态区（暂空）
    dominant_ingredients TEXT[],                           -- 本地优势原材料（暂空）
    description         TEXT,                              -- 中文环境描述（暂 NULL）
    boundary            GEOMETRY(MultiPolygon, 4326)       -- SHP 矢量边界
);

-- ============================================================================
-- 原材料
-- ============================================================================
CREATE TABLE ingredient (
    ingredient_id   CHAR(8)  PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    type            ingredient_type NOT NULL,
    flavor_tags     TEXT[]
);

-- ============================================================================
-- 原材料原产地（M:N）
-- ============================================================================
CREATE TABLE ingredient_origin (
    ingredient_id   CHAR(8)       REFERENCES ingredient(ingredient_id),
    eco_name        VARCHAR(150)  REFERENCES eco_geo_unit(eco_name),
    PRIMARY KEY (ingredient_id, eco_name)
);

-- ============================================================================
-- 菜肴成品
-- ============================================================================
CREATE TABLE dish (
    dish_id         CHAR(12) PRIMARY KEY,
    node_key        VARCHAR(80) UNIQUE NOT NULL,          -- 原 app_data id / 前端稳定标识
    city_name       VARCHAR(50) NOT NULL,                 -- 城市展示名
    dish_name       VARCHAR(50) NOT NULL,
    dish_family     VARCHAR(50),
    region_label    VARCHAR(100),                         -- 原 app_data region
    eco_label       VARCHAR(80),                          -- 原 app_data eco（展示标签）
    category        VARCHAR(30),
    eco_name        VARCHAR(150) REFERENCES eco_geo_unit(eco_name),
    flavor_genotype JSONB,                                -- 六维风味向量（麻、辣、咸、酸、甜、鲜）
    primary_labels  TEXT[],                               -- 原 app_data primary
    primary_values  NUMERIC(4,2)[],                       -- 原 app_data vals
    color_hex       VARCHAR(7),                           -- 原 app_data color
    coordinates     GEOMETRY(Point, 4326)
);

-- ============================================================================
-- 传播事件
-- ============================================================================
CREATE TABLE dispersal_event (
    event_id        CHAR(12) PRIMARY KEY,
    route_name      VARCHAR(40) UNIQUE NOT NULL,
    route_type      VARCHAR(10) NOT NULL CHECK (route_type IN ('land', 'sea')),
    route_color     VARCHAR(7) NOT NULL,
    display_order   SMALLINT NOT NULL,
    ingredient_id   CHAR(8)       REFERENCES ingredient(ingredient_id),
    from_eco_name   VARCHAR(150)  REFERENCES eco_geo_unit(eco_name),
    to_eco_name     VARCHAR(150)  REFERENCES eco_geo_unit(eco_name),
    route_geom      GEOMETRY(LineString, 4326),
    CHECK (from_eco_name IS NULL OR to_eco_name IS NULL OR from_eco_name <> to_eco_name)
);

-- ============================================================================
-- 配方连结（M:N）
-- ============================================================================
CREATE TABLE recipe_link (
    dish_id         CHAR(12) REFERENCES dish(dish_id),
    ingredient_id   CHAR(8)  REFERENCES ingredient(ingredient_id),
    role            VARCHAR(20),
    importance      NUMERIC(3,2) CHECK (importance BETWEEN 0 AND 1),
    is_native       BOOLEAN,
    PRIMARY KEY (dish_id, ingredient_id)
);

-- ============================================================================
-- 菜肴溯源链（M:N 自引用）— 当前无数据
-- ============================================================================
CREATE TABLE dish_lineage (
    ancestor_dish_id    CHAR(12) REFERENCES dish(dish_id),
    descendant_dish_id  CHAR(12) REFERENCES dish(dish_id),
    mutation_desc   TEXT,
    PRIMARY KEY (ancestor_dish_id, descendant_dish_id),
    CHECK (ancestor_dish_id <> descendant_dish_id)
);

-- ============================================================================
-- C1 扩展：CHAPTERS 史料表
-- ============================================================================
CREATE TABLE chapter (
    chapter_id      INT PRIMARY KEY,
    title           VARCHAR(50) NOT NULL,
    date_label      VARCHAR(40),
    body            TEXT,
    cite            TEXT,
    source          VARCHAR(80),
    route_name      VARCHAR(40) REFERENCES dispersal_event(route_name)
);

-- ============================================================================
-- 数据来源说明
-- ============================================================================
CREATE TABLE data_source (
    source_id       INT PRIMARY KEY,
    name            VARCHAR(80) NOT NULL,
    description     TEXT NOT NULL,
    color_hex       VARCHAR(7) NOT NULL,
    url             TEXT NOT NULL
);

-- ============================================================================
-- 索引
-- ============================================================================

-- GiST 空间索引
CREATE INDEX idx_eco_boundary       ON eco_geo_unit    USING GIST (boundary);
CREATE INDEX idx_dish_coord         ON dish            USING GIST (coordinates);
CREATE INDEX idx_dispersal_route    ON dispersal_event USING GIST (route_geom);

-- GIN（JSONB / 数组）索引
CREATE INDEX idx_eco_climate        ON eco_geo_unit    USING GIN (climate);
CREATE INDEX idx_dish_flavor        ON dish            USING GIN (flavor_genotype);
CREATE INDEX idx_ingredient_tag     ON ingredient      USING GIN (flavor_tags);

-- B-Tree 索引
CREATE INDEX idx_eco_code           ON eco_geo_unit    (eco_code);
CREATE INDEX idx_dish_eco           ON dish            (eco_name);
CREATE INDEX idx_dish_city          ON dish            (city_name);
CREATE INDEX idx_dish_name          ON dish            (dish_name);
CREATE INDEX idx_dispersal_ing      ON dispersal_event (ingredient_id);
CREATE INDEX idx_dispersal_name     ON dispersal_event (route_name);
CREATE INDEX idx_dispersal_order    ON dispersal_event (display_order);
CREATE INDEX idx_dispersal_from     ON dispersal_event (from_eco_name);
CREATE INDEX idx_dispersal_to       ON dispersal_event (to_eco_name);
CREATE INDEX idx_recipe_ing         ON recipe_link     (ingredient_id);
CREATE INDEX idx_ing_origin_eco     ON ingredient_origin (eco_name);
CREATE INDEX idx_chapter_route      ON chapter         (route_name);
