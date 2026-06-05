<template>
  <div
    class="free-layout-shell"
    :class="{ 'is-editing': editable }"
    :style="{ width: `${layout.width * scale}px`, height: `${layout.height * scale}px` }"
  >
    <div
      ref="canvasRef"
      class="free-layout-canvas"
      :class="[`pattern-${theme.canvas.backgroundPattern || 'plain'}`]"
      :style="canvasStyle"
      role="application"
      aria-label="自由布局画布"
      tabindex="0"
      @pointerdown="onCanvasPointerDown"
      @keydown="onKeydown"
      @dragover.prevent="onDragOver"
      @drop.prevent="onDrop"
    >
      <FreeLayoutElement
        v-for="element in orderedElements"
        :key="element.id"
        :element="element"
        :theme="theme"
        :editable="editable"
        :selected="selectedIds.includes(element.id)"
        @select="selectElement"
        @drag-start="startDrag"
        @resize-start="startResize"
      />
      <div v-if="marquee" class="marquee-box" :style="marqueeStyle" />
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { getTheme } from '../../data/themes'
import FreeLayoutElement from './FreeLayoutElement.vue'

const props = defineProps({
  layout: { type: Object, required: true },
  scale: { type: Number, default: 1 },
  selectedIds: { type: Array, default: () => [] },
  editable: { type: Boolean, default: false },
})

const emit = defineEmits([
  'select',
  'clear-selection',
  'update-elements',
  'history-point',
  'delete-selected',
  'duplicate-selected',
  'undo',
  'redo',
  'drop-element',
])

const canvasRef = ref(null)
let dragState = null
let resizeState = null
const marquee = ref(null)

const theme = computed(() => getTheme(props.layout.themeId, props.layout.themeOverrides))
const orderedElements = computed(() =>
  (props.layout.elements || [])
    .filter(element => element.visible !== false)
    .slice()
    .sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
)

const canvasStyle = computed(() => ({
  width: `${props.layout.width}px`,
  height: `${props.layout.height}px`,
  backgroundColor: props.layout.backgroundColor || theme.value.canvas.backgroundColor,
  transform: `scale(${props.scale})`,
  transformOrigin: 'top left',
  '--t-primary': theme.value.colors.primary,
  '--t-accent': theme.value.colors.accent,
  '--t-bg': theme.value.colors.bg,
  '--t-paper': theme.value.colors.paper,
  '--t-text': theme.value.colors.text,
  '--map-base-fill': theme.value.colors.mapBaseFill,
  '--map-base-stroke': theme.value.colors.mapBaseStroke,
  '--map-active-fill': theme.value.colors.mapActiveFill,
  '--map-active-stroke': theme.value.colors.mapActiveStroke,
}))

const marqueeStyle = computed(() => {
  if (!marquee.value) return {}
  const x = Math.min(marquee.value.startX, marquee.value.x)
  const y = Math.min(marquee.value.startY, marquee.value.y)
  return {
    left: `${x}px`,
    top: `${y}px`,
    width: `${Math.abs(marquee.value.x - marquee.value.startX)}px`,
    height: `${Math.abs(marquee.value.y - marquee.value.startY)}px`,
  }
})

function selectElement({ id, additive }) {
  if (!props.editable) return
  const current = new Set(props.selectedIds)
  if (additive) {
    if (current.has(id)) current.delete(id)
    else current.add(id)
    emit('select', [...current])
  } else {
    emit('select', [id])
  }
}

function onCanvasPointerDown(event) {
  if (!props.editable || event.target !== canvasRef.value) return
  const point = localPoint(event)
  marquee.value = { startX: point.x, startY: point.y, x: point.x, y: point.y }
  emit('clear-selection')
  window.addEventListener('pointermove', onMarqueeMove)
  window.addEventListener('pointerup', stopMarquee)
}

function onDragOver(event) {
  if (!props.editable) return
  event.dataTransfer.dropEffect = 'copy'
}

function onDrop(event) {
  if (!props.editable) return
  const raw = event.dataTransfer.getData('application/x-studio-element')
  if (!raw) return
  const point = localPoint(event)
  try {
    const item = JSON.parse(raw)
    emit('drop-element', {
      elementType: item.type,
      preset: item.preset,
      x: Math.round(point.x),
      y: Math.round(point.y),
    })
  } catch {
    // Ignore malformed drag payloads from outside the editor.
  }
}

function startDrag({ event, element }) {
  if (!props.editable || element.locked) return
  const selected = props.selectedIds.includes(element.id) ? props.selectedIds : [element.id]
  emit('select', selected)
  dragState = {
    startX: event.clientX,
    startY: event.clientY,
    items: selected
      .map(id => props.layout.elements.find(item => item.id === id))
      .filter(Boolean)
      .map(item => ({ id: item.id, x: item.x, y: item.y, w: item.w, h: item.h })),
  }
  window.addEventListener('pointermove', onDragMove)
  window.addEventListener('pointerup', stopDrag)
}

function onDragMove(event) {
  if (!dragState) return
  const dx = (event.clientX - dragState.startX) / props.scale
  const dy = (event.clientY - dragState.startY) / props.scale
  emit('update-elements', dragState.items.map(item => ({
    id: item.id,
    patch: snapPosition(item, Math.round(item.x + dx), Math.round(item.y + dy)),
  })), { history: false })
}

function stopDrag() {
  if (!dragState) return
  dragState = null
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', stopDrag)
  emit('history-point')
}

function startResize({ event, element, handle }) {
  if (!props.editable || element.locked) return
  emit('select', [element.id])
  resizeState = {
    id: element.id,
    handle,
    startX: event.clientX,
    startY: event.clientY,
    x: element.x,
    y: element.y,
    w: element.w,
    h: element.h,
  }
  window.addEventListener('pointermove', onResizeMove)
  window.addEventListener('pointerup', stopResize)
}

function onResizeMove(event) {
  if (!resizeState) return
  const dx = (event.clientX - resizeState.startX) / props.scale
  const dy = (event.clientY - resizeState.startY) / props.scale
  let { x, y, w, h } = resizeState
  if (resizeState.handle.includes('e')) w += dx
  if (resizeState.handle.includes('s')) h += dy
  if (resizeState.handle.includes('w')) {
    x += dx
    w -= dx
  }
  if (resizeState.handle.includes('n')) {
    y += dy
    h -= dy
  }
  w = Math.max(24, Math.round(w))
  h = Math.max(16, Math.round(h))
  x = clamp(Math.round(x), 0, props.layout.width - w)
  y = clamp(Math.round(y), 0, props.layout.height - h)
  emit('update-elements', [{ id: resizeState.id, patch: { x, y, w, h } }], { history: false })
}

function stopResize() {
  if (!resizeState) return
  resizeState = null
  window.removeEventListener('pointermove', onResizeMove)
  window.removeEventListener('pointerup', stopResize)
  emit('history-point')
}

function onMarqueeMove(event) {
  if (!marquee.value) return
  const point = localPoint(event)
  marquee.value = { ...marquee.value, x: point.x, y: point.y }
}

function stopMarquee() {
  if (!marquee.value) return
  const box = normalizeRect(marquee.value)
  const ids = props.layout.elements
    .filter(element => element.visible !== false && intersects(box, {
      x: element.x,
      y: element.y,
      w: element.w,
      h: element.h,
    }))
    .map(element => element.id)
  marquee.value = null
  window.removeEventListener('pointermove', onMarqueeMove)
  window.removeEventListener('pointerup', stopMarquee)
  emit('select', ids)
}

function onKeydown(event) {
  if (!props.editable) return
  const tag = event.target?.tagName?.toLowerCase()
  if (['input', 'textarea', 'select'].includes(tag)) return
  const selected = props.selectedIds
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
    event.preventDefault()
    emit(event.shiftKey ? 'redo' : 'undo')
    return
  }
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'y') {
    event.preventDefault()
    emit('redo')
    return
  }
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'd') {
    event.preventDefault()
    emit('duplicate-selected')
    return
  }
  if (event.key === 'Escape') emit('clear-selection')
  if ((event.key === 'Delete' || event.key === 'Backspace') && selected.length) {
    event.preventDefault()
    emit('delete-selected')
  }
  const arrows = {
    ArrowLeft: [-1, 0],
    ArrowRight: [1, 0],
    ArrowUp: [0, -1],
    ArrowDown: [0, 1],
  }
  if (!arrows[event.key] || !selected.length) return
  event.preventDefault()
  const step = event.shiftKey ? 10 : 1
  const [mx, my] = arrows[event.key]
  emit('update-elements', selected.map(id => {
    const item = props.layout.elements.find(element => element.id === id)
    return item ? {
      id,
      patch: {
        x: clamp(item.x + mx * step, 0, props.layout.width - item.w),
        y: clamp(item.y + my * step, 0, props.layout.height - item.h),
      },
    } : null
  }).filter(Boolean))
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), Math.max(min, max))
}

function localPoint(event) {
  const rect = canvasRef.value.getBoundingClientRect()
  return {
    x: clamp((event.clientX - rect.left) / props.scale, 0, props.layout.width),
    y: clamp((event.clientY - rect.top) / props.scale, 0, props.layout.height),
  }
}

function snapPosition(item, rawX, rawY) {
  const threshold = 5
  const otherElements = props.layout.elements.filter(element => element.id !== item.id && element.visible !== false)
  const xTargets = [0, props.layout.width / 2, props.layout.width]
  const yTargets = [0, props.layout.height / 2, props.layout.height]
  otherElements.forEach(element => {
    xTargets.push(element.x, element.x + element.w / 2, element.x + element.w)
    yTargets.push(element.y, element.y + element.h / 2, element.y + element.h)
  })
  const candidatesX = [
    { edge: rawX, offset: 0 },
    { edge: rawX + item.w / 2, offset: item.w / 2 },
    { edge: rawX + item.w, offset: item.w },
  ]
  const candidatesY = [
    { edge: rawY, offset: 0 },
    { edge: rawY + item.h / 2, offset: item.h / 2 },
    { edge: rawY + item.h, offset: item.h },
  ]
  let x = rawX
  let y = rawY
  for (const candidate of candidatesX) {
    const target = xTargets.find(value => Math.abs(value - candidate.edge) <= threshold)
    if (target !== undefined) {
      x = Math.round(target - candidate.offset)
      break
    }
  }
  for (const candidate of candidatesY) {
    const target = yTargets.find(value => Math.abs(value - candidate.edge) <= threshold)
    if (target !== undefined) {
      y = Math.round(target - candidate.offset)
      break
    }
  }
  return {
    x: clamp(x, 0, props.layout.width - item.w),
    y: clamp(y, 0, props.layout.height - item.h),
  }
}

function normalizeRect(rect) {
  const x = Math.min(rect.startX, rect.x)
  const y = Math.min(rect.startY, rect.y)
  return { x, y, w: Math.abs(rect.x - rect.startX), h: Math.abs(rect.y - rect.startY) }
}

function intersects(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y
}

onBeforeUnmount(() => {
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', stopDrag)
  window.removeEventListener('pointermove', onResizeMove)
  window.removeEventListener('pointerup', stopResize)
  window.removeEventListener('pointermove', onMarqueeMove)
  window.removeEventListener('pointerup', stopMarquee)
})
</script>

<style scoped>
.free-layout-shell {
  position: relative;
  flex-shrink: 0;
  filter: drop-shadow(0 22px 36px rgba(32, 27, 22, 0.16));
}

.free-layout-canvas {
  position: relative;
  overflow: hidden;
  color: var(--t-text);
  outline: none;
}

.free-layout-canvas::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.pattern-paper::before {
  opacity: 0.18;
  background-image: radial-gradient(rgba(42, 65, 40, 0.16) 0.7px, transparent 0.7px);
  background-size: 12px 12px;
}

.pattern-grain::before {
  opacity: 0.22;
  background-image: radial-gradient(rgba(60, 49, 39, 0.18) 0.7px, transparent 0.7px);
  background-size: 9px 9px;
}

.pattern-cyanotype::before {
  opacity: 0.28;
  background-image: radial-gradient(rgba(255, 255, 255, 0.22) 0.8px, transparent 0.8px);
  background-size: 7px 7px;
}

.is-editing .free-layout-canvas {
  box-shadow: 0 0 0 1px rgba(74, 65, 55, 0.12);
}

.marquee-box {
  position: absolute;
  z-index: 100000;
  border: 1px dashed #3e7891;
  background: rgba(62, 120, 145, 0.1);
  pointer-events: none;
}
</style>
