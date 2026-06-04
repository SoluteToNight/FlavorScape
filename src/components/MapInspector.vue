<template>
  <div class="inspector glass-panel fixed top-[calc(var(--navbar-h)+16px)] right-7 bottom-7 w-[290px] rounded-lg overflow-visible z-10" :class="{ collapsed: inspectorCollapsed }">
    <button
      type="button"
      class="inspector-toggle absolute -left-4 top-1/2 z-[2] w-8 h-11 border border-[rgba(180,165,140,0.2)] rounded-full inline-flex items-center justify-center bg-[rgba(255,252,248,0.92)] text-[rgba(87,83,78,0.68)] cursor-pointer -translate-y-1/2"
      :aria-label="inspectorCollapsed ? '展开详情面板' : '折叠详情面板'"
      :aria-expanded="!inspectorCollapsed"
      @click="inspectorCollapsed = !inspectorCollapsed"
    >
      <span class="text-[22px] leading-none -translate-y-px">{{ inspectorCollapsed ? '‹' : '›' }}</span>
    </button>

    <div v-show="!inspectorCollapsed" class="h-full overflow-hidden rounded-[inherit]">
      <Transition name="panel" mode="out-in">
        <!-- Node panel -->
        <div v-if="selectedNode" key="node" class="panel-content px-6 py-6 overflow-y-auto h-full">
        <div class="text-2xs tracking-[0.18em] text-text-muted uppercase mb-3.5">风味节点</div>
        <div class="panel-title font-serif text-2xl font-medium text-text mb-1">{{ selectedNode.dish || selectedNode.city }}</div>
        <div class="panel-subtitle text-xs text-text-muted tracking-[0.06em] mb-[18px]">{{ selectedNode.city }} · {{ selectedNode.region }} · {{ selectedNode.eco }}</div>

        <div class="section-label text-2xs text-text-muted tracking-[0.12em] uppercase mb-2.5">风味雷达图</div>
        <div class="panel-card rounded-[18px] border border-[rgba(180,165,140,0.16)]">
          <div class="radar-wrap flex justify-center py-3">
            <FlavorRadar :scores="selectedNode.scores" :color="selectedNode.color" :size="148" :animated="true" />
          </div>
        </div>

        <div class="section-label text-2xs text-text-muted tracking-[0.12em] uppercase mb-2.5 mt-4">风味描述</div>
        <div class="panel-card rounded-[18px] border border-[rgba(180,165,140,0.16)]">
          <p class="node-description m-0 px-4 py-3.5 text-xs leading-[1.85] text-text-mid tracking-[0.03em]">
            {{ selectedNode.description }}
          </p>
        </div>

        <div class="section-label text-2xs text-text-muted tracking-[0.12em] uppercase mb-2.5" style="margin-top:16px">食材基因</div>
        <div class="panel-card rounded-[18px] border border-[rgba(180,165,140,0.16)]">
          <div class="chips flex flex-wrap gap-2 p-3">
            <span
              v-for="ing in selectedNode.ingredients"
              :key="ing"
              class="chip px-3 py-1.5 rounded-full text-xs border border-transparent"
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
          <div class="section-label text-2xs text-text-muted tracking-[0.12em] uppercase mb-2.5" style="margin-top:16px">同族成品 · {{ selectedNode.dish_family }}</div>
          <div class="panel-card rounded-[18px] border border-[rgba(180,165,140,0.16)]">
            <div class="chips flex flex-wrap gap-2 p-3">
              <span
                v-for="sib in siblings"
                :key="sib.id"
                class="chip chip-clickable cursor-pointer px-3 py-1.5 rounded-full text-xs border border-transparent"
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
        <div v-else-if="selectedEcozone" key="ecozone" class="panel-content px-6 py-6 overflow-y-auto h-full">
        <div class="text-2xs tracking-[0.18em] text-text-muted uppercase mb-3.5">L1 自然生态档案</div>
        <div class="panel-title font-serif font-medium text-text mb-1" style="font-size:16px;line-height:1.5">{{ selectedEcozone.eco_name_cn || selectedEcozone.eco_name || '未知生态区' }}</div>
        <div class="panel-subtitle text-xs text-text-muted tracking-[0.06em] mb-[18px]">{{ selectedEcozone.biome_cn || selectedEcozone.biome }} · {{ selectedEcozone.realm }}</div>

        <div class="section-label text-2xs text-text-muted tracking-[0.12em] uppercase mb-2.5">生境概况</div>
        <div class="eco-biome-badge inline-flex items-center gap-2 px-3.5 py-1.5 rounded-[20px] border bg-[rgba(200,180,150,0.08)] mb-0.5" :style="{ borderColor: biomePalette[selectedEcozone.biome] || biomePaletteFallback }">
          <span class="font-['Inter',sans-serif] text-xs text-text-muted">{{ selectedEcozone.eco_code }}</span>
          <span class="text-xs text-text-mid">{{ selectedEcozone.biome_cn || selectedEcozone.biome }}</span>
        </div>

        <div class="section-label text-2xs text-text-muted tracking-[0.12em] uppercase mb-2.5" style="margin-top:16px">气候特征（模拟示意）</div>
        <div class="panel-card rounded-[18px] border border-[rgba(180,165,140,0.16)]">
          <div ref="climateEl" class="echart-climate w-full h-[130px] py-2.5 px-0" />
        </div>

        <div v-if="selectedEcozone.realm" class="text-2xs text-text-muted tracking-[0.06em]" style="margin-top:16px">
          生物地理界：{{ selectedEcozone.realm }}
        </div>
        </div>

        <!-- Route panel -->
        <div v-else-if="selectedRoute" key="route" class="panel-content px-6 py-6 overflow-y-auto h-full">
        <div class="text-2xs tracking-[0.18em] text-text-muted uppercase mb-3.5">传播路径</div>
        <div class="panel-title font-serif text-2xl font-medium text-text mb-1">{{ selectedRoute.name }}</div>
        <div class="panel-subtitle text-xs text-text-muted tracking-[0.06em] mb-[18px]">{{ selectedRoute.type === 'sea' ? '海路传播' : '陆路传播' }} · {{ selectedRoute.path.length }} 个节点</div>
        <div class="panel-card route-card rounded-[18px] border border-[rgba(180,165,140,0.16)] p-3.5 pb-3">
          <div class="route-line h-0.5 rounded-full mx-0.5 my-0 mb-3.5 opacity-[0.72]" :style="{ background: selectedRoute.color }" />
          <p class="text-xs leading-[1.9] text-text-mid font-light mb-4">
            这条{{ selectedRoute.type === 'sea' ? '海上' : '陆上' }}路线是风味基因跨越地理屏障的核心通道。
            沿途经过的生态区差异与气候梯度，塑造了食材在传播过程中的逐步"变异"。
          </p>
          <div class="flex flex-col gap-2">
            <div v-for="(pt, i) in selectedRoute.path" :key="i" class="flex items-center gap-2.5">
              <span class="w-[5px] h-[5px] rounded-full shrink-0" :style="{ background: selectedRoute.color }" />
              <span class="text-xs font-['Inter',sans-serif] text-text-muted">{{ pt[0].toFixed(1) }}°, {{ pt[1].toFixed(1) }}°</span>
            </div>
          </div>
        </div>
        </div>

        <!-- Empty state -->
        <div v-else key="empty" class="h-full flex flex-col items-center justify-center gap-4 opacity-[0.58] p-6 text-center">
        <div class="empty-icon w-[42px] h-[42px] rounded-full border border-[rgba(180,165,140,0.22)] flex items-center justify-center text-text-muted">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
        </div>
        <p class="text-xs text-[rgba(87,83,78,0.72)] leading-[1.9] tracking-[0.04em]">点击地图节点<br>或搜索食材查看详情</p>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useAppStore } from '../stores/app.js'
import FlavorRadar from './FlavorRadar.vue'

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
let echartsModule = null

async function getEcharts() {
  if (!echartsModule) {
    echartsModule = await import('echarts')
  }
  return echartsModule
}

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
async function ensureClimateChart() {
  if (!climateChart && climateEl.value) {
    const echarts = await getEcharts()
    climateChart = echarts.init(climateEl.value, null, { renderer: 'canvas' })
  }
  return climateChart
}

onMounted(async () => {
  await nextTick()
  if (selectedEcozone.value) {
    const chart = await ensureClimateChart()
    chart?.setOption(buildClimateOption(selectedEcozone.value), true)
  }
})

watch(selectedNode, async (node) => {
  hoveredIngredient.value = null
  if (!node) return
})

watch(selectedEcozone, async (eco) => {
  if (!eco) return
  await nextTick()
  const chart = await ensureClimateChart()
  chart?.setOption(buildClimateOption(eco), true)
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
/* KEPT: complex transitions, gradients, composite shadows, hover effects, Vue transitions */

.inspector {
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

.inspector-toggle {
  box-shadow: 0 12px 28px rgba(42, 31, 18, 0.1);
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
.inspector.collapsed .inspector-toggle {
  inset: 0;
  width: 48px;
  height: 48px;
  transform: none;
}

.empty-icon {
  background: radial-gradient(circle, rgba(255,252,248,0.82) 0%, rgba(255,252,248,0.36) 100%);
  box-shadow: 0 14px 28px rgba(42, 31, 18, 0.08);
}

.panel-card {
  background:
    linear-gradient(180deg, rgba(255, 252, 248, 0.74) 0%, rgba(255, 252, 248, 0.58) 100%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.55);
}

.chip {
  transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease;
}
.chip.active,
.chip:hover { transform: translateY(-1px); }

.route-line { box-shadow: 0 0 16px rgba(232,169,23,0.18); }

.panel-enter-active, .panel-leave-active { transition: opacity 200ms ease; }
.panel-enter-from, .panel-leave-to { opacity: 0; }
</style>
