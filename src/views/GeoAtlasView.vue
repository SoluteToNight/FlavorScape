<template>
  <BrandDisplayExperience
    v-if="studioDisplayData"
    :display-data="studioDisplayData"
    :route-data="studioRouteData"
    :route-options="routeOptions"
    fullscreen
    @select-event="selectStudioDisplayEvent"
    @select-route="selectStudioDisplayRoute"
  />

  <main v-else class="exhibition-screen fixed top-navbar inset-x-0 bottom-0 overflow-hidden">
    <!-- 顶部隐形 HUD 控制栏 -->
    <header class="hud-top-bar absolute top-0 inset-x-0 z-50 px-10 py-6 flex justify-between items-start">
      <div>
        <span class="hud-kicker text-[10px] font-sans font-semibold tracking-[0.18em] uppercase">FLAVORSCAPE GEO-ATLAS</span>
        <h1 class="font-serif text-3xl font-medium mt-1 mb-0 tracking-[0.08em]">风味空间叙事 · 智慧大屏</h1>
      </div>

      <div class="flex gap-6 items-center pointer-events-auto">
        <div class="product-tabs flex bg-[rgba(255,255,255,0.05)] rounded-[30px] p-1 border border-[rgba(255,255,255,0.1)]">
          <button
            v-for="item in products" :key="item.id"
            class="flex items-center gap-2 bg-transparent border-none text-[#888] py-1.5 pr-4 pl-2 rounded-[24px] cursor-pointer transition-all duration-300"
            :class="{ active: activeProductId === item.id }"
            @click="switchProduct(item.id)"
          >
            <img :src="item.image" alt="" class="w-6 h-6 rounded-full opacity-50" :class="{ 'opacity-100': activeProductId === item.id }" />
            <span>{{ item.name }}</span>
          </button>
        </div>

        <button class="tour-btn flex items-center gap-2 bg-transparent text-white border border-[rgba(255,255,255,0.3)] py-2.5 px-5 rounded-[30px] text-xs cursor-pointer transition-all duration-300" :class="{ playing: isTouring }" @click="toggleTour">
          <svg v-if="!isTouring" viewBox="0 0 24 24" fill="currentColor" class="w-[14px] h-[14px]"><path d="M8 5v14l11-7z"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor" class="w-[14px] h-[14px]"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
          {{ isTouring ? '停止巡航' : '开启自动巡航' }}
        </button>
      </div>
    </header>

    <!-- 全屏 3D 地图层 -->
    <section class="absolute inset-0">
      <div ref="atlasMapContainer" class="w-full h-full">
        <div v-if="!mapReady" class="map-loading absolute inset-0 flex flex-col justify-center items-center gap-4 bg-[#04080c] z-10 font-sans text-[13px] font-normal tracking-[0.08em]">
          <span class="loader-ring" />
          初始化空间遥感图层...
        </div>
      </div>

      <!-- 叠加交互层 -->
      <div class="hud-overlay absolute inset-0 pointer-events-none z-20" :class="{ 'is-touring': isTouring }">

        <!-- 左侧：产品信息 HUD -->
        <aside class="hud-panel pointer-events-auto absolute top-[100px] left-10 w-[280px] p-5 bg-[rgba(10,15,20,0.4)] border border-[rgba(255,255,255,0.08)] rounded shadow-[0_20px_40px_rgba(0,0,0,0.5)]">
          <div>
            <h2 class="font-serif text-[24px] font-medium m-0 mb-1 text-[#e6e0d4]">{{ product.name }}</h2>
            <p class="text-[11px] font-sans font-normal m-0 mb-5 pb-4 border-b border-[rgba(255,255,255,0.1)] hud-species">{{ product.species }}</p>
          </div>
          <div class="flex flex-col gap-3">
            <div v-for="item in identityItems" :key="item.label" class="flex flex-col gap-1">
              <span class="text-[9px] font-semibold uppercase tracking-[0.12em] hud-label-dim">{{ item.label }}</span>
              <span class="text-[13px] text-[#ccc]">{{ item.value }}</span>
            </div>
          </div>
        </aside>

        <!-- 右侧：时间线轨道 -->
        <aside class="hud-panel pointer-events-auto absolute top-[100px] right-10 w-[240px] px-5 py-6 bg-[rgba(10,15,20,0.4)] border border-[rgba(255,255,255,0.08)] rounded">
          <div class="timeline-track relative flex flex-col gap-6">
            <div
              v-for="(node, index) in nodes" :key="node.id"
              class="relative flex gap-4 cursor-pointer opacity-40 transition-all duration-400 items-center"
              :class="{
                active: selectedNode.id === node.id,
                passed: currentIndex > index
              }"
              @click="selectMapNode(node.id)"
            >
              <div class="node-icon w-7 h-7 rounded-full border border-[rgba(255,255,255,0.2)] grid place-items-center bg-[#0a0f14] z-[2]" :style="{ '--node-color': node.color }">
                <div class="pulse-ring" />
              </div>
              <div class="flex flex-col">
                <span class="step-num font-sans text-[9px] font-bold tracking-[0.08em]">0{{ index + 1 }}</span>
                <strong class="text-base font-normal tracking-[1px] mt-0.5">{{ node.short }}</strong>
              </div>
            </div>
          </div>
        </aside>

        <!-- 底部：电影字幕 -->
        <footer class="cinematic-subtitle-dock absolute bottom-0 inset-x-0 pointer-events-auto flex justify-center text-center px-10 pt-[60px] pb-10">
          <transition name="fade-slide" mode="out-in">
            <div class="subtitle-content max-w-[800px]" :key="selectedNode.id">
              <div class="flex justify-center gap-4 mb-3 font-sans text-[11px] font-semibold tracking-[0.1em]">
                <span :style="{ color: selectedNode.color }">[ {{ selectedNode.type }} ]</span>
                <span class="node-coord font-[tabular-nums]">{{ formatCoord(selectedNode.coord) }}</span>
              </div>
              <h3 class="subtitle-title font-serif text-[32px] font-medium text-white m-0 mb-4">{{ selectedNode.name }}</h3>
              <p class="text-[15px] text-[#ccc] leading-[1.8] m-0 mb-4">{{ selectedNode.story }}</p>
              <div class="subtitle-evidence inline-block py-1.5 px-4 border border-[rgba(255,255,255,0.15)] rounded text-[11px] bg-[rgba(0,0,0,0.3)]">
                <strong class="text-[#666] font-normal">核心资产验证：</strong>{{ selectedNode.evidence }}
              </div>
            </div>
          </transition>
        </footer>

        <!-- SVG 连线 -->
        <svg class="absolute inset-0 w-full h-full pointer-events-none" aria-hidden="true">
          <path
            v-for="route in projectedRoutePaths" :key="route.id" :d="route.d"
            class="projected-route-line"
          />
        </svg>

        <!-- 节点标定 -->
        <div
          v-for="node in projectedNodes" :key="`${node.id}-target`"
          class="map-target-reticle absolute -translate-x-1/2 -translate-y-1/2 pointer-events-auto cursor-pointer flex justify-center items-center w-[60px] h-[60px]"
          :class="{ active: selectedNode.id === node.id }"
          :style="{ left: `${node.x}px`, top: `${node.y}px`, '--node-color': node.color }"
          @click="selectMapNode(node.id)"
        >
          <div class="radar-ping" />
          <div class="core-dot w-2 h-2 rounded-full transition-all duration-300" />
          <div v-if="selectedNode.id === node.id" class="target-label absolute -top-[25px] whitespace-nowrap text-[11px] text-white bg-[rgba(0,0,0,0.6)] py-1 px-2 border border-[rgba(255,255,255,0.2)] rounded-sm pointer-events-none">
            {{ node.short }}
          </div>
        </div>

      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { createMap, removeMap } from '../map/maplibre.js'
import { createHypRasterStyle } from '../map/mapStyle.js'
import BrandDisplayExperience from '../components/BrandDisplayExperience.vue'
import { useSpreadRoutes } from '../composables/useSpreadRoutes'
import { useStudioStore } from '../stores/studio'

const vueRoute = useRoute()
const studioStore = useStudioStore()
const { routeOptions, loadRoutes, loadRoute, getRoute } = useSpreadRoutes()

const studioProjectId = computed(() => {
  const value = vueRoute.query.project
  return typeof value === 'string' ? value : ''
})
const studioDisplayData = computed(() => {
  const id = studioProjectId.value
  const project = studioStore.activeProject
  if (!id || project?.id !== id || project.outputType !== 'display' || project.outputs?.display?.contentConfirmed !== true) return null
  return studioStore.mergedDisplayData
})
const studioRouteData = computed(() => getRoute(studioDisplayData.value?.selectedRouteId))

async function applyStudioProject() {
  const id = studioProjectId.value
  if (!id || !studioStore.projects.some(project => project.id === id)) return
  studioStore.switchProject(id)
  await loadRoutes()
  const routeId = studioStore.mergedDisplayData?.selectedRouteId
  if (routeId) await loadRoute(routeId)
}

function selectStudioDisplayEvent(key) {
  studioStore.updateOutputField('display', 'selectedEventKey', key)
}

async function selectStudioDisplayRoute(id) {
  studioStore.updateOutputField('display', 'selectedRouteId', id)
  studioStore.updateOutputField('display', 'selectedEventKey', null)
  await loadRoute(id)
}

const products = [
  { id: 'pepper', name: '汉源花椒', image: '/ingredients/pepper-realistic.png', species: '花椒 Zanthoxylum bungeanum' },
  { id: 'rice', name: '五常大米', image: '/ingredients/rice-realistic.png', species: '稻米 Oryza sativa' }
]
const pepperIdentity = [
  { label: '核心产区', value: '四川雅安汉源 · 大渡河干热河谷' },
  { label: '气候微相', value: '海拔1600m，极端昼夜温差促油胞浓缩' },
  { label: '空间凭证', value: '国家地理标志保护产品' }
]
const riceIdentity = [
  { label: '核心产区', value: '黑龙江哈尔滨五常 · 拉林河流域' },
  { label: '土壤水文', value: '寒地黑土，昼夜温差大，生长期长' },
  { label: '空间凭证', value: '五常大米地理标志保护产品' }
]
const pepperStages = [
  { id: 'origin', coord: [102.6342, 29.5621], short: '源起产地', type: '核心产区', name: '大渡河干热河谷贡椒区', color: '#8b9a76', story: '独享大渡河干热河谷微气候，海拔1600米坡地。极端昼夜温差促使植物油胞浓缩，红油饱满，是流传千年的正路贡椒原产地。', evidence: '国家地理标志保护产品' },
  { id: 'process', coord: [102.6511, 29.3512], short: '精炼加工', type: '加工节点', name: '智能化分级初加工中心', color: '#c7925e', story: '伏天清晨手工采摘以保护果皮油包，经过智能化筛分与低温太阳能模拟曝晒，自然开裂脱籽，锁住山地麻香。', evidence: '非遗工艺 · 低温曝晒' },
  { id: 'storage', coord: [104.1623, 30.8241], short: '气调仓储', type: '冷链仓储', name: '西南冷链气调仓储枢纽', color: '#6896aa', story: '采用高阻隔充氮真空包装，全程0-4℃恒温冷链锁鲜，隔绝光照与氧气，减少挥发油流失。', evidence: '0-4℃恒温 · 充氮真空' },
  { id: 'market', coord: [121.3821, 31.1123], short: '终端直达', type: '主销市场', name: '长三角精品调味品渠道枢纽', color: '#9782bb', story: '辐射华东的主销区枢纽。每一批次绑定数字化追溯二维码，进入精品零售及有机商超。', evidence: '一物一码 · 批次可溯' },
  { id: 'dining', coord: [106.5512, 29.5631], short: '美学餐桌', type: '餐饮应用', name: '经典川味与重度麻辣体验空间', color: '#bc5b5a', story: '在沸腾的牛油火锅中，高纯度羟基山椒素瞬间爆发，完成从高山河谷到城市餐桌的空间证据闭环。', evidence: '川菜24味型麻味基底' }
]
const riceStages = [
  { id: 'origin', coord: [127.1676, 44.9192], short: '源起产地', type: '核心产区', name: '拉林河流域核心稻作区', color: '#8b9a76', story: '依托洁净水源与寒地黑土。昼夜温差促使稻米中干物质与游离双糖持续积累，形成清晰稻花香。', evidence: '寒地黑土 · 积温2700℃' },
  { id: 'process', coord: [127.0679, 44.9322], short: '精密碾磨', type: '加工节点', name: '智能化精密碾磨中心', color: '#c7925e', story: '低温烘干与光学粒选，控制水分与抛光度。轻度碾磨保留米粒天然芳香成分。', evidence: '碎米率<5% · 轻度留胚' },
  { id: 'storage', coord: [126.6331, 45.7422], short: '气调保鲜', type: '冷链仓储', name: '绿色充氮稻谷保鲜库', color: '#6896aa', story: '原粮带壳仓储，全程维持低温与高纯度充氮环境，抑制大米呼吸作用与脂肪酸劣变。', evidence: '15℃恒温 · 锁鲜365天' },
  { id: 'market', coord: [121.3821, 31.1123], short: '终端直达', type: '主销市场', name: '华东地理标志风物枢纽', color: '#9782bb', story: '辐射长三角。每袋出库绑定溯源二维码，直供有机商超和高端膳食渠道。', evidence: '全链路监控数据' },
  { id: 'dining', coord: [121.4737, 31.2304], short: '美学餐桌', type: '餐饮应用', name: '东方米食高端膳食体验', color: '#bc5b5a', story: '进入现代膳食空间，淀粉与蛋白质比例在烹调中形成稳定口感。饭粒油亮、香气外溢。', evidence: '食味值>85分' }
]

const routePairs = [['origin', 'process'], ['process', 'storage'], ['storage', 'market'], ['storage', 'dining']]

const activeProductId = ref('pepper')
const selectedNodeId = ref('origin')
const isTouring = ref(false)
const mapReady = ref(false)
const atlasMapContainer = ref(null)
const projectedNodes = ref([])
const projectedRoutePaths = ref([])
let atlasMap = null
let tourInterval = null

const product = computed(() => products.find(p => p.id === activeProductId.value))
const identityItems = computed(() => activeProductId.value === 'rice' ? riceIdentity : pepperIdentity)
const nodes = computed(() => activeProductId.value === 'rice' ? riceStages : pepperStages)
const selectedNode = computed(() => nodes.value.find(n => n.id === selectedNodeId.value) || nodes.value[0])
const currentIndex = computed(() => nodes.value.findIndex(n => n.id === selectedNodeId.value))

function formatCoord(coord) { return `${Math.abs(coord[1]).toFixed(4)}°N, ${Math.abs(coord[0]).toFixed(4)}°E` }

const MAP_STYLE = createHypRasterStyle({
  backgroundLayerId: 'trace-bg',
  backgroundColor: '#060B10',
  rasterPaint: {
    'raster-saturation': -0.8,
    'raster-contrast': 0.3,
    'raster-brightness-min': 0.1,
    'raster-opacity': 0.8,
  },
})

async function initAtlasMap() {
  if (atlasMap || !atlasMapContainer.value) return
  atlasMap = createMap({
    container: atlasMapContainer.value,
    style: MAP_STYLE,
    center: [106.6, 30.4],
    zoom: 4.8, pitch: 55, bearing: -15,
    antialias: true, attributionControl: false
  })
  atlasMap.on('load', () => { mapReady.value = true; updateProjectedNodes() })
  atlasMap.on('move', updateProjectedNodes)
  atlasMap.on('resize', updateProjectedNodes)
}

function selectMapNode(id, options = {}) {
  if(isTouring.value && id !== selectedNodeId.value && !options.fromTour) stopTour()
  selectedNodeId.value = id
  const node = nodes.value.find(n => n.id === id)
  if (!node || !atlasMap) return
  atlasMap.flyTo({
    center: node.coord,
    zoom: id === 'market' || id === 'dining' ? 5.2 : 6.8,
    pitch: 65,
    bearing: (Math.random() - 0.5) * 40,
    duration: 3500,
    essential: true,
    curve: 1.2
  })
}

function buildCurve(start, end, bend = 0.2) {
  const [x1, y1] = start, [x2, y2] = end
  const cx = (x1 + x2) / 2 - (y2 - y1) * bend
  const cy = (y1 + y2) / 2 + (x2 - x1) * bend * 0.5
  return Array.from({ length: 30 }, (_, i) => {
    const t = i / 29, mt = 1 - t
    return [ mt*mt*x1 + 2*mt*t*cx + t*t*x2, mt*mt*y1 + 2*mt*t*cy + t*t*y2 ]
  })
}

function updateProjectedNodes() {
  if (!atlasMap) return
  projectedNodes.value = nodes.value.map(node => {
    const pt = atlasMap.project(node.coord)
    return { ...node, x: pt.x, y: pt.y }
  })
  projectedRoutePaths.value = routePairs.map(([fromId, toId], idx) => {
    const from = nodes.value.find(n => n.id === fromId), to = nodes.value.find(n => n.id === toId)
    const pts = buildCurve(from.coord, to.coord, idx === 3 ? -0.15 : 0.2).map(c => atlasMap.project(c))
    const d = pts.map((p, i) => `${i===0?'M':'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
    return { id: `route-${idx}`, d }
  })
}

function toggleTour() {
  if (isTouring.value) stopTour(); else startTour()
}

function startTour() {
  isTouring.value = true
  let nextIdx = (currentIndex.value + 1) % nodes.value.length
  selectMapNode(nodes.value[nextIdx].id, { fromTour: true })
  tourInterval = setInterval(() => {
    nextIdx = (currentIndex.value + 1) % nodes.value.length
    selectMapNode(nodes.value[nextIdx].id, { fromTour: true })
  }, 7000)
}

function stopTour() { isTouring.value = false; clearInterval(tourInterval) }

function switchProduct(id) { activeProductId.value = id; stopTour(); selectedNodeId.value = 'origin'; setTimeout(() => selectMapNode('origin'), 100) }

onMounted(async () => {
  await applyStudioProject()
  if (!studioDisplayData.value) nextTick(initAtlasMap)
})
watch(studioProjectId, async () => {
  await applyStudioProject()
  if (!studioDisplayData.value && !atlasMap) nextTick(initAtlasMap)
})
onUnmounted(() => { stopTour(); removeMap(atlasMap) })
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════
   KEPT — Tailwind cannot express these:
   dark cinematic theme colors (not in design system),
   linear-gradient overlays, backdrop-filter,
   pseudo-elements, dynamic --node-color theming,
   @keyframes animations, SVG presentation attributes,
   Vue transitions, responsive media queries
   ═══════════════════════════════════════════════════════════════ */

/* KEPT: dark cinematic background — specific colors outside design system */
.exhibition-screen {
  background: #04080c;
  color: #fff;
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  text-rendering: geometricPrecision;
}

/* KEPT: gradient overlay + pointer-events cascade */
.hud-top-bar {
  background: linear-gradient(180deg, rgba(4,8,12,0.9) 0%, rgba(4,8,12,0) 100%);
  pointer-events: none;
}

/* KEPT: dark theme — specific semi-transparent gold accent */
.hud-kicker { color: rgba(224, 195, 145, 0.86); }

/* KEPT: dark theme — specific semi-transparent HUD text */
.hud-species { color: rgba(230, 224, 212, 0.48); }
.hud-label-dim { color: rgba(230, 224, 212, 0.42); }

/* KEPT: product tabs — backdrop-filter + dark semi-transparent bg */
.product-tabs { backdrop-filter: blur(10px); }
.product-tabs button.active { background: rgba(255,255,255,0.1); color: #fff; }

/* KEPT: tour button — backdrop-filter + dark glow effects */
.tour-btn { backdrop-filter: blur(10px); }
.tour-btn:hover { background: rgba(255,255,255,0.1); }
.tour-btn.playing { border-color: #a18a66; color: #a18a66; box-shadow: 0 0 15px rgba(161,138,102,0.3); }

/* KEPT: map loading — dark theme specific color */
.map-loading { color: rgba(230, 224, 212, 0.72); }

/* KEPT: loader ring — dark theme + spin animation */
.loader-ring { width: 40px; height: 40px; border: 2px solid rgba(255,255,255,0.1); border-top-color: #a18a66; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* KEPT: touring state — panel dimming */
.hud-overlay.is-touring .hud-panel { opacity: 0.6; }

/* KEPT: HUD panel — backdrop-filter + dark semi-transparent bg */
.hud-panel { backdrop-filter: blur(16px); transition: opacity 0.5s; }

/* KEPT: product HUD — dark border-left accent */
.product-hud { border-left: 3px solid #a18a66; }

/* KEPT: timeline HUD — dark border-right accent */
.timeline-hud { border-right: 3px solid #a18a66; }

/* KEPT: timeline track — pseudo-element vertical line */
.timeline-track::before {
  content: ''; position: absolute; top: 10px; bottom: 10px; left: 13px;
  width: 1px; background: rgba(255,255,255,0.1);
}

/* KEPT: timeline node active state — dynamic --node-color + glow */
.timeline-node.active { transform: translateX(-5px); }
.timeline-node.active .node-icon {
  border-color: var(--node-color);
  box-shadow: 0 0 15px var(--node-color);
  background: var(--node-color);
}
.timeline-node.active .pulse-ring { width: 8px; height: 8px; background: #fff; border-radius: 50%; box-shadow: 0 0 10px #fff; }
.timeline-node.active .step-num { color: var(--node-color); }

/* KEPT: step-num — dark theme color outside design system */
.step-num { color: rgba(230, 224, 212, 0.48); font-variant-numeric: tabular-nums; }

/* KEPT: cinematic subtitle dock — multi-stop gradient overlay */
.cinematic-subtitle-dock {
  background: linear-gradient(0deg, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.6) 60%, rgba(0,0,0,0) 100%);
}

/* KEPT: subtitle title — text-shadow for cinematic depth */
.subtitle-title { text-shadow: 0 4px 20px rgba(0,0,0,0.8); }

/* KEPT: subtitle evidence — specific gold color + backdrop-filter */
.subtitle-evidence { color: #a18a66; backdrop-filter: blur(4px); }

/* KEPT: subtitle coord — dark theme specific color */
.node-coord { color: rgba(230, 224, 212, 0.42); }

/* KEPT: Vue transition classes */
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.5s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(15px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-15px); }

/* KEPT: SVG route line — presentation attributes */
.projected-route-line { fill: none; stroke: rgba(255,255,255,0.15); stroke-width: 1.5; stroke-dasharray: 4 4; }

/* KEPT: map target reticle — dark theme specific colors + dynamic var */
.core-dot { background: rgba(255,255,255,0.6); }
.map-target-reticle:hover .core-dot { background: #fff; transform: scale(1.5); }
.map-target-reticle.active .core-dot { background: var(--node-color); box-shadow: 0 0 20px var(--node-color); transform: scale(1.2); }

/* KEPT: target label — backdrop-filter */
.target-label { backdrop-filter: blur(4px); }

/* KEPT: radar ping — animation + dynamic --node-color */
.radar-ping { position: absolute; width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--node-color); opacity: 0; }
.map-target-reticle.active .radar-ping { animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite; }
@keyframes ping {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(6); opacity: 0; }
}

/* KEPT: responsive — hide HUD panels on mobile */
@media (max-width: 900px) {
  .hud-top-bar { flex-direction: column; gap: 16px; padding: 16px; }
  .product-hud, .timeline-hud { display: none; }
  .cinematic-subtitle-dock { padding: 40px 20px 20px; }
  .subtitle-title { font-size: 24px; }
}
</style>
