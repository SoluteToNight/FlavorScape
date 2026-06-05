<template>
  <section class="layer-panel">
    <header class="editor-panel-head">
      <div>
        <span>Layers</span>
        <strong>图层</strong>
      </div>
      <small>{{ selectedIds.length }} 选中</small>
    </header>

    <div class="layer-actions">
      <button type="button" :disabled="!primarySelectedId" @click="$emit('duplicate')">复制</button>
      <button type="button" :disabled="!primarySelectedId" @click="$emit('remove')">删除</button>
    </div>

    <div class="layer-list">
      <button
        v-for="element in orderedElements"
        :key="element.id"
        type="button"
        class="layer-row"
        :class="{ active: selectedIds.includes(element.id), locked: element.locked, hidden: element.visible === false }"
        @click="$emit('select', [element.id])"
      >
        <span class="layer-type">{{ labelForElementType(element.type) }}</span>
        <strong>{{ titleForElement(element) }}</strong>
        <span class="layer-state">
          <button type="button" title="显示/隐藏" @click.stop="$emit('toggle-visible', element)">
            {{ element.visible === false ? '隐' : '显' }}
          </button>
          <button type="button" title="锁定/解锁" @click.stop="$emit('toggle-lock', element)">
            {{ element.locked ? '锁' : '开' }}
          </button>
        </span>
      </button>
    </div>

    <div class="layer-order">
      <button type="button" :disabled="!primarySelectedId" @click="$emit('reorder', 'front')">置顶</button>
      <button type="button" :disabled="!primarySelectedId" @click="$emit('reorder', 'up')">上移</button>
      <button type="button" :disabled="!primarySelectedId" @click="$emit('reorder', 'down')">下移</button>
      <button type="button" :disabled="!primarySelectedId" @click="$emit('reorder', 'back')">置底</button>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { labelForElementType, titleForElement } from '../../data/editor-elements'

const props = defineProps({
  layout: { type: Object, required: true },
  selectedIds: { type: Array, default: () => [] },
})

defineEmits(['select', 'toggle-visible', 'toggle-lock', 'reorder', 'duplicate', 'remove'])

const orderedElements = computed(() =>
  (props.layout.elements || []).slice().sort((a, b) => (b.zIndex || 0) - (a.zIndex || 0))
)

const primarySelectedId = computed(() => props.selectedIds[0] || null)
</script>

<style scoped>
.layer-panel {
  border-bottom: 1px solid rgba(74, 65, 55, 0.12);
}

.editor-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px;
  border-bottom: 1px solid rgba(74, 65, 55, 0.12);
  background: rgba(255, 252, 247, 0.58);
}

.editor-panel-head span {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.editor-panel-head strong {
  display: block;
  color: var(--text);
  font-size: 14px;
  font-weight: 850;
}

.editor-panel-head small {
  color: var(--text-muted);
  font-size: 10px;
}

.layer-actions,
.layer-order {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
  padding: 8px 12px;
}

.layer-order {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  border-top: 1px solid rgba(74, 65, 55, 0.1);
}

.layer-actions button,
.layer-order button,
.layer-state button {
  min-height: 26px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 5px;
  background: rgba(255, 252, 247, 0.74);
  color: var(--text-mid);
  cursor: pointer;
  font-size: 10px;
  font-weight: 800;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.layer-list {
  display: grid;
  max-height: 280px;
  overflow: auto;
  gap: 6px;
  padding: 0 12px 10px;
}

.layer-row {
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  min-height: 36px;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.58);
  color: var(--text);
  cursor: pointer;
  padding: 4px 6px;
  text-align: left;
}

.layer-row.active {
  border-color: rgba(62, 120, 145, 0.5);
  background: rgba(62, 120, 145, 0.08);
}

.layer-row.hidden {
  opacity: 0.55;
}

.layer-type {
  color: var(--water);
  font-size: 10px;
  font-weight: 850;
}

.layer-row strong {
  overflow: hidden;
  color: var(--text-mid);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.layer-state {
  display: inline-flex;
  gap: 4px;
}

.layer-state button {
  min-width: 26px;
  padding: 0;
}
</style>
