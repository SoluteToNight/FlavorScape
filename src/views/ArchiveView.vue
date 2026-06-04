<template>
  <main class="archive-atlas-page" :style="cssVars">
    <!-- 左侧：环境与气候基因 -->
    <aside class="atlas-sidebar left-sidebar">
      <header class="atlas-header">
        <span class="kicker">Provenance Dashboard</span>
        <h1>科学溯源白皮书</h1>
        <p>基于原产地遥感与第三方实验室实证的品质看板</p>
      </header>

      <div class="archive-actions">
        <button type="button" @click="printDossier">打印 / 导出 PDF</button>
      </div>

      <!-- 样本切换：无框极简标签 -->
      <nav class="product-tabs">
        <button
          v-for="item in dossiers" :key="item.id"
          :class="{ active: activeId === item.id }"
          @click="activeId = item.id"
        >
          {{ item.name }}
        </button>
      </nav>

      <div class="data-section">
        <div class="section-title">
          <h3>气候风土因子</h3>
          <span class="badge">{{ dossier.stationCode }}</span>
        </div>
        <p class="section-desc">关键生长期月均降水量与气温曲线</p>
        <div ref="climateChartEl" class="chart-box"></div>
      </div>

      <div class="data-section">
        <div class="section-title">
          <h3>生长期有效积温</h3>
          <span class="badge">GDD Data</span>
        </div>
        <p class="section-desc">作物生命周期内的热量累积证据</p>
        <div ref="heatChartEl" class="chart-box"></div>
      </div>
    </aside>

    <!-- 中间：核心空间地图 (绝对视觉焦点) -->
    <section class="atlas-center-map">
      <!-- 地图容器 -->
      <div ref="terrainMapEl" class="terrain-map-layer"></div>
      
      <!-- 悬浮在地图上方的统计条 -->
      <div class="floating-metrics-strip">
        <div v-for="metric in dossier.metrics" :key="metric.label" class="f-metric">
          <span class="fm-label">{{ metric.label }}</span>
          <strong class="fm-value">{{ metric.value }}</strong>
          <span class="fm-note">{{ metric.note }}</span>
        </div>
      </div>

      <!-- 地图悬浮图例/节点摘要 -->
      <div class="floating-map-legend">
        <div class="origin-pin-info">
          <strong>◉ {{ dossier.originPoint.name }}</strong>
          <span>{{ dossier.originPoint.precision }} | {{ formatCoord(dossier.originPoint.coord) }}</span>
        </div>
        <div class="node-timeline">
          <div v-for="node in dossier.nodes" :key="node.short" class="node-item">
            <span class="node-dot"></span>
            <div>
              <strong>{{ node.short }}</strong>
              <span>{{ node.desc }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 右侧：理化指标与食品安全 -->
    <aside class="atlas-sidebar right-sidebar">
      <div class="data-section">
        <div class="section-title">
          <h3>品质对标国标</h3>
          <span class="badge">Benchmark</span>
        </div>
        <p class="section-desc">关键理化指标实测值与收购验收线对比</p>
        <div ref="standardRadarEl" class="chart-box"></div>
      </div>

      <div class="data-section flavor-section">
        <div class="section-title">
          <h3>原产地风味指纹</h3>
        </div>
        <div class="flavor-integration">
          <FlavorRadar :scores="dossier.flavorScores" :color="dossier.color" :size="140" animated />
          <p class="flavor-summary">“{{ dossier.flavorSummary }}”</p>
        </div>
      </div>

      <div class="data-section safety-section">
        <div class="section-title">
          <h3>实验室级安全凭证</h3>
          <span class="badge pass">已通过检验</span>
        </div>
        <div class="cert-grid">
          <div v-for="report in dossier.reports" :key="report.org" class="cert-ticket">
            <div class="cert-org">{{ report.org }}</div>
            <div class="cert-result">{{ report.result }}</div>
            <div class="cert-code">REP: {{ report.code }}</div>
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

// 【数据部分保持不变，直接复用您提供的 dossiers，仅为精简代码未重复贴出所有内容】
const dossiers = [
  {
    id: 'pepper',
    name: '汉源花椒',
    origin: '四川汉源 · 干热河谷',
    province: '四川省',
    color: '#9C3131', // 调优为更沉稳的高级红
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
    color: '#4B6342', // 调优为高级苔藓绿
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
  },
  {
    id: 'jasmine',
    name: '七窨茉莉翠芽茶底',
    origin: '广西横县 · 福建茶坯双城窨制',
    province: '广西壮族自治区',
    color: '#2F6B54',
    accent: '#C49A4A',
    stationCode: 'HX-JAS-2605',
    metrics: [
      { label: '窨制周期', value: '近20天', note: '七次换花与通花散热' },
      { label: '换花次数', value: '7窨', note: '只闻花香不见花影' },
      { label: '香气指纹', value: 'GC-MS', note: '芳樟醇/乙酸苄酯追踪' },
      { label: '溯源采样点', value: '15 处', note: '茶坯/花源/窨制/仓储' }
    ],
    nodes: [
      { short: '宁德茶坯', desc: '清明前高山茶坯抽样', coord: [119.5479, 27.2489] },
      { short: '横县花源', desc: '午后伏花精油浓度监测', coord: [109.2679, 22.6799] },
      { short: '窨制工坊', desc: '堆窨温控与起花记录', coord: [109.2458, 22.6874] },
      { short: '配方供应链仓', desc: '充氮防潮批次留样', coord: [113.7518, 23.0207] }
    ],
    originPoint: { name: '广西壮族自治区·南宁市横州市', coord: [109.2679, 22.6799], precision: '茉莉花源与窨制核心坐标' },
    climate: { rain: [42, 51, 72, 126, 188, 226, 206, 176, 92, 48, 36, 28], temp: [13.8, 15.6, 19.1, 23.3, 26.4, 28.4, 29.1, 28.7, 27.1, 23.5, 19.2, 15.2] },
    heat: [ { stage: '茶坯清选', value: 180 }, { stage: '伏花采收', value: 360 }, { stage: '一窨', value: 520 }, { stage: '四窨', value: 980 }, { stage: '七窨', value: 1380 } ],
    benchmark: [132, 145, 112, 136, 128],
    benchmarkLabels: ['芳樟醇', '乙酸苄酯', '含水率', '温控稳定', '茶汤纯净'],
    flavorScores: [0.12, 0.04, 0.94, 0.18, 0.22, 0.46],
    flavorSummary: '花香高扬但茶汤清爽，核心不是添加香气，而是让茶坯在反复窨制中吸收夏夜茉莉精油。',
    reports: [ { org: 'GC-MS 香气指纹留样', result: '芳樟醇/乙酸苄酯峰值稳定', code: 'FS-HX-JAS-2605-007' }, { org: '窨制温控批次记录', result: '通花散热曲线完整', code: 'FS-HX-JAS-2605-012' } ]
  },
  {
    id: 'coconut',
    name: '文昌生椰',
    origin: '海南文昌 · 东郊椰林',
    province: '海南省',
    color: '#2D7B67',
    accent: '#C9A05A',
    stationCode: 'WC-COC-2605',
    metrics: [
      { label: '冷榨窗口', value: '1小时', note: '破壳到生榨闭环' },
      { label: 'HPP 锁鲜', value: '600MPa', note: '超高压冷杀菌' },
      { label: '冷链温度', value: '-18°C', note: '跨海冷链分拨' },
      { label: '溯源采样点', value: '10 处', note: '椰林/工厂/HPP/冷链' }
    ],
    nodes: [
      { short: '东郊椰林', desc: '黄金树龄老椰原料抽样', coord: [110.8783, 19.6286] },
      { short: '零度生榨工厂', desc: '1小时破壳到冷榨记录', coord: [110.7792, 19.5433] },
      { short: 'HPP锁鲜中心', desc: '600MPa冷杀菌验证', coord: [110.3312, 20.0311] },
      { short: '跨海冷链仓', desc: '-18°C温控与批次留样', coord: [113.2644, 23.1291] }
    ],
    originPoint: { name: '海南省·文昌市东郊椰林', coord: [110.8783, 19.6286], precision: '核心椰林原料基准坐标' },
    climate: { rain: [22, 31, 48, 86, 154, 202, 214, 238, 260, 206, 88, 38], temp: [18.9, 20.1, 22.4, 25.3, 27.2, 28.3, 28.6, 28.3, 27.5, 25.6, 22.6, 19.8] },
    heat: [ { stage: '老椰现采', value: 260 }, { stage: '破壳分离', value: 390 }, { stage: '低温生榨', value: 620 }, { stage: 'HPP锁鲜', value: 860 }, { stage: '冷链分拨', value: 1120 } ],
    benchmark: [136, 128, 146, 132, 122],
    benchmarkLabels: ['鲜椰香', '乳化稳定', '微生物控制', '冷链温控', '复配表现'],
    flavorScores: [0.08, 0.12, 0.24, 0.14, 0.78, 0.36],
    flavorSummary: '鲜椰香与轻乳脂感并存，HPP冷杀菌避免高温熟化味，是咖啡和茶汤复配中的植物基清爽底色。',
    reports: [ { org: 'HPP 工艺验证留样', result: '600MPa压力批次记录完整', code: 'FS-WC-COC-2605-004' }, { org: '冷链微生物筛查', result: '菌落与霉酵母控制达标', code: 'FS-WC-COC-2605-009' } ]
  }
]

// 基础变量
const activeId = ref('pepper')
const dossier = computed(() => dossiers.find(item => item.id === activeId.value))
const provinceFeature = computed(() => chinaGeoJson.features.find(f => f.properties?.name === dossier.value.province))

// Refs
const climateChartEl = ref(null), heatChartEl = ref(null), standardRadarEl = ref(null), terrainMapEl = ref(null)
let climateChart, heatChart, standardRadar, terrainMap, originMarker

const cssVars = computed(() => ({
  '--theme-main': dossier.value.color,
  '--theme-accent': dossier.value.accent
}))

const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

function formatCoord(coord) { return `${coord[0].toFixed(4)}°E, ${coord[1].toFixed(4)}°N` }

function printDossier() {
  window.print()
}

// ================= ECharts 矢量化风格配置 =================
// 风格核心：细线、无背景、高通透感
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
      splitArea: { show: false }, // 去除雷达图默认的灰色填充
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

// ================= 地图逻辑 (精简底色融合) =================
function initTerrainMap() {
  if (terrainMap) return
  terrainMap = new maplibregl.Map({
    container: terrainMapEl.value,
    style: {
      version: 8,
      sources: { 'hyp-tiles': { type: 'raster', tiles: ['/tiles/raster/{z}/{x}/{y}.png'], tileSize: 256, maxzoom: 8 } },
      layers: [
        { id: 'bg', type: 'background', paint: { 'background-color': '#F4F3ED' } }, // 纸张底色
        { id: 'hyp', type: 'raster', source: 'hyp-tiles', paint: { 'raster-opacity': 0.6, 'raster-saturation': -0.8, 'raster-contrast': 0.1 } } // 降低底图干扰，呈现水墨/单色感
      ]
    },
    center: dossier.value.originPoint.coord, zoom: 6,
    interactive: true, dragRotate: false, pitchWithRotate: false // 允许平移缩放供B端查阅，但禁止旋转
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

  // 更新 Origin Marker (矢量靶心风格)
  if (originMarker) originMarker.remove()
  const el = document.createElement('div')
  el.className = 'vector-pinpoint'
  el.style.borderColor = dossier.value.color
  originMarker = new maplibregl.Marker({ element: el }).setLngLat(dossier.value.originPoint.coord).addTo(terrainMap)

  // 缩放至省份边界
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
/* ================= 核心架构 ================= */
.archive-atlas-page {
  position: fixed; top: var(--navbar-h); left: 0; right: 0; bottom: 0;
  background: #F4F3ED; /* 高级画册纸张底色 */
  color: #332F2A;
  display: grid;
  grid-template-columns: clamp(270px, 20vw, 320px) minmax(420px, 1fr) clamp(260px, 19vw, 300px); /* 三栏布局 */
  overflow: auto;
  font-family: -apple-system, "PingFang SC", sans-serif;
}

/* ================= 两侧信息列 ================= */
.atlas-sidebar {
  padding: clamp(20px, 2vw, 32px) clamp(18px, 1.8vw, 24px);
  overflow-y: auto;
  z-index: 10;
  display: flex; flex-direction: column; gap: 40px;
  background: rgba(244, 243, 237, 0.85); /* 半透明以融合地图边缘 */
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-right: 1px solid rgba(0,0,0,0.06);
}
.right-sidebar { border-right: none; border-left: 1px solid rgba(0,0,0,0.06); }

/* ================= 排版与字体 ================= */
.atlas-header h1 { font-family: "Noto Serif SC", "Songti SC", serif; font-size: 28px; margin: 4px 0 8px; color: #1A1815; font-weight: 600; letter-spacing: 2px; }
.atlas-header p { font-size: 12px; color: #666; line-height: 1.6; }
.kicker { font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--theme-main); font-weight: bold; }
.archive-actions button {
  width: 100%;
  border: 1px solid rgba(0,0,0,0.16);
  background: #1A1815;
  color: #F4F3ED;
  padding: 11px 14px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}
.archive-actions button:hover { background: var(--theme-main); border-color: var(--theme-main); }

/* ================= 标签页 (无框极简) ================= */
.product-tabs { display: flex; flex-wrap: wrap; gap: 10px 14px; border-bottom: 1px solid rgba(0,0,0,0.1); padding-bottom: 8px; }
.product-tabs button {
  background: none; border: none; padding: 0 0 6px 0; font-size: 15px; cursor: pointer;
  color: #888; position: relative; font-family: "Noto Serif SC", serif; transition: 0.3s;
}
.product-tabs button.active { color: var(--theme-main); font-weight: bold; }
.product-tabs button.active::after {
  content: ''; position: absolute; left: 0; right: 0; bottom: -9px;
  height: 2px; background: var(--theme-main);
}

/* ================= 数据区块 ================= */
.data-section { display: flex; flex-direction: column; }
.section-title { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }
.section-title h3 { font-size: 14px; font-weight: 600; letter-spacing: 1px; color: #222; margin: 0; }
.badge { font-size: 9px; font-family: monospace; border: 1px solid rgba(0,0,0,0.15); padding: 2px 6px; border-radius: 2px; color: #555; }
.badge.pass { background: rgba(81, 110, 88, 0.1); color: #516E58; border-color: #516E58; font-weight: bold; }
.section-desc { font-size: 11px; color: #777; margin: 0 0 12px 0; }
.chart-box { width: 100%; height: 200px; } /* ECharts 容器 */

/* ================= 中央地图舞台 ================= */
.atlas-center-map { position: relative; width: 100%; min-height: 100%; }
.terrain-map-layer { position: absolute; inset: 0; width: 100%; height: 100%; }

/* 地图上的悬浮统计条 */
.floating-metrics-strip {
  position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 32px; background: rgba(255,255,255,0.9);
  width: min(760px, calc(100% - 72px));
  padding: 20px 32px; border-radius: 4px; box-shadow: 0 12px 32px rgba(0,0,0,0.08);
  border: 1px solid rgba(0,0,0,0.05); z-index: 5;
}
.f-metric { display: flex; flex-direction: column; align-items: center; text-align: center; }
.fm-label { font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.fm-value { font-size: 20px; font-family: "Noto Serif SC", serif; font-weight: bold; color: var(--theme-main); margin-bottom: 2px; }
.fm-note { font-size: 10px; color: #999; }

/* 地图左上角节点摘要 */
.floating-map-legend {
  position: absolute; top: 24px; left: 24px; z-index: 5;
  background: rgba(255,255,255,0.85); padding: 16px; border: 1px solid rgba(0,0,0,0.08);
  backdrop-filter: blur(4px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-radius: 2px;
}
.origin-pin-info strong { display: block; font-size: 13px; color: var(--theme-main); }
.origin-pin-info span { font-size: 10px; color: #666; font-family: monospace; }
.node-timeline { margin-top: 16px; padding-top: 16px; border-top: 1px dashed rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 12px; }
.node-item { display: flex; gap: 8px; align-items: flex-start; }
.node-dot { width: 6px; height: 6px; border-radius: 50%; background: #ccc; margin-top: 4px; }
.node-item strong { display: block; font-size: 12px; color: #333; }
.node-item span { font-size: 10px; color: #888; }

/* 自定义 MapLibre Marker (十字准星风格) */
:deep(.vector-pinpoint) {
  width: 14px; height: 14px; border: 2px solid; border-radius: 50%;
  background: rgba(255,255,255,0.8); box-shadow: 0 0 0 4px rgba(255,255,255,0.4);
  position: relative;
}
:deep(.vector-pinpoint::after) {
  content: ''; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 4px; height: 4px; background: currentColor; border-radius: 50%;
}

/* ================= 右侧特殊区块 ================= */
.flavor-integration { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.flavor-summary { font-size: 12px; color: #555; line-height: 1.6; font-style: italic; text-align: center; background: rgba(0,0,0,0.03); padding: 12px; border-radius: 2px;}

.cert-grid { display: flex; flex-direction: column; gap: 12px; }
.cert-ticket {
  border: 1px solid rgba(0,0,0,0.1); padding: 12px; border-radius: 2px;
  background: url('data:image/svg+xml;utf8,<svg width="4" height="4" viewBox="0 0 4 4" xmlns="http://www.w3.org/2000/svg"><rect width="4" height="4" fill="none"/><circle cx="2" cy="2" r="0.5" fill="%23000" fill-opacity="0.05"/></svg>');
}
.cert-org { font-size: 10px; color: #777; margin-bottom: 4px; }
.cert-result { font-size: 13px; font-weight: bold; color: #222; margin-bottom: 6px; }
.cert-code { font-size: 10px; font-family: monospace; color: #aaa; }

/* ================= 响应式调整 ================= */
@media (max-width: 1439px), (max-height: 800px) {
  .archive-atlas-page { grid-template-columns: 260px minmax(380px, 1fr) 250px; }
  .floating-metrics-strip { flex-wrap: wrap; justify-content: center; width: 80%; padding: 16px; gap: 16px; bottom: 20px; }
}
@media (max-height: 760px) {
  .archive-atlas-page { min-height: 720px; }
}
@media (max-width: 860px) {
  .archive-atlas-page { grid-template-columns: 1fr; overflow-y: auto; position: static; height: auto; display: flex; flex-direction: column; }
  .atlas-center-map { height: 50vh; min-height: 400px; order: -1; }
  .atlas-sidebar { border: none; padding: 20px; }
}

@media print {
  @page { size: A4 landscape; margin: 10mm; }

  body { background: #fff !important; }
  .archive-atlas-page {
    position: static !important;
    display: grid !important;
    grid-template-columns: 260px 1fr 260px !important;
    height: auto !important;
    min-height: auto !important;
    overflow: visible !important;
    background: #fff !important;
    color: #111 !important;
  }
  .atlas-sidebar {
    height: auto !important;
    overflow: visible !important;
    padding: 14px !important;
    gap: 18px !important;
    background: #fff !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
  }
  .archive-actions,
  .product-tabs,
  .terrain-map-layer,
  :global(.navbar) {
    display: none !important;
  }
  .atlas-center-map {
    min-height: 560px !important;
    height: auto !important;
    border-left: 1px solid #ddd;
    border-right: 1px solid #ddd;
  }
  .floating-metrics-strip,
  .floating-map-legend {
    position: static !important;
    transform: none !important;
    box-shadow: none !important;
    background: #fff !important;
    margin: 12px !important;
  }
  .floating-metrics-strip {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    width: auto !important;
    gap: 12px !important;
    padding: 12px !important;
  }
  .chart-box { height: 150px !important; }
  .atlas-header h1 { font-size: 22px !important; }
}
</style>
