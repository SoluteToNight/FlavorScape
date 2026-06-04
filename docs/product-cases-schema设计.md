# product_cases JSON Schema — 字段设计 (v2)

> 本文档定义 `data/product_cases/*.json` 的统一数据结构。
> **核心架构**：JSON 分为两层 — **空间底板**（GIS 事实，不可变）+ **创作默认值**（用户可覆盖的起点）。

---

## 0. 架构理念

```
产品 JSON                          Studio 项目状态（Pinia）        导出产物
────────                          ────────────────────          ────────
空间底板（不可变）                  用户编辑覆盖层                  合并渲染
  ├ 坐标、气候、检测报告             ├ 修改后的标题文案              → 海报 PNG
  ├ 供应链节点位置                  ├ 选择的海报风格                → 白皮书 PDF
  └ 风味指纹数值                   ├ 可见节点清单                 → 大屏嵌入代码
                                  └ 自定义主图
创作默认值（可编辑起点）
  ├ 建议标题文案
  ├ 推荐风格
  └ 预设叙事文本
```

- **产品 JSON 提供「起点」**：空间事实 + 建议文案，让用户不需要从零开始
- **Studio 是「画布」**：用户在 JSON 默认值之上编辑、配置、设计
- **导出是「产出」**：合并两层数据，生成最终产物

---

## 1. 设计原则

1. **一个产品 = 一个 JSON 文件**，文件名用产品 ID（如 `hanyuan-pepper.json`）
2. 每个模块拆为 `spatial`（不可变）+ `creative`（可编辑默认值）两个子对象
3. `creative` 字段标注 `type`、`maxLength`、`options` 等元信息，供 Studio 编辑面板使用
4. 坐标统一使用 `[lng, lat]`（EPSG:4326）
5. 面向现有实际消费字段设计，不超前抽象

---

## 2. TypeScript 接口定义

```typescript
// ═══════════════════════════════════════════════════════
// 顶层
// ═══════════════════════════════════════════════════════

interface ProductCase {
  // ─── §1 通用标识（不可变）───
  id: string;
  name: string;
  nameEn?: string;
  category: string;
  province: string;
  heroImage: string;
  species?: string;
  origin: string;
  originCoord: [number, number];

  // ─── §2 品牌色彩（不可变）───
  colors: {
    primary: string;        // 主色，用于图表 / 标题高亮
    accent: string;         // 辅色
  };

  // ─── §3 各模块 ───
  marketing: MarketingModule;
  archive: ArchiveModule;
  display: DisplayModule;
  spread: SpreadModule;
  studio: StudioMeta;
}

// ═══════════════════════════════════════════════════════
// §3 营销海报模块
// ═══════════════════════════════════════════════════════

interface MarketingModule {
  /** 空间底板 — GIS 事实，用户不可改 */
  spatial: {
    /** 供应链关键节点（用于海报地图标注） */
    nodes: SupplyChainNode[];
    /** 核心指标数据（海报底部卡片的数据来源） */
    evidence: EvidenceItem[];
  };

  /** 创作默认值 — 用户可覆盖的起点 */
  creative: {
    /** 产品描述短句 */
    desc: EditableField<"text", 60>;
    /** 诗意短句（装饰文字） */
    poeticLine: EditableField<"text", 40>;
    /** 叙事文本（支持 HTML 高亮标签） */
    narrative: EditableField<"rich-text", 300>;
    /** 海报风格 */
    theme: EditableSelect<["nature", "heritage", "indigo"]>;
    /** 社交媒体文案 */
    copy: {
      xiaohongshu: EditableField<"text", 200>;
      ecommerce: EditableField<"text", 200>;
    };
  };
}

interface SupplyChainNode {
  short: string;            // 短名，如 "汉源"
  coord: [number, number];
  desc?: string;            // 采样点描述（ArchiveView 用）
}

interface EvidenceItem {
  label: string;            // "芳香挥发油"
  value: string;            // "≥ 5.5%"
}

// ═══════════════════════════════════════════════════════
// §4 实证白皮书模块
// ═══════════════════════════════════════════════════════

interface ArchiveModule {
  /** 空间底板 — GIS 事实 + 检测数据 */
  spatial: {
    originPoint: {
      name: string;
      coord: [number, number];
      precision: string;
    };
    /** 白皮书指标数据 */
    metrics: ArchiveMetric[];
    /** 气候数据（12 个月降水量 + 气温） */
    climate: {
      rain: number[];
      temp: number[];
    };
    /** 有效积温（生长阶段） */
    heat: HeatStage[];
    /** 品质对标国标雷达图 */
    qualityBenchmark: {
      labels: string[];
      values: number[];
    };
    /** 风味指纹（FlavorRadar 6 维） */
    flavor: {
      scores: number[];     // [麻, 辣, 咸, 酸, 甜, 鲜]
    };
    /** 第三方检测报告 */
    reports: LabReport[];
    /** 气象站代码（仅装饰） */
    stationCode: string;
  };

  /** 创作默认值 */
  creative: {
    /** 风味文字总结 */
    flavorSummary: EditableField<"text", 150>;
    /** 产品 origin 描述 */
    originDesc: EditableField<"text", 80>;
  };
}

interface ArchiveMetric {
  label: string;
  value: string;
  note: string;
}

interface HeatStage {
  stage: string;
  value: number;
}

interface LabReport {
  org: string;
  result: string;
  code: string;
}

// ═══════════════════════════════════════════════════════
// §5 智慧大屏模块
// ═══════════════════════════════════════════════════════

interface DisplayModule {
  /** 空间底板 */
  spatial: {
    /** 大屏叙事节点（5 个固定阶段：产地→加工→仓储→市场→餐桌） */
    stages: DisplayStage[];
    /** 身份信息 */
    identity: IdentityItem[];
  };

  /** 创作默认值 */
  creative: {
    /** 节点可见性默认值 */
    visibleNodeIds: string[];
    /** 默认镜头模式 */
    cameraMode: EditableSelect<["tour", "origin", "market", "dining"]>;
    /** 每个节点的叙事文本，用户可编辑 */
    stageStories: Record<string, EditableField<"text", 200>>;
  };
}

interface DisplayStage {
  id: string;               // "origin" | "process" | "storage" | "market" | "dining"
  coord: [number, number];
  short: string;            // "源起产地"
  type: string;             // "核心产区"
  name: string;             // "大渡河干热河谷贡椒区"
  color: string;            // "#8b9a76"
  evidence: string;         // "国家地理标志保护产品"
}

interface IdentityItem {
  label: string;
  value: string;
}

// ═══════════════════════════════════════════════════════
// §6 传播图谱模块
// ═══════════════════════════════════════════════════════

interface SpreadModule {
  /** 空间底板 — 引用 data/ingredient/*.json */
  spatial: {
    /** 关联的食材 ID */
    ingredientId: string;
  };

  /** 创作默认值 */
  creative: {
    /** 100 字传播短文案 */
    storySummary: EditableField<"text", 100>;
    /** 300 字品牌故事 */
    brandStory: EditableField<"text", 300>;
    /** 展陈讲解稿 */
    exhibitionScript: EditableField<"text", 500>;
  };
}

// ═══════════════════════════════════════════════════════
// §7 Studio 元数据
// ═══════════════════════════════════════════════════════

interface StudioMeta {
  /** 适用场景标签 */
  brandScenario: string;
  /** 推荐产出物列表 */
  recommendedOutputs: Array<"poster" | "archive" | "display" | "spread">;
  /** 品牌名称（导入流程用） */
  brandName?: string;
}

// ═══════════════════════════════════════════════════════
// 通用编辑字段类型
// ═══════════════════════════════════════════════════════

/** 可编辑文本字段 */
interface EditableField<T extends "text" | "rich-text", L extends number> {
  default: string;          // 默认值（JSON 提供的起点）
  type: T;                  // 编辑控件类型
  maxLength: L;             // 最大字符数
  /** 占位变量（可选），渲染时自动替换，如 "{province}" → "四川省" */
  placeholders?: string[];
}

/** 可编辑选择字段 */
interface EditableSelect<O extends string[]> {
  default: O[number];       // 默认选项
  type: "select";
  options: O;               // 可选值列表
}
```

---

## 3. 完整示例：汉源花椒

```jsonc
{
  // ═══ §1 通用标识（不可变） ═══
  "id": "hanyuan-pepper",
  "name": "漢源花椒",
  "nameEn": "Hanyuan Pepper",
  "category": "调味品",
  "province": "四川省",
  "heroImage": "/ingredients/pepper-realistic.png",
  "species": "花椒 Zanthoxylum bungeanum",
  "origin": "四川汉源 · 干热河谷",
  "originCoord": [102.6506, 29.3443],

  // ═══ §2 品牌色彩 ═══
  "colors": {
    "primary": "#9C3131",
    "accent": "#516E58"
  },

  // ═══ §3 营销海报 ═══
  "marketing": {

    // ── 空间底板（不可变）─
    "spatial": {
      "nodes": [
        { "short": "汉源", "coord": [102.6342, 29.5621], "desc": "海拔1600m批次抽样" },
        { "short": "成都", "coord": [104.1623, 30.8241], "desc": "入库理化复检" },
        { "short": "上海", "coord": [121.3821, 31.1123], "desc": "冷链全损耗监控" }
      ],
      "evidence": [
        { "label": "芳香挥发油", "value": "≥ 5.5%" },
        { "label": "羟基山椒素", "value": "≥ 35mg/g" },
        { "label": "农残检测",   "value": "零检出" }
      ]
    },

    // ── 创作默认值（用户可覆盖）─
    "creative": {
      "desc": {
        "default": "大渡河干热河谷微气候 · 海拔1600米正路贡椒",
        "type": "text",
        "maxLength": 60
      },
      "poeticLine": {
        "default": "健康且好吃的食物，有趣且爱吃的朋友。",
        "type": "text",
        "maxLength": 40
      },
      "narrative": {
        "default": "溯源于<span class='hl'>{province}</span>，经<span class='hl'>{nodePath}</span>全链路冷链直达。",
        "type": "rich-text",
        "maxLength": 300,
        "placeholders": ["{province}", "{nodePath}"]
      },
      "theme": {
        "default": "nature",
        "type": "select",
        "options": ["nature", "heritage", "indigo"]
      },
      "copy": {
        "xiaohongshu": {
          "default": "这颗花椒来自四川汉源大渡河干热河谷，海拔1600米的正路贡椒，挥发油超5.5%，麻味层次感无敌。",
          "type": "text",
          "maxLength": 200
        },
        "ecommerce": {
          "default": "【产地直供】汉源贡椒·国家地理标志保护产品。大渡河谷微气候孕育，挥发油≥5.5%，粒粒饱满麻香醇厚。",
          "type": "text",
          "maxLength": 200
        }
      }
    }
  },

  // ═══ §4 实证白皮书 ═══
  "archive": {

    "spatial": {
      "originPoint": {
        "name": "四川省·雅安市汉源县",
        "coord": [102.6506, 29.3443],
        "precision": "核心原产地基准坐标"
      },
      "metrics": [
        { "label": "挥发油总量",   "value": "5.8%",     "note": "远超行标验收线" },
        { "label": "羟基山椒素",   "value": "38 mg/g",  "note": "决定级麻感指标" },
        { "label": "SGS 安全筛查", "value": "0 检出",   "note": "219项农残未检出" },
        { "label": "溯源采样点",   "value": "18 处",     "note": "产地/中转/前置仓" }
      ],
      "climate": {
        "rain": [7, 12, 24, 55, 82, 118, 176, 143, 96, 46, 18, 8],
        "temp": [6.2, 8.8, 13.1, 17.4, 20.6, 23.2, 24.8, 24.1, 20.5, 16.4, 11.1, 7.2]
      },
      "heat": [
        { "stage": "萌芽", "value": 240 },
        { "stage": "展叶", "value": 510 },
        { "stage": "开花", "value": 760 },
        { "stage": "坐果", "value": 1030 },
        { "stage": "成熟", "value": 1290 }
      ],
      "qualityBenchmark": {
        "labels": ["挥发油", "麻味物质", "净含水率", "果皮洁净度", "香气留存"],
        "values": [132, 128, 116, 141, 125]
      },
      "flavor": {
        "scores": [0.92, 0.58, 0.18, 0.12, 0.06, 0.36]
      },
      "reports": [
        { "org": "SGS 通标标准技术", "result": "219项农残：未检出",     "code": "SGS-HY-2605-018" },
        { "org": "谱尼测试 PONY",    "result": "重金属元素：符合国标", "code": "PONY-HY-2605-022" }
      ],
      "stationCode": "HY-MET-2605"
    },

    "creative": {
      "flavorSummary": {
        "default": "极为霸道的醇麻感与清晰的柑橘类辛香，是鉴别正路贡椒的决定性风味指纹。",
        "type": "text",
        "maxLength": 150
      },
      "originDesc": {
        "default": "四川汉源 · 干热河谷",
        "type": "text",
        "maxLength": 80
      }
    }
  },

  // ═══ §5 智慧大屏 ═══
  "display": {

    "spatial": {
      "identity": [
        { "label": "核心产区", "value": "四川雅安汉源 · 大渡河干热河谷" },
        { "label": "气候微相", "value": "海拔1600m，极端昼夜温差促油胞浓缩" },
        { "label": "空间凭证", "value": "国家地理标志保护产品" }
      ],
      "stages": [
        {
          "id": "origin",  "coord": [102.6342, 29.5621],
          "short": "源起产地", "type": "核心产区", "name": "大渡河干热河谷贡椒区",
          "color": "#8b9a76", "evidence": "国家地理标志保护产品"
        },
        {
          "id": "process", "coord": [102.6511, 29.3512],
          "short": "精炼加工", "type": "加工节点", "name": "智能化分级初加工中心",
          "color": "#c7925e", "evidence": "非遗工艺 · 低温曝晒"
        },
        {
          "id": "storage", "coord": [104.1623, 30.8241],
          "short": "气调仓储", "type": "冷链仓储", "name": "西南冷链气调仓储枢纽",
          "color": "#6896aa", "evidence": "0-4℃恒温 · 充氮真空"
        },
        {
          "id": "market",  "coord": [121.3821, 31.1123],
          "short": "终端直达", "type": "主销市场", "name": "长三角精品调味品渠道枢纽",
          "color": "#9782bb", "evidence": "一物一码 · 批次可溯"
        },
        {
          "id": "dining",  "coord": [106.5512, 29.5631],
          "short": "美学餐桌", "type": "餐饮应用", "name": "经典川味与重度麻辣体验空间",
          "color": "#bc5b5a", "evidence": "川菜24味型麻味基底"
        }
      ]
    },

    "creative": {
      "visibleNodeIds": {
        "default": ["origin", "process", "storage", "market", "dining"],
        "type": "select",
        "options": ["origin", "process", "storage", "market", "dining"]
      },
      "cameraMode": {
        "default": "tour",
        "type": "select",
        "options": ["tour", "origin", "market", "dining"]
      },
      "stageStories": {
        "origin": {
          "default": "独享大渡河干热河谷微气候，海拔1600米坡地。极端昼夜温差促使植物油胞浓缩，红油饱满，是流传千年的正路贡椒原产地。",
          "type": "text",
          "maxLength": 200
        },
        "process": {
          "default": "伏天清晨手工采摘以保护果皮油包，经过智能化筛分与低温太阳能模拟曝晒，自然开裂脱籽，锁住山地麻香。",
          "type": "text",
          "maxLength": 200
        },
        "storage": {
          "default": "采用高阻隔充氮真空包装，全程0-4℃恒温冷链锁鲜，隔绝光照与氧气，减少挥发油流失。",
          "type": "text",
          "maxLength": 200
        },
        "market": {
          "default": "辐射华东的主销区枢纽。每一批次绑定数字化追溯二维码，进入精品零售及有机商超。",
          "type": "text",
          "maxLength": 200
        },
        "dining": {
          "default": "在沸腾的牛油火锅中，高纯度羟基山椒素瞬间爆发，完成从高山河谷到城市餐桌的空间证据闭环。",
          "type": "text",
          "maxLength": 200
        }
      }
    }
  },

  // ═══ §6 传播图谱 ═══
  "spread": {

    "spatial": {
      "ingredientId": "pepper"
    },

    "creative": {
      "storySummary": {
        "default": "辣椒原产中美洲，15世纪末由哥伦布带回欧洲，明代后期经海路传入中国，三百余年间从观赏植物演变为改变中国饮食格局的核心调味料。",
        "type": "text",
        "maxLength": 100
      },
      "brandStory": {
        "default": "汉源花椒的故事始于大渡河干热河谷。在这片海拔1600米的坡地上，极端昼夜温差促使花椒油胞浓缩，成就了\"正路贡椒\"千年不衰的醇麻风味。从唐代贡品到川菜灵魂，每一粒花椒承载着高山河谷的空间印记。",
        "type": "text",
        "maxLength": 300
      },
      "exhibitionScript": {
        "default": "各位观众，您现在看到的是产自四川汉源的正路贡椒。汉源地处大渡河干热河谷，独特的地理气候条件造就了花椒粒大饱满、油胞丰富、麻味醇厚的品质特征。该产品已获得国家地理标志保护，并通过SGS 219项农残检测。",
        "type": "text",
        "maxLength": 500
      }
    }
  },

  // ═══ §7 Studio 元数据 ═══
  "studio": {
    "brandScenario": "地方农产品品牌化 / 餐饮供应链 / 非遗食材",
    "recommendedOutputs": ["poster", "archive", "display", "spread"],
    "brandName": "汉源贡椒"
  }
}
```

---

## 4. 字段层级速查

```
product_cases/{id}.json
├── id, name, nameEn        ← 不可变
├── category                ← 不可变
├── province                ← 不可变（GIS 事实）
├── heroImage               ← 不可变（用户可在 Studio 上传自定义图片覆盖）
├── species                 ← 不可变
├── origin, originCoord     ← 不可变
├── colors                  ← 不可变
│
├── marketing/
│   ├── spatial/            ← 不可变：nodes[], evidence[]
│   └── creative/           ← 可编辑：desc, poeticLine, narrative, theme, copy
│
├── archive/
│   ├── spatial/            ← 不可变：originPoint, metrics, climate, heat, benchmark, flavor.scores, reports
│   └── creative/           ← 可编辑：flavorSummary, originDesc
│
├── display/
│   ├── spatial/            ← 不可变：stages[], identity[]
│   └── creative/           ← 可编辑：visibleNodeIds, cameraMode, stageStories
│
├── spread/
│   ├── spatial/            ← 不可变：ingredientId（引用）
│   └── creative/           ← 可编辑：storySummary, brandStory, exhibitionScript
│
└── studio/                 ← 元数据（推荐产出物、适用场景等）
```

---

## 5. 迁移对照表

### MarketingView `products[]` → 新 schema

| 旧字段 | 新位置 | 层级 |
|---|---|---|
| `id` | `id` | 通用（不变） |
| `name` | `name` | 通用（不变） |
| `province` | `province` | 通用（不变） |
| `image` | `heroImage` | 通用（不变） |
| `desc` | `marketing.creative.desc.default` | 创作默认值 |
| `poeticLine` | `marketing.creative.poeticLine.default` | 创作默认值 |
| `narrative` | `marketing.creative.narrative.default` | 创作默认值 |
| `nodes[].short` | `marketing.spatial.nodes[].short` | 空间底板 |
| `nodes[].coord` | `marketing.spatial.nodes[].coord` | 空间底板 |
| `evidence` | `marketing.spatial.evidence` | 空间底板 |

### ArchiveView `dossiers[]` → 新 schema

| 旧字段 | 新位置 | 层级 |
|---|---|---|
| `flavorSummary` | `archive.creative.flavorSummary.default` | 创作默认值 |
| `color` | `colors.primary` | 通用（不变） |
| 其余所有 | `archive.spatial.*` | 空间底板 |

### GeoAtlasView → 新 schema

| 旧字段 | 新位置 | 层级 |
|---|---|---|
| `stages[].story` | `display.creative.stageStories[id].default` | 创作默认值 |
| `identity` | `display.spatial.identity` | 空间底板 |
| `stages`（除 story） | `display.spatial.stages` | 空间底板 |

---

## 6. MVP 最小填充

如果没有时间填满所有字段，只需以下内容即可让 Studio 跑起来：

```jsonc
{
  "id": "...",
  "name": "...",
  "province": "...",
  "heroImage": "...",
  "colors": { "primary": "#...", "accent": "#..." },

  "marketing": {
    "spatial": {
      "nodes": [{ "short": "...", "coord": [lng, lat] }],
      "evidence": []
    },
    "creative": {
      "desc":       { "default": "...", "type": "text", "maxLength": 60 },
      "poeticLine": { "default": "...", "type": "text", "maxLength": 40 },
      "narrative":  { "default": "...", "type": "rich-text", "maxLength": 300 },
      "theme":      { "default": "nature", "type": "select", "options": ["nature", "heritage", "indigo"] },
      "copy": { "xiaohongshu": { "default": "...", "type": "text", "maxLength": 200 }, "ecommerce": { "default": "...", "type": "text", "maxLength": 200 } }
    }
  },

  "studio": {
    "brandScenario": "...",
    "recommendedOutputs": ["poster"],
    "brandName": "..."
  }
}
```

---

## 7. 与现有数据源的协同

| 数据源 | 关系 | 处理方式 |
|---|---|---|
| `data/ingredient/*.json` | 通过 `spread.spatial.ingredientId` 引用 | 不合并，独立维护 |
| `src/assets/china.json` | 省份边界底图 | 不合并，地图图层数据 |
| `backend/data/app_data.py` | 后端 display metadata | 未来可同步读取 |
| 用户上传图片 | Studio 项目状态 | 存在 Pinia store，不写入 JSON |
