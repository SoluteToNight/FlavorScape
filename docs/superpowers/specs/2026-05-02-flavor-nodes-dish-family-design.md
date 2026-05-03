# 风味节点扩张 & 同族成品联动 · 设计稿

**日期**：2026-05-02
**作者**：Claude (Opus 4.7) + 项目所有者
**目标**：把地图节点从"一城一味"升级为"一城多成品 + 跨城同族联动"，新增 9 个节点（8 个火锅家族 + 1 个烤鸭兄弟），让"同源异构"这一品牌叙事在地图上真的可被看见、可被走通。

---

## 一、动机与原则

现状：`FLAVORS` 8 条，隐含"每座城只有一个代表性风味"的假设。这与博物志的核心哲学相悖——真实地理空间里，**北京既有烤鸭也有铜锅涮羊肉**，**北京烤鸭与金陵烤鸭明显是同源演化**。模型应当：

1. **一城多成品**：同一城市可有多个节点，各表达一种成品风味基因。
2. **跨城同源联动**：同一菜系（"烤鸭"、"火锅"）跨城的多个节点视为同族，可在 UI 上互链 fly。
3. **向后兼容**：现有 8 条数据不丢失，只补字段、不改语义。

---

## 二、可选方案（trade-offs）

| 方案 | 描述 | 优势 | 劣势 | 决策 |
|---|---|---|---|---|
| **A. FLAVORS 内嵌 dish/dish_family** | 现有 schema 加 `id`/`dish`/`dish_family` 三个字段，多节点同城合法 | 改动小、零迁移成本、字段语义一目了然 | FLAVORS 同时承担"城市档案"和"具体菜品"两层含义，长期可能臃肿 | **采纳** |
| B. 拆分 DISHES 表，FLAVORS 仅留城市 | 引入 `DISHES` 列表，每条 dish 引用一个 city；FLAVORS 退化为"城市 + 生态" | 模型最纯粹 | 前端要 join 两份数据；现有 FLAVORS 全部需改写 | 拒绝（YAGNI） |
| C. 不动 FLAVORS，加并行 HOTPOTS 数组 | 火锅作为独立图层 | 隔离干净 | 无法表达"烤鸭"的跨城同族；多类菜品时数组会爆炸 | 拒绝 |

---

## 三、数据模型升级（FLAVORS schema）

### 3.1 字段定义

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | `str` | **新增·必填** | 全库唯一稳定 ID，命名 `<city-pinyin>-<dish-key>`，如 `"beijing-roast-duck"`、`"chongqing-mala-hotpot"`。是后续 Inspector 同族 chip 的引用键。 |
| `dish` | `str` | **新增·必填** | 成品菜名，作为新的 `panel-title`（替代 city） |
| `dish_family` | `str \| null` | **新增·可选** | 跨城同族键，例 `"火锅"`、`"烤鸭"`；同值的节点互为兄弟 |
| `city` | `str` | 保留 | 仍作行政地标，移到 `panel-subtitle` 显示 |
| `region` `eco` `scores` `primary` `vals` `color` `cat` `ingredients` `coordinates` | 保留 | 不变 |

### 3.2 唯一性约束

- `id` 必须全库唯一
- `(city, dish)` 元组必须唯一（防止重复条目）
- `coordinates` 同城多节点错峰 ≥ 0.03°（约 3 km），避免 ScatterplotLayer 完全重叠

### 3.3 现有 8 条回填表

| 原 city | 新 id | 新 dish | dish_family | 备注 |
|---|---|---|---|---|
| 成都 | `chengdu-mala` | `川蜀麻辣` | `"火锅"` | 麻辣火锅基因之源，归入火锅同族 |
| 顺德 | `shunde-rawfish` | `顺德鱼生` | `null` | |
| 兰州 | `lanzhou-beef-noodle` | `兰州牛肉面` | `null` | |
| 新疆 | `xinjiang-naan` | `馕与孜然羊` | `null` | |
| 北京 | `beijing-roast-duck` | `北京烤鸭` | `"烤鸭"` | 与 金陵烤鸭 互链 |
| 杭州 | `hangzhou-longjing` | `龙井·东坡肉` | `null` | |
| 云南 | `yunnan-stone-tofu` | `石屏豆腐·宣威火腿` | `null` | 现有云南位 [102.7, 25.0]，新菌菇火锅在楚雄 [101.0, 25.5] 错峰 |
| 潮汕 | `chaoshan-beef-hotpot` | `潮汕牛肉火锅` | `"火锅"` | 现有 ingredients 已含"牛肉火锅"，自然加入火锅家族 |

### 3.4 新增 9 条节点

> 6-d scores 顺序：`[麻, 辣, 咸, 酸, 甜, 鲜]`（与 MapInspector 的 `dims` 对齐）

#### 火锅家族（dish_family="火锅"，8 条新）

| id | city | dish | coords | scores | primary / vals | color / cat | region 字面 | ingredients |
|---|---|---|---|---|---|---|---|---|
| `chongqing-mala-hotpot` | 重庆 | 重庆麻辣火锅 | [106.5, 29.5] | [0.95, 0.98, 0.70, 0.20, 0.10, 0.45] | 麻 0.95 / 辣 0.98 | `#E5394E` 辛辣 | 嘉陵江畔 · 麻辣牛油锅 | 牛油底料、毛肚、鸭肠、花椒 |
| `haikou-coconut-chicken` | 海口 | 椰子鸡火锅 | [110.3, 20.0] | [0.05, 0.05, 0.30, 0.10, 0.65, 0.85] | 甜 0.65 / 鲜 0.85 | `#0FB89A` 鲜甜 | 琼岛热土 · 椰青清锅 | 椰青、文昌鸡、玉米、胡萝卜 |
| `guangzhou-congee-hotpot` | 广州 | 粥底火锅 | [113.27, 23.13] | [0.05, 0.10, 0.45, 0.10, 0.15, 0.90] | 鲜 0.90 / 清 0.55 | `#0FB89A` 鲜甜 | 珠江口岸 · 粥底涮 | 白粥底、鱼片、象拔蚌、时蔬 |
| `beijing-shuanyangrou` | 北京 | 铜锅涮羊肉 | [116.36, 39.95] | [0.05, 0.10, 0.65, 0.15, 0.05, 0.85] | 鲜 0.85 / 咸 0.65 | `#8B6A3E` 咸香 | 老北京胡同 · 铜锅清水涮 | 内蒙羊脊、麻酱、韭菜花、腐乳 |
| `guiyang-sour-fish-hotpot` | 贵阳 | 酸汤鱼火锅 | [106.7, 26.6] | [0.20, 0.65, 0.50, 0.85, 0.10, 0.75] | 酸 0.85 / 鲜 0.75 | `#7FA961` 酸鲜 | 云贵高原 · 红酸汤 | 红酸汤、稻花鱼、木姜子、糟辣椒 |
| `harbin-suancai-bairou` | 哈尔滨 | 酸菜白肉锅 | [126.6, 45.7] | [0.05, 0.10, 0.55, 0.70, 0.10, 0.65] | 酸 0.70 / 浓 0.65 | `#7FA961` 酸鲜 | 松花江北岸 · 酸菜白肉 | 东北酸菜、五花肉、粉条、血肠 |
| `chuxiong-mushroom-hotpot` | 楚雄 | 野生菌火锅 | [101.0, 25.5] | [0.10, 0.15, 0.40, 0.30, 0.30, 0.95] | 鲜 0.95 / 野 0.65 | `#7FA961` 酸鲜 | 横断山菌径 · 野生菌锅 | 松茸、鸡枞菌、牛肝菌、土鸡汤 |
| `taizhou-yipin-hotpot` | 台州 | 海鲜一品锅 | [121.4, 28.7] | [0.05, 0.10, 0.55, 0.20, 0.40, 0.90] | 鲜 0.90 / 甜 0.40 | `#0FB89A` 鲜甜 | 椒江口 · 海鲜一品 | 东海带鱼、三门青蟹、小海螺、土豆 |

#### 烤鸭家族（dish_family="烤鸭"，1 条新）

| id | city | dish | coords | scores | primary / vals | color / cat | region | ingredients |
|---|---|---|---|---|---|---|---|---|
| `nanjing-roast-duck` | 南京 | 金陵烤鸭 | [118.78, 32.05] | [0.05, 0.10, 0.65, 0.10, 0.30, 0.85] | 鲜 0.85 / 甜 0.30 | `#8B6A3E` 咸香 | 金陵秦淮 · 桂花卤鸭 | 蜜桂花、湖鸭、青盐、陈皮 |

### 3.5 同族汇总

| dish_family | 成员 ids |
|---|---|
| `火锅` | `chongqing-mala-hotpot`, `haikou-coconut-chicken`, `guangzhou-congee-hotpot`, `beijing-shuanyangrou`, `guiyang-sour-fish-hotpot`, `harbin-suancai-bairou`, `chuxiong-mushroom-hotpot`, `taizhou-yipin-hotpot`, `chengdu-mala` (现有), `chaoshan-beef-hotpot` (现有) → 共 10 |
| `烤鸭` | `beijing-roast-duck` (现有), `nanjing-roast-duck` → 共 2 |

---

## 四、后端调整

### 4.1 `backend/data/app_data.py`

- FLAVORS 8 条回填 `id`/`dish`/`dish_family` 三个字段
- 追加 9 条新节点（火锅 8 + 烤鸭 1），坐标 / scores / primary / vals / color / cat / ingredients 严格按 §3.4 表格

### 4.2 `backend/routers/api.py` —— /api/search 增强

- 搜索字段扩展：`city / region / eco / primary / dish / dish_family`
- 结果 `label` 字段：从 `f["city"]` 改为 `f["dish"]`，`sub` 字段从 `f["region"]` 改为 `f["city"] + " · " + f["region"]`，避免 "北京/北京" 重名
- 上限仍 8 条

### 4.3 不变项

- `/tiles/*` 一切不变
- `/api/routes` `/api/chapters` `/api/data-sources` 一切不变

---

## 五、前端调整

### 5.1 `src/components/MapInspector.vue` —— Node 面板

- `panel-title` 由 `selectedNode.city` 改为 `selectedNode.dish`
- `panel-subtitle` 由 `region · eco` 改为 `selectedNode.city + ' · ' + selectedNode.region + ' · ' + selectedNode.eco`
- **新增"同族成品"区块**（仅当 `selectedNode.dish_family` 非空时显示）：
  - section-label = `同族成品 · ${selectedNode.dish_family}`
  - chip 列表：从 `appStore.flavors` 中筛选 `dish_family === selectedNode.dish_family && id !== selectedNode.id` 的兄弟节点
  - 每个 chip 文案 = `${node.city} · ${node.dish}`（如"南京 · 金陵烤鸭"），避免同族跨城重名时指代不明；背景色 = `node.color + '18'`，前景色 = `node.color`
  - chip click → `appStore.selectNode(node)` → 触发 MapView 已有 watcher 自动 flyTo + 切换面板

### 5.2 `src/stores/app.js`

- `flavors` 从 setter（在 MapView mounted 时 `appStore.flavors = await fRes.json()`）变成 store 内部 state；MapInspector 直接读取
- 现状是否已经在 store 中？若未导出，加一个 `setFlavors(list)` action 与 `flavors` state（与现有 selectedNode 等保持同位）

### 5.3 `src/views/MapView.vue`

- 在 mounted 流程把 `flavors`、`routes` 同步进 store（`appStore.setFlavors(flavors)` 之类），让 Inspector 可枚举兄弟节点
- ScatterplotLayer 数据源不变（`flavors` 直接来自 store 或 const）

### 5.4 layerLegend / dims / 其它视觉

- 不动。dish_family chip 复用现有 chip 样式（与"食材基因" chips 一致），保持博物志风格。

---

## 六、数据流

```
后端 startup → app_data.FLAVORS (含新字段) ── /api/flavors ──▶ MapView.mounted
                                                                     │
                                                                     ├─ scatterplot 数据
                                                                     │
                                                                     └─ store.setFlavors(list)
                                                                              │
                                                                              ▼
                                                          MapInspector.computed siblings
                                                          = flavors.filter(f => f.dish_family === selectedNode.dish_family && f.id !== selectedNode.id)
                                                                              │
                                                            (chip click) ─────▶ store.selectNode(sibling)
                                                                              │
                                                                              ▼
                                                          MapView watcher → map.flyTo(sibling.coordinates)
                                                          MapInspector reactively re-renders
```

---

## 七、错误与边界

| 情形 | 处理 |
|---|---|
| `dish_family` 为 `null` | 不显示 "同族成品" 区块 |
| `dish_family` 在库中只剩自己 | 不显示（filter 后空数组） |
| 同族包含 ≥ 6 个 chip 撑面板 | flex-wrap 换行，与"食材基因"一致；不限定上限 |
| 两节点同城坐标接近 | ScatterplotLayer 默认按数组顺序渲染，后渲染者覆盖。已通过 ≥ 0.03° 错峰减轻 |
| 用户点击同族 chip 时已经选中该 chip 节点 | `selectNode` 是幂等 setter，watcher 不会 re-fly（值未变）；UI 无明显反馈，可接受 |
| /api/search "北京" 返回 2 条 | 是预期行为（北京烤鸭 + 涮羊肉），label 用 dish 区分 |

---

## 八、测试与验收

### 8.1 后端

- `curl /api/flavors` 返回 17 条（8 旧 + 9 新），每条含 `id`、`dish` 字段
- `curl /api/search?q=烤鸭` 返回 2 条（北京烤鸭、金陵烤鸭），label 字段为 dish 名
- `curl /api/search?q=北京` 返回 ≥ 2 条（北京烤鸭、北京铜锅涮羊肉）
- `curl /api/search?q=火锅` 返回 ≥ 5 条（凡 dish 含"火锅"或 dish_family="火锅"的节点）

### 8.2 前端目视

- 地图初次加载，新 9 个圆点正确出现在对应坐标，颜色符合 cat
- 北京区域可见两枚相距约 5km 的点（烤鸭 + 涮羊肉），各自可独立点击
- 点击 北京烤鸭 → 面板标题"北京烤鸭"，副标题"北京 · 华北平原 · 暖温带落叶阔叶林"
- 面板底部出现 "同族成品 · 烤鸭" chip，内含 "金陵烤鸭"
- 点击 "金陵烤鸭" chip → 相机飞至 [118.78, 32.05]，面板切到金陵烤鸭，底部 chip 反向显示 "北京烤鸭"
- 点击任一火锅节点 → 同族 chip 显示其它 9 个火锅成员（重庆/海口/广州/北京涮/贵阳/哈尔滨/楚雄菌/台州/成都/潮汕牛肉 中除自身外的 9 个）
- 点击 顺德/兰州/新疆/杭州/云南 等不属于任何 family 的节点 → 不显示"同族成品"区块
- /api/search 输入框搜"烤鸭" → 下拉 2 项；点击 "金陵烤鸭" → 飞过去

### 8.3 回归

- 现有路径暗线、流光、生态区、左侧图例 全部不变
- 现有 8 个旧节点仍可点击，radar/score-bars/食材chips 渲染正常
- L1 生态区点击仍切到 ecozone 面板

---

## 九、不做（out of scope）

- 不新增 ROUTES / CHAPTERS（用户明确只加节点）
- 不引入"按 family 高亮整族"的多选交互（仅单点 chip flyTo）
- 不修改风味雷达图的 6 维定义
- 不增加 dish 缩略图
- 不为 dish_family 引入颜色编码（chip 仍用各节点自身 color，保持视觉一致性）

---

## 十、实施顺序（先后端、再前端，最小往返）

1. 后端 `app_data.py` 回填 + 新增 9 条
2. 后端 `routers/api.py` /search 改造（label/sub/字段扩展）
3. 前端 `stores/app.js` 加 `flavors` state + `setFlavors` action
4. 前端 `MapView.vue` mounted 时调 `setFlavors`
5. 前端 `MapInspector.vue` 改 panel-title/subtitle + 同族 chip 区块
6. 端到端验收（§8.1 + §8.2 + §8.3）
