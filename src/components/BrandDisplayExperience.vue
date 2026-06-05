<template>
  <article class="brand-display-experience" :class="{ framed, fullscreen }" :style="rootStyle">
    <div ref="mapContainer" class="display-map">
      <div v-if="!mapReady" class="display-loading">
        <span class="loader-ring" />
        初始化品牌空间演示...
      </div>
    </div>

    <div class="hud-layer" :class="{ touring: isTouring }">
      <header class="hud-top">
        <div class="title-block">
          <span class="hud-kicker">FLAVORSCAPE BRAND DISPLAY</span>
          <h1>{{ displayData.title }}</h1>
          <p>{{ displayData.subtitle }}</p>
        </div>
        <div class="top-actions">
          <div v-if="routeOptions.length" class="route-switch">
            <button
              v-for="route in routeOptions"
              :key="route.id"
              type="button"
              :class="{ active: route.id === displayData.selectedRouteId }"
              @click="$emit('select-route', route.id)"
            >
              {{ route.name }}
            </button>
          </div>
          <button type="button" class="tour-btn" :class="{ active: isTouring }" @click="toggleTour">
            {{ isTouring ? '停止巡航' : '开启巡航' }}
          </button>
        </div>
      </header>

      <aside class="hud-panel product-panel">
        <span class="hud-kicker">Product Asset</span>
        <h2>{{ displayData.brandName || displayData.productName }}</h2>
        <p>{{ displayData.caption }}</p>
        <div class="identity-grid">
          <div>
            <span>核心产区</span>
            <strong>{{ displayData.origin }}</strong>
          </div>
          <div>
            <span>品类场景</span>
            <strong>{{ displayData.brandScenario || displayData.category }}</strong>
          </div>
        </div>
        <div v-if="displayData.spatial?.evidence?.length" class="metric-grid">
          <div v-for="item in displayData.spatial.evidence.slice(0, 3)" :key="item.label">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </aside>

      <aside class="hud-panel timeline-panel">
        <span class="hud-kicker">Spread Timeline</span>
        <h2>{{ routeData?.name || '传播路径' }}</h2>
        <p>{{ routeData?.summary || displayData.caption }}</p>
        <div v-if="routeTimeline.length && displayData.showTimeline !== false" class="timeline-track">
          <button
            v-for="(event, index) in routeTimeline.slice(0, 7)"
            :key="eventKey(event, index)"
            type="button"
            :class="{ active: eventKey(event, index) === selectedKey }"
            @click="selectEvent(event, index)"
          >
            <span>{{ formatYear(event.year) }} · {{ event.dynasty || event.event_type }}</span>
            <strong>{{ event.location }}</strong>
          </button>
        </div>
        <div v-else class="panel-empty">
          当前资产包没有可投影的路线时间线。
        </div>
      </aside>

      <aside v-if="spatialNotice" class="hud-panel spatial-status-panel">
        <span class="hud-kicker">Asset Spatial Data</span>
        <h2>空间数据待补齐</h2>
        <p>{{ spatialNotice }}</p>
        <div v-if="unmappedNodes.length" class="unmapped-list">
          <div v-for="item in unmappedNodes" :key="item.name">
            <strong>{{ item.name }}</strong>
            <span>{{ item.reason }}</span>
          </div>
        </div>
      </aside>

      <footer class="subtitle-dock">
        <transition name="fade-slide" mode="out-in">
          <div :key="focusKey" class="subtitle-content">
            <div class="subtitle-meta">
              <span :style="{ color: accentColor }">{{ focusMeta }}</span>
              <span>{{ focusCoord }}</span>
            </div>
            <h3>{{ focusTitle }}</h3>
            <p>{{ focusDescription }}</p>
          </div>
        </transition>
      </footer>

      <svg class="route-overlay" aria-hidden="true">
        <path v-if="projectedRoutePath" :d="projectedRoutePath" class="route-line" />
        <path v-if="projectedProductPath" :d="projectedProductPath" class="product-line" />
      </svg>

      <button
        v-for="point in projectedRoutePoints"
        :key="point.key"
        type="button"
        class="map-target route-target"
        :class="{ active: point.key === selectedKey }"
        :style="{ left: `${point.x}px`, top: `${point.y}px`, '--node-color': accentColor }"
        @click="selectProjectedPoint(point)"
      >
        <span class="radar-ping" />
        <span class="core-dot" />
        <span v-if="point.key === selectedKey" class="target-label">{{ point.label }}</span>
      </button>

      <button
        v-for="point in projectedProductPoints"
        :key="point.key"
        type="button"
        class="map-target product-target"
        :style="{ left: `${point.x}px`, top: `${point.y}px`, '--node-color': productColor }"
        @click="flyTo(point.coord)"
      >
        <span class="core-dot" />
        <span class="target-label">{{ point.label }}</span>
      </button>
    </div>
  </article>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { routeEventKey } from '../composables/useSpreadRoutes'
import { createMap, removeMap } from '../map/maplibre.js'
import { createHypRasterStyle } from '../map/mapStyle.js'

const props = defineProps({
  displayData: { type: Object, required: true },
  routeData: { type: Object, default: null },
  routeOptions: { type: Array, default: () => [] },
  scale: { type: Number, default: 1 },
  framed: { type: Boolean, default: false },
  fullscreen: { type: Boolean, default: false },
})

const emit = defineEmits(['select-event', 'select-route'])

const mapContainer = ref(null)
const mapReady = ref(false)
const projectedRoutePoints = ref([])
const projectedProductPoints = ref([])
const projectedRoutePath = ref('')
const projectedProductPath = ref('')
const isTouring = ref(false)
let map = null
let tourTimer = null

const MAP_STYLE = createHypRasterStyle({
  backgroundLayerId: 'trace-bg',
  backgroundColor: '#05090d',
  rasterPaint: {
    'raster-saturation': -0.82,
    'raster-contrast': 0.34,
    'raster-brightness-min': 0.08,
    'raster-opacity': 0.82,
  },
})

const rootStyle = computed(() => props.framed ? {
  width: '1280px',
  height: '720px',
  transform: `scale(${props.scale})`,
  transformOrigin: 'top left',
} : {})

const routeTimeline = computed(() =>
  [...(props.routeData?.timeline || [])]
    .filter(event => Array.isArray(event.coordinates))
    .sort((a, b) => Number(a.year || 0) - Number(b.year || 0))
)
const productNodes = computed(() => props.displayData.spatial?.nodes || [])
const unmappedNodes = computed(() => props.displayData.spatial?.unmappedNodes || [])
const accentColor = computed(() => props.routeData?.color || props.displayData.colors?.accent || '#b8d46c')
const productColor = computed(() => props.displayData.colors?.primary || '#78a6b8')
const selectedKey = computed(() => {
  if (props.displayData.selectedEventKey) return props.displayData.selectedEventKey
  const first = routeTimeline.value[0]
  return first ? eventKey(first, 0) : ''
})
const selectedEvent = computed(() => {
  const index = routeTimeline.value.findIndex((event, i) => eventKey(event, i) === selectedKey.value)
  return index >= 0 ? routeTimeline.value[index] : routeTimeline.value[0]
})
const focusKey = computed(() => selectedKey.value || props.displayData.projectId || props.displayData.productName)
const focusTitle = computed(() => selectedEvent.value?.location || props.displayData.productName)
const focusMeta = computed(() => selectedEvent.value ? `${formatYear(selectedEvent.value.year)} · ${selectedEvent.value.event_type || '传播节点'}` : props.displayData.category)
const focusDescription = computed(() => selectedEvent.value?.route || selectedEvent.value?.notes || props.displayData.caption)
const focusCoord = computed(() => {
  const coord = selectedEvent.value?.coordinates || productNodes.value[0]?.coord
  if (!Array.isArray(coord)) return props.displayData.origin || ''
  return `${Math.abs(coord[1]).toFixed(3)}N, ${Math.abs(coord[0]).toFixed(3)}E`
})
const spatialNotice = computed(() => {
  if (!props.displayData.needsSpatialData && (productNodes.value.length || routeTimeline.value.length)) return ''
  if (props.displayData.sourceAsset) {
    return '这是 DeepSeek 资产包项目。系统未使用默认案例地图；需要在资产包中补充 map_nodes 或 routes/timeline 的经纬度后，地图才会显示真实节点和路线。'
  }
  return ''
})

function eventKey(event, index) {
  return routeEventKey(event, index)
}

function formatYear(year) {
  if (year === null || year === undefined || Number.isNaN(Number(year))) return '未知年代'
  const numeric = Number(year)
  return numeric < 0 ? `公元前${Math.abs(numeric)}` : `${numeric}`
}

function buildPath(points, bend = 0.18) {
  if (!map || points.length < 2) return ''
  const projected = []
  for (let i = 0; i < points.length - 1; i += 1) {
    const [x1, y1] = points[i]
    const [x2, y2] = points[i + 1]
    const cx = (x1 + x2) / 2 - (y2 - y1) * bend
    const cy = (y1 + y2) / 2 + (x2 - x1) * bend * 0.42
    for (let step = 0; step < 18; step += 1) {
      const t = step / 17
      const mt = 1 - t
      const coord = [
        mt * mt * x1 + 2 * mt * t * cx + t * t * x2,
        mt * mt * y1 + 2 * mt * t * cy + t * t * y2,
      ]
      projected.push(map.project(coord))
    }
  }
  return projected.map((p, index) => `${index === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
}

function updateProjection() {
  if (!map) return
  projectedRoutePoints.value = routeTimeline.value.map((event, index) => {
    const point = map.project(event.coordinates)
    return {
      key: eventKey(event, index),
      label: event.location,
      coord: event.coordinates,
      event,
      x: point.x,
      y: point.y,
    }
  })
  projectedProductPoints.value = productNodes.value
    .filter(node => Array.isArray(node.coord))
    .map((node, index) => {
      const point = map.project(node.coord)
      return {
        key: `product-${index}-${node.short}`,
        label: node.short,
        coord: node.coord,
        x: point.x,
        y: point.y,
      }
    })
  projectedRoutePath.value = buildPath(routeTimeline.value.map(event => event.coordinates), 0.2)
  projectedProductPath.value = buildPath(productNodes.value.map(node => node.coord).filter(Boolean), -0.1)
}

function flyTo(coord, duration = 1700) {
  if (!map || !Array.isArray(coord)) return
  map.flyTo({
    center: coord,
    zoom: Math.abs(coord[0]) > 125 ? 4.5 : 5.4,
    pitch: 58,
    bearing: -10,
    duration,
    essential: true,
  })
}

function selectEvent(event, index) {
  const key = eventKey(event, index)
  emit('select-event', key)
  flyTo(event.coordinates)
}

function selectProjectedPoint(point) {
  emit('select-event', point.key)
  flyTo(point.coord)
}

function toggleTour() {
  if (isTouring.value) stopTour()
  else startTour()
}

function startTour() {
  if (!routeTimeline.value.length) return
  isTouring.value = true
  let index = Math.max(0, routeTimeline.value.findIndex((event, i) => eventKey(event, i) === selectedKey.value))
  tourTimer = window.setInterval(() => {
    index = (index + 1) % routeTimeline.value.length
    selectEvent(routeTimeline.value[index], index)
  }, 6000)
}

function stopTour() {
  isTouring.value = false
  if (tourTimer) window.clearInterval(tourTimer)
  tourTimer = null
}

function initMap() {
  if (map || !mapContainer.value) return
  map = createMap({
    container: mapContainer.value,
    style: MAP_STYLE,
    center: [104, 32],
    zoom: 3.9,
    pitch: 54,
    bearing: -12,
    antialias: true,
    attributionControl: false,
  })
  map.on('load', () => {
    mapReady.value = true
    updateProjection()
    const first = selectedEvent.value?.coordinates || productNodes.value[0]?.coord
    if (first) flyTo(first, 900)
  })
  map.on('move', updateProjection)
  map.on('resize', updateProjection)
}

watch(
  () => [props.routeData, props.displayData?.selectedRouteId, props.displayData?.selectedEventKey, productNodes.value.length],
  async () => {
    stopTour()
    await nextTick()
    updateProjection()
    const coord = selectedEvent.value?.coordinates
    if (coord) flyTo(coord, 900)
  }
)

onMounted(() => nextTick(initMap))
onUnmounted(() => {
  stopTour()
  removeMap(map)
  map = null
})
</script>

<style scoped>
.brand-display-experience {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #05090d;
  color: #f8fafc;
}

.brand-display-experience.fullscreen {
  position: fixed;
  top: var(--navbar-h);
  left: 0;
  right: 0;
  bottom: 0;
  height: auto;
}

.brand-display-experience.framed {
  box-shadow: 0 38px 80px rgba(0, 0, 0, 0.26);
}

.brand-display-experience.framed .hud-top {
  padding: 30px 42px;
}

.display-map {
  position: absolute;
  inset: 0;
}

.display-loading {
  position: absolute;
  inset: 0;
  z-index: 6;
  display: grid;
  place-items: center;
  gap: 12px;
  background: #05090d;
  color: rgba(255, 255, 255, 0.68);
  font-size: 13px;
  letter-spacing: 0.08em;
}

.loader-ring {
  width: 34px;
  height: 34px;
  border: 2px solid rgba(255, 255, 255, 0.16);
  border-top-color: rgba(255, 255, 255, 0.74);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.hud-layer {
  position: absolute;
  inset: 0;
  z-index: 10;
  pointer-events: none;
}

.hud-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  padding: 32px 44px;
  pointer-events: none;
}

.title-block {
  min-width: 0;
}

.hud-kicker {
  display: block;
  color: rgba(255, 255, 255, 0.48);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

h1,
h2,
h3,
p {
  margin: 0;
}

h1 {
  margin-top: 7px;
  font-family: var(--font-serif);
  font-size: 34px;
  font-weight: 500;
  letter-spacing: 0.04em;
}

.title-block p {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.64);
  font-size: 13px;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  pointer-events: auto;
}

.route-switch {
  display: flex;
  gap: 4px;
  max-width: 520px;
  padding: 4px;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
}

.route-switch button,
.tour-btn {
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: rgba(255, 255, 255, 0.62);
  cursor: pointer;
  white-space: nowrap;
  transition: background 180ms ease, color 180ms ease, border-color 180ms ease;
}

.route-switch button {
  padding: 7px 13px;
  font-size: 12px;
}

.route-switch button.active {
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
}

.tour-btn {
  height: 34px;
  padding: 0 15px;
  border: 1px solid rgba(255, 255, 255, 0.24);
  font-size: 12px;
}

.tour-btn.active,
.tour-btn:hover {
  border-color: rgba(255, 255, 255, 0.46);
  color: #fff;
}

.hud-panel {
  position: absolute;
  z-index: 18;
  width: 292px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 8px;
  background: rgba(8, 13, 18, 0.46);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 22px 46px rgba(0, 0, 0, 0.38);
  pointer-events: auto;
  transition: opacity 300ms ease;
}

.touring .hud-panel {
  opacity: 0.7;
}

.product-panel {
  top: 128px;
  left: 44px;
  padding: 20px;
}

.timeline-panel {
  top: 128px;
  right: 44px;
  bottom: 230px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.spatial-status-panel {
  left: 44px;
  bottom: 170px;
  padding: 18px;
}

.hud-panel h2 {
  margin-top: 8px;
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 500;
  color: #e6e0d4;
}

.hud-panel p {
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.64);
  font-size: 13px;
  line-height: 1.65;
}

.identity-grid,
.metric-grid {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.identity-grid div,
.metric-grid div {
  display: grid;
  gap: 4px;
}

.identity-grid span,
.metric-grid span,
.timeline-track span {
  color: rgba(255, 255, 255, 0.43);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.identity-grid strong,
.metric-grid strong {
  color: rgba(255, 255, 255, 0.78);
  font-size: 13px;
  font-weight: 500;
}

.metric-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.timeline-track {
  display: grid;
  gap: 8px;
  margin-top: 16px;
  min-height: 0;
  overflow-y: auto;
  padding-right: 3px;
}

.timeline-track button {
  display: grid;
  gap: 3px;
  width: 100%;
  min-height: 44px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.045);
  color: rgba(255, 255, 255, 0.74);
  cursor: pointer;
  padding: 8px 10px;
  text-align: left;
  transition: background 180ms ease, border-color 180ms ease;
}

.timeline-track button.active,
.timeline-track button:hover {
  border-color: color-mix(in srgb, v-bind(accentColor) 48%, rgba(255,255,255,0.18));
  background: rgba(255, 255, 255, 0.1);
}

.timeline-track strong {
  font-size: 14px;
  font-weight: 500;
}

.panel-empty {
  margin-top: 16px;
  border: 1px dashed rgba(255, 255, 255, 0.14);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  line-height: 1.55;
  padding: 10px;
}

.unmapped-list {
  display: grid;
  gap: 7px;
  margin-top: 12px;
}

.unmapped-list div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 7px;
}

.unmapped-list strong,
.unmapped-list span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unmapped-list strong {
  color: rgba(255, 255, 255, 0.78);
  font-size: 12px;
  font-weight: 500;
}

.unmapped-list span {
  color: rgba(255, 255, 255, 0.45);
  font-size: 11px;
}

.subtitle-dock {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  padding: 64px 44px 38px;
  background: linear-gradient(180deg, rgba(5, 9, 13, 0) 0%, rgba(5, 9, 13, 0.62) 100%);
  text-align: center;
}

.subtitle-content {
  max-width: 780px;
}

.subtitle-meta {
  display: flex;
  justify-content: center;
  gap: 16px;
  color: rgba(255, 255, 255, 0.46);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.subtitle-content h3 {
  margin-top: 12px;
  font-family: var(--font-serif);
  font-size: 32px;
  font-weight: 500;
  color: #fff;
}

.subtitle-content p {
  margin-top: 12px;
  color: rgba(255, 255, 255, 0.72);
  font-size: 15px;
  line-height: 1.8;
}

.route-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.route-line,
.product-line {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.route-line {
  stroke: v-bind(accentColor);
  stroke-width: 2.4;
  stroke-dasharray: 7 10;
  filter: drop-shadow(0 0 8px color-mix(in srgb, v-bind(accentColor) 68%, transparent));
  animation: dash 12s linear infinite;
}

.product-line {
  stroke: rgba(255, 255, 255, 0.22);
  stroke-width: 1.4;
}

.map-target {
  position: absolute;
  z-index: 19;
  width: 56px;
  height: 56px;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: #fff;
  cursor: pointer;
  pointer-events: auto;
  transform: translate(-50%, -50%);
}

.product-target {
  width: 42px;
  height: 42px;
  opacity: 0.78;
}

.radar-ping {
  position: absolute;
  inset: 8px;
  border: 1px solid color-mix(in srgb, var(--node-color) 72%, transparent);
  border-radius: 50%;
  animation: ping 2.4s ease-out infinite;
}

.core-dot {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--node-color) 72%, white);
  box-shadow: 0 0 16px color-mix(in srgb, var(--node-color) 70%, transparent);
  transform: translate(-50%, -50%);
}

.map-target.active .core-dot {
  width: 13px;
  height: 13px;
}

.target-label {
  position: absolute;
  left: 50%;
  top: -18px;
  padding: 4px 8px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.54);
  color: rgba(255, 255, 255, 0.86);
  font-size: 11px;
  white-space: nowrap;
  transform: translateX(-50%);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes ping {
  0% { opacity: 0.8; transform: scale(0.75); }
  100% { opacity: 0; transform: scale(1.8); }
}

@keyframes dash {
  to { stroke-dashoffset: -160; }
}
</style>
