<template>
  <svg class="spread-route-map" viewBox="0 0 680 360" role="img" :aria-label="ariaLabel">
    <defs>
      <linearGradient id="routeGlow" x1="0" x2="1" y1="0" y2="0">
        <stop offset="0" :stop-color="routeColor" stop-opacity="0.25" />
        <stop offset="1" :stop-color="routeColor" stop-opacity="0.95" />
      </linearGradient>
    </defs>

    <rect width="680" height="360" rx="18" fill="rgba(255,255,255,0.035)" />
    <g class="grid">
      <line v-for="x in gridX" :key="`x-${x}`" :x1="x" y1="34" :x2="x" y2="326" />
      <line v-for="y in gridY" :key="`y-${y}`" x1="34" :y1="y" x2="646" :y2="y" />
    </g>

    <path v-if="routePath" class="route-shadow" :d="routePath" />
    <path v-if="routePath" class="route-line" :d="routePath" />

    <g
      v-for="(point, index) in projectedPoints"
      :key="point.key"
      class="route-point"
      :class="{ selected: point.key === selectedKey }"
      :transform="`translate(${point.x},${point.y})`"
      @click="$emit('select', point.key)"
    >
      <circle r="13" class="point-halo" />
      <circle :r="point.key === selectedKey ? 7 : 5" class="point-core" />
      <text y="-18" class="point-year">{{ point.yearLabel }}</text>
      <text y="29" class="point-label">{{ index === 0 ? 'ORIGIN' : point.location }}</text>
    </g>
  </svg>
</template>

<script setup>
import { computed } from 'vue'
import { routeEventKey } from '../composables/useSpreadRoutes'

const props = defineProps({
  route: { type: Object, default: null },
  selectedKey: { type: String, default: '' },
})

defineEmits(['select'])

const width = 680
const height = 360
const pad = 54
const gridX = [110, 200, 290, 380, 470, 560]
const gridY = [82, 132, 182, 232, 282]

const routeColor = computed(() => props.route?.color || '#C9A646')
const ariaLabel = computed(() => props.route ? `${props.route.name}传播路径` : '传播路径地图')

const routePoints = computed(() => {
  if (!props.route) return []
  const points = []
  if (Array.isArray(props.route.origin_coordinates)) {
    points.push({
      key: `${props.route.ingredient_id}-origin`,
      location: props.route.origin || '起源地',
      coordinates: props.route.origin_coordinates,
      year: null,
      yearLabel: 'Origin',
    })
  }
  ;(props.route.timeline || []).forEach((event, index) => {
    if (!Array.isArray(event.coordinates)) return
    points.push({
      ...event,
      key: routeEventKey(event, index),
      location: event.location || '',
      yearLabel: event.year ? String(event.year) : '',
    })
  })
  return points
})

const projectedPoints = computed(() => {
  if (!routePoints.value.length) return []
  const lngs = routePoints.value.map(point => Number(point.coordinates[0]))
  const lats = routePoints.value.map(point => Number(point.coordinates[1]))
  const minLng = Math.min(...lngs)
  const maxLng = Math.max(...lngs)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  const lngSpan = maxLng - minLng || 1
  const latSpan = maxLat - minLat || 1

  return routePoints.value.map(point => ({
    ...point,
    x: pad + ((Number(point.coordinates[0]) - minLng) / lngSpan) * (width - pad * 2),
    y: height - pad - ((Number(point.coordinates[1]) - minLat) / latSpan) * (height - pad * 2),
  }))
})

const routePath = computed(() => {
  const points = projectedPoints.value
  if (points.length < 2) return ''
  return points.map((point, index) => {
    if (index === 0) return `M ${point.x.toFixed(1)} ${point.y.toFixed(1)}`
    const prev = points[index - 1]
    const cx = (prev.x + point.x) / 2
    const cy = (prev.y + point.y) / 2 - 24
    return `Q ${cx.toFixed(1)} ${cy.toFixed(1)} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`
  }).join(' ')
})
</script>

<style scoped>
.spread-route-map {
  width: 100%;
  height: 100%;
  display: block;
  color: v-bind(routeColor);
}

.grid line {
  stroke: rgba(255,255,255,0.08);
  stroke-width: 1;
}

.route-shadow {
  fill: none;
  stroke: currentColor;
  stroke-width: 14;
  opacity: 0.12;
  stroke-linecap: round;
}

.route-line {
  fill: none;
  stroke: url(#routeGlow);
  stroke-width: 3;
  stroke-linecap: round;
}

.route-point {
  cursor: pointer;
}

.point-halo {
  fill: currentColor;
  opacity: 0.14;
}

.point-core {
  fill: currentColor;
  stroke: rgba(8, 12, 16, 0.96);
  stroke-width: 2;
}

.route-point.selected .point-halo {
  opacity: 0.34;
}

.point-year,
.point-label {
  fill: rgba(255,255,255,0.72);
  font-family: Arial, sans-serif;
  text-anchor: middle;
  pointer-events: none;
}

.point-year {
  font-size: 10px;
  font-weight: 700;
}

.point-label {
  font-size: 9px;
  letter-spacing: 0.05em;
}
</style>
