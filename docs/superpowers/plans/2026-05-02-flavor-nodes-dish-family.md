# 风味节点扩张 & 同族成品联动 · 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把地图节点从"一城一味"升级为"一城多成品 + 跨城同族联动"，新增 9 节点（8 火锅 + 1 烤鸭），使 dish_family 同族 chip 在 Inspector 中可点击 flyTo 兄弟节点。

**Architecture:** 后端在 `app_data.py` 给 FLAVORS 加 `id`/`dish`/`dish_family` 字段 + 追加 9 条新数据；`/api/search` 同步扩展。前端把 `flavors` 列表抬进 Pinia store；`MapInspector` 节点面板换 title/subtitle + 增加"同族成品"chip 区块，点击 chip → `selectNode(sibling)` → MapView 已有 watcher 自动 flyTo。

**Tech Stack:** FastAPI · Pinia · Vue 3 · MapLibre · Deck.gl

**约束**：
- 项目非 git 仓库，所有任务的 "commit" 步骤略过；以"curl 探针 + 目视验收"代替单元测试。
- 启动方式：`.\start.ps1`，前端 5173 / 后端 8001。
- 后端 uvicorn 已 `--reload`，前端 Vite 已 HMR；保存即生效。
- 任务的"运行 / 验证"步骤都假设两端服务已在跑；如未跑请先启动。

**对应 spec：** `docs/superpowers/specs/2026-05-02-flavor-nodes-dish-family-design.md`

---

## File Structure

| 文件 | 责任 | 改动类型 |
|---|---|---|
| `backend/data/app_data.py` | 业务数据 | Modify (回填 8 条 + 追加 9 条) |
| `backend/routers/api.py` | API 路由 | Modify (`/search` 字段扩展、label 改 dish) |
| `src/stores/app.js` | Pinia store | Modify (加 `flavors` state + `setFlavors` action) |
| `src/views/MapView.vue` | 地图视图 | Modify (mounted 时调 `setFlavors`) |
| `src/components/MapInspector.vue` | 右侧面板 | Modify (title/subtitle 调整、新增同族 chip 区块) |

---

## Task 1: app_data.py — 8 条现有节点回填

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\backend\data\app_data.py:3-68`

- [ ] **Step 1: 替换 8 条 FLAVORS 完整列表**

定位 `backend/data/app_data.py` 第 3 行起的 `FLAVORS = [` 列表（共 8 条 dict，到第 68 行 `]` 结束）。整段替换为：

```python
FLAVORS = [
    {
        "id": "chengdu-mala", "city": "成都", "dish": "川蜀麻辣", "dish_family": "火锅",
        "region": "四川盆地", "eco": "亚热带常绿阔叶林",
        "scores": [0.90, 0.95, 0.65, 0.30, 0.20, 0.70],
        "primary": ["麻", "辣"], "vals": [0.90, 0.95],
        "color": "#E5394E", "cat": "辛辣",
        "ingredients": ["花椒", "朝天椒", "郫县豆瓣", "井盐"],
        "coordinates": [104.1, 30.7],
    },
    {
        "id": "shunde-rawfish", "city": "顺德", "dish": "顺德鱼生", "dish_family": None,
        "region": "珠三角河网", "eco": "南亚热带常绿林",
        "scores": [0.05, 0.10, 0.55, 0.25, 0.35, 0.95],
        "primary": ["鲜", "清"], "vals": [0.95, 0.35],
        "color": "#0FB89A", "cat": "鲜甜",
        "ingredients": ["生猛海鲜", "桑基鱼塘", "米酒", "陈皮"],
        "coordinates": [113.3, 22.8],
    },
    {
        "id": "lanzhou-beef-noodle", "city": "兰州", "dish": "兰州牛肉面", "dish_family": None,
        "region": "黄土高原", "eco": "温带草原",
        "scores": [0.20, 0.30, 0.80, 0.45, 0.10, 0.75],
        "primary": ["咸", "鲜"], "vals": [0.80, 0.75],
        "color": "#E8A917", "cat": "咸香",
        "ingredients": ["蓬灰", "牛肉", "白萝卜", "辣子"],
        "coordinates": [103.8, 36.1],
    },
    {
        "id": "xinjiang-naan", "city": "新疆", "dish": "馕与孜然羊", "dish_family": None,
        "region": "塔里木盆地", "eco": "温带荒漠",
        "scores": [0.15, 0.35, 0.70, 0.30, 0.60, 0.55],
        "primary": ["甜", "咸"], "vals": [0.60, 0.70],
        "color": "#E8A917", "cat": "咸香",
        "ingredients": ["哈密瓜", "孜然", "羊脂", "葡萄干"],
        "coordinates": [87.6, 43.8],
    },
    {
        "id": "beijing-roast-duck", "city": "北京", "dish": "北京烤鸭", "dish_family": "烤鸭",
        "region": "华北平原", "eco": "暖温带落叶阔叶林",
        "scores": [0.10, 0.25, 0.80, 0.20, 0.30, 0.65],
        "primary": ["咸", "浓"], "vals": [0.80, 0.65],
        "color": "#8B6A3E", "cat": "咸香",
        "ingredients": ["黄豆酱", "烤鸭", "小葱", "大料"],
        "coordinates": [116.4, 39.9],
    },
    {
        "id": "hangzhou-longjing", "city": "杭州", "dish": "龙井·东坡肉", "dish_family": None,
        "region": "太湖流域", "eco": "中亚热带常绿林",
        "scores": [0.10, 0.15, 0.60, 0.30, 0.75, 0.80],
        "primary": ["甜", "鲜"], "vals": [0.75, 0.80],
        "color": "#0FB89A", "cat": "鲜甜",
        "ingredients": ["龙井茶", "西湖莼菜", "东坡肉", "桂花"],
        "coordinates": [120.2, 30.3],
    },
    {
        "id": "yunnan-stone-tofu", "city": "云南", "dish": "石屏豆腐·宣威火腿", "dish_family": None,
        "region": "横断山区", "eco": "亚热带山地植被",
        "scores": [0.55, 0.65, 0.55, 0.60, 0.45, 0.65],
        "primary": ["野", "酸"], "vals": [0.65, 0.60],
        "color": "#7FA961", "cat": "酸鲜",
        "ingredients": ["石屏豆腐", "宣威火腿", "酸笋", "野菌"],
        "coordinates": [102.7, 25.0],
    },
    {
        "id": "chaoshan-beef-hotpot", "city": "潮汕", "dish": "潮汕牛肉火锅", "dish_family": "火锅",
        "region": "韩江三角洲", "eco": "南亚热带季风林",
        "scores": [0.10, 0.15, 0.60, 0.75, 0.20, 0.90],
        "primary": ["鲜", "酸"], "vals": [0.90, 0.75],
        "color": "#0FB89A", "cat": "酸鲜",
        "ingredients": ["牛肉火锅", "沙茶酱", "鱼露", "反沙芋"],
        "coordinates": [116.7, 23.4],
    },
]
```

- [ ] **Step 2: curl 验证字段已回填**

```bash
curl -s http://localhost:8001/api/flavors | python -c "import json,sys; data=json.load(sys.stdin); print('count:', len(data)); print('first id:', data[0].get('id')); print('beijing dish_family:', next(f for f in data if f['city']=='北京')['dish_family']); print('all have id:', all('id' in f for f in data)); print('all have dish:', all('dish' in f for f in data))"
```

预期输出：
```
count: 8
first id: chengdu-mala
beijing dish_family: 烤鸭
all have id: True
all have dish: True
```

---

## Task 2: app_data.py — 追加 9 条新节点

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\backend\data\app_data.py` （在 Task 1 后修改的 FLAVORS 列表末尾、`]` 之前）

- [ ] **Step 1: 在 FLAVORS `]` 之前插入 9 条新节点**

定位 Task 1 后的 FLAVORS 列表末尾，潮汕节点的 `},` 之后、`]` 之前。插入以下 9 条 dict：

```python
    {
        "id": "chongqing-mala-hotpot", "city": "重庆", "dish": "重庆麻辣火锅", "dish_family": "火锅",
        "region": "嘉陵江畔 · 麻辣牛油锅", "eco": "亚热带常绿阔叶林",
        "scores": [0.95, 0.98, 0.70, 0.20, 0.10, 0.45],
        "primary": ["麻", "辣"], "vals": [0.95, 0.98],
        "color": "#E5394E", "cat": "辛辣",
        "ingredients": ["牛油底料", "毛肚", "鸭肠", "花椒"],
        "coordinates": [106.5, 29.5],
    },
    {
        "id": "haikou-coconut-chicken", "city": "海口", "dish": "椰子鸡火锅", "dish_family": "火锅",
        "region": "琼岛热土 · 椰青清锅", "eco": "热带季雨林",
        "scores": [0.05, 0.05, 0.30, 0.10, 0.65, 0.85],
        "primary": ["甜", "鲜"], "vals": [0.65, 0.85],
        "color": "#0FB89A", "cat": "鲜甜",
        "ingredients": ["椰青", "文昌鸡", "玉米", "胡萝卜"],
        "coordinates": [110.3, 20.0],
    },
    {
        "id": "guangzhou-congee-hotpot", "city": "广州", "dish": "粥底火锅", "dish_family": "火锅",
        "region": "珠江口岸 · 粥底涮", "eco": "南亚热带常绿林",
        "scores": [0.05, 0.10, 0.45, 0.10, 0.15, 0.90],
        "primary": ["鲜", "清"], "vals": [0.90, 0.55],
        "color": "#0FB89A", "cat": "鲜甜",
        "ingredients": ["白粥底", "鱼片", "象拔蚌", "时蔬"],
        "coordinates": [113.27, 23.13],
    },
    {
        "id": "beijing-shuanyangrou", "city": "北京", "dish": "铜锅涮羊肉", "dish_family": "火锅",
        "region": "老北京胡同 · 铜锅清水涮", "eco": "暖温带落叶阔叶林",
        "scores": [0.05, 0.10, 0.65, 0.15, 0.05, 0.85],
        "primary": ["鲜", "咸"], "vals": [0.85, 0.65],
        "color": "#8B6A3E", "cat": "咸香",
        "ingredients": ["内蒙羊脊", "麻酱", "韭菜花", "腐乳"],
        "coordinates": [116.36, 39.95],
    },
    {
        "id": "guiyang-sour-fish-hotpot", "city": "贵阳", "dish": "酸汤鱼火锅", "dish_family": "火锅",
        "region": "云贵高原 · 红酸汤", "eco": "亚热带山地植被",
        "scores": [0.20, 0.65, 0.50, 0.85, 0.10, 0.75],
        "primary": ["酸", "鲜"], "vals": [0.85, 0.75],
        "color": "#7FA961", "cat": "酸鲜",
        "ingredients": ["红酸汤", "稻花鱼", "木姜子", "糟辣椒"],
        "coordinates": [106.7, 26.6],
    },
    {
        "id": "harbin-suancai-bairou", "city": "哈尔滨", "dish": "酸菜白肉锅", "dish_family": "火锅",
        "region": "松花江北岸 · 酸菜白肉", "eco": "温带针阔叶混交林",
        "scores": [0.05, 0.10, 0.55, 0.70, 0.10, 0.65],
        "primary": ["酸", "浓"], "vals": [0.70, 0.65],
        "color": "#7FA961", "cat": "酸鲜",
        "ingredients": ["东北酸菜", "五花肉", "粉条", "血肠"],
        "coordinates": [126.6, 45.7],
    },
    {
        "id": "chuxiong-mushroom-hotpot", "city": "楚雄", "dish": "野生菌火锅", "dish_family": "火锅",
        "region": "横断山菌径 · 野生菌锅", "eco": "亚热带山地针阔混交林",
        "scores": [0.10, 0.15, 0.40, 0.30, 0.30, 0.95],
        "primary": ["鲜", "野"], "vals": [0.95, 0.65],
        "color": "#7FA961", "cat": "酸鲜",
        "ingredients": ["松茸", "鸡枞菌", "牛肝菌", "土鸡汤"],
        "coordinates": [101.0, 25.5],
    },
    {
        "id": "taizhou-yipin-hotpot", "city": "台州", "dish": "海鲜一品锅", "dish_family": "火锅",
        "region": "椒江口 · 海鲜一品", "eco": "中亚热带常绿林",
        "scores": [0.05, 0.10, 0.55, 0.20, 0.40, 0.90],
        "primary": ["鲜", "甜"], "vals": [0.90, 0.40],
        "color": "#0FB89A", "cat": "鲜甜",
        "ingredients": ["东海带鱼", "三门青蟹", "小海螺", "土豆"],
        "coordinates": [121.4, 28.7],
    },
    {
        "id": "nanjing-roast-duck", "city": "南京", "dish": "金陵烤鸭", "dish_family": "烤鸭",
        "region": "金陵秦淮 · 桂花卤鸭", "eco": "北亚热带常绿落叶混交林",
        "scores": [0.05, 0.10, 0.65, 0.10, 0.30, 0.85],
        "primary": ["鲜", "甜"], "vals": [0.85, 0.30],
        "color": "#8B6A3E", "cat": "咸香",
        "ingredients": ["蜜桂花", "湖鸭", "青盐", "陈皮"],
        "coordinates": [118.78, 32.05],
    },
```

- [ ] **Step 2: curl 验证总数与同族分组**

```bash
curl -s http://localhost:8001/api/flavors | python -c "import json,sys; data=json.load(sys.stdin); print('total:', len(data)); print('hotpot family:', sorted(f['id'] for f in data if f.get('dish_family')=='火锅')); print('roast-duck family:', sorted(f['id'] for f in data if f.get('dish_family')=='烤鸭')); print('null family count:', sum(1 for f in data if not f.get('dish_family')))"
```

预期输出：
```
total: 17
hotpot family: ['beijing-shuanyangrou', 'chaoshan-beef-hotpot', 'chengdu-mala', 'chongqing-mala-hotpot', 'chuxiong-mushroom-hotpot', 'guangzhou-congee-hotpot', 'guiyang-sour-fish-hotpot', 'haikou-coconut-chicken', 'harbin-suancai-bairou', 'taizhou-yipin-hotpot']
roast-duck family: ['beijing-roast-duck', 'nanjing-roast-duck']
null family count: 5
```

火锅族 10 个、烤鸭族 2 个、不归族 5 个 = 共 17 ✓

- [ ] **Step 3: 目视验证 9 个新点出现在地图**

刷新 `http://localhost:5173`（`Ctrl+Shift+R` 强刷）。在地图上确认新增节点圆点位置正确：
- 重庆（106.5, 29.5）
- 海口（110.3, 20.0）
- 广州（113.27, 23.13，与顺德相邻偏北）
- 北京老胡同（116.36, 39.95，与现有北京烤鸭相距 ~5km，肉眼可见两个圆点）
- 贵阳（106.7, 26.6）
- 哈尔滨（126.6, 45.7）
- 楚雄（101.0, 25.5，与现有云南节点相距约 100 km）
- 台州（121.4, 28.7）
- 南京（118.78, 32.05）

如某点未出现：先刷新；仍无则检查 `/api/flavors` 是否真返 17 条。

---

## Task 3: api.py — `/search` 字段扩展 + label 改 dish

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\backend\routers\api.py:27-54`

- [ ] **Step 1: 替换整个 `search` 函数**

定位 `backend/routers/api.py` 第 27 行起的 `@router.get("/search")` 装饰器及其下函数（一直到 54 行 `return results[:8]`）。整段替换为：

```python
@router.get("/search")
def search(q: str = ""):
    q = q.strip()
    if not q:
        return []

    results = []
    for f in FLAVORS:
        haystack_fields = [
            f.get("city", ""),
            f.get("region", ""),
            f.get("eco", ""),
            f.get("dish", ""),
            f.get("dish_family") or "",
        ]
        primary_hit = any(q in p for p in f.get("primary", []))
        if any(q in field for field in haystack_fields) or primary_hit:
            results.append({
                "type": "node",
                "label": f.get("dish") or f["city"],
                "sub": f"{f['city']} · {f['region']}",
                "color": f["color"],
                "data": f,
            })
    for r in ROUTES:
        if q in r["name"]:
            results.append({
                "type": "route",
                "label": r["name"],
                "sub": "海路传播" if r["type"] == "sea" else "陆路传播",
                "color": r["color"],
                "data": r,
            })

    return results[:8]
```

- [ ] **Step 2: curl 验证 dish_family 检索**

```bash
curl -s "http://localhost:8001/api/search?q=烤鸭" | python -c "import json,sys; data=json.load(sys.stdin); print('count:', len(data)); print('labels:', [r['label'] for r in data])"
```

预期：
```
count: 2
labels: ['北京烤鸭', '金陵烤鸭']
```

- [ ] **Step 3: curl 验证多 北京 节点都返**

```bash
curl -s "http://localhost:8001/api/search?q=北京" | python -c "import json,sys; data=json.load(sys.stdin); print('count:', len(data)); print('labels:', [r['label'] for r in data]); print('subs:', [r['sub'] for r in data])"
```

预期 count ≥ 2，labels 含 `北京烤鸭` 和 `铜锅涮羊肉`，subs 含 `北京 · 华北平原` 和 `北京 · 老北京胡同 · 铜锅清水涮`。

- [ ] **Step 4: curl 验证 火锅 跨族搜索**

```bash
curl -s "http://localhost:8001/api/search?q=火锅" | python -c "import json,sys; data=json.load(sys.stdin); print('count:', len(data)); print('labels:', [r['label'] for r in data])"
```

预期 count = 8（上限截断）。labels 应为 dish 含"火锅"或归属"火锅" family 的节点子集。

---

## Task 4: stores/app.js — 加 `flavors` state + `setFlavors` action

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\src\stores\app.js`

- [ ] **Step 1: 在 state 中加 flavors 字段**

定位 `src/stores/app.js:4-10`，整段 `state: () => ({...})` 替换为：

```js
  state: () => ({
    flavors: [],
    selectedNode: null,
    selectedRoute: null,
    selectedEcozone: null,
    currentChapter: 0,
    searchQuery: '',
  }),
```

- [ ] **Step 2: 在 actions 中加 setFlavors action**

定位 `src/stores/app.js:11`（`actions: {`），在其下、`selectNode(node) {` 之前插入：

```js
    setFlavors(list) {
      this.flavors = Array.isArray(list) ? list : []
    },
```

最终 actions 块应起始为：

```js
  actions: {
    setFlavors(list) {
      this.flavors = Array.isArray(list) ? list : []
    },
    selectNode(node) {
      this.selectedNode = node
      this.selectedRoute = null
      this.selectedEcozone = null
    },
    ...
```

- [ ] **Step 3: Vite 编译无报错**

保存后观察 Vite dev 终端 + 浏览器：终端无 `Failed to compile` 报错；浏览器强刷后页面正常加载、地图节点仍显示 17 个。本 step 只做编译/加载检查，store 内 flavors 是否真填充将在 Task 6 通过同族 chip 出现来间接验证。

---

## Task 5: MapView.vue — mounted 时调 setFlavors

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\src\views\MapView.vue:218-225`

- [ ] **Step 1: 在 fetch 后调 setFlavors**

定位 `src/views/MapView.vue:218-225`（`onMounted(async () => {` 起始的那一段）。原文：

```js
onMounted(async () => {
  const [fRes, rRes] = await Promise.all([fetch('/api/flavors'), fetch('/api/routes')])
  flavors = await fRes.json()
  routes  = await rRes.json()

  // Check if raster is ready (might still be extracting on first run)
  fetch('/tiles/status').then(r => r.json()).then(s => {
    rasterReady.value = s.raster_ready
  })
```

替换为：

```js
onMounted(async () => {
  const [fRes, rRes] = await Promise.all([fetch('/api/flavors'), fetch('/api/routes')])
  flavors = await fRes.json()
  routes  = await rRes.json()
  appStore.setFlavors(flavors)

  // Check if raster is ready (might still be extracting on first run)
  fetch('/tiles/status').then(r => r.json()).then(s => {
    rasterReady.value = s.raster_ready
  })
```

（仅新增 `appStore.setFlavors(flavors)` 这一行）

- [ ] **Step 2: 浏览器 Console 无报错**

强刷页面，打开 DevTools Console，确认无 `appStore.setFlavors is not a function` 报错；地图上仍显示 17 个节点圆点；点击任一节点，Inspector 仍正常打开（虽然此时还未加同族区块）。store 真实填充情况将在 Task 6 通过同族 chip 显现。

---

## Task 6: MapInspector.vue — Node 面板升级（title/subtitle/同族 chip）

**Files:**
- Modify: `E:\大学\大三下\GIS开发\Food\src\components\MapInspector.vue:16-47`（template 中 node panel 段）
- Modify: `E:\大学\大三下\GIS开发\Food\src\components\MapInspector.vue:102-111`（script 段加 siblings computed）

- [ ] **Step 1: 替换 node panel 模板**

定位 `src/components/MapInspector.vue:16-47`，原文：

```html
      <!-- Node panel -->
      <div v-else-if="selectedNode" key="node" class="panel-content">
        <div class="panel-tab">风味节点</div>
        <div class="panel-title">{{ selectedNode.city }}</div>
        <div class="panel-subtitle">{{ selectedNode.region }} · {{ selectedNode.eco }}</div>

        <div class="section-label">风味雷达图</div>
        <div class="radar-wrap">
          <FlavorRadar :scores="selectedNode.scores" :color="selectedNode.color" :size="148" :animated="true" />
        </div>

        <div class="section-label">维度得分</div>
        <div class="score-bars">
          <div v-for="(dim, i) in dims" :key="dim" class="score-row">
            <span class="score-dim">{{ dim }}</span>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{ width: (selectedNode.scores[i] * 100) + '%', background: selectedNode.color }"
              />
            </div>
            <span class="score-num">{{ selectedNode.scores[i].toFixed(2) }}</span>
          </div>
        </div>

        <div class="section-label" style="margin-top:16px">食材基因</div>
        <div class="chips">
          <span v-for="ing in selectedNode.ingredients" :key="ing" class="chip"
            :style="{ background: selectedNode.color + '18', color: selectedNode.color }">
            {{ ing }}
          </span>
        </div>
      </div>
```

整段替换为：

```html
      <!-- Node panel -->
      <div v-else-if="selectedNode" key="node" class="panel-content">
        <div class="panel-tab">风味节点</div>
        <div class="panel-title">{{ selectedNode.dish || selectedNode.city }}</div>
        <div class="panel-subtitle">{{ selectedNode.city }} · {{ selectedNode.region }} · {{ selectedNode.eco }}</div>

        <div class="section-label">风味雷达图</div>
        <div class="radar-wrap">
          <FlavorRadar :scores="selectedNode.scores" :color="selectedNode.color" :size="148" :animated="true" />
        </div>

        <div class="section-label">维度得分</div>
        <div class="score-bars">
          <div v-for="(dim, i) in dims" :key="dim" class="score-row">
            <span class="score-dim">{{ dim }}</span>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{ width: (selectedNode.scores[i] * 100) + '%', background: selectedNode.color }"
              />
            </div>
            <span class="score-num">{{ selectedNode.scores[i].toFixed(2) }}</span>
          </div>
        </div>

        <div class="section-label" style="margin-top:16px">食材基因</div>
        <div class="chips">
          <span v-for="ing in selectedNode.ingredients" :key="ing" class="chip"
            :style="{ background: selectedNode.color + '18', color: selectedNode.color }">
            {{ ing }}
          </span>
        </div>

        <template v-if="siblings.length">
          <div class="section-label" style="margin-top:16px">同族成品 · {{ selectedNode.dish_family }}</div>
          <div class="chips">
            <span v-for="sib in siblings" :key="sib.id" class="chip chip-clickable"
              :style="{ background: sib.color + '18', color: sib.color }"
              @click="appStore.selectNode(sib)">
              {{ sib.city }} · {{ sib.dish }}
            </span>
          </div>
        </template>
      </div>
```

- [ ] **Step 2: 在 `<script setup>` 中加 siblings computed**

定位 `src/components/MapInspector.vue:102-111`，原文：

```js
<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app.js'
import FlavorRadar from './FlavorRadar.vue'

const appStore = useAppStore()
const selectedNode   = computed(() => appStore.selectedNode)
const selectedRoute  = computed(() => appStore.selectedRoute)
const selectedEcozone = computed(() => appStore.selectedEcozone)
const dims = ['麻', '辣', '咸', '酸', '甜', '鲜']
```

替换为：

```js
<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app.js'
import FlavorRadar from './FlavorRadar.vue'

const appStore = useAppStore()
const selectedNode   = computed(() => appStore.selectedNode)
const selectedRoute  = computed(() => appStore.selectedRoute)
const selectedEcozone = computed(() => appStore.selectedEcozone)
const dims = ['麻', '辣', '咸', '酸', '甜', '鲜']

const siblings = computed(() => {
  const node = appStore.selectedNode
  if (!node || !node.dish_family) return []
  return appStore.flavors.filter(f => f.dish_family === node.dish_family && f.id !== node.id)
})
```

- [ ] **Step 3: 在 `<style scoped>` 中加 chip-clickable 样式**

定位 `src/components/MapInspector.vue` 中的 `.chip { padding: 4px 12px; border-radius: 12px; font-size: 11px; }` 那一行（约第 183 行）。在该行之后插入：

```css
.chip-clickable { cursor: pointer; transition: transform 150ms ease, opacity 150ms ease; }
.chip-clickable:hover { transform: translateY(-1px); opacity: 0.85; }
```

- [ ] **Step 4: 目视验证 同族联动**

强刷页面，按下列步骤操作：

1. 点击地图上 **北京烤鸭** 节点（116.4, 39.9）
   - 期望：面板标题 "北京烤鸭"，副标题 "北京 · 华北平原 · 暖温带落叶阔叶林"
   - 期望：底部出现 "同族成品 · 烤鸭" 区块，含 1 个 chip "南京 · 金陵烤鸭"

2. 点击 chip "南京 · 金陵烤鸭"
   - 期望：相机平滑 flyTo 至 [118.78, 32.05]
   - 期望：面板自动切换为 "金陵烤鸭"，底部 chip 反向显示 "北京 · 北京烤鸭"

3. 点击地图上 **重庆** 节点（106.5, 29.5）
   - 期望：面板标题 "重庆麻辣火锅"，底部 "同族成品 · 火锅" 区块出现 9 个 chip（除自身外的全部火锅成员）

4. 点击地图上 **顺德** / **杭州** 等不归族节点
   - 期望：底部不出现 "同族成品" 区块

5. 点击同族中 **任一 chip**（例如重庆面板里点 "成都 · 川蜀麻辣"）
   - 期望：相机飞向成都，面板切换，新的同族 chip 区块包含其它 9 个火锅成员（含 "重庆 · 重庆麻辣火锅"）

如果 chip 不出现：DevTools Console 检查 `useAppStore().flavors.length` 是否为 17；若为 0 → Task 5 未生效。

---

## Task 7: 端到端验收

**Files:** （无文件修改）

- [ ] **Step 1: 后端总检**

```bash
curl -s http://localhost:8001/api/flavors | python -c "import json,sys; d=json.load(sys.stdin); assert len(d)==17, len(d); assert all('id' in x and 'dish' in x for x in d); print('OK 17 nodes, all have id+dish')"
```

预期输出：`OK 17 nodes, all have id+dish`

- [ ] **Step 2: 前端图层无回归**

强刷页面，确认下列已有功能仍正常：

- HYP 栅格底图加载完成
- 海岸线 / 河流 / 生态区边界 三层正常显示
- 5 条路径暗线渲染（含 sea 虚线 / land 实线，from 上一轮）
- 流光粒子运动正常
- 点击生态区边界 → 切到 L1 自然生态档案面板
- 悬停节点 / 路径 → tooltip 正常

- [ ] **Step 3: 浏览器 Console 无报错**

打开 DevTools Console，刷新页面，确认无下列报错：
- `Cannot read property 'flavors' of undefined`
- `appStore.setFlavors is not a function`
- `Cannot read property 'dish_family' of undefined`

- [ ] **Step 4: 对照 spec §8 验收清单逐项确认**

参考 `docs/superpowers/specs/2026-05-02-flavor-nodes-dish-family-design.md` §8 测试与验收：

- [ ] §8.1 后端 4 项 curl 全部通过
- [ ] §8.2 目视 6 项全部通过
- [ ] §8.3 回归 3 项全部通过

---
