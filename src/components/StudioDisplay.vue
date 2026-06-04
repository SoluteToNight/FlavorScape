<template>
  <article class="display-canvas" :style="{ transform: `scale(${scale})`, transformOrigin: 'top left' }">
    <div class="display-bg" />
    <header class="display-head">
      <div>
        <span class="kicker">FLAVORSCAPE LIVE DISPLAY</span>
        <h1>{{ displayData.title }}</h1>
        <p>{{ displayData.subtitle }}</p>
      </div>
      <div v-if="displayData.routeInteractionEnabled" class="mode-chip">
        {{ displayData.interactionMode === 'route' ? '传播路径交互' : '产品空间节点' }}
      </div>
    </header>

    <section v-if="displayData.interactionMode === 'route'" class="route-mode">
      <div class="route-map-wrap">
        <StaticSpreadRouteMap
          v-if="routeData"
          :route="routeData"
          :selected-key="selectedKey"
          @select="$emit('select-event', $event)"
        />
        <div v-else class="route-empty">等待选择传播路径</div>
      </div>
      <aside class="route-info">
        <span class="kicker">Selected Route</span>
        <h2>{{ routeData?.name || '未选择路径' }}</h2>
        <p>{{ routeData?.summary || displayData.caption }}</p>
        <div v-if="displayData.routeInteractionEnabled && routeOptions.length" class="route-picker">
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
        <div class="route-stats">
          <div>
            <span>起源地</span>
            <strong>{{ routeData?.origin || '--' }}</strong>
          </div>
          <div>
            <span>事件数</span>
            <strong>{{ routeData?.timeline?.length || 0 }}</strong>
          </div>
        </div>
        <div v-if="selectedEvent && displayData.showTimeline" class="event-focus">
          <span>{{ selectedEvent.year }} · {{ selectedEvent.dynasty }}</span>
          <strong>{{ selectedEvent.location }}</strong>
          <p>{{ selectedEvent.route || selectedEvent.event_type }}</p>
        </div>
        <div v-if="routeData?.timeline?.length && displayData.showTimeline" class="timeline-list">
          <button
            v-for="(event, index) in routeData.timeline.slice(0, 5)"
            :key="routeEventKey(event, index)"
            type="button"
            :class="{ active: routeEventKey(event, index) === selectedKey }"
            @click="$emit('select-event', routeEventKey(event, index))"
          >
            <span>{{ event.year }}</span>
            <strong>{{ event.location }}</strong>
          </button>
        </div>
      </aside>
    </section>

    <section v-else class="product-mode">
      <div v-if="showProductPanel" class="product-panel">
        <span class="kicker">Product Asset</span>
        <h2 v-if="displayData.modules?.productInfo !== false">{{ displayData.productName }}</h2>
        <p v-if="displayData.modules?.productInfo !== false && displayData.caption">{{ displayData.caption }}</p>
        <div v-if="displayData.modules?.evidenceMetrics !== false && displayData.spatial.evidence.length" class="evidence-grid">
          <div v-for="item in displayData.spatial.evidence" :key="item.label">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </div>
      <div v-if="displayData.modules?.spatialNodes !== false && displayData.spatial.nodes.length" class="node-board">
        <div
          v-for="(node, index) in displayData.spatial.nodes"
          :key="node.short"
          class="node-card"
        >
          <span>0{{ index + 1 }}</span>
          <strong>{{ node.short }}</strong>
          <p v-if="displayData.showTimeline">{{ node.desc }}</p>
        </div>
      </div>
    </section>

    <footer class="display-foot">
      <span>{{ displayData.province }} · {{ displayData.origin }}</span>
      <span>{{ displayData.category }}</span>
    </footer>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { routeEventKey } from '../composables/useSpreadRoutes'
import StaticSpreadRouteMap from './StaticSpreadRouteMap.vue'

const props = defineProps({
  displayData: { type: Object, required: true },
  routeData: { type: Object, default: null },
  routeOptions: { type: Array, default: () => [] },
  scale: { type: Number, default: 1 },
})

defineEmits(['select-event', 'select-route'])

const selectedKey = computed(() => {
  if (props.displayData.selectedEventKey) return props.displayData.selectedEventKey
  const first = props.routeData?.timeline?.[0]
  return first ? routeEventKey(first, 0) : ''
})

const selectedEvent = computed(() => {
  if (!props.routeData?.timeline?.length) return null
  return props.routeData.timeline.find((event, index) => routeEventKey(event, index) === selectedKey.value)
    || props.routeData.timeline[0]
})

const showProductPanel = computed(() =>
  props.displayData.modules?.productInfo !== false
  || (props.displayData.modules?.evidenceMetrics !== false && Boolean(props.displayData.spatial.evidence?.length))
)
</script>

<style scoped>
.display-canvas {
  width: 960px;
  height: 540px;
  position: relative;
  overflow: hidden;
  background: #081016;
  color: #f8fafc;
  box-shadow: 0 38px 80px rgba(0,0,0,0.24);
}

.display-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 15%, rgba(62,120,145,0.35), transparent 30%),
    linear-gradient(135deg, rgba(255,255,255,0.08), transparent 38%),
    #081016;
}

.display-head,
.display-foot {
  position: absolute;
  left: 34px;
  right: 34px;
  z-index: 3;
  display: flex;
  justify-content: space-between;
  gap: 24px;
}

.display-head {
  top: 28px;
  align-items: flex-start;
}

.display-foot {
  bottom: 24px;
  color: rgba(255,255,255,0.48);
  font-size: 11px;
  letter-spacing: 0.08em;
}

.kicker {
  display: block;
  color: rgba(255,255,255,0.46);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  margin-top: 6px;
  font-family: var(--font-serif);
  font-size: 30px;
  font-weight: 500;
}

.display-head p {
  margin-top: 5px;
  color: rgba(255,255,255,0.62);
  font-size: 13px;
}

.mode-chip {
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 999px;
  padding: 8px 14px;
  color: rgba(255,255,255,0.72);
  font-size: 12px;
}

.route-mode,
.product-mode {
  position: absolute;
  inset: 104px 34px 62px;
  z-index: 2;
  display: grid;
  gap: 20px;
}

.route-mode {
  grid-template-columns: minmax(0, 1fr) 260px;
}

.route-map-wrap,
.product-panel,
.node-card,
.route-info {
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.045);
  border-radius: 8px;
}

.route-map-wrap {
  min-width: 0;
  overflow: hidden;
}

.route-empty {
  height: 100%;
  display: grid;
  place-items: center;
  color: rgba(255,255,255,0.5);
  font-size: 13px;
}

.route-info {
  padding: 18px;
  overflow: hidden;
}

.route-info h2,
.product-panel h2 {
  margin-top: 8px;
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 500;
}

.route-info p,
.product-panel p,
.node-card p {
  margin-top: 10px;
  color: rgba(255,255,255,0.62);
  font-size: 12px;
  line-height: 1.7;
}

.route-info > p {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.route-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 18px;
}

.route-picker {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  margin-top: 14px;
}

.route-picker button,
.timeline-list button {
  width: 100%;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 5px;
  background: rgba(255,255,255,0.045);
  color: rgba(255,255,255,0.64);
  cursor: pointer;
  font-size: 11px;
  font-weight: 700;
  min-height: 28px;
  overflow: hidden;
  padding: 5px 8px;
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: border-color 180ms ease, background 180ms ease, color 180ms ease;
}

.route-picker button:hover,
.route-picker button.active,
.timeline-list button:hover,
.timeline-list button.active {
  border-color: rgba(255,255,255,0.26);
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.route-stats div,
.event-focus {
  border-top: 1px solid rgba(255,255,255,0.12);
  padding-top: 10px;
}

.route-stats span,
.event-focus span {
  display: block;
  color: rgba(255,255,255,0.42);
  font-size: 10px;
}

.route-stats strong,
.event-focus strong {
  display: block;
  margin-top: 4px;
  font-size: 14px;
}

.event-focus {
  margin-top: 18px;
}

.timeline-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  margin-top: 12px;
}

.timeline-list button span {
  display: block;
  color: rgba(255,255,255,0.44);
  font-size: 9px;
}

.timeline-list button strong {
  display: block;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 10px;
}

.timeline-list button.active span {
  color: rgba(255,255,255,0.66);
}

.product-mode {
  grid-template-columns: 310px minmax(0, 1fr);
}

.product-panel {
  padding: 20px;
}

.evidence-grid {
  display: grid;
  gap: 10px;
  margin-top: 20px;
}

.evidence-grid div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 10px;
}

.evidence-grid span {
  color: rgba(255,255,255,0.48);
  font-size: 11px;
}

.evidence-grid strong {
  font-size: 14px;
}

.node-board {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  align-content: center;
}

.node-card {
  min-height: 130px;
  padding: 16px;
}

.node-card span {
  color: rgba(255,255,255,0.38);
  font-family: monospace;
  font-size: 11px;
}

.node-card strong {
  display: block;
  margin-top: 10px;
  font-size: 18px;
}
</style>
