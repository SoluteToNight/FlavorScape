# 地图页视觉表达升级 v1 设计

**日期**：2026-05-02
**范围**：调色板原色提纯 + L2 海陆传播路径虚实线区分
**对应文档**：`docs/地图页设计.md`

## 背景

地图页（`src/views/MapView.vue` + `src/components/MapInspector.vue`）已实现 L0 栅格底图、L1 生态区线框、L2 PathLayer 暗线、TripsLayer 流光、L3 节点、右侧 Inspector 等基础结构。本轮聚焦两个差距：

1. 当前调色饱和度与不透明度偏低，光斑/暗线/节点的"刺透力"不足。原文档要求"高明度、高纯度的自然提取色"形成"清晰干脆的视觉刺透力"。
2. L2 暗线一视同仁，未按文档区分"虚线表示越洋、实线表示陆路 / 内河"。

呼吸光晕、底部留白、智能搜索台、时序接力等其余差距不在本轮范围。

## 一、原色提纯

### 1.1 CSS 变量（`src/styles/global.css`）

| 变量 | 旧值 | 新值 |
|---|---|---|
| `--amber` | `#C8960F` | `#E8A917` |
| `--carmine` | `#C84B4B` | `#E5394E` |
| `--turquoise` | `#2BB89C` | `#0FB89A` |
| `--sage` | `#7B9E5A` | `#7FA961` |
| `--amber-soft` | `rgba(200, 150, 15, 0.12)` | `rgba(232, 169, 23, 0.12)` |
| `--carmine-soft` | `rgba(200, 75, 75, 0.12)` | `rgba(229, 57, 78, 0.12)` |
| `--turq-soft` | `rgba(43, 184, 156, 0.12)` | `rgba(15, 184, 154, 0.12)` |

`@keyframes breathe` 中 `rgba(200, 150, 15, ...)` 同步替换为 `rgba(232, 169, 23, ...)`。

### 1.2 后端业务数据色（`backend/data/app_data.py`）

`FLAVORS`、`ROUTES`、`DATA_SOURCES` 中下列 hex 全字段替换：

| 旧 | 新 |
|---|---|
| `#C8960F` | `#E8A917` |
| `#C84B4B` | `#E5394E` |
| `#2BB89C` | `#0FB89A` |
| `#7B9E5A` | `#7FA961` |

`#8B6A3E`（北京暗咖）保留不动 —— 与新调色板和谐共存，且作为暖灰色对比已足够。

### 1.3 Deck.gl 透明度提升（`src/views/MapView.vue`）

| 位置 | 旧 | 新 |
|---|---|---|
| `PathLayer.getColor` α | `55` | `90` |
| `TripsLayer.opacity` | `0.92` | `1.0` |
| `buildTripData` 中 `hexToRgb(route.color, 220)` | α `220` | α `250` |
| `ScatterplotLayer.getFillColor` α | `200` | `240` |
| `ScatterplotLayer.getLineColor` | `[248, 244, 239, 240]` | `[255, 253, 250, 255]` |
| `ScatterplotLayer.lineWidthMinPixels` | `1.5` | `2` |

### 1.4 矢量底图色微调（`addVectorLayers` in `MapView.vue`）

| 图层 | 旧 paint | 新 paint |
|---|---|---|
| `coastline` | color `#9E8870`, opacity `0.5` | color `#8A7560`, opacity `0.65` |
| `rivers` | color `#7AAEC0`, opacity `0.45` | color `#5BA0B8`, opacity `0.6` |
| `ecoregions` | color `#7A5530`, opacity `0.55` | color `#6B4825`, opacity `0.7` |

线宽（`line-width`）保持原值不变。

## 二、L2 海陆虚实线区分

### 2.1 新增依赖

`package.json` 增加 `"@deck.gl/extensions": "^9.0.10"`，与现有 deck.gl 主包版本对齐。`npm install`（或 `npm i @deck.gl/extensions`）后落到 `node_modules`。

### 2.2 PathLayer 改造（`src/views/MapView.vue`）

引入扩展并加到 PathLayer 的 `extensions` / `getDashArray` / `dashJustified` 上：

```js
import { PathStyleExtension } from '@deck.gl/extensions'

new PathLayer({
  id: 'path-layer',
  data: routeList,
  getPath: d => d.path,
  getColor: d => hexToRgb(d.color, 90),
  getWidth: 1,
  widthUnits: 'pixels',
  pickable: true,
  // 海陆虚实区分
  extensions: [new PathStyleExtension({ dash: true })],
  getDashArray: d => d.type === 'sea' ? [6, 3] : [0, 0],
  dashJustified: true,
  // ...onHover / onClick 不变
})
```

- 陆路 / 内河（`type !== 'sea'`）：`[0, 0]` 表示连续实线
- 越洋（`type === 'sea'`）：`[6, 3]` —— 6 单位实段 + 3 单位空段。dash 单位与 PathLayer 的 `widthUnits` 对齐，本工程为 `'pixels'`，故 6 / 3 即像素。
- `dashJustified: true` 让端点处虚线段自然对齐

### 2.3 TripsLayer 保持原样

流光层 **不** 区分虚实：虚线 + 动态流光叠加会让画面过碎。`widthMinPixels` 海陆均保持 `2`。流光自身的方向感已足够表达"传播路径"语义。

### 2.4 左侧图层图例（`layerLegend` in `MapView.vue`）

把现有"传播路径"一行拆成两行：

```js
{
  label: '陆路传播',
  style: { width: '20px', height: '1px', background: 'var(--amber)', display: 'inline-block', opacity: 0.7 }
},
{
  label: '越洋传播',
  style: { width: '20px', height: '0', display: 'inline-block', borderTop: '1px dashed var(--amber)', opacity: 0.85 }
},
```

颜色样本统一用 `var(--amber)`（已是新色 `#E8A917`），与具体路径色解耦。

## 改动清单

| 文件 | 变更 |
|---|---|
| `src/styles/global.css` | 4 个色相变量 + 3 个 *-soft 变量 + breathe keyframe RGB |
| `backend/data/app_data.py` | FLAVORS / ROUTES / DATA_SOURCES 中的 4 组旧 hex 替换 |
| `src/views/MapView.vue` | Deck.gl 透明度提升、矢量底图 paint 微调、引入 PathStyleExtension、layerLegend 拆行 |
| `package.json` | 新增 `@deck.gl/extensions` 依赖 |

## 测试与验收

启动 `start.ps1` 后在浏览器观察：

- [ ] 三色光斑（琥珀 / 胭脂 / 松石）在浅米白底图上"刺透感"明显高于改前
- [ ] 节点圆边缘清晰，与底图分离感更强
- [ ] 暗线在地图静止状态下可见，但仍属"低层蛰伏"而非抢眼
- [ ] 海上香料之路、辣椒传播路线、香料群岛东传 三条 `type: 'sea'` 路径暗线呈虚线；丝绸之路、大运河·茶叶北行 两条 `type: 'land'` 暗线呈实线
- [ ] 左侧图例正确呈现"陆路传播"实线样本与"越洋传播"虚线样本
- [ ] 已有交互（点击节点 → flyTo + Inspector、点击生态区 → Inspector、悬停 tooltip）不受影响

## 不在本轮范围

延后到下一轮的差距点（来自 `docs/地图页设计.md`）：

- L3 节点呼吸光晕 + 地表投影
- L2 时序错落接力（年代早 → 晚的接力点亮）
- 左侧极简探索台（Omni-Search + 智能图层触发）
- 底部全空视角（拿掉 NavigationControl 与提示行）
- CHGIS 历史脉络叠加层
