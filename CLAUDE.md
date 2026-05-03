# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**寻味地理** — 前后端分离的 WebGIS 应用，以博物志风格可视化中国饮食文化的地理分布与历史传播路径。

- **前端**: Vue 3 + Vite，MapLibre GL JS + Deck.gl 地图渲染
- **后端**: FastAPI（Python），提供栅格瓦片、矢量 GeoJSON 和业务数据
- **地图数据**: Natural Earth HYP 栅格底图 + WWF TEOW 生态区矢量边界

---

## 启动命令

### 推荐：一键启动（Windows PowerShell）
```powershell
.\start.ps1
```
自动创建 `.venv`、安装依赖、清理端口冲突，并弹出两个子窗口分别运行前后端。

### 或：Bash（Git Bash / MSYS2）
```bash
bash start.sh
```

### 手动分步启动
```bash
# 后端 (FastAPI, port 8001)
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload

# 前端 (Vite dev, port 5173) — 另一个终端
npm run dev
```

### 构建 & 生产
```bash
npm run build          # 输出到 dist/
NODE_ENV=production node server.js   # 以 Express 静态托管 dist/
```

### 检查后端状态
```bash
curl http://localhost:8001/health
curl http://localhost:8001/tiles/status   # 含图层列表和缓存命中率
```

---

## 架构

### 通信方式
- Vite 开发服务器将 `/api/*` 和 `/tiles/*` 代理至 `http://localhost:8001`（见 `vite.config.js`）
- 生产模式：Express (`server.js`) 托管静态文件，**不**代理 Python 后端——部署时需自行配置反向代理

### 后端启动流程（`backend/startup.py`）

FastAPI `lifespan` 在线程池中同步执行 `run_startup()`：

1. **解压栅格**：`data/HYP_HR_SR_W_DR.zip` → `data/extracted/HYP_HR_SR_W_DR.tif`（700 MB，首次约需 1–2 分钟，已存在则跳过）
2. **解压矢量**：`ne_10m_coastline.shp`、`ne_10m_rivers_lake_centerlines.shp`、`ne_10m_land.shp` 从 `10m_physical.zip` 按需解压
3. **加载矢量到内存**：用 Fiona + Shapely 读取并简化，存入 `vector_data` 全局字典
4. **生态区**：优先读 `wwf_terr_ecos_wgs84.shp`（预重投影版本）；若不存在则从 ZIP 提取原版并动态转换

> **关键**: 服务器只有在 `run_startup()` 完全结束后才开始接受请求。

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

### Pinia Store（`src/stores/app.js`）

三种互斥的地图选中状态：`selectedNode` / `selectedRoute` / `selectedEcozone`。选中任一会清除其他两个。`MapInspector.vue` 根据当前选中类型切换展示面板。`watch(selectedNode)` 触发 `map.flyTo()`。

### 后端 API 路由

| 端点 | 文件 | 说明 |
|------|------|------|
| `/api/flavors` `/api/routes` `/api/chapters` | `routers/api.py` | 硬编码业务数据（`data/app_data.py`） |
| `/api/search?q=` | `routers/api.py` | 模糊匹配节点和路线 |
| `/tiles/raster/{z}/{x}/{y}.png` | `routers/tiles.py` | `rio-tiler.io.Reader` 从 COG TIF 切片，LRU 缓存 512 条 |
| `/tiles/vector/{layer}` | `routers/tiles.py` | 返回内存中的 GeoJSON FeatureCollection |
| `/tiles/status` | `routers/tiles.py` | 栅格就绪状态 + 缓存统计 |

---

## 重要约束

**坐标系**：所有矢量数据必须是 EPSG:4326（WGS84 度数）。TEOW 原始 shapefile 是 EPSG:3857（米），已永久重投影为 `data/extracted/wwf_terr_ecos_wgs84.shp`（65 MB）。若该文件不存在，后端会自动转换，但会增加约 12 秒启动时间。

**端口**：后端固定 **8001**（`backend/config.py` 中 `PORT = 8001`）。8000 在部分 Windows 系统上因权限策略被拒（WinError 10013）。

**rio-tiler 版本**：已升至 9.x，使用 `from rio_tiler.io import Reader`（不是旧版 `COGReader`）。

**MapLibre `addLayer` 第二参数**：`map.addLayer(spec, beforeId)` 是将新层插到 `beforeId` **之前**（渲染顺序更低）。矢量层不应传 `'hyp'` 作为 beforeId，否则会被栅格层覆盖不可见。

**uv 虚拟环境**：使用 `.venv`（miniconda Python 3.12）。安装依赖时必须指定 `--python .venv/Scripts/python.exe`，否则会落到系统 Python。

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
