# 寻味地理 · 风味博物志

WebGIS 全栈项目。前端 Vue 3 + MapLibre + Deck.gl，后端 FastAPI + rio-tiler + PostGIS。

## 前置要求

| 工具 | 用途 | 安装 |
|---|---|---|
| **uv** | Python 虚拟环境和依赖管理 | `winget install uv` 或 [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| **Node.js 18+** | 前端构建和开发服务器 | [nodejs.org](https://nodejs.org/) |
| **PostgreSQL + PostGIS** | 空间数据库（搜索、矢量查询） | [postgresql.org](https://www.postgresql.org/) |

## 快速启动

```bash
# Windows（PowerShell）
.\start.ps1

# macOS / Linux / Git Bash
bash start.sh
```

脚本自动完成：创建虚拟环境 → 安装依赖 → 启动后端 → 等待就绪 → 启动前端。

首次启动需解压底图数据（~700MB），最多等待 5 分钟。

启动后访问：
- 前端：http://localhost:5173
- 后端 API 文档：http://localhost:8001/docs

## 手动部署

### 1. 克隆项目

```bash
git clone <repo-url>
cd Food
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填写你的 PostgreSQL 连接信息：

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/Flavor
```

### 3. 准备数据文件

项目依赖三组公开 GIS 数据，需手动下载放入 `data/` 目录。

#### 3a. 底图栅格（~29 MB）

Natural Earth 50m HYP 着色地形：

```bash
# 下载到 data/ 目录
curl -L -o data/HYP_HR_SR_W_DR.zip \
  "https://naciscdn.org/naturalearth/50m/raster/HYP_HR_SR_W_DR.zip"
```

#### 3b. 物理矢量（海岸线 / 河流 / 陆地，~50 MB）

下载三个独立的 Natural Earth 10m 图层，打包为 `10m_physical.zip`：

**PowerShell（推荐）：**

```powershell
mkdir data\tmp -Force

curl -L -o data\tmp\coastline.zip "https://naciscdn.org/naturalearth/10m/physical/ne_10m_coastline.zip"
curl -L -o data\tmp\rivers.zip    "https://naciscdn.org/naturalearth/10m/physical/ne_10m_rivers_lake_centerlines.zip"
curl -L -o data\tmp\land.zip      "https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip"

Expand-Archive data\tmp\coastline.zip data\tmp\coastline
Expand-Archive data\tmp\rivers.zip    data\tmp\rivers
Expand-Archive data\tmp\land.zip      data\tmp\land

# 合并打包
Compress-Archive -Path data\tmp\coastline\*.shp, data\tmp\coastline\*.dbf, data\tmp\coastline\*.shx, data\tmp\coastline\*.prj, data\tmp\coastline\*.cpg, data\tmp\rivers\*.shp, data\tmp\rivers\*.dbf, data\tmp\rivers\*.shx, data\tmp\rivers\*.prj, data\tmp\rivers\*.cpg, data\tmp\land\*.shp, data\tmp\land\*.dbf, data\tmp\land\*.shx, data\tmp\land\*.prj, data\tmp\land\*.cpg -DestinationPath data\10m_physical.zip

Remove-Item data\tmp -Recurse
```

**Bash / macOS / Linux：**

```bash
mkdir -p data/tmp

curl -L -o data/tmp/coastline.zip "https://naciscdn.org/naturalearth/10m/physical/ne_10m_coastline.zip"
curl -L -o data/tmp/rivers.zip    "https://naciscdn.org/naturalearth/10m/physical/ne_10m_rivers_lake_centerlines.zip"
curl -L -o data/tmp/land.zip      "https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip"

unzip -o data/tmp/coastline.zip -d data/tmp/coastline
unzip -o data/tmp/rivers.zip    -d data/tmp/rivers
unzip -o data/tmp/land.zip      -d data/tmp/land

zip -j data/10m_physical.zip \
  data/tmp/coastline/ne_10m_coastline.* \
  data/tmp/rivers/ne_10m_rivers_lake_centerlines.* \
  data/tmp/land/ne_10m_land.*

rm -rf data/tmp
```

#### 3c. 生态区矢量（~480 MB）

WWF 陆地生态区（TEOW）shapefile：

1. 访问 [WWF 发布页](https://www.worldwildlife.org/publications/terrestrial-ecoregions-of-the-world)
2. 下载 "Terrestrial Ecoregions of the World" ZIP 文件
3. 重命名为 `Terrestrial Ecoregions of the World.zip`，放入 `data/`

> 如 WWF 页面无法直接下载，可搜索 `wwf_terr_ecos.shp` 从学术数据仓库获取。ZIP 内需包含 `data/commondata/data0/wwf_terr_ecos.{shp,dbf,shx,prj,cpg}`。

#### 3d. 最终 data/ 目录结构

```
data/
├── HYP_HR_SR_W_DR.zip                    # 底图栅格
├── 10m_physical.zip                      # 海岸线 + 河流 + 陆地矢量
└── Terrestrial Ecoregions of the World.zip  # TEOW 生态区
```

后端首次启动会自动解压并转换为 COG 格式。

### 4. 安装后端依赖

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/Scripts/python.exe -r backend/requirements.txt
```

### 5. 初始化数据库

确保 PostgreSQL 已创建 `Flavor` 数据库并启用 PostGIS 扩展：

```sql
CREATE DATABASE "Flavor";
CREATE EXTENSION postgis;
```

然后运行迁移和种子数据：

```bash
.venv/Scripts/python.exe -m backend.db.run_migration
```

### 6. 安装前端依赖

```bash
npm install
```

### 7. 启动服务

需要同时运行两个进程：

```bash
# 终端 1 — 后端（端口 8001）
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload

# 终端 2 — 前端（Vite :5173 + Express :3001）
npm run dev
```

## 局域网访问

```bash
.\start-lan.ps1
```

将以 `0.0.0.0` 启动服务，同一局域网设备可通过本机 IP 访问。需确保防火墙放行 5173 和 8001 端口。

## 项目结构

```
Food/
├── backend/              # FastAPI 后端
│   ├── main.py           # 应用入口
│   ├── config.py         # 路径和端口配置
│   ├── routers/          # API 路由（瓦片、搜索、数据）
│   ├── db/               # 数据库查询和 schema
│   ├── startup.py        # 启动时加载栅格和矢量数据
│   └── tile_cache.py     # 瓦片缓存（512 条 LRU）
├── src/                  # Vue 3 前端
│   ├── views/            # 页面组件
│   ├── components/       # 通用组件
│   ├── router/           # 路由配置
│   └── stores/           # Pinia 状态管理
├── server.js             # Express 生产服务器（端口 3001）
├── vite.config.js        # Vite 配置（代理 /api、/tiles 到后端）
├── data/                 # GIS 数据（不纳入版本控制）
├── start.ps1 / start.sh  # 一键启动脚本
└── start-lan.ps1         # 局域网启动脚本
```

## 技术栈

| 层 | 技术 |
|---|---|
| 前端框架 | Vue 3 + Pinia + Vue Router |
| 地图 | MapLibre GL JS + Deck.gl |
| 图表 | ECharts |
| 后端框架 | FastAPI |
| 栅格瓦片 | rio-tiler + rasterio（COG 格式） |
| 矢量瓦片 | PostGIS → MVT |
| 数据库 | PostgreSQL + PostGIS |
| 构建工具 | Vite |
| 生产服务器 | Express |
