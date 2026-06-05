# FlavorScape 开发进度与架构说明：Studio 与 DeepSeek 资产生产模块

日期：2026-06-04

## 1. 项目定位

FlavorScape / 寻味地理是一个面向地方风味、食材传播、产地证据和品牌资产生产的 WebGIS + 内容生成系统。当前项目已经从早期的地图展示原型，推进到“空间证据 + 品牌内容 + 可交付物生产”的产品化原型阶段。

系统核心目标包括：

- 用地图、路径、生态区和节点数据解释食材与地方风味的空间关系。
- 将产地、工艺、检测、认证、品牌叙事等资料组织为可视化证据。
- 通过 Studio 工作台生产营销海报、实证白皮书和智慧大屏。
- 接入 DeepSeek，让用户上传资料后获得结构化资产包，并继续通过 AI 对话推进编辑和交付。

## 2. 开发历程简述

### 2.1 地图与数据原型阶段

早期重点是 WebGIS 底图和业务数据：

- FastAPI 后端提供 `/api/*` 数据接口和 `/tiles/*` 瓦片接口。
- PostgreSQL / PostGIS 存储食材、节点、路线、生态区等业务数据。
- MapLibre、Deck.gl 和 ECharts 用于地图、路径、节点和图表展示。
- 地图页围绕食材节点、传播路线、生态区边界和 HYP 栅格底图进行交互展示。

这一阶段的主要成果是证明“地方风味可以被空间化表达”。

### 2.2 页面拆分与产品化表达阶段

随后项目从单一展示页拆分出多个业务页面：

- 首页：产品入口与视觉封面。
- 地图页：WebGIS 主探索界面。
- 食材传播页：食材历史传播路径和节点叙事。
- 品牌/大屏页：面向展示场景的空间品牌叙事。
- 营销海报页：品牌海报生成和样式展示。
- 白皮书页：证据型内容输出。
- 资产导入页：导入资料并生成空间品牌资产包。

这一阶段开始从“展示系统”转向“内容生产系统”。

### 2.3 Studio 与用户体系阶段

近期合入并重点推进的是 Studio 工作台和用户管理：

- 新增注册、登录、个人页和 JWT 认证。
- 新增 `/studio` 路由。
- Studio 支持按用户保存项目。
- 每个项目可选择产出类型：海报、白皮书、智慧大屏。
- 项目数据通过 `/api/studio/projects` 持久化到数据库。
- Studio 内可编辑文案、主题、图片焦点、证据指标、大屏交互模式等。

这一阶段把项目从“页面展示”推进为“可保存、可编辑、可导出”的工作台。

### 2.4 DeepSeek 融合阶段

最新开发重点是 DeepSeek 与资产生产流程融合：

- 资产导入页支持多格式文档上传。
- 后端解析 PDF、DOCX、XLSX、CSV、TXT、Markdown、JSON 等资料。
- DeepSeek 将资料分析为结构化资产包。
- 页面展示文件解析状态、AI 可见分析步骤、证据、风险、评分和产出建议。
- 新增资产包级 AI 对话，辅助用户继续推进业务流程。
- Studio 海报编辑器新增 AI 对话助手，可直接给出标题、副标题、短句、叙事、主题和图片焦点建议，并支持一键应用。

这一阶段的目标是让 DeepSeek 从“文本分析器”升级为“业务流程协作者”。

## 3. 整体架构

### 3.1 前端架构

前端使用 Vue 3 + Vite + Pinia + Vue Router。

主要目录：

- `src/views/`：页面级视图。
- `src/components/`：复用组件，包括 Studio 组件、地图组件、AI 助手组件。
- `src/stores/`：Pinia 状态管理。
- `src/composables/`：数据加载和业务组合逻辑。
- `src/map/`：MapLibre 地图封装和底图样式。
- `src/data/product_cases/`：前端产品案例 JSON。
- `src/styles/`：全局样式和 MapLibre 样式。

主要页面：

- `HomeView.vue`：首页。
- `MapView.vue`：WebGIS 地图探索。
- `IngredientSpreadView.vue`：食材传播路径。
- `GeoAtlasView.vue`：智慧大屏 / 品牌空间叙事。
- `MarketingView.vue`：营销海报展示。
- `ArchiveView.vue`：实证白皮书。
- `DemoImportView.vue`：资产导入与 DeepSeek 分析。
- `StudioView.vue`：Studio 工作台。
- `LoginView.vue` / `RegisterView.vue` / `ProfileView.vue`：用户体系。

### 3.2 后端架构

后端使用 FastAPI，主要职责是：

- 提供业务数据 API。
- 提供栅格和矢量瓦片接口。
- 初始化数据库连接池。
- 加载 GIS 数据。
- 提供认证、Studio 项目、资产分析等服务。

主要目录：

- `backend/main.py`：FastAPI 应用入口，注册中间件和路由。
- `backend/config.py`：路径、端口、JWT、DeepSeek 等配置。
- `backend/db/connection.py`：PostgreSQL 连接池。
- `backend/db/query.py`：业务数据查询。
- `backend/db/auth_queries.py`：用户表和认证查询。
- `backend/db/studio_queries.py`：Studio 项目持久化查询。
- `backend/routers/auth.py`：注册、登录、当前用户。
- `backend/routers/studio.py`：Studio 项目 CRUD。
- `backend/routers/assets.py`：DeepSeek 资产分析和 AI 对话。
- `backend/routers/ingredient_spread.py`：食材传播接口。
- `backend/routers/tiles.py`：瓦片接口。

### 3.3 数据与配置

数据库：

- PostgreSQL / PostGIS。
- `.env` 提供 `DATABASE_URL`。
- 用户表 `app_user` 由后端启动时幂等创建。
- Studio 项目表 `studio_project` 由后端启动时幂等创建。

DeepSeek 配置：

```env
DEEPSEEK_API_KEY=your_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
```

其中 `DEEPSEEK_MODEL` 以 `.env` 和 `backend/config.py` 的实际配置为准，后续如果更换模型，只需要同步调整环境变量。

运行端口：

- FastAPI：`8001`
- Vite dev：`3002`
- Express production：`3001`
- Vite preview：`4173`

## 4. Studio 模块进度

### 4.1 当前能力

Studio 已具备以下能力：

- 用户登录后访问 `/studio`。
- 从产品案例库选择产品。
- 创建项目并选择产出类型。
- 产出类型包括：
  - 海报
  - 白皮书
  - 智慧大屏
- 每个项目会保存：
  - 项目 ID
  - 用户 ID
  - 产品 ID
  - 产出类型
  - 输出配置
  - 导出记录
  - 版本号
- 项目通过后端接口按用户持久化。
- 支持项目列表、切换、重命名、删除、复制。
- 支持乐观锁版本控制，避免覆盖并发编辑。

### 4.2 Studio 产出编辑

海报编辑：

- 标题
- 副标题
- 诗意短句
- 品牌叙事
- 主题
  - 自然绿
  - 东方红
  - 蓝印花
- 主图上传
- 图片焦点调整
- PNG 导出

白皮书编辑：

- 报告标题
- 证明摘要
- 结论说明
- 证据指标显示控制

智慧大屏编辑：

- 大屏标题
- 副标题
- 展示说明
- 产品空间节点 / 传播路径模式
- 路径选择
- 时间线显示控制

### 4.3 Studio 与 DeepSeek 的结合

当前已实现 Studio 海报编辑 AI 助手：

- 文件：`src/components/AiPosterAssistant.vue`
- 接口：`POST /api/assets/poster-chat`
- 位置：Studio 海报项目进入编辑状态后，出现在左侧编辑面板。

AI 助手能力：

- 与用户对话。
- 读取当前产品和海报内容。
- 给出标题、副标题、短句、叙事、主题、图片焦点建议。
- 支持快捷提示：
  - 强化产地高级感
  - 改成更年轻的社媒风格
  - 压缩叙事，增强标题
  - 给出三种色系方案
- 支持一键应用字段建议。

当前限制：

- 模板目前只支持三个主题：`nature`、`heritage`、`indigo`。
- AI 可以提出布局建议，但暂不能自动重排海报模板结构。
- AI 对话结果不会自动创建全新模板，只能修改现有字段。

## 5. 资产导入与 DeepSeek 模块进度

### 5.1 当前页面

入口：`/import`

文件：`src/views/DemoImportView.vue`

当前页面已经从早期文本分析页升级为资产生成工作台。

用户流程：

1. 选择案例模板。
2. 上传资料文件。
3. 填写补充说明。
4. 点击“开始生成资产分析”。
5. 后端解析文件。
6. DeepSeek 生成结构化资产包。
7. 页面展示结果。
8. 用户继续通过 AI 对话共创。
9. 复制或下载资产包 JSON。
10. 跳转 Studio、海报、白皮书或大屏继续编辑。

### 5.2 支持的文档格式

后端接口：`POST /api/assets/analyze-files`

当前支持：

- PDF：通过 `pypdf` 提取页面文本。
- DOCX：通过 `python-docx` 提取段落和表格文本。
- XLSX：通过 `openpyxl` 提取工作表单元格。
- CSV：按文本读取。
- TXT：按文本读取。
- Markdown：按文本读取。
- JSON：按文本读取。
- PNG / JPG / JPEG / WEBP：记录为视觉素材，当前不做 OCR。

当前限制：

- `.xls` 旧格式暂不解析，建议另存为 `.xlsx` 或 CSV。
- 图片暂未接入 OCR。
- 单文件大小限制为 12MB。
- 合并后进入 DeepSeek 的文本限制为 60000 字符。

### 5.3 DeepSeek 分析输出

接口返回结构包括：

- `extraction`：文件解析结果。
- `thinking_trace`：用户可见的分析步骤摘要。
- `asset_package`：结构化资产包。

说明：`thinking_trace` 不是模型隐藏思维链，而是面向用户展示的处理步骤摘要，用于提供视觉反馈和流程透明度。

资产包结构：

```json
{
  "product": {
    "name": "",
    "category": "",
    "origin": "",
    "ingredients": []
  },
  "evidence": {
    "lab_indicators": [],
    "certifications": [],
    "origin_claims": [],
    "process_steps": []
  },
  "visualization": {
    "map_nodes": [],
    "routes": [],
    "timeline": [],
    "radar_metrics": []
  },
  "brand_assets": {
    "slogan": "",
    "poster_copy": [],
    "whitepaper_outline": [],
    "dashboard_cards": [],
    "style_direction": [],
    "layout_direction": []
  },
  "scores": {
    "completeness": 0,
    "evidence_strength": 0,
    "visualization_fit": 0,
    "risk": 0
  },
  "risks": [],
  "citations": [],
  "next_actions": []
}
```

### 5.4 资产页视觉反馈

资产导入页已经展示：

- 文件队列。
- 文件解析结果。
- AI 工作流进度。
- DeepSeek 可见分析步骤。
- 资料完整度、证据强度、可视化适配、风险评分。
- 证据与风险列表。
- 资产产出建议。
- 业务流转面板。

业务流转面板包括：

1. 资料解析
2. 证据审核
3. AI 共创
4. Studio 编辑
5. 交付导出

### 5.5 资产包级 AI 对话

新增接口：`POST /api/assets/asset-chat`

该接口用于资产导入页中的 AI 对话，不局限于海报编辑。

输入：

- 当前资产包。
- 文件解析摘要。
- 用户对话历史。

输出：

- `reply`：AI 回复。
- `recommendations`：业务建议卡片。
- `next_actions`：下一步动作列表。

页面中的快捷问题：

- 帮我规划海报、白皮书和大屏的生产顺序。
- 把这个资产包改成更适合招商路演。
- 指出当前证据链最大的风险。
- 给我三种视觉风格和色系方向。

### 5.6 非 JSON 响应修复

DeepSeek 有时会返回 Markdown 或自然语言，而不是严格 JSON。后端现在已增加防护：

1. 先解析纯 JSON。
2. 再解析 fenced JSON code block。
3. 再从文本中提取 JSON 对象。
4. 如果仍失败，调用 DeepSeek 做一次 JSON 修复。
5. 如果修复仍失败，返回兜底资产包，避免页面中断。

这样用户上传 Markdown 后，即使模型输出不稳定，页面也不会直接报错。

## 6. 当前已验证内容

已执行并通过：

- 前端构建：`npm.cmd run build`
- 后端编译：`.venv/Scripts/python.exe -m compileall backend`
- FastAPI app 导入：`from backend.main import app`
- `git diff --check`

新增 Python 依赖已安装：

- `pypdf`
- `python-docx`
- `openpyxl`

## 7. 当前风险与限制

### 7.1 DeepSeek 输出稳定性

虽然已经增加 JSON 修复和兜底逻辑，但模型输出仍可能存在：

- 字段缺失。
- 风格建议过泛。
- 证据判断偏乐观。
- 对检测指标或认证的真实性无法独立验证。

建议后续加入：

- 更严格的 schema 校验。
- 字段级置信度。
- 人工复核状态。
- 证据来源标注和引用定位。

### 7.2 文档解析限制

当前解析能力以文本提取为主：

- PDF 扫描件无法提取，需要 OCR。
- 图片未 OCR。
- `.xls` 暂未支持。
- 大文件会被限制。

建议后续加入：

- OCR。
- 旧版 Excel 解析。
- 分块分析。
- 文件级引用回溯。

### 7.3 Studio 与资产导入尚未完全打通

目前资产导入页可以生成资产包并跳转 Studio，但还没有把 AI 资产包自动转为 Studio 项目。

建议后续实现：

- `POST /api/studio/projects/from-asset-package`
- 资产包一键生成 Studio 项目。
- 将 DeepSeek 产出的标题、叙事、证据、视觉方向写入 Studio 默认字段。
- 在 Studio 中保留资产包来源记录。

### 7.4 模板体系限制

当前海报模板主题较少：

- 自然绿
- 东方红
- 蓝印花

AI 可以建议更多风格、色系、布局，但前端模板还不能完全执行这些建议。

建议后续扩展：

- 增加模板 schema。
- 支持布局变体。
- 支持色板配置。
- 支持字体和装饰元素配置。
- 支持 AI 生成模板参数，而不只是生成文案。

## 8. 后续开发建议

优先级建议：

1. 资产包一键进入 Studio。
2. Studio 项目保存资产包来源。
3. OCR 支持图片和扫描 PDF。
4. 海报模板参数化。
5. 白皮书和大屏也加入 AI 编辑助手。
6. DeepSeek 输出增加引用定位和人工复核状态。
7. 为资产包增加版本历史。
8. 增加导出：JSON、PDF、PNG、可分享链接。

## 9. 当前模块关系图

```text
用户
  │
  ├─ /import 资产导入页
  │    ├─ 上传 PDF / DOCX / XLSX / CSV / TXT / Markdown / JSON / 图片
  │    ├─ /api/assets/analyze-files
  │    │    ├─ 文件解析
  │    │    ├─ DeepSeek 结构化分析
  │    │    └─ 返回 asset_package
  │    ├─ 展示解析结果、分析步骤、评分、风险、产出建议
  │    ├─ /api/assets/asset-chat
  │    │    └─ 资产包级业务对话
  │    ├─ 复制 / 下载资产包 JSON
  │    └─ 跳转 Studio / 海报 / 白皮书 / 大屏
  │
  ├─ /studio Studio 工作台
  │    ├─ 用户登录校验
  │    ├─ /api/studio/projects
  │    │    └─ 按用户持久化项目
  │    ├─ 海报 / 白皮书 / 大屏编辑
  │    ├─ /api/assets/poster-chat
  │    │    └─ 海报编辑 AI 助手
  │    └─ PNG 导出
  │
  └─ /map /spread /brand /marketing /archive
       └─ 空间展示、传播路径、品牌叙事和交付预览
```

## 10. 结论

当前项目已经形成较清晰的产品化方向：

- 地图模块负责空间证据与食材传播。
- Studio 负责可编辑、可保存、可导出的品牌资产生产。
- 资产导入页负责把外部资料转换为结构化资产包。
- DeepSeek 开始从“分析文本”转向“参与业务流程和编辑决策”。

下一步最关键的是打通“资产包 → Studio 项目”的自动落地，让用户上传资料后可以直接进入可编辑项目，而不是只停留在分析结果展示。
