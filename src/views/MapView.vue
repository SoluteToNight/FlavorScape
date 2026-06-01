<template>
  <div class="map-page">
    <div ref="mapContainer" class="map-container" />
    <div v-if="!isGlobeMode" class="bubble-layer">
      <button
        v-for="item in projectedNodes"
        :key="item.id"
        type="button"
        class="bubble-node"
        :class="[item.mode, item.placement, item.kind, { selected: item.selected, hovered: item.hovered }]"
        :style="{
          transform: `translate3d(${item.x}px, ${item.y}px, 0)`,
          zIndex: String(item.zIndex),
          '--node-color': item.color,
        }"
        @mouseenter="hoverBubble(item.id)"
        @mouseleave="hoverBubble(null)"
        @focus="hoverBubble(item.id)"
        @blur="hoverBubble(null)"
        @click="selectBubbleNode(item)"
      >
        <span class="bubble-card">
          <span class="bubble-thumb-wrap" :class="{ stacked: item.kind === 'cluster' }">
            <template v-if="item.kind === 'cluster'">
              <img
                v-for="(src, index) in item.bubbleImages"
                :key="`${item.id}-thumb-${index}`"
                class="bubble-thumb bubble-thumb-stack"
                :class="`stack-${index}`"
                :src="src"
                :alt="item.title"
              />
              <span class="bubble-count">{{ item.count }}</span>
            </template>
            <img v-else class="bubble-thumb" :src="item.bubbleImage" :alt="item.dish" />
          </span>
          <span class="bubble-copy">
            <span class="bubble-city">{{ item.city }}</span>
            <span class="bubble-title">{{ item.title }}</span>
            <span class="bubble-desc">{{ item.description }}</span>
          </span>
        </span>
      </button>
    </div>
    <div class="map-vignette map-vignette-top" aria-hidden="true" />
    <div class="map-vignette map-vignette-bottom" aria-hidden="true" />

    <div class="legend-panel glass-panel">
      <div class="legend-head">
        <div>
          <div class="panel-section-label">Map Layers</div>
          <div class="legend-title">图层图例</div>
        </div>
        <div v-if="!rasterReady" class="legend-status" aria-label="底图加载中">
          <span class="loading-dot" />
        </div>
      </div>
      <div class="layer-rows">
        <div v-for="lr in layerLegend" :key="lr.label" class="layer-row" :class="{ dimmed: lr.dimmed }">
          <span class="layer-icon" :style="lr.style" />
          <span class="layer-label">{{ lr.label }}</span>
        </div>
      </div>
    </div>

    <button
      type="button"
      class="devtools-trigger glass-panel"
      :class="{ active: devToolsOpen }"
      aria-label="打开图层调试开关"
      @click="devToolsOpen = !devToolsOpen"
    >
      <span class="devtools-glyph">&lt;/&gt;</span>
      <span class="devtools-text">Dev Tools</span>
    </button>

    <Transition name="devtools">
      <div v-if="devToolsOpen" class="devtools-panel">
        <div class="devtools-header">
          <div>
            <div class="panel-section-label panel-section-label-dark">Debug Console</div>
            <div class="devtools-title">图层调试台</div>
          </div>
          <button
            type="button"
            class="devtools-close"
            aria-label="关闭图层调试开关"
            @click="devToolsOpen = false"
          >×</button>
        </div>

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

        <div class="toggle-hint">L2 仍由上下文触发；这里仅决定该层是否允许进入画面。</div>
        <div v-if="!rasterReady" class="loading-hint">
          <span class="loading-dot" />底图加载中…
        </div>
      </div>
    </Transition>

    <MapInspector />

    <div
      v-if="tooltip.visible"
      class="map-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >{{ tooltip.text }}</div>

    <div class="map-hint">悬浮节点与弧线展示风味迁徙 · 点击对象查看剖面</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAppStore } from '../stores/app.js'
import MapInspector from '../components/MapInspector.vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { AmbientLight, DirectionalLight, LightingEffect } from '@deck.gl/core'
import { MapboxOverlay } from '@deck.gl/mapbox'
import { PathLayer, ScatterplotLayer } from '@deck.gl/layers'
import { TripsLayer } from '@deck.gl/geo-layers'

const mapContainer = ref(null)
const appStore = useAppStore()
const tooltip = ref({ visible: false, x: 0, y: 0, text: '' })
const rasterReady = ref(false)
const devToolsOpen = ref(false)
const projectedNodes = ref([])
const hoveredBubbleId = ref(null)
const isGlobeMode = ref(false)

const L1_OPACITY_WEAK = 0.35
const L1_OPACITY_STRONG = 0.85
const INITIAL_MAP_CENTER = [100, 35]
const GLOBE_ENTER_ZOOM = 2.2
const GLOBE_EXIT_ZOOM = 2.8
const RASTER_MAX_ZOOM = 8
const POLAR_TILE_LIMIT = 85.051129
const LOOP_LENGTH = 2200
const ANIMATION_SPEED = 1.2
const ARC_BLEND_PARAMETERS = {
  blend: true,
  depthWriteEnabled: false,
  blendColorOperation: 'add',
  blendAlphaOperation: 'add',
  blendColorSrcFactor: 'src-alpha',
  blendColorDstFactor: 'one',
  blendAlphaSrcFactor: 'one',
  blendAlphaDstFactor: 'one-minus-src-alpha',
}

const contextLayerVisibility = computed(() => appStore.layerVisibility)
const layerEnabled = computed(() => appStore.layerEnabled)
const layerVisibility = computed(() => ({
  L0: layerEnabled.value.L0 && contextLayerVisibility.value.L0,
  L1: layerEnabled.value.L1 && contextLayerVisibility.value.L1,
  L2: layerEnabled.value.L2 && contextLayerVisibility.value.L2,
  L3: layerEnabled.value.L3 && contextLayerVisibility.value.L3,
}))
const selectedNodeId = computed(() => appStore.selectedNode?.id ?? null)
const selectedRouteName = computed(() => appStore.selectedRoute?.name ?? null)

let map = null
let deckOverlay = null
let animId = null
let currentTime = 0
let flavors = []
let routes = []
let projectFrame = 0
let ignoreBackgroundClickUntil = 0
let pitchBeforeGlobe = 36
let needsMercatorPitchRestore = false
let renderWorldCopiesEnabled = true
let projectionModeFrame = 0
let pendingPitchTarget = null

const POLAR_CAPS_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { cap: 'north' },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [-180, POLAR_TILE_LIMIT],
          [180, POLAR_TILE_LIMIT],
          [180, 90],
          [-180, 90],
          [-180, POLAR_TILE_LIMIT],
        ]],
      },
    },
    {
      type: 'Feature',
      properties: { cap: 'south' },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [-180, -90],
          [180, -90],
          [180, -POLAR_TILE_LIMIT],
          [-180, -POLAR_TILE_LIMIT],
          [-180, -90],
        ]],
      },
    },
  ],
}

const ambientLight = new AmbientLight({
  color: [255, 248, 236],
  intensity: 1.25,
})
const keyLight = new DirectionalLight({
  color: [255, 240, 222],
  intensity: 0.92,
  direction: [-2.5, -6, -1.2],
  shadow: true,
})
const rimLight = new DirectionalLight({
  color: [196, 229, 255],
  intensity: 0.35,
  direction: [1.8, 3.2, -0.6],
})
const lightingEffect = new LightingEffect({
  ambientLight,
  keyLight,
  rimLight,
})

const ADAPTIVE_GLOBE_PROJECTION = {
  type: [
    'interpolate',
    ['linear'],
    ['zoom'],
    GLOBE_ENTER_ZOOM,
    'vertical-perspective',
    GLOBE_EXIT_ZOOM,
    'mercator',
  ],
}

const MAP_STYLE = {
  version: 8,
  projection: ADAPTIVE_GLOBE_PROJECTION,
  sky: {
    'sky-color': '#D9E7EC',
    'sky-horizon-blend': 0.12,
    'horizon-color': '#F4F1EA',
    'horizon-fog-blend': 0.18,
    'fog-color': '#D9E7EC',
    'atmosphere-blend': [
      'interpolate',
      ['linear'],
      ['zoom'],
      0,
      0.34,
      GLOBE_ENTER_ZOOM,
      0.24,
      GLOBE_EXIT_ZOOM,
      0,
    ],
  },
  sources: {
    'hyp-tiles': {
      type: 'raster',
      tiles: ['/tiles/raster/{z}/{x}/{y}.png'],
      tileSize: 256,
      minzoom: 0,
      maxzoom: RASTER_MAX_ZOOM,
      attribution: '© Natural Earth',
    },
  },
  layers: [
    { id: 'bg', type: 'background', paint: { 'background-color': '#C8DDE8' } },
    {
      id: 'hyp',
      type: 'raster',
      source: 'hyp-tiles',
      paint: {
        'raster-saturation': -0.18,
        'raster-contrast': 0.08,
        'raster-brightness-min': 0.05,
        'raster-opacity': 1,
      },
    },
  ],
}

function hexToRgb(hex, a = 255) {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
    a,
  ]
}

function buildTripData(routeList, activeRouteName) {
  const trips = []

  routeList.forEach((route, index) => {
    const emphasis = !activeRouteName || activeRouteName === route.name ? 1 : 0.28
    const pulseCount = activeRouteName === route.name ? 4 : 3

    for (let pulse = 0; pulse < pulseCount; pulse++) {
      const start = (index * 420 + pulse * (LOOP_LENGTH / pulseCount)) % LOOP_LENGTH
      trips.push({
        path: route.path,
        timestamps: route.path.map((_, pointIndex) => start + (pointIndex / (route.path.length - 1)) * 980),
        color: hexToRgb(route.color, Math.round(255 * emphasis)),
      })
    }
  })

  return trips
}

function buildRoutePaths(routeList, activeRouteName) {
  return routeList.map(route => {
    const emphasis = !activeRouteName || activeRouteName === route.name ? 1 : 0.3
    const isSea = route.type === 'sea'

    return {
      ...route,
      width: (isSea ? 4.4 : 3.5) * emphasis,
      color: hexToRgb(route.color, Math.round((isSea ? 228 : 210) * emphasis)),
    }
  })
}

function buildLayers(time, flavorList, routeList, vis, activeNodeId, activeRouteName) {
  const layers = []

  if (vis.L2) {
    layers.push(
      new PathLayer({
        id: 'route-path-layer',
        data: buildRoutePaths(routeList, activeRouteName),
        getPath: d => d.path,
        getColor: d => d.color,
        getWidth: d => d.width,
        widthUnits: 'pixels',
        widthMinPixels: 2,
        rounded: true,
        jointRounded: true,
        capRounded: true,
        pickable: true,
        parameters: ARC_BLEND_PARAMETERS,
        onHover: ({ object, x, y }) => {
          tooltip.value = object
            ? { visible: true, x: x + 14, y: y - 10, text: object.name }
            : { ...tooltip.value, visible: false }
        },
        onClick: ({ object }) => {
          if (!object) return
          consumeMapClick()
          appStore.selectRoute(object)
        },
      }),
      new TripsLayer({
        id: 'route-trips-layer',
        data: buildTripData(routeList, activeRouteName),
        getPath: d => d.path,
        getTimestamps: d => d.timestamps,
        getColor: d => d.color,
        opacity: 1,
        widthMinPixels: 4,
        rounded: true,
        fadeTrail: true,
        trailLength: 240,
        currentTime: time,
        parameters: ARC_BLEND_PARAMETERS,
      }),
    )
  }

  if (vis.L3) {
    layers.push(
      new ScatterplotLayer({
        id: 'node-glow-layer',
        data: flavorList,
        getPosition: d => d.coordinates,
        getRadius: d => (activeNodeId === d.id ? 54000 : 36000),
        radiusUnits: 'meters',
        getFillColor: d => hexToRgb(d.color, activeNodeId === d.id ? 96 : 42),
        stroked: false,
        pickable: false,
        parameters: ARC_BLEND_PARAMETERS,
      }),
    )
  }

  return layers
}

function getActiveMap() {
  return map
}

function syncProjectionMode() {
  if (!map) return

  const zoom = map.getZoom()
  const shouldBeFullGlobe = zoom <= GLOBE_ENTER_ZOOM
  const shouldUseSingleWorld = zoom < GLOBE_EXIT_ZOOM
  const nextWorldCopiesEnabled = !shouldUseSingleWorld

  if (renderWorldCopiesEnabled !== nextWorldCopiesEnabled) {
    renderWorldCopiesEnabled = nextWorldCopiesEnabled
    map.setRenderWorldCopies(renderWorldCopiesEnabled)
  }

  if (shouldBeFullGlobe && !isGlobeMode.value) {
    pitchBeforeGlobe = map.getPitch()
    needsMercatorPitchRestore = true
    isGlobeMode.value = true
    queueProjectionPitch(0)
  } else if (!shouldBeFullGlobe && isGlobeMode.value) {
    isGlobeMode.value = false
  }

  if (zoom >= GLOBE_EXIT_ZOOM && needsMercatorPitchRestore) {
    needsMercatorPitchRestore = false
    queueProjectionPitch(pitchBeforeGlobe)
  }

  syncPolarCapsState()
  scheduleProjectedNodesUpdate()
  applyQueuedProjectionPitch()
}

function scheduleProjectionModeSync() {
  if (projectionModeFrame) return
  projectionModeFrame = requestAnimationFrame(() => {
    projectionModeFrame = 0
    syncProjectionMode()
  })
}

function queueProjectionPitch(pitch) {
  pendingPitchTarget = pitch
}

function applyQueuedProjectionPitch() {
  if (!map || pendingPitchTarget === null || map.isMoving()) return

  const pitch = pendingPitchTarget
  pendingPitchTarget = null
  if (Math.abs(map.getPitch() - pitch) < 0.25) return
  map.easeTo({ pitch, duration: 420, essential: true })
}

function getClusterDistance(zoom) {
  if (zoom < 3.4) return 118
  if (zoom < 4.15) return 84
  return 0
}

function getBubblePlacement(index) {
  return ['north-east', 'north-west', 'north-east', 'north-west'][index % 4]
}

function getBubbleMode(flavor, zoom) {
  const selected = selectedNodeId.value === flavor.id
  const hovered = hoveredBubbleId.value === flavor.id
  if (selected || hovered) return 'expanded'
  if (zoom >= 4.9) return 'expanded'
  if (zoom >= 4.15) return 'compact'
  return 'hidden'
}

function isPointVisible(point) {
  if (!map) return false
  const { width, height } = map.getContainer().getBoundingClientRect()
  const pad = 120
  return point.x > -pad && point.x < width + pad && point.y > -pad && point.y < height + pad
}

function createBubbleNode(flavor, point, zoom, modeOverride = null) {
  const selected = selectedNodeId.value === flavor.id
  const hovered = hoveredBubbleId.value === flavor.id
  const mode = modeOverride ?? getBubbleMode(flavor, zoom)

  if (mode === 'hidden') return null

  return {
    kind: 'node',
    id: flavor.id,
    title: flavor.dish,
    city: flavor.city,
    dish: flavor.dish,
    description: flavor.description,
    bubbleImage: flavor.bubbleImage,
    count: 1,
    raw: flavor,
    color: flavor.color,
    x: point.x,
    y: point.y,
    mode,
    selected,
    hovered,
    placement: getBubblePlacement(flavor.__bubbleIndex ?? 0),
    zIndex: selected ? 28 : (hovered ? 24 : (mode === 'expanded' ? 16 : 12)),
  }
}

function clusterBaseNodes(nodes, threshold) {
  const clusters = []
  const visited = new Set()

  for (let i = 0; i < nodes.length; i++) {
    const seed = nodes[i]
    if (visited.has(seed.id)) continue

    const stack = [seed]
    const members = []
    visited.add(seed.id)

    while (stack.length) {
      const current = stack.pop()
      members.push(current)

      for (let j = 0; j < nodes.length; j++) {
        const candidate = nodes[j]
        if (visited.has(candidate.id)) continue

        const dx = current.point.x - candidate.point.x
        const dy = current.point.y - candidate.point.y
        if (Math.hypot(dx, dy) <= threshold) {
          visited.add(candidate.id)
          stack.push(candidate)
        }
      }
    }

    clusters.push(members)
  }

  return clusters
}

function createClusterBubble(members) {
  const centroid = members.reduce(
    (acc, member) => {
      acc.x += member.point.x
      acc.y += member.point.y
      return acc
    },
    { x: 0, y: 0 },
  )
  centroid.x /= members.length
  centroid.y /= members.length

  const sorted = [...members].sort((a, b) => a.flavor.city.localeCompare(b.flavor.city, 'zh-CN'))
  const citySummary = sorted.slice(0, 3).map(member => member.flavor.city).join(' · ')
  const dishSummary = sorted.slice(0, 3).map(member => member.flavor.dish).join(' · ')
  const suffix = members.length > 3 ? ` 等 ${members.length} 个节点` : ` 共 ${members.length} 个节点`

  return {
    kind: 'cluster',
    id: `cluster-${sorted.map(member => member.id).join('-')}`,
    title: `${members.length} 个风味节点`,
    city: citySummary,
    dish: '',
    description: `${dishSummary}${suffix}`,
    bubbleImages: sorted.slice(0, 3).map(member => member.flavor.bubbleImage),
    count: members.length,
    children: sorted.map(member => member.flavor),
    coordinates: sorted.map(member => member.flavor.coordinates),
    color: sorted[0].flavor.color,
    x: centroid.x,
    y: centroid.y,
    mode: 'cluster',
    selected: false,
    hovered: hoveredBubbleId.value === `cluster-${sorted.map(member => member.id).join('-')}`,
    placement: getBubblePlacement(sorted[0].flavor.__bubbleIndex ?? 0),
    zIndex: hoveredBubbleId.value === `cluster-${sorted.map(member => member.id).join('-')}` ? 22 : 14,
  }
}

function updateProjectedNodes() {
  if (!map || isGlobeMode.value || !layerVisibility.value.L3) {
    projectedNodes.value = []
    return
  }

  const zoom = map.getZoom()
  const baseNodes = flavors
    .map((flavor, index) => {
      flavor.__bubbleIndex = index
      const point = map.project(flavor.coordinates)
      if (!isPointVisible(point)) return null
      return {
        id: flavor.id,
        flavor,
        point,
        selected: selectedNodeId.value === flavor.id,
      }
    })
    .filter(Boolean)

  const clusterDistance = getClusterDistance(zoom)
  const selectedNodes = baseNodes.filter(node => node.selected)
  const normalNodes = baseNodes.filter(node => !node.selected)

  if (!clusterDistance) {
    projectedNodes.value = baseNodes
      .map(node => createBubbleNode(node.flavor, node.point, zoom))
      .filter(Boolean)
    return
  }

  const items = selectedNodes
    .map(node => createBubbleNode(node.flavor, node.point, zoom, 'expanded'))
    .filter(Boolean)

  const clusters = clusterBaseNodes(normalNodes, clusterDistance)
  clusters.forEach(members => {
    if (members.length === 1) {
      const member = members[0]
      const mode = zoom >= 3 ? 'compact' : 'hidden'
      const nodeItem = createBubbleNode(member.flavor, member.point, zoom, mode)
      if (nodeItem) items.push(nodeItem)
      return
    }

    items.push(createClusterBubble(members))
  })

  projectedNodes.value = items
}

function scheduleProjectedNodesUpdate() {
  if (projectFrame) cancelAnimationFrame(projectFrame)
  projectFrame = requestAnimationFrame(() => {
    projectFrame = 0
    updateProjectedNodes()
  })
}

function hoverBubble(id) {
  hoveredBubbleId.value = id
  scheduleProjectedNodesUpdate()
}

function consumeMapClick() {
  ignoreBackgroundClickUntil = performance.now() + 240
}

function clearMapSelection() {
  if (!appStore.selectedNode && !appStore.selectedRoute && !appStore.selectedEcozone) return
  appStore.clearSelection()
}

function handleMapBackgroundClick() {
  if (performance.now() < ignoreBackgroundClickUntil) {
    return
  }

  clearMapSelection()
}

function handleWindowKeydown(event) {
  if (event.key !== 'Escape') return
  clearMapSelection()
}

function selectBubbleNode(item) {
  consumeMapClick()

  const activeMap = getActiveMap()
  if (item.kind === 'cluster' && activeMap && item.coordinates?.length) {
    const bounds = item.coordinates.reduce(
      (acc, point) => acc.extend(point),
      new maplibregl.LngLatBounds(item.coordinates[0], item.coordinates[0]),
    )
    activeMap.fitBounds(bounds, { padding: 120, maxZoom: 5.25, duration: 900, essential: true })
    return
  }

  if (item.raw) {
    appStore.selectNode(item.raw)
  }
}

function redrawDeck() {
  deckOverlay?.setProps({
    layers: buildLayers(
      currentTime,
      flavors,
      routes,
      layerVisibility.value,
      selectedNodeId.value,
      selectedRouteName.value,
    ),
  })
}

function setPolarCapsVisibility(visible) {
  setMapLayerVisibility('polar-caps', visible)
}

function syncPolarCapsState() {
  if (!map) return
  setPolarCapsVisibility(map.getZoom() < GLOBE_EXIT_ZOOM && layerVisibility.value.L0)
}

function startAnimation() {
  function frame() {
    currentTime = (currentTime + ANIMATION_SPEED) % LOOP_LENGTH
    redrawDeck()
    animId = requestAnimationFrame(frame)
  }

  frame()
}

async function addVectorLayers() {
  const physLayers = [
    { id: 'coastline', url: '/tiles/vector/coastline', type: 'line', paint: { 'line-color': '#8A7560', 'line-width': 0.6, 'line-opacity': 0.65 } },
    { id: 'rivers', url: '/tiles/vector/rivers', type: 'line', paint: { 'line-color': '#5BA0B8', 'line-width': 0.4, 'line-opacity': 0.6 } },
  ]

  for (const layer of physLayers) {
    try {
      map.addSource(layer.id, { type: 'geojson', data: layer.url })
      map.addLayer({ id: layer.id, type: layer.type, source: layer.id, paint: layer.paint })
    } catch (err) {
      console.warn(`Vector layer [${layer.id}] skipped:`, err.message)
    }
  }

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

  map.on('click', 'ecoregions', e => {
    const props = e.features?.[0]?.properties
    if (props) {
      consumeMapClick()
      appStore.selectEcozone(props)
    }
  })
  map.on('mouseenter', 'ecoregions', () => { map.getCanvas().style.cursor = 'pointer' })
  map.on('mouseleave', 'ecoregions', () => { map.getCanvas().style.cursor = '' })
}

function addPolarCapLayer() {
  try {
    map.addSource('polar-caps', { type: 'geojson', data: POLAR_CAPS_GEOJSON })
    map.addLayer({
      id: 'polar-caps',
      type: 'fill',
      source: 'polar-caps',
      layout: { visibility: 'none' },
      paint: {
        'fill-color': [
          'match',
          ['get', 'cap'],
          'north',
          '#C8DDE8',
          'south',
          '#F4F1EA',
          '#D9E7EC',
        ],
        'fill-opacity': [
          'interpolate',
          ['linear'],
          ['zoom'],
          GLOBE_ENTER_ZOOM,
          1,
          GLOBE_EXIT_ZOOM,
          0,
        ],
      },
    })
  } catch (err) {
    console.warn('polar caps skipped:', err.message)
  }
}

onMounted(async () => {
  const [fRes, rRes] = await Promise.all([fetch('/api/flavors'), fetch('/api/routes')])
  flavors = await fRes.json()
  routes = await rRes.json()
  appStore.setFlavors(flavors)

  fetch('/tiles/status')
    .then(r => r.json())
    .then(s => {
      rasterReady.value = s.raster_ready
    })
    .catch(() => {
      rasterReady.value = false
    })

  map = new maplibregl.Map({
    container: mapContainer.value,
    style: MAP_STYLE,
    center: INITIAL_MAP_CENTER,
    zoom: 2.5,
    pitch: 36,
    bearing: -8,
    antialias: true,
    attributionControl: false,
  })

  map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right')
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right')

  map.on('load', async () => {
    rasterReady.value = true

    deckOverlay = new MapboxOverlay({
      interleaved: true,
      effects: [lightingEffect],
      layers: buildLayers(0, flavors, routes, layerVisibility.value, selectedNodeId.value, selectedRouteName.value),
      getCursor: ({ isHovering }) => (isHovering ? 'pointer' : 'grab'),
    })

    map.addControl(deckOverlay)
    startAnimation()
    addPolarCapLayer()
    await addVectorLayers()
    syncBaseLayerState()
    syncEcoregionState()
    syncProjectionMode()
    updateProjectedNodes()
  })

  map.on('render', updateProjectedNodes)
  map.on('zoom', scheduleProjectionModeSync)
  map.on('zoomend', syncProjectionMode)
  map.on('moveend', syncProjectionMode)
  map.on('resize', updateProjectedNodes)
  map.on('click', handleMapBackgroundClick)
  window.addEventListener('keydown', handleWindowKeydown)
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  cancelAnimationFrame(projectFrame)
  cancelAnimationFrame(projectionModeFrame)
  window.removeEventListener('keydown', handleWindowKeydown)
  map?.remove()
})

function setL1Strength(opacity) {
  if (!map) return

  try {
    map.setPaintProperty('ecoregions', 'line-opacity', opacity)
    map.setPaintProperty('ecoregions', 'line-width', opacity > 0.5 ? 1.8 : 1.4)
  } catch (_) {
    // ecoregions layer may not be added yet
  }
}

function setMapLayerVisibility(id, visible) {
  if (!map) return

  try {
    map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none')
  } catch (_) {
    // layer may not be added yet
  }
}

function syncBaseLayerState() {
  const showL0 = layerVisibility.value.L0
  setMapLayerVisibility('bg', showL0)
  setMapLayerVisibility('hyp', showL0)
  setMapLayerVisibility('coastline', showL0)
  setMapLayerVisibility('rivers', showL0)
  syncPolarCapsState()
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

watch(
  () => [appStore.selectedNode, appStore.selectedRoute, appStore.selectedEcozone],
  ([node, route]) => {
    const activeMap = getActiveMap()

    if (node && activeMap) {
      activeMap.flyTo({
        center: node.coordinates,
        zoom: 5.5,
        pitch: isGlobeMode.value ? 0 : 44,
        duration: 1200,
        essential: true,
      })
    }

    if (route && activeMap && route.path?.length) {
      const bounds = route.path.reduce(
        (b, point) => b.extend(point),
        new maplibregl.LngLatBounds(route.path[0], route.path[0]),
      )
      activeMap.fitBounds(bounds, { padding: 88, duration: 1200, essential: true })
    }

    redrawDeck()
    scheduleProjectedNodesUpdate()
  },
)

watch(
  () => [
    layerVisibility.value.L0,
    layerVisibility.value.L1,
    layerVisibility.value.L2,
    layerVisibility.value.L3,
    appStore.l1Emphasis,
  ],
  () => {
    syncBaseLayerState()
    syncEcoregionState()
    redrawDeck()
    scheduleProjectedNodesUpdate()
  },
  { immediate: true },
)

const layerLegend = computed(() => [
  {
    label: 'HYP 自然地形底图',
    dimmed: !layerVisibility.value.L0,
    style: {
      width: '16px',
      height: '8px',
      background: 'linear-gradient(90deg, #6EAA7B 0%, #D8C1A0 52%, #9CB9D8 100%)',
      borderRadius: '999px',
      display: 'inline-block',
      opacity: layerVisibility.value.L0 ? 1 : 0.2,
    },
  },
  {
    label: '海岸线 / 主干水系',
    dimmed: !layerVisibility.value.L0,
    style: {
      width: '20px',
      height: '2px',
      background: 'linear-gradient(90deg, #8A7560 0 48%, transparent 48% 54%, #5BA0B8 54% 100%)',
      borderRadius: '999px',
      display: 'inline-block',
      opacity: layerVisibility.value.L0 ? 0.95 : 0.2,
    },
  },
  {
    label: 'L1 生态区边界',
    dimmed: !layerVisibility.value.L1,
    style: {
      width: '20px',
      height: '2px',
      background: '#6B4825',
      borderRadius: '999px',
      display: 'inline-block',
      opacity: !layerVisibility.value.L1 ? 0.15 : (appStore.l1Emphasis ? L1_OPACITY_STRONG : L1_OPACITY_WEAK),
    },
  },
  {
    label: 'L2 迁徙弧线',
    dimmed: !layerVisibility.value.L2,
    style: {
      width: '20px',
      height: '10px',
      display: 'inline-block',
      borderTop: '2px solid rgba(232, 169, 23, 0.95)',
      borderRadius: '999px 999px 0 0',
      transform: 'translateY(3px)',
      opacity: layerVisibility.value.L2 ? 1 : 0.25,
    },
  },
  {
    label: '脉冲流光',
    dimmed: !layerVisibility.value.L2,
    style: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      background: 'radial-gradient(circle, rgba(255, 245, 220, 1) 0%, rgba(232, 169, 23, 0.98) 45%, rgba(232, 169, 23, 0) 100%)',
      display: 'inline-block',
      opacity: layerVisibility.value.L2 ? 1 : 0.25,
      boxShadow: layerVisibility.value.L2 ? '0 0 12px rgba(232, 169, 23, 0.48)' : 'none',
    },
  },
  {
    label: 'L3 气泡节点',
    dimmed: !layerVisibility.value.L3,
    style: {
      width: '8px',
      height: '14px',
      borderRadius: '999px',
      background: 'linear-gradient(180deg, rgba(255, 250, 245, 0.95) 0%, var(--carmine) 48%, rgba(229, 57, 78, 0.8) 100%)',
      display: 'inline-block',
      opacity: layerVisibility.value.L3 ? 1 : 0.2,
      boxShadow: layerVisibility.value.L3 ? '0 5px 15px rgba(229, 57, 78, 0.22)' : 'none',
    },
  },
])

const layerToggles = computed(() => [
  { key: 'L0', label: 'L0 底图', enabled: layerEnabled.value.L0, contextual: false },
  { key: 'L1', label: 'L1 区划', enabled: layerEnabled.value.L1, contextual: false },
  { key: 'L2', label: 'L2 路径', enabled: layerEnabled.value.L2, contextual: true },
  { key: 'L3', label: 'L3 节点', enabled: layerEnabled.value.L3, contextual: false },
])
</script>

<style scoped>
.map-page {
  position: fixed;
  inset: 0;
  background: #c8dde8;
  overflow: hidden;
}

.map-container {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  background: #d9e7ec;
}

.bubble-layer {
  position: absolute;
  inset: 0;
  z-index: 8;
  pointer-events: none;
}

.bubble-node {
  position: absolute;
  width: 0;
  height: 0;
  padding: 0;
  margin: 0;
  overflow: visible;
  border: 0;
  background: transparent;
  pointer-events: auto;
  cursor: pointer;
}

.bubble-node:focus-visible {
  outline: none;
}

.bubble-card {
  position: absolute;
  bottom: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  width: 214px;
  padding: 10px;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.14);
  background:
    linear-gradient(180deg, rgba(255,252,248,0.94) 0%, rgba(255,249,243,0.86) 100%);
  box-shadow:
    0 18px 46px rgba(34, 24, 14, 0.16),
    inset 0 1px 0 rgba(255,255,255,0.62);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transform-origin: bottom center;
  transition:
    opacity 220ms ease,
    transform 220ms ease,
    width 220ms ease,
    padding 220ms ease,
    box-shadow 220ms ease;
}

.bubble-node.north-east .bubble-card {
  transform: translate(18px, 0);
}

.bubble-node.north-west .bubble-card {
  transform: translate(calc(-100% - 18px), 0);
}

.bubble-thumb-wrap {
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  border-radius: 14px;
  overflow: hidden;
  background: rgba(255,255,255,0.74);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}

.bubble-thumb-wrap.stacked {
  position: relative;
}

.bubble-thumb {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bubble-thumb-stack {
  position: absolute;
  inset: auto;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.94);
  box-shadow: 0 8px 20px rgba(26, 18, 12, 0.16);
}

.bubble-thumb-stack.stack-0 {
  left: 6px;
  top: 16px;
}

.bubble-thumb-stack.stack-1 {
  right: 6px;
  top: 8px;
}

.bubble-thumb-stack.stack-2 {
  left: 18px;
  bottom: 4px;
}

.bubble-count {
  position: absolute;
  right: 0;
  bottom: 2px;
  min-width: 24px;
  height: 24px;
  padding: 0 7px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--node-color) 88%, white);
  color: white;
  font-size: 11px;
  font-weight: 700;
  box-shadow: 0 8px 18px color-mix(in srgb, var(--node-color) 28%, transparent);
}

.bubble-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
}

.bubble-city {
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(121, 104, 88, 0.72);
}

.bubble-title {
  font-size: 14px;
  line-height: 1.25;
  font-family: var(--font-serif);
  color: #2e2218;
}

.bubble-desc {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  font-size: 11px;
  line-height: 1.45;
  color: rgba(87, 83, 78, 0.88);
}

.bubble-node.compact .bubble-card {
  width: 48px;
  height: 48px;
  padding: 4px;
  gap: 0;
  border-radius: 50%;
}

.bubble-node.compact .bubble-thumb-wrap {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.bubble-node.compact .bubble-copy {
  display: none;
}

.bubble-node.cluster .bubble-card {
  width: 188px;
  padding: 8px 10px;
  gap: 10px;
  border-radius: 20px;
}

.bubble-node.cluster .bubble-thumb-wrap {
  width: 68px;
  height: 68px;
}

.bubble-node.cluster .bubble-city {
  font-size: 9px;
}

.bubble-node.cluster .bubble-title {
  font-size: 13px;
}

.bubble-node.cluster .bubble-desc {
  -webkit-line-clamp: 1;
  font-size: 10px;
  color: rgba(87, 83, 78, 0.74);
}

.bubble-node.expanded .bubble-card,
.bubble-node:hover .bubble-card,
.bubble-node:focus-visible .bubble-card {
  box-shadow:
    0 22px 58px rgba(34, 24, 14, 0.22),
    0 0 0 1px color-mix(in srgb, var(--node-color) 22%, transparent),
    inset 0 1px 0 rgba(255,255,255,0.74);
}

.bubble-node.selected .bubble-card {
  box-shadow:
    0 24px 64px rgba(34, 24, 14, 0.24),
    0 0 0 1px color-mix(in srgb, var(--node-color) 36%, transparent),
    0 0 24px color-mix(in srgb, var(--node-color) 18%, transparent);
}

.bubble-node.selected .bubble-title,
.bubble-node.hovered .bubble-title {
  color: color-mix(in srgb, var(--node-color) 62%, #2e2218);
}

.map-vignette {
  position: absolute;
  left: 0;
  right: 0;
  pointer-events: none;
  z-index: 2;
}

.map-vignette-top {
  top: 0;
  height: 180px;
  background: linear-gradient(180deg, rgba(248, 244, 239, 0.78) 0%, rgba(248, 244, 239, 0) 100%);
}

.map-vignette-bottom {
  bottom: 0;
  height: 120px;
  background: linear-gradient(180deg, rgba(248, 244, 239, 0) 0%, rgba(248, 244, 239, 0.64) 100%);
}

:deep(.maplibregl-canvas) {
  outline: none;
}

:deep(.maplibregl-ctrl-attrib) {
  background: rgba(255, 252, 248, 0.7) !important;
  border-radius: 4px !important;
  font-size: 10px !important;
}

:deep(.maplibregl-ctrl-group) {
  background: rgba(255, 252, 248, 0.78) !important;
  border: 1px solid rgba(180, 165, 140, 0.22) !important;
  border-radius: 10px !important;
  box-shadow: 0 10px 32px rgba(35, 25, 12, 0.08) !important;
  backdrop-filter: var(--blur-sm) !important;
  margin-bottom: 28px !important;
  margin-right: 308px !important;
}

.legend-panel {
  position: absolute;
  top: calc(var(--navbar-h) + 18px);
  left: 28px;
  width: 218px;
  padding: 16px 16px 14px;
  border-radius: 20px;
  z-index: 10;
}

.legend-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}

.legend-title {
  font-family: var(--font-serif);
  font-size: 16px;
  color: var(--text);
}

.legend-status {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 252, 248, 0.66);
  border: 1px solid rgba(180, 165, 140, 0.2);
}

.panel-section-label {
  font-size: 10px;
  letter-spacing: 0.18em;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.panel-section-label-dark {
  color: rgba(255, 255, 255, 0.46);
}

.layer-rows {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.layer-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: var(--text-mid);
  transition: opacity 0.3s ease;
}

.layer-row.dimmed {
  opacity: 0.35;
}

.layer-icon {
  flex-shrink: 0;
}

.layer-label {
  letter-spacing: 0.02em;
}

.devtools-trigger {
  position: absolute;
  left: 28px;
  bottom: 28px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 1px solid rgba(180, 165, 140, 0.2);
  border-radius: 999px;
  cursor: pointer;
  z-index: 10;
  color: var(--text-mid);
  transition: transform var(--transition), box-shadow var(--transition), background var(--transition);
}

.devtools-trigger:hover,
.devtools-trigger.active {
  transform: translateY(-1px);
  box-shadow: 0 14px 36px rgba(34, 23, 10, 0.12);
  background: rgba(255, 252, 248, 0.94);
}

.devtools-glyph {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  letter-spacing: 0.04em;
  color: var(--amber);
}

.devtools-text {
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.devtools-panel {
  position: absolute;
  left: 28px;
  bottom: 84px;
  width: 228px;
  padding: 16px;
  border-radius: 20px;
  z-index: 11;
  color: rgba(255, 255, 255, 0.84);
  background:
    linear-gradient(180deg, rgba(26, 30, 36, 0.9) 0%, rgba(17, 20, 24, 0.94) 100%),
    rgba(16, 18, 22, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 20px 48px rgba(3, 5, 8, 0.26);
}

.devtools-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}

.devtools-title {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.92);
  font-family: var(--font-serif);
}

.devtools-close {
  width: 26px;
  height: 26px;
  border: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.72);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.layer-toggles {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
}

.layer-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 9px 10px;
  border-radius: 10px;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.48);
  font-size: 11px;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: opacity var(--transition), background var(--transition), color var(--transition), border-color var(--transition);
  outline: none;
}

.layer-toggle:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.72);
}

.layer-toggle:focus-visible {
  border-color: rgba(232, 169, 23, 0.42);
}

.layer-toggle.active {
  color: rgba(255, 255, 255, 0.92);
  border-color: rgba(232, 169, 23, 0.22);
  background: rgba(232, 169, 23, 0.1);
}

.layer-toggle.context::after {
  content: '↗';
  font-size: 8px;
  color: rgba(255, 255, 255, 0.36);
  margin-left: -2px;
}

.toggle-name {
  white-space: nowrap;
}

.toggle-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.14);
  flex-shrink: 0;
  transition: background var(--transition), box-shadow var(--transition);
}

.toggle-indicator.on {
  background: var(--amber);
  box-shadow: 0 0 12px rgba(232, 169, 23, 0.5);
}

.toggle-hint {
  margin-top: 10px;
  font-size: 10px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.5);
}

.loading-hint {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.54);
  letter-spacing: 0.06em;
}

.loading-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--amber);
  animation: breathe 1.4s ease-in-out infinite;
  flex-shrink: 0;
}

.map-tooltip {
  position: fixed;
  z-index: 30;
  background: rgba(18, 22, 26, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 8px 14px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  pointer-events: none;
  white-space: nowrap;
  box-shadow: 0 16px 40px rgba(5, 8, 11, 0.2);
}

.map-hint {
  position: absolute;
  bottom: 26px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: rgba(90, 83, 78, 0.48);
  letter-spacing: 0.14em;
  z-index: 10;
  pointer-events: none;
}

.devtools-enter-active,
.devtools-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.devtools-enter-from,
.devtools-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

@media (max-width: 1080px) {
  :deep(.maplibregl-ctrl-group) {
    margin-right: 28px !important;
  }

  .legend-panel {
    width: 196px;
    left: 18px;
  }

  .devtools-trigger,
  .devtools-panel {
    left: 18px;
  }
}

@media (max-width: 840px) {
  .legend-panel {
    top: calc(var(--navbar-h) + 12px);
    width: calc(100% - 36px);
  }

  .devtools-panel {
    width: calc(100% - 36px);
  }

  .map-hint {
    width: calc(100% - 36px);
    text-align: center;
    letter-spacing: 0.08em;
  }
}
</style>
