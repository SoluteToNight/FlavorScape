# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**寻味地理** — 前后端分离的 WebGIS 应用，以博物志风格可视化中国饮食文化的地理分布与历史传播路径。

- **前端**: Vue 3 + Vite + TailwindCSS，MapLibre GL JS + Deck.gl 地图渲染，ECharts 图表
- **后端**: FastAPI（Python），提供栅格瓦片、MVT 矢量瓦片、GeoJSON 和业务数据
- **数据库**: PostgreSQL + PostGIS，存储生态区、食材、风味节点、传播路径等
- **地图数据**: Natural Earth HYP 栅格底图 + WWF TEOW 生态区矢量边界

---

## 启动命令

### 推荐：一键启动
```powershell
.\start.ps1        # Windows PowerShell — 弹出两个子窗口分别运行前后端
```
```bash
bash start.sh      # Bash — 后端后台运行（日志写入 .backend.log），前端前台运行
```
自动创建 `.venv`、安装依赖、清理端口冲突，等待后端 `/health` 就绪（最长 300s）后启动前端。

### 手动分步启动
```bash
# 后端 — 推荐方式（run_server.py 在导入前设置 PROJ_LIB，避免 PROJ 冲突）
.venv/Scripts/python.exe run_server.py

# 后端 — 备选方式（直接 uvicorn，需依赖 backend/main.py 内的 PROJ_LIB 修复）
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload

# 前端 (Vite dev, port 5173) — 另一个终端
npm run dev
```

`start.ps1` 优先使用 `run_server.py`（若存在），其次回退到 `uvicorn` 命令。

### 构建 & 生产
```bash
npm run build       # 输出到 dist/
npm run start       # Express 在 :3001 托管 dist/ 并代理 /api/* /tiles/* 到 FastAPI :8001
```

### 数据库初始化
```bash
# 确保 .env 中 DATABASE_URL 指向 PostGIS 数据库，然后：
.venv/Scripts/python.exe -m backend.db.run_migration
```

### 检查状态
```bash
curl http://localhost:8001/health          # 后端健康 + 栅格就绪 + 矢量图层列表
curl http://localhost:8001/tiles/status    # 图层列表 + 缓存命中率
curl http://localhost:8001/docs            # Swagger API 文档
```

### 工具脚本

`tools/generate_design_figures.py` — 设计图表生成脚本。`backend/db/import_json.py` — 将 JSON 数据包导入 PostgreSQL 的 CLI 工具。

---

## 架构

### 通信方式

```
开发:  Browser → Vite :5173 → proxy /api/*,/tiles/* → FastAPI :8001
生产:  Browser → Express :3001 → proxy /api/*,/tiles/* → FastAPI :8001
                                   ↓ 托管 dist/ 静态文件
```

- Vite 开发代理配置在 `vite.config.js`，Express 生产代理在 `server.js`
- 两种模式下 `/api/*` 和 `/tiles/*` 都会被代理到 FastAPI :8001
- 后端 CORS 白名单：`:5173`（Vite dev）、`:3001`（Express）、`:4173`（Vite preview）

### 端口一览

| 端口 | 用途 |
|------|------|
| 8001 | FastAPI 后端 |
| 5173 | Vite 开发服务器 |
| 3001 | Express 生产服务器 |
| 4173 | Vite preview |
| 5432 | PostgreSQL |

> **注意**: `backend/main.py` 文档字符串中写的是 port 8000（已过时），实际端口由 `backend/config.py` 控制为 8001。

### 后端启动流程（`backend/startup.py` + `backend/main.py`）

FastAPI `lifespan` 在线程池中同步执行 `run_startup()`：

1. **PROJ_LIB 修复**：强制 rasterio 使用自有 PROJ 数据，避免与 PostgreSQL 16 的旧 proj.db 冲突
2. **解压栅格**：`data/HYP_HR_SR_W_DR.zip` → `data/extracted/HYP_HR_SR_W_DR.tif`（700 MB，首次约需 1–2 分钟，已存在则跳过）
3. **解压矢量**：`ne_10m_coastline.shp`、`ne_10m_rivers_lake_centerlines.shp`、`ne_10m_land.shp` 从 `10m_physical.zip` 按需解压
4. **加载矢量到内存**：用 Fiona + Shapely 读取并简化，存入 `vector_data` 全局字典
5. **生态区**：优先读 `wwf_terr_ecos_wgs84.shp`（预重投影版本）；若不存在则从 ZIP 提取原版并动态转换
6. **PostgreSQL 连接池**：`init_pool()` 打开 ThreadedConnectionPool（min=1, max=4）
7. **加载生态区到数据库缓存**：`load_ecoregions_from_db()`

> **关键**: 服务器只有在 `run_startup()` 完全结束后才开始接受请求。

### 数据库架构（PostgreSQL + PostGIS）

9 张核心表（见 `backend/db/schema.sql`）：

| 表 | 说明 |
|----|------|
| `eco_geo_unit` | WWF TEOW 827 个生态区（geometry + BIOME/REALM_1/area_km2 属性） |
| `ingredient` | 食材（名称、类型、图片 URL） |
| `ingredient_origin` | 食材发源地（点几何） |
| `dish` | 17 个风味节点（点几何 + 风味评分 JSONB） |
| `dispersal_event` | 5 条传播路径（LineString + 时间范围、距离、速度） |
| `recipe_link` | 节点间关联 |
| `dish_lineage` | 风味谱系 |
| `chapter` | 5 个叙事章节 |
| `data_source` | 4 个数据来源 |

`backend/db/query.py` 查询数据库并与 `backend/data/app_data.py` 中的硬编码 UI 元数据合并。**注意**：dish 名称是 join key，改名会破坏数据关联；route 按 `dispersal_event` 顺序匹配 `app_data.ROUTES`，重排序会错配名称/颜色/类型。

数据库迁移和种子数据通过 `backend/db/run_migration.py` 执行，`backend/db/seed.py` 导入 827 个 TEOW 生态区行。`backend/data/biome_names.py` 定义 14 个 WWF 生物群落的中英文名称映射，被 `startup.py`（显示）和 `seed.py`（入库）共享使用。

### 测试

`package.json` 中未配置 lint/test 脚本。主要的质量检查手段：

```bash
npm run build                                # 前端构建检查
curl http://localhost:8001/health            # 后端健康检查
curl http://localhost:8001/tiles/status      # 瓦片缓存状态
```

**Playwright E2E**：`dev/spread-interactions.spec.js` — 针对 `/spread` 食材传播页面的端到端测试。覆盖侧边栏开关、食材卡片选择、时间线交互、地图缩放/拖拽、marker 点击。截图输出到 `dev/screenshots/`。

### 后端 API 路由

| 端点 | 文件 | 说明 |
|------|------|------|
| `/api/flavors` `/api/routes` `/api/chapters` `/api/data-sources` | `routers/api.py` | 业务数据（DB 查询 + app_data 元数据合并） |
| `/api/search?q=` | `routers/api.py` | 模糊匹配节点和路线 |
| `/api/auth/register` `/api/auth/login` `/api/auth/me` | `routers/auth.py` | JWT 认证（bcrypt 密码哈希，24h 过期） |
| `/api/ingredients/spread` `/api/ingredients/spread/{id}` `/api/ingredients/spread/{id}/path` | `routers/ingredient_spread.py` | 食材传播数据（从 `data/ingredient/*.json` 读取，线程安全缓存） |
| `/tiles/raster/{z}/{x}/{y}.png` | `routers/tiles.py` | rio-tiler COG 瓦片，LRU 缓存 512 条 |
| `/tiles/mvt/{z}/{x}/{y}.pbf` | `routers/tiles.py` | PostGIS MVT 矢量瓦片（ST_AsMVT） |
| `/tiles/vector/{layer}` | `routers/tiles.py` | 返回内存中的 GeoJSON FeatureCollection |
| `/tiles/status` | `routers/tiles.py` | 栅格就绪状态 + 缓存统计 |

### 前端应用壳（`src/App.vue` + `src/main.js`）

```
main.js: createApp → Pinia → Router → global.css → mount('#app')
App.vue: Navbar (固定顶部) + <RouterView> (page transition 动画)
         └─ onMounted: authStore.init() 从 localStorage 恢复登录态
```

- **Navbar**（`src/components/Navbar.vue`）：顶部导航栏，包含 logo、6 个中心导航链接、OmniSearch 搜索框（带 API 自动补全下拉）、认证区域（未登录显示登录按钮，已登录显示用户菜单）。毛玻璃 backdrop-filter 效果。
- **NavDot**（`src/components/NavDot.vue`）：左下角浮动径向菜单，hover 展开 5 个导航项（首页、地图、图库、叙事、关于）。独立于 Navbar。
- **MapInspector**（`src/components/MapInspector.vue`）：右侧可折叠详情面板，根据 Pinia 选中类型切换展示：风味节点（FlavorRadar 雷达图 + 描述 + 食材标签 + 同族菜品）、生态区（气候图表 + 生物群落徽章）、传播路径（路线详情）。
- **FlavorRadar**（`src/components/FlavorRadar.vue`）：可复用 ECharts 雷达图组件，接收 scores/color/size/animated props。

### 静态资源

| 目录 | 内容 |
|------|------|
| `public/geo/coastline-110m.geojson` | 简化海岸线 GeoJSON，供 HomeView 粒子画布使用（独立于后端矢量数据） |
| `public/ingredients/` | 食材装饰图片（chili, star-anise, tea, rice, sichuan-pepper 及 realistic 变体），用于登录/注册页等装饰 |
| `data/ingredient/*.json` | 4 个食材传播 JSON（pepper, rice, star_anise, tea），结构含 timeline 事件数组（年份、朝代、坐标、历史名称、来源文献、事件类型） |
| `data/extracted/` | 解压后的栅格 TIF 和矢量 SHP 文件（gitignored，首次启动自动生成） |

### 前端路由 & 视图

| 路径 | 名称 | 视图 | 认证 |
|------|------|------|------|
| `/` | home | HomeView — 粒子画布 + SVG 装饰的着陆页 | 否 |
| `/brand` | brand | GeoAtlasView — 智慧大屏，Maplibre 3D + HUD + 自动巡游 | 否 |
| `/marketing` | marketing | MarketingView — 海报生成器，html2canvas 导出 | 否 |
| `/archive` | archive | ArchiveView — 科学溯源白皮书，3 列仪表盘 | 否 |
| `/map` | map | MapView — 主交互地图，Deck.gl 图层 | 否 |
| `/library` | library | LibraryView — 风味基因库（卡片网格 + ECharts 雷达图） | 否 |
| `/narrative` | narrative | NarrativeView — 叙事时间线 | 否 |
| `/spread` | spread | IngredientSpreadView — 食材传播时间线地图 | 否 |
| `/about` | about | AboutView — 数据来源页 | 否 |
| `/login` | login | LoginView | 否（已登录重定向到 /profile） |
| `/register` | register | RegisterView | 否（已登录重定向到 /profile） |
| `/profile` | profile | ProfileView — 用户中心 | **是**（未登录重定向到 /login） |

Vue Router 全局导航守卫（`src/router/index.js`）：`requiresAuth` meta 字段控制认证；已登录用户访问 login/register 自动跳转 profile。

### 地图图层结构（`src/views/MapView.vue`）

```
底层 ────────────────────────────────────────────── 顶层
  MapLibre: bg → hyp(栅格) → coastline → rivers → ecoregions
                                                      ↑
                                              Deck.gl MapboxOverlay (interleaved)
                                              PathLayer + TripsLayer + ScatterplotLayer
```

| 图层 | 来源 | 类型 |
|------|------|------|
| HYP 栅格底图 | `/tiles/raster/{z}/{x}/{y}.png` | MapLibre raster source |
| 海岸线/河流/陆地 | `/tiles/vector/{layer}` GeoJSON | MapLibre geojson source |
| L1 生态区边界 | `/tiles/vector/ecoregions` GeoJSON | MapLibre geojson source，click → `selectEcozone()` |
| 传播路径暗线 | `PathLayer` | Deck.gl，pickable |
| 流光粒子 | `TripsLayer` | Deck.gl，`currentTime` 以 1/frame 步进，LOOP=1800 |
| 风味节点 | `ScatterplotLayer` | Deck.gl，click → `selectNode()` + `map.flyTo()` |

`TripsLayer` 每条路线生成 3 个错峰粒子（startOffset 间距 = LOOP_LENGTH / 3），trailLength = 180。

### 状态管理（Pinia）

**`src/stores/app.js`**（`useAppStore`）：
- 三种互斥的地图选中状态：`selectedNode` / `selectedRoute` / `selectedEcozone`，选中任一会清除其他两个
- `MapInspector.vue` 根据当前选中类型切换展示面板
- `watch(selectedNode)` 触发 `map.flyTo()`
- 图层可见性控制（L0-L3）、L1 强调模式、食材时间线年份

**`src/stores/auth.js`**（`useAuthStore`，Composition API 风格）：
- `user` / `token` / `loading` refs，`isLoggedIn` computed
- `init()`: 从 localStorage 恢复 token，调 `/api/auth/me` 验证
- `login()` / `register()`: 调 auth API，持久化 token 到 localStorage
- `logout()`: 清除 token 和 user 状态

### TailwindCSS + 设计系统

- `tailwind.config.js` 定义完整设计令牌（颜色、阴影、圆角、字体、字号、间距、过渡）
- `src/styles/global.css` 包含 Tailwind 指令 + CSS 自定义属性（**与 tailwind.config 双端维护，修改时需同步更新**）
- `preflight: false` — 不禁用浏览器默认样式
- 字体：Noto Sans SC / Noto Serif SC / Inter（Google Fonts，`index.html` 中加载）
- 各 Vue 组件的 `<style scoped>` 中对无法用 Tailwind 表达的效果（多重径向渐变、mask-image、`color-mix()`、动态 CSS 变量、SVG 属性、伪元素、复杂阴影、关键帧动画）保留了原生 CSS

### 认证系统

- **JWT**：HS256，24h 过期，密钥通过 `.env` 的 `JWT_SECRET` 配置
- **密码哈希**：bcrypt（`backend/routers/auth.py`）
- **前端**：`src/utils/api.js` 封装 fetch，自动注入 `Authorization: Bearer <token>` 头
- **后端依赖注入**：`backend/auth_deps.py` 的 `get_current_user` 解码 JWT 并查询数据库
- `.env.example` 提供模板；`.env` 已被 `.gitignore` 排除

### 食材传播数据

`data/ingredient/` 目录包含 4 个 JSON 文件：`pepper.json`、`rice.json`、`star_anise.json`、`tea.json`。后端 `routers/ingredient_spread.py` 使用线程安全缓存 + 文件签名监控，文件变更时自动重载。

### 空间聚类（`src/utils/clustering.js`）

Haversine 距离 + Union-Find（DSU）+ 球面质心计算。缩放相关阈值：zoom < 3.4 → 800km，3.4–4.15 → 400km，> 4.15 → 不聚类。透明度按距离插值。

---

## 重要约束

**坐标系**：所有矢量数据必须是 EPSG:4326（WGS84 度数）。TEOW 原始 shapefile 是 EPSG:3857（米），已永久重投影为 `data/extracted/wwf_terr_ecos_wgs84.shp`（65 MB）。若该文件不存在，后端会自动转换，但会增加约 12 秒启动时间。

**端口**：后端固定 **8001**（`backend/config.py` 中 `PORT = 8001`）。8000 在部分 Windows 系统上因权限策略被拒（WinError 10013）。

**rio-tiler 版本**：已升至 9.x，使用 `from rio_tiler.io import Reader`（不是旧版 `COGReader`）。

**MapLibre `addLayer` 第二参数**：`map.addLayer(spec, beforeId)` 是将新层插到 `beforeId` **之前**（渲染顺序更低）。矢量层不应传 `'hyp'` 作为 beforeId，否则会被栅格层覆盖不可见。

**uv 虚拟环境**：使用 `.venv`（miniconda Python 3.12）。安装依赖时必须指定 `--python .venv/Scripts/python.exe`，否则会落到系统 Python。

**PROJ 库冲突**：PostgreSQL 16 自带旧版 proj.db，与 rasterio 冲突。`backend/main.py` 启动时通过设置 `PROJ_LIB` 环境变量强制 rasterio 使用自有 PROJ 数据解决。

**设计令牌双端维护**：`tailwind.config.js` 和 `src/styles/global.css :root` 定义了相同的 CSS 自定义属性。修改颜色/阴影/圆角等令牌时，**必须同时更新两个文件**。

**产品范围**：桌面端 only。不要设计、实现、审查或截图移动端布局，除非用户明确要求。

**pyproject.toml 版本声明**：`pyproject.toml` 声明 `requires-python = ">=3.14"`，但实际 `.venv` 使用 Python 3.12（miniconda）。不要按 3.14 的语法特性编写代码。

**大型二进制文件**：`data/extracted/` 和 `data/*.zip` 被 gitignore 排除。首次启动时 `backend/startup.py` 自动解压生成。若需在新环境部署，确保 `data/HYP_HR_SR_W_DR.zip` 和 `data/10m_physical.zip` 存在。

---

## Python 依赖管理

```bash
# 安装 / 同步
uv pip install --python .venv/Scripts/python.exe -r backend/requirements.txt --quiet

# 新增依赖
uv pip install --python .venv/Scripts/python.exe <package>
```

推荐用 conda 安装重量级 GIS 依赖以避免 GDAL 编译问题：
```bash
conda install -c conda-forge rasterio fiona shapely
```
