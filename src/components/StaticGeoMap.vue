<template>
  <div class="static-geo-map">
    <svg viewBox="-15 -15 350 350" width="100%" height="100%" class="carto-svg-viewport">
      <g class="carto-grid-mesh" opacity="0.15">
        <line v-for="n in 5" :key="'h-'+n" x1="0" :y1="n * 60" x2="320" :y2="n * 60" stroke="currentColor" stroke-width="0.5" />
        <line v-for="n in 5" :key="'v-'+n" :x1="n * 60" y1="0" :x2="n * 60" y2="320" stroke="currentColor" stroke-width="0.5" />
      </g>

      <path
        v-for="feature in geoData.features"
        :key="feature.properties.id"
        :d="pathGenerator(feature)"
        class="map-province-path"
        :class="{ 'is-target-active': feature.properties.name === targetProvince }"
      />

      <path v-if="curvedPath" :d="curvedPath" class="vector-flow-arc" />

      <g v-for="(node, i) in projectedNodes" :key="i" :transform="'translate(' + node.x + ',' + node.y + ')'">
        <circle v-if="i === 0" r="7" class="origin-target-halo" />
        <circle r="3" class="node-core-dot" />
        <text y="-8" class="node-micro-code">{{ node.code }}</text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { geoMercator, geoPath } from 'd3-geo'
import chinaGeoJson from '@/assets/china.json'

const props = defineProps({
  targetProvince: { type: String, required: true },
  nodes: { type: Array, default: () => [] },
})

const geoData = chinaGeoJson

const projection = geoMercator()
  .center([105, 36.5])
  .scale(320)
  .translate([160, 160])

const pathGenerator = geoPath().projection(projection)

const projectedNodes = computed(() => {
  return props.nodes.map((node, index) => {
    const [x, y] = projection(node.coord)
    return { ...node, x, y, code: index === 0 ? 'ORIGIN' : `LOC.${index}` }
  })
})

const curvedPath = computed(() => {
  if (projectedNodes.value.length < 2) return null
  return projectedNodes.value.map((node, index) => {
    if (index === 0) return `M ${node.x},${node.y}`
    const prev = projectedNodes.value[index - 1]
    const cx = (prev.x + node.x) / 2 - 12
    const cy = (prev.y + node.y) / 2 - 20
    return `Q ${cx},${cy} ${node.x},${node.y}`
  }).join(' ')
})
</script>

<style scoped>
.static-geo-map {
  position: relative;
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  overflow: hidden;
  display: grid;
  place-items: center;
  contain: layout paint;
}

.carto-svg-viewport {
  display: block;
  width: 100% !important;
  height: 100% !important;
  max-width: 100%;
  max-height: 100%;
  overflow: hidden;
  color: var(--t-primary);
  object-fit: contain;
}

.map-province-path {
  fill: var(--map-base-fill, rgba(40, 35, 30, 0.04));
  stroke: var(--map-base-stroke, rgba(0, 0, 0, 0.15));
  stroke-width: 0.6;
  transition: all 0.4s ease;
}

.map-province-path.is-target-active {
  fill: var(--map-active-fill, var(--t-primary));
  stroke: var(--map-active-stroke, var(--t-accent));
  stroke-width: 1.4;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.06));
}

.vector-flow-arc {
  fill: none;
  stroke: var(--t-accent);
  stroke-width: 1.5;
  stroke-dasharray: 4 3;
}

.node-core-dot {
  fill: var(--t-accent);
}

.origin-target-halo {
  fill: none;
  stroke: var(--t-accent);
  stroke-width: 1;
  opacity: 0.5;
}

.node-micro-code {
  fill: var(--t-text);
  font-size: 7px;
  font-family: monospace;
  font-weight: 700;
  text-anchor: middle;
  opacity: 0.5;
}
</style>
