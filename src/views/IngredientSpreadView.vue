<template>
  <div class="spread-page" :class="{ 'sidebar-open': !sidebarCollapsed }">
    <div ref="mapContainer" class="spread-map" />
    <div class="spread-vignette spread-vignette-top" aria-hidden="true" />
    <div class="spread-vignette spread-vignette-bottom" aria-hidden="true" />

    <div class="map-overlay-info" v-if="hasAnyData">
      <div class="overlay-kicker">{{ isOverview ? '食材传播总览' : '传播路径总览' }}</div>
      <div class="overlay-year" :style="{ color: activeColor }">{{ displayedYearRange }}</div>
      <div class="overlay-location">{{ overlayTitle }}</div>
    </div>

    <div class="spread-route-caption" v-if="hasAnyData">
      <div class="caption-kicker">{{ isOverview ? 'Overview' : (currentEvent ? `历史 ${activeEventIndex + 1} / ${timeline.length}` : 'Route') }}</div>
      <div class="caption-title">
        {{ isOverview ? `${shownIngredients.length} 种食材传播线同时显示` : captionTitle }}
      </div>
      <div class="caption-route" :style="{ color: activeColor }">
        {{ isOverview ? '点击食材卡片或地图节点查看单条传播路径' : captionRoute }}
      </div>
    </div>

    <button class="sidebar-toggle" @click="toggleSidebar" :class="{ open: !sidebarCollapsed }" :title="sidebarCollapsed ? '展开面板' : '收起面板'">
      <span class="toggle-icon">{{ sidebarCollapsed ? '◀' : '▶' }}</span>
      <span class="toggle-label">{{ sidebarCollapsed ? '展开' : '收起' }}</span>
    </button>

    <aside class="spread-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="sidebar-close-btn" @click="sidebarCollapsed = true" title="收起面板">✕</button>
        <div class="ingredient-selector" v-if="ingredients.length">
          <button
            class="ing-tab overview-tab"
            :class="{ active: isOverview }"
            @click="selectOverview"
          >
            全部
          </button>
          <button
            v-for="ing in ingredients"
            :key="ing.ingredient_id"
            class="ing-tab"
            :class="{ active: activeId === ing.ingredient_id }"
            :style="{ '--ing-color': ing.color }"
            @click="selectIngredient(ing.ingredient_id)"
          >
            {{ ing.name }}
          </button>
        </div>

        <template v-if="isOverview">
          <div class="overview-profile">
            <div class="overview-emblem">
              <img
                v-for="ing in shownIngredients.slice(0, 3)"
                :key="ing.ingredient_id"
                :src="ingredientImage(ing)"
                :alt="ing.name"
              />
            </div>
            <div class="ingredient-title">
              <div class="ing-name overview-name">食材传播图谱</div>
              <div class="ing-meta">
                <span>多食材总览</span>
                <span>{{ overviewStats.uniqueNodes }} 个首传节点</span>
              </div>
            </div>
          </div>

        </template>

        <template v-else-if="activeData">
          <div class="ingredient-profile">
            <div class="ingredient-image" :style="{ '--ing-color': activeColor }">
              <img v-if="ingredientImageUrl" :src="ingredientImageUrl" :alt="activeData.name" @error="onIngredientImageError" />
              <div v-else class="ingredient-image-fallback">{{ activeData.name?.slice(0, 1) }}</div>
            </div>
            <div class="ingredient-title">
              <div class="ing-name" :style="{ color: activeColor }">{{ activeData.name }}</div>
              <div class="ing-meta">
                <span class="ing-name-en">{{ activeData.name_en }}</span>
                <span class="ing-species">{{ activeData.species }}</span>
              </div>
            </div>
          </div>

          <div class="specimen-record">
            <span>Origin</span>
            <strong>{{ activeData.origin }}</strong>
            <span>Nodes</span>
            <strong>{{ uniqueEvents.length }} / {{ timeline.length }}</strong>
          </div>
          <p class="ing-summary">{{ activeData.summary }}</p>
        </template>
      </div>

      <div class="overview-section" v-if="isOverview">
        <div class="timeline-header">
          <span class="section-label">可视化图层</span>
          <button class="route-fit-btn" @click="focusFullRoute">查看全图</button>
        </div>

        <div class="ingredient-overview-list">
          <button
            v-for="detail in shownIngredients"
            :key="detail.ingredient_id"
            class="overview-card"
            :style="{ '--ing-color': detail.color }"
            @click="selectIngredient(detail.ingredient_id)"
          >
            <span class="overview-card-image">
              <img :src="ingredientImage(detail)" :alt="detail.name" />
            </span>
            <span class="overview-card-body">
              <span class="overview-card-title">{{ detail.name }}</span>
              <span class="overview-card-meta">{{ formatIngredientRange(detail) }} · {{ uniqueEventsFor(detail).length }} 个首传节点</span>
              <span class="overview-card-summary">{{ detail.summary }}</span>
            </span>
          </button>
        </div>
      </div>

      <div class="timeline-section" v-else-if="activeData">
        <div class="timeline-header">
          <span class="section-label">首传节点</span>
          <button class="route-fit-btn" @click="focusFullRoute">查看全路径</button>
        </div>


        <div class="event-list" ref="eventListEl">
          <div
            v-for="(evt, i) in timeline"
            :key="stableEventKey(evt)"
            :ref="el => { if (el) eventCardRefs[i] = el }"
            class="event-card"
            :class="{ active: stableEventKey(evt) === currentEventKey, duplicate: isDuplicateEvent(evt) }"
            @click="focusEvent(evt, i)"
          >
            <div class="event-card-inner">
              <div class="event-left-rail">
                <div class="event-dot" :style="{ '--ing-color': activeColor }">
                  <img v-if="ingredientImageUrl" :src="ingredientImageUrl" :alt="activeData.name" />
                  <span v-else>{{ mapOrderForEvent(evt) || i + 1 }}</span>
                </div>
                <div class="event-line" v-if="i < timeline.length - 1" />
              </div>
              <div class="event-content">
                <div class="event-top-row">
                  <span class="event-year" :style="{ color: activeColor }">{{ formatYear(evt.year) }}</span>
                  <span class="event-dynasty">{{ evt.dynasty }}</span>
                </div>
                <div class="event-location">{{ evt.location }}</div>
                <div class="event-type-badge" :style="{ borderColor: activeColor + '66', color: activeColor }">
                  {{ evt.event_type }}
                </div>
                <div class="event-map-note" v-if="isDuplicateEvent(evt)">
                  同一地区后续记录，地图中并入首次传入节点
                </div>
                <div class="event-names" v-if="evt.historical_name?.length">
                  {{ evt.historical_name.join(' · ') }}
                </div>
                <div class="event-route" v-if="evt.route" :style="{ color: activeColor }">
                  <span class="route-arrow">→</span>
                  {{ evt.route }}
                </div>
                <p class="event-notes">{{ evt.notes }}</p>
                <div class="event-source" v-if="evt.source_literature">—— {{ evt.source_literature }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const mapContainer = ref(null)
const eventListEl = ref(null)
const eventCardRefs = ref({})

const OVERVIEW_ID = 'all'
const FALLBACK_ICON_ID = 'ingredient-icon-fallback'

const ingredients = ref([])
const ingredientDetails = ref({})
const activeId = ref(OVERVIEW_ID)
const currentEventKey = ref('')
const imageLoadFailed = ref(false)
const sidebarCollapsed = ref(true)

let map = null
let flowFrame = 0
let routePopup = null
let spreadMarkers = []
let markerSyncFrame = 0
let clusterRouteSyncFrame = 0
let clusterRouteUpdateVersion = 0
let normalizingMinZoomCamera = false
let spreadPointFeatureCache = null
let clusterRouteFeatureCache = null
const loadedImageIds = new Set()

const DEFAULT_MAP_CENTER = [104, 32]
const DEFAULT_MAP_ZOOM = 3.05
const DEFAULT_MAP_PITCH = 24
const DEFAULT_MAP_BEARING = 0
const WORLD_TILE_SIZE = 512
const MIN_MAP_ZOOM_FALLBACK = 0.65
const MAX_RESPONSIVE_MIN_ZOOM = 1.45
const MIN_ZOOM_CENTER_LAT = 0
const MIN_ZOOM_SNAP_MARGIN = 0.08
const MIN_ZOOM_CAMERA_DURATION = 220
const SPREAD_CLUSTER_MAX_ZOOM = 10
const SAME_INGREDIENT_CLUSTER_RADIUS = 55
const MIXED_INGREDIENT_CLUSTER_RADIUS = 18
const FOCUSED_CLUSTER_MAX_ZOOM = 5.4
const FOCUSED_CLUSTER_RADIUS = 22
const TEMPORAL_CLUSTER_WEIGHT = 0.6
const SPATIAL_CLUSTER_WEIGHT = 0.4
const OVERVIEW_CLUSTER_TIME_WINDOW_YEARS = 600
const FOCUSED_CLUSTER_TIME_WINDOW_YEARS = 90
const RASTER_MAX_ZOOM = 8

const EMPTY_GEOJSON = { type: 'FeatureCollection', features: [] }
const SPREAD_SOURCES = {
  routes: 'spread-routes',
  points: 'spread-points',
  particles: 'spread-particles',
  clusterRoutes: 'spread-cluster-routes',
}

const MAP_STYLE = {
  version: 8,
  projection: { type: 'mercator' },
  sources: {
    'hyp-tiles': {
      type: 'raster',
      tiles: ['/tiles/raster/{z}/{x}/{y}.png'],
      tileSize: 256,
      minzoom: 0,
      maxzoom: RASTER_MAX_ZOOM,
      attribution: 'Natural Earth',
    },
  },
  layers: [
    { id: 'bg', type: 'background', paint: { 'background-color': '#C8DDE8' } },
    {
      id: 'hyp',
      type: 'raster',
      source: 'hyp-tiles',
      paint: {
        'raster-saturation': -0.08,
        'raster-contrast': 0.22,
        'raster-brightness-min': 0.02,
        'raster-brightness-max': 1,
        'raster-opacity': 1,
      },
    },
  ],
}

const isOverview = computed(() => activeId.value === OVERVIEW_ID)
const activeData = computed(() => isOverview.value ? null : ingredientDetails.value[activeId.value])
const activeColor = computed(() => activeData.value?.color || '#A96B2D')
const hasAnyData = computed(() => shownIngredients.value.length > 0)
const shownIngredients = computed(() => {
  const details = ingredients.value
    .map(item => ingredientDetails.value[item.ingredient_id] || item)
    .filter(Boolean)
  return isOverview.value ? details : (activeData.value ? [activeData.value] : [])
})
const timeline = computed(() => activeData.value ? sortedTimeline(activeData.value.timeline) : [])
const uniqueEvents = computed(() => dedupeFirstArrival(timeline.value))
const duplicateCount = computed(() => Math.max(0, timeline.value.length - uniqueEvents.value.length))
const currentEvent = computed(() => timeline.value.find(event => stableEventKey(event) === currentEventKey.value))
const activeEventIndex = computed(() => timeline.value.findIndex(event => stableEventKey(event) === currentEventKey.value))
const selectedRegionKey = computed(() => currentEvent.value ? normalizeRegionKey(currentEvent.value) : '')
const firstArrivalKeySet = computed(() => new Set(uniqueEvents.value.map(event => stableEventKey(event))))
const ingredientImageUrl = computed(() => {
  if (imageLoadFailed.value || !activeData.value) return ''
  return ingredientImage(activeData.value)
})
const overviewStats = computed(() => {
  const uniqueNodes = shownIngredients.value.reduce((sum, item) => sum + uniqueEventsFor(item).length, 0)
  const historyRecords = shownIngredients.value.reduce((sum, item) => sum + sortedTimeline(item.timeline).length, 0)
  return { uniqueNodes, historyRecords }
})
const displayedYearRange = computed(() => formatRangeForIngredients(shownIngredients.value))
const overlayTitle = computed(() => {
  if (isOverview.value) return `${shownIngredients.value.length} 种食材 · ${overviewStats.value.uniqueNodes} 个首传节点`
  return `${activeData.value?.name || ''} · ${uniqueEvents.value.length} 个首传节点`
})
const captionTitle = computed(() => {
  if (!activeData.value) return ''
  if (currentEvent.value) return `${formatYear(currentEvent.value.year)} · ${currentEvent.value.location}`
  const last = uniqueEvents.value.at(-1)?.location || activeData.value.origin
  return `${activeData.value.origin} → ${last}`
})
const captionRoute = computed(() => {
  return currentEvent.value?.route || '同一地区重复出现时，仅保留最早传入记录作为地图节点。'
})

function sortedTimeline(events = []) {
  return [...events].filter(event => event?.coordinates).sort((a, b) => a.year - b.year)
}

function onIngredientImageError() {
  imageLoadFailed.value = true
}

function ingredientImage(ingredient) {
  return ingredient?.image_url || ingredient?.image || (ingredient?.ingredient_id ? `/ingredients/${ingredient.ingredient_id}.svg` : '')
}

function iconIdForIngredient(ingredient) {
  return `ingredient-icon-${ingredient?.ingredient_id || 'unknown'}`
}

function eventKey(event, index) {
  return event.event_id || `${event.year}-${event.location}-${index}`
}

function stableEventKey(event) {
  return String(event?.event_id || `${event?.year ?? ''}-${normalizeRegionKey(event)}-${event?.location || ''}-${event?.route || ''}`)
}

function normalizeRegionKey(event) {
  return String(event?.region_key || event?.region || event?.province || event?.location || '')
    .trim()
    .replace(/\s+/g, '')
}

function dedupeFirstArrival(events) {
  const seen = new Set()
  return sortedTimeline(events)
    .filter(event => {
      const key = normalizeRegionKey(event)
      if (!key) return true
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
}

function uniqueEventsFor(ingredient) {
  return dedupeFirstArrival(ingredient?.timeline || [])
}

function isDuplicateEvent(event) {
  if (!event?.coordinates) return false
  return !firstArrivalKeySet.value.has(stableEventKey(event))
}

function mapOrderForEvent(event) {
  const regionKey = normalizeRegionKey(event)
  const index = uniqueEvents.value.findIndex(item => normalizeRegionKey(item) === regionKey)
  return index >= 0 ? index + 1 : null
}

function formatYear(year) {
  if (year === null || year === undefined || Number.isNaN(Number(year))) return '未知年代'
  const numeric = Number(year)
  if (numeric < 0) return `公元前${Math.abs(numeric)}`
  return `${numeric}`
}

function formatRange(minYear, maxYear) {
  if (minYear === null || minYear === undefined || maxYear === null || maxYear === undefined) return '未载入'
  return minYear === maxYear ? formatYear(minYear) : `${formatYear(minYear)}—${formatYear(maxYear)}`
}

function formatRangeForIngredients(list) {
  const years = list.flatMap(item => sortedTimeline(item.timeline).map(event => event.year))
  if (!years.length) return '未载入'
  return formatRange(Math.min(...years), Math.max(...years))
}

function formatIngredientRange(ingredient) {
  const events = sortedTimeline(ingredient?.timeline)
  if (!events.length) return '未载入'
  return formatRange(events[0].year, events.at(-1).year)
}

function hexToRgb(hex) {
  const normalized = /^#[0-9a-f]{6}$/i.test(hex || '') ? hex : '#E5394E'
  return [
    parseInt(normalized.slice(1, 3), 16),
    parseInt(normalized.slice(3, 5), 16),
    parseInt(normalized.slice(5, 7), 16),
  ]
}

function rgba(color, alpha) {
  const [r, g, b] = hexToRgb(color)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value))
}

function normalizedLngLat(coord) {
  const lngRaw = Array.isArray(coord) ? coord[0] : coord?.lng
  const latRaw = Array.isArray(coord) ? coord[1] : coord?.lat
  const lng = Number(lngRaw)
  const lat = Number(latRaw)
  if (!Number.isFinite(lng) || !Number.isFinite(lat)) return null
  return [lng, lat]
}

function sameLngLat(a, b, epsilon = 0.000001) {
  const first = normalizedLngLat(a)
  const second = normalizedLngLat(b)
  if (!first || !second) return false
  return Math.abs(first[0] - second[0]) <= epsilon && Math.abs(first[1] - second[1]) <= epsilon
}

function haversineKm(from, to) {
  const R = 6371
  const [lng1, lat1] = from.map(v => v * Math.PI / 180)
  const [lng2, lat2] = to.map(v => v * Math.PI / 180)
  const dLat = lat2 - lat1
  const dLng = lng2 - lng1
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2
  return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function buildGreatCircleArc(from, to, segments = 72) {
  const [lng1, lat1] = from
  const [lng2, lat2] = to
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const lat1R = lat1 * Math.PI / 180
  const lat2R = lat2 * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1R) * Math.cos(lat2R) * Math.sin(dLng / 2) ** 2
  const dist = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  if (!Number.isFinite(dist) || dist < 0.00001) return [from, to]

  const points = []
  for (let i = 0; i <= segments; i += 1) {
    const f = i / segments
    const A = Math.sin((1 - f) * dist) / Math.sin(dist)
    const B = Math.sin(f * dist) / Math.sin(dist)
    const x = A * Math.cos(lat1R) * Math.cos(lng1 * Math.PI / 180) + B * Math.cos(lat2R) * Math.cos(lng2 * Math.PI / 180)
    const y = A * Math.cos(lat1R) * Math.sin(lng1 * Math.PI / 180) + B * Math.cos(lat2R) * Math.sin(lng2 * Math.PI / 180)
    const z = A * Math.sin(lat1R) + B * Math.sin(lat2R)
    points.push([
      Math.atan2(y, x) * 180 / Math.PI,
      Math.atan2(z, Math.sqrt(x * x + y * y)) * 180 / Math.PI,
    ])
  }
  return points
}

function getSegmentMode(event) {
  const text = `${event?.route || ''} ${event?.event_type || ''} ${event?.location || ''}`
  if (/海|港|船|跨洋|荷兰|西班牙|日本|朝鲜|泉州|广州|香料/.test(text)) return 'sea'
  if (/江|河|运河|漕运|水运|长江|珠江|黄河|岷江/.test(text)) return 'river'
  return 'land'
}

function buildStylizedPath(from, to, segmentIndex, ingredientIndex, mode) {
  const distance = haversineKm(from, to)
  const base = buildGreatCircleArc(from, to, mode === 'sea' || distance > 2800 ? 96 : 58)
  if (base.length < 3) return base

  const dx = to[0] - from[0]
  const dy = to[1] - from[1]
  const length = Math.sqrt(dx * dx + dy * dy) || 1
  const normal = [-dy / length, dx / length]
  const sign = ((segmentIndex + ingredientIndex) % 2 === 0 ? 1 : -1)
  const modeFactor = mode === 'river' ? 0.55 : mode === 'sea' ? 1.18 : 0.92
  const spreadFactor = isOverview.value ? 1.16 : 0.82
  const ingredientLift = isOverview.value ? (ingredientIndex - (shownIngredients.value.length - 1) / 2) * 0.18 : 0
  const offset = sign * clamp(distance / 900, 0.18, 1.65) * modeFactor * spreadFactor + ingredientLift

  return base.map((point, pointIndex) => {
    const t = pointIndex / (base.length - 1)
    const lift = Math.sin(t * Math.PI) * offset
    return [point[0] + normal[0] * lift, point[1] + normal[1] * lift]
  })
}

function getRoutePointsForIngredient(ingredient, ingredientIndex = 0) {
  if (!ingredient) return []
  const color = ingredient.color || '#E5394E'
  const icon = iconIdForIngredient(ingredient)
  const points = []

  const originPosition = normalizedLngLat(ingredient.origin_coordinates)
  if (originPosition) {
    points.push({
      id: `${ingredient.ingredient_id}-origin`,
      ingredient,
      ingredientIndex,
      position: originPosition,
      label: ingredient.origin,
      order: 0,
      eventKey: `${ingredient.ingredient_id}-origin`,
      color,
      icon,
      isOrigin: true,
      isSelected: false,
    })
  }

  uniqueEventsFor(ingredient).forEach((event, index) => {
    const eventPosition = normalizedLngLat(event.coordinates)
    if (!eventPosition) return
    if (originPosition && sameLngLat(eventPosition, originPosition)) return
    const eventStableKey = stableEventKey(event)
    points.push({
      id: `${ingredient.ingredient_id}-${eventKey(event, index)}`,
      ingredient,
      ingredientIndex,
      position: eventPosition,
      label: event.location,
      order: index + 1,
      event,
      eventKey: eventStableKey,
      color,
      icon,
      isOrigin: false,
      isSelected: ingredient.ingredient_id === activeData.value?.ingredient_id && eventStableKey === currentEventKey.value,
    })
  })

  return points
}

function getDisplayedRoutePoints() {
  return shownIngredients.value.flatMap((ingredient, index) => getRoutePointsForIngredient(ingredient, index))
}

function buildSpreadGeometry() {
  const allPoints = []
  const segments = []

  shownIngredients.value.forEach((ingredient, ingredientIndex) => {
    const points = getRoutePointsForIngredient(ingredient, ingredientIndex)
    allPoints.push(...points)
    for (let i = 0; i < points.length - 1; i += 1) {
      const source = points[i]
      const target = points[i + 1]
      const mode = getSegmentMode(target.event)
      const path = buildStylizedPath(source.position, target.position, i, ingredientIndex, mode)
      segments.push({
        id: `${source.id}->${target.id}`,
        ingredient,
        ingredientIndex,
        index: i,
        mode,
        source: source.position,
        target: target.position,
        sourceLabel: source.label,
        targetLabel: target.label,
        event: target.event,
        path,
      })
    }
  })

  return { points: allPoints, segments }
}

function lineFeature(segment) {
  const color = segment.ingredient?.color || '#E5394E'
  return {
    type: 'Feature',
    properties: {
      id: segment.id,
      ingredient_id: segment.ingredient?.ingredient_id || '',
      ingredient_name: segment.ingredient?.name || '',
      mode: segment.mode,
      order: segment.index + 1,
      from: segment.sourceLabel,
      to: segment.targetLabel,
      year: segment.event?.year || '',
      route: segment.event?.route || '',
      color,
      color_soft: rgba(color, 0.34),
      overview: isOverview.value,
    },
    geometry: {
      type: 'LineString',
      coordinates: segment.path,
    },
  }
}

function pointFeature(point) {
  const event = point.event || {}
  const state = point.isOrigin ? 'origin' : (point.isSelected ? 'selected' : 'arrival')
  return {
    type: 'Feature',
    properties: {
      id: point.id,
      ingredient_id: point.ingredient?.ingredient_id || '',
      ingredient_name: point.ingredient?.name || '',
      order: point.order,
      event_key: point.eventKey,
      state,
      label: point.label,
      year: event.year ?? '',
      year_label: event.year === undefined ? '' : formatYear(event.year),
      dynasty: event.dynasty || '',
      event_type: event.event_type || (point.isOrigin ? '原产地' : ''),
      route: event.route || '',
      notes: event.notes || '',
      source_literature: event.source_literature || '',
      historical_name: Array.isArray(event.historical_name) ? event.historical_name.join(' · ') : '',
      color: point.color,
      icon: point.icon,
      overview: isOverview.value,
      sort_key: point.isSelected ? 0 : point.isOrigin ? 2 + point.ingredientIndex : 10 + point.ingredientIndex * 100 + point.order,
    },
    geometry: {
      type: 'Point',
      coordinates: point.position,
    },
  }
}

function pointIngredientId(point) {
  return point.ingredient?.ingredient_id || point.ingredient_id || ''
}

function pointYearValue(point) {
  const year = Number(point.event?.year)
  return Number.isFinite(year) ? year : null
}

function averageProjectedCenter(items) {
  if (!map || !items.length) return null
  let x = 0
  let y = 0
  items.forEach(item => {
    x += item.screen.x
    y += item.screen.y
  })
  const center = map.unproject([x / items.length, y / items.length])
  return normalizedLngLat(center)
}

function makePointClusterFeature(items, clusterIndex) {
  const coordinates = averageProjectedCenter(items)
  if (!coordinates) return null
  const leafIds = items.flatMap(item => item.leafIds || [item.point.id])
  const ingredientIds = [...new Set(items.flatMap(item => item.ingredientIds || [pointIngredientId(item.point)]).filter(Boolean))]
  const colors = [...new Set(items.map(item => item.point?.color).filter(Boolean))]
  const primary = items[0]?.point || {}
  return {
    type: 'Feature',
    properties: {
      cluster_id: `custom-cluster-${clusterIndex}`,
      point_count: leafIds.length,
      point_count_abbreviated: leafIds.length > 99 ? '99+' : String(leafIds.length),
      leaf_ids: leafIds,
      ingredient_ids: ingredientIds,
      mixed: ingredientIds.length > 1,
      color: ingredientIds.length === 1 ? (primary.color || colors[0] || '#A96B2D') : '#A96B2D',
    },
    geometry: {
      type: 'Point',
      coordinates,
    },
  }
}

function averageItemYear(items) {
  const years = items
    .map(item => item.year)
    .filter(year => Number.isFinite(year))
  if (!years.length) return null
  return years.reduce((sum, year) => sum + year, 0) / years.length
}

function weightedClusterDistance(candidate, center, radius, timeWindow) {
  const dx = candidate.screen.x - center.x
  const dy = candidate.screen.y - center.y
  const spatialDistance = Math.sqrt(dx * dx + dy * dy)
  const spatialScore = spatialDistance / Math.max(radius, 1)
  const temporalScore = Number.isFinite(candidate.year) && Number.isFinite(center.year)
    ? Math.abs(candidate.year - center.year) / Math.max(timeWindow, 1)
    : 1
  return TEMPORAL_CLUSTER_WEIGHT * temporalScore + SPATIAL_CLUSTER_WEIGHT * spatialScore
}

function clusterProjectedItems(items, radius, timeWindow) {
  const clusters = []
  const used = new Set()
  items.forEach((item, index) => {
    if (used.has(index)) return
    const group = [item]
    used.add(index)
    let center = { x: item.screen.x, y: item.screen.y, year: item.year }

    let expanded = true
    while (expanded) {
      expanded = false
      items.forEach((candidate, candidateIndex) => {
        if (used.has(candidateIndex)) return
        if (weightedClusterDistance(candidate, center, radius, timeWindow) > 1) return
        group.push(candidate)
        used.add(candidateIndex)
        center = {
          x: group.reduce((sum, value) => sum + value.screen.x, 0) / group.length,
          y: group.reduce((sum, value) => sum + value.screen.y, 0) / group.length,
          year: averageItemYear(group),
        }
        expanded = true
      })
    }

    clusters.push(group)
  })
  return clusters
}

function shouldClusterSpreadPoints() {
  if (!map) return false
  const zoom = map.getZoom()
  if (isOverview.value) return zoom <= SPREAD_CLUSTER_MAX_ZOOM
  return shownIngredients.value.length === 1 && zoom <= FOCUSED_CLUSTER_MAX_ZOOM
}

function hasVisiblePointClusters() {
  return Boolean(spreadPointFeatureCache?.features?.some(feature => feature.properties?.point_count))
}

function buildCustomClusteredPointGeoJson(points) {
  if (!map || !shouldClusterSpreadPoints()) {
    return { type: 'FeatureCollection', features: points.map(pointFeature) }
  }
  const sameRadius = isOverview.value ? SAME_INGREDIENT_CLUSTER_RADIUS : FOCUSED_CLUSTER_RADIUS
  const mixedRadius = isOverview.value ? MIXED_INGREDIENT_CLUSTER_RADIUS : 0
  const timeWindow = isOverview.value ? OVERVIEW_CLUSTER_TIME_WINDOW_YEARS : FOCUSED_CLUSTER_TIME_WINDOW_YEARS

  const projected = points.map(point => {
    const screen = map.project(point.position)
    return {
      point,
      screen,
      leafIds: [point.id],
      ingredientIds: [pointIngredientId(point)],
      year: pointYearValue(point),
    }
  })

  const byIngredient = new Map()
  projected.forEach(item => {
    const id = pointIngredientId(item.point)
    if (!byIngredient.has(id)) byIngredient.set(id, [])
    byIngredient.get(id).push(item)
  })

  const sameIngredientGroups = []
  byIngredient.forEach(items => {
    sameIngredientGroups.push(...clusterProjectedItems(items, sameRadius, timeWindow))
  })

  const representatives = sameIngredientGroups.map((group, index) => {
    const point = group[0].point
    const screen = group.reduce((acc, item) => ({ x: acc.x + item.screen.x, y: acc.y + item.screen.y }), { x: 0, y: 0 })
    return {
      point,
      screen: { x: screen.x / group.length, y: screen.y / group.length },
      leafIds: group.map(item => item.point.id),
      ingredientIds: [...new Set(group.map(item => pointIngredientId(item.point)).filter(Boolean))],
      year: averageItemYear(group),
      groupIndex: index,
    }
  })

  const mixedGroups = mixedRadius > 0 ? clusterProjectedItems(representatives, mixedRadius, timeWindow) : representatives.map(item => [item])
  let clusterIndex = 0
  const features = []
  mixedGroups.forEach(group => {
    const leafIds = group.flatMap(item => item.leafIds)
    if (leafIds.length <= 1) {
      const sourceItem = projected.find(item => item.point.id === leafIds[0])
      if (sourceItem) features.push(pointFeature(sourceItem.point))
      return
    }
    const feature = makePointClusterFeature(group, clusterIndex)
    clusterIndex += 1
    if (feature) features.push(feature)
  })

  return { type: 'FeatureCollection', features }
}

function buildNativeSpreadGeoJson() {
  const { points, segments } = buildSpreadGeometry()
  return {
    routes: { type: 'FeatureCollection', features: segments.map(lineFeature) },
    points: buildCustomClusteredPointGeoJson(points),
    rawPoints: points,
  }
}

function updateSpreadPointSourceData(points = null) {
  if (!map || !map.getSource(SPREAD_SOURCES.points)) return EMPTY_GEOJSON
  const sourcePoints = points || buildSpreadGeometry().points
  const data = buildCustomClusteredPointGeoJson(sourcePoints)
  spreadPointFeatureCache = data
  setSourceData(SPREAD_SOURCES.points, data)
  return data
}

function buildClusterRoutes() {
  if (!map) return EMPTY_GEOJSON

  const sourceFeatures = spreadPointFeatureCache?.features || []
  const idToCoord = new Map()

  // Process custom cluster features: map each leaf point to its visible cluster center.
  const clusterFeatures = sourceFeatures.filter(f => f.properties.point_count)
  for (const cluster of clusterFeatures) {
    const leafIds = Array.isArray(cluster.properties.leaf_ids) ? cluster.properties.leaf_ids : []
    for (const leafId of leafIds) {
      if (leafId) {
        idToCoord.set(leafId, cluster.geometry.coordinates)
      }
    }
  }

  // Process unclustered points: map point id to its own coordinates
  const pointFeatures = sourceFeatures.filter(f => !f.properties.point_count)
  for (const point of pointFeatures) {
    if (point.properties.id) {
      idToCoord.set(point.properties.id, point.geometry.coordinates)
    }
  }

  if (!idToCoord.size) return EMPTY_GEOJSON

  const { segments } = buildSpreadGeometry()
  const dedupeKey = new Set()
  const features = []

  for (const segment of segments) {
    const parts = segment.id.split('->')
    if (parts.length < 2) continue
    const sourceId = parts[0]
    const targetId = parts.slice(1).join('->') // handle if id contains '->'
    const sourceCoord = idToCoord.get(sourceId)
    const targetCoord = idToCoord.get(targetId)
    if (!sourceCoord || !targetCoord) continue

    // Skip self-loops (same cluster)
    if (sourceCoord[0] === targetCoord[0] && sourceCoord[1] === targetCoord[1]) continue

    const key = `${sourceCoord[0].toFixed(4)},${sourceCoord[1].toFixed(4)}->${targetCoord[0].toFixed(4)},${targetCoord[1].toFixed(4)}`
    if (dedupeKey.has(key)) continue
    dedupeKey.add(key)

    const color = segment.ingredient?.color || '#A96B2D'
    const path = buildStylizedPath(sourceCoord, targetCoord, segment.index, segment.ingredientIndex, segment.mode)
    features.push({
      type: 'Feature',
      properties: {
        color,
        color_soft: rgba(color, 0.28),
        mode: segment.mode,
      },
      geometry: {
        type: 'LineString',
        coordinates: path,
      },
    })
  }

  return { type: 'FeatureCollection', features }
}

async function updateClusterRoutes() {
  if (!map || !map.getSource(SPREAD_SOURCES.clusterRoutes)) return

  const shouldCluster = hasVisiblePointClusters()
  const updateVersion = ++clusterRouteUpdateVersion

  if (shouldCluster) {
    const data = buildClusterRoutes()
    if (updateVersion !== clusterRouteUpdateVersion) return
    clusterRouteFeatureCache = data
    setSourceData(SPREAD_SOURCES.clusterRoutes, data)
    try { map.setLayoutProperty('spread-cluster-route-shadow', 'visibility', 'visible') } catch (_) {}
    try { map.setLayoutProperty('spread-cluster-route-main', 'visibility', 'visible') } catch (_) {}
    try { map.setLayoutProperty('spread-route-shadow', 'visibility', 'none') } catch (_) {}
    try { map.setLayoutProperty('spread-route-corridor', 'visibility', 'none') } catch (_) {}
    try { map.setLayoutProperty('spread-route-main', 'visibility', 'none') } catch (_) {}
    try { map.setLayoutProperty('spread-route-texture', 'visibility', 'none') } catch (_) {}
  } else {
    clusterRouteFeatureCache = EMPTY_GEOJSON
    setSourceData(SPREAD_SOURCES.clusterRoutes, EMPTY_GEOJSON)
    try { map.setLayoutProperty('spread-cluster-route-shadow', 'visibility', 'none') } catch (_) {}
    try { map.setLayoutProperty('spread-cluster-route-main', 'visibility', 'none') } catch (_) {}
    try { map.setLayoutProperty('spread-route-shadow', 'visibility', 'visible') } catch (_) {}
    try { map.setLayoutProperty('spread-route-corridor', 'visibility', 'visible') } catch (_) {}
    try { map.setLayoutProperty('spread-route-main', 'visibility', 'visible') } catch (_) {}
    try { map.setLayoutProperty('spread-route-texture', 'visibility', 'visible') } catch (_) {}
  }
}

function scheduleClusterRouteUpdate() {
  if (clusterRouteSyncFrame) return
  clusterRouteSyncFrame = requestAnimationFrame(() => {
    clusterRouteSyncFrame = 0
    updateSpreadPointSourceData()
    updateClusterRoutes()
  })
}

function pointAlongPath(path, t) {
  if (!path.length) return null
  if (path.length === 1) return path[0]
  const scaled = clamp(t, 0, 0.9999) * (path.length - 1)
  const idx = Math.floor(scaled)
  const local = scaled - idx
  const a = path[idx]
  const b = path[idx + 1] || a
  return [
    a[0] + (b[0] - a[0]) * local,
    a[1] + (b[1] - a[1]) * local,
  ]
}

function buildParticles(phase) {
  const useClusterRoutes = hasVisiblePointClusters() && clusterRouteFeatureCache?.features?.length
  if (useClusterRoutes) {
    const features = []
    clusterRouteFeatureCache.features.forEach((route, segmentIndex) => {
      const path = route.geometry?.coordinates || []
      const point = pointAlongPath(path, (phase + segmentIndex * 0.19) % 1)
      if (!point) return
      features.push({
        type: 'Feature',
        properties: {
          mode: route.properties?.mode || 'land',
          color: route.properties?.color || '#E5394E',
          size: route.properties?.mode === 'sea' ? 5.3 : 4.3,
          overview: true,
        },
        geometry: { type: 'Point', coordinates: point },
      })
    })
    return { type: 'FeatureCollection', features }
  }

  const { segments } = buildSpreadGeometry()
  const features = []
  segments.forEach((segment, segmentIndex) => {
    const pulses = isOverview.value ? 1 : (segment.mode === 'sea' ? 3 : 2)
    for (let i = 0; i < pulses; i += 1) {
      const t = (phase + segmentIndex * 0.19 + i / pulses) % 1
      const point = pointAlongPath(segment.path, t)
      if (!point) continue
      features.push({
        type: 'Feature',
        properties: {
          mode: segment.mode,
          color: segment.ingredient?.color || '#E5394E',
          size: segment.mode === 'sea' ? 5.3 : 4.3,
          overview: isOverview.value,
        },
        geometry: { type: 'Point', coordinates: point },
      })
    }
  })
  return { type: 'FeatureCollection', features }
}

function setSourceData(sourceId, data) {
  const source = map?.getSource(sourceId)
  if (source?.setData) source.setData(data)
}

async function updateNativeSpreadLayers() {
  if (!map || !map.getSource(SPREAD_SOURCES.routes)) return

  const data = buildNativeSpreadGeoJson()
  setSourceData(SPREAD_SOURCES.routes, data.routes)
  spreadPointFeatureCache = data.points
  setSourceData(SPREAD_SOURCES.points, data.points)
  syncPointMarkers()
  await ensureIngredientImages()
  updateSpreadPointSourceData(data.rawPoints)
  map.triggerRepaint?.()
  updateClusterRoutes()

  try {
    map.setPaintProperty('spread-route-particles', 'circle-opacity', isOverview.value ? 0.68 : 0.9)
  } catch (_) {}
}

function animateFlow(timestamp = 0) {
  if (!map) return
  const phase = (timestamp % 4600) / 4600
  try {
    if (map.getSource(SPREAD_SOURCES.particles)) {
      setSourceData(SPREAD_SOURCES.particles, buildParticles(phase))
    }
  } catch (_) {}
  flowFrame = requestAnimationFrame(animateFlow)
}

function stopFlowAnimation() {
  if (flowFrame) {
    cancelAnimationFrame(flowFrame)
    flowFrame = 0
  }
}

function addFallbackIcon() {
  if (!map || map.hasImage(FALLBACK_ICON_ID)) return
  const canvas = document.createElement('canvas')
  canvas.width = 96
  canvas.height = 96
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, 96, 96)
  ctx.fillStyle = 'rgba(255,248,232,0.96)'
  ctx.beginPath()
  ctx.arc(48, 48, 34, 0, Math.PI * 2)
  ctx.fill()
  ctx.strokeStyle = 'rgba(120,84,45,0.42)'
  ctx.lineWidth = 5
  ctx.stroke()
  ctx.fillStyle = 'rgba(130,82,34,0.86)'
  ctx.font = '600 38px sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('食', 48, 50)
  map.addImage(FALLBACK_ICON_ID, canvasToImageData(canvas), { pixelRatio: 2 })
  loadedImageIds.add(FALLBACK_ICON_ID)
}

function createTextIcon(text, color = '#9B6A2F') {
  const canvas = document.createElement('canvas')
  canvas.width = 128
  canvas.height = 128
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, 128, 128)
  ctx.fillStyle = 'rgba(255,248,232,0.96)'
  ctx.beginPath()
  ctx.arc(64, 64, 42, 0, Math.PI * 2)
  ctx.fill()
  ctx.strokeStyle = color
  ctx.globalAlpha = 0.66
  ctx.lineWidth = 5
  ctx.stroke()
  ctx.globalAlpha = 1
  ctx.fillStyle = color
  ctx.font = '700 42px sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(String(text || '食').slice(0, 1), 64, 66)
  return canvas
}

function canvasToImageData(canvas) {
  const ctx = canvas.getContext('2d')
  return ctx.getImageData(0, 0, canvas.width, canvas.height)
}

function safeAddGeneratedIcon(iconId, text, color) {
  if (!map || map.hasImage(iconId)) return
  map.addImage(iconId, canvasToImageData(createTextIcon(text, color)), { pixelRatio: 2 })
  loadedImageIds.add(iconId)
}

function loadMapImage(iconId, url, ingredient) {
  if (!map || map.hasImage(iconId) || loadedImageIds.has(iconId)) return Promise.resolve()
  return new Promise(resolve => {
    if (!url) {
      safeAddGeneratedIcon(iconId, ingredient?.name, ingredient?.color)
      resolve()
      return
    }
    const image = new Image()
    image.crossOrigin = 'anonymous'
    const fallback = () => {
      try {
        safeAddGeneratedIcon(iconId, ingredient?.name, ingredient?.color)
      } catch (_) {}
      resolve()
    }
    const timer = window.setTimeout(fallback, 3000)
    image.onload = () => {
      window.clearTimeout(timer)
      try {
        if (!map.hasImage(iconId)) {
          map.addImage(iconId, image, { pixelRatio: 2 })
          loadedImageIds.add(iconId)
        }
      } catch (_) {
        try {
          safeAddGeneratedIcon(iconId, ingredient?.name, ingredient?.color)
        } catch (_) {}
      }
      resolve()
    }
    image.onerror = () => {
      window.clearTimeout(timer)
      fallback()
    }
    image.src = url
  })
}

async function ensureIngredientImages() {
  if (!map) return
  addFallbackIcon()
  const tasks = shownIngredients.value.map(ingredient => loadMapImage(iconIdForIngredient(ingredient), ingredientImage(ingredient), ingredient))
  await Promise.all(tasks)
}

function addNativeSpreadLayers() {
  if (!map || map.getSource(SPREAD_SOURCES.routes)) return

  map.addSource(SPREAD_SOURCES.routes, { type: 'geojson', data: EMPTY_GEOJSON, lineMetrics: true })
  map.addSource(SPREAD_SOURCES.points, { type: 'geojson', data: EMPTY_GEOJSON })
  map.addSource(SPREAD_SOURCES.particles, { type: 'geojson', data: EMPTY_GEOJSON })
  map.addSource(SPREAD_SOURCES.clusterRoutes, { type: 'geojson', data: EMPTY_GEOJSON, lineMetrics: true })

  map.addLayer({
    id: 'spread-route-shadow',
    type: 'line',
    source: SPREAD_SOURCES.routes,
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': '#23170E',
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 5.8, 5, 12.5],
      'line-opacity': ['case', ['boolean', ['get', 'overview'], false], 0.12, 0.20],
      'line-blur': 5.2,
    },
  })

  map.addLayer({
    id: 'spread-route-corridor',
    type: 'line',
    source: SPREAD_SOURCES.routes,
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': ['get', 'color'],
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 4.4, 5, 9.2, 7, 13.5],
      'line-opacity': ['case', ['boolean', ['get', 'overview'], false], 0.16, 0.24],
      'line-blur': 2.6,
    },
  })

  map.addLayer({
    id: 'spread-route-main',
    type: 'line',
    source: SPREAD_SOURCES.routes,
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': ['get', 'color'],
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 1.45, 5, 3.6, 7, 5.8],
      'line-opacity': ['case', ['boolean', ['get', 'overview'], false], 0.62, 0.92],
    },
  })

  map.addLayer({
    id: 'spread-route-texture',
    type: 'line',
    source: SPREAD_SOURCES.routes,
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': '#FFF7DF',
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 0.8, 5, 1.6],
      'line-opacity': ['case', ['boolean', ['get', 'overview'], false], 0.30, 0.42],
      'line-dasharray': [0.15, 2.4],
    },
  })

  map.addLayer({
    id: 'spread-cluster-route-shadow',
    type: 'line',
    source: SPREAD_SOURCES.clusterRoutes,
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': ['get', 'color_soft'],
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 6.2, 5, 13.5, 7, 17],
      'line-opacity': 0.16,
      'line-blur': 3.8,
    },
  })

  map.addLayer({
    id: 'spread-cluster-route-main',
    type: 'line',
    source: SPREAD_SOURCES.clusterRoutes,
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': ['get', 'color'],
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 2.2, 5, 5, 7, 7.5],
      'line-opacity': 0.72,
      'line-dasharray': [2, 1.5],
    },
  })

  map.addLayer({
    id: 'spread-cluster-area',
    type: 'circle',
    source: SPREAD_SOURCES.points,
    filter: ['has', 'point_count'],
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 25, 5, 35, 8, 45],
      'circle-color': '#A96B2D',
      'circle-opacity': 0.16,
      'circle-stroke-color': '#A96B2D',
      'circle-stroke-opacity': 0.3,
      'circle-stroke-width': 1,
    },
  })

  map.addLayer({
    id: 'spread-cluster-core',
    type: 'circle',
    source: SPREAD_SOURCES.points,
    filter: ['has', 'point_count'],
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 14, 5, 18, 8, 24],
      'circle-color': '#FFF8EA',
      'circle-opacity': 0.96,
      'circle-stroke-color': '#A96B2D',
      'circle-stroke-width': 2,
    },
  })

  map.addLayer({
    id: 'spread-cluster-count',
    type: 'symbol',
    source: SPREAD_SOURCES.points,
    filter: ['has', 'point_count'],
    layout: {
      'text-field': ['get', 'point_count_abbreviated'],
      'text-size': ['interpolate', ['linear'], ['zoom'], 2, 11, 6, 14],
      'text-font': ['DIN Pro Medium', 'Arial Unicode MS Bold'],
      'text-allow-overlap': true,
    },
    paint: {
      'text-color': '#A96B2D',
      'text-halo-color': '#FFF8EA',
      'text-halo-width': 0.8,
    },
  })

  map.addLayer({
    id: 'spread-arrival-area',
    type: 'circle',
    source: SPREAD_SOURCES.points,
    filter: ['!', ['has', 'point_count']],
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 8, 5, 26, 7, 50],
      'circle-color': ['get', 'color'],
      'circle-opacity': [
        'match',
        ['get', 'state'],
        'origin', 0.16,
        'selected', 0.30,
        0.18,
      ],
      'circle-stroke-color': ['get', 'color'],
      'circle-stroke-opacity': [
        'match',
        ['get', 'state'],
        'origin', 0.36,
        'selected', 0.64,
        0.38,
      ],
      'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 2, 0.9, 6, 2],
      'circle-blur': 0.25,
    },
  })

  map.addLayer({
    id: 'spread-arrival-core',
    type: 'circle',
    source: SPREAD_SOURCES.points,
    filter: ['!', ['has', 'point_count']],
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 7.4, 5, 11.5, 7, 15],
      'circle-color': '#FFF8EA',
      'circle-opacity': [
        'match',
        ['get', 'state'],
        'selected', 0.98,
        'origin', 0.92,
        0.86,
      ],
      'circle-stroke-color': ['get', 'color'],
      'circle-stroke-opacity': [
        'match',
        ['get', 'state'],
        'selected', 0.86,
        'origin', 0.68,
        0.58,
      ],
      'circle-stroke-width': ['match', ['get', 'state'], 'selected', 3.4, 'origin', 2.4, 1.8],
    },
  })

  map.addLayer({
    id: 'spread-arrival-icons',
    type: 'symbol',
    source: SPREAD_SOURCES.points,
    filter: ['!', ['has', 'point_count']],
    layout: {
      'icon-image': ['get', 'icon'],
      'icon-size': ['interpolate', ['linear'], ['zoom'], 2, 0.20, 4, 0.33, 6, 0.50, 8, 0.66],
      'icon-allow-overlap': true,
      'icon-ignore-placement': true,
      'icon-padding': 2,
      'symbol-sort-key': ['get', 'sort_key'],
    },
  })

  map.addLayer({
    id: 'spread-route-particles',
    type: 'circle',
    source: SPREAD_SOURCES.particles,
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 1.7, 5, 4.7, 7, 6.4],
      'circle-color': ['get', 'color'],
      'circle-opacity': 0.82,
      'circle-blur': 0.08,
      'circle-stroke-color': '#FFF8EA',
      'circle-stroke-width': 0.75,
    },
  })

  bindSpreadInteractions()
  map.on('zoom', updatePointMarkerScale)
  map.on('zoomend', syncPointMarkers)
  map.on('moveend', scheduleMarkerSync)
  map.on('zoom', scheduleClusterRouteUpdate)

  map.on('click', 'spread-cluster-core', async (e) => {
    const feature = e.features?.[0]
    if (!feature) return
    const coordinates = normalizedLngLat(feature.geometry.coordinates)
    if (!coordinates) return
    const targetZoom = isOverview.value
      ? Math.min(SPREAD_CLUSTER_MAX_ZOOM + 1, map.getZoom() + 2.5)
      : Math.min(FOCUSED_CLUSTER_MAX_ZOOM + 1, map.getZoom() + 1.6)
    map.stop()
    map.easeTo({ center: coordinates, zoom: targetZoom, duration: 600 })
  })

  updateNativeSpreadLayers()
  stopFlowAnimation()
  flowFrame = requestAnimationFrame(animateFlow)
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function popupHtml(props) {
  const color = props.color || activeColor.value
  const order = props.state === 'origin' ? '源' : props.order
  const title = props.state === 'origin'
    ? `${props.ingredient_name}原产地 · ${props.label}`
    : `${props.year_label || props.year} · ${props.label}`
  return `
    <div class="spread-popup-card" style="--popup-color: ${escapeHtml(color)}">
      <div class="popup-heading">
        <div class="popup-order">${escapeHtml(order)}</div>
        <div>
          <div class="popup-title">${escapeHtml(title)}</div>
          <div class="popup-type">${escapeHtml(props.ingredient_name || '')} · ${escapeHtml(props.event_type || '')}</div>
        </div>
      </div>
      ${props.historical_name ? `<div class="popup-alias">历史称谓：${escapeHtml(props.historical_name)}</div>` : ''}
      ${props.route ? `<div class="popup-route">传播线索：${escapeHtml(props.route)}</div>` : ''}
      ${props.notes ? `<div class="popup-notes">${escapeHtml(props.notes)}</div>` : ''}
      ${props.source_literature ? `<div class="popup-source">—— ${escapeHtml(props.source_literature)}</div>` : ''}
    </div>
  `
}

function showPointPopup(feature, lngLat) {
  const popupPosition = normalizedLngLat(lngLat)
  if (!popupPosition) return
  if (!routePopup) {
    routePopup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
      className: 'spread-point-popup',
      maxWidth: '340px',
      offset: 18,
    })
  }
  routePopup.setLngLat(popupPosition).setHTML(popupHtml(feature.properties)).addTo(map)
}

function hidePointPopup() {
  routePopup?.remove()
}

async function focusFeaturePoint(properties) {
  const ingredientId = properties?.ingredient_id
  const eventKeyValue = properties?.event_key
  if (!ingredientId) return
  sidebarCollapsed.value = false
  if (isOverview.value || ingredientId !== activeId.value) {
    await selectIngredient(ingredientId, { focus: false, resetSelection: false })
  }
  if (properties.state === 'origin') {
    currentEventKey.value = ''
    updateNativeSpreadLayers()
    focusFullRoute(760)
    return
  }
  currentEventKey.value = eventKeyValue || ''
  const point = getRoutePointsForIngredient(activeData.value).find(item => item.eventKey === eventKeyValue)
  if (point) focusRoutePoint(point, 820, false)
}

function bindSpreadInteractions() {
  const layers = ['spread-arrival-icons', 'spread-arrival-core']
  layers.forEach(layerId => {
    map.on('mouseenter', layerId, () => {
      map.getCanvas().style.cursor = 'pointer'
    })
    map.on('mousemove', layerId, (event) => {
      const feature = event.features?.[0]
      if (feature) showPointPopup(feature, event.lngLat)
    })
    map.on('mouseleave', layerId, () => {
      map.getCanvas().style.cursor = ''
      hidePointPopup()
    })
    map.on('click', layerId, (event) => {
      const feature = event.features?.[0]
      if (!feature) return
      focusFeaturePoint(feature.properties)
    })
  })
}

function clearPointMarkers() {
  spreadMarkers.forEach(marker => marker.remove())
  spreadMarkers = []
}

function scheduleMarkerSync() {
  if (markerSyncFrame) return
  markerSyncFrame = requestAnimationFrame(() => {
    markerSyncFrame = 0
    syncPointMarkers()
  })
}

function updatePointMarkerScale() {
  if (!map || !spreadMarkers.length) return
  const size = markerSizeForZoom(map.getZoom())
  spreadMarkers.forEach(marker => {
    marker.getElement()?.style.setProperty('--marker-size', `${size}px`)
  })
}

function markerSizeForZoom(zoom) {
  const base = isOverview.value ? 24 : 30
  const scale = isOverview.value ? 5.2 : 6.8
  return clamp(base + Math.max(0, zoom - 2) * scale, isOverview.value ? 22 : 28, isOverview.value ? 42 : 54)
}

function markerCullDistance(zoom) {
  return isOverview.value ? clamp(62 - zoom * 7, 28, 54) : clamp(48 - zoom * 5, 22, 42)
}

function markerPriority(point) {
  if (point.isSelected) return 0
  if (point.isOrigin) return 1
  return 10 + point.ingredientIndex * 100 + point.order
}

function createImageMarker(point, size) {
  const el = document.createElement('button')
  el.type = 'button'
  el.className = `spread-image-marker ${point.isOrigin ? 'origin' : ''} ${point.isSelected ? 'selected' : ''}`
  el.style.setProperty('--ing-color', point.color)
  el.style.setProperty('--marker-size', `${size}px`)
  el.title = point.isOrigin
    ? `${point.ingredient?.name || ''}原产地 · ${point.label}`
    : `${point.ingredient?.name || ''} · ${point.event?.year ? formatYear(point.event.year) : ''} · ${point.label}`

  const img = document.createElement('img')
  img.src = ingredientImage(point.ingredient)
  img.alt = point.ingredient?.name || point.label
  img.loading = 'eager'
  el.appendChild(img)

  const activate = async event => {
    event.stopPropagation()
    event.preventDefault()
    await focusMarkerPoint(point)
  }

  el.addEventListener('pointerup', activate)
  el.addEventListener('click', event => {
    event.stopPropagation()
  })
  el.addEventListener('keydown', async event => {
    if (event.key !== 'Enter' && event.key !== ' ') return
    await activate(event)
  })
  el.addEventListener('mouseenter', () => showPointPopup(pointFeature(point), point.position))
  el.addEventListener('mouseleave', hidePointPopup)
  return el
}

async function focusMarkerPoint(point) {
  if (!point?.ingredient?.ingredient_id) return
  sidebarCollapsed.value = false
  if (isOverview.value || point.ingredient.ingredient_id !== activeId.value) {
    await selectIngredient(point.ingredient.ingredient_id, { focus: false, resetSelection: false })
  }
  if (point.isOrigin) {
    currentEventKey.value = ''
    updateNativeSpreadLayers()
    focusFullRoute(760)
    return
  }
  currentEventKey.value = point.eventKey
  focusRoutePoint(point, 820, false)
}

function syncPointMarkers() {
  clearPointMarkers()
}

async function addVectorLayers() {
  const physLayers = [
    { id: 'coastline', url: '/tiles/vector/coastline', type: 'line', paint: { 'line-color': '#8A7560', 'line-width': 0.6, 'line-opacity': 0.58 } },
    { id: 'rivers', url: '/tiles/vector/rivers', type: 'line', paint: { 'line-color': '#5BA0B8', 'line-width': 0.45, 'line-opacity': 0.62 } },
  ]
  for (const layer of physLayers) {
    try {
      map.addSource(layer.id, { type: 'geojson', data: layer.url })
      map.addLayer({ id: layer.id, type: layer.type, source: layer.id, paint: layer.paint })
    } catch (_) {}
  }
}

function routeBounds() {
  const points = getDisplayedRoutePoints()
    .map(point => normalizedLngLat(point.position))
    .filter(Boolean)
  if (!points.length) return null
  const bounds = new maplibregl.LngLatBounds(points[0], points[0])
  points.slice(1).forEach(point => bounds.extend(point))
  return bounds
}

function focusFullRoute() {
  if (!map) return
  const bounds = routeBounds()
  if (!bounds) return
  const padding = { top: 96, bottom: 92, left: 82, right: sidebarCollapsed.value ? 82 : 486 }
  const maxZoom = isOverview.value ? 4.1 : 5.4
  const camera = map.cameraForBounds(bounds, {
    padding,
    maxZoom,
    bearing: DEFAULT_MAP_BEARING,
  })
  const center = normalizedLngLat(camera?.center) || normalizedLngLat(bounds.getCenter()) || DEFAULT_MAP_CENTER
  const zoom = Number.isFinite(camera?.zoom) ? Math.min(camera.zoom, maxZoom) : maxZoom
  map.stop()
  map.jumpTo({
    center,
    zoom,
    pitch: DEFAULT_MAP_PITCH,
    bearing: DEFAULT_MAP_BEARING,
  })
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  nextTick(() => {
    if (!sidebarCollapsed.value) focusFullRoute(600)
  })
}

function focusRoutePoint(point, duration = 820, updateSelection = true) {
  const center = normalizedLngLat(point?.position)
  if (!map || !center) return
  if (updateSelection) {
    currentEventKey.value = point.event ? stableEventKey(point.event) : ''
  }
  updateNativeSpreadLayers()
  nextTick(() => scrollToActiveEvent())
  map.stop()
  map.easeTo({
    center,
    zoom: point.isOrigin ? 4.15 : 5.65,
    pitch: DEFAULT_MAP_PITCH,
    bearing: DEFAULT_MAP_BEARING,
    duration,
    essential: true,
  })
}

function focusEvent(event) {
  currentEventKey.value = stableEventKey(event)
  const regionKey = normalizeRegionKey(event)
  const points = getRoutePointsForIngredient(activeData.value)
  const point = points.find(item => item.event && normalizeRegionKey(item.event) === regionKey)
    || points.find(item => item.isOrigin && sameLngLat(item.position, event.coordinates))
  focusRoutePoint(point, 820, false)
}

function scrollToActiveEvent() {
  const idx = timeline.value.findIndex(event => stableEventKey(event) === currentEventKey.value)
  if (idx < 0 || !eventListEl.value) return
  const card = eventCardRefs.value[idx]
  if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

function normalizeIngredientData(data, fallback = {}) {
  return {
    ...fallback,
    ...data,
    timeline: sortedTimeline(data?.timeline || fallback?.timeline || []),
  }
}

async function fetchIngredientDetail(id) {
  if (ingredientDetails.value[id]) return ingredientDetails.value[id]
  const res = await fetch(`/api/ingredients/spread/${id}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const fallback = ingredients.value.find(item => item.ingredient_id === id)
  const detail = normalizeIngredientData(await res.json(), fallback)
  ingredientDetails.value = { ...ingredientDetails.value, [id]: detail }
  return detail
}

async function loadIngredients() {
  try {
    const res = await fetch('/api/ingredients/spread')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    ingredients.value = await res.json()
    const entries = await Promise.all(ingredients.value.map(async item => {
      const detail = await fetchIngredientDetail(item.ingredient_id)
      return [item.ingredient_id, detail]
    }))
    ingredientDetails.value = Object.fromEntries(entries)
    activeId.value = OVERVIEW_ID
    currentEventKey.value = ''
    eventCardRefs.value = {}
    updateNativeSpreadLayers()
  } catch (err) {
    console.warn('[IngredientSpread] load failed:', err)
  }
}

async function selectOverview() {
  activeId.value = OVERVIEW_ID
  currentEventKey.value = ''
  imageLoadFailed.value = false
  eventCardRefs.value = {}
  sidebarCollapsed.value = false
  await updateNativeSpreadLayers()
  nextTick(() => focusFullRoute(760))
}

async function selectIngredient(id, options = {}) {
  const { focus = true, resetSelection = true } = options
  activeId.value = id
  sidebarCollapsed.value = false
  imageLoadFailed.value = false
  try {
    const detail = await fetchIngredientDetail(id)
    if (resetSelection) {
      const first = sortedTimeline(detail.timeline)[0]
      currentEventKey.value = first ? stableEventKey(first) : ''
    }
    eventCardRefs.value = {}
    await updateNativeSpreadLayers()
    if (focus) {
      nextTick(() => {
        scrollToActiveEvent()
        focusFullRoute(760)
      })
    }
  } catch (err) {
    console.warn('[IngredientSpread] load detail failed:', err)
  }
}

function initMap() {
  if (!mapContainer.value) return

  map = new maplibregl.Map({
    container: mapContainer.value,
    style: MAP_STYLE,
    center: DEFAULT_MAP_CENTER,
    zoom: DEFAULT_MAP_ZOOM,
    pitch: DEFAULT_MAP_PITCH,
    bearing: DEFAULT_MAP_BEARING,
    antialias: true,
    attributionControl: false,
  })

  map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'bottom-right')

  map.on('load', () => {
    addVectorLayers()
    addNativeSpreadLayers()
  })
}

onMounted(async () => {
  await loadIngredients()
  await nextTick()
  initMap()
})

onUnmounted(() => {
  stopFlowAnimation()
  if (markerSyncFrame) {
    cancelAnimationFrame(markerSyncFrame)
    markerSyncFrame = 0
  }
  if (clusterRouteSyncFrame) {
    cancelAnimationFrame(clusterRouteSyncFrame)
    clusterRouteSyncFrame = 0
  }
  clearPointMarkers()
  hidePointPopup()
  map?.remove()
  map = null
})
</script>

<style scoped>
.spread-page {
  position: fixed;
  top: var(--navbar-h);
  left: 0;
  right: 0;
  bottom: 0;
  background:
    linear-gradient(90deg, rgba(93, 74, 48, 0.045) 1px, transparent 1px),
    linear-gradient(180deg, rgba(93, 74, 48, 0.035) 1px, transparent 1px),
    #f5efe5;
  background-size: 44px 44px;
}

.spread-map {
  width: 100%;
  height: 100%;
  background: #d9e7ec;
}

.spread-vignette {
  position: fixed;
  left: 0;
  right: 0;
  pointer-events: none;
  z-index: 2;
}

.spread-vignette-top {
  top: var(--navbar-h);
  height: 88px;
  background: linear-gradient(180deg, rgba(249, 245, 238, 0.35) 0%, rgba(249, 245, 238, 0) 100%);
}

.spread-vignette-bottom {
  bottom: 0;
  height: 88px;
  background: linear-gradient(180deg, rgba(42, 34, 24, 0) 0%, rgba(42, 34, 24, 0.22) 100%);
}

:deep(.maplibregl-canvas) {
  outline: none;
}

:deep(.maplibregl-ctrl-bottom-right) {
  right: 18px;
  bottom: 18px;
  transition: right 0.38s cubic-bezier(0.4, 0, 0.2, 1), bottom 0.38s cubic-bezier(0.4, 0, 0.2, 1);
}

.spread-page.sidebar-open :deep(.maplibregl-ctrl-bottom-right) {
  right: 438px;
}

:deep(.spread-point-popup .maplibregl-popup-content) {
  padding: 0;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(255, 252, 248, 0.96);
  border: 1px solid rgba(120, 93, 62, 0.18);
  box-shadow: 0 18px 46px rgba(52, 35, 20, 0.18);
  backdrop-filter: blur(12px);
}

:deep(.spread-popup-card) {
  padding: 14px 15px 13px;
  color: rgba(33, 28, 23, 0.88);
  border-top: 3px solid var(--popup-color, #e5394e);
}

:deep(.popup-heading) {
  display: grid;
  grid-template-columns: 30px 1fr;
  gap: 10px;
  align-items: start;
  margin-bottom: 7px;
}

:deep(.popup-order) {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--popup-color, #e5394e) 14%, #fff8ea);
  color: var(--popup-color, #e5394e);
  font-size: 11px;
  font-weight: 700;
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--popup-color, #e5394e) 32%, transparent);
}

:deep(.popup-title) {
  font-family: var(--font-serif);
  font-size: 17px;
  line-height: 1.35;
  margin-bottom: 3px;
}

:deep(.popup-type) {
  display: inline-block;
  margin-bottom: 7px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(120, 93, 62, 0.2);
  color: rgba(80, 64, 48, 0.76);
  font-size: 10px;
  letter-spacing: 0.08em;
}

:deep(.popup-alias),
:deep(.popup-route),
:deep(.popup-source) {
  color: rgba(87, 78, 68, 0.72);
  font-size: 11px;
  line-height: 1.55;
}

:deep(.popup-notes) {
  margin-top: 7px;
  color: rgba(45, 38, 30, 0.82);
  font-size: 12px;
  line-height: 1.75;
}

.map-overlay-info {
  position: fixed;
  top: calc(var(--navbar-h) + 24px);
  left: 24px;
  z-index: 10;
  pointer-events: none;
}

.overlay-kicker {
  color: rgba(36, 28, 20, 0.54);
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin-bottom: 6px;
  text-shadow: 0 1px 0 rgba(255,255,255,0.78);
}

.overlay-year {
  font-family: var(--font-serif);
  font-size: 40px;
  font-weight: 500;
  line-height: 1.08;
  text-shadow: 0 1px 0 rgba(255,255,255,0.78), 0 14px 28px rgba(70, 48, 28, 0.12);
}

.overlay-location {
  font-size: 16px;
  color: rgba(36, 28, 20, 0.82);
  margin-top: 4px;
  text-shadow: 0 1px 0 rgba(255,255,255,0.72);
}

.spread-route-caption {
  position: fixed;
  left: 24px;
  bottom: 28px;
  z-index: 10;
  width: min(430px, calc(100vw - 468px));
  padding: 14px 16px 15px;
  border-left: 2px solid rgba(93, 74, 48, 0.28);
  background: rgba(255, 252, 248, 0.72);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 18px 42px rgba(58, 42, 24, 0.09);
  pointer-events: none;
}

.caption-kicker {
  font-size: 10px;
  color: rgba(87,83,78,0.52);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.caption-title {
  font-family: var(--font-serif);
  font-size: 18px;
  line-height: 1.35;
  color: rgba(28,25,23,0.86);
}

.caption-route {
  margin-top: 6px;
  font-size: 11px;
  line-height: 1.55;
  letter-spacing: 0.03em;
}

.spread-sidebar {
  position: fixed;
  top: var(--navbar-h);
  right: 0;
  bottom: 0;
  width: 420px;
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--glass-border);
  background: linear-gradient(180deg, rgba(255, 252, 248, 0.96) 0%, rgba(246, 238, 226, 0.92) 100%);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  overflow: hidden;
  z-index: 20;
  transform: translateX(0);
  transition: transform 0.38s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: -8px 0 32px rgba(42, 34, 24, 0.12);
}

.spread-sidebar.collapsed {
  transform: translateX(100%);
  box-shadow: none;
}

.sidebar-toggle {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  z-index: 25;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 8px;
  border: 1px solid rgba(180, 165, 140, 0.28);
  border-right: none;
  border-radius: 10px 0 0 10px;
  background: rgba(255, 252, 248, 0.88);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: rgba(70, 48, 28, 0.72);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.28s ease;
  box-shadow: -2px 0 18px rgba(42, 34, 24, 0.08);
}

.sidebar-toggle:hover {
  color: rgba(70, 48, 28, 0.92);
  background: rgba(255, 252, 248, 0.96);
  border-color: rgba(180, 165, 140, 0.42);
  padding-right: 12px;
}

.sidebar-toggle.open {
  right: 420px;
}

.sidebar-toggle .toggle-icon {
  font-size: 13px;
  line-height: 1;
}

.sidebar-toggle .toggle-label {
  font-size: 10px;
  letter-spacing: 0.08em;
  writing-mode: vertical-rl;
}

.sidebar-close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(180, 165, 140, 0.22);
  border-radius: 50%;
  background: rgba(255, 252, 248, 0.6);
  color: rgba(87, 78, 68, 0.6);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 5;
}

.sidebar-close-btn:hover {
  background: rgba(255, 252, 248, 0.9);
  color: rgba(45, 38, 30, 0.8);
  border-color: rgba(180, 165, 140, 0.36);
}

.sidebar-header {
  position: relative;
  padding: 24px 24px 18px;
  border-bottom: 1px solid var(--glass-border);
}

.ingredient-selector {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.ing-tab {
  padding: 5px 14px;
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  background: transparent;
  font-family: var(--font-sans);
  font-size: 12px;
  color: var(--text-mid);
  cursor: pointer;
  transition: all var(--transition);
}

.ing-tab:hover {
  background: var(--amber-soft);
  border-color: rgba(200, 150, 15, 0.3);
}

.ing-tab.active {
  background: color-mix(in srgb, var(--ing-color, var(--amber)) 12%, transparent);
  border-color: var(--ing-color, var(--amber));
  color: var(--ing-color, var(--amber));
  font-weight: 600;
}

.overview-tab {
  --ing-color: #8b6a3e;
}

.ingredient-profile,
.overview-profile {
  display: grid;
  grid-template-columns: 76px 1fr;
  gap: 16px;
  align-items: center;
  margin-bottom: 14px;
}

.ingredient-image,
.overview-emblem {
  position: relative;
  width: 76px;
  height: 76px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background:
    radial-gradient(circle at 30% 22%, rgba(255,255,255,0.98), rgba(255,255,255,0.42) 30%, transparent 58%),
    color-mix(in srgb, var(--ing-color, #e5394e) 16%, #fff8ea);
  border: 1px solid color-mix(in srgb, var(--ing-color, #e5394e) 42%, rgba(180,165,140,0.24));
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.64), 0 16px 34px rgba(70, 48, 28, 0.15);
}

.ingredient-image img {
  width: 94%;
  height: 94%;
  object-fit: contain;
  filter: drop-shadow(0 5px 9px rgba(52, 35, 20, 0.26));
}

.overview-emblem img {
  width: 42px;
  height: 42px;
  object-fit: contain;
  margin-left: -16px;
  filter: drop-shadow(0 4px 10px rgba(70,48,28,0.18));
}

.overview-emblem img:first-child {
  margin-left: 0;
}

.ingredient-image-fallback {
  font-family: var(--font-serif);
  font-size: 32px;
  color: var(--ing-color, #e5394e);
}

.ingredient-title {
  min-width: 0;
}

.ing-name {
  font-family: var(--font-serif);
  font-size: 28px;
  font-weight: 500;
  letter-spacing: 0.06em;
  margin-bottom: 4px;
}

.overview-name {
  color: rgba(70, 48, 28, 0.9);
}

.ing-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px 10px;
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.06em;
}

.ing-species {
  font-size: 11px;
  color: var(--text-muted);
  font-style: italic;
}

.specimen-record {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: 8px 10px;
  align-items: baseline;
  padding: 10px 0;
  margin-bottom: 8px;
  border-top: 1px solid rgba(180, 165, 140, 0.22);
  border-bottom: 1px solid rgba(180, 165, 140, 0.22);
}

.specimen-record span {
  font-size: 9px;
  letter-spacing: 0.14em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.specimen-record strong {
  min-width: 0;
  font-size: 12px;
  font-weight: 500;
  color: rgba(28,25,23,0.78);
}

.ing-summary {
  font-size: 13px;
  line-height: 1.85;
  color: var(--text-mid);
  font-weight: 300;
  letter-spacing: 0.03em;
}

.timeline-section,
.overview-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 24px 8px;
}

.section-label {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.1em;
}

.route-fit-btn {
  border: 1px solid rgba(180, 165, 140, 0.32);
  border-radius: 16px;
  padding: 5px 12px;
  background: rgba(255,252,248,0.56);
  color: rgba(58, 42, 24, 0.74);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition);
}

.route-fit-btn:hover {
  color: var(--text);
  border-color: rgba(120, 93, 62, 0.36);
  background: rgba(255,252,248,0.86);
}

.ingredient-overview-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px 24px;
  display: grid;
  gap: 10px;
  align-content: start;
}

.overview-card {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 13px;
  align-items: center;
  text-align: left;
  border: 1px solid rgba(180, 165, 140, 0.22);
  background: rgba(255,252,248,0.58);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition), background var(--transition);
}

.overview-card:hover {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--ing-color, #c9a646) 42%, rgba(180,165,140,0.22));
  background: rgba(255,252,248,0.82);
  box-shadow: 0 14px 30px rgba(70, 48, 28, 0.09);
}

.overview-card-image {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 35% 25%, rgba(255,255,255,0.9), transparent 58%),
    color-mix(in srgb, var(--ing-color, #c9a646) 18%, #fff8ea);
  box-shadow:
    inset 0 0 0 1px color-mix(in srgb, var(--ing-color, #c9a646) 38%, transparent),
    0 8px 18px rgba(70, 48, 28, 0.12);
}

.overview-card-image img {
  width: 84%;
  height: 84%;
  object-fit: contain;
  filter: drop-shadow(0 4px 7px rgba(52, 35, 20, 0.24));
}

.overview-card-body {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.overview-card-title {
  font-family: var(--font-serif);
  font-size: 18px;
  color: color-mix(in srgb, var(--ing-color, #9b6a2f) 82%, #2e241a);
}

.overview-card-meta {
  font-size: 11px;
  color: rgba(87,83,78,0.62);
}

.overview-card-summary {
  font-size: 12px;
  line-height: 1.55;
  color: rgba(58, 50, 42, 0.76);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.event-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px 24px;
  scroll-behavior: smooth;
}

.event-card {
  position: relative;
  cursor: pointer;
  opacity: 0.84;
  transition: opacity var(--transition);
}

.event-card.duplicate {
  opacity: 0.63;
}

.event-card:hover,
.event-card.active {
  opacity: 1;
}

.event-card-inner {
  display: flex;
  gap: 14px;
  padding: 10px 0;
  border-radius: 8px;
  transition: background var(--transition), padding var(--transition), box-shadow var(--transition);
}

.event-card.active .event-card-inner,
.event-card:hover .event-card-inner {
  padding: 10px 12px;
  background: rgba(255,252,248,0.66);
  box-shadow: inset 0 0 0 1px rgba(180,165,140,0.18);
}

.event-left-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24px;
  flex-shrink: 0;
  padding-top: 3px;
}

.event-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--ing-color, var(--amber)) 13%, #fff8ea);
  color: var(--ing-color, var(--amber));
  flex-shrink: 0;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--ing-color, var(--amber)) 12%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--ing-color, var(--amber)) 38%, transparent);
  overflow: hidden;
}

.event-dot img {
  width: 90%;
  height: 90%;
  object-fit: contain;
}

.event-card.active .event-dot {
  box-shadow: 0 0 0 6px color-mix(in srgb, var(--ing-color, var(--amber)) 20%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--ing-color, var(--amber)) 48%, transparent);
}

.event-line {
  width: 1px;
  flex: 1;
  background: var(--glass-border);
  margin-top: 5px;
}

.event-content {
  flex: 1;
  min-width: 0;
  padding-bottom: 8px;
}

.event-top-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.event-year {
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 500;
}

.event-dynasty {
  font-size: 11px;
  color: var(--text-muted);
}

.event-location {
  font-size: 14px;
  font-weight: 400;
  color: var(--text);
  margin-top: 2px;
}

.event-type-badge {
  display: inline-block;
  font-size: 10px;
  padding: 1px 8px;
  border-radius: 8px;
  border: 1px solid;
  margin-top: 6px;
  letter-spacing: 0.06em;
}

.event-map-note {
  display: inline-flex;
  margin-top: 6px;
  padding: 2px 8px;
  border-radius: 8px;
  background: rgba(120, 93, 62, 0.08);
  color: rgba(87,83,78,0.68);
  font-size: 11px;
  line-height: 1.5;
}

.event-names {
  margin-top: 6px;
  color: rgba(87,83,78,0.68);
  font-size: 11px;
  line-height: 1.55;
}

.event-route {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 7px;
  font-size: 12px;
  line-height: 1.55;
}

.route-arrow {
  font-size: 13px;
}

.event-notes {
  margin: 7px 0 0;
  color: rgba(45,38,30,0.78);
  font-size: 12px;
  line-height: 1.75;
  font-weight: 300;
}

.event-source {
  margin-top: 6px;
  color: rgba(87,83,78,0.56);
  font-size: 11px;
  line-height: 1.55;
}

:deep(.spread-image-marker) {
  width: var(--marker-size, 32px);
  height: var(--marker-size, 32px);
  border: 0;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  appearance: none;
  background: transparent;
  box-shadow: none;
  cursor: pointer;
  transform: translateZ(0);
  transition: width 160ms ease, height 160ms ease, filter 160ms ease, transform 160ms ease;
}

:deep(.spread-image-marker img) {
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
  filter: drop-shadow(0 5px 7px rgba(52, 35, 20, 0.26));
}

:deep(.spread-image-marker.origin) {
  background: transparent;
}

:deep(.spread-image-marker.selected),
:deep(.spread-image-marker:hover) {
  filter: drop-shadow(0 0 10px color-mix(in srgb, var(--ing-color, #c9a646) 54%, transparent));
  transform: translateZ(0) scale(1.08);
}

@media (max-width: 900px) {
  .spread-vignette {
    right: 0;
  }

  .spread-sidebar {
    width: 100%;
    height: 48vh;
    top: auto;
    bottom: 0;
    border-left: none;
    border-top: 1px solid var(--glass-border);
    border-radius: 16px 16px 0 0;
    transform: translateY(100%);
  }

  .spread-sidebar.collapsed {
    transform: translateY(100%);
    box-shadow: none;
  }

  .spread-sidebar:not(.collapsed) {
    transform: translateY(0);
  }

  .sidebar-toggle {
    top: auto;
    bottom: 16px;
    right: 16px;
    flex-direction: row;
    padding: 10px 16px;
    border: 1px solid rgba(180, 165, 140, 0.28);
    border-radius: 20px;
  }

  .sidebar-toggle.open {
    right: 16px;
    bottom: calc(48vh + 16px);
  }

  .sidebar-toggle .toggle-label {
    writing-mode: horizontal-tb;
  }

  :deep(.maplibregl-ctrl-bottom-right) {
    right: 16px;
    bottom: 76px;
  }

  .spread-page.sidebar-open :deep(.maplibregl-ctrl-bottom-right) {
    right: 16px;
    bottom: calc(48vh + 72px);
  }

  .spread-route-caption {
    display: none;
  }

  .map-overlay-info {
    top: calc(var(--navbar-h) + 14px);
    left: 14px;
    right: 14px;
  }

  .overlay-year {
    font-size: 28px;
  }
}
</style>
