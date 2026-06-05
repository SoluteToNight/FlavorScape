# 工作台自由元素布局编辑器 — 实施路线图

> **状态**: 方案已确认，可进入编码
> **创建**: 2026-06-05
> **范围**: Poster（海报）+ Archive（白皮书）。Display（演示）不纳入本次改造
> **原则**: 渐进共存、DOM 渲染、混合粒度、模板起点

---

## 架构决策（已确认）

| # | 决策 | 结论 |
|---|------|------|
| 1 | 编辑器范式 | **DOM 自由布局**（absolute positioning + CSS transforms），非 Canvas |
| 2 | 元素粒度 | **混合模型**：原子元素（文本/图片/标签）自由定位 + 复合块（地图/证据/叙述文）整体拖拽、内部子元素相对定位 |
| 3 | 数据迁移 | **渐进共存**：保留现有 `outputs.poster.*` 字段，新增 `outputs.poster.layout` 字段 |
| 4 | 新项目起点 | **模板起点**：根据产品数据自动生成默认布局（含"空白画布"模板，用户可选择从零搭建） |
| 5 | 文本样式系统 | **完整版**：字号 + 颜色 + 对齐 + 字体族 + 行高 + 字间距 + 加粗/斜体 |
| 6 | 范围 | 仅 **Poster + Archive**。Display 不再纳入本次改造

---

## 主题系统设计

### 主题 vs 布局预设 — 职责分离

两者是**独立文件**，各管各的，通过 `themeId` 关联。

| | **主题 `themes/*.json`** | **布局预设 `layout-presets/*.json`** |
|---|---|---|
| 存什么 | 颜色、字体、装饰样式（纯视觉 token） | 元素类型、位置、尺寸（纯结构） |
| 何时用 | 新建项目 + 切换主题 | 仅在**新建项目**时用于生成初始元素 |
| 可切换 | ✓ 随时切换，不影响元素位置 | ✗ 创建后用户自由编辑 |
| 类比 | PPT 的"配色方案" | PPT 的"版式/母版" |

```
新建项目时:
  layout-presets/poster-nature.json  ──→  初始元素排列（创建一次）
  themes/nature.json                 ──→  给元素填默认颜色/字号

用户拖拽后:
  元素位置 → 用户自己的（不受主题影响）
  元素颜色 → 跟随主题（除非手动改过）

换 indigo 主题:
  themes/indigo.json  ──→  只覆盖跟随主题的字段（颜色/字体）
  元素位置 → 不动
```

### 主题文件结构

**目录**: `src/data/themes/`

```json
// nature.json
{
  "id": "nature",
  "name": "自然探索",
  "canvas": {
    "backgroundColor": "#ffffff",
    "backgroundPattern": null
  },
  "colors": {
    "primary": "#2a4128",
    "accent": "#708a68",
    "bg": "#ffffff",
    "paper": "#f4f5f2",
    "text": "#333333",
    "mapBaseFill": "#eef1eb",
    "mapBaseStroke": "rgba(0,0,0,0.08)",
    "mapActiveFill": "#2a4128",
    "mapActiveStroke": "#ffffff"
  },
  "typography": {
    "titleFont": "Noto Sans SC",
    "titleWeight": 700,
    "titleSize": 36,
    "bodyFont": "Noto Sans SC",
    "bodySize": 12,
    "bodyLineHeight": 1.6,
    "highlightColor": "#2a4128",
    "highlightStyle": "bold"
  },
  "elements": {
    "badge": {
      "style": "tag",
      "color": "#2a4128",
      "bgColor": "transparent"
    },
    "metricCard": {
      "labelColor": "rgba(0,0,0,0.68)",
      "valueColor": "#2a4128",
      "borderStyle": "top-line"
    },
    "divider": { "color": "#2a4128", "opacity": 0.15 },
    "frame": { "borderColor": "#2a4128", "borderOpacity": 0.08, "inset": 16 }
  }
}
```

三套主题同结构不同值：
- `nature.json` — 深绿主色 / 白底 / 现代无衬线
- `heritage.json` — 棕褐主色 / 暖米底 / 衬线古典
- `indigo.json` — 白字主色 / 深蓝底 / 混合衬线

### 主题继承标记 `_themeSlots`

每个元素携带 `_themeSlots` 数组，标记哪些属性跟随主题。从布局预设加载时自动标记，用户手动修改时自动解除。

```typescript
interface BaseElement {
  // ... 基础字段 ...
  _themeSlots: string[]  // 如 ['fontSize', 'fontFamily', 'color', 'fontWeight']
}
```

**规则**:
- 预设加载 → 根据 `_themeRefs` 生成 `_themeSlots`
- 用户在属性面板改某字段 → 从 `_themeSlots` 中移除对应 key
- 切换主题 → 遍历 `_themeSlots`，从新主题 token 解析值覆盖

### 主题色覆盖 `themeOverrides`

用户可以在不换主题的情况下微调当前主题色（如"nature 绿色太暗，调亮一点"），覆盖值存在项目数据中：

```typescript
interface PageLayout {
  // ...
  themeId: string
  themeOverrides?: {
    [key: string]: string  // 如 "colors.primary": "#4a613a"
  }
}
```

加载时：`themes/{id}.json` 基础值 → `themeOverrides` 覆盖 → 最终主题色。

### 三种颜色操作 — 分流设计

| 操作 | 改什么 | 影响范围 | 存储位置 |
|------|--------|---------|---------|
| 改单个元素色 | 元素 `.color` | 只这一个 | `element.color`，同时从 `_themeSlots` 移除 `color` |
| 整体换主题 | `layout.themeId` | 所有 `_themeSlots` 含 `color` 的元素（手动改过的除外） | `layout.themeId` |
| 调当前主题色 | `layout.themeOverrides` | 同换主题，但保留 `themeId` 不变 | `layout.themeOverrides` |

三者互不冲突。换整个主题后再调主题色也生效——叠加逻辑：`themeOverrides` 始终作为最后一层覆盖。

---

## 画布尺寸系统

### 问题：用户想要不同比例的输出怎么办

当前海报 440×860、白皮书 760×1040 是硬编码的。自由布局下画布尺寸即为 `PageLayout.width/height` 数据字段，天然可配置。核心问题是**改尺寸后元素如何重新适配**。

### 策略选择：本期固定预设 + 锚点接口预留

| | 策略 A: 固定预设 | 策略 B: 锚点自适应 | 策略 C: 原地不动 |
|---|---|---|---|
| 做法 | 每个尺寸配一套布局模板 | 元素锚定画布边/角，改尺寸时等比移动 | 改尺寸，元素留在原位 |
| 体验 | 选尺寸 → 自动排版 | 改尺寸 → 元素自动重新定位 | 改尺寸 → 空白/跑出画布 |
| 实现复杂度 | 低（多几个 JSON 文件） | 高（锚点系统 + 布局引擎） | 零（不推荐） |
| 本期 | **✓ 采用** | 预留接口 | ✗ 不采用 |

### 尺寸预设

海报和白皮书各配常用尺寸，每个尺寸独立布局模板：

```
海报预设（竖版为主）:
  poster-nature-440x860.json      # 现有尺寸  ≈ 1:1.95
  poster-nature-600x900.json      # 更大竖版   ≈ 1:1.5
  poster-nature-800x800.json      # 方形（社交媒体）
  poster-nature-1200x600.json     # 横版 banner

白皮书预设（横版为主）:
  archive-default-760x1040.json   # 现有尺寸
  archive-default-A4.json         # 标准 A4 竖版  595×842
  archive-default-1200x800.json   # 横版宽幅
```

> **注意**: 不是每个"主题 × 尺寸"都要一份。布局模板只定义元素位置（x/y/w/h），不绑主题。同一尺寸可配合任意主题使用。

### 创建流程：三维度组合

新建项目时三个独立维度组合：

```
尺寸（canvas size）   ×   布局模板（元素排列）   ×   主题（配色字体）
       ↓                        ↓                       ↓
  poster-600x900          竖版大图居中结构          nature / heritage / indigo
```

流程步骤：
1. 选输出类型（海报 / 白皮书）
2. 选尺寸 → 决定 `canvas.width/height`，加载对应布局模板
3. 选主题 → 填入颜色和字体默认值
4. 生成初始元素数组 → 用户开始编辑

### 锚点接口（本期预留，不实现逻辑）

`BaseElement` 上增加可选 `_anchor` 字段，为后续尺寸自适应留数据结构基础：

```typescript
interface BaseElement {
  // ... 现有字段 ...
  _anchor?: {
    h: 'left' | 'center' | 'right'    // 水平锚点
    v: 'top' | 'center' | 'bottom'    // 垂直锚点
    hOffset: number                    // 距离锚点的偏移 (px)
    vOffset: number                    // 距离锚点的偏移 (px)
  }
}
```

示例：标题 horizontal=center + vertical=top + vOffset=40 → 无论画布多宽，始终居中距顶 40px。

### 与 PageLayout 的整合

```typescript
interface PageLayout {
  version: number
  width: number            // 画布宽 — 由尺寸预设决定
  height: number           // 画布高 — 由尺寸预设决定
  presetId: string         // 尺寸预设 ID，如 "poster-600x900"
  backgroundColor: string
  elements: Element[]
  themeId: string
  themeOverrides?: Record<string, string>
}
```

新增 `presetId` 字段记录当前使用的尺寸预设，供后续尺寸自适应逻辑参考。

---

## Phase 0: 元素系统 Schema 设计

**目标**: 产出 `src/types/elements.ts`，定义所有元素和复合块的 TypeScript 接口。

### 元素基础接口

```typescript
// 所有元素的公共字段
interface BaseElement {
  id: string                    // 唯一标识，如 "el-xxxx"
  type: ElementType             // 元素类型
  x: number                     // 画布内绝对 X 坐标 (px)
  y: number                     // 画布内绝对 Y 坐标 (px)
  w: number                     // 宽度 (px)
  h: number                     // 高度 (px)
  zIndex: number                // 层级
  locked: boolean               // 锁定（不可选中/移动）
  visible: boolean              // 可见性
  opacity: number               // 不透明度 0-1
  _themeSlots: string[]         // 主题继承标记，如 ['fontSize', 'color']。空数组 = 全部手动
}

// 原子元素类型
type AtomicElementType =
  | 'text'        // 单行/多行文本
  | 'image'       // 图片
  | 'badge'       // 徽章标签
  | 'divider'     // 分割线
  | 'shape'       // 装饰形状（矩形/圆形）

// 复合块类型
type BlockType =
  | 'mapBlock'        // 空间地图块（内嵌 StaticGeoMap）
  | 'evidenceBlock'   // 证据指标块（多个 metricCard）
  | 'narrativeBlock'  // 叙述文块（富文本段落）
  | 'titleBlock'      // 标题块（品牌标题 + 副标题组合）

type ElementType = AtomicElementType | BlockType
```

### 原子元素子类型

```typescript
interface TextElement extends BaseElement {
  type: 'text'
  content: string               // 文本内容（支持 <span class="hl">）
  fontSize: number              // 字号 (px)
  fontFamily: string            // 字体族 ('Noto Sans SC' | 'Noto Serif SC')
  fontWeight: 400 | 700         // 字重
  fontStyle: 'normal' | 'italic' // 斜体
  color: string                 // 文字颜色 hex
  textAlign: 'left' | 'center' | 'right'
  lineHeight: number            // 行高倍数（默认 1.5）
  letterSpacing: number         // 字间距 (px，默认 0)
}

interface ImageElement extends BaseElement {
  type: 'image'
  src: string                   // 图片 URL 或 data URL
  objectFit: 'cover' | 'contain' | 'fill'
  objectPositionX: number       // 焦点 X (0-100%)
  objectPositionY: number       // 焦点 Y (0-100%)
  borderRadius: number          // 圆角 (px，默认 0)
}

interface BadgeElement extends BaseElement {
  type: 'badge'
  content: string
  style: 'tag' | 'seal' | 'pill'  // 当前 poster 有 tag 和 seal 两种
  color: string
  bgColor: string
}

interface DividerElement extends BaseElement {
  type: 'divider'
  style: 'solid' | 'dashed' | 'dotted'
  color: string
  thickness: number             // 线粗细 (px)
}
```

### 复合块子类型

```typescript
interface MapBlock extends BaseElement {
  type: 'mapBlock'
  children: Element[]           // 地图子元素（svgMap + nodeLabels）
  province: string              // 目标省份
  nodes: SpatialNode[]          // 空间节点数据
}

interface EvidenceBlock extends BaseElement {
  type: 'evidenceBlock'
  children: MetricCardElement[] // 指标卡片列表
  columns: number               // 列数（默认 auto，根据 w 自适应）
  gap: number                   // 卡片间距 (px)
}

interface MetricCardElement extends BaseElement {
  type: 'metricCard'
  label: string
  value: string
  labelColor: string
  valueColor: string
}

interface NarrativeBlock extends BaseElement {
  type: 'narrativeBlock'
  children: Element[]           // 内部的文本元素
  kicker: string                // 小标题（如 "品牌叙事"）
  subtitle: string              // 副标题
}

interface TitleBlock extends BaseElement {
  type: 'titleBlock'
  children: Element[]           // 内部文本 + badge 元素
}

type Element = TextElement | ImageElement | BadgeElement | DividerElement
             | MapBlock | EvidenceBlock | NarrativeBlock | TitleBlock
```

### 布局数据模型

```typescript
interface PageLayout {
  version: number               // schema 版本号
  width: number                 // 画布宽度 (px) — 由尺寸预设决定
  height: number                // 画布高度 (px) — 由尺寸预设决定
  presetId: string              // 尺寸预设 ID，如 "poster-440x860"
  backgroundColor: string       // 画布背景色
  elements: Element[]           // 所有顶层元素（含原子元素和复合块）
  themeId: string               // 关联的主题 ID，如 "nature"
  themeOverrides?: Record<string, string>  // 主题色微调覆盖
}
```

### 默认布局预设（Phase 0 产出）

为 poster 的 3 种主题和 archive 各产出 1 份默认布局 JSON，将现有 CSS 固定布局转换为自由布局坐标：

| 预设文件 | 对应旧输出 | 元素数量（预估） |
|----------|-----------|-----------------|
| `poster-nature.json` | StudioPoster nature 主题 | ~10 个元素 |
| `poster-heritage.json` | StudioPoster heritage 主题 | ~10 个元素 |
| `poster-indigo.json` | StudioPoster indigo 主题 | ~10 个元素 |
| `archive-default.json` | StudioArchive | ~12 个元素 |
| `blank.json` | 空白画布（用户从零搭建） | 0 个元素 |

---

## Phase 1: 数据层改造

### Phase 1a: Pinia Store (`src/stores/studio.js`)

**改动点**:

1. 在 `createPosterDefaults()` / `createArchiveDefaults()` 中新增 `layout: null` 字段
   ```
   outputs.poster.layout: PageLayout | null
   ```
   - `null` = 使用经典模式（旧表单编辑）
   - `{ ... }` = 使用自由布局模式

2. 新增 element CRUD 方法：
   ```
   addElement(outputType, element)
   updateElement(outputType, elementId, patch)
   removeElement(outputType, elementId)
   reorderElement(outputType, elementId, newZIndex)
   ```

3. 新增 `initLayout(outputType, presetName)` — 从预设 JSON 加载默认布局，将当前 product 数据填充到元素中

4. 计算属性：`isFreeLayout(outputType)` — 判断 `layout !== null`

5. 兼容性：`mergedPosterData` 等计算属性检测 `layout` 是否为空，为空则走旧逻辑

**新文件**:
- `src/types/elements.ts` — 所有类型定义
- `src/data/layout-presets/poster-nature.json` — 默认布局预设
- `src/data/layout-presets/poster-heritage.json`
- `src/data/layout-presets/poster-indigo.json`
- `src/data/layout-presets/archive-default.json`

### Phase 1b: 后端兼容 (`backend/routers/studio.py`)

**改动**: `StudioProjectPayload` 已有 `extra = "allow"` 和 `outputs: dict[str, Any]`，无需改动 Pydantic model。

**验证**: 确保包含 `layout` 嵌套对象的 JSONB payload 能正常写入和读出 PostgreSQL。

### Phase 1c: Undo/Redo 历史栈

**实现位置**: `src/stores/studio.js` 内或独立 composable `src/composables/useHistory.ts`

**设计**: Command 模式。每次 element CRUD 操作自动入栈。

```
historyStack: LayoutSnapshot[]    // 最多 50 个快照
historyIndex: number              // 当前快照位置
undo() → index-- → 恢复 layout
redo() → index++ → 恢复 layout
```

**快照策略**: 延迟快照（debounce 300ms），批量操作（如拖拽结束才入栈，不是每个 mousemove 入栈）。

---

## Phase 2: 布局引擎

### Phase 2a: FreeLayoutCanvas 容器

**新文件**: `src/components/editor/FreeLayoutCanvas.vue`

**职责**:
- 绝对定位容器（`position: relative` + 固定 `width/height`）
- 缩放平移：`transform: scale(N)` 包裹整个画布，中心缩放
- 点击空白区域：清除所有选中
- 暴露 `canvasRef` 给外部用于 html2canvas 导出
- 接收 props: `layout: PageLayout`, `scale: number`, `selectedIds: string[]`
- Emit: `element-click`, `canvas-click`, `element-drag-start/end`

### Phase 2b: 原子元素渲染组件

| 新文件 | 对应元素 |
|--------|---------|
| `src/components/editor/elements/TextElement.vue` | text |
| `src/components/editor/elements/ImageElement.vue` | image |
| `src/components/editor/elements/BadgeElement.vue` | badge |
| `src/components/editor/elements/DividerElement.vue` | divider |

每个元素组件的统一模式：
```
<div :style="{ position: absolute, left: x, top: y, width: w, height: h, zIndex }">
  <!-- 内容渲染 -->
  <!-- 选中时显示边框 + resize handles -->
</div>
```

### Phase 2c: 复合块渲染组件

| 新文件 | 对应块 | 复用现有组件 |
|--------|--------|-------------|
| `src/components/editor/blocks/MapBlock.vue` | mapBlock | `StaticGeoMap.vue` |
| `src/components/editor/blocks/EvidenceBlock.vue` | evidenceBlock | 无（新写 metric cards 布局） |
| `src/components/editor/blocks/NarrativeBlock.vue` | narrativeBlock | 无（文本段落 + hl 高亮） |
| `src/components/editor/blocks/TitleBlock.vue` | titleBlock | 无 |

复合块的 `children[]` 在自己的绝对定位容器内用 flex/grid 相对布局。块整体跟随父容器的 `x/y`。

---

## Phase 3: 编辑器交互

### Phase 3a: 拖拽移动

**新文件**: `src/composables/useElementDrag.ts`

```
mousedown 在元素上 → 记录偏移
mousemove → 更新 element.x/y（带 boundary clamp）
mouseup → 入栈 undo/redo
```

边界约束：`x ∈ [0, canvasWidth - element.w]`, `y ∈ [0, canvasHeight - element.h]`

### Phase 3b: 缩放手柄

**新文件**: `src/components/editor/SelectionOverlay.vue`
**新文件**: `src/composables/useElementResize.ts`

8 个手柄：四角 + 四边中点。拖拽角时等比缩放（可选 Shift 解除比例锁），拖拽边时单向拉伸。

### Phase 3c: 选择系统

**新文件**: `src/composables/useSelection.ts`

- 单击元素 → 单选（其他取消选中）
- Shift + 单击 → 多选切换
- 在空白区域拖拽 → 框选（marquee selection）
- Delete/Backspace → 删除所有选中元素
- 选中态视觉：2px 蓝色边框 + 8 个圆形白色手柄

### Phase 3d: 智能对齐

**新文件**: `src/components/editor/AlignmentGuides.vue`

拖拽/缩放时检测：
- 边缘对齐（与相邻元素 left/right/top/bottom 距离 < 5px 时吸附）
- 中线对齐（水平/垂直中线）
- 间距均分（3+ 元素等间距时显示引导线）

对齐阈值：5px 吸附距离。

### Phase 3e: 层级控制

- 工具栏按钮：置于顶层 / 上移一层 / 下移一层 / 置于底层
- 右键菜单：同样的 4 个选项
- 实现：交换 `zIndex` 值

---

## Phase 4: 编辑 UI

### Phase 4a: 元素工具栏

**新文件**: `src/components/editor/ElementToolbar.vue`

固定在画布上方或左侧的工具栏：

```
[+ 添加] [文本] [图片] [地图块] [证据块] [分割线] [徽章]
```

点击 "+ 添加" 或类型按钮 → 在画布中央创建一个默认元素。默认坐标：`(canvasWidth/2 - 50, canvasHeight/2 - 25)`。

### Phase 4b: 属性面板

**新文件**: `src/components/editor/PropertyPanel.vue`

选中元素时，在右侧栏显示可编辑属性：

- 文本元素：内容 textarea、字号 slider、颜色 picker、对齐按钮组、字体族下拉（Sans/Serif）、加粗/斜体切换、行高 slider、字间距 slider
- 图片元素：替换图片按钮、object-fit 选择、焦点 slider
- 通用：X/Y 坐标输入、宽/高输入、锁定/可见开关

复用现有 `CreativeEditor.vue` 的 glass-panel 样式。

---

## Phase 5: 输出类型迁移

### Phase 5a: 海报迁移

- 新项目创建时：检测 product 数据 → `initLayout('poster', productTheme)` → 生成自由布局
- 旧项目加载时：`layout === null` → 仍走旧 `StudioPoster.vue` 渲染；提供"升级到自由布局"按钮（一次性迁移）
- 迁移函数：读取旧的 `outputs.poster.{title, subtitle, narrative, ...}` → 填入预设布局的元素 `content` 中

### Phase 5b: 白皮书迁移

同海报模式。旧 `StudioArchive.vue` 保留作为经典模式回退。

### Phase 5c: 展示屏 — 不纳入本次改造

Display（演示）已是完整体——MapLibre GL 交互地图 + Deck.gl 动态路线 + 时间轴 + 自动巡览。其编辑需求（选路线、开时间轴等）通过现有表单已满足，不纳入自由布局改造范围。

---

## Phase 6: CreativeEditor 重构

**文件**: `src/components/CreativeEditor.vue`（重写）

**新模式切换**:

```
┌──────────────────────────────────┐
│  [经典模式] [自由布局]  ← 切换按钮  │
├──────────────────────────────────┤
│  经典模式：现有的表单字段（不变）   │
│  自由布局：                        │
│    ├─ ElementToolbar              │
│    ├─ FreeLayoutCanvas            │
│    └─ PropertyPanel（右侧栏）      │
└──────────────────────────────────┘
```

模式切换保存到 `outputs.poster.layout === null`（经典）vs 非 null（自由）。

---

## Phase 7: 导出适配

**影响文件**: `src/components/OutputChecklist.vue`, `src/views/StudioView.vue`

**改动**:
- PNG 导出：html2canvas 捕获 `FreeLayoutCanvas` 的 DOM 容器（绝对定位元素天然可被捕获）
- 文本复制：读取 `layout.elements[]` 中所有 text 元素的 `content` 拼接
- 项目 JSON 下载：包含 `layout` 字段完整导出

**验证清单**:
- [ ] poster 自由布局导出 PNG 与预览一致
- [ ] archive 自由布局导出 PNG 与预览一致
- [ ] 2x / 3x 分辨率导出正常
- [ ] 经典模式导出不受影响

---

## Phase 8: 快捷键 & 体验打磨

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Z` | 撤销 |
| `Ctrl+Y` / `Ctrl+Shift+Z` | 重做 |
| `Delete` / `Backspace` | 删除选中元素 |
| `Ctrl+A` | 全选 |
| `Ctrl+D` | 复制选中元素（偏移 20px） |
| `方向键` | 微调选中元素位置 1px |
| `Shift+方向键` | 微调选中元素位置 10px |
| `Escape` | 取消所有选中 |

**其他打磨项**:
- 元素 hover 时显示半透明边框（预览态）
- 框选时 marquee 虚线框
- 缩放至 100% / 适应窗口 / 实际大小按钮

---

## 文件总览

### 新建文件（~26 个）

```
src/types/elements.ts                          # 类型定义
src/data/themes/nature.json                    # 主题 token - 自然探索
src/data/themes/heritage.json                  # 主题 token - 古典传承
src/data/themes/indigo.json                    # 主题 token - 靛蓝拓印
src/data/themes/index.ts                       # Theme 类型 + 加载/查询函数
src/data/layout-presets/poster-nature-440x860.json   # 海报预设 - 现有尺寸
src/data/layout-presets/poster-nature-600x900.json   # 海报预设 - 大竖版
src/data/layout-presets/poster-nature-800x800.json   # 海报预设 - 方形
src/data/layout-presets/archive-default-760x1040.json # 白皮书预设 - 现有尺寸
src/data/layout-presets/archive-default-A4.json       # 白皮书预设 - A4
src/data/layout-presets/blank.json                    # 空白画布模板
src/data/layout-presets/index.ts                      # 类型 + 加载/解析函数

src/components/editor/FreeLayoutCanvas.vue     # 画布容器
src/components/editor/ElementToolbar.vue       # 元素工具栏
src/components/editor/PropertyPanel.vue        # 属性面板
src/components/editor/SelectionOverlay.vue     # 选中框 + 手柄
src/components/editor/AlignmentGuides.vue      # 智能对齐线

src/components/editor/elements/TextElement.vue
src/components/editor/elements/ImageElement.vue
src/components/editor/elements/BadgeElement.vue
src/components/editor/elements/DividerElement.vue

src/components/editor/blocks/MapBlock.vue
src/components/editor/blocks/EvidenceBlock.vue
src/components/editor/blocks/NarrativeBlock.vue
src/components/editor/blocks/TitleBlock.vue

src/composables/useElementDrag.ts
src/composables/useElementResize.ts
src/composables/useSelection.ts
src/composables/useHistory.ts                  # undo/redo
src/composables/useTheme.ts                    # 主题加载、token 解析、切换主题
src/composables/useLayoutPreset.ts            # 预设加载、_themeRefs 解析、创建元素数组
```

### 修改文件（~7 个）

```
src/stores/studio.js              # layout 字段 + element CRUD + undo/redo
src/components/CreativeEditor.vue # 整体重构 -> 模式切换
src/views/StudioView.vue          # 集成 FreeLayoutCanvas
src/components/OutputChecklist.vue # 导出适配
backend/routers/studio.py         # Pydantic model（可能无需改）
```


