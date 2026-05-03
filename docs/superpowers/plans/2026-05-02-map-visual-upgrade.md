# 地图页视觉升级 v1 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把地图页调色板提纯到"高明度高纯度"，让光斑/暗线/节点的视觉刺透力增强；同时让 L2 传播路径按 type 区分"越洋虚线 / 陆路实线"。

**Architecture:** 改动全部集中在前端样式与 Deck.gl 图层属性 + 后端 `app_data.py` 硬编码颜色同步。新增 `@deck.gl/extensions`（与 deck.gl 主包同版）以引入 `PathStyleExtension` 实现 dash。

**Tech Stack:** Vue 3 · MapLibre GL JS · Deck.gl 9.x（+ extensions）· FastAPI · Vite

**约束**：
- 项目非 git 仓库，所有任务的"commit"步骤略过；以"目视验收"代替单元测试。
- 启动方式：`.\start.ps1`（PowerShell）或 `bash start.sh`，前端默认 5173 端口、后端 8001 端口。
- 任何任务的"运行 / 验证"步骤都假设两端服务已在跑；如未跑请先启动。

**对应 spec：** `docs/superpowers/specs/2026-05-02-map-visual-upgrade-design.md`

---

## Task 1: 安装 @deck.gl/extensions 依赖

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\package.json`

- [ ] **Step 1: 检查现有 deck.gl 版本作为对齐参考**

```bash
grep -E "@deck.gl" "E:/大学/大三下/GIS开发/Food/package.json"
```

预期输出包含 `"@deck.gl/core": "^9.0.10"` 等四行；记下版本号 `^9.0.10`。

- [ ] **Step 2: 安装 extensions 依赖（与主包同版）**

```bash
cd "E:/大学/大三下/GIS开发/Food" && npm install @deck.gl/extensions@^9.0.10
```

预期：`package.json` 的 dependencies 中新增一行 `"@deck.gl/extensions": "^9.0.10"`，`node_modules/@deck.gl/extensions` 目录存在。

- [ ] **Step 3: 验证可正常 import**

```bash
node -e "console.log(Object.keys(require('@deck.gl/extensions')))" 2>&1 | head -3
```

预期输出包含 `PathStyleExtension`、`Fp64Extension`、`BrushingExtension` 等导出名。

---

## Task 2: 升级 CSS 变量与 keyframe（global.css）

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\src\styles\global.css`

- [ ] **Step 1: 替换 `:root` 中 4 个主色变量**

定位 `src/styles/global.css:8-13`，将原 6 行：

```css
  --amber: #C8960F;
  --amber-soft: rgba(200, 150, 15, 0.12);
  --carmine: #C84B4B;
  --carmine-soft: rgba(200, 75, 75, 0.12);
  --turquoise: #2BB89C;
  --turq-soft: rgba(43, 184, 156, 0.12);
```

改为：

```css
  --amber: #E8A917;
  --amber-soft: rgba(232, 169, 23, 0.12);
  --carmine: #E5394E;
  --carmine-soft: rgba(229, 57, 78, 0.12);
  --turquoise: #0FB89A;
  --turq-soft: rgba(15, 184, 154, 0.12);
```

- [ ] **Step 2: 替换 `--sage`**

定位 `src/styles/global.css:14`：

```css
  --sage: #7B9E5A;
```

改为：

```css
  --sage: #7FA961;
```

- [ ] **Step 3: 同步 `breathe` keyframe 中的 RGB**

定位 `src/styles/global.css:73-76`：

```css
@keyframes breathe {
  0%, 100% { box-shadow: 0 0 0 0 rgba(200, 150, 15, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(200, 150, 15, 0); }
}
```

改为：

```css
@keyframes breathe {
  0%, 100% { box-shadow: 0 0 0 0 rgba(232, 169, 23, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(232, 169, 23, 0); }
}
```

- [ ] **Step 4: 目视验证**

刷新浏览器（Vite 热更新即可），打开地图页，确认：

- 左侧"图层"面板的"流光粒子"和"风味节点"两个色块色相比改前更亮、更纯
- 顶部 navbar 上凡是用了 `var(--amber)` / `var(--carmine)` / `var(--turquoise)` 的 chip 色相同步变更
- 加载提示中的 `loading-dot` 呼吸动画颜色变成新琥珀

---

## Task 3: 后端业务数据色同步刷新

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\backend\data\app_data.py`

- [ ] **Step 1: 替换 FLAVORS 中的旧 hex**

逐条替换以下出现处（搜索 + 全字段替换）：

| 旧 | 新 |
|---|---|
| `"#C84B4B"` | `"#E5394E"` |
| `"#2BB89C"` | `"#0FB89A"` |
| `"#C8960F"` | `"#E8A917"` |
| `"#7B9E5A"` | `"#7FA961"` |

`"#8B6A3E"`（北京）保留不动。

- [ ] **Step 2: 重启后端，使内存数据生效**

后端在 startup lifespan 加载 `app_data.py` 的常量。代码改动需要重启 uvicorn。`start.ps1` 启动时已加 `--reload`，保存即重启。

- [ ] **Step 3: 验证 API 返回新色**

```bash
curl -s http://localhost:8001/api/flavors | grep -E '"color"' | sort -u
```

预期：仅出现 `"color": "#E5394E"`、`"color": "#0FB89A"`、`"color": "#E8A917"`、`"color": "#7FA961"`、`"color": "#8B6A3E"` 五种；不再出现任何旧 hex。

```bash
curl -s http://localhost:8001/api/routes | grep -E '"color"' | sort -u
```

预期：仅出现 `"color": "#E8A917"`、`"color": "#0FB89A"`、`"color": "#E5394E"`、`"color": "#7FA961"` 四种。

- [ ] **Step 4: 目视验证**

刷新地图页，确认：

- 风味节点圆色变成新色（成都/潮汕/顺德/杭州 应明显更亮）
- 流光粒子色随路径色更新（丝路琥珀更亮、辣椒胭脂更跳脱、海上香料松石更清）

---

## Task 4: Deck.gl 透明度提升（MapView.vue）

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\src\views\MapView.vue`

- [ ] **Step 1: 提升 PathLayer 暗线 α**

定位 `src/views/MapView.vue:116`：

```js
      getColor: d => hexToRgb(d.color, 55),
```

改为：

```js
      getColor: d => hexToRgb(d.color, 90),
```

- [ ] **Step 2: 提升 TripsLayer opacity**

定位 `src/views/MapView.vue:133`：

```js
      opacity: 0.92,
```

改为：

```js
      opacity: 1.0,
```

- [ ] **Step 3: 提升 buildTripData 中流光颜色 α**

定位 `src/views/MapView.vue:103`：

```js
        color: hexToRgb(route.color, 220),
```

改为：

```js
        color: hexToRgb(route.color, 250),
```

- [ ] **Step 4: 提升 ScatterplotLayer 节点 α、描边、线宽**

定位 `src/views/MapView.vue:145-148`：

```js
      getFillColor: d => hexToRgb(d.color, 200),
      getLineColor: [248, 244, 239, 240],
      lineWidthMinPixels: 1.5,
      stroked: true,
```

改为：

```js
      getFillColor: d => hexToRgb(d.color, 240),
      getLineColor: [255, 253, 250, 255],
      lineWidthMinPixels: 2,
      stroked: true,
```

- [ ] **Step 5: 目视验证**

热更新后查看：

- 静止状态下，所有 5 条传播路径的暗线（不亮的灰色细线）从"几乎看不见"变成"明确可辨但仍属低层蛰伏"
- 流光粒子在暗背景下亮度提升，但颜色不糊
- 节点圆边缘（白色描边）更清晰，与底图分离感更强

---

## Task 5: 矢量底图色微调（MapView.vue）

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\src\views\MapView.vue`

- [ ] **Step 1: 替换 coastline / rivers / ecoregions 三层 paint**

定位 `src/views/MapView.vue:172-191`，将原三段 layer 配置：

```js
    {
      id: 'coastline',
      url: '/tiles/vector/coastline',
      type: 'line',
      paint: { 'line-color': '#9E8870', 'line-width': 0.6, 'line-opacity': 0.5 },
    },
    {
      id: 'rivers',
      url: '/tiles/vector/rivers',
      type: 'line',
      paint: { 'line-color': '#7AAEC0', 'line-width': 0.4, 'line-opacity': 0.45 },
    },
    // L1 — WWF TEOW ecoregions (fill-transparent, line only)
    {
      id: 'ecoregions',
      url: '/tiles/vector/ecoregions',
      type: 'line',
      paint: { 'line-color': '#7A5530', 'line-width': 1.2, 'line-opacity': 0.55 },
    },
```

改为：

```js
    {
      id: 'coastline',
      url: '/tiles/vector/coastline',
      type: 'line',
      paint: { 'line-color': '#8A7560', 'line-width': 0.6, 'line-opacity': 0.65 },
    },
    {
      id: 'rivers',
      url: '/tiles/vector/rivers',
      type: 'line',
      paint: { 'line-color': '#5BA0B8', 'line-width': 0.4, 'line-opacity': 0.6 },
    },
    // L1 — WWF TEOW ecoregions (fill-transparent, line only)
    {
      id: 'ecoregions',
      url: '/tiles/vector/ecoregions',
      type: 'line',
      paint: { 'line-color': '#6B4825', 'line-width': 1.2, 'line-opacity': 0.7 },
    },
```

- [ ] **Step 2: 目视验证**

热更新后查看：

- 海岸线整体更清晰，但仍属"低饱和暖灰"，不抢眼
- 河流（长江/黄河/亚马逊等）颜色更"水蓝"，能在底图上看清主干
- 生态区边界（褐色细线）更易识别，便于点击

---

## Task 6: L2 海陆虚实线区分（PathStyleExtension）

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\src\views\MapView.vue`

- [ ] **Step 1: 引入 PathStyleExtension**

定位 `src/views/MapView.vue:42`，原 import 块：

```js
import { PathLayer, ScatterplotLayer } from '@deck.gl/layers'
import { TripsLayer } from '@deck.gl/geo-layers'
```

下方加一行：

```js
import { PathLayer, ScatterplotLayer } from '@deck.gl/layers'
import { TripsLayer } from '@deck.gl/geo-layers'
import { PathStyleExtension } from '@deck.gl/extensions'
```

- [ ] **Step 2: 在 PathLayer 上加 dash props**

定位 `src/views/MapView.vue:112-126`（PathLayer 配置块），在 `onClick` 行之前、`onHover` 行之后插入三个新属性。最终该 PathLayer 配置应为：

```js
    new PathLayer({
      id: 'path-layer',
      data: routeList,
      getPath: d => d.path,
      getColor: d => hexToRgb(d.color, 90),
      getWidth: 1,
      widthUnits: 'pixels',
      pickable: true,
      extensions: [new PathStyleExtension({ dash: true })],
      getDashArray: d => d.type === 'sea' ? [6, 3] : [0, 0],
      dashJustified: true,
      onHover: ({ object, x, y }) => {
        tooltip.value = object
          ? { visible: true, x: x + 14, y: y - 8, text: object.name }
          : { ...tooltip.value, visible: false }
      },
      onClick: ({ object }) => { if (object) appStore.selectRoute(object) },
    }),
```

dash 单位与 `widthUnits: 'pixels'` 对齐，故 `[6, 3]` 即 6 像素实段 + 3 像素空段。

- [ ] **Step 3: 目视验证**

热更新后查看 5 条路径的暗线（先暂停在地图静止状态、不要让流光遮住判断）：

| 路径 | type | 期望 |
|---|---|---|
| 丝绸之路 | land | 实线 |
| 海上香料之路 | sea | 虚线 |
| 辣椒传播路线 | sea | 虚线 |
| 大运河·茶叶北行 | land | 实线 |
| 香料群岛东传 | sea | 虚线 |

如果 sea 路线仍是实线，常见原因：(a) `@deck.gl/extensions` 没装（回 Task 1），(b) `getDashArray` 语法写错或 `extensions` 写成数组外，(c) 浏览器缓存（强刷 Ctrl+Shift+R）。

- [ ] **Step 4: 验证已有交互未受影响**

测试：

- 鼠标悬停一条路径暗线 → tooltip 显示路径 name
- 点击一条路径暗线 → 右侧 Inspector 切到"传播路径"面板
- 鼠标悬停 / 点击 节点 → tooltip 与 Inspector 节点面板正常
- 点击生态区边界 → Inspector 切到"L1 自然生态档案"

---

## Task 7: 左侧图层图例拆"陆路 / 越洋"两行

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\src\views\MapView.vue`

- [ ] **Step 1: 替换 layerLegend 中"传播路径"一行为两行**

定位 `src/views/MapView.vue:268-276`，将原 `layerLegend` 数组中的：

```js
  { label: '传播路径',          style: { width: '20px', height: '1px', background: '#C8960F', display: 'inline-block', opacity: 0.7 } },
```

改为两行：

```js
  { label: '陆路传播',          style: { width: '20px', height: '1px', background: 'var(--amber)', display: 'inline-block', opacity: 0.85 } },
  { label: '越洋传播',          style: { width: '20px', height: '0', display: 'inline-block', borderTop: '1px dashed var(--amber)', opacity: 0.85 } },
```

注意：原"传播路径"行下方还有"流光粒子"和"风味节点"两行，保持不动。

- [ ] **Step 2: 目视验证**

刷新地图页，左侧"图层"面板从原 7 行变成 8 行：

```
HYP 自然地形底图   [渐变色块]
海岸线             [深米色细线]
主干水系           [蓝色细线]
L1 生态区边界      [褐色细线]
陆路传播           [琥珀实线]      ← 新
越洋传播           [琥珀虚线]      ← 新
流光粒子           [琥珀光点]
风味节点           [胭脂光点]
```

确认实线 / 虚线样本视觉上能区分（虚线段隔较细，但能看出间断）。

---

## Task 8: 端到端验收

**Files:** （无文件修改）

- [ ] **Step 1: 启动两端服务（如未启动）**

```powershell
.\start.ps1
```

打开浏览器 `http://localhost:5173`，等待 `/tiles/status` 返回 `raster_ready: true`、地图栅格底图加载完成。

- [ ] **Step 2: 对照 spec 验收清单逐项确认**

参考 `docs/superpowers/specs/2026-05-02-map-visual-upgrade-design.md` 的"测试与验收"段：

- [ ] 三色光斑（琥珀 / 胭脂 / 松石）在浅米白底图上"刺透感"明显高于改前
- [ ] 节点圆边缘清晰，与底图分离感更强
- [ ] 暗线在地图静止状态下可见，但仍属"低层蛰伏"而非抢眼
- [ ] 三条 sea 路径（海上香料之路、辣椒传播路线、香料群岛东传）暗线呈虚线
- [ ] 两条 land 路径（丝绸之路、大运河·茶叶北行）暗线呈实线
- [ ] 左侧图例正确呈现"陆路传播"实线样本与"越洋传播"虚线样本
- [ ] 已有交互（点击节点 → flyTo + Inspector、点击生态区 → Inspector、悬停 tooltip）不受影响

- [ ] **Step 3: 浏览器控制台检查无 error / warning**

打开 DevTools Console，刷新页面，无下列报错：
- `Module not found: @deck.gl/extensions`
- `PathStyleExtension is not a constructor`
- `Cannot read property 'type' of undefined`（可能是路径数据结构问题）

如有报错，回到对应 Task 排查。
