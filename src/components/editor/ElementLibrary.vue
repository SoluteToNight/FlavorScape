<template>
  <section class="element-library">
    <header class="editor-panel-head">
      <span>Assets</span>
      <strong>元素库</strong>
    </header>

    <div class="element-library-scroll">
      <section v-for="group in EDITOR_ELEMENT_GROUPS" :key="group.id" class="element-group">
        <div class="element-group-title">{{ group.label }}</div>
        <div class="element-grid">
          <button
            v-for="item in group.items"
            :key="`${item.type}-${item.preset || 'default'}`"
            type="button"
            class="element-card"
            draggable="true"
            @click="addElement(item)"
            @dragstart="onDragStart($event, item)"
          >
            <span class="element-card-icon">{{ iconText(item.type) }}</span>
            <strong>{{ item.label }}</strong>
            <small>{{ item.hint }}</small>
          </button>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { EDITOR_ELEMENT_GROUPS } from '../../data/editor-elements'

const props = defineProps({
  addElement: { type: Function, default: null },
})

function addElement(item) {
  props.addElement?.(item)
}

function onDragStart(event, item) {
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('application/x-studio-element', JSON.stringify(item))
}

function iconText(type) {
  const map = {
    text: 'T',
    richText: 'R',
    image: 'IMG',
    badge: 'TAG',
    labelPill: 'PILL',
    divider: 'LINE',
    lineArrow: 'ARW',
    shape: 'BOX',
    icon: 'ICO',
    mapBlock: 'MAP',
    mapLegend: 'PIN',
    evidenceBlock: 'DATA',
    metricCard: 'NUM',
    certCard: 'CERT',
    timelineNode: 'NODE',
    chartBlock: 'CHT',
    quoteBlock: '“”',
    qrPlaceholder: 'QR',
  }
  return map[type] || 'EL'
}
</script>

<style scoped>
.element-library {
  display: grid;
  min-height: 0;
  grid-template-rows: auto minmax(0, 1fr);
}

.element-library-scroll {
  min-height: 0;
  overflow: auto;
  padding: 12px;
}

.editor-panel-head {
  display: grid;
  gap: 2px;
  padding: 12px;
  border-bottom: 1px solid rgba(74, 65, 55, 0.12);
  background: rgba(255, 252, 247, 0.58);
}

.editor-panel-head span,
.element-group-title {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.editor-panel-head strong {
  color: var(--text);
  font-size: 14px;
  font-weight: 850;
}

.element-group + .element-group {
  margin-top: 16px;
}

.element-group-title {
  margin-bottom: 8px;
}

.element-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.element-card {
  display: grid;
  gap: 5px;
  min-height: 104px;
  padding: 10px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 8px;
  background: rgba(255, 252, 247, 0.72);
  color: var(--text);
  cursor: grab;
  text-align: left;
  transition: border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
}

.element-card:hover {
  border-color: rgba(62, 120, 145, 0.42);
  background: rgba(255, 252, 247, 0.96);
  box-shadow: 0 10px 24px rgba(32, 27, 22, 0.08);
}

.element-card:active {
  cursor: grabbing;
}

.element-card-icon {
  display: inline-grid;
  width: 34px;
  height: 24px;
  place-items: center;
  border-radius: 5px;
  background: rgba(62, 120, 145, 0.1);
  color: var(--water);
  font-size: 9px;
  font-weight: 900;
}

.element-card strong {
  font-size: 12px;
  font-weight: 850;
}

.element-card small {
  color: var(--text-muted);
  font-size: 10px;
  line-height: 1.45;
}
</style>
