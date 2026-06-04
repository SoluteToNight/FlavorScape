# TODO: 地图瓦片预切片

## 背景

- GDAL 已确认 `data/extracted/HYP_HR_SR_W_DR_cog.tif` 是 COG GeoTIFF：
  - `LAYOUT=COG`
  - `Block=512x512`
  - 已有 overviews: `10800x5400` 到 `338x169`
- 这表示栅格已经做了 COG 内部块和金字塔优化，但还不是 Web 端可直接读取的 `/z/x/y` 静态瓦片。
- 当前 `/tiles/raster/{z}/{x}/{y}.png` 仍然由 FastAPI + rio-tiler 按请求实时读取 COG、裁剪/重采样并编码 PNG。

## 待办

1. 用 GDAL 从 `HYP_HR_SR_W_DR_cog.tif` 生成 Web 瓦片产物，优先考虑单文件 `MBTiles`，避免散落大量 PNG。
2. 建议输出路径：

```text
data/tiles/hyp.mbtiles
```

3. 推荐先验证 MBTiles 方案：

```powershell
gdal_translate -of MBTILES `
  -co NAME=HYP_HR_SR_W_DR `
  -co TYPE=baselayer `
  -co TILE_FORMAT=PNG `
  -co BLOCKSIZE=256 `
  -co RESAMPLING=BILINEAR `
  data\extracted\HYP_HR_SR_W_DR_cog.tif `
  data\tiles\hyp.mbtiles

gdaladdo -r bilinear data\tiles\hyp.mbtiles 2 4 8 16 32 64 128
```

4. 后端改造方向：
   - `/tiles/raster/{z}/{x}/{y}.png` 优先从 `data/tiles/hyp.mbtiles` 读取 `tile_data`。
   - MBTiles 通常使用 TMS 行号，XYZ 请求需要转换：`tile_row = (1 << z) - 1 - y`。
   - 如果 MBTiles 不存在，再回退到当前 COG + rio-tiler 动态渲染。
   - `/tiles/status` 增加 `raster_source: "mbtiles" | "cog"`，方便确认运行路径。

5. 验证项：
   - `gdalinfo data\tiles\hyp.mbtiles`
   - 随机检查 SQLite 表 `tiles` 是否有目标 zoom 的瓦片。
   - 启动 FastAPI 后访问 `/tiles/status`。
   - 打开 `/map`，确认首屏不再出现多秒级 raster tile。

## 注意

- 不要把 `data/tiles/hyp.mbtiles` 提交进 Git，应该继续作为本地/部署数据产物管理。
- 当前仅创建了空目录 `data/tiles/`，尚未执行切片命令。

---

## 完成状态（2026-06-04）

### ✅ 1. MBTiles 生成
- `gdal_translate` + `gdaladdo` 成功生成 `data/tiles/hyp.mbtiles`（289 MB）
- 瓦片数：5,461（zoom 0–6），COG 回退覆盖 zoom 7–10

### ✅ 2. 后端改造（`backend/config.py` + `backend/routers/tiles.py`）
- 新增 `MBTILES_PATH` 配置
- `_read_mbtiles_sync()` — SQLite 查询，TMS→XYZ 坐标转换
- `_render_tile_sync()` 三级路径：cache hit → MBTiles → COG fallback
- `X-Cache` 头区分来源：`hit` / `mbtiles` / `cog-miss` / `outside` / `error`
- `/tiles/status` 新增 `raster_source` 和 `mbtiles` 字段

### ✅ 3. Git 管理
- `.gitignore` 添加 `data/tiles/`，`hyp.mbtiles` 不会进入版本控制

### ✅ 4. 验证
- `/tiles/status` → `raster_source: "mbtiles"`
- z=0,3,6 瓦片 → `X-Cache: mbtiles`，返回正常 PNG（67–89 KB）
- z=8 瓦片 → `X-Cache: cog-miss`，COG 回退正常
- 重复请求 → `X-Cache: hit`，缓存命中正常
