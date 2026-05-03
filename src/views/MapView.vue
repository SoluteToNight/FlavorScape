<template>
  <div class="map-page">
    <div ref="mapContainer" class="map-container" />

    <!-- Left: layer legend -->
    <div class="left-panel glass-panel">
      <div class="panel-section-label">图层</div>
      <div class="layer-rows">
        <div v-for="lr in layerLegend" :key="lr.label" class="layer-row" :class="{ dimmed: lr.dimmed }">
          <span class="layer-icon" :style="lr.style" />
          <span class="layer-label">{{ lr.label }}</span>
        </div>
      </div>
      <div class="panel-section-label toggle-section-label">开关</div>
      <div class="layer-toggles" role="group" aria-label="图层开关">
        <button
          v-for="toggle in layerToggles"
          :key="toggle.key"
          type="button"
          class="layer-toggle"
          :class="{ active: toggle.enabled, context: toggle.contextual }"
          :aria-pressed="toggle.enabled"
          @click="toggleLayer(toggle.key)"
        >
          <span class="toggle-name">{{ toggle.label }}</span>
          <span class="toggle-indicator" :class="{ on: toggle.enabled }" aria-hidden="true" />
        </button>
      </div>
      <div class="toggle-hint">L2 受上下文触发；开关用于允许/禁止该层参与显示。</div>
      <div v-if="!rasterReady" class="loading-hint">
        <span class="loading-dot" />底图加载中…
      </div>
    </div>

    <!-- Right: inspector panel -->
    <MapInspector />

    <!-- Hover tooltip -->
    <div
      v-if="tooltip.visible"
      class="map-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >{{ tooltip.text }}</div>

    <!-- Bottom hint -->
    <div class="map-hint">点击节点或生态区边界探索 · 滚轮缩放</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAppStore } from '../stores/app.js'
import MapInspector from '../components/MapInspector.vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { MapboxOverlay } from '@deck.gl/mapbox'
import { PathLayer, ScatterplotLayer } from '@deck.gl/layers'
import { TripsLayer } from '@deck.gl/geo-layers'
import { PathStyleExtension } from '@deck.gl/extensions'

const mapContainer = ref(null)
const appStore = useAppStore()
const tooltip = ref({ visible: false, x: 0, y: 0, text: '' })
const rasterReady = ref(false)

// ── Layer visibility model (L0 physical / L1 ecoregion / L2 routes / L3 nodes) ─
const L1_OPACITY_WEAK   = 0.35   // default: visible but subtle
const L1_OPACITY_STRONG = 0.85   // context: ecozone selected

const contextLayerVisibility = computed(() => appStore.layerVisibility)
const layerEnabled = computed(() => appStore.layerEnabled)
const layerVisibility = computed(() => ({
  L0: layerEnabled.value.L0 && contextLayerVisibility.value.L0,
  L1: layerEnabled.value.L1 && contextLayerVisibility.value.L1,
  L2: layerEnabled.value.L2 && contextLayerVisibility.value.L2,
  L3: layerEnabled.value.L3 && contextLayerVisibility.value.L3,
}))

let map = null, deckOverlay = null, animId = null
let currentTime = 0
let flavors = [], routes = []

const LOOP_LENGTH = 1800
const ANIMATION_SPEED = 1

// ── MapLibre inline style — uses our Python raster tiles ──────────────────
const MAP_STYLE = {
  version: 8,
  sources: {
    'hyp-tiles': {
      type: 'raster',
      tiles: ['/tiles/raster/{z}/{x}/{y}.png'],
      tileSize: 256,
      minzoom: 0,
      maxzoom: 8,
      attribution: '© Natural Earth',
    },
  },
  layers: [
    // Ocean background (shown before raster tiles arrive)
    { id: 'bg', type: 'background', paint: { 'background-color': '#C8DDE8' } },
    {
      id: 'hyp',
      type: 'raster',
      source: 'hyp-tiles',
      paint: {
        'raster-saturation': -0.12,   // slightly desaturate for museum aesthetic
        'raster-brightness-min': 0.04,
        'raster-opacity': 1,
      },
    },
  ],
}

// ── Helpers ───────────────────────────────────────────────────────────────
function hexToRgb(hex, a = 255) {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
    a,
  ]
}

function buildTripData(routeList) {
  const trips = []
  routeList.forEach((route, ri) => {
    for (let p = 0; p < 3; p++) {
      const start = (ri * 360 + p * (LOOP_LENGTH / 3)) % LOOP_LENGTH
      trips.push({
        path: route.path,
        timestamps: route.path.map((_, j) => start + (j / (route.path.length - 1)) * 900),
        color: hexToRgb(route.color, 250),
      })
    }
  })
  return trips
}

function buildLayers(time, flavorList, routeList, vis) {
  const layers = []

  // L2 — route path + animated trips (hidden by default, shown on context)
  if (vis.L2) {
    layers.push(
      new PathLayer({
        id: 'path-layer',
        data: routeList,
        getPath: d => d.path,
        getColor: d => hexToRgb(d.color, 180),
        getWidth: 2,
        widthUnits: 'pixels',
        pickable: true,
        extensions: [new PathStyleExtension({ dash: true })],
        getDashArray: d => d.type === 'sea' ? [6, 3] : [0, 0],
        dashJustified: true,
        onHover: ({ object, x, y }) => {
          tooltip.value = object
            ? { visible: true, x: x + 14, y: y - 8, text: object.name }
            : { ...tooltip.value, visible: false }
        },
        onClick: ({ object }) => { if (object) appStore.selectRoute(object) },
      }),
      new TripsLayer({
        id: 'trips-layer',
        data: buildTripData(routeList),
        getPath: d => d.path,
        getTimestamps: d => d.timestamps,
        getColor: d => d.color,
        opacity: 1.0,
        widthMinPixels: 3,
        rounded: true,
        trailLength: 180,
        currentTime: time,
      }),
    )
  }

  // L3 — flavor nodes (visible by default, independently controllable)
  if (vis.L3) {
    layers.push(
      new ScatterplotLayer({
        id: 'scatter-layer',
        data: flavorList,
        getPosition: d => d.coordinates,
        getRadius: 12000,
        radiusUnits: 'meters',
        getFillColor: d => hexToRgb(d.color, 240),
        getLineColor: [255, 253, 250, 255],
        lineWidthMinPixels: 2,
        stroked: true,
        pickable: true,
        onHover: ({ object, x, y }) => {
          tooltip.value = object
            ? { visible: true, x: x + 14, y: y - 8, text: `${object.city} · ${object.primary[0]} ${object.vals[0].toFixed(2)}` }
            : { ...tooltip.value, visible: false }
        },
        onClick: ({ object }) => { if (object) appStore.selectNode(object) },
      }),
    )
  }

  return layers
}

function startAnimation() {
  function frame() {
    currentTime = (currentTime + ANIMATION_SPEED) % LOOP_LENGTH
    deckOverlay?.setProps({ layers: buildLayers(currentTime, flavors, routes, layerVisibility.value) })
    animId = requestAnimationFrame(frame)
  }
  frame()
}

// ── Add vector layers from Python backend ─────────────────────────────────
async function addVectorLayers() {
  // L0 — coastline & rivers (GeoJSON, loaded once)
  const physLayers = [
    { id: 'coastline', url: '/tiles/vector/coastline', type: 'line', paint: { 'line-color': '#8A7560', 'line-width': 0.6, 'line-opacity': 0.65 } },
    { id: 'rivers',    url: '/tiles/vector/rivers',    type: 'line', paint: { 'line-color': '#5BA0B8', 'line-width': 0.4, 'line-opacity': 0.6 } },
  ]
  for (const layer of physLayers) {
    try {
      map.addSource(layer.id, { type: 'geojson', data: layer.url })
      map.addLayer({ id: layer.id, type: layer.type, source: layer.id, paint: layer.paint })
    } catch (err) {
      console.warn(`Vector layer [${layer.id}] skipped:`, err.message)
    }
  }

  // L1 — WWF TEOW ecoregions via GeoJSON (stable; MVT endpoint ready at /tiles/mvt/)
  try {
    map.addSource('ecoregions', { type: 'geojson', data: '/tiles/vector/ecoregions' })
    map.addLayer({
      id: 'ecoregions',
      type: 'line',
      source: 'ecoregions',
      paint: { 'line-color': '#6B4825', 'line-width': 1.4, 'line-opacity': L1_OPACITY_WEAK },
    })
  } catch (err) {
    console.warn('ecoregions skipped:', err.message)
  }

  // Click on ecoregion boundary → L1 inspector
  map.on('click', 'ecoregions', e => {
    const props = e.features?.[0]?.properties
    if (props) appStore.selectEcozone(props)
  })
  map.on('mouseenter', 'ecoregions', () => { map.getCanvas().style.cursor = 'pointer' })
  map.on('mouseleave', 'ecoregions', () => { map.getCanvas().style.cursor = '' })
}

// ── Lifecycle ─────────────────────────────────────────────────────────────
onMounted(async () => {
  const [fRes, rRes] = await Promise.all([fetch('/api/flavors'), fetch('/api/routes')])
  flavors = await fRes.json()
  routes  = await rRes.json()
  appStore.setFlavors(flavors)

  // Check if raster is ready (might still be extracting on first run)
  fetch('/tiles/status').then(r => r.json()).then(s => {
    rasterReady.value = s.raster_ready
  })

  map = new maplibregl.Map({
    container: mapContainer.value,
    style: MAP_STYLE,
    center: [100, 35],
    zoom: 3.5,
    pitch: 20,
    attributionControl: false,
  })

  map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right')
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right')

  map.on('load', async () => {
    rasterReady.value = true

    // Deck.gl overlay
    deckOverlay = new MapboxOverlay({
      interleaved: true,
      layers: buildLayers(0, flavors, routes, layerVisibility.value),
      getCursor: ({ isHovering }) => (isHovering ? 'pointer' : 'grab'),
    })
    map.addControl(deckOverlay)
    startAnimation()

    // Vector layers from Python backend (non-blocking)
    addVectorLayers()
    syncBaseLayerState()
    syncEcoregionState()
  })
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  map?.remove()
})

// ── L1 MapLibre paint helper ───────────────────────────────────────────────
function setL1Strength(opacity) {
  if (!map) return
  try {
    map.setPaintProperty('ecoregions', 'line-opacity', opacity)
    map.setPaintProperty('ecoregions', 'line-width', opacity > 0.5 ? 1.8 : 1.4)
  } catch (_) { /* ecoregions layer may not be added yet */ }
}

function setMapLayerVisibility(id, visible) {
  if (!map) return
  try {
    map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none')
  } catch (_) { /* layer may not be added yet */ }
}

function syncBaseLayerState() {
  const showL0 = layerVisibility.value.L0
  setMapLayerVisibility('bg', showL0)
  setMapLayerVisibility('hyp', showL0)
  setMapLayerVisibility('coastline', showL0)
  setMapLayerVisibility('rivers', showL0)
}

function syncEcoregionState() {
  const showL1 = layerVisibility.value.L1
  setMapLayerVisibility('ecoregions', showL1)
  if (showL1) {
    setL1Strength(appStore.l1Emphasis ? L1_OPACITY_STRONG : L1_OPACITY_WEAK)
  }
}

function toggleLayer(layer) {
  appStore.setLayerEnabled(layer, !layerEnabled.value[layer])
}

// ── Context-driven visibility watchers ─────────────────────────────────────
watch(() => [appStore.selectedNode, appStore.selectedRoute, appStore.selectedEcozone], ([node, route]) => {
  // Node flyTo (preserves original behavior)
  if (node && map) {
    map.flyTo({ center: node.coordinates, zoom: 5.5, duration: 1200, essential: true })
  }

  // Route flyTo — zoom to route bounds
  if (route && map && route.path?.length) {
    const bounds = route.path.reduce(
      (b, p) => b.extend(p),
      new maplibregl.LngLatBounds(route.path[0], route.path[0]),
    )
    map.fitBounds(bounds, { padding: 80, duration: 1200, essential: true })
  }

})

watch(
  () => [layerVisibility.value.L0, layerVisibility.value.L1, layerVisibility.value.L2, layerVisibility.value.L3, appStore.l1Emphasis],
  () => {
    syncBaseLayerState()
    syncEcoregionState()
    deckOverlay?.setProps({ layers: buildLayers(currentTime, flavors, routes, layerVisibility.value) })
  },
  { immediate: true },
)

const layerLegend = computed(() => [
  { label: 'HYP 自然地形底图',  dimmed: !layerVisibility.value.L0, style: { width: '14px', height: '8px', background: 'linear-gradient(to right, #7BAA6B, #C8A46A, #8BA8C0)', borderRadius: '2px', display: 'inline-block', opacity: layerVisibility.value.L0 ? 1 : 0.2 } },
  { label: '海岸线',            dimmed: !layerVisibility.value.L0, style: { width: '20px', height: '1px', background: '#9E8870', display: 'inline-block', opacity: layerVisibility.value.L0 ? 1 : 0.2 } },
  { label: '主干水系',          dimmed: !layerVisibility.value.L0, style: { width: '20px', height: '1px', background: '#7AAEC0', display: 'inline-block', opacity: layerVisibility.value.L0 ? 1 : 0.2 } },
  { label: 'L1 生态区边界',     dimmed: !layerVisibility.value.L1, style: { width: '20px', height: '1.2px', background: '#7A5530', display: 'inline-block', opacity: !layerVisibility.value.L1 ? 0.15 : (appStore.l1Emphasis ? L1_OPACITY_STRONG : L1_OPACITY_WEAK) } },
  { label: '陆路传播',          dimmed: !layerVisibility.value.L2, style: { width: '20px', height: '1px', background: 'var(--amber)', display: 'inline-block', opacity: layerVisibility.value.L2 ? 0.85 : 0.25 } },
  { label: '越洋传播',          dimmed: !layerVisibility.value.L2, style: { width: '20px', height: '0', display: 'inline-block', borderTop: '1px dashed var(--amber)', opacity: layerVisibility.value.L2 ? 0.85 : 0.25 } },
  { label: '流光粒子',          dimmed: !layerVisibility.value.L2, style: { width: '8px', height: '8px', borderRadius: '50%', background: 'var(--amber)', display: 'inline-block', opacity: layerVisibility.value.L2 ? 1 : 0.25 } },
  { label: '风味节点',          dimmed: !layerVisibility.value.L3, style: { width: '8px', height: '8px', borderRadius: '50%', background: 'var(--carmine)', display: 'inline-block', opacity: layerVisibility.value.L3 ? 0.8 : 0.2 } },
])

const layerToggles = computed(() => [
  { key: 'L0', label: 'L0 底图', enabled: layerEnabled.value.L0, contextual: false },
  { key: 'L1', label: 'L1 区划', enabled: layerEnabled.value.L1, contextual: false },
  { key: 'L2', label: 'L2 路径', enabled: layerEnabled.value.L2, contextual: true },
  { key: 'L3', label: 'L3 节点', enabled: layerEnabled.value.L3, contextual: false },
])
</script>

<style scoped>
.map-page { position: fixed; inset: 0; background: #C8DDE8; }
.map-container { position: absolute; inset: 0; width: 100%; height: 100%; }

:deep(.maplibregl-canvas) { outline: none; }
:deep(.maplibregl-ctrl-attrib) {
  background: rgba(255,252,248,0.7) !important;
  border-radius: 4px !important;
  font-size: 10px !important;
}
:deep(.maplibregl-ctrl-group) {
  background: var(--glass) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 8px !important;
  box-shadow: var(--shadow-sm) !important;
  backdrop-filter: var(--blur-sm) !important;
  margin-bottom: 28px !important;
  margin-right: 300px !important; /* keep clear of inspector */
}

.left-panel {
  position: absolute;
  top: calc(var(--navbar-h) + 16px);
  left: 28px;
  width: 188px;
  padding: 14px 16px;
  border-radius: var(--radius);
  z-index: 10;
}
.panel-section-label {
  font-size: 10px; letter-spacing: 0.15em;
  color: var(--text-muted); margin-bottom: 10px;
  text-transform: uppercase;
}
.layer-rows { display: flex; flex-direction: column; gap: 9px; }
.layer-row  { display: flex; align-items: center; gap: 10px; font-size: 11px; color: var(--text-mid); transition: opacity 0.3s ease; }
.layer-row.dimmed { opacity: 0.35; }
.layer-icon { flex-shrink: 0; }
.toggle-section-label { margin-top: 16px; }
.layer-toggles {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px 6px;
  margin-top: 2px;
}
.layer-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  font-size: 11px;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: opacity var(--transition), background var(--transition), color var(--transition);
  outline: none;
  opacity: 0.5;
}
.layer-toggle:hover {
  background: rgba(180,165,140,0.06);
  color: var(--text-mid);
  opacity: 0.75;
}
.layer-toggle:focus-visible {
  border-color: var(--glass-border);
  box-shadow: 0 0 0 2px rgba(180,165,140,0.18);
}
.layer-toggle.active {
  color: var(--text-mid);
  opacity: 1;
  background: rgba(180,165,140,0.06);
}
.layer-toggle.active:hover {
  background: rgba(180,165,140,0.1);
}
.layer-toggle.context {
  font-style: italic;
}
.layer-toggle.context::after {
  content: '↗';
  font-size: 8px;
  font-style: normal;
  color: var(--text-muted);
  opacity: 0.5;
  margin-left: -2px;
}
.toggle-name { white-space: nowrap; }
.toggle-indicator {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(168,162,158,0.3);
  flex-shrink: 0;
  transition: background var(--transition);
}
.toggle-indicator.on {
  background: var(--amber);
}
.toggle-hint {
  margin-top: 8px;
  font-size: 10px;
  line-height: 1.5;
  color: var(--text-muted);
}

.loading-hint {
  margin-top: 12px; display: flex; align-items: center; gap: 8px;
  font-size: 10px; color: var(--text-muted); letter-spacing: 0.06em;
}
.loading-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--amber);
  animation: breathe 1.4s ease-in-out infinite;
  flex-shrink: 0;
}

.map-tooltip {
  position: fixed; z-index: 30;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 7px 13px;
  font-size: 11px; color: var(--text-mid);
  backdrop-filter: var(--blur-sm); -webkit-backdrop-filter: var(--blur-sm);
  pointer-events: none; white-space: nowrap;
  box-shadow: var(--shadow-sm);
}
.map-hint {
  position: absolute; bottom: 28px; left: 50%; transform: translateX(-50%);
  font-size: 11px; color: rgba(90,83,78,0.45);
  letter-spacing: 0.12em; z-index: 10; pointer-events: none;
}
</style>
