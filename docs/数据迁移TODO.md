# 数据迁移 TODO

> 状态：仅记录，不实施  
> 目的：保留后续可迁移项，避免和当前已完成的 `app_data -> DB` 迁移混淆

## 已完成

- `flavor_genotype` 运行时改为从数据库读取
- `dispersal_event` 运行时改为从数据库读取
- `chapter` 运行时改为从数据库读取
- `data_source` 运行时改为从数据库读取
- JSON 导入脚本已支持四个实体文件导入，关系表自动构建

## 暂不做，但建议后续评估

### 1. 生态区气候数据入库

- 当前状态：
  `MapInspector` 中生态区气候图仍为前端模拟数据
- 后续可做：
  将真实气候月序列写入 `eco_geo_unit.climate`
  或拆为独立的生态区气候表
- 影响位置：
  [src/components/MapInspector.vue](</E:/大学/大三下/GIS开发/Food/src/components/MapInspector.vue>)

### 2. 路线详情文案入库

- 当前状态：
  路线详情说明仍是前端通用文案模板
- 后续可做：
  给 `dispersal_event` 增加 `summary`、`description`、`source_excerpt`、`period_label` 等字段
- 影响位置：
  [src/components/MapInspector.vue](</E:/大学/大三下/GIS开发/Food/src/components/MapInspector.vue>)

### 3. 首页内容配置化

- 当前状态：
  首页主文案、ticker、背景路径定义都写死在前端
- 后续可做：
  新建首页内容表或配置表，把文案和 ticker 入库
- 影响位置：
  [src/views/HomeView.vue](</E:/大学/大三下/GIS开发/Food/src/views/HomeView.vue>)

### 4. 导入规则映射表化

- 当前状态：
  以下规则仍在后端代码中硬编码：
  - `INGREDIENT_TYPE_MAP`
  - `ROUTE_INGREDIENT_MAP`
  - `BIOME_MAP`
  - `ECO_NAME_CN`
  - `ECO_CN_MAP`
- 后续可做：
  迁为数据库字典表或独立配置文件
- 影响位置：
  [backend/db/seed.py](</E:/大学/大三下/GIS开发/Food/backend/db/seed.py>)

### 5. 叙事章节扩展元数据

- 当前状态：
  `chapter` 已入库，但字段仍偏轻
- 后续可做：
  增加 `display_order`、`cover_center`、`cover_zoom`、`hero_route_segment` 等展示字段
- 影响位置：
  [src/views/NarrativeView.vue](</E:/大学/大三下/GIS开发/Food/src/views/NarrativeView.vue>)

### 6. 导航与页面文案配置化

- 当前状态：
  顶部导航名称和顺序仍写死在前端
- 后续可做：
  迁为配置表或页面内容表
- 影响位置：
  [src/components/Navbar.vue](</E:/大学/大三下/GIS开发/Food/src/components/Navbar.vue>)

### 7. 基因库分类动态化

- 当前状态：
  `LibraryView` 的分类项仍为前端常量
- 后续可做：
  从数据库实际分类动态生成
  或维护独立分类表
- 影响位置：
  [src/views/LibraryView.vue](</E:/大学/大三下/GIS开发/Food/src/views/LibraryView.vue>)

## 明确不建议优先迁移

以下更偏前端视觉配置，暂不建议优先放进数据库：

- 地图样式 `MAP_STYLE`
- 图层图例 `layerLegend`
- 图层开关 `layerToggles`
- 首页粒子背景 `pathDefs`
- 生态区颜色 `biomePalette`

这些更适合留在前端，或者以后抽成配置文件，而不是数据库表。
