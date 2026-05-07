<template>
  <div class="inspector glass-panel" :class="{ collapsed: inspectorCollapsed }">
    <button
      type="button"
      class="inspector-toggle"
      :aria-label="inspectorCollapsed ? '展开详情面板' : '折叠详情面板'"
      :aria-expanded="!inspectorCollapsed"
      @click="inspectorCollapsed = !inspectorCollapsed"
    >
      <span>{{ inspectorCollapsed ? '‹' : '›' }}</span>
    </button>

    <div v-show="!inspectorCollapsed" class="inspector-body">
      <Transition name="panel" mode="out-in">
        <!-- Node panel -->
        <div v-if="selectedNode" key="node" class="panel-content">
        <div class="panel-tab">风味节点</div>
        <div class="panel-title">{{ selectedNode.dish || selectedNode.city }}</div>
        <div class="panel-subtitle">{{ selectedNode.city }} · {{ selectedNode.region }} · {{ selectedNode.eco }}</div>

        <div class="section-label">风味雷达图</div>
        <div class="panel-card">
          <div class="radar-wrap">
            <FlavorRadar :scores="selectedNode.scores" :color="selectedNode.color" :size="148" :animated="true" />
          </div>
        </div>

        <div class="section-label">风味描述</div>
        <div class="panel-card">
          <p class="node-description">
            {{ selectedNode.description }}
          </p>
        </div>

        <div class="section-label" style="margin-top:16px">食材基因</div>
        <div class="panel-card">
          <div class="chips">
            <span
              v-for="ing in selectedNode.ingredients"
              :key="ing"
              class="chip"
              :class="{ active: hoveredIngredient === ing }"
              :style="buildTagStyle(selectedNode.color, hoveredIngredient === ing)"
              @mouseenter="hoveredIngredient = ing"
              @mouseleave="hoveredIngredient = null"
            >
              {{ ing }}
            </span>
          </div>
        </div>

        <template v-if="siblings.length">
          <div class="section-label" style="margin-top:16px">同族成品 · {{ selectedNode.dish_family }}</div>
          <div class="panel-card">
            <div class="chips">
              <span
                v-for="sib in siblings"
                :key="sib.id"
                class="chip chip-clickable"
                :style="buildTagStyle(sib.color, false)"
                @click="appStore.selectNode(sib)"
              >
                {{ sib.city }} · {{ sib.dish }}
              </span>
            </div>
          </div>
        </template>
        </div>

        <!-- L1 Ecozone panel -->
        <div v-else-if="selectedEcozone" key="ecozone" class="panel-content">
        <div class="panel-tab">L1 自然生态档案</div>
        <div class="panel-title" style="font-size:16px;line-height:1.5">{{ selectedEcozone.eco_name_cn || selectedEcozone.eco_name || '未知生态区' }}</div>
        <div class="panel-subtitle">{{ selectedEcozone.biome_cn || selectedEcozone.biome }} · {{ selectedEcozone.realm }}</div>

        <div class="section-label">生境概况</div>
        <div class="eco-biome-badge" :style="{ borderColor: biomePalette[selectedEcozone.biome] || biomePaletteFallback }">
          <span class="biome-num">{{ selectedEcozone.eco_code }}</span>
          <span class="biome-name">{{ selectedEcozone.biome_cn || selectedEcozone.biome }}</span>
        </div>

        <div class="section-label" style="margin-top:16px">气候特征（模拟示意）</div>
        <div class="panel-card">
          <div ref="climateEl" class="echart-wrap echart-climate" />
        </div>

        <div v-if="selectedEcozone.realm" class="panel-source" style="margin-top:16px">
          生物地理界：{{ selectedEcozone.realm }}
        </div>
        </div>

        <!-- Route panel -->
        <div v-else-if="selectedRoute" key="route" class="panel-content">
        <div class="panel-tab">传播路径</div>
        <div class="panel-title">{{ selectedRoute.name }}</div>
        <div class="panel-subtitle">{{ selectedRoute.type === 'sea' ? '海路传播' : '陆路传播' }} · {{ selectedRoute.path.length }} 个节点</div>
        <div class="panel-card route-card">
          <div class="route-line" :style="{ background: selectedRoute.color }" />
          <p class="route-desc">
            这条{{ selectedRoute.type === 'sea' ? '海上' : '陆上' }}路线是风味基因跨越地理屏障的核心通道。
            沿途经过的生态区差异与气候梯度，塑造了食材在传播过程中的逐步"变异"。
          </p>
          <div class="waypoints">
            <div v-for="(pt, i) in selectedRoute.path" :key="i" class="waypoint">
              <span class="wpt-dot" :style="{ background: selectedRoute.color }" />
              <span class="wpt-coord">{{ pt[0].toFixed(1) }}°, {{ pt[1].toFixed(1) }}°</span>
            </div>
          </div>
        </div>
        </div>

        <!-- Empty state -->
        <div v-else key="empty" class="empty-state">
        <div class="empty-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
        </div>
        <p>点击地图节点<br>或搜索食材查看详情</p>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useAppStore } from '../stores/app.js'
import FlavorRadar from './FlavorRadar.vue'
import * as echarts from 'echarts'

const appStore = useAppStore()
const selectedNode   = computed(() => appStore.selectedNode)
const selectedRoute  = computed(() => appStore.selectedRoute)
const selectedEcozone = computed(() => appStore.selectedEcozone)
const hoveredIngredient = ref(null)
const inspectorCollapsed = ref(false)

const siblings = computed(() => {
  const node = appStore.selectedNode
  if (!node || !node.dish_family) return []
  return appStore.flavors.filter(f => f.dish_family === node.dish_family && f.id !== node.id)
})

// ── ECharts instances ──────────────────────────────────────────────────────
const climateEl = ref(null)
let climateChart = null

// ── Climate chart → ECharts dual-axis line ─────────────────────────────────
const MONTHS = ['J','F','M','A','M','J','J','A','S','O','N','D']

function biomeHash(str) {
  let h = 0
  for (let i = 0; i < (str || '').length; i++) h = ((h << 5) - h) + str.charCodeAt(i)
  return Math.abs(h)
}

function hexToRgba(hex, alpha) {
  const value = hex.replace('#', '')
  const r = parseInt(value.slice(0, 2), 16)
  const g = parseInt(value.slice(2, 4), 16)
  const b = parseInt(value.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

function buildTagStyle(color, active = false) {
  return {
    background: active ? hexToRgba(color, 0.2) : hexToRgba(color, 0.1),
    color,
    borderColor: active ? hexToRgba(color, 0.28) : hexToRgba(color, 0.14),
    boxShadow: active ? `0 12px 26px ${hexToRgba(color, 0.16)}` : 'none',
  }
}

function buildClimateOption(ecozone) {
  if (!ecozone) return {}
  const b = biomeHash(ecozone.biome)
  const temps = Array.from({ length: 12 }, (_, i) => 10 + (b % 5) * 4 + Math.sin((i - 1) * Math.PI / 6) * 12)
  const precips = Array.from({ length: 12 }, (_, i) => 8 + ((b * 3 + i * 2) % 20) + Math.random() * 2)

  return {
    grid: { left: 32, right: 32, top: 22, bottom: 18 },
    xAxis: { type: 'category', data: MONTHS, axisLine: { lineStyle: { color: 'rgba(0,0,0,0.07)' } }, axisTick: { show: false }, axisLabel: { fontSize: 8, color: 'rgba(87,83,78,0.45)', fontFamily: 'Inter,sans-serif' } },
    yAxis: [
      { type: 'value', name: '°C', nameTextStyle: { fontSize: 8, color: '#E5394E' }, splitLine: { lineStyle: { color: 'rgba(0,0,0,0.04)' } }, axisLabel: { fontSize: 8, color: 'rgba(87,83,78,0.4)' }, min: -5 },
      { type: 'value', name: 'mm', nameTextStyle: { fontSize: 8, color: '#0FB89A' }, splitLine: { show: false }, axisLabel: { fontSize: 8, color: 'rgba(87,83,78,0.4)' } },
    ],
    series: [
      { type: 'line', data: temps, smooth: true, lineStyle: { color: '#E5394E', width: 1.5 }, itemStyle: { color: '#E5394E' }, symbol: 'none', animation: true, animationDuration: 800, silent: true },
      { type: 'line', yAxisIndex: 1, data: precips, smooth: true, lineStyle: { color: '#0FB89A', width: 1.5, type: 'dashed' }, itemStyle: { color: '#0FB89A' }, symbol: 'none', animation: true, animationDuration: 800, silent: true, areaStyle: { color: 'rgba(15,184,154,0.08)' } },
    ],
    legend: { show: false },
    tooltip: { show: false },
  }
}

// ── Lifecycle ──────────────────────────────────────────────────────────────
function ensureClimateChart() {
  if (!climateChart && climateEl.value) {
    climateChart = echarts.init(climateEl.value, null, { renderer: 'canvas' })
  }
  return climateChart
}

onMounted(async () => {
  await nextTick()
  if (selectedEcozone.value) ensureClimateChart()?.setOption(buildClimateOption(selectedEcozone.value), true)
})

watch(selectedNode, async (node) => {
  hoveredIngredient.value = null
  if (!node) return
})

watch(selectedEcozone, async (eco) => {
  if (!eco) return
  await nextTick()
  ensureClimateChart()?.setOption(buildClimateOption(eco), true)
})

onUnmounted(() => { climateChart?.dispose() })

// ── Biome palette ──────────────────────────────────────────────────────────
const biomePalette = {
  'Tropical & Subtropical Moist Broadleaf Forests': '#3A7D44',
  'Tropical & Subtropical Dry Broadleaf Forests':   '#8DB87A',
  'Tropical & Subtropical Coniferous Forests':       '#C8B05A',
  'Temperate Broadleaf & Mixed Forests':             '#5A8A5A',
  'Temperate Conifer Forests':                       '#A0C060',
  'Boreal Forests/Taiga':                            '#5A7040',
  'Tropical & Subtropical Grasslands & Savannas':    '#D0A050',
  'Temperate Grasslands & Savannas':                 '#C8C870',
  'Flooded Grasslands & Savannas':                   '#70B8A0',
  'Montane Grasslands & Shrublands':                 '#A0B8C8',
  'Tundra':                                          '#40A890',
  'Mediterranean Forests & Woodlands':               '#A09050',
  'Deserts & Xeric Shrublands':                      '#D8B880',
  'Mangroves':                                       '#2A8870',
}
const biomePaletteFallback = '#C4B49A'
</script>

<style scoped>
.inspector {
  position: fixed;
  top: calc(var(--navbar-h) + 16px);
  right: 28px;
  bottom: 28px;
  width: 290px;
  border-radius: var(--radius);
  overflow: visible;
  z-index: 10;
  transition:
    width 220ms ease,
    height 220ms ease,
    bottom 220ms ease,
    border-radius 220ms ease,
    box-shadow 220ms ease;
}

.inspector.collapsed {
  bottom: auto;
  width: 48px;
  height: 48px;
  border-radius: 999px;
}

.inspector-body {
  height: 100%;
  overflow: hidden;
  border-radius: inherit;
}

.inspector-toggle {
  position: absolute;
  left: -16px;
  top: 50%;
  z-index: 2;
  width: 32px;
  height: 44px;
  border: 1px solid rgba(180, 165, 140, 0.2);
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 252, 248, 0.92);
  color: rgba(87, 83, 78, 0.68);
  box-shadow: 0 12px 28px rgba(42, 31, 18, 0.1);
  cursor: pointer;
  transform: translateY(-50%);
  transition:
    left 220ms ease,
    width 220ms ease,
    height 220ms ease,
    color 180ms ease,
    background 180ms ease,
    box-shadow 180ms ease;
}

.inspector-toggle:hover {
  color: var(--amber);
  background: rgba(255, 252, 248, 0.98);
  box-shadow: 0 14px 32px rgba(42, 31, 18, 0.14);
}

.inspector-toggle:focus-visible {
  outline: 2px solid rgba(232, 169, 23, 0.34);
  outline-offset: 2px;
}

.inspector-toggle span {
  font-size: 22px;
  line-height: 1;
  transform: translateY(-1px);
}

.inspector.collapsed .inspector-toggle {
  inset: 0;
  width: 48px;
  height: 48px;
  transform: none;
}

.empty-state {
  height: 100%;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 16px; opacity: 0.58; padding: 24px;
  text-align: center;
}
.empty-icon {
  width: 42px; height: 42px;
  border-radius: 50%;
  border: 1px solid rgba(180, 165, 140, 0.22);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-muted);
  background: radial-gradient(circle, rgba(255,252,248,0.82) 0%, rgba(255,252,248,0.36) 100%);
  box-shadow: 0 14px 28px rgba(42, 31, 18, 0.08);
}
.empty-state p { font-size: 12px; color: rgba(87,83,78,0.72); line-height: 1.9; letter-spacing: 0.04em; }

.panel-content { padding: 24px; overflow-y: auto; height: 100%; }
.panel-tab { font-size: 10px; letter-spacing: 0.18em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 14px; }
.panel-title { font-family: var(--font-serif); font-size: 20px; font-weight: 500; color: var(--text); margin-bottom: 4px; }
.panel-subtitle { font-size: 11px; color: var(--text-muted); letter-spacing: 0.06em; margin-bottom: 18px; }
.section-label { font-size: 10px; color: var(--text-muted); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 10px; }
.panel-card {
  border-radius: 18px;
  border: 1px solid rgba(180, 165, 140, 0.16);
  background:
    linear-gradient(180deg, rgba(255, 252, 248, 0.74) 0%, rgba(255, 252, 248, 0.58) 100%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.55);
}
.radar-wrap { display: flex; justify-content: center; padding: 12px 0; }

.echart-wrap { width: 100%; }
.echart-climate { height: 130px; padding: 10px 0 6px; }

.node-description {
  margin: 0;
  padding: 14px 16px;
  font-size: 12px;
  line-height: 1.85;
  color: var(--text-mid);
  letter-spacing: 0.03em;
}

.chips { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px; }
.chip {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 11px;
  border: 1px solid transparent;
  transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease;
}
.chip.active,
.chip:hover { transform: translateY(-1px); }
.chip-clickable { cursor: pointer; }

.eco-biome-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 14px; border-radius: 20px;
  border: 1px solid; background: rgba(200,180,150,0.08);
  margin-bottom: 2px;
}
.biome-num { font-family: 'Inter',sans-serif; font-size: 11px; color: var(--text-muted); }
.biome-name { font-size: 12px; color: var(--text-mid); }

.route-card { padding: 14px 14px 12px; }
.route-line { height: 2px; border-radius: 999px; margin: 2px 0 14px; opacity: 0.72; box-shadow: 0 0 16px rgba(232,169,23,0.18); }
.route-desc { font-size: 12px; line-height: 1.9; color: var(--text-mid); font-weight: 300; margin-bottom: 16px; }
.waypoints { display: flex; flex-direction: column; gap: 8px; }
.waypoint { display: flex; align-items: center; gap: 10px; }
.wpt-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.wpt-coord { font-size: 11px; font-family: 'Inter', sans-serif; color: var(--text-muted); }
.panel-source { font-size: 10px; color: var(--text-muted); letter-spacing: 0.06em; }

.panel-enter-active, .panel-leave-active { transition: opacity 200ms ease; }
.panel-enter-from, .panel-leave-to { opacity: 0; }
</style>
