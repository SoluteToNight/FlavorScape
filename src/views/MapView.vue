<template>
  <div class="map-page fixed top-navbar inset-x-0 bottom-0" :class="{ transitioning: isSceneBusy }">
    <div
      class="map-scene flat-scene"
      :class="{ active: isSceneActive('flat'), visible: isSceneVisible('flat') }"
      :style="getSceneStyle('flat')"
    >
      <div ref="flatMapContainer" class="map-container absolute inset-0 w-full h-full" />
      <img
        v-if="sceneSnapshot.visible"
        class="scene-snapshot"
        :src="sceneSnapshot.src"
        alt=""
        aria-hidden="true"
      />
      <div class="bubble-layer">
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
          <span v-if="item.kind === 'node' && item.selected" class="poi-photo-card">
            <span class="poi-photo-frame">
              <img class="poi-photo-img" :src="item.bubbleImage" :alt="item.dish" />
            </span>
            <span class="poi-photo-caption">
              <span class="poi-photo-city">{{ item.city }}</span>
              <span class="poi-photo-title">{{ item.title }}</span>
            </span>
          </span>
          <span v-else class="bubble-card">
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
    </div>
    <div
      class="map-scene globe-scene"
      :class="{ active: isSceneActive('globe'), visible: isSceneVisible('globe') }"
      :style="getSceneStyle('globe')"
    >
      <div ref="globeMapContainer" class="map-container" />
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

    <button
      type="button"
      class="scene-toggle glass-panel"
      :class="{ transitioning: isSceneBusy }"
      :aria-label="sceneToggleLabel"
      :aria-pressed="activeScene === 'globe'"
      :aria-busy="isSceneBusy"
      :disabled="isSceneBusy || !sceneToggleReady"
      @click="toggleSceneMode"
    >
      <svg class="scene-toggle-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path v-if="activeScene === 'flat'" d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z" />
        <path v-if="activeScene === 'flat'" d="M3.6 9h16.8M3.6 15h16.8M12 3c2.2 2.3 3.3 5.3 3.3 9S14.2 18.7 12 21M12 3C9.8 5.3 8.7 8.3 8.7 12s1.1 6.7 3.3 9" />
        <path v-if="activeScene !== 'flat'" d="M3 6.5 9 4l6 2.5 6-2.5v13.5L15 20l-6-2.5L3 20V6.5Z" />
        <path v-if="activeScene !== 'flat'" d="M9 4v13.5M15 6.5V20" />
      </svg>
      <span>{{ sceneToggleLabel }}</span>
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

        <div class="debug-readout" aria-label="地图调试状态">
          <div v-for="row in mapDebugRows" :key="row.label" class="debug-readout-row">
            <span class="debug-readout-label">{{ row.label }}</span>
            <span class="debug-readout-value">{{ row.value }}</span>
          </div>
        </div>

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

    <div class="map-hint">悬浮节点展示地方风味 · 点击对象查看剖面</div>
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
import { ScatterplotLayer, TextLayer } from '@deck.gl/layers'
import { computeClusters, getClusterOpacity } from '../utils/clustering.js'

const flatMapContainer = ref(null)
const globeMapContainer = ref(null)
const appStore = useAppStore()
const tooltip = ref({ visible: false, x: 0, y: 0, text: '' })
const rasterReady = ref(false)
const devToolsOpen = ref(false)
const projectedNodes = ref([])
const hoveredBubbleId = ref(null)
const activeScene = ref('flat')
const mapDebugTick = ref(0)
const isSceneTransitioning = ref(false)
const transitionToScene = ref(null)
const sceneTransitionProgress = ref(0)
const sceneSnapshot = ref({ visible: false, src: '' })

const L1_OPACITY_WEAK = 0.42
const L1_OPACITY_STRONG = 0.62
const L1_BOUNDARY_COLOR = 'rgba(86, 125, 132, 0.42)'
const L1_BOUNDARY_COLOR_STRONG = 'rgba(63, 104, 114, 0.62)'
const INITIAL_MAP_CENTER = [100, 35]
const ATMOSPHERE_LOW_ZOOM = 2.2
const ATMOSPHERE_HIGH_ZOOM = 2.8
const SCENE_TRANSITION_DURATION = 820
const SCENE_MORPH_ZOOM_SPAN = 0.18
const SCENE_RENDER_WAIT_TIMEOUT = 140
const SCENE_TILE_PREWARM_TIMEOUT = 1200
const POLAR_TILE_LIMIT = 85.051129
const GLOBE_NODE_SOURCE_ID = 'globe-nodes'
const GLOBE_NODE_HALO_LAYER_ID = 'globe-node-halo'
const GLOBE_NODE_GLOW_LAYER_ID = 'globe-node-glow'
const GLOBE_NODE_DOT_LAYER_ID = 'globe-node-dot'
const GLOBE_CLUSTER_LABEL_LAYER_ID = 'globe-cluster-label'
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
  L3: layerEnabled.value.L3 && contextLayerVisibility.value.L3,
}))
const selectedNodeId = computed(() => appStore.selectedNode?.id ?? null)
const sceneToggleReady = computed(() => {
  mapDebugTick.value
  return Boolean(flatScene?.loaded && globeScene?.loaded)
})
const isSceneBusy = computed(() => isSceneTransitioning.value || Boolean(transitionToScene.value))
const sceneToggleLabel = computed(() => activeScene.value === 'flat' ? '切换到地球' : '切换到平面')
const mapDebugRows = computed(() => {
  mapDebugTick.value
  const activeMap = getActiveMap()
  const progress = isSceneTransitioning.value
    ? `${Math.round(sceneTransitionProgress.value * 100)}%`
    : (transitionToScene.value ? 'prewarm' : 'idle')
  return [
    { label: 'Zoom', value: activeMap ? activeMap.getZoom().toFixed(3) : '3.500' },
    { label: 'Scene', value: activeScene.value },
    { label: 'Target', value: transitionToScene.value || '-' },
    { label: 'Progress', value: progress },
    { label: 'Surface', value: getVisibleSceneKind() },
  ]
})

let flatScene = null
let globeScene = null
let flavors = []
let clusterState = { clusters: [], clusterMap: new Map(), unclusteredFlavors: [] }
let lastClusterZoom = -1
let projectFrame = 0
let ignoreBackgroundClickUntil = 0
let pitchBeforeGlobe = 36
let cameraSyncFrame = 0
let syncingCamera = false
let sceneTransitionFrame = 0
let inactiveScenePrepFrame = 0
let sceneTransitionMap = null
let sceneTransitionEndHandler = null
let sceneTransitionPrepMap = null
let sceneTransitionPrepHandler = null
let sceneTransitionPrepEvents = []
let sceneTransitionPrepTimer = 0
let sceneTransitionToken = 0
let sceneSnapshotTimer = 0

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

const MAP_STYLE = {
  version: 8,
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
      ATMOSPHERE_LOW_ZOOM,
      0.24,
      ATMOSPHERE_HIGH_ZOOM,
      0,
    ],
  },
  sources: {
    'hyp-tiles': {
      type: 'raster',
      tiles: ['/tiles/raster/{z}/{x}/{y}.png'],
      tileSize: 512,
      minzoom: 0,
      maxzoom: 8,
      bounds: [-180, -POLAR_TILE_LIMIT, 180, POLAR_TILE_LIMIT],
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

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

function hexToRgb(hex, a = 255) {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
    a,
  ]
}

function createFeatureCollection(features = []) {
  return {
    type: 'FeatureCollection',
    features,
  }
}


function buildGlobeNodeData(flavorList, activeNodeId, clusterData = null) {
  const features = []

  // 聚合节点 feature
  if (clusterData?.clusters?.length) {
    clusterData.clusters.forEach(cluster => {
      features.push({
        type: 'Feature',
        properties: {
          id: cluster.id,
          kind: 'cluster',
          count: cluster.count,
          color: cluster.dominantColor,
          haloRadius: 62,
          glowRadius: 44,
          dotRadius: 10,
          haloOpacity: 0.36,
          glowOpacity: 0.92,
        },
        geometry: {
          type: 'Point',
          coordinates: cluster.center,
        },
      })
    })
  }

  // 个体节点 feature
  flavorList.forEach(flavor => {
    const selected = activeNodeId === flavor.id
    features.push({
      type: 'Feature',
      properties: {
        id: flavor.id,
        kind: 'node',
        dish: flavor.dish,
        city: flavor.city,
        color: flavor.color,
        haloRadius: selected ? 46 : 30,
        glowRadius: selected ? 26 : 17,
        dotRadius: selected ? 6.4 : 4.2,
        haloOpacity: selected ? 0.32 : 0.18,
        glowOpacity: selected ? 0.84 : 0.56,
      },
      geometry: {
        type: 'Point',
        coordinates: flavor.coordinates,
      },
    })
  })

  return createFeatureCollection(features)
}

function handleClusterClick(cluster) {
  const activeMap = getActiveMap()
  if (!activeMap) return

  const targetZoom = Math.min(activeMap.getZoom() + 2, 5.5)
  activeMap.flyTo({
    center: cluster.center,
    zoom: targetZoom,
    duration: 800,
    essential: true,
  })
}


function buildLayers(flavorList, vis, activeNodeId, sceneKind = 'flat') {
  const layers = []
  if (sceneKind === 'globe') return layers

  const map = getActiveMap()
  const zoom = map ? map.getZoom() : 3.5
  updateClusterState(zoom)
  const cOpacity = getClusterOpacity(zoom)

  if (vis.L3) {
    layers.push(
      new ScatterplotLayer({
        id: 'node-aura-layer',
        data: flavorList,
        getPosition: d => d.coordinates,
        getRadius: d => (activeNodeId === d.id ? 96000 : 56000),
        radiusUnits: 'meters',
        getFillColor: d => hexToRgb(d.color, activeNodeId === d.id ? 54 : 24),
        stroked: false,
        pickable: false,
        parameters: ARC_BLEND_PARAMETERS,
      }),
      new ScatterplotLayer({
        id: 'node-glow-layer',
        data: flavorList,
        getPosition: d => d.coordinates,
        getRadius: d => (activeNodeId === d.id ? 46000 : 28000),
        radiusUnits: 'meters',
        getFillColor: d => hexToRgb(d.color, activeNodeId === d.id ? 112 : 62),
        stroked: false,
        pickable: false,
        parameters: ARC_BLEND_PARAMETERS,
      }),
      new ScatterplotLayer({
        id: 'node-core-layer',
        data: flavorList,
        getPosition: d => d.coordinates,
        getRadius: d => (activeNodeId === d.id ? 9800 : 6200),
        radiusUnits: 'meters',
        getFillColor: d => hexToRgb(d.color, activeNodeId === d.id ? 235 : 190),
        getLineColor: () => [255, 252, 246, 210],
        getLineWidth: d => (activeNodeId === d.id ? 3 : 1.5),
        lineWidthUnits: 'pixels',
        stroked: true,
        pickable: false,
        parameters: ARC_BLEND_PARAMETERS,
      }),
    )

    // ---- 聚合叠加层 ----
    if (cOpacity > 0.01 && clusterState.clusters.length > 0) {
      layers.push(
        new ScatterplotLayer({
          id: 'cluster-aura-layer',
          data: clusterState.clusters,
          getPosition: d => d.center,
          getRadius: 140000,
          radiusUnits: 'meters',
          getFillColor: d => hexToRgb(d.dominantColor, Math.round(68 * cOpacity)),
          stroked: false,
          pickable: false,
          parameters: ARC_BLEND_PARAMETERS,
        }),
        new ScatterplotLayer({
          id: 'cluster-glow-layer',
          data: clusterState.clusters,
          getPosition: d => d.center,
          getRadius: 72000,
          radiusUnits: 'meters',
          getFillColor: d => hexToRgb(d.dominantColor, Math.round(140 * cOpacity)),
          stroked: false,
          pickable: false,
          parameters: ARC_BLEND_PARAMETERS,
        }),
        new ScatterplotLayer({
          id: 'cluster-core-layer',
          data: clusterState.clusters,
          getPosition: d => d.center,
          getRadius: 16000,
          radiusUnits: 'meters',
          getFillColor: d => hexToRgb(d.dominantColor, Math.round(240 * cOpacity)),
          getLineColor: () => [255, 252, 246, Math.round(230 * cOpacity)],
          getLineWidth: 2.8,
          lineWidthUnits: 'pixels',
          stroked: true,
          pickable: true,
          parameters: ARC_BLEND_PARAMETERS,
          onClick: ({ object }) => {
            if (!object) return
            consumeMapClick()
            handleClusterClick(object)
          },
          onHover: ({ object, x, y }) => {
            tooltip.value = object
              ? { visible: true, x: x + 14, y: y - 10, text: `${object.count} 个风味节点 (点击展开)` }
              : { ...tooltip.value, visible: false }
          },
        }),
        new TextLayer({
          id: 'cluster-count-layer',
          data: clusterState.clusters,
          getPosition: d => d.center,
          getText: d => String(d.count),
          getSize: 16,
          getColor: [255, 255, 255, Math.round(255 * cOpacity)],
          getTextAnchor: 'middle',
          getAlignmentBaseline: 'center',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          fontWeight: 700,
          pickable: false,
          parameters: ARC_BLEND_PARAMETERS,
        }),
      )
    }
  }

  return layers
}

function sceneList() {
  return [flatScene, globeScene].filter(s => s?.loaded)
}

function getScene(kind) {
  return kind === 'globe' ? globeScene : flatScene
}

function getActiveScene() {
  return getScene(activeScene.value)
}

function getActiveMap() {
  return getActiveScene()?.map ?? null
}

function updateMapDebugState() {
  mapDebugTick.value += 1
}

function createMapStyle(kind) {
  const style = JSON.parse(JSON.stringify(MAP_STYLE))
  style.projection = { type: kind === 'globe' ? 'globe' : 'mercator' }
  return style
}

function getCameraOptions(sourceMap, targetKind) {
  const center = sourceMap.getCenter()
  return {
    center: [center.lng, center.lat],
    zoom: sourceMap.getZoom(),
    bearing: sourceMap.getBearing(),
    pitch: targetKind === 'globe' ? 0 : pitchBeforeGlobe,
  }
}

function jumpSceneToCamera(scene, camera) {
  if (!scene?.map || !camera) return

  syncingCamera = true
  try {
    scene.map.jumpTo({
      center: camera.center,
      zoom: camera.zoom,
      bearing: camera.bearing,
      pitch: camera.pitch,
    })
  } finally {
    syncingCamera = false
  }
}

function syncCameraToScene(sourceScene, targetScene) {
  if (!sourceScene?.map || !targetScene?.map) return

  jumpSceneToCamera(targetScene, getCameraOptions(sourceScene.map, targetScene.kind))
}

function scheduleInactiveCameraSync() {
  if (syncingCamera || cameraSyncFrame) return

  cameraSyncFrame = requestAnimationFrame(() => {
    cameraSyncFrame = 0
    const sourceScene = getActiveScene()
    const targetScene = sourceScene?.kind === 'globe' ? flatScene : globeScene
    syncCameraToScene(sourceScene, targetScene)
  })
}

function smoothStep(value) {
  const t = Math.min(Math.max(value, 0), 1)
  return t * t * (3 - 2 * t)
}

function syncSceneVisualState() {
  if (isSceneTransitioning.value) return
  updateMapDebugState()
}

function getVisibleSceneKind() {
  return isSceneTransitioning.value ? 'flat' : activeScene.value
}

function isSceneActive(kind) {
  return getVisibleSceneKind() === kind
}

function isSceneVisible(kind) {
  return getVisibleSceneKind() === kind
}

function getSceneStyle(kind) {
  return { opacity: isSceneVisible(kind) ? 1 : 0 }
}

function setSceneProjection(scene, projection) {
  if (!scene?.map) return

  try {
    scene.map.setProjection(projection)
  } catch (err) {
    console.warn(`Projection update skipped for ${scene.kind}:`, err.message)
  }
}

function setStableSceneProjections() {
  setSceneProjection(flatScene, { type: 'mercator' })
  setSceneProjection(globeScene, { type: 'globe' })
  flatScene?.map?.setRenderWorldCopies(true)
  globeScene?.map?.setRenderWorldCopies(false)
}

function getMorphProjection(direction, startZoom, endZoom) {
  if (direction === 'plane-to-globe') {
    return {
      type: [
        'interpolate',
        ['linear'],
        ['zoom'],
        endZoom,
        'vertical-perspective',
        startZoom,
        'mercator',
      ],
    }
  }

  return {
    type: [
      'interpolate',
      ['linear'],
      ['zoom'],
      startZoom,
      'vertical-perspective',
      endZoom,
      'mercator',
    ],
  }
}

function getViewportCenterAnchor(sourceMap) {
  const canvas = sourceMap.getCanvas()
  const container = sourceMap.getContainer()
  const width = canvas?.clientWidth || container?.clientWidth || 0
  const height = canvas?.clientHeight || container?.clientHeight || 0
  const anchor = sourceMap.unproject([width / 2, height / 2])
  return [anchor.lng, anchor.lat]
}

function getAnchoredTransitionCamera(sourceMap, targetKind) {
  const startZoom = sourceMap.getZoom()
  const direction = targetKind === 'globe' ? 'plane-to-globe' : 'globe-to-plane'
  const endZoom = direction === 'plane-to-globe'
    ? Math.max(startZoom - SCENE_MORPH_ZOOM_SPAN, 0.05)
    : startZoom + SCENE_MORPH_ZOOM_SPAN

  return {
    direction,
    center: getViewportCenterAnchor(sourceMap),
    startZoom,
    endZoom,
    bearing: sourceMap.getBearing(),
    startPitch: sourceMap.getPitch(),
    endPitch: targetKind === 'globe' ? 0 : pitchBeforeGlobe,
  }
}

function getTransitionStartCamera(transitionCamera) {
  return {
    center: transitionCamera.center,
    zoom: transitionCamera.startZoom,
    bearing: transitionCamera.bearing,
    pitch: transitionCamera.startPitch,
  }
}

function getStableCameraForScene(transitionCamera, kind) {
  return {
    center: transitionCamera.center,
    zoom: transitionCamera.endZoom,
    bearing: transitionCamera.bearing,
    pitch: kind === 'globe' ? 0 : pitchBeforeGlobe,
  }
}

function syncTransitionCameraFromScene(scene, transitionCamera) {
  if (!scene?.map || !transitionCamera) return

  const center = scene.map.getCenter()
  transitionCamera.center = [center.lng, center.lat]
  transitionCamera.endZoom = scene.map.getZoom()
  transitionCamera.bearing = scene.map.getBearing()
}

function prepareStableScene(scene, kind, transitionCamera) {
  if (!scene?.map) return

  setSceneProjection(scene, { type: kind === 'globe' ? 'globe' : 'mercator' })
  scene.map.setRenderWorldCopies(kind === 'flat')
  setMapLayerVisibility('polar-caps', kind === 'globe' && layerVisibility.value.L0, scene)
  jumpSceneToCamera(scene, getStableCameraForScene(transitionCamera, kind))
}

function prepareMorphPolarCaps(scene, transitionCamera) {
  if (!scene?.map) return

  const lowerZoom = Math.min(transitionCamera.startZoom, transitionCamera.endZoom)
  const upperZoom = Math.max(transitionCamera.startZoom, transitionCamera.endZoom)
  try {
    scene.map.setPaintProperty('polar-caps', 'fill-opacity', [
      'interpolate',
      ['linear'],
      ['zoom'],
      lowerZoom,
      1,
      upperZoom,
      0,
    ])
  } catch (_) {
    // polar caps layer may not be present yet
  }
  setMapLayerVisibility('polar-caps', layerVisibility.value.L0, scene)
}

function prepareMorphScene(scene, transitionCamera, syncCamera = true) {
  if (!scene?.map) return

  scene.map.stop()
  setSceneProjection(scene, getMorphProjection(
    transitionCamera.direction,
    transitionCamera.startZoom,
    transitionCamera.endZoom,
  ))
  scene.map.setRenderWorldCopies(true)
  prepareMorphPolarCaps(scene, transitionCamera)
  if (syncCamera) {
    jumpSceneToCamera(scene, getTransitionStartCamera(transitionCamera))
  }
}

function getTransitionProgress(scene, transitionCamera) {
  if (!scene?.map) return 0

  const range = transitionCamera.endZoom - transitionCamera.startZoom
  if (Math.abs(range) < 0.0001) return 1
  return Math.min(Math.max((scene.map.getZoom() - transitionCamera.startZoom) / range, 0), 1)
}

function monitorSceneTransition(scene, transitionCamera) {
  sceneTransitionProgress.value = getTransitionProgress(scene, transitionCamera)
  updateMapDebugState()
  scheduleProjectedNodesUpdate()

  if (!isSceneTransitioning.value) return
  sceneTransitionFrame = requestAnimationFrame(() => monitorSceneTransition(scene, transitionCamera))
}

function clearSceneTransitionEndHandler() {
  if (sceneTransitionMap && sceneTransitionEndHandler) {
    sceneTransitionMap.off('moveend', sceneTransitionEndHandler)
  }
  sceneTransitionMap = null
  sceneTransitionEndHandler = null
}

function clearSceneTransitionPrep() {
  if (sceneTransitionPrepMap && sceneTransitionPrepHandler) {
    sceneTransitionPrepEvents.forEach(eventName => {
      sceneTransitionPrepMap.off(eventName, sceneTransitionPrepHandler)
    })
  }
  if (sceneTransitionPrepTimer) {
    clearTimeout(sceneTransitionPrepTimer)
  }
  sceneTransitionPrepMap = null
  sceneTransitionPrepHandler = null
  sceneTransitionPrepEvents = []
  sceneTransitionPrepTimer = 0
}

function hideSceneSnapshot() {
  if (sceneSnapshotTimer) {
    clearTimeout(sceneSnapshotTimer)
    sceneSnapshotTimer = 0
  }
  sceneSnapshot.value = { visible: false, src: '' }
}

function showSceneSnapshot(scene, duration = 90) {
  const canvas = scene?.map?.getCanvas?.()
  if (!canvas) return

  try {
    const src = canvas.toDataURL('image/png')
    if (!src || src.length < 5000) return
    sceneSnapshot.value = { visible: true, src }
    if (sceneSnapshotTimer) clearTimeout(sceneSnapshotTimer)
    sceneSnapshotTimer = window.setTimeout(hideSceneSnapshot, duration)
  } catch (_) {
    hideSceneSnapshot()
  }
}

function isSceneTilesReady(scene) {
  if (!scene?.map) return true

  try {
    return scene.map.loaded() && scene.map.areTilesLoaded()
  } catch (_) {
    return false
  }
}

function afterSceneRendered(scene, callback, options = {}) {
  if (!scene?.map) {
    callback()
    return
  }

  const { requireTiles = false, timeout = SCENE_RENDER_WAIT_TIMEOUT } = options
  const token = sceneTransitionToken
  let complete = false
  const finish = (force = false) => {
    if (complete || token !== sceneTransitionToken) return
    if (requireTiles && !force && !isSceneTilesReady(scene)) return
    complete = true
    clearSceneTransitionPrep()
    requestAnimationFrame(() => {
      if (token === sceneTransitionToken) {
        callback()
      }
    })
  }

  clearSceneTransitionPrep()
  sceneTransitionPrepMap = scene.map
  sceneTransitionPrepHandler = () => finish(false)
  sceneTransitionPrepEvents = requireTiles
    ? ['render', 'idle', 'sourcedata']
    : ['render']
  sceneTransitionPrepEvents.forEach(eventName => {
    scene.map.on(eventName, sceneTransitionPrepHandler)
  })
  scene.map.triggerRepaint()
  if (!requireTiles || isSceneTilesReady(scene)) {
    sceneTransitionPrepTimer = window.setTimeout(() => finish(false), 0)
  } else {
    sceneTransitionPrepTimer = window.setTimeout(() => finish(true), timeout)
  }
}

function scheduleInactiveScenePrep(targetKind, transitionCamera) {
  cancelAnimationFrame(inactiveScenePrepFrame)
  inactiveScenePrepFrame = requestAnimationFrame(() => {
    inactiveScenePrepFrame = 0
    const inactiveScene = targetKind === 'globe' ? flatScene : globeScene
    prepareStableScene(inactiveScene, inactiveScene?.kind, transitionCamera)
  })
}

function toggleSceneMode() {
  const targetKind = activeScene.value === 'flat' ? 'globe' : 'flat'
  startSceneTransition(targetKind)
}

function runSceneTransition(targetKind, fromScene, transitionScene, transitionCamera) {
  transitionToScene.value = targetKind
  sceneTransitionProgress.value = 0
  isSceneTransitioning.value = true
  tooltip.value = { ...tooltip.value, visible: false }
  updateMapDebugState()

  sceneTransitionMap = transitionScene.map
  sceneTransitionEndHandler = () => finishSceneTransition(targetKind, transitionCamera)
  transitionScene.map.once('moveend', sceneTransitionEndHandler)
  const easeOptions = {
    zoom: transitionCamera.endZoom,
    bearing: transitionCamera.bearing,
    pitch: transitionCamera.endPitch,
    duration: SCENE_TRANSITION_DURATION,
    easing: smoothStep,
    essential: true,
  }
  if (transitionScene !== fromScene) {
    easeOptions.center = transitionCamera.center
  }
  transitionScene.map.easeTo(easeOptions)
  sceneTransitionFrame = requestAnimationFrame(() => monitorSceneTransition(transitionScene, transitionCamera))
}

function startSceneTransition(targetKind) {
  if (targetKind === activeScene.value || isSceneBusy.value || !sceneToggleReady.value) return

  const fromScene = getActiveScene()
  const targetScene = getScene(targetKind)
  const transitionScene = flatScene
  if (!fromScene?.map || !targetScene?.map || !targetScene.loaded || !transitionScene?.map || !transitionScene.loaded) return

  if (fromScene.kind === 'flat') {
    pitchBeforeGlobe = fromScene.map.getPitch()
  }

  const transitionCamera = getAnchoredTransitionCamera(fromScene.map, targetKind)
  sceneTransitionToken += 1
  clearSceneTransitionEndHandler()
  clearSceneTransitionPrep()
  cancelAnimationFrame(sceneTransitionFrame)
  cancelAnimationFrame(cameraSyncFrame)
  cancelAnimationFrame(inactiveScenePrepFrame)
  cameraSyncFrame = 0
  inactiveScenePrepFrame = 0

  transitionToScene.value = targetKind
  sceneTransitionProgress.value = 0
  tooltip.value = { ...tooltip.value, visible: false }
  updateMapDebugState()

  if (targetScene !== transitionScene) {
    prepareStableScene(targetScene, targetKind, transitionCamera)
    syncGlobeNativeOverlayState()
    targetScene.map.triggerRepaint()
  }

  if (transitionScene !== fromScene) {
    prepareMorphScene(transitionScene, transitionCamera, true)
    afterSceneRendered(
      transitionScene,
      () => runSceneTransition(targetKind, fromScene, transitionScene, transitionCamera),
      { requireTiles: true, timeout: SCENE_TILE_PREWARM_TIMEOUT },
    )
    return
  }

  isSceneTransitioning.value = true
  showSceneSnapshot(transitionScene)
  prepareMorphScene(transitionScene, transitionCamera, false)
  runSceneTransition(targetKind, fromScene, transitionScene, transitionCamera)
}

function finishSceneTransition(targetKind, transitionCamera) {
  const targetScene = getScene(targetKind)
  if (!targetScene?.map || !isSceneTransitioning.value) return

  clearSceneTransitionEndHandler()
  cancelAnimationFrame(sceneTransitionFrame)
  syncTransitionCameraFromScene(flatScene, transitionCamera)
  prepareStableScene(targetScene, targetKind, transitionCamera)
  if (targetScene !== flatScene) {
    afterSceneRendered(
      targetScene,
      () => commitSceneTransition(targetKind, transitionCamera),
      { requireTiles: true, timeout: SCENE_TILE_PREWARM_TIMEOUT },
    )
    return
  }

  commitSceneTransition(targetKind, transitionCamera)
}

function commitSceneTransition(targetKind, transitionCamera) {
  hideSceneSnapshot()
  activeScene.value = targetKind
  isSceneTransitioning.value = false
  transitionToScene.value = null
  sceneTransitionProgress.value = 1
  sceneTransitionFrame = 0
  syncSceneVisualState()
  scheduleProjectedNodesUpdate()
  syncPolarCapsState()
  syncGlobeNativeOverlayState()
  updateMapDebugState()
  scheduleInactiveScenePrep(targetKind, transitionCamera)
}

function handleSceneCameraChange(scene) {
  if (syncingCamera || isSceneTransitioning.value || scene.kind !== activeScene.value) return

  scheduleInactiveCameraSync()
  updateMapDebugState()
  if (scene.kind === 'flat') {
    scheduleProjectedNodesUpdate()
  }
}


function updateClusterState(zoom) {
  if (Math.abs(zoom - lastClusterZoom) < 0.05) return
  lastClusterZoom = zoom
  clusterState = computeClusters(flavors, zoom)
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
  const flatMap = flatScene?.map
  if (!flatMap) return false
  const { width, height } = flatMap.getContainer().getBoundingClientRect()
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

function updateProjectedNodes() {
  const flatMap = flatScene?.map
  const flatSceneVisible = isSceneVisible('flat')
  if (!flatMap || !flatSceneVisible || !layerVisibility.value.L3) {
    projectedNodes.value = []
    return
  }

  const zoom = flatMap.getZoom()
  updateClusterState(zoom)
  const items = []

  // 选中的节点始终单独渲染为 expanded 气泡
  const selectedFlavor = flavors.find(f => f.id === selectedNodeId.value)
  if (selectedFlavor) {
    const point = flatMap.project(selectedFlavor.coordinates)
    if (isPointVisible(point)) {
      const bubble = createBubbleNode(selectedFlavor, point, zoom, 'expanded')
      if (bubble) items.push(bubble)
    }
  }

  // 未聚类的独立节点
  clusterState.unclusteredFlavors.forEach((flavor, index) => {
    flavor.__bubbleIndex = index
    if (flavor.id === selectedNodeId.value) return // 已在上方处理
    const point = flatMap.project(flavor.coordinates)
    if (!isPointVisible(point)) return
    const mode = zoom >= 4.15 ? 'expanded' : (zoom >= 3 ? 'compact' : 'hidden')
    const bubble = createBubbleNode(flavor, point, zoom, mode)
    if (bubble) items.push(bubble)
  })

  // 聚合气泡
  clusterState.clusters.forEach((cluster, index) => {
    const point = flatMap.project(cluster.center)
    if (!isPointVisible(point)) return

    const sorted = [...cluster.members].sort((a, b) => a.city.localeCompare(b.city, 'zh-CN'))
    const citySummary = sorted.slice(0, 3).map(m => m.city).join(' · ')
    const dishSummary = sorted.slice(0, 3).map(m => m.dish).join(' · ')
    const suffix = cluster.count > 3 ? ` 等 ${cluster.count} 个节点` : ` 共 ${cluster.count} 个节点`

    items.push({
      kind: 'cluster',
      id: cluster.id,
      title: `${cluster.count} 个风味节点`,
      city: citySummary,
      dish: '',
      description: `${dishSummary}${suffix}`,
      bubbleImages: sorted.slice(0, 3).map(m => m.bubbleImage),
      count: cluster.count,
      children: sorted,
      coordinates: sorted.map(m => m.coordinates),
      color: cluster.dominantColor,
      x: point.x,
      y: point.y,
      mode: 'cluster',
      selected: false,
      hovered: hoveredBubbleId.value === cluster.id,
      placement: getBubblePlacement(index),
      zIndex: hoveredBubbleId.value === cluster.id ? 22 : 14,
    })
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
  if (!appStore.selectedNode && !appStore.selectedEcozone) return
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

function getFlatNodeFocusOffset(map) {
  if (!map) return [0, 0]
  const { width, height } = map.getContainer().getBoundingClientRect()
  return [
    clamp(width * 0.1, 48, 140),
    clamp(height * 0.08, 36, 90),
  ]
}

function redrawDeck() {
  sceneList().forEach(scene => {
    scene.deckOverlay?.setProps({
      layers: buildLayers(
        flavors,
        layerVisibility.value,
        selectedNodeId.value,
        scene.kind,
      ),
    })
  })
  syncGlobeNativeOverlayState()
}

function syncPolarCapsState() {
  if (flatScene?.loaded) {
    setMapLayerVisibility('polar-caps', isSceneTransitioning.value && layerVisibility.value.L0, flatScene)
  }
  if (globeScene?.loaded) {
    setMapLayerVisibility('polar-caps', activeScene.value === 'globe' && layerVisibility.value.L0, globeScene)
  }
}

function setGeoJsonSourceData(scene, sourceId, data) {
  const source = scene?.map?.getSource(sourceId)
  if (!source?.setData) return

  try {
    source.setData(data)
  } catch (err) {
    console.warn(`GeoJSON source [${sourceId}] update skipped:`, err.message)
  }
}

function addGlobeNativeOverlayLayers(scene) {
  if (scene.kind !== 'globe') return
  const sceneMap = scene.map

  try {
    sceneMap.addSource(GLOBE_NODE_SOURCE_ID, {
      type: 'geojson',
      data: buildGlobeNodeData(flavors, selectedNodeId.value),
    })
    sceneMap.addLayer({
      id: GLOBE_NODE_HALO_LAYER_ID,
      type: 'circle',
      source: GLOBE_NODE_SOURCE_ID,
      layout: { visibility: 'none' },
      paint: {
        'circle-color': ['get', 'color'],
        'circle-radius': ['get', 'haloRadius'],
        'circle-blur': 0.72,
        'circle-opacity': ['get', 'haloOpacity'],
      },
    })
    sceneMap.addLayer({
      id: GLOBE_NODE_GLOW_LAYER_ID,
      type: 'circle',
      source: GLOBE_NODE_SOURCE_ID,
      layout: { visibility: 'none' },
      paint: {
        'circle-color': ['get', 'color'],
        'circle-radius': ['get', 'glowRadius'],
        'circle-blur': 0.42,
        'circle-opacity': ['get', 'glowOpacity'],
      },
    })
    sceneMap.addLayer({
      id: GLOBE_NODE_DOT_LAYER_ID,
      type: 'circle',
      source: GLOBE_NODE_SOURCE_ID,
      layout: { visibility: 'none' },
      paint: {
        'circle-color': ['get', 'color'],
        'circle-radius': ['get', 'dotRadius'],
        'circle-opacity': 0.9,
        'circle-stroke-color': 'rgba(255, 252, 246, 0.92)',
        'circle-stroke-width': 1,
        'circle-stroke-opacity': 0.84,
      },
    })
  } catch (err) {
    console.warn('globe node layer skipped:', err.message)
  }

  // 聚合 count 数字标签 (symbol layer on same source)
  if (!sceneMap.getLayer(GLOBE_CLUSTER_LABEL_LAYER_ID)) {
    sceneMap.addLayer({
      id: GLOBE_CLUSTER_LABEL_LAYER_ID,
      type: 'symbol',
      source: GLOBE_NODE_SOURCE_ID,
      filter: ['==', ['get', 'kind'], 'cluster'],
      layout: {
        visibility: 'none',
        'text-field': ['to-string', ['get', 'count']],
        'text-size': 14,
        'text-font': ['DIN Pro Medium', 'Arial Unicode MS Bold'],
        'text-allow-overlap': true,
        'text-ignore-placement': true,
      },
      paint: {
        'text-color': '#FFFFFF',
        'text-halo-color': 'rgba(0,0,0,0.3)',
        'text-halo-width': 1.5,
      },
    })
  }

  sceneMap.on('click', GLOBE_NODE_DOT_LAYER_ID, e => {
    if (scene.kind !== activeScene.value) return
    const props = e.features?.[0]?.properties
    if (!props) return

    // 聚合点击：飞至聚合中心并放大
    if (props.kind === 'cluster') {
      const cluster = clusterState.clusters.find(c => c.id === props.id)
      if (cluster) {
        consumeMapClick()
        handleClusterClick(cluster)
      }
      return
    }

    const node = flavors.find(item => item.id === props.id)
    if (!node) return
    consumeMapClick()
    appStore.selectNode(node)
  })
  sceneMap.on('mouseenter', GLOBE_NODE_DOT_LAYER_ID, e => {
    if (scene.kind !== activeScene.value) return
    sceneMap.getCanvas().style.cursor = 'pointer'
    const props = e.features?.[0]?.properties
    if (props?.kind === 'cluster') {
      tooltip.value = { visible: true, x: e.point.x + 14, y: e.point.y - 10, text: `${props.count} 个风味节点 (点击展开)` }
    } else if (props?.dish) {
      tooltip.value = { visible: true, x: e.point.x + 14, y: e.point.y - 10, text: `${props.city} · ${props.dish}` }
    }
  })
  sceneMap.on('mouseleave', GLOBE_NODE_DOT_LAYER_ID, () => {
    sceneMap.getCanvas().style.cursor = ''
    tooltip.value = { ...tooltip.value, visible: false }
  })
}

function syncGlobeNativeOverlayState() {
  if (!globeScene?.loaded) return

  const canShowGlobeOverlay = activeScene.value === 'globe' || transitionToScene.value === 'globe'
  const showL3 = canShowGlobeOverlay && layerVisibility.value.L3

  const globeZoom = globeScene.map.getZoom()
  updateClusterState(globeZoom)

  setGeoJsonSourceData(globeScene, GLOBE_NODE_SOURCE_ID, buildGlobeNodeData(flavors, selectedNodeId.value, clusterState))

  setMapLayerVisibility(GLOBE_NODE_HALO_LAYER_ID, showL3, globeScene)
  setMapLayerVisibility(GLOBE_NODE_GLOW_LAYER_ID, showL3, globeScene)
  setMapLayerVisibility(GLOBE_NODE_DOT_LAYER_ID, showL3, globeScene)
  setMapLayerVisibility(GLOBE_CLUSTER_LABEL_LAYER_ID, showL3, globeScene)
}



async function addVectorLayers(scene) {
  const sceneMap = scene.map
  const physLayers = [
    { id: 'coastline', url: '/tiles/vector/coastline', type: 'line', paint: { 'line-color': '#8A7560', 'line-width': 0.6, 'line-opacity': 0.65 } },
    { id: 'rivers', url: '/tiles/vector/rivers', type: 'line', paint: { 'line-color': '#5BA0B8', 'line-width': 0.4, 'line-opacity': 0.6 } },
  ]

  for (const layer of physLayers) {
    try {
      sceneMap.addSource(layer.id, { type: 'geojson', data: layer.url })
      sceneMap.addLayer({ id: layer.id, type: layer.type, source: layer.id, paint: layer.paint })
    } catch (err) {
      console.warn(`Vector layer [${layer.id}] skipped:`, err.message)
    }
  }

  try {
    sceneMap.addSource('ecoregions', { type: 'geojson', data: '/tiles/vector/ecoregions' })
    sceneMap.addLayer({
      id: 'ecoregions',
      type: 'line',
      source: 'ecoregions',
      paint: { 'line-color': L1_BOUNDARY_COLOR, 'line-width': 1.35, 'line-opacity': L1_OPACITY_WEAK },
    })
  } catch (err) {
    console.warn('ecoregions skipped:', err.message)
  }

  sceneMap.on('click', 'ecoregions', e => {
    if (scene.kind !== activeScene.value) return
    const props = e.features?.[0]?.properties
    if (props) {
      consumeMapClick()
      appStore.selectEcozone(props)
    }
  })
  sceneMap.on('mouseenter', 'ecoregions', () => {
    if (scene.kind === activeScene.value) {
      sceneMap.getCanvas().style.cursor = 'pointer'
    }
  })
  sceneMap.on('mouseleave', 'ecoregions', () => { sceneMap.getCanvas().style.cursor = '' })
}

function addPolarCapLayer(scene) {
  const sceneMap = scene.map
  try {
    sceneMap.addSource('polar-caps', { type: 'geojson', data: POLAR_CAPS_GEOJSON })
    sceneMap.addLayer({
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
        'fill-opacity': 1,
      },
    })
  } catch (err) {
    console.warn('polar caps skipped:', err.message)
  }
}

function createMapScene(kind, container) {
  const scene = {
    kind,
    map: new maplibregl.Map({
      container,
      style: createMapStyle(kind),
      center: INITIAL_MAP_CENTER,
      zoom: 3.5,
      pitch: kind === 'globe' ? 0 : 36,
      bearing: -8,
      antialias: true,
      attributionControl: false,
    }),
    deckOverlay: null,
    loaded: false,
  }

  scene.map.setRenderWorldCopies(kind === 'flat')
  scene.map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right')
  scene.map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right')

  scene.map.on('load', async () => {
    scene.loaded = true
    rasterReady.value = true

    scene.deckOverlay = new MapboxOverlay({
      interleaved: true,
      effects: [lightingEffect],
      layers: buildLayers(flavors, layerVisibility.value, selectedNodeId.value, scene.kind),
      getCursor: ({ isHovering }) => (isHovering ? 'pointer' : 'grab'),
    })

    scene.map.addControl(scene.deckOverlay)
    addPolarCapLayer(scene)
    await addVectorLayers(scene)
    addGlobeNativeOverlayLayers(scene)
    syncBaseLayerState()
    syncEcoregionState()
    redrawDeck()

    if (kind === 'globe' && flatScene?.map) {
      syncCameraToScene(flatScene, scene)
    }

    if (kind === 'flat') {
      updateProjectedNodes()
    }

    setStableSceneProjections()
    syncSceneVisualState()
    updateMapDebugState()
  })

  scene.map.on('move', () => handleSceneCameraChange(scene))
  scene.map.on('zoom', () => handleSceneCameraChange(scene))
  scene.map.on('rotate', () => handleSceneCameraChange(scene))
  scene.map.on('pitch', () => handleSceneCameraChange(scene))
  scene.map.on('resize', () => {
    if (kind === 'flat') scheduleProjectedNodesUpdate()
  })
  scene.map.on('render', () => {
    if (kind === 'flat') updateProjectedNodes()
  })
  scene.map.on('click', () => {
    if (kind !== activeScene.value) return
    handleMapBackgroundClick()
  })

  return scene
}

onMounted(async () => {
  const fRes = await fetch('/api/flavors')
  flavors = await fRes.json()
  appStore.setFlavors(flavors)

  fetch('/tiles/status')
    .then(r => r.json())
    .then(s => {
      rasterReady.value = s.raster_ready
    })
    .catch(() => {
      rasterReady.value = false
    })

  flatScene = createMapScene('flat', flatMapContainer.value)
  globeScene = createMapScene('globe', globeMapContainer.value)
  window.addEventListener('keydown', handleWindowKeydown)
})

onUnmounted(() => {
  cancelAnimationFrame(projectFrame)
  cancelAnimationFrame(cameraSyncFrame)
  cancelAnimationFrame(sceneTransitionFrame)
  cancelAnimationFrame(inactiveScenePrepFrame)
  clearSceneTransitionEndHandler()
  clearSceneTransitionPrep()
  hideSceneSnapshot()
  window.removeEventListener('keydown', handleWindowKeydown)
  flatScene?.map.remove()
  globeScene?.map.remove()
})

function setL1Strength(opacity, scene = null) {
  const targets = scene ? [scene] : sceneList()

  targets.forEach(target => {
    try {
      target.map.setPaintProperty('ecoregions', 'line-opacity', opacity)
      target.map.setPaintProperty('ecoregions', 'line-color', opacity > 0.5 ? L1_BOUNDARY_COLOR_STRONG : L1_BOUNDARY_COLOR)
      target.map.setPaintProperty('ecoregions', 'line-width', opacity > 0.5 ? 1.65 : 1.25)
    } catch (_) {
      // ecoregions layer may not be added yet
    }
  })
}

function setMapLayerVisibility(id, visible, scene = null) {
  const targets = scene ? [scene] : sceneList()

  targets.forEach(target => {
    try {
      target.map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none')
    } catch (_) {
      // layer may not be added yet
    }
  })
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
  () => [appStore.selectedNode, appStore.selectedEcozone],
  ([node, ecozone]) => {
    const activeMap = getActiveMap()

    if (node && activeMap) {
      const flatFocus = activeScene.value === 'flat'
      const flyOptions = {
        center: node.coordinates,
        zoom: flatFocus ? 5.75 : 5.5,
        pitch: flatFocus ? 48 : 0,
        bearing: flatFocus ? -12 : activeMap.getBearing(),
        duration: flatFocus ? 1450 : 1200,
        essential: true,
      }

      if (flatFocus) {
        flyOptions.offset = getFlatNodeFocusOffset(activeMap)
        flyOptions.easing = smoothStep
      }

      activeMap.flyTo(flyOptions)
    }

    redrawDeck()
    scheduleProjectedNodesUpdate()
  },
)

watch(
  () => [
    layerVisibility.value.L0,
    layerVisibility.value.L1,

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
      background: appStore.l1Emphasis ? L1_BOUNDARY_COLOR_STRONG : L1_BOUNDARY_COLOR,
      borderRadius: '999px',
      display: 'inline-block',
      opacity: !layerVisibility.value.L1 ? 0.15 : (appStore.l1Emphasis ? L1_OPACITY_STRONG : L1_OPACITY_WEAK),
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
  { key: 'L3', label: 'L3 节点', enabled: layerEnabled.value.L3, contextual: false },
])
</script>

<style scoped>
.map-page {
  background: #c8dde8;
  overflow: hidden;
}

.map-scene {
  position: absolute;
  inset: 0;
  z-index: 1;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

.map-scene.active {
  z-index: 2;
  pointer-events: auto;
}

.map-scene.visible {
  visibility: visible;
}

.map-page.transitioning .map-scene {
  pointer-events: none;
}

.map-container {
  background: #d9e7ec;
}

.scene-snapshot {
  position: absolute;
  inset: 0;
  z-index: 3;
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
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

.bubble-node::before,
.bubble-node::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  border-radius: 50%;
  pointer-events: none;
}

.bubble-node::before {
  width: 104px;
  height: 104px;
  transform: translate(-50%, -50%);
  background:
    radial-gradient(circle, color-mix(in srgb, var(--node-color) 34%, transparent) 0%, color-mix(in srgb, var(--node-color) 18%, transparent) 32%, transparent 70%);
  filter: blur(7px);
  opacity: 0.72;
  animation: nodeAuraPulse 3.8s ease-in-out infinite;
}

.bubble-node::after {
  width: 22px;
  height: 22px;
  transform: translate(-50%, -50%);
  border: 1px solid color-mix(in srgb, var(--node-color) 58%, white);
  background:
    radial-gradient(circle, rgba(255,255,255,0.96) 0%, color-mix(in srgb, var(--node-color) 74%, white) 44%, color-mix(in srgb, var(--node-color) 58%, transparent) 100%);
  box-shadow:
    0 0 0 5px color-mix(in srgb, var(--node-color) 16%, transparent),
    0 0 22px color-mix(in srgb, var(--node-color) 46%, transparent);
  opacity: 0.86;
}

.bubble-node.hovered::before,
.bubble-node.selected::before {
  width: 142px;
  height: 142px;
  opacity: 0.96;
  filter: blur(10px);
}

.bubble-node.selected::after {
  width: 30px;
  height: 30px;
  border-width: 2px;
  box-shadow:
    0 0 0 7px color-mix(in srgb, var(--node-color) 18%, transparent),
    0 0 34px color-mix(in srgb, var(--node-color) 62%, transparent);
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
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.34);
  background:
    linear-gradient(180deg, rgba(255,252,248,0.92) 0%, rgba(255,249,243,0.80) 100%),
    radial-gradient(circle at 18% 20%, color-mix(in srgb, var(--node-color) 16%, transparent) 0%, transparent 46%);
  box-shadow:
    0 18px 46px rgba(34, 24, 14, 0.13),
    0 0 26px color-mix(in srgb, var(--node-color) 10%, transparent),
    inset 0 1px 0 rgba(255,255,255,0.68);
  backdrop-filter: blur(16px) saturate(1.08);
  -webkit-backdrop-filter: blur(16px) saturate(1.08);
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

.bubble-node.north-east {
  --poi-photo-x: 24px;
  --poi-photo-rotate: -1.25deg;
  --poi-photo-origin: left bottom;
}

.bubble-node.north-west {
  --poi-photo-x: calc(-100% - 24px);
  --poi-photo-rotate: 1.25deg;
  --poi-photo-origin: right bottom;
}

.poi-photo-card {
  position: absolute;
  bottom: 26px;
  display: block;
  width: clamp(232px, 24vw, 326px);
  border-radius: 8px;
  border: 1px solid color-mix(in srgb, var(--node-color) 36%, rgba(255, 253, 239, 0.7));
  background:
    linear-gradient(180deg, rgba(15, 25, 18, 0.92) 0%, rgba(9, 17, 12, 0.86) 100%),
    radial-gradient(circle at 22% 18%, color-mix(in srgb, var(--node-color) 24%, transparent) 0%, transparent 54%);
  box-shadow:
    0 20px 54px rgba(12, 17, 10, 0.34),
    0 0 0 1px rgba(255, 253, 239, 0.16),
    0 0 42px color-mix(in srgb, var(--node-color) 28%, transparent);
  overflow: hidden;
  pointer-events: none;
  transform-origin: var(--poi-photo-origin, left bottom);
  transform: translate3d(var(--poi-photo-x, 24px), 0, 0) rotate(var(--poi-photo-rotate, -1deg)) scale(1);
  animation: poiPhotoReveal 680ms cubic-bezier(.19, 1, .22, 1) both;
}

.poi-photo-card::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(230, 255, 195, 0.18), transparent 24%, transparent 76%, rgba(230, 255, 195, 0.1)),
    linear-gradient(180deg, rgba(255, 255, 255, 0.18), transparent 28%);
  mix-blend-mode: screen;
}

.poi-photo-frame {
  position: relative;
  display: block;
  aspect-ratio: 16 / 9;
  background: rgba(8, 14, 10, 0.92);
  overflow: hidden;
}

.poi-photo-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.92) contrast(1.08) brightness(0.9);
  transform: scale(1.02);
}

.poi-photo-caption {
  display: grid;
  gap: 2px;
  padding: 8px 10px 9px;
  text-align: left;
}

.poi-photo-city {
  font-size: 10px;
  line-height: 1;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: color-mix(in srgb, var(--node-color) 52%, #f4f7d4);
}

.poi-photo-title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--font-serif);
  font-size: 15px;
  line-height: 1.25;
  color: rgba(250, 255, 226, 0.94);
}

.bubble-thumb-wrap {
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255,255,255,0.74);
  box-shadow:
    0 0 0 1px color-mix(in srgb, var(--node-color) 16%, transparent),
    0 10px 26px color-mix(in srgb, var(--node-color) 16%, transparent),
    inset 0 1px 0 rgba(255,255,255,0.6);
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
    0 22px 58px rgba(34, 24, 14, 0.18),
    0 0 0 1px color-mix(in srgb, var(--node-color) 26%, transparent),
    0 0 34px color-mix(in srgb, var(--node-color) 16%, transparent),
    inset 0 1px 0 rgba(255,255,255,0.74);
}

.bubble-node.selected .bubble-card {
  box-shadow:
    0 24px 64px rgba(34, 24, 14, 0.2),
    0 0 0 1px color-mix(in srgb, var(--node-color) 42%, transparent),
    0 0 42px color-mix(in srgb, var(--node-color) 26%, transparent);
}

.bubble-node.selected .bubble-title,
.bubble-node.hovered .bubble-title {
  color: color-mix(in srgb, var(--node-color) 62%, #2e2218);
}

@keyframes nodeAuraPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(0.92);
    opacity: 0.58;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.08);
    opacity: 0.9;
  }
}

@keyframes poiPhotoReveal {
  0% {
    opacity: 0;
    clip-path: inset(0 68% 0 0 round 8px);
    transform: translate3d(var(--poi-photo-x, 24px), 18px, 0) rotate(var(--poi-photo-rotate, -1deg)) scale(0.64);
    filter: blur(4px);
  }
  58% {
    opacity: 1;
    clip-path: inset(0 0 0 0 round 8px);
    transform: translate3d(var(--poi-photo-x, 24px), -2px, 0) rotate(var(--poi-photo-rotate, -1deg)) scale(1.035);
    filter: blur(0);
  }
  100% {
    opacity: 1;
    clip-path: inset(0 0 0 0 round 8px);
    transform: translate3d(var(--poi-photo-x, 24px), 0, 0) rotate(var(--poi-photo-rotate, -1deg)) scale(1);
    filter: blur(0);
  }
}

@media (max-width: 720px) {
  .poi-photo-card {
    width: min(238px, 62vw);
    bottom: 22px;
  }

  .poi-photo-title {
    font-size: 13px;
  }
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

:deep(.maplibregl-ctrl-bottom-right) {
  left: 28px !important;
  right: auto !important;
  bottom: 84px !important;
}

:deep(.maplibregl-ctrl-group) {
  background: rgba(255, 252, 248, 0.78) !important;
  border: 1px solid rgba(180, 165, 140, 0.22) !important;
  border-radius: 10px !important;
  box-shadow: 0 10px 32px rgba(35, 25, 12, 0.08) !important;
  backdrop-filter: var(--blur-sm) !important;
  margin: 0 !important;
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

.scene-toggle {
  position: absolute;
  left: 172px;
  bottom: 28px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 0 14px;
  border: 1px solid rgba(180, 165, 140, 0.2);
  border-radius: 999px;
  cursor: pointer;
  z-index: 10;
  color: var(--text-mid);
  font-size: 11px;
  letter-spacing: 0.12em;
  transition:
    transform var(--transition),
    box-shadow var(--transition),
    background var(--transition),
    color var(--transition),
    opacity var(--transition);
}

.scene-toggle:hover:not(:disabled),
.scene-toggle.transitioning {
  transform: translateY(-1px);
  box-shadow: 0 14px 36px rgba(34, 23, 10, 0.12);
  background: rgba(255, 252, 248, 0.94);
  color: var(--text);
}

.scene-toggle:disabled {
  cursor: wait;
  opacity: 0.64;
}

.scene-toggle-icon {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: var(--amber);
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex: 0 0 auto;
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

.debug-readout {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.debug-readout-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 10px;
  letter-spacing: 0.08em;
}

.debug-readout-label {
  color: rgba(255, 255, 255, 0.42);
  text-transform: uppercase;
}

.debug-readout-value {
  color: rgba(255, 255, 255, 0.9);
  font-variant-numeric: tabular-nums;
  font-family: 'Inter', sans-serif;
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
  :deep(.maplibregl-ctrl-bottom-right) {
    left: 18px !important;
  }

  .legend-panel {
    width: 196px;
    left: 18px;
  }

  .devtools-trigger,
  .scene-toggle,
  .devtools-panel {
    left: 18px;
  }

  .scene-toggle {
    bottom: 80px;
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
