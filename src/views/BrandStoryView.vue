<template>
  <main class="product-page" :class="`view-${currentView}`">
    <section class="studio-toolbar">
      <div class="toolbar-copy">
        <span>FlavorScape Product Studio</span>
        <strong>{{ activeView.name }}</strong>
        <p>{{ activeView.description }}</p>
      </div>

      <div class="product-switcher" aria-label="示例产品切换">
        <button
          v-for="item in products"
          :key="item.id"
          type="button"
          :class="{ active: activeProductId === item.id }"
          @click="activeProductId = item.id"
        >
          <img :src="item.image" :alt="item.name" />
          <span>{{ item.name }}</span>
        </button>
      </div>

      <div class="toolbar-actions" aria-label="产品形态切换">
        <button
          v-for="view in views"
          :key="view.id"
          type="button"
          :class="{ active: currentView === view.id }"
          @click="currentView = view.id"
        >
          {{ view.name }}
        </button>
        <button
          type="button"
          class="download-btn"
          :disabled="isExporting"
          @click="downloadCapture('png')"
        >
          {{ isExporting ? '正在生成...' : 'PNG' }}
        </button>
        <button
          type="button"
          class="download-btn secondary"
          :disabled="isExporting"
          @click="downloadCapture('jpeg')"
        >
          JPG
        </button>
        <button type="button" class="download-btn secondary" @click="printCapture">
          PDF
        </button>
      </div>
    </section>

    <section v-if="currentView === 'brand'" class="poster-stage">
      <article id="capture-zone" class="poster-card" aria-label="品牌公示海报画布">
        <div class="poster-fieldmark" aria-hidden="true">
          <span>FLAVORSCAPE</span>
          <i v-for="n in 18" :key="n" />
        </div>
        <header class="poster-masthead">
          <div>
            <span class="eyebrow">Origin Public Board</span>
            <h1>{{ product.name }}<br />产地公示</h1>
            <p class="poster-subline">{{ product.category }} · {{ product.species }}</p>
          </div>
          <div class="poster-product-seal">
            <img :src="product.image" :alt="product.name" />
            <strong>{{ product.name }}</strong>
            <span>国家地理标志保护产品</span>
          </div>
        </header>

        <section class="poster-map-anchor">
          <div class="poster-map-ring" aria-hidden="true" />
          <div ref="posterMapContainer" class="poster-real-map" aria-label="溯源路线真实地图" />
          <div v-if="!posterMapReady" class="poster-map-loading">底图加载中...</div>
          <div class="poster-map-glass">
            <span>Traceability Route</span>
            <strong>{{ traceRouteLabel }}</strong>
            <p>{{ routePairs.length }} 条路径 · {{ coverageRegions }} 供应半径</p>
          </div>
          <div class="poster-route-tags" aria-label="溯源节点">
            <span v-for="node in nodes" :key="node.id" :style="{ '--node-color': node.color }">
              {{ node.short }}
            </span>
          </div>
        </section>

        <div class="poster-axis" aria-label="溯源节点轴线">
          <span v-for="node in nodes" :key="`axis-${node.id}`" :style="{ '--node-color': node.color }">
            <i />
            {{ node.short }}
          </span>
        </div>

        <section class="poster-proof-grid">
          <article v-for="item in posterProofs" :key="item.label">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </article>
        </section>

        <footer class="poster-footer">
          <div class="qr-code" aria-label="二维码占位">
            <i v-for="n in 25" :key="n" />
          </div>
          <div>
            <span>Scan For Full Report</span>
            <strong>完整地理志 / 产区影像 / 检测报告</strong>
            <p>{{ activeProductId === 'rice' ? '寒地黑土产区样例' : '大渡河河谷产区样例' }} · Exportable PNG/JPG</p>
          </div>
        </footer>
      </article>
    </section>

    <section v-else-if="currentView === 'chain'" class="chain-stage">
      <article id="capture-zone" class="chain-canvas" aria-label="产业链流程画布">
        <div class="chain-ruler" aria-hidden="true">
          <span v-for="n in 28" :key="n" />
        </div>
        <header class="chain-header">
          <span class="eyebrow">Industry Chain Map</span>
          <h1>{{ product.name }} 全链路地理溯源</h1>
          <p>{{ traceRouteLabel }} · 工艺参数蓝图</p>
          <div class="chain-meta-row">
            <b>{{ product.category }}</b>
            <b>{{ routePairs.length }} relations</b>
            <b>{{ coverageRegions }}</b>
          </div>
        </header>

        <div class="chain-flow">
          <div v-for="(node, i) in nodes" :key="node.id" class="chain-step">
            <div class="chain-step-num" :style="{ '--num-color': node.color }">{{ i + 1 }}</div>
            <div class="chain-step-card">
              <div class="chain-step-icon" :style="{ '--node-color': node.color }">
                <img :src="product.image" :alt="node.short" />
              </div>
              <div class="chain-step-body">
                <span class="chain-step-type">{{ node.type }}</span>
                <strong>{{ node.name }}</strong>
                <div class="chain-step-tags">
                  <b v-for="tag in node.evidence.split(' · ')" :key="tag">{{ tag }}</b>
                </div>
                <p>{{ node.story }}</p>
              </div>
            </div>
            <div v-if="i < nodes.length - 1" class="chain-arrow" aria-hidden="true">
              <svg width="28" height="48" viewBox="0 0 28 48">
                <line x1="14" y1="0" x2="14" y2="38" stroke-width="2" stroke-dasharray="4 4" />
                <polygon points="4,38 14,48 24,38" />
              </svg>
            </div>
          </div>
        </div>

        <footer class="chain-footer">
          <div class="chain-signal-bar" aria-hidden="true">
            <i v-for="node in nodes" :key="`signal-${node.id}`" :style="{ '--node-color': node.color }" />
          </div>
          <span>Source-to-Table Process Standard</span>
          <strong>{{ nodes.length }} 节点 · {{ routePairs.length }} 道工艺关系 · {{ coverageRegions }} 供应半径</strong>
          <p>蓝图模式隐藏地图窗口，把视觉重心交给工艺顺序、参数标签与标准化流程。</p>
        </footer>
      </article>
    </section>

    <section v-else-if="currentView === 'archive'" class="archive-stage">
      <article id="capture-zone" class="archive-canvas" aria-label="风物档案画布">
        <header class="archive-hero">
          <div class="archive-hero-img">
            <img :src="product.image" :alt="product.name" />
          </div>
          <div class="archive-hero-text">
            <span class="eyebrow">Ingredient Culture Archive</span>
            <h1>{{ product.name }}</h1>
            <p class="archive-species">{{ product.species }}</p>
            <p>{{ product.summary }}</p>
          </div>
        </header>

        <div class="archive-grid">
          <section class="archive-panel archive-abstract">
            <span class="archive-panel-kicker">Field Notes</span>
            <h3>{{ traceRouteLabel }}</h3>
            <p>{{ product.summary }}</p>
          </section>

          <section class="archive-panel archive-identity">
            <span class="archive-panel-kicker">Origin Identity</span>
            <h3>产地身份与证据标签</h3>
            <div class="archive-capsule-cloud">
              <span v-for="item in archiveCapsules" :key="`${item.label}-${item.value}`">
                <b>{{ item.label }}</b>{{ item.value }}
              </span>
            </div>
          </section>

          <section class="archive-panel archive-map">
            <span class="archive-panel-kicker">Geographic Evidence</span>
            <h3>空间证据</h3>
            <div ref="archiveMapContainer" class="archive-real-map" aria-label="档案地图" />
            <div v-if="!archiveMapReady" class="archive-map-loading">底图加载中...</div>
            <div class="archive-map-caption">
              <span>Evidence Radius</span>
              <strong>{{ coverageRegions }}</strong>
              <p>{{ traceRouteLabel }}</p>
            </div>
          </section>

          <section class="archive-panel archive-cert">
            <span class="archive-panel-kicker">Certification & Quality</span>
            <h3>认证与品质</h3>
            <div class="archive-cert-grid">
              <article v-for="item in certificationCards" :key="item.label">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
                <p>{{ item.note }}</p>
              </article>
            </div>
          </section>

          <section class="archive-panel archive-nodes">
            <span class="archive-panel-kicker">Traceability Nodes</span>
            <h3>溯源节点</h3>
            <div class="archive-node-list">
              <article v-for="node in nodes" :key="node.id">
                <svg width="32" height="12" viewBox="0 0 32 12">
                  <circle cx="6" cy="6" r="5" :fill="node.color" opacity="0.82" />
                  <line x1="12" y1="6" x2="28" y2="6" stroke="rgba(107,84,55,0.3)" stroke-dasharray="3 3" />
                </svg>
                <div>
                  <span>{{ node.type }}</span>
                  <strong>{{ node.name }}</strong>
                  <p>{{ node.meta }}</p>
                </div>
              </article>
            </div>
          </section>
        </div>

        <footer class="archive-footer">
          <div class="qr-code" aria-label="二维码占位">
            <i v-for="n in 25" :key="n" />
          </div>
          <div>
            <span>Scan for Interactive StoryMap</span>
            <strong>完整风物档案 · 交互地理志</strong>
            <p>数据来源：国家地理标志公告 · WWF TEOW · SGS检测报告</p>
          </div>
        </footer>
      </article>
    </section>

    <section v-else class="story-stage">
      <article id="capture-zone" class="storymap-canvas" aria-label="地理志联动布局画布">
        <aside class="atlas-panel atlas-left">
          <span class="eyebrow">Product Identity</span>
          <h2>{{ product.name }}</h2>
          <p>{{ product.species }}</p>
          <div class="product-photo">
            <img :src="product.image" :alt="product.name" />
          </div>
          <dl>
            <div v-for="item in identityItems" :key="item.label">
              <dt>{{ item.label }}</dt>
              <dd>{{ item.value }}</dd>
            </div>
          </dl>
        </aside>

        <section class="atlas-map-card">
          <div class="map-heading">
            <div>
              <span class="eyebrow">StoryMap Evidence Layer</span>
              <h1>从产地到餐桌的空间叙事</h1>
            </div>
            <div class="atlas-index-stamp" aria-hidden="true">
              <span>{{ nodes.length }}</span>
              <small>Nodes</small>
            </div>
            <button type="button" @click="selectedNodeId = nextNodeId">下一节点</button>
          </div>
          <div class="map-metric-strip" aria-label="地图摘要指标">
            <article v-for="metric in mapMetrics" :key="metric.label">
              <span>{{ metric.label }}</span>
              <strong>{{ metric.value }}</strong>
            </article>
          </div>

          <div class="large-map-wrap">
            <div ref="atlasMapContainer" class="atlas-real-map" aria-label="真实地理底图">
              <div v-if="!mapReady" class="map-loading">正在加载地理底图...</div>
            </div>

            <div class="atlas-map-overlay" aria-label="溯源节点覆盖层">
              <svg class="projected-route-svg" aria-hidden="true">
                <defs>
                  <linearGradient id="projectedRouteGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#6f8b63" />
                    <stop offset="52%" stop-color="#c39b44" />
                    <stop offset="100%" stop-color="#c4503d" />
                  </linearGradient>
                </defs>
                <path
                  v-for="route in projectedRoutePaths"
                  :key="`${route.id}-halo`"
                  :d="route.d"
                  class="projected-route-halo"
                />
                <path
                  v-for="route in projectedRoutePaths"
                  :key="route.id"
                  :d="route.d"
                  class="projected-route-line"
                />
                <polyline
                  v-for="node in projectedNodes"
                  :key="`${node.id}-leader`"
                  :points="node.leader"
                  class="leader-line"
                />
              </svg>

              <button
                v-for="node in projectedNodes"
                :key="`${node.id}-dot`"
                type="button"
                class="real-map-dot"
                :class="{ selected: selectedNode.id === node.id }"
                :style="{
                  left: `${node.x}px`,
                  top: `${node.y}px`,
                  '--node-color': node.color,
                }"
                @mouseenter="selectedNodeId = node.id"
                @click="selectMapNode(node.id)"
              >
                <span class="sr-only">{{ node.short }}</span>
              </button>

              <button
                v-for="node in projectedNodes"
                :key="`${node.id}-label`"
                type="button"
                class="real-map-label"
                :class="{ selected: selectedNode.id === node.id }"
                :style="{
                  left: `${node.labelX}px`,
                  top: `${node.labelY}px`,
                  '--node-color': node.color,
                }"
                @mouseenter="selectedNodeId = node.id"
                @click="selectMapNode(node.id)"
              >
                <span>{{ node.type }}</span>
                <strong>{{ node.short }}</strong>
                <em>{{ node.meta }}</em>
              </button>
            </div>

            <svg class="large-map legacy-map" viewBox="0 0 920 620" role="img" aria-label="食材品牌地理志路线图">
              <defs>
                <linearGradient id="atlasLand" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#f1e7d2" />
                  <stop offset="56%" stop-color="#dde9d5" />
                  <stop offset="100%" stop-color="#d7e8e9" />
                </linearGradient>
                <linearGradient id="atlasRoute" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#6f8b63" />
                  <stop offset="48%" stop-color="#c39b44" />
                  <stop offset="100%" stop-color="#c4503d" />
                </linearGradient>
                <filter id="atlasRouteGlow" x="-30%" y="-30%" width="160%" height="160%">
                  <feGaussianBlur stdDeviation="8" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                <marker id="routeArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#9a6535" />
                </marker>
              </defs>

              <rect class="map-water" x="0" y="0" width="920" height="620" rx="30" />
              <path class="atlas-land" d="M82 345 C125 213 233 143 356 155 C422 69 565 88 641 170 C761 181 849 253 864 363 C813 477 693 526 558 492 C477 558 337 543 270 459 C178 465 108 423 82 345 Z" />
              <path class="atlas-terrain" d="M132 382 C166 292 233 249 315 263 C361 287 362 358 312 411 C241 468 169 440 132 382 Z" />
              <path class="atlas-river" d="M162 447 C256 374 341 368 422 404 C516 447 632 425 775 343" />
              <path class="atlas-river atlas-river-thin" d="M231 236 C318 259 399 239 492 205 C575 174 665 191 777 255" />

              <g class="route-layer">
                <path v-for="route in routes" :key="`${route.id}-glow`" :d="route.path" class="route-glow" />
                <path v-for="route in routes" :key="route.id" :d="route.path" class="atlas-route" marker-end="url(#routeArrow)" />
              </g>

              <g class="route-particles">
                <circle v-for="particle in particles" :key="particle.id" r="5" :class="particle.className" />
              </g>

              <g class="node-layer">
                <g
                  v-for="node in nodes"
                  :key="node.id"
                  class="atlas-node"
                  :class="{ selected: selectedNode.id === node.id }"
                  :transform="`translate(${node.x} ${node.y})`"
                  @click="selectedNodeId = node.id"
                >
                  <circle r="28" class="node-halo" />
                  <circle r="18" class="node-disc" />
                  <image :href="product.image" x="-13" y="-13" width="26" height="26" preserveAspectRatio="xMidYMid meet" />
                  <text y="48" text-anchor="middle">{{ node.short }}</text>
                </g>
              </g>
            </svg>

            <article class="selected-card">
              <span :style="{ color: selectedNode.color }">{{ selectedNode.type }}</span>
              <strong>{{ selectedNode.name }}</strong>
              <p>{{ selectedNode.story }}</p>
              <em>{{ selectedNode.evidence }}</em>
            </article>
          </div>
        </section>

        <aside class="atlas-panel atlas-right">
          <span class="eyebrow">Narrative Timeline</span>
          <h2>溯源叙事线</h2>
          <p class="atlas-panel-lede">右侧只保留解释空间关系所需的节点故事，主视觉交给地图承担。</p>
          <div class="story-timeline">
            <article
              v-for="node in nodes"
              :key="node.id"
              :class="{ active: selectedNode.id === node.id }"
              @mouseenter="selectedNodeId = node.id"
              @click="selectedNodeId = node.id"
            >
              <i :style="{ '--node-color': node.color }" />
              <span>{{ node.type }}</span>
              <strong>{{ node.name }}</strong>
              <p>{{ node.story }}</p>
            </article>
          </div>
        </aside>
      </article>
    </section>
  </main>
</template>

<script setup>
import html2canvas from 'html2canvas'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const initialView = new URLSearchParams(window.location.search).get('view')
const validInitialViews = new Set(['atlas', 'brand', 'chain', 'archive'])
const currentView = ref(validInitialViews.has(initialView) ? initialView : 'atlas')
const selectedNodeId = ref('origin')
const isExporting = ref(false)
const atlasMapContainer = ref(null)
const posterMapContainer = ref(null)
const chainMapContainer = ref(null)
const archiveMapContainer = ref(null)
const mapReady = ref(false)
const posterMapReady = ref(false)
const archiveMapReady = ref(false)
const projectedNodes = ref([])
const projectedRoutePaths = ref([])

const MAP_STYLE = {
  version: 8,
  sources: {
    'hyp-tiles': {
      type: 'raster',
      tiles: ['/tiles/raster/{z}/{x}/{y}.png'],
      tileSize: 256,
      minzoom: 0,
      maxzoom: 8,
      attribution: 'Natural Earth',
    },
  },
  layers: [
    { id: 'trace-bg', type: 'background', paint: { 'background-color': '#dce8e4' } },
    {
      id: 'hyp',
      type: 'raster',
      source: 'hyp-tiles',
      paint: {
        'raster-saturation': -0.28,
        'raster-contrast': 0.06,
        'raster-brightness-min': 0.08,
        'raster-opacity': 0.92,
      },
    },
  ],
}

let atlasMap = null
let posterMap = null
let archiveMap = null
let chainMap = null

const views = [
  {
    id: 'atlas',
    name: '地理志',
    description: '全屏 StoryMap 联动布局，用地图、节点卡片和叙事时间线呈现完整产品故事。',
  },
  {
    id: 'brand',
    name: '品牌公示',
    description: '3:4 纵向海报卡片，融合真实地图与溯源证据，用于门店公示、电商详情图和展会展示。',
  },
  {
    id: 'chain',
    name: '产业链',
    description: '纵向流程图，按产地→加工→仓储→市场→餐桌顺序展开全链路地理溯源。',
  },
  {
    id: 'archive',
    name: '风物档案',
    description: '食材文化知识图谱：产地环境、历史传播、加工技艺、认证检测、代表菜品综合档案。',
  },
]

const activeProductId = ref('pepper')
const products = [
  {
    id: 'pepper',
    name: '汉源花椒',
    image: '/ingredients/pepper-realistic.png',
    species: '花椒 Zanthoxylum bungeanum',
    category: '香辛料',
    summary: '贡椒千年传承，独享大渡河干热河谷微气候。从海拔1600米坡地到城市餐桌，每一粒汉源花椒都是高山河谷的空间证据。',
  },
  {
    id: 'rice',
    name: '五常大米',
    image: '/ingredients/rice-realistic.png',
    species: '稻米 Oryza sativa',
    category: '谷物主食',
    summary: '寒地黑土、河湖灌溉与长周期成熟共同塑造稻米香气。该样例用于展示生成器可从香辛料扩展到主粮类地理品牌。',
  },
]
const product = computed(() => products.find(item => item.id === activeProductId.value) || products[0])

const pepperIdentity = [
  { label: '核心产区', value: '四川雅安汉源 · 大渡河干热河谷' },
  { label: '海拔与气候', value: '海拔1600m，极端昼夜温差促油胞浓缩' },
  { label: '地理标志', value: '中华人民共和国地理标志保护产品' },
  { label: '输出场景', value: '品牌官网 · 展厅 · 包装内页 · 电商详情页' },
]

const riceIdentity = [
  { label: '核心产区', value: '黑龙江哈尔滨五常 · 拉林河流域' },
  { label: '土壤与气候', value: '寒地黑土，昼夜温差大，生长期长' },
  { label: '地理标志', value: '五常大米地理标志保护产品' },
  { label: '输出场景', value: '产地公示 · 礼盒内页 · 电商详情页 · 展销会' },
]

const identityItems = computed(() => activeProductId.value === 'rice' ? riceIdentity : pepperIdentity)

const certificationCards = computed(() => activeProductId.value === 'rice'
  ? [
      { label: '地理标志', value: '五常大米 — 国家地理标志保护产品', note: '寒地黑土核心产区 · 区域公用品牌保护' },
      { label: '品质特征', value: '米粒饱满 · 蒸煮香气突出', note: '以长粒香、稻花香等品类为代表，适合礼盒与家庭主食场景' },
      { label: '加工工艺', value: '低温烘干 · 精准碾磨 · 分级仓储', note: '控制水分与碎米率，保留稻米香气和口感稳定性' },
      { label: '代表场景', value: '东北米饭 · 寿司饭 · 家庭主食 · 团餐供应', note: '主粮消费高频，适合做产地信任和供应半径表达' },
    ]
  : [
      { label: '地理标志', value: '汉源花椒 — 国家地理标志保护产品', note: '国家农产品地理标志登记产品 · 汉源贡椒证明商标' },
      { label: '核心成分检测', value: '挥发油 ≥ 5.5% · 羟基山椒素 ≥ 35 mg/g', note: 'SGS / 谱尼测试官方抽检 · 农残0检出合格证' },
      { label: '加工工艺', value: '伏天手工采摘 · 智能筛分(>4.5mm) · 低温太阳能曝晒', note: '非遗初加工技艺 · 充氮真空包装 · 0-4℃恒温冷链锁鲜' },
      { label: '代表菜品', value: '牛油火锅 · 麻婆豆腐 · 水煮系列 · 椒麻鸡', note: '川菜24味型之麻味基底 · 重庆火锅灵魂香料' },
    ])

const pepperStages = [
  {
    id: 'origin',
    x: 204,
    y: 384,
    coord: [102.6342, 29.5621],
    short: '产地',
    type: '核心产区',
    name: '大渡河干热河谷贡椒核心产区（清溪镇）',
    color: '#6f8b63',
    story: '独享大渡河干热河谷微气候，海拔1600米坡地。极端昼夜温差促使植物油胞疯狂浓缩，红油饱满，是流传千年的"正路贡椒"原产地。',
    evidence: '国家地理标志保护产品 · 汉源花椒',
    meta: '海拔1600m · 大渡河干热河谷微气候',
  },
  {
    id: 'process',
    x: 296,
    y: 326,
    coord: [102.6511, 29.3512],
    short: '加工',
    type: '加工节点',
    name: '贡椒非遗初加工与智能化分级中心',
    color: '#b8793d',
    story: '坚持伏天清晨手工采摘以保护果皮油包。历经现代智能化筛分（直径>4.5mm）与低温太阳能模拟曝晒，自然开裂脱籽，锁住纯正山地麻香。',
    evidence: '非遗工艺 · 智能分级 · 低温太阳能曝晒',
    meta: '手工采摘 · 筛分>4.5mm · 自然脱籽',
  },
  {
    id: 'storage',
    x: 426,
    y: 296,
    coord: [104.1623, 30.8241],
    short: '仓储',
    type: '冷链仓储',
    name: '西南冷链气调仓储中心（成都基地）',
    color: '#3e7891',
    story: '采用高阻隔充氮真空包装，全程0-4℃恒温冷链锁鲜。彻底隔绝光照与氧气，防止花椒挥发油与芳香烃成分流失，实现跨季节风味零损耗。',
    evidence: '充氮真空 · 0-4℃恒温 · 气调锁鲜',
    meta: '成都新都 · 西南冷链枢纽',
  },
  {
    id: 'market',
    x: 776,
    y: 282,
    coord: [121.3821, 31.1123],
    short: '市场',
    type: '外部市场',
    name: '长三角精品调味品与高阶食材供应链枢纽',
    color: '#8a6fb3',
    story: '辐射华东的主销区枢纽。每一批次均绑定数字化追溯二维码，直供一线城市的精品高端零售、有机商超及地理标志风物展销渠道。',
    evidence: '数字化追溯二维码 · 精品零售 · 有机商超',
    meta: '上海闵行 · 长三角供应链枢纽',
  },
  {
    id: 'dining',
    x: 558,
    y: 402,
    coord: [106.5512, 29.5631],
    short: '餐桌',
    type: '餐饮应用',
    name: '经典川味与重度麻辣美学体验空间（火锅/川菜）',
    color: '#c64240',
    story: '汉源花椒的终极归宿。在沸腾的牛油火锅与非遗麻婆豆腐中，高纯度羟基山椒素瞬间爆发，完成从高山河谷到城市餐桌的空间证据链闭环。',
    evidence: '牛油火锅 · 麻婆豆腐 · 川菜24味型麻味基底',
    meta: '重庆渝中 · 川菜麻辣美学圣地',
  },
]

const riceStages = [
  {
    id: 'origin',
    x: 204,
    y: 384,
    coord: [127.1676, 44.9192],
    short: '产地',
    type: '产地',
    name: '牤牛河与拉林河流域核心稻作区',
    color: '#5e7b50',
    story: '依托长白山余脉的洁净水源与上万年沉积形成的寒地黑土。极端昼夜温差促使稻米中干物质与游离双糖持续积累，形成清晰的稻花香风味。',
    evidence: '土壤：寒地黑土 · 积温：2700℃ · 140天超长生长期',
    meta: '寒地黑土 · 河流灌溉 · 超长成熟期',
  },
  {
    id: 'process',
    x: 296,
    y: 326,
    coord: [127.0679, 44.9322],
    short: '加工',
    type: '加工',
    name: '非遗质检与智能化精密碾磨中心',
    color: '#8f7b48',
    story: '伏天开镰后进行低温烘干与光学粒选，控制水分、碎米率与抛光度。轻度碾磨保留米粒天然芳香成分，锁住新米的原始米香。',
    evidence: '水分控制：≤14.5% · 碎米率：<5% · 轻度留胚',
    meta: '低温烘干 · 光学粒选 · 精密碾磨',
  },
  {
    id: 'storage',
    x: 426,
    y: 296,
    coord: [126.6331, 45.7422],
    short: '仓储',
    type: '仓储',
    name: '低温绿色充氮稻谷气调保鲜库',
    color: '#3e7891',
    story: '采用原粮带壳仓储方式，全程维持低温与高纯度充氮环境，抑制大米呼吸作用与脂肪酸劣变，确保跨季节出库口感稳定。',
    evidence: '控温：15℃恒温 · 高阻隔充氮 · 锁鲜周期：365天',
    meta: '恒温保鲜 · 充氮气调 · 原粮仓储',
  },
  {
    id: 'market',
    x: 776,
    y: 282,
    coord: [121.3821, 31.1123],
    short: '市场',
    type: '市场',
    name: '华东精品主粮与地理标志风物直销枢纽',
    color: '#7c6fb1',
    story: '辐射长三角高端主销区。每袋出库大米绑定地标溯源二维码，直供城市有机商超、精品零售和高端膳食渠道。',
    evidence: '精品零售 · 一袋一码 · 长三角渠道',
    meta: '上海枢纽 · 精品主粮 · 数字追溯',
  },
  {
    id: 'dining',
    x: 558,
    y: 402,
    coord: [121.4737, 31.2304],
    short: '餐桌',
    type: '餐饮',
    name: '东方米食美学与高端膳食体验空间',
    color: '#c64240',
    story: '五常大米进入现代膳食空间后，淀粉与蛋白质比例在烹调中形成稳定口感。饭粒油亮、香气外溢，完成从黑土地到都市餐桌的证据链闭环。',
    evidence: '高端日料 · 柴火米饭 · 饭粒油亮',
    meta: '米食美学 · 高端膳食 · 城市餐桌',
  },
]

const routes = [
  { id: 'r1', path: 'M204 384 C235 333 272 290 326 306' },
  { id: 'r2', path: 'M326 306 C382 288 436 338 482 352' },
  { id: 'r3', path: 'M482 352 C586 302 682 268 776 282' },
  { id: 'r4', path: 'M482 352 C514 388 532 418 558 402' },
]

const particles = [
  { id: 'p1', className: 'particle particle-one' },
  { id: 'p2', className: 'particle particle-two' },
  { id: 'p3', className: 'particle particle-three' },
  { id: 'p4', className: 'particle particle-four' },
]

const posterNodes = [
  { id: 'poster-origin', x: 148, y: 256, label: '产地' },
  { id: 'poster-process', x: 246, y: 210, label: '加工' },
  { id: 'poster-storage', x: 348, y: 242, label: '仓储' },
  { id: 'poster-market', x: 468, y: 198, label: '市场' },
  { id: 'poster-dining', x: 420, y: 310, label: '餐桌' },
]

const posterProofs = computed(() => activeProductId.value === 'rice'
  ? [
      { label: '产地环境', value: '寒地黑土 · 拉林河流域', note: '低温长日照与肥沃黑土共同塑造稻米香气和颗粒饱满度。' },
      { label: '加工工艺', value: '低温烘干 · 分级碾磨', note: '控制水分和碎米率，保留新米香气，适合礼盒与家庭主食。' },
      { label: '品质认证', value: '地理标志 · 批次质检', note: '建议接入产区授权、检测报告、入库批次和包装追溯码。' },
      { label: '供应链', value: '产区仓储 · 冷凉干燥配送', note: '以东北产区仓储为起点，覆盖城市商超、团餐和电商渠道。' },
    ]
  : [
      { label: '产地环境', value: '大渡河干热河谷 · 海拔1600m', note: '独享干热河谷微气候，极端昼夜温差促油胞浓缩，正路贡椒原产地。' },
      { label: '加工工艺', value: '伏天手工采摘 · 智能分级', note: '非遗初加工技艺。筛分>4.5mm，低温太阳能曝晒，自然脱籽。' },
      { label: '品质认证', value: '挥发油≥5.5% · 农残0检出', note: 'SGS/谱尼测试抽检。羟基山椒素≥35mg/g，远超国家标准。' },
      { label: '供应链', value: '充氮真空 · 0-4℃冷链直达', note: '高阻隔充氮包装，全程恒温锁鲜。绑定数字化追溯二维码。' },
    ])

const mapMetrics = computed(() => [
  { label: '空间证据', value: '5 个节点' },
  { label: '地理范围', value: coverageRegions.value },
  { label: '输出用途', value: '公示牌 / 长图 / 展板' },
])
const traceRouteLabel = computed(() => nodes.value.map(stage => stage.short).join(' → '))
const archiveCapsules = computed(() => {
  const identityTags = identityItems.value.map(item => ({
    label: item.label,
    value: item.value,
  }))
  const evidenceTags = nodes.value.flatMap(node => node.evidence.split(' · ').slice(0, 2).map(tag => ({
    label: node.short,
    value: tag,
  })))
  return [...identityTags, ...evidenceTags].slice(0, 12)
})


const activeView = computed(() => views.find(view => view.id === currentView.value) || views[0])
const nodes = computed(() => activeProductId.value === 'rice' ? riceStages : pepperStages)
const coverageRegions = computed(() => {
  const regions = new Set(nodes.value.map(n => n.coord[0] > 120 ? '东北/沪' : n.coord[0] > 110 ? '沪' : n.coord[0] > 106 ? '渝' : n.coord[0] > 104 ? '川' : '川'))
  const ordered = []
  if ([...regions].includes('川')) ordered.push('川')
  if ([...regions].includes('渝')) ordered.push('渝')
  if ([...regions].includes('沪')) ordered.push('沪')
  if ([...regions].includes('东北/沪')) ordered.push('东北/沪')
  return ordered.join(' · ')
})
const selectedNode = computed(() => nodes.value.find(item => item.id === selectedNodeId.value) || nodes.value[0])
const nextNodeId = computed(() => {
  const index = nodes.value.findIndex(item => item.id === selectedNodeId.value)
  return nodes.value[(index + 1) % nodes.value.length].id
})

const routePairs = [
  ['origin', 'process'],
  ['process', 'storage'],
  ['storage', 'market'],
  ['storage', 'dining'],
]

function getTraceBounds() {
  const bounds = new maplibregl.LngLatBounds()
  nodes.value.forEach(node => bounds.extend(node.coord))
  return bounds
}

function fitTraceView(activeMap, mode = 'atlas') {
  if (!activeMap || !nodes.value.length) return
  const paddingMap = {
    atlas: { top: 120, right: 440, bottom: 170, left: 120 },
    poster: { top: 54, right: 54, bottom: 54, left: 54 },
    archive: { top: 90, right: 84, bottom: 90, left: 84 },
    chain: { top: 70, right: 70, bottom: 70, left: 70 },
  }
  const maxZoomMap = {
    atlas: 5.1,
    poster: 4.6,
    archive: 5.2,
    chain: 5,
  }
  activeMap.resize()
  activeMap.fitBounds(getTraceBounds(), {
    padding: paddingMap[mode] || paddingMap.atlas,
    maxZoom: maxZoomMap[mode] || 5,
    duration: 0,
  })
  if (mode === 'atlas') {
    activeMap.setPitch(38)
    activeMap.setBearing(-10)
  } else if (mode === 'archive') {
    activeMap.setPitch(28)
    activeMap.setBearing(-8)
  } else {
    activeMap.setPitch(0)
    activeMap.setBearing(0)
  }
}

function buildCurve(start, end, bend = 0.18) {
  const [lng1, lat1] = start
  const [lng2, lat2] = end
  const dx = lng2 - lng1
  const dy = lat2 - lat1
  const control = [
    (lng1 + lng2) / 2 - dy * bend,
    (lat1 + lat2) / 2 + dx * bend * 0.42,
  ]

  return Array.from({ length: 34 }, (_, index) => {
    const t = index / 33
    const mt = 1 - t
    return [
      mt * mt * lng1 + 2 * mt * t * control[0] + t * t * lng2,
      mt * mt * lat1 + 2 * mt * t * control[1] + t * t * lat2,
    ]
  })
}

function buildRouteGeoJson() {
  return {
    type: 'FeatureCollection',
    features: routePairs.map(([fromId, toId], index) => {
      const from = nodes.value.find(node => node.id === fromId)
      const to = nodes.value.find(node => node.id === toId)
      return {
        type: 'Feature',
        properties: {
          id: `trace-route-${index + 1}`,
          from: from.name,
          to: to.name,
        },
        geometry: {
          type: 'LineString',
          coordinates: buildCurve(from.coord, to.coord, index === 3 ? -0.16 : 0.2),
        },
      }
    }),
  }
}

function buildNodeGeoJson() {
  return {
    type: 'FeatureCollection',
    features: nodes.value.map(node => ({
      type: 'Feature',
      properties: {
        id: node.id,
        name: node.name,
        type: node.type,
        color: node.color,
      },
      geometry: {
        type: 'Point',
        coordinates: node.coord,
      },
    })),
  }
}

async function addContextLayers(map) {
  const contextLayers = [
    { id: 'trace-coastline', url: '/tiles/vector/coastline', color: '#8a7560', width: 0.55, opacity: 0.48 },
    { id: 'trace-rivers', url: '/tiles/vector/rivers', color: '#4f95ad', width: 0.55, opacity: 0.58 },
    { id: 'trace-ecoregions', url: '/tiles/vector/ecoregions', color: '#6f8b63', width: 0.8, opacity: 0.22 },
  ]

  for (const layer of contextLayers) {
    try {
      if (!map.getSource(layer.id)) {
        map.addSource(layer.id, { type: 'geojson', data: layer.url })
      }
      if (!map.getLayer(layer.id)) {
        map.addLayer({
          id: layer.id,
          type: 'line',
          source: layer.id,
          paint: {
            'line-color': layer.color,
            'line-width': layer.width,
            'line-opacity': layer.opacity,
          },
        })
      }
    } catch (error) {
      console.warn(`${layer.id} skipped`, error)
    }
  }
}

function addTraceLayers(map) {
  if (!map.getSource('trace-routes')) {
    map.addSource('trace-routes', {
      type: 'geojson',
      lineMetrics: true,
      data: buildRouteGeoJson(),
    })
  }

  if (!map.getLayer('trace-route-glow')) {
    map.addLayer({
      id: 'trace-route-glow',
      type: 'line',
      source: 'trace-routes',
      paint: {
        'line-color': '#b8793d',
        'line-width': 15,
        'line-opacity': 0.18,
        'line-blur': 6,
      },
    })
  }

  if (!map.getLayer('trace-route-main')) {
    map.addLayer({
      id: 'trace-route-main',
      type: 'line',
      source: 'trace-routes',
      paint: {
        'line-width': 4.2,
        'line-opacity': 0.95,
        'line-color': [
          'interpolate',
          ['linear'],
          ['line-progress'],
          0,
          '#6f8b63',
          0.52,
          '#c39b44',
          1,
          '#c4503d',
        ],
      },
    })
  }

  if (!map.getSource('trace-nodes')) {
    map.addSource('trace-nodes', { type: 'geojson', data: buildNodeGeoJson() })
  }

  if (!map.getLayer('trace-node-halo')) {
    map.addLayer({
      id: 'trace-node-halo',
      type: 'circle',
      source: 'trace-nodes',
      paint: {
        'circle-radius': 20,
        'circle-color': '#fff6e4',
        'circle-opacity': 0.62,
        'circle-stroke-color': ['get', 'color'],
        'circle-stroke-width': 2,
      },
    })
  }
}

function updateProjectedNodes() {
  if (!atlasMap || !atlasMapContainer.value) return
  const labelOffsets = {
    origin: [-138, -118],
    process: [86, -106],
    storage: [96, 38],
    market: [-142, -92],
    dining: [82, 78],
  }
  projectedNodes.value = nodes.value.map(node => {
    const point = atlasMap.project(node.coord)
    const [offsetX, offsetY] = labelOffsets[node.id] || [76, -76]
    const labelX = point.x + offsetX
    const labelY = point.y + offsetY
    const elbowX = point.x + offsetX * 0.48
    const elbowY = point.y + offsetY * 0.42
    return {
      ...node,
      x: point.x,
      y: point.y,
      labelX,
      labelY,
      leader: `${point.x.toFixed(1)},${point.y.toFixed(1)} ${elbowX.toFixed(1)},${elbowY.toFixed(1)} ${labelX.toFixed(1)},${labelY.toFixed(1)}`,
    }
  })

  projectedRoutePaths.value = routePairs.map(([fromId, toId], index) => {
    const from = nodes.value.find(node => node.id === fromId)
    const to = nodes.value.find(node => node.id === toId)
    const points = buildCurve(from.coord, to.coord, index === 3 ? -0.16 : 0.2)
      .map(coord => atlasMap.project(coord))
    const d = points.map((point, pointIndex) => `${pointIndex === 0 ? 'M' : 'L'} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(' ')
    return { id: `projected-route-${index + 1}`, d }
  })
}

function selectMapNode(id) {
  selectedNodeId.value = id
  const node = nodes.value.find(item => item.id === id)
  if (!node || !atlasMap) return
  atlasMap.easeTo({
    center: node.coord,
    zoom: Math.max(atlasMap.getZoom(), node.id === 'market' ? 4.2 : 5.6),
    pitch: 42,
    bearing: node.id === 'market' ? -16 : -8,
    duration: 900,
  })
}

async function initAtlasMap() {
  if (atlasMap || !atlasMapContainer.value || currentView.value !== 'atlas') return

  mapReady.value = false
  atlasMap = new maplibregl.Map({
    container: atlasMapContainer.value,
    style: MAP_STYLE,
    center: [106.6, 30.4],
    zoom: 4.45,
    pitch: 38,
    bearing: -10,
    antialias: true,
    attributionControl: false,
    preserveDrawingBuffer: true,
  })

  atlasMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right')
  atlasMap.on('load', async () => {
    await addContextLayers(atlasMap)
    addTraceLayers(atlasMap)
    fitTraceView(atlasMap, 'atlas')
    mapReady.value = true
    updateProjectedNodes()
    atlasMap.once('idle', updateProjectedNodes)
  })
  atlasMap.on('move', updateProjectedNodes)
  atlasMap.on('resize', updateProjectedNodes)
  atlasMap.on('click', 'trace-node-halo', event => {
    const id = event.features?.[0]?.properties?.id
    if (id) selectMapNode(id)
  })
  atlasMap.on('mouseenter', 'trace-node-halo', () => {
    atlasMap.getCanvas().style.cursor = 'pointer'
  })
  atlasMap.on('mouseleave', 'trace-node-halo', () => {
    atlasMap.getCanvas().style.cursor = ''
  })
}

function destroyAtlasMap() {
  if (!atlasMap) return
  atlasMap.remove()
  atlasMap = null
  mapReady.value = false
  projectedNodes.value = []
  projectedRoutePaths.value = []
}

async function initPosterMap() {
  if (posterMap || !posterMapContainer.value || currentView.value !== 'brand') return
  posterMapReady.value = false
  posterMap = new maplibregl.Map({
    container: posterMapContainer.value,
    style: MAP_STYLE,
    center: [108, 30.8],
    zoom: 4.2,
    pitch: 0,
    bearing: 0,
    antialias: true,
    attributionControl: false,
    preserveDrawingBuffer: true,
  })
  posterMap.on('load', async () => {
    await addContextLayers(posterMap)
    addTraceLayers(posterMap)
    fitTraceView(posterMap, 'poster')
    posterMapReady.value = true
  })
}

function destroyPosterMap() {
  if (!posterMap) return
  posterMap.remove()
  posterMap = null
  posterMapReady.value = false
}

async function initArchiveMap() {
  if (archiveMap || !archiveMapContainer.value || currentView.value !== 'archive') return
  archiveMapReady.value = false
  archiveMap = new maplibregl.Map({
    container: archiveMapContainer.value,
    style: MAP_STYLE,
    center: [106.6, 30.4],
    zoom: 4.45,
    pitch: 28,
    bearing: -8,
    antialias: true,
    attributionControl: false,
    preserveDrawingBuffer: true,
  })
  archiveMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right')
  archiveMap.on('load', async () => {
    await addContextLayers(archiveMap)
    addTraceLayers(archiveMap)
    fitTraceView(archiveMap, 'archive')
    archiveMapReady.value = true
  })
}

function destroyArchiveMap() {
  if (!archiveMap) return
  archiveMap.remove()
  archiveMap = null
  archiveMapReady.value = false
}

async function initChainMap() {
  if (chainMap || !chainMapContainer.value || currentView.value !== 'chain') return
  chainMap = new maplibregl.Map({
    container: chainMapContainer.value,
    style: MAP_STYLE,
    center: [106.6, 30.4],
    zoom: 4.45,
    pitch: 0,
    bearing: 0,
    antialias: true,
    attributionControl: false,
    preserveDrawingBuffer: true,
  })
  chainMap.on('load', async () => {
    await addContextLayers(chainMap)
    addTraceLayers(chainMap)
  })
}

function destroyChainMap() {
  if (!chainMap) return
  chainMap.remove()
  chainMap = null
}

function destroyAllMaps() {
  destroyAtlasMap()
  destroyPosterMap()
  destroyArchiveMap()
  destroyChainMap()
}

function initCurrentMap() {
  if (currentView.value === 'atlas') {
    initAtlasMap()
  } else if (currentView.value === 'brand') {
    initPosterMap()
  } else if (currentView.value === 'archive') {
    initArchiveMap()
  } else if (currentView.value === 'chain') {
    initChainMap()
  }
}

onMounted(() => {
  nextTick(initCurrentMap)
})

onUnmounted(() => {
  destroyAllMaps()
})

watch(currentView, view => {
  if (view === 'atlas') {
    destroyPosterMap()
    destroyArchiveMap()
    destroyChainMap()
    nextTick(() => {
      initAtlasMap()
      atlasMap?.resize()
      updateProjectedNodes()
    })
  } else if (view === 'brand') {
    destroyAtlasMap()
    destroyArchiveMap()
    destroyChainMap()
    nextTick(() => initPosterMap())
  } else if (view === 'chain') {
    destroyAtlasMap()
    destroyPosterMap()
    destroyArchiveMap()
    nextTick(() => initChainMap())
  } else if (view === 'archive') {
    destroyAtlasMap()
    destroyPosterMap()
    destroyChainMap()
    nextTick(() => initArchiveMap())
  }
})

watch(selectedNodeId, id => {
  if (!atlasMap || currentView.value !== 'atlas') return
  const node = nodes.value.find(item => item.id === id)
  if (!node) return
  const source = atlasMap.getSource('trace-nodes')
  source?.setData(buildNodeGeoJson())
})

watch(activeProductId, () => {
  selectedNodeId.value = 'origin'
  const maps = [
    { instance: atlasMap, mode: 'atlas' },
    { instance: posterMap, mode: 'poster' },
    { instance: archiveMap, mode: 'archive' },
    { instance: chainMap, mode: 'chain' },
  ]
  for (const active of maps) {
    active.instance?.getSource('trace-routes')?.setData(buildRouteGeoJson())
    active.instance?.getSource('trace-nodes')?.setData(buildNodeGeoJson())
    fitTraceView(active.instance, active.mode)
  }
  updateProjectedNodes()
})

function waitForMapIdle(activeMap) {
  if (!activeMap) return Promise.resolve()
  activeMap.resize()
  return new Promise(resolve => {
    const done = () => resolve()
    if (activeMap.loaded() && !activeMap.areTilesLoaded?.()) {
      activeMap.once('idle', done)
      window.setTimeout(done, 1200)
      return
    }
    activeMap.once('idle', done)
    window.setTimeout(done, 900)
  })
}

async function downloadCapture(format = 'png') {
  const target = document.querySelector('#capture-zone')
  if (!target || isExporting.value) return

  isExporting.value = true
  try {
    await nextTick()
    const activeMap = currentView.value === 'atlas'
      ? atlasMap
      : currentView.value === 'brand'
        ? posterMap
        : currentView.value === 'archive'
          ? archiveMap
          : null
    await waitForMapIdle(activeMap)
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))
    const canvas = await html2canvas(target, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#f7efe1',
      logging: false,
      imageTimeout: 15000,
    })
    const mime = format === 'jpeg' ? 'image/jpeg' : 'image/png'
    const ext = format === 'jpeg' ? 'jpg' : 'png'
    const link = document.createElement('a')
    link.download = `flavorscape-${currentView.value}-${activeProductId.value}-${Date.now()}.${ext}`
    link.href = canvas.toDataURL(mime, 0.92)
    link.click()
  } catch (error) {
    console.error('导出产品画布失败', error)
    window.alert('导出失败，请稍后重试；如果地图仍在加载，请等待底图出现后再导出。')
  } finally {
    isExporting.value = false
  }
}

function printCapture() {
  window.print()
}
</script>

<style scoped>
.product-page {
  position: fixed;
  inset: var(--navbar-h) 0 0;
  overflow: auto;
  --ink: #241d17;
  --muted: #6f6254;
  --paper: #f7efe1;
  --paper-strong: #fff9ec;
  --line: rgba(107, 84, 55, 0.18);
  --accent: #8b5e34;
  --leaf: #6f8b63;
  --water: #3e7891;
  background:
    linear-gradient(90deg, rgba(116, 92, 62, 0.045) 1px, transparent 1px),
    linear-gradient(180deg, rgba(116, 92, 62, 0.04) 1px, transparent 1px),
    radial-gradient(circle at 18% 12%, rgba(111, 139, 99, 0.16), transparent 26%),
    radial-gradient(circle at 82% 16%, rgba(62, 120, 145, 0.12), transparent 28%),
    linear-gradient(135deg, #f3e8d5, #eef2e4 52%, #eadcc6);
  background-size: 42px 42px, 42px 42px, auto, auto, auto;
  color: var(--ink);
}

.studio-toolbar {
  position: sticky;
  top: 0;
  z-index: 20;
  min-height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 22px;
  padding: 12px 28px;
  border-bottom: 1px solid rgba(107, 84, 55, 0.14);
  background: rgba(250, 245, 236, 0.82);
  backdrop-filter: blur(18px);
}

.toolbar-copy span,
.eyebrow,
.mini-map-title span,
.poster-masthead span,
.poster-footer span,
.poster-proof-grid span {
  display: block;
  color: rgba(104, 88, 70, 0.74);
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.toolbar-copy strong {
  display: block;
  margin-top: 3px;
  color: var(--ink);
  font-size: 16px;
  font-weight: 700;
}

.toolbar-copy p {
  margin-top: 3px;
  color: rgba(73, 61, 49, 0.68);
  font-size: 12px;
}

.product-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.product-switcher button {
  min-width: 116px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(107, 84, 55, 0.14);
  border-radius: 999px;
  padding: 5px 11px 5px 6px;
  background: rgba(255, 249, 236, 0.55);
  color: rgba(51, 42, 34, 0.72);
  cursor: pointer;
  transition: background 180ms ease, border-color 180ms ease, transform 180ms ease;
}

.product-switcher button.active {
  border-color: rgba(139, 94, 52, 0.42);
  background: rgba(255, 249, 236, 0.86);
  color: var(--accent);
}

.product-switcher img {
  width: 28px;
  height: 28px;
  object-fit: contain;
  border-radius: 50%;
  background: rgba(255,255,255,0.64);
}

.product-switcher span {
  font-size: 12px;
  font-weight: 800;
}

.toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.toolbar-actions button,
.map-heading button {
  border: 1px solid rgba(107, 84, 55, 0.18);
  border-radius: 999px;
  padding: 8px 14px;
  background: rgba(255, 249, 236, 0.72);
  color: rgba(51, 42, 34, 0.74);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  transition: transform 180ms ease, background 180ms ease, color 180ms ease, border-color 180ms ease;
}

.toolbar-actions button:hover,
.toolbar-actions button.active {
  transform: translateY(-1px);
  border-color: rgba(139, 94, 52, 0.42);
  background: rgba(139, 94, 52, 0.1);
  color: var(--accent);
}

.toolbar-actions .download-btn {
  border-color: rgba(36, 29, 23, 0.16);
  background: #2a241e;
  color: #fff5e3;
}

.toolbar-actions .download-btn.secondary {
  background: rgba(36, 29, 23, 0.08);
  color: rgba(36, 29, 23, 0.78);
}

.toolbar-actions .download-btn:disabled {
  cursor: wait;
  opacity: 0.62;
}

.poster-stage {
  min-height: calc(100% - 72px);
  display: grid;
  place-items: start center;
  padding: 30px 24px 54px;
}

.poster-card {
  position: relative;
  width: min(660px, calc(100vw - 48px));
  aspect-ratio: 3 / 4;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto auto;
  gap: 16px;
  padding: 26px;
  overflow: hidden;
  border: 1px solid rgba(107, 84, 55, 0.18);
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(255, 249, 236, 0.92), rgba(245, 235, 218, 0.96)),
    #f8f0df;
  box-shadow: 0 28px 80px rgba(64, 43, 24, 0.22);
}

.view-brand .poster-card,
.view-archive .archive-canvas {
  border: 0;
  border-radius: 0;
  background:
    linear-gradient(90deg, rgba(83, 72, 56, 0.08) 1px, transparent 1px),
    linear-gradient(180deg, rgba(83, 72, 56, 0.065) 1px, transparent 1px),
    #f7f1e7;
  background-size: 32px 32px;
  box-shadow: none;
}

.poster-masthead {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 156px;
  gap: 18px;
  align-items: center;
}

.poster-masthead h1 {
  margin-top: 8px;
  font-family: var(--font-serif);
  font-size: 50px;
  font-weight: 500;
  line-height: 1.02;
}

.poster-masthead p {
  margin-top: 10px;
  color: rgba(53, 43, 33, 0.72);
  font-size: 13px;
  line-height: 1.7;
}

.poster-product-seal {
  display: grid;
  justify-items: center;
  gap: 5px;
  padding: 0;
  border: 0;
  background: transparent;
}

.poster-product-seal img {
  width: 148px;
  height: 148px;
  object-fit: contain;
  border-radius: 50%;
  background: transparent;
  transform: translate(8px, -8px) scale(1.08);
  filter: drop-shadow(0 22px 24px rgba(80, 48, 25, 0.18));
}

.poster-product-seal strong {
  font-family: var(--font-serif);
  font-size: 17px;
  font-weight: 500;
}

.poster-product-seal span {
  text-align: center;
  letter-spacing: 0.04em;
}

.poster-map-anchor {
  position: relative;
  width: 300px;
  height: 300px;
  justify-self: center;
  align-self: center;
  min-height: 0;
  overflow: hidden;
  border: 1px solid rgba(107, 84, 55, 0.14);
  border-radius: 50%;
  background: #dfe9e3;
  box-shadow: inset 0 0 0 1px rgba(255, 249, 236, 0.48);
}

.poster-map-anchor::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(180deg, rgba(20, 25, 20, 0.04), transparent 28%),
    linear-gradient(0deg, rgba(33, 26, 19, 0.18), transparent 42%);
}

.poster-map-glass {
  position: absolute;
  left: 34px;
  right: 34px;
  bottom: 28px;
  z-index: 2;
  display: grid;
  gap: 3px;
  padding: 13px 15px;
  border: 1px solid rgba(255, 249, 236, 0.56);
  border-radius: 12px;
  background: rgba(255, 249, 236, 0.82);
  backdrop-filter: blur(14px);
  box-shadow: 0 16px 34px rgba(40, 31, 22, 0.16);
}

.poster-map-glass strong {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 500;
}

.poster-map-glass p {
  color: rgba(53, 43, 33, 0.64);
  font-size: 11px;
}

.poster-route-tags {
  position: absolute;
  left: 50%;
  top: 20px;
  z-index: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  transform: translateX(-50%);
}

.poster-route-tags span {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 4px 9px;
  border: 1px solid var(--node-color);
  border-radius: 999px;
  background: rgba(255, 249, 236, 0.82);
  color: var(--node-color);
  font-size: 11px;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(50, 36, 20, 0.1);
}

.poster-map,
.large-map {
  display: block;
  width: 100%;
  height: 100%;
}

.map-water {
  fill: #e9efe9;
}

.map-land,
.atlas-land {
  fill: url(#atlasLand);
  stroke: rgba(100, 82, 60, 0.32);
  stroke-width: 2;
}

.poster-map .map-land {
  fill: #eadfca;
}

.terrain,
.atlas-terrain {
  fill: rgba(111, 139, 99, 0.22);
  stroke: rgba(111, 139, 99, 0.54);
  stroke-width: 2;
  stroke-dasharray: 8 7;
}

.river,
.atlas-river {
  fill: none;
  stroke: rgba(62, 120, 145, 0.34);
  stroke-width: 5;
  stroke-linecap: round;
}

.atlas-river-thin {
  stroke-width: 2.5;
  stroke-dasharray: 10 9;
}

.poster-route,
.atlas-route {
  fill: none;
  stroke: url(#atlasRoute);
  stroke-width: 6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.poster-route {
  stroke: url(#posterRoute);
}

.route-glow {
  fill: none;
  stroke: url(#atlasRoute);
  stroke-width: 22;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.16;
  filter: url(#atlasRouteGlow);
}

.poster-map .route-glow {
  stroke: url(#posterRoute);
  filter: url(#posterGlow);
}

.poster-node circle,
.node-halo {
  fill: rgba(255, 250, 238, 0.88);
  stroke: rgba(107, 84, 55, 0.14);
  stroke-width: 1;
  filter: drop-shadow(0 10px 14px rgba(67, 43, 24, 0.18));
}

.poster-node text,
.atlas-node text {
  fill: rgba(36, 29, 23, 0.82);
  font-size: 13px;
  font-weight: 800;
  paint-order: stroke;
  stroke: rgba(255, 249, 236, 0.94);
  stroke-width: 4px;
}

.poster-proof-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.poster-proof-grid article {
  padding: 11px;
  border-radius: 0;
  background: transparent;
  border-top: 1px solid rgba(107, 84, 55, 0.18);
  box-shadow: none;
}

.poster-proof-grid strong {
  display: block;
  margin-top: 5px;
  color: var(--accent);
  font-size: 14px;
}

.poster-proof-grid p {
  margin-top: 4px;
  color: rgba(53, 43, 33, 0.66);
  font-size: 11px;
  line-height: 1.45;
}

.poster-footer {
  display: grid;
  grid-template-columns: 76px 1fr;
  gap: 12px;
  align-items: center;
  padding-top: 12px;
  border-top: 1px dashed rgba(107, 84, 55, 0.26);
}

.poster-footer strong {
  display: block;
  margin-top: 4px;
  font-size: 13px;
}

.poster-footer p {
  margin-top: 4px;
  color: rgba(53, 43, 33, 0.64);
  font-size: 11px;
}

.qr-code {
  width: 72px;
  height: 72px;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 3px;
  padding: 7px;
  border-radius: 10px;
  background: #fffaf0;
  box-shadow: inset 0 0 0 1px rgba(107, 84, 55, 0.16);
}

.qr-code i {
  border-radius: 2px;
  background: rgba(36, 29, 23, 0.84);
}

.qr-code i:nth-child(3n),
.qr-code i:nth-child(4n + 1) {
  opacity: 0.2;
}

.story-stage {
  min-height: calc(100% - 72px);
  padding: 28px 32px 44px;
}

.storymap-canvas {
  width: min(1540px, 100%);
  min-height: calc(100vh - var(--navbar-h) - 128px);
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  grid-template-areas:
    "map side"
    "detail side";
  align-items: stretch;
  gap: 18px;
  margin: 0 auto;
}

.atlas-panel,
.atlas-map-card {
  border: 1px solid rgba(107, 84, 55, 0.16);
  background:
    linear-gradient(90deg, rgba(116, 92, 62, 0.04) 1px, transparent 1px),
    linear-gradient(180deg, rgba(116, 92, 62, 0.035) 1px, transparent 1px),
    rgba(255, 249, 236, 0.76);
  background-size: 36px 36px;
  box-shadow: 0 24px 70px rgba(57, 42, 25, 0.13), inset 0 1px 0 rgba(255, 255, 255, 0.62);
}

.atlas-panel {
  position: relative;
  z-index: 1;
  padding: 24px;
  border-radius: 12px;
}

.atlas-left {
  grid-area: detail;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) 220px minmax(260px, 0.9fr);
  gap: 20px;
  align-items: center;
}

.atlas-right {
  grid-area: side;
  align-self: stretch;
  overflow: hidden;
}

.atlas-map-card {
  grid-area: map;
  position: relative;
  z-index: 3;
  margin: 0;
  padding: 20px;
  border-radius: 14px;
  background-color: rgba(250, 243, 230, 0.92);
}

.atlas-panel h2 {
  margin-top: 8px;
  font-family: var(--font-serif);
  font-size: 28px;
  font-weight: 500;
}

.atlas-panel p {
  margin-top: 12px;
  color: rgba(53, 43, 33, 0.72);
  font-size: 13px;
  line-height: 1.8;
}

.atlas-panel-lede {
  margin-top: 8px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(107, 84, 55, 0.12);
}

.product-photo {
  height: 170px;
  display: grid;
  place-items: center;
  margin: 0;
  border-radius: 12px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.82), rgba(111, 139, 99, 0.12));
}

.product-photo img {
  width: 88%;
  height: 88%;
  object-fit: contain;
  filter: drop-shadow(0 18px 22px rgba(64, 43, 24, 0.18));
}

.atlas-panel dl {
  display: grid;
  gap: 12px;
}

.atlas-panel dl div {
  padding-top: 12px;
  border-top: 1px solid rgba(107, 84, 55, 0.14);
}

.atlas-panel dt {
  color: rgba(104, 88, 70, 0.74);
  font-size: 11px;
}

.atlas-panel dd {
  margin-top: 5px;
  color: rgba(36, 29, 23, 0.82);
  font-size: 13px;
  line-height: 1.55;
}

.map-heading {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 12px;
}

.map-heading h1 {
  margin-top: 7px;
  font-family: var(--font-serif);
  font-size: clamp(30px, 3vw, 44px);
  font-weight: 500;
  line-height: 1.06;
}

.map-metric-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.map-metric-strip article {
  padding: 10px 12px;
  border: 1px solid rgba(107, 84, 55, 0.12);
  border-radius: 10px;
  background: rgba(255, 249, 236, 0.62);
}

.map-metric-strip span {
  display: block;
  color: rgba(104, 88, 70, 0.68);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.map-metric-strip strong {
  display: block;
  margin-top: 4px;
  color: var(--ink);
  font-size: 15px;
}

.large-map-wrap {
  position: relative;
  min-height: 0;
  height: min(68vh, 700px);
  overflow: hidden;
  border-radius: 12px;
}

.atlas-real-map {
  position: absolute;
  inset: 0;
  overflow: hidden;
  border-radius: 12px;
  background:
    radial-gradient(circle at 22% 24%, rgba(111, 139, 99, 0.18), transparent 30%),
    #dfe9e3;
  box-shadow: inset 0 0 0 1px rgba(107, 84, 55, 0.12);
}

.atlas-real-map :deep(.maplibregl-canvas) {
  filter: saturate(0.86) contrast(0.96) sepia(0.08);
}

.atlas-real-map :deep(.maplibregl-ctrl-bottom-right) {
  right: 10px;
  bottom: 10px;
}

.map-loading {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: grid;
  place-items: center;
  color: rgba(53, 43, 33, 0.62);
  font-size: 13px;
  letter-spacing: 0.08em;
  background: rgba(247, 239, 225, 0.62);
}

.atlas-map-overlay {
  position: absolute;
  inset: 0;
  z-index: 4;
  pointer-events: none;
}

.projected-route-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.projected-route-halo,
.projected-route-line {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.projected-route-halo {
  stroke: rgba(255, 248, 230, 0.88);
  stroke-width: 13;
  opacity: 0.72;
  filter: drop-shadow(0 6px 12px rgba(73, 50, 28, 0.22));
}

.projected-route-line {
  stroke: url(#projectedRouteGradient);
  stroke-width: 5.5;
  stroke-dasharray: 1 13;
  animation: routeDash 2.8s linear infinite;
}

@keyframes routeDash {
  to {
    stroke-dashoffset: -56;
  }
}

.leader-line {
  fill: none;
  stroke: rgba(255, 249, 236, 0.82);
  stroke-width: 1.2;
  stroke-dasharray: 4 5;
  filter: drop-shadow(0 2px 5px rgba(20, 25, 28, 0.28));
}

.real-map-dot {
  position: absolute;
  width: 16px;
  height: 16px;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(255, 249, 236, 0.92);
  border-radius: 50%;
  background: var(--node-color);
  cursor: pointer;
  pointer-events: auto;
  box-shadow:
    0 0 0 7px rgba(255, 249, 236, 0.14),
    0 0 26px rgba(118, 196, 214, 0.34),
    0 10px 18px rgba(20, 25, 28, 0.28);
  animation: mapNodePulse 2.8s ease-in-out infinite;
}

.real-map-dot.selected {
  width: 20px;
  height: 20px;
}

.real-map-label {
  position: absolute;
  width: 168px;
  transform: translate(-50%, -50%);
  display: grid;
  gap: 3px;
  padding: 9px 10px;
  border: 0;
  border-radius: 10px;
  background: rgba(16, 22, 24, 0.48);
  color: rgba(255, 249, 236, 0.92);
  text-align: left;
  cursor: pointer;
  pointer-events: auto;
  backdrop-filter: blur(12px);
  box-shadow: 0 16px 30px rgba(12, 18, 22, 0.2);
}

.real-map-label span {
  color: #d8f4ff;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.real-map-label strong {
  font-size: 15px;
  line-height: 1.1;
}

.real-map-label em {
  color: rgba(255, 249, 236, 0.68);
  font-size: 10px;
  font-style: normal;
  line-height: 1.35;
}

.real-map-label.selected {
  background: rgba(255, 249, 236, 0.86);
  color: var(--ink);
}

.product-page.view-atlas {
  background:
    radial-gradient(circle at 22% 20%, rgba(77, 142, 169, 0.22), transparent 34%),
    radial-gradient(circle at 78% 18%, rgba(111, 139, 99, 0.16), transparent 30%),
    linear-gradient(135deg, #0e171b, #1b2524 52%, #172022);
}

.product-page.view-brand,
.product-page.view-archive {
  background:
    linear-gradient(90deg, rgba(83, 72, 56, 0.08) 1px, transparent 1px),
    linear-gradient(180deg, rgba(83, 72, 56, 0.065) 1px, transparent 1px),
    #f4efe6;
  background-size: 34px 34px;
}

.real-map-label.selected em {
  color: rgba(53, 43, 33, 0.62);
}

@keyframes mapNodePulse {
  0%,
  100% {
    box-shadow:
      0 0 0 6px rgba(255, 249, 236, 0.12),
      0 10px 18px rgba(20, 25, 28, 0.28),
      0 0 16px rgba(118, 196, 214, 0.28);
  }
  50% {
    box-shadow:
      0 0 0 12px rgba(255, 249, 236, 0.08),
      0 14px 24px rgba(20, 25, 28, 0.3),
      0 0 32px rgba(118, 196, 214, 0.42);
  }
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}

.large-map {
  min-height: 560px;
}

.legacy-map {
  visibility: hidden;
  pointer-events: none;
}

.node-disc {
  fill: rgba(255, 249, 236, 0.96);
  stroke: rgba(255, 249, 236, 0.95);
  stroke-width: 3;
}

.atlas-node {
  cursor: pointer;
}

.atlas-node.selected .node-halo {
  stroke: var(--accent);
  stroke-width: 3;
}

.particle {
  fill: #fff8e7;
  stroke: #a86a38;
  stroke-width: 2;
  filter: drop-shadow(0 0 10px rgba(184, 121, 61, 0.5));
}

.particle-one {
  offset-path: path('M204 384 C235 333 272 290 326 306');
  animation: routeMove 4.8s linear infinite;
}

.particle-two {
  offset-path: path('M326 306 C382 288 436 338 482 352');
  animation: routeMove 5.2s 0.6s linear infinite;
}

.particle-three {
  offset-path: path('M482 352 C586 302 682 268 776 282');
  animation: routeMove 5.4s 1.2s linear infinite;
}

.particle-four {
  offset-path: path('M482 352 C514 388 532 418 558 402');
  animation: routeMove 6.2s 1.8s linear infinite;
}

@keyframes routeMove {
  0% {
    offset-distance: 0%;
    opacity: 0;
  }
  12%,
  82% {
    opacity: 1;
  }
  100% {
    offset-distance: 100%;
    opacity: 0;
  }
}

.selected-card {
  position: absolute;
  left: 28px;
  right: 28px;
  bottom: 24px;
  display: grid;
  grid-template-columns: 100px 210px minmax(0, 1fr) 220px;
  gap: 16px;
  align-items: center;
  padding: 15px 18px;
  border: 1px solid rgba(107, 84, 55, 0.16);
  border-radius: 16px;
  background: rgba(255, 249, 236, 0.88);
  backdrop-filter: blur(12px);
  box-shadow: 0 22px 44px rgba(57, 42, 25, 0.16);
}

.selected-card span {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.selected-card strong {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 500;
}

.selected-card p,
.selected-card em {
  color: rgba(53, 43, 33, 0.68);
  font-size: 12px;
  font-style: normal;
  line-height: 1.65;
}

.story-timeline {
  position: relative;
  display: grid;
  gap: 18px;
  margin-top: 22px;
  padding-left: 22px;
}

.story-timeline::before {
  content: "";
  position: absolute;
  top: 8px;
  bottom: 8px;
  left: 8px;
  border-left: 2px dotted rgba(139, 94, 52, 0.34);
}

.story-timeline article {
  position: relative;
  padding: 0 0 2px 18px;
  cursor: pointer;
}

.story-timeline i {
  position: absolute;
  top: 2px;
  left: -20px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--node-color);
  box-shadow: 0 0 0 6px rgba(255, 249, 236, 0.88), 0 0 18px rgba(118, 196, 214, 0.36);
  animation: breathe 2.4s ease-in-out infinite;
}

.story-timeline article.active i {
  width: 18px;
  height: 18px;
  left: -22px;
}

.story-timeline span {
  color: rgba(104, 88, 70, 0.72);
  font-size: 11px;
}

.story-timeline strong {
  display: block;
  margin-top: 4px;
  color: var(--ink);
  font-size: 15px;
}

.story-timeline article.active strong {
  color: var(--accent);
}

.story-timeline p {
  margin-top: 5px;
  color: rgba(53, 43, 33, 0.66);
  font-size: 12px;
  line-height: 1.58;
}

@keyframes breathe {
  0%,
  100% {
    transform: scale(0.88);
    opacity: 0.78;
  }
  50% {
    transform: scale(1.12);
    opacity: 1;
  }
}

.view-atlas .story-stage {
  min-height: calc(100% - 72px);
  padding: 0;
}

.view-atlas .storymap-canvas {
  position: relative;
  display: block;
  width: 100%;
  min-height: calc(100vh - var(--navbar-h) - 72px);
}

.view-atlas .atlas-map-card {
  position: absolute;
  inset: 0;
  z-index: 1;
  margin: 0;
  padding: 24px;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.view-atlas .large-map-wrap {
  height: calc(100vh - var(--navbar-h) - 166px);
  min-height: 560px;
  border-radius: 0;
}

.view-atlas .atlas-real-map {
  border-radius: 0;
  box-shadow: inset 0 0 180px rgba(0, 0, 0, 0.38);
}

.view-atlas .atlas-real-map :deep(.maplibregl-canvas) {
  filter: saturate(0.72) contrast(1.12) brightness(0.72) hue-rotate(154deg);
}

.view-atlas .atlas-left,
.view-atlas .atlas-right,
.view-atlas .map-metric-strip article,
.view-atlas .selected-card {
  border-color: rgba(255, 249, 236, 0.12);
  background: rgba(12, 18, 22, 0.46);
  color: rgba(255, 249, 236, 0.9);
  backdrop-filter: blur(14px);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.22);
}

.view-atlas .atlas-left {
  position: absolute;
  left: 24px;
  right: 408px;
  bottom: 24px;
  z-index: 8;
  grid-template-columns: minmax(0, 1fr) 168px minmax(260px, 0.8fr);
}

.view-atlas .atlas-right {
  position: absolute;
  top: 104px;
  right: 24px;
  bottom: 24px;
  z-index: 8;
  width: 360px;
  overflow: auto;
}

.view-atlas .atlas-panel h2,
.view-atlas .atlas-panel dd,
.view-atlas .map-heading h1,
.view-atlas .selected-card strong,
.view-atlas .map-metric-strip strong,
.view-atlas .story-timeline strong {
  color: rgba(255, 249, 236, 0.96);
}

.view-atlas .atlas-panel p,
.view-atlas .story-timeline p,
.view-atlas .selected-card p,
.view-atlas .selected-card em {
  color: rgba(255, 249, 236, 0.66);
}

@media (max-width: 1220px) {
  .storymap-canvas {
    grid-template-columns: 1fr;
    grid-template-areas:
      "map"
      "side"
      "detail";
    gap: 18px;
  }

  .atlas-map-card,
  .atlas-left,
  .atlas-right {
    margin: 0;
    padding: 22px;
  }

  .atlas-left {
    grid-template-columns: minmax(0, 1fr) 220px;
    gap: 20px;
  }

  .product-photo {
    margin: 0;
  }
}

@media (max-width: 760px) {
  .studio-toolbar,
  .poster-masthead,
  .poster-footer,
  .selected-card,
  .atlas-left {
    grid-template-columns: 1fr;
  }

.studio-toolbar {
    align-items: stretch;
    padding: 12px 16px;
  }

  .story-stage,
  .poster-stage {
    padding: 18px 14px 32px;
  }

  .poster-card {
    width: 100%;
    min-height: auto;
    aspect-ratio: auto;
    padding: 18px;
  }

  .poster-product-seal {
    grid-template-columns: 88px 1fr;
    justify-items: start;
    text-align: left;
  }

  .poster-product-seal img {
    width: 88px;
    height: 88px;
    grid-row: span 2;
  }

  .poster-masthead h1 {
    font-size: 38px;
  }

  .map-metric-strip {
    grid-template-columns: 1fr;
  }

  .large-map-wrap {
    min-height: 520px;
    height: auto;
  }

  .selected-card {
    position: static;
    margin-top: 14px;
  }

  .large-map {
    height: 420px;
    min-height: 420px;
  }
}

.poster-real-map {
  width: 100%;
  height: 100%;
  min-height: 360px;
  border-radius: 16px;
  overflow: hidden;
  background: #dfe9e3;
  box-shadow: inset 0 0 0 1px rgba(107, 84, 55, 0.12);
}

.view-atlas .studio-toolbar {
  border-bottom-color: rgba(255, 249, 236, 0.12);
  background: rgba(12, 18, 22, 0.66);
  color: rgba(255, 249, 236, 0.92);
}

.view-atlas .toolbar-copy strong,
.view-atlas .toolbar-copy p {
  color: rgba(255, 249, 236, 0.86);
}

.poster-real-map :deep(.maplibregl-canvas) {
  filter: saturate(0.78) contrast(0.92) sepia(0.1);
}

.poster-map-loading,
.archive-map-loading {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: rgba(53, 43, 33, 0.52);
  font-size: 11px;
  background: rgba(247, 239, 225, 0.44);
  border-radius: 14px;
}

.chain-stage {
  min-height: calc(100% - 72px);
  display: grid;
  place-items: start center;
  padding: 30px 24px 54px;
}

.chain-canvas {
  width: min(860px, calc(100vw - 48px));
  display: grid;
  gap: 0;
  border: 0;
  border-radius: 0;
  padding: 42px 48px;
  background: #f8f6f0;
  box-shadow: none;
}

.chain-header {
  text-align: center;
  padding-bottom: 28px;
  border-bottom: 1px solid rgba(107, 84, 55, 0.14);
  margin-bottom: 20px;
}

.chain-header h1 {
  margin-top: 8px;
  font-family: var(--font-serif);
  font-size: 38px;
  font-weight: 500;
}

.chain-header p {
  margin-top: 8px;
  color: rgba(53, 43, 33, 0.62);
  font-size: 13px;
}

.chain-flow {
  position: relative;
  display: grid;
  gap: 18px;
  padding: 14px 0 10px;
}

.chain-flow::before {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1px;
  background: #333333;
}

.chain-step {
  display: grid;
  grid-template-columns: 1fr 42px 1fr;
  gap: 18px;
  align-items: start;
  position: relative;
}

.chain-step-num {
  grid-column: 2;
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--num-color);
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  box-shadow: 0 0 0 6px #f8f6f0;
  flex-shrink: 0;
  justify-self: center;
  margin-top: 14px;
}

.chain-step-card {
  grid-column: 3;
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  align-items: start;
  padding: 8px 0 24px 18px;
  border: 0;
  border-radius: 0;
  background: transparent;
}

.chain-step:nth-child(odd) .chain-step-card {
  grid-column: 1;
  text-align: right;
  padding: 8px 18px 24px 0;
}

.chain-step-icon {
  display: none;
}

.chain-step-icon img {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.chain-step-body span,
.chain-step-type {
  display: block;
  color: var(--accent);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.chain-step-body strong {
  display: block;
  margin-top: 4px;
  color: var(--ink);
  font-size: 16px;
}

.chain-step-body p {
  margin-top: 6px;
  color: rgba(53, 43, 33, 0.7);
  font-size: 12px;
  line-height: 1.6;
}

.chain-step-body em {
  display: block;
  margin-top: 6px;
  color: rgba(53, 43, 33, 0.52);
  font-size: 11px;
  font-style: normal;
}

.chain-arrow {
  display: none;
}

.chain-arrow svg {
  fill: none;
  stroke: rgba(139, 94, 52, 0.42);
}

.chain-footer {
  display: grid;
  gap: 7px;
  margin-top: 24px;
  padding-top: 22px;
  border-top: 1px solid rgba(107, 84, 55, 0.14);
}

.chain-footer span {
  display: block;
  color: rgba(104, 88, 70, 0.74);
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.chain-footer strong {
  display: block;
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 500;
}

.chain-footer p {
  color: rgba(53, 43, 33, 0.62);
  font-size: 12px;
  line-height: 1.6;
}

.archive-stage {
  min-height: calc(100% - 72px);
  display: grid;
  place-items: start center;
  padding: 30px 24px 54px;
}

.archive-canvas {
  width: min(1320px, calc(100vw - 48px));
  min-height: 760px;
  display: grid;
  grid-template-columns: 4fr 6fr;
  grid-template-areas:
    "hero map"
    "abstract map"
    "identity map"
    "cert map"
    "nodes map"
    "footer map";
  gap: 18px 30px;
  border: 0;
  border-radius: 0;
  padding: 36px;
  background: #f5f3ee;
  box-shadow: none;
}

.archive-hero {
  grid-area: hero;
  display: grid;
  grid-template-columns: 130px 1fr;
  gap: 18px;
  align-items: center;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(107, 84, 55, 0.14);
  margin-bottom: 24px;
}

.archive-hero-img {
  width: 160px;
  height: 160px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.9), rgba(111, 139, 99, 0.12));
}

.archive-hero-img img {
  width: 70%;
  height: 70%;
  object-fit: contain;
  filter: drop-shadow(0 18px 18px rgba(64, 43, 24, 0.18));
}

.archive-hero-text h1 {
  font-family: var(--font-serif);
  font-size: 42px;
  font-weight: 500;
}

.archive-species {
  margin-top: 4px;
  color: rgba(107, 84, 55, 0.68);
  font-size: 13px;
  font-style: italic;
}

.archive-hero-text p {
  margin-top: 8px;
  color: rgba(53, 43, 33, 0.68);
  font-size: 12px;
  line-height: 1.7;
}

.archive-grid {
  display: contents;
}

.archive-panel {
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
}

.archive-identity {
  grid-area: identity;
}

.archive-abstract {
  grid-area: abstract;
}

.archive-map {
  grid-area: map;
  min-height: 0;
}

.archive-cert {
  grid-area: cert;
}

.archive-nodes {
  grid-area: nodes;
}

.archive-panel-kicker {
  display: block;
  color: rgba(104, 88, 70, 0.72);
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.archive-panel h3 {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 14px;
}

.archive-identity dl {
  display: grid;
  gap: 12px;
}

.archive-identity dl div {
  padding-top: 10px;
  border-top: 1px solid rgba(107, 84, 55, 0.1);
}

.archive-identity dt {
  color: rgba(104, 88, 70, 0.68);
  font-size: 11px;
}

.archive-identity dd {
  margin-top: 4px;
  color: rgba(36, 29, 23, 0.82);
  font-size: 13px;
  line-height: 1.5;
}

.archive-real-map {
  width: 100%;
  height: 100%;
  min-height: 100%;
  border-radius: 0;
  overflow: hidden;
  background: #eef0ed;
  position: relative;
  box-shadow: inset 0 0 0 1px rgba(107, 84, 55, 0.12);
}

.archive-real-map :deep(.maplibregl-canvas) {
  filter: saturate(0.5) contrast(1.04) brightness(1.04) sepia(0.06);
}

.archive-cert-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.archive-cert-grid article {
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(107, 84, 55, 0.08);
  box-shadow: none;
}

.archive-cert-grid span {
  display: block;
  color: var(--accent);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.archive-cert-grid strong {
  display: block;
  margin-top: 4px;
  color: var(--ink);
  font-size: 13px;
  line-height: 1.4;
}

.archive-cert-grid p {
  display: none;
  margin-top: 3px;
  color: rgba(53, 43, 33, 0.58);
  font-size: 11px;
  line-height: 1.4;
}

.archive-node-list {
  display: grid;
  gap: 10px;
}

.archive-node-list article {
  display: grid;
  grid-template-columns: 36px 1fr;
  gap: 10px;
  align-items: start;
  padding: 10px;
  border-radius: 10px;
  background: rgba(255, 249, 236, 0.44);
}

.archive-node-list article span {
  display: block;
  color: var(--accent);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.archive-node-list article strong {
  display: block;
  margin-top: 2px;
  font-size: 13px;
}

.archive-node-list article p {
  margin-top: 2px;
  color: rgba(53, 43, 33, 0.56);
  font-size: 11px;
}

.archive-node-list svg {
  margin-top: 4px;
}

.archive-footer {
  grid-area: footer;
  display: grid;
  grid-template-columns: 76px 1fr;
  gap: 12px;
  align-items: center;
  padding-top: 18px;
  margin-top: 24px;
  border-top: 1px dashed rgba(107, 84, 55, 0.26);
}

.archive-footer strong {
  display: block;
  margin-top: 4px;
  font-size: 13px;
}

.archive-footer p {
  margin-top: 4px;
  color: rgba(53, 43, 33, 0.54);
  font-size: 11px;
}

/* Final generator art direction: four export modes use different skeletons. */
.product-page.view-brand {
  background:
    radial-gradient(circle at 24% 18%, rgba(197, 178, 145, 0.24), transparent 30%),
    radial-gradient(circle at 80% 82%, rgba(111, 139, 99, 0.16), transparent 30%),
    linear-gradient(180deg, #f8f3ea, #ebe1d1);
}

.product-page.view-chain {
  background:
    linear-gradient(90deg, rgba(22, 63, 91, 0.08) 1px, transparent 1px),
    linear-gradient(180deg, rgba(22, 63, 91, 0.06) 1px, transparent 1px),
    linear-gradient(135deg, #edf5f3, #f8faf5 58%, #e7eef1);
  background-size: 28px 28px, 28px 28px, auto;
}

.product-page.view-archive {
  background:
    radial-gradient(circle at 72% 34%, rgba(129, 145, 137, 0.18), transparent 34%),
    linear-gradient(180deg, #ebe8de, #dcd9cf);
}

.poster-fieldmark {
  position: absolute;
  inset: 22px;
  z-index: 0;
  pointer-events: none;
  display: grid;
  grid-template-columns: repeat(18, 1fr);
  align-items: end;
  opacity: 0.42;
}

.poster-fieldmark span {
  position: absolute;
  right: -68px;
  top: 350px;
  transform: rotate(90deg);
  color: rgba(107, 84, 55, 0.16);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.28em;
}

.poster-fieldmark i {
  height: 12px;
  border-left: 1px solid rgba(107, 84, 55, 0.1);
}

.view-brand .poster-stage {
  background:
    radial-gradient(circle at 22% 18%, rgba(197, 178, 145, 0.24), transparent 28%),
    linear-gradient(180deg, #f7f2e9, #eee6d7);
}

.view-brand .poster-card {
  width: min(750px, calc(100vw - 56px));
  grid-template-rows: auto minmax(310px, 1fr) auto auto auto;
  gap: 14px;
  padding: 44px 48px 32px;
  border: 0;
  border-radius: 0;
  background:
    radial-gradient(circle at 70% 20%, rgba(255, 255, 255, 0.92), transparent 24%),
    linear-gradient(135deg, #fbf7ef 0%, #f0e8d7 100%);
  box-shadow: 0 32px 90px rgba(64, 43, 24, 0.18);
}

.view-brand .poster-card > *:not(.poster-fieldmark) {
  position: relative;
  z-index: 1;
}

.view-brand .poster-card::before,
.view-brand .poster-card::after {
  content: "";
  position: absolute;
  pointer-events: none;
}

.view-brand .poster-card::before {
  inset: 18px;
  border: 1px solid rgba(197, 178, 145, 0.52);
}

.view-brand .poster-card::after {
  width: 380px;
  height: 380px;
  right: -120px;
  bottom: -90px;
  border-radius: 50%;
  border: 1px solid rgba(197, 178, 145, 0.34);
  box-shadow: inset 0 0 0 34px rgba(197, 178, 145, 0.04);
}

.view-brand .poster-masthead {
  grid-template-columns: minmax(0, 1fr) 190px;
  min-height: 182px;
  align-items: start;
}

.view-brand .poster-masthead h1 {
  max-width: 430px;
  margin-top: 10px;
  color: #241d17;
  font-size: clamp(64px, 7vw, 94px);
  letter-spacing: 0.04em;
}

.view-brand .poster-subline {
  max-width: 420px;
  color: rgba(53, 43, 33, 0.56);
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.view-brand .poster-product-seal {
  align-self: start;
  transform: translate(10px, -20px);
}

.view-brand .poster-product-seal img {
  width: 184px;
  height: 184px;
  filter: drop-shadow(0 30px 34px rgba(76, 50, 28, 0.2));
}

.view-brand .poster-product-seal strong {
  font-size: 18px;
}

.view-brand .poster-product-seal span {
  max-width: 142px;
  color: rgba(53, 43, 33, 0.52);
  font-size: 10px;
}

.view-brand .poster-map-anchor {
  width: 316px;
  height: 316px;
  margin-top: -2px;
  border-color: #c5b291;
  box-shadow:
    0 0 0 13px rgba(197, 178, 145, 0.08),
    0 28px 60px rgba(70, 50, 28, 0.14);
}

.view-brand .poster-real-map {
  min-height: 100%;
  border-radius: 50%;
}

.poster-map-ring {
  position: absolute;
  inset: -18px;
  z-index: 3;
  pointer-events: none;
  border: 1px dashed rgba(197, 178, 145, 0.72);
  border-radius: 50%;
}

.view-brand .poster-map-glass {
  left: 46px;
  right: 46px;
  bottom: 30px;
  padding: 11px 13px;
  border-radius: 0;
  background: rgba(255, 249, 236, 0.84);
}

.view-brand .poster-map-glass strong {
  font-size: 17px;
}

.view-brand .poster-route-tags {
  top: 22px;
}

.view-brand .poster-route-tags span {
  min-height: 22px;
  border-color: rgba(255, 249, 236, 0.62);
  background: var(--node-color);
  color: #fff9ec;
  box-shadow: none;
}

.poster-axis {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0;
  margin-top: 2px;
  border-top: 1px dotted rgba(107, 84, 55, 0.36);
  border-bottom: 1px dotted rgba(107, 84, 55, 0.22);
}

.poster-axis span {
  display: grid;
  justify-items: center;
  gap: 6px;
  padding: 10px 4px 9px;
  color: rgba(53, 43, 33, 0.68);
  font-size: 11px;
  font-weight: 800;
}

.poster-axis i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--node-color);
  box-shadow: 0 0 0 4px rgba(197, 178, 145, 0.14);
}

.view-brand .poster-proof-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
  margin-top: 0;
  border-bottom: 1px dotted rgba(107, 84, 55, 0.2);
}

.view-brand .poster-proof-grid article {
  min-height: 74px;
  padding: 12px 10px;
  border-top: 0;
  border-right: 1px solid rgba(107, 84, 55, 0.1);
}

.view-brand .poster-proof-grid article:last-child {
  border-right: 0;
}

.view-brand .poster-proof-grid strong {
  color: #2c2924;
  font-size: 12px;
  line-height: 1.42;
}

.view-brand .poster-footer {
  grid-template-columns: 64px 1fr;
  padding-top: 12px;
  border-top: 0;
}

.view-brand .qr-code {
  width: 58px;
  height: 58px;
  border-radius: 0;
  background: transparent;
}

.view-brand .poster-footer p {
  color: rgba(53, 43, 33, 0.52);
}

.view-atlas .story-stage {
  padding: 0;
}

.view-atlas .storymap-canvas {
  min-height: calc(100vh - var(--navbar-h) - 72px);
  overflow: hidden;
}

.view-atlas .atlas-map-card {
  overflow: hidden;
  padding: 0;
}

.view-atlas .map-heading {
  position: absolute;
  top: 24px;
  left: 28px;
  right: 28px;
  z-index: 12;
  align-items: center;
  margin: 0;
  pointer-events: none;
}

.view-atlas .map-heading > * {
  pointer-events: auto;
}

.view-atlas .map-heading h1 {
  max-width: 560px;
  color: rgba(255, 249, 236, 0.96);
  text-shadow: 0 18px 42px rgba(0, 0, 0, 0.32);
}

.atlas-index-stamp {
  width: 72px;
  height: 72px;
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 3px;
  margin-left: auto;
  border: 1px solid rgba(255, 249, 236, 0.24);
  border-radius: 50%;
  color: rgba(255, 249, 236, 0.9);
  background: rgba(12, 18, 22, 0.36);
  backdrop-filter: blur(14px);
}

.atlas-index-stamp span {
  font-family: var(--font-serif);
  font-size: 28px;
  line-height: 0.9;
}

.atlas-index-stamp small {
  font-size: 9px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.view-atlas .map-heading button {
  border-color: rgba(255, 249, 236, 0.24);
  background: rgba(255, 249, 236, 0.88);
  color: #10191d;
}

.view-atlas .map-metric-strip {
  position: absolute;
  top: 132px;
  left: 28px;
  z-index: 12;
  width: 330px;
  grid-template-columns: 1fr;
  margin: 0;
}

.view-atlas .map-metric-strip article {
  border-color: rgba(255, 249, 236, 0.16);
  border-radius: 0;
  background: rgba(12, 18, 22, 0.48);
  color: rgba(255, 249, 236, 0.92);
  backdrop-filter: blur(14px);
}

.view-atlas .large-map-wrap {
  height: calc(100vh - var(--navbar-h) - 72px);
  min-height: 640px;
}

.view-atlas .atlas-real-map {
  box-shadow:
    inset 0 0 220px rgba(0, 0, 0, 0.44),
    inset 0 0 0 1px rgba(255, 255, 255, 0.04);
}

.view-atlas .real-map-label {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 0;
  background: rgba(12, 18, 22, 0.58);
  color: rgba(255, 249, 236, 0.9);
}

.view-atlas .real-map-label.selected {
  background: rgba(255, 249, 236, 0.9);
}

.view-atlas .atlas-left {
  left: 28px;
  right: auto;
  bottom: 26px;
  width: 520px;
  grid-template-columns: minmax(0, 1fr) 148px;
  align-items: center;
  border-radius: 0;
}

.view-atlas .atlas-left .product-photo {
  grid-column: 2;
  grid-row: 1 / span 3;
  height: 138px;
  border-radius: 50%;
  background: rgba(255, 249, 236, 0.12);
}

.view-atlas .atlas-left dl {
  grid-column: 1 / -1;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 8px;
}

.view-atlas .atlas-right {
  top: 132px;
  right: 28px;
  bottom: 26px;
  width: 348px;
  border-radius: 0;
}

.view-atlas .story-timeline {
  gap: 14px;
}

.view-atlas .story-timeline p,
.view-atlas .selected-card p {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.view-atlas .selected-card {
  left: 576px;
  right: 400px;
  bottom: 26px;
  grid-template-columns: 86px minmax(180px, 0.45fr) minmax(0, 1fr);
  border-radius: 0;
}

.view-atlas .selected-card em {
  display: none;
}

.chain-ruler {
  position: absolute;
  inset: 28px auto 28px 28px;
  width: 28px;
  display: grid;
  grid-template-rows: repeat(28, 1fr);
  opacity: 0.62;
}

.chain-ruler span {
  border-top: 1px solid rgba(20, 58, 84, 0.24);
}

.chain-ruler span:nth-child(4n) {
  width: 28px;
  border-top-color: rgba(20, 58, 84, 0.5);
}

.view-chain .chain-stage {
  place-items: start center;
  background:
    linear-gradient(90deg, rgba(31, 66, 92, 0.06) 1px, transparent 1px),
    linear-gradient(180deg, rgba(31, 66, 92, 0.05) 1px, transparent 1px),
    #f3f7f5;
  background-size: 28px 28px;
}

.view-chain .chain-canvas {
  position: relative;
  width: min(940px, calc(100vw - 48px));
  min-height: 1180px;
  padding: 56px 74px 44px 92px;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(31, 66, 92, 0.08) 1px, transparent 1px),
    linear-gradient(180deg, rgba(31, 66, 92, 0.06) 1px, transparent 1px),
    radial-gradient(circle at 78% 16%, rgba(63, 133, 158, 0.13), transparent 26%),
    #fbfcf6;
  background-size: 28px 28px, 28px 28px, auto, auto;
  color: #17384d;
}

.view-chain .chain-canvas::after {
  content: "";
  position: absolute;
  right: -130px;
  top: 180px;
  width: 360px;
  height: 360px;
  border: 1px solid rgba(31, 66, 92, 0.12);
  border-radius: 50%;
  box-shadow: inset 0 0 0 40px rgba(31, 66, 92, 0.035);
}

.view-chain .chain-header {
  position: relative;
  z-index: 1;
  text-align: left;
  padding-bottom: 26px;
  border-bottom: 2px solid rgba(31, 66, 92, 0.22);
}

.view-chain .chain-header h1 {
  max-width: 620px;
  color: #12354d;
  font-size: 44px;
}

.view-chain .chain-header p {
  color: rgba(23, 56, 77, 0.68);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.chain-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.chain-meta-row b {
  padding: 6px 10px;
  border: 1px solid rgba(31, 66, 92, 0.22);
  color: #17384d;
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.view-chain .chain-flow {
  z-index: 1;
  gap: 8px;
  padding: 34px 0 20px;
}

.view-chain .chain-flow::before {
  top: 22px;
  bottom: 22px;
  width: 1px;
  background: rgba(20, 58, 84, 0.82);
  box-shadow: 0 0 0 8px rgba(31, 66, 92, 0.04);
}

.view-chain .chain-step {
  min-height: 138px;
}

.view-chain .chain-step-num {
  width: 24px;
  height: 24px;
  margin-top: 18px;
  border: 2px solid #fbfcf6;
  background: #143a54;
  color: #fbfcf6;
  box-shadow: 0 0 0 7px #fbfcf6, 0 0 0 8px rgba(20, 58, 84, 0.5);
}

.view-chain .chain-step-card {
  width: min(330px, 100%);
  padding: 6px 0 26px 22px;
  background: transparent;
}

.view-chain .chain-step:nth-child(odd) .chain-step-card {
  justify-self: end;
  padding: 6px 22px 26px 0;
}

.view-chain .chain-step-body strong {
  color: #102f45;
  font-size: 17px;
  line-height: 1.42;
}

.chain-step-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 9px;
}

.chain-step:nth-child(odd) .chain-step-tags {
  justify-content: flex-end;
}

.chain-step-tags b {
  display: inline-flex;
  padding: 5px 8px;
  border: 1px solid rgba(31, 66, 92, 0.16);
  background: rgba(31, 66, 92, 0.06);
  color: #1f425c;
  font-size: 10px;
  line-height: 1;
}

.view-chain .chain-step-body p {
  color: rgba(23, 56, 77, 0.62);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.view-chain .chain-footer {
  position: relative;
  z-index: 1;
  margin-top: 26px;
  border-top: 2px solid rgba(31, 66, 92, 0.22);
}

.chain-signal-bar {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  height: 7px;
  margin-bottom: 16px;
}

.chain-signal-bar i {
  background: var(--node-color);
}

.view-archive .archive-stage {
  background: #ebe9e2;
}

.view-archive .archive-canvas {
  width: min(1380px, calc(100vw - 48px));
  min-height: 820px;
  grid-template-columns: minmax(360px, 4fr) minmax(0, 6fr);
  gap: 18px 34px;
  padding: 42px 48px;
  background:
    radial-gradient(circle at 75% 42%, rgba(211, 216, 211, 0.48), transparent 30%),
    linear-gradient(90deg, rgba(107, 84, 55, 0.045) 1px, transparent 1px),
    #f4f2ed;
  background-size: auto, 34px 34px, auto;
}

.view-archive .archive-hero {
  grid-template-columns: 120px 1fr;
  gap: 20px;
  padding-bottom: 18px;
  margin-bottom: 8px;
}

.view-archive .archive-hero-img {
  width: 120px;
  height: 120px;
  border: 1px solid rgba(107, 84, 55, 0.18);
  background:
    radial-gradient(circle, rgba(255, 255, 255, 0.88), rgba(129, 145, 137, 0.14));
}

.view-archive .archive-hero-text h1 {
  font-size: 48px;
  line-height: 1;
}

.view-archive .archive-hero-text p:not(.archive-species),
.archive-abstract p {
  color: rgba(53, 43, 33, 0.62);
  font-size: 12px;
  line-height: 1.7;
}

.archive-capsule-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.archive-capsule-cloud span,
.view-archive .archive-cert-grid article {
  display: inline-flex;
  align-items: baseline;
  gap: 5px;
  min-height: 30px;
  padding: 7px 10px;
  border: 0;
  border-radius: 999px;
  background: rgba(107, 84, 55, 0.08);
  color: rgba(36, 29, 23, 0.76);
  font-size: 12px;
  box-shadow: none;
}

.archive-capsule-cloud b {
  color: rgba(104, 88, 70, 0.72);
  font-size: 10px;
  letter-spacing: 0.08em;
}

.view-archive .archive-cert-grid strong {
  margin-top: 0;
  font-size: 12px;
}

.view-archive .archive-cert-grid span {
  display: none;
}

.view-archive .archive-map {
  position: relative;
  min-height: 100%;
}

.view-archive .archive-map h3,
.view-archive .archive-map .archive-panel-kicker {
  position: absolute;
  left: 24px;
  z-index: 4;
  color: rgba(36, 29, 23, 0.74);
}

.view-archive .archive-map .archive-panel-kicker {
  top: 22px;
}

.view-archive .archive-map h3 {
  top: 48px;
  font-size: 34px;
}

.view-archive .archive-real-map {
  min-height: 760px;
  border: 1px solid rgba(107, 84, 55, 0.12);
  background: #eef0ed;
  box-shadow:
    inset 0 0 130px rgba(72, 80, 74, 0.12),
    0 24px 70px rgba(72, 60, 44, 0.12);
}

.archive-map-caption {
  position: absolute;
  left: 24px;
  right: 24px;
  bottom: 24px;
  z-index: 4;
  display: grid;
  grid-template-columns: 120px 180px 1fr;
  gap: 14px;
  align-items: center;
  padding: 13px 16px;
  background: rgba(244, 242, 237, 0.84);
  backdrop-filter: blur(12px);
}

.archive-map-caption span {
  color: rgba(104, 88, 70, 0.72);
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.archive-map-caption strong {
  font-family: var(--font-serif);
  font-size: 22px;
  font-weight: 500;
}

.archive-map-caption p {
  color: rgba(53, 43, 33, 0.58);
  font-size: 12px;
}

.view-archive .archive-node-list {
  grid-template-columns: 1fr;
  gap: 6px;
}

.view-archive .archive-node-list article {
  grid-template-columns: 24px 1fr;
  padding: 8px 0;
  background: transparent;
  border-top: 1px solid rgba(107, 84, 55, 0.1);
}

.view-archive .archive-node-list article p {
  display: none;
}

@media print {
  .product-page {
    position: static;
    overflow: visible;
  }

  .studio-toolbar {
    display: none;
  }
}
</style>
