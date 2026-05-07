# ZOOM 拖动触发 morph 状态变化问题记录

记录日期：2026-05-07

## 问题现象

地图在 globe / morph 过渡区间内，上下拖动地图时，即使用户没有滚轮缩放，调试面板中的 `Zoom` 读数也会变化。当前投影状态机直接使用 `map.getZoom()` 判断是否进入 `globe`、`morph` 或 `mercator`，因此一次纯拖动可能被误判为缩放行为，并触发 morph 方向或投影状态变化。

该现象在上下拖动时更明显，因为上下拖动主要改变中心纬度；左右拖动主要改变经度，对当前 MapLibre globe zoom 修正影响较小。

## 当前代码链路

问题集中在 `src/views/MapView.vue`：

- 投影切换阈值定义在 `MORPH_CENTER_ZOOM`、`PLANE_TO_GLOBE_START_ZOOM`、`PLANE_TO_GLOBE_END_ZOOM`、`GLOBE_TO_PLANE_START_ZOOM`、`GLOBE_TO_PLANE_END_ZOOM`（`src/views/MapView.vue:158-163`）。当前实际阈值为：
  - `plane-to-globe`: `3.2 -> 2.4`
  - `globe-to-plane`: `3.0 -> 3.8`
- `MORPH_PROJECTIONS` 使用 MapLibre 表达式按 `['zoom']` 在 `vertical-perspective` 和 `mercator` 间插值（`src/views/MapView.vue:314`）。
- `syncProjectionMode()` 每次执行时读取 `const zoom = map.getZoom()`，并用该值驱动投影状态机（`src/views/MapView.vue:486-527`）。
- `map.on('zoom')` 调用 `scheduleProjectionModeSync()`，`map.on('zoomend')` 直接调用 `syncProjectionMode()`（`src/views/MapView.vue:1001-1008`）。
- `map.on('move')` 只更新调试读数，但如果 MapLibre 在拖动过程中内部修正了 zoom，就会产生 `zoom` 事件，进而进入上述投影同步逻辑（`src/views/MapView.vue:1004-1006`）。

关键结果：项目没有区分“用户主动缩放导致的 zoom 变化”和“globe 控制器为了保持球体屏幕尺寸而产生的 zoom 修正”。只要 `map.getZoom()` 穿过阈值，morph 状态机就会响应。

## 底层原因

MapLibre 在 globe / vertical-perspective 控制模式下，拖动中心纬度时会主动调整 zoom，以保持不同纬度下地球球体的屏幕半径一致。

本项目进入 globe 或 morph 后会启用 globe 相关控制逻辑：

- `node_modules/maplibre-gl/src/geo/projection/globe_projection.ts` 中，`useGlobeControls` 在 `transitionState > 0` 时返回 `true`。
- `node_modules/maplibre-gl/src/geo/projection/globe_camera_helper.ts` 根据 `useGlobeControls` 在 `VerticalPerspectiveCameraHelper` 和 `MercatorCameraHelper` 之间切换。
- `node_modules/maplibre-gl/src/geo/projection/vertical_perspective_camera_helper.ts` 的 `handleMapControlsPan()` 在 pan 时执行（约 `:126-138`）：
  - 记录 `oldLat`、`oldZoom`
  - 通过 `computeGlobePanCenter()` 更新中心点
  - 调用 `tr.setZoom(oldZoom + getZoomAdjustment(oldLat, tr.center.lat))`
- `getZoomAdjustment(oldLat, newLat)` 的注释说明该返回值是“为了在新纬度保持相同 planet radius 而需要加到 zoom 上的值”（`node_modules/maplibre-gl/src/geo/projection/globe_utils.ts:161`）。

因此，拖动地图本身就可能改变 MapLibre transform 的 zoom。这个 zoom 改变不是业务层定义的缩放意图，而是 MapLibre globe 相机模型的补偿值。

## 为什么会影响 morph

当前 morph 的状态机输入只有 `map.getZoom()`。在 `syncProjectionMode()` 内：

- 如果当前在 `plane-to-globe`，`zoom <= 2.4` 会进入 globe，`zoom >= 3.2` 会回到 mercator。
- 如果当前在 `globe-to-plane`，`zoom >= 3.8` 会进入 mercator，`zoom <= 2.4` 会回到 globe。
- 如果当前在 globe 且 `zoom > 2.4`，会进入 `globe-to-plane` morph。
- 如果当前不在 globe 且 `zoom < 3.2`，会进入 `plane-to-globe` morph。

当上下拖动造成中心纬度变化，MapLibre 通过 `getZoomAdjustment()` 修改 zoom 后，上述逻辑会把该变化当作缩放阈值穿越处理。于是用户只是拖动地图，也可能导致：

- `activeMorphDirection` 被重新设置；
- `map.setProjection(MORPH_PROJECTIONS[direction])` 被调用；
- Deck.gl overlay 被移除或恢复；
- polar caps 可见性、world copies、pitch 队列等投影相关状态被同步。

## 影响范围

- 主要影响 `src/views/MapView.vue` 的投影切换状态机。
- 可能同时影响依赖 `map.getZoom()` 的节点气泡聚合逻辑，因为 `updateProjectedNodes()` 也直接读取当前 zoom 判断聚类距离和气泡展示模式。
- 不涉及后端、瓦片接口或数据库。

## 复现建议

1. 打开地图页，进入低 zoom 或 morph 临界区域。
2. 观察开发面板中的 `Zoom / Projection / Globe`。
3. 不使用滚轮，仅上下拖动地图。
4. 如果中心纬度变化足够大，可看到 `Zoom` 读数变化，并可能触发 `Projection` 在 `morph`、`globe`、`mercator` 间切换。

## 后续修复方向

建议不要再直接使用 MapLibre 的实时 `map.getZoom()` 作为 morph 状态机的唯一输入。可选方向：

1. 为投影状态机维护业务层 `intentZoom`：只在滚轮、双击缩放、导航控件缩放、程序化 `flyTo/fitBounds/setZoom` 等明确缩放动作后更新，普通 pan 不更新。
2. 在 drag/pan 期间冻结投影状态：`dragstart` 记录投影模式，`drag` 和由 globe 相机补偿产生的 `zoom` 不驱动 morph，`dragend` 后再按用户缩放意图或当前稳定状态决定是否同步。
3. 将 morph 进度与 MapLibre camera zoom 解耦：用独立的 transition progress 或 mode state 控制 `MORPH_PROJECTIONS`，避免 globe 相机模型的纬度补偿直接跨过阈值。
4. 如果仍保留 `map.getZoom()`，至少需要识别 pan 期间由 `getZoomAdjustment(oldLat, newLat)` 带来的 zoom 漂移，并对投影状态机加防抖、阈值滞回或事件来源过滤。

优先建议方向 1 或 2。方向 1 更干净，能把“用户缩放意图”和“MapLibre globe 相机补偿”分开；方向 2 改动较小，但仍需要小心处理拖动结束后是否同步状态。

## 回退策略

如果后续修复 morph 状态机后出现交互抖动、投影切换失效、Deck.gl 图层异常或节点气泡位置明显漂移，应优先按以下顺序回退。

### 回退触发条件

满足任一条件即可回退：

1. 拖动、滚轮缩放、节点 `flyTo()`、路线 `fitBounds()` 中任一核心交互不可用。
2. `Projection` 长时间停留在错误状态，例如高 zoom 仍为 `globe/morph`，低 zoom 仍为 `mercator`。
3. Deck.gl 路线层或节点层在投影切换后不恢复。
4. 地图出现连续 `setProjection()` 循环、明显卡顿或控制台持续报错。
5. 修复后无法通过地图页基础烟测。

### 首选回退：恢复原有 zoom 驱动逻辑

适用于已经改动 `MapView.vue` 的投影状态机，但新逻辑风险较高的情况。

回退目标：

- `syncProjectionMode()` 继续直接读取 `map.getZoom()`。
- `map.on('zoom')` 继续调用 `scheduleProjectionModeSync()`。
- `map.on('zoomend')` 继续调用 `syncProjectionMode()`。
- 移除新增的 `intentZoom`、drag freeze、事件来源过滤、morph progress 等中间状态。

回退后预期：

- 已知问题会恢复：上下拖动仍可能改变 zoom 并触发 morph。
- 但原有地图核心能力应恢复到修复前状态，适合作为短期稳定回退。

### 降级回退：关闭 morph，只保留 globe / mercator 硬切换

适用于 morph 插值本身引发渲染异常，但 globe 和 mercator 单独可用的情况。

建议降级方式：

1. 保留阈值判断，但不再调用 `enableMorphProjection(direction)`。
2. zoom 低于低阈值时调用 `enterGlobeMode()`。
3. zoom 高于高阈值时调用 `enterMercatorMode()`。
4. 中间区间保持当前投影，不做 morph 插值。

回退后预期：

- 投影过渡不再平滑。
- 可避免 morph 区间内由 `vertical-perspective` 控制逻辑引发的状态反复切换。
- Deck.gl overlay 的移除/恢复次数会减少。

### 最保守回退：固定 mercator

适用于投影切换整体影响演示或开发联调的情况。

建议方式：

1. 初始化 style 保持 `projection: { type: 'mercator' }`。
2. 暂停 `syncProjectionMode()` 对投影的修改。
3. 保留底图、矢量层、Deck.gl 层、节点气泡逻辑。
4. 隐藏或标注调试面板中的 `Globe`/`Projection` 状态，避免误导。

回退后预期：

- globe 视角和 morph 效果暂时不可用。
- 地图页主要数据浏览、节点选择、路线展示能力保留。

### 验证项

任一回退完成后至少验证：

1. `npm run build` 通过。
2. 地图页可加载 HYP raster、海岸线/河流、生态区边界。
3. 滚轮缩放和上下左右拖动可用。
4. 节点选择后 `flyTo()` 可用，路线选择后 `fitBounds()` 可用。
5. Deck.gl 路线动画在非 morph 状态下正常恢复。
6. 控制台无持续重复报错。

### 记录要求

执行回退时，在提交或变更说明中注明：

- 回退级别：首选回退、降级回退或最保守回退。
- 回退原因：对应上面的触发条件。
- 已知遗留问题：是否仍保留“拖动导致 zoom 变化并触发 morph”的原始问题。
