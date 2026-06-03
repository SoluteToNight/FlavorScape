<template>
  <main class="exhibition-screen">
    <!-- 顶部隐形栏：控制产品切换与播放，融入背景 -->
    <header class="hud-top-bar">
      <div class="brand-identity">
        <span class="hud-kicker">FLAVORSCAPE GEO-ATLAS</span>
        <h1>风味空间叙事 · 智慧大屏</h1>
      </div>

      <div class="exhibition-controls">
        <div class="product-tabs">
          <button
            v-for="item in products" :key="item.id"
            :class="{ active: activeProductId === item.id }"
            @click="switchProduct(item.id)"
          >
            <img :src="item.image" alt="" />
            <span>{{ item.name }}</span>
          </button>
        </div>
        
        <!-- 大屏核心互动：自动巡航播放 -->
        <button class="tour-btn" :class="{ playing: isTouring }" @click="toggleTour">
          <svg v-if="!isTouring" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
          {{ isTouring ? '停止巡航' : '开启自动巡航' }}
        </button>
      </div>
    </header>

    <!-- 全屏 3D 地图层 -->
    <section class="cinematic-stage">
      <div ref="atlasMapContainer" class="atlas-real-map">
        <div v-if="!mapReady" class="map-loading">
          <span class="loader-ring"></span>
          初始化空间遥感图层...
        </div>
      </div>

      <!-- 叠加交互层 (指针穿透) -->
      <div class="hud-overlay" :class="{ 'is-touring': isTouring }">
        
        <!-- 左侧：产品基础信息 (HUD 扫描风格) -->
        <aside class="hud-panel product-hud">
          <div class="hud-title-wrap">
            <h2>{{ product.name }}</h2>
            <p>{{ product.species }}</p>
          </div>
          <div class="hud-data-list">
            <div v-for="item in identityItems" :key="item.label" class="hud-data-row">
              <span class="label">{{ item.label }}</span>
              <span class="value">{{ item.value }}</span>
            </div>
          </div>
        </aside>

        <!-- 右侧：时间线轨道 -->
        <aside class="hud-panel timeline-hud">
          <div class="timeline-track">
            <div 
              v-for="(node, index) in nodes" :key="node.id"
              class="timeline-node"
              :class="{ 
                active: selectedNode.id === node.id,
                passed: currentIndex > index 
              }"
              @click="selectMapNode(node.id)"
            >
              <div class="node-icon" :style="{ '--node-color': node.color }">
                <div class="pulse-ring"></div>
              </div>
              <div class="node-info">
                <span class="step-num">0{{ index + 1 }}</span>
                <strong>{{ node.short }}</strong>
              </div>
            </div>
          </div>
        </aside>

        <!-- 底部中央：电影级字幕与叙事 -->
        <footer class="cinematic-subtitle-dock">
          <transition name="fade-slide" mode="out-in">
            <div class="subtitle-content" :key="selectedNode.id">
              <div class="subtitle-meta">
                <span class="node-type" :style="{ color: selectedNode.color }">
                  [ {{ selectedNode.type }} ]
                </span>
                <span class="node-coord">{{ formatCoord(selectedNode.coord) }}</span>
              </div>
              <h3 class="subtitle-title">{{ selectedNode.name }}</h3>
              <p class="subtitle-text">{{ selectedNode.story }}</p>
              <div class="subtitle-evidence">
                <strong>核心资产验证：</strong>{{ selectedNode.evidence }}
              </div>
            </div>
          </transition>
        </footer>

        <!-- SVG 连线与节点标定 (依附于地图之上) -->
        <svg class="projected-svg" aria-hidden="true">
          <path
            v-for="route in projectedRoutePaths" :key="route.id" :d="route.d"
            class="projected-route-line"
          />
        </svg>

        <div
          v-for="node in projectedNodes" :key="`${node.id}-target`"
          class="map-target-reticle"
          :class="{ active: selectedNode.id === node.id }"
          :style="{ left: `${node.x}px`, top: `${node.y}px`, '--node-color': node.color }"
          @click="selectMapNode(node.id)"
        >
          <!-- 雷达波纹动画 -->
          <div class="radar-ping"></div>
          <div class="core-dot"></div>
          <div class="target-label" v-if="selectedNode.id === node.id">
            {{ node.short }}
          </div>
        </div>

      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

// ================= 数据定义 (复用您的数据，精简展示) =================
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

// ================= 状态管理 =================
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

// ================= 地图核心逻辑 (增强 3D 飞行与沉浸感) =================
const MAP_STYLE = {
  version: 8,
  sources: {
    'hyp-tiles': { type: 'raster', tiles: ['/tiles/raster/{z}/{x}/{y}.png'], tileSize: 256, maxzoom: 8 },
  },
  layers: [
    { id: 'trace-bg', type: 'background', paint: { 'background-color': '#060B10' } }, // 深色虚空背景
    {
      id: 'hyp', type: 'raster', source: 'hyp-tiles',
      paint: {
        'raster-saturation': -0.8, // 降低色彩
        'raster-contrast': 0.3,    // 提高对比度
        'raster-brightness-min': 0.1,
        'raster-opacity': 0.8,
      },
    },
  ],
}

async function initAtlasMap() {
  if (atlasMap) return
  atlasMap = new maplibregl.Map({
    container: atlasMapContainer.value,
    style: MAP_STYLE,
    center: [106.6, 30.4],
    zoom: 4.8, pitch: 55, bearing: -15, // 初始化为强烈的 3D 视角
    antialias: true, attributionControl: false
  })

  atlasMap.on('load', () => {
    mapReady.value = true
    updateProjectedNodes()
  })
  atlasMap.on('move', updateProjectedNodes)
  atlasMap.on('resize', updateProjectedNodes)
}

function selectMapNode(id) {
  if(isTouring.value && id !== selectedNodeId.value) stopTour() // 手动点击中断自动播放
  selectedNodeId.value = id
  const node = nodes.value.find(n => n.id === id)
  if (!node || !atlasMap) return

  // 大屏级别的无人机运镜效果 (FlyTo)
  atlasMap.flyTo({
    center: node.coord,
    zoom: id === 'market' || id === 'dining' ? 5.2 : 6.8, // 城市节点拉远，山地节点拉近
    pitch: 65, // 强烈的倾斜角
    bearing: (Math.random() - 0.5) * 40, // 每次飞行带有一点随机旋转角度，增加电影感
    duration: 3500, // 飞行时间延长，显得优雅
    essential: true,
    curve: 1.2
  })
}

// ================= 投影连线逻辑 =================
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

// ================= 自动巡航 (Auto-Tour) 大屏核心功能 =================
function toggleTour() {
  if (isTouring.value) stopTour()
  else startTour()
}

function startTour() {
  isTouring.value = true
  let nextIdx = (currentIndex.value + 1) % nodes.value.length
  selectMapNode(nodes.value[nextIdx].id)
  
  tourInterval = setInterval(() => {
    nextIdx = (currentIndex.value + 1) % nodes.value.length
    selectMapNode(nodes.value[nextIdx].id)
  }, 7000) // 每 7 秒切换一个镜头
}

function stopTour() {
  isTouring.value = false
  clearInterval(tourInterval)
}

function switchProduct(id) {
  activeProductId.value = id
  stopTour()
  selectedNodeId.value = 'origin'
  setTimeout(() => selectMapNode('origin'), 100)
}

onMounted(() => { nextTick(initAtlasMap) })
onUnmounted(() => { stopTour(); atlasMap?.remove() })
</script>

<style scoped>
/* ================= 全局设定 ================= */
.exhibition-screen {
  position: fixed; inset: var(--navbar-h) 0 0 0;
  background: #04080c; color: #fff;
  font-family: -apple-system, "PingFang SC", "Helvetica Neue", sans-serif;
  overflow: hidden;
}

/* ================= 顶部隐形 HUD 控制栏 ================= */
.hud-top-bar {
  position: absolute; top: 0; left: 0; right: 0; z-index: 50;
  padding: 24px 40px; display: flex; justify-content: space-between; align-items: flex-start;
  background: linear-gradient(180deg, rgba(4,8,12,0.9) 0%, rgba(4,8,12,0) 100%);
  pointer-events: none; /* 让空白区域鼠标穿透到底图 */
}

.brand-identity h1 { font-family: "Noto Serif SC", serif; font-size: 22px; font-weight: 400; margin: 4px 0 0; letter-spacing: 2px; }
.hud-kicker { font-size: 10px; font-family: monospace; color: #a18a66; letter-spacing: 0.2em; text-transform: uppercase; }

.exhibition-controls { display: flex; gap: 24px; align-items: center; pointer-events: auto; }
.product-tabs { display: flex; background: rgba(255,255,255,0.05); border-radius: 30px; padding: 4px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); }
.product-tabs button {
  display: flex; align-items: center; gap: 8px; background: transparent; border: none;
  color: #888; padding: 6px 16px 6px 8px; border-radius: 24px; cursor: pointer; transition: 0.3s;
}
.product-tabs button img { width: 24px; height: 24px; border-radius: 50%; opacity: 0.5; }
.product-tabs button.active { background: rgba(255,255,255,0.1); color: #fff; }
.product-tabs button.active img { opacity: 1; }

.tour-btn {
  display: flex; align-items: center; gap: 8px; background: transparent; color: #fff;
  border: 1px solid rgba(255,255,255,0.3); padding: 10px 20px; border-radius: 30px;
  font-size: 12px; cursor: pointer; transition: 0.3s; backdrop-filter: blur(10px);
}
.tour-btn svg { width: 14px; height: 14px; }
.tour-btn:hover { background: rgba(255,255,255,0.1); }
.tour-btn.playing { border-color: #a18a66; color: #a18a66; box-shadow: 0 0 15px rgba(161,138,102,0.3); }

/* ================= 3D 地图画板 ================= */
.cinematic-stage { position: absolute; inset: 0; }
.atlas-real-map { width: 100%; height: 100%; }

.map-loading { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 16px; background: #04080c; z-index: 10; font-family: monospace; color: #666; font-size: 12px; }
.loader-ring { width: 40px; height: 40px; border: 2px solid rgba(255,255,255,0.1); border-top-color: #a18a66; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* ================= HUD 界面叠层 ================= */
.hud-overlay { position: absolute; inset: 0; pointer-events: none; z-index: 20; }
.hud-overlay.is-touring .hud-panel { opacity: 0.6; } /* 巡航时弱化两侧面板 */
.hud-panel { pointer-events: auto; position: absolute; background: rgba(10,15,20,0.4); border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(16px); border-radius: 4px; transition: opacity 0.5s; }

/* 左侧：微型扫描仪面板 */
.product-hud { top: 100px; left: 40px; width: 280px; padding: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); border-left: 3px solid #a18a66; }
.hud-title-wrap h2 { font-family: "Noto Serif SC", serif; font-size: 24px; font-weight: 500; margin: 0 0 4px; color: #e6e0d4; }
.hud-title-wrap p { font-size: 11px; color: #888; font-family: monospace; margin: 0 0 20px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.1); }
.hud-data-list { display: flex; flex-direction: column; gap: 12px; }
.hud-data-row { display: flex; flex-direction: column; gap: 4px; }
.hud-data-row .label { font-size: 9px; color: #666; text-transform: uppercase; letter-spacing: 1px; }
.hud-data-row .value { font-size: 13px; color: #ccc; }

/* 右侧：科幻感时间轴 */
.timeline-hud { top: 100px; right: 40px; width: 240px; padding: 24px 20px; border-right: 3px solid #a18a66; }
.timeline-track { position: relative; display: flex; flex-direction: column; gap: 24px; }
.timeline-track::before { content: ''; position: absolute; top: 10px; bottom: 10px; left: 13px; width: 1px; background: rgba(255,255,255,0.1); }
.timeline-node { position: relative; display: flex; gap: 16px; cursor: pointer; opacity: 0.4; transition: 0.4s; align-items: center;}
.timeline-node.passed { opacity: 0.8; }
.timeline-node.active { opacity: 1; transform: translateX(-5px); }
.node-icon { width: 28px; height: 28px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.2); display: grid; place-items: center; background: #0a0f14; z-index: 2; }
.timeline-node.active .node-icon { border-color: var(--node-color); box-shadow: 0 0 15px var(--node-color); background: var(--node-color); }
.timeline-node.active .pulse-ring { width: 8px; height: 8px; background: #fff; border-radius: 50%; box-shadow: 0 0 10px #fff; }
.node-info { display: flex; flex-direction: column; }
.step-num { font-family: monospace; font-size: 9px; color: #888; }
.timeline-node.active .step-num { color: var(--node-color); }
.node-info strong { font-size: 14px; font-weight: 400; letter-spacing: 1px; margin-top: 2px;}

/* 底部：电影字幕栏 */
.cinematic-subtitle-dock {
  position: absolute; bottom: 0; left: 0; right: 0; pointer-events: auto;
  background: linear-gradient(0deg, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.6) 60%, rgba(0,0,0,0) 100%);
  padding: 60px 40px 40px; display: flex; justify-content: center; text-align: center;
}
.subtitle-content { max-width: 800px; }
.subtitle-meta { display: flex; justify-content: center; gap: 16px; margin-bottom: 12px; font-family: monospace; font-size: 11px; letter-spacing: 1px; }
.node-coord { color: #666; }
.subtitle-title { font-family: "Noto Serif SC", serif; font-size: 32px; font-weight: 500; color: #fff; margin: 0 0 16px; text-shadow: 0 4px 20px rgba(0,0,0,0.8); }
.subtitle-text { font-size: 15px; color: #ccc; line-height: 1.8; margin: 0 0 16px; }
.subtitle-evidence { display: inline-block; padding: 6px 16px; border: 1px solid rgba(255,255,255,0.15); border-radius: 4px; font-size: 11px; color: #a18a66; background: rgba(0,0,0,0.3); backdrop-filter: blur(4px); }
.subtitle-evidence strong { color: #666; font-weight: normal; }

/* 动画过渡 */
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.5s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(15px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-15px); }

/* ================= 目标锁定点 (Target Reticle) & SVG 线条 ================= */
.projected-svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.projected-route-line { fill: none; stroke: rgba(255,255,255,0.15); stroke-width: 1.5; stroke-dasharray: 4 4; }

.map-target-reticle { position: absolute; transform: translate(-50%, -50%); pointer-events: auto; cursor: pointer; display: flex; justify-content: center; align-items: center; width: 60px; height: 60px; }
.core-dot { width: 8px; height: 8px; background: rgba(255,255,255,0.6); border-radius: 50%; transition: 0.3s; }
.map-target-reticle:hover .core-dot { background: #fff; transform: scale(1.5); }
.target-label { position: absolute; top: -25px; white-space: nowrap; font-size: 11px; color: #fff; background: rgba(0,0,0,0.6); padding: 4px 8px; border: 1px solid rgba(255,255,255,0.2); border-radius: 2px; backdrop-filter: blur(4px); pointer-events: none; }

/* 雷达光波动画 (仅选中状态显示) */
.radar-ping { position: absolute; width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--node-color); opacity: 0; }
.map-target-reticle.active .core-dot { background: var(--node-color); box-shadow: 0 0 20px var(--node-color); transform: scale(1.2); }
.map-target-reticle.active .radar-ping { animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite; }

@keyframes ping {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(6); opacity: 0; }
}

/* 响应式降级 */
@media (max-width: 900px) {
  .hud-top-bar { flex-direction: column; gap: 16px; padding: 16px; }
  .product-hud, .timeline-hud { display: none; } /* 小屏幕隐藏两侧仪表盘，保留字幕 */
  .cinematic-subtitle-dock { padding: 40px 20px 20px; }
  .subtitle-title { font-size: 24px; }
}
</style>