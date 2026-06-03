<template>
  <main class="archive-atlas-page fixed top-navbar inset-x-0 bottom-0 grid grid-cols-[320px_1fr_300px] overflow-hidden" :style="cssVars">
    <!-- 左侧：环境与气候基因 -->
    <aside class="atlas-sidebar left-sidebar py-8 px-6 overflow-y-auto z-10 flex flex-col gap-10">
      <header>
        <span class="kicker text-[10px] uppercase tracking-[0.1em] font-bold">Provenance Dashboard</span>
        <h1 class="font-serif text-[28px] my-1 mb-2 text-[#1A1815] font-semibold tracking-[2px]">科学溯源白皮书</h1>
        <p class="text-[12px] text-[#666] leading-[1.6]">基于原产地遥感与第三方实验室实证的品质看板</p>
      </header>

      <nav class="flex gap-4 border-b border-[rgba(0,0,0,0.1)] pb-2">
        <button
          v-for="item in dossiers" :key="item.id"
          class="product-tab bg-transparent border-none px-0 pb-1.5 text-[15px] cursor-pointer text-[#888] relative font-serif transition-all duration-300"
          :class="{ active: activeId === item.id }"
          @click="activeId = item.id"
        >
          {{ item.name }}
        </button>
      </nav>

      <div class="flex flex-col">
        <div class="flex justify-between items-baseline mb-1">
          <h3 class="text-base font-semibold tracking-[1px] text-[#222] m-0">气候风土因子</h3>
          <span class="text-[9px] font-mono border border-[rgba(0,0,0,0.15)] py-0.5 px-1.5 rounded-sm text-[#555]">{{ dossier.stationCode }}</span>
        </div>
        <p class="text-[11px] text-[#777] m-0 mb-3">关键生长期月均降水量与气温曲线</p>
        <div ref="climateChartEl" class="w-full h-[200px]" />
      </div>

      <div class="flex flex-col">
        <div class="flex justify-between items-baseline mb-1">
          <h3 class="text-base font-semibold tracking-[1px] text-[#222] m-0">生长期有效积温</h3>
          <span class="text-[9px] font-mono border border-[rgba(0,0,0,0.15)] py-0.5 px-1.5 rounded-sm text-[#555]">GDD Data</span>
        </div>
        <p class="text-[11px] text-[#777] m-0 mb-3">作物生命周期内的热量累积证据</p>
        <div ref="heatChartEl" class="w-full h-[200px]" />
      </div>
    </aside>

    <!-- 中间：核心空间地图 -->
    <section class="relative w-full h-full">
      <div ref="terrainMapEl" class="absolute inset-0 w-full h-full" />

      <div class="floating-metrics-strip absolute bottom-10 left-1/2 -translate-x-1/2 flex gap-8 bg-[rgba(255,255,255,0.9)] px-8 py-5 rounded z-[5] border border-[rgba(0,0,0,0.05)]">
        <div v-for="metric in dossier.metrics" :key="metric.label" class="flex flex-col items-center text-center">
          <span class="text-[10px] text-[#888] uppercase tracking-[1px] mb-1">{{ metric.label }}</span>
          <strong class="fm-value font-serif text-[20px] font-bold mb-0.5">{{ metric.value }}</strong>
          <span class="text-[10px] text-[#999]">{{ metric.note }}</span>
        </div>
      </div>

      <div class="floating-map-legend absolute top-8 left-8 z-[5] bg-[rgba(255,255,255,0.85)] p-4 rounded-sm border border-[rgba(0,0,0,0.08)]">
        <div class="origin-pin-info">
          <strong class="block text-[13px]">◉ {{ dossier.originPoint.name }}</strong>
          <span class="text-[10px] text-[#666] font-mono">{{ dossier.originPoint.precision }} | {{ formatCoord(dossier.originPoint.coord) }}</span>
        </div>
        <div class="mt-4 pt-4 border-t border-dashed border-[rgba(0,0,0,0.1)] flex flex-col gap-3">
          <div v-for="node in dossier.nodes" :key="node.short" class="flex gap-2 items-start">
            <span class="w-1.5 h-1.5 rounded-full bg-[#ccc] mt-1" />
            <div>
              <strong class="block text-[12px] text-[#333]">{{ node.short }}</strong>
              <span class="text-[10px] text-[#888]">{{ node.desc }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 右侧：理化指标与食品安全 -->
    <aside class="atlas-sidebar right-sidebar py-8 px-6 overflow-y-auto z-10 flex flex-col gap-10 border-r-0 border-l border-[rgba(0,0,0,0.06)]">
      <div class="flex flex-col">
        <div class="flex justify-between items-baseline mb-1">
          <h3 class="text-base font-semibold tracking-[1px] text-[#222] m-0">品质对标国标</h3>
          <span class="text-[9px] font-mono border border-[rgba(0,0,0,0.15)] py-0.5 px-1.5 rounded-sm text-[#555]">Benchmark</span>
        </div>
        <p class="text-[11px] text-[#777] m-0 mb-3">关键理化指标实测值与收购验收线对比</p>
        <div ref="standardRadarEl" class="w-full h-[200px]" />
      </div>

      <div class="flex flex-col">
        <div class="flex justify-between items-baseline mb-1">
          <h3 class="text-base font-semibold tracking-[1px] text-[#222] m-0">原产地风味指纹</h3>
        </div>
        <div class="flex flex-col items-center gap-4">
          <FlavorRadar :scores="dossier.flavorScores" :color="dossier.color" :size="140" animated />
          <p class="text-[12px] text-[#555] leading-[1.6] italic text-center bg-[rgba(0,0,0,0.03)] p-3 rounded-sm">"{{ dossier.flavorSummary }}"</p>
        </div>
      </div>

      <div class="flex flex-col">
        <div class="flex justify-between items-baseline mb-1">
          <h3 class="text-base font-semibold tracking-[1px] text-[#222] m-0">实验室级安全凭证</h3>
          <span class="badge-pass text-[9px] font-mono border py-0.5 px-1.5 rounded-sm font-bold">已通过检验</span>
        </div>
        <div class="flex flex-col gap-3">
          <div v-for="report in dossier.reports" :key="report.org" class="cert-ticket border border-[rgba(0,0,0,0.1)] p-3 rounded-sm">
            <div class="text-[10px] text-[#777] mb-1">{{ report.org }}</div>
            <div class="text-[13px] font-bold text-[#222] mb-1.5">{{ report.result }}</div>
            <div class="text-[10px] font-mono text-[#aaa]">REP: {{ report.code }}</div>
          </div>
        </div>
      </div>
    </aside>
  </main>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import chinaGeoJson from '../assets/china.json'
import FlavorRadar from '../components/FlavorRadar.vue'

const dossiers = [
  {
    id: 'pepper',
    name: '汉源花椒',
    origin: '四川汉源 · 干热河谷',
    province: '四川省',
    color: '#9C3131',
    accent: '#516E58',
    stationCode: 'HY-MET-2605',
    metrics: [
      { label: '挥发油总量', value: '5.8%', note: '远超行标验收线' },
      { label: '羟基山椒素', value: '38 mg/g', note: '决定级麻感指标' },
      { label: 'SGS 安全筛查', value: '0 检出', note: '219项农残未检出' },
      { label: '溯源采样点', value: '18 处', note: '产地/中转/前置仓' }
    ],
    nodes: [
      { short: '汉源采样区', desc: '海拔1600m批次抽样', coord: [102.6342, 29.5621] },
      { short: '成都中转仓', desc: '入库理化复检', coord: [104.1623, 30.8241] },
      { short: '终端交付', desc: '冷链全损耗监控', coord: [121.3821, 31.1123] }
    ],
    originPoint: { name: '四川省·雅安市汉源县', coord: [102.6506, 29.3443], precision: '核心原产地基准坐标' },
    climate: { rain: [7, 12, 24, 55, 82, 118, 176, 143, 96, 46, 18, 8], temp: [6.2, 8.8, 13.1, 17.4, 20.6, 23.2, 24.8, 24.1, 20.5, 16.4, 11.1, 7.2] },
    heat: [ { stage: '萌芽', value: 240 }, { stage: '展叶', value: 510 }, { stage: '开花', value: 760 }, { stage: '坐果', value: 1030 }, { stage: '成熟', value: 1290 } ],
    benchmark: [132, 128, 116, 141, 125],
    benchmarkLabels: ['挥发油', '麻味物质', '净含水率', '果皮洁净度', '香气留存'],
    flavorScores: [0.92, 0.58, 0.18, 0.12, 0.06, 0.36],
    flavorSummary: '极为霸道的醇麻感与清晰的柑橘类辛香，是鉴别正路贡椒的决定性风味指纹。',
    reports: [ { org: 'SGS 通标标准技术', result: '219项农残：未检出', code: 'SGS-HY-2605-018' }, { org: '谱尼测试 PONY', result: '重金属元素：符合国标', code: 'PONY-HY-2605-022' } ]
  },
  {
    id: 'rice',
    name: '五常大米',
    origin: '黑龙江五常 · 寒地黑土',
    province: '黑龙江省',
    color: '#4B6342',
    accent: '#B57A3C',
    stationCode: 'WC-MET-2605',
    metrics: [
      { label: '天然直链淀粉', value: '17.2%', note: '软糯口感核心区间' },
      { label: '胶稠度指标', value: '72 mm', note: '超越一等优质米线' },
      { label: 'SGS 安全筛查', value: '0 检出', note: '百项农残专项抽检' },
      { label: '溯源采样点', value: '12 处', note: '田块/原粮仓/销地' }
    ],
    nodes: [
      { short: '五常水稻田', desc: '拉林河流域原粮抽检', coord: [127.1676, 44.9192] },
      { short: '恒温去壳仓', desc: '温湿度及碎米率监控', coord: [126.6331, 45.7422] },
      { short: '长三角终端', desc: '鲜米直达复检', coord: [121.4737, 31.2304] }
    ],
    originPoint: { name: '黑龙江省·哈尔滨五常市', coord: [127.1676, 44.9318], precision: '核心原产地基准坐标' },
    climate: { rain: [4, 6, 13, 28, 49, 86, 142, 118, 62, 31, 12, 5], temp: [-18.4, -12.6, -3.1, 8.6, 16.4, 21.1, 23.5, 21.2, 15.3, 6.7, -5.2, -15.7] },
    heat: [ { stage: '育秧', value: 180 }, { stage: '返青', value: 420 }, { stage: '分蘖', value: 870 }, { stage: '抽穗', value: 1560 }, { stage: '成熟', value: 2380 } ],
    benchmark: [118, 136, 126, 112, 129],
    benchmarkLabels: ['直链淀粉', '胶稠度', '垩白率', '整精米率', '食味值'],
    flavorScores: [0.08, 0.04, 0.18, 0.06, 0.54, 0.46],
    flavorSummary: '入口回甘伴随清淡的植物甜香，米粒形态和咀嚼质感极度稳定。',
    reports: [ { org: 'SGS 通标标准技术', result: '全量农残：未检出', code: 'SGS-WC-2605-011' }, { org: '谱尼测试 PONY', result: '真菌毒素：符合国标', code: 'PONY-WC-2605-016' } ]
  }
]

const activeId = ref('pepper')
const dossier = computed(() => dossiers.find(item => item.id === activeId.value))
const provinceFeature = computed(() => chinaGeoJson.features.find(f => f.properties?.name === dossier.value.province))

const climateChartEl = ref(null), heatChartEl = ref(null), standardRadarEl = ref(null), terrainMapEl = ref(null)
let climateChart, heatChart, standardRadar, terrainMap, originMarker

const cssVars = computed(() => ({
  '--theme-main': dossier.value.color,
  '--theme-accent': dossier.value.accent
}))

const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

function formatCoord(coord) { return `${coord[0].toFixed(4)}°E, ${coord[1].toFixed(4)}°N` }

const commonEchartsOptions = {
  textStyle: { fontFamily: '-apple-system, "PingFang SC", sans-serif' },
  backgroundColor: 'transparent',
}

function renderCharts() {
  if (!climateChart) climateChart = echarts.init(climateChartEl.value)
  if (!heatChart) heatChart = echarts.init(heatChartEl.value)
  if (!standardRadar) standardRadar = echarts.init(standardRadarEl.value)

  climateChart.setOption({
    ...commonEchartsOptions,
    color: [dossier.value.accent, dossier.value.color],
    grid: { top: 30, right: 30, bottom: 20, left: 30, containLabel: true },
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.9)', borderColor: dossier.value.color },
    legend: { top: 0, right: 0, itemWidth: 12, itemHeight: 2, textStyle: { color: '#666', fontSize: 10 } },
    xAxis: { type: 'category', data: months, axisTick: { show: false }, axisLine: { lineStyle: { color: '#ddd' } }, axisLabel: { color: '#888', fontSize: 10 } },
    yAxis: [
      { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }, axisLabel: { color: '#888', fontSize: 10 } },
      { type: 'value', splitLine: { show: false }, axisLabel: { color: '#888', fontSize: 10 } },
    ],
    series: [
      { name: '降水量', type: 'bar', barWidth: 8, itemStyle: { borderRadius: [2,2,0,0] }, data: dossier.value.climate.rain },
      { name: '均温', type: 'line', smooth: true, yAxisIndex: 1, symbol: 'circle', symbolSize: 6, lineStyle: { width: 2 }, data: dossier.value.climate.temp },
    ],
  }, true)

  heatChart.setOption({
    ...commonEchartsOptions,
    color: [dossier.value.color],
    grid: { top: 10, right: 10, bottom: 20, left: 10, containLabel: true },
    tooltip: { trigger: 'axis', valueFormatter: value => `${value} ℃·d` },
    xAxis: { type: 'category', data: dossier.value.heat.map(item => item.stage), axisTick: { show: false }, axisLine: { lineStyle: { color: '#ddd' } }, axisLabel: { color: '#888', fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }, axisLabel: { color: '#888', fontSize: 10 } },
    series: [{ type: 'line', step: 'middle', symbol: 'emptyCircle', symbolSize: 6, lineStyle: { width: 1.5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: dossier.value.color + '44'}, {offset: 1, color: dossier.value.color + '00'}]) }, data: dossier.value.heat.map(item => item.value) }],
  }, true)

  standardRadar.setOption({
    ...commonEchartsOptions,
    color: [dossier.value.color, '#b0b0b0'],
    radar: {
      radius: '65%', center: ['50%', '55%'],
      indicator: dossier.value.benchmarkLabels.map(name => ({ name, max: 160 })),
      axisName: { color: '#555', fontSize: 10, fontFamily: 'serif' },
      splitLine: { lineStyle: { color: '#e0e0e0', width: 1 } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: '#e0e0e0' } },
    },
    series: [{
      type: 'radar', symbolSize: 4,
      data: [
        { value: dossier.value.benchmark, name: '批次实测', lineStyle: { width: 2 }, areaStyle: { color: dossier.value.color + '22' } },
        { value: [100, 100, 100, 100, 100], name: '国标底线', lineStyle: { type: 'dashed', width: 1 } },
      ]
    }],
  }, true)
}

function initTerrainMap() {
  if (terrainMap) return
  terrainMap = new maplibregl.Map({
    container: terrainMapEl.value,
    style: {
      version: 8,
      sources: { 'hyp-tiles': { type: 'raster', tiles: ['/tiles/raster/{z}/{x}/{y}.png'], tileSize: 256, maxzoom: 8 } },
      layers: [
        { id: 'bg', type: 'background', paint: { 'background-color': '#F4F3ED' } },
        { id: 'hyp', type: 'raster', source: 'hyp-tiles', paint: { 'raster-opacity': 0.6, 'raster-saturation': -0.8, 'raster-contrast': 0.1 } }
      ]
    },
    center: dossier.value.originPoint.coord, zoom: 6,
    interactive: true, dragRotate: false, pitchWithRotate: false
  })

  terrainMap.on('load', () => {
    terrainMap.addSource('active-province', { type: 'geojson', data: { type: 'FeatureCollection', features: [provinceFeature.value] } })
    terrainMap.addLayer({ id: 'province-fill', type: 'fill', source: 'active-province', paint: { 'fill-color': dossier.value.color, 'fill-opacity': 0.1 } })
    terrainMap.addLayer({ id: 'province-line', type: 'line', source: 'active-province', paint: { 'line-color': dossier.value.color, 'line-width': 1.5, 'line-dasharray': [2, 2] } })
    updateMapData()
  })
}

function updateMapData() {
  if (!terrainMap || !terrainMap.isStyleLoaded()) return
  terrainMap.getSource('active-province')?.setData({ type: 'FeatureCollection', features: [provinceFeature.value] })
  terrainMap.setPaintProperty('province-fill', 'fill-color', dossier.value.color)
  terrainMap.setPaintProperty('province-line', 'line-color', dossier.value.color)

  if (originMarker) originMarker.remove()
  const el = document.createElement('div')
  el.className = 'vector-pinpoint'
  el.style.borderColor = dossier.value.color
  originMarker = new maplibregl.Marker({ element: el }).setLngLat(dossier.value.originPoint.coord).addTo(terrainMap)

  const bounds = new maplibregl.LngLatBounds()
  const coords = provinceFeature.value?.geometry?.coordinates
  if (coords) {
    const flatCoords = coords.flat(Infinity)
    for (let i = 0; i < flatCoords.length; i += 2) bounds.extend([flatCoords[i], flatCoords[i+1]])
    terrainMap.fitBounds(bounds, { padding: 80, duration: 1200 })
  }
}

function handleResize() { climateChart?.resize(); heatChart?.resize(); standardRadar?.resize(); terrainMap?.resize(); }

onMounted(() => {
  nextTick(() => { renderCharts(); initTerrainMap(); })
  window.addEventListener('resize', handleResize)
})
watch(activeId, () => { nextTick(() => { renderCharts(); updateMapData(); }) })
onUnmounted(() => { window.removeEventListener('resize', handleResize); climateChart?.dispose(); heatChart?.dispose(); standardRadar?.dispose(); terrainMap?.remove(); })
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════
   KEPT — Tailwind cannot express these:
   dynamic CSS variable theming (--theme-main),
   semi-transparent backgrounds, backdrop-filter,
   pseudo-elements, composite box-shadows,
   :deep() MapLibre marker styles, responsive restructuring
   ═══════════════════════════════════════════════════════════════ */

/* KEPT: paper background + font — specific "canvas" aesthetic not in design system */
.archive-atlas-page {
  background: #F4F3ED;
  color: #332F2A;
  font-family: -apple-system, "PingFang SC", sans-serif;
}

/* KEPT: semi-transparent bg + backdrop-filter for fused-with-map sidebar */
.atlas-sidebar {
  background: rgba(244, 243, 237, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-right: 1px solid rgba(0,0,0,0.06);
}

/* KEPT: dynamic var(--theme-main) for brand accent color */
.kicker { color: var(--theme-main); }

/* KEPT: dynamic active color + pseudo-element underline */
.product-tab.active { color: var(--theme-main); font-weight: bold; }
.product-tab.active::after {
  content: ''; position: absolute; left: 0; right: 0; bottom: -9px;
  height: 2px; background: var(--theme-main);
}

/* KEPT: semi-transparent green pass badge */
.badge-pass { background: rgba(81, 110, 88, 0.1); color: #516E58; border-color: #516E58; }

/* KEPT: floating panel — composite box-shadow + semi-transparent bg */
.floating-metrics-strip { box-shadow: 0 12px 32px rgba(0,0,0,0.08); }

/* KEPT: floating legend — semi-transparent bg + backdrop-filter + box-shadow */
.floating-map-legend { backdrop-filter: blur(4px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

/* KEPT: dynamic var(--theme-main) for metric values */
.fm-value { color: var(--theme-main); }

/* KEPT: dynamic var(--theme-main) for origin pin label */
.origin-pin-info strong { color: var(--theme-main); }

/* KEPT: cert ticket — SVG data URI background texture */
.cert-ticket {
  background: url('data:image/svg+xml;utf8,<svg width="4" height="4" viewBox="0 0 4 4" xmlns="http://www.w3.org/2000/svg"><rect width="4" height="4" fill="none"/><circle cx="2" cy="2" r="0.5" fill="%23000" fill-opacity="0.05"/></svg>');
}

/* KEPT: MapLibre marker — :deep() + pseudo-element crosshair */
:deep(.vector-pinpoint) {
  width: 14px; height: 14px; border: 2px solid; border-radius: 50%;
  background: rgba(255,255,255,0.8); box-shadow: 0 0 0 4px rgba(255,255,255,0.4);
  position: relative;
}
:deep(.vector-pinpoint::after) {
  content: ''; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 4px; height: 4px; background: currentColor; border-radius: 50%;
}

/* KEPT: responsive — grid restructuring (3-col → 1-col + reorder) */
@media (max-width: 1200px) {
  .archive-atlas-page { grid-template-columns: 280px 1fr 280px; }
  .floating-metrics-strip { flex-wrap: wrap; justify-content: center; width: 80%; padding: 16px; gap: 16px; bottom: 20px; }
}
@media (max-width: 860px) {
  .archive-atlas-page { grid-template-columns: 1fr; overflow-y: auto; position: static; height: auto; display: flex; flex-direction: column; }
  .atlas-center-map { height: 50vh; min-height: 400px; order: -1; }
  .atlas-sidebar { border: none; padding: 20px; }
}
</style>
