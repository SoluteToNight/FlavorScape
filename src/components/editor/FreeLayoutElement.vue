<template>
  <div
    v-if="element.visible !== false"
    class="layout-element"
    :class="{ selected, editable, locked: element.locked }"
    :style="frameStyle"
    role="button"
    :aria-label="elementLabel"
    tabindex="0"
    @pointerdown.stop="onPointerDown"
    @keydown.enter.prevent="emitSelect(false)"
    @keydown.space.prevent="emitSelect(false)"
  >
    <component :is="contentComponent" :element="element" :theme="theme" />
    <template v-if="editable && selected && !element.locked">
      <button
        v-for="handle in handles"
        :key="handle"
        type="button"
        class="resize-handle"
        :class="`handle-${handle}`"
        :aria-label="`缩放 ${handle}`"
        @pointerdown.stop="startResize($event, handle)"
      />
    </template>
    <span v-if="editable && element.locked" class="lock-mark">LOCK</span>
  </div>
</template>

<script setup>
import { computed, h } from 'vue'
import {
  Award,
  BadgeCheck,
  BarChart3,
  FileText,
  Image as ImageIcon,
  Leaf,
  LineChart,
  MapPin,
  Package,
  QrCode,
  Quote,
  ShieldCheck,
  Type,
} from '@lucide/vue'
import StaticGeoMap from '../StaticGeoMap.vue'

const props = defineProps({
  element: { type: Object, required: true },
  theme: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  editable: { type: Boolean, default: false },
})

const emit = defineEmits(['select', 'drag-start', 'resize-start'])

const handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w']
const elementLabel = computed(() => `${props.element.type} ${props.element.content || props.element.subtitle || ''}`.trim())
const frameStyle = computed(() => ({
  left: `${props.element.x}px`,
  top: `${props.element.y}px`,
  width: `${props.element.w}px`,
  height: `${props.element.h}px`,
  zIndex: props.element.zIndex || 1,
  opacity: props.element.opacity ?? 1,
}))

const contentComponent = computed(() => {
  const map = {
    text: TextContent,
    image: ImageContent,
    badge: BadgeContent,
    divider: DividerContent,
    shape: ShapeContent,
    mapBlock: MapContent,
    evidenceBlock: EvidenceContent,
    narrativeBlock: NarrativeContent,
    titleBlock: NarrativeContent,
    richText: TextContent,
    icon: IconContent,
    labelPill: PillContent,
    metricCard: MetricCardContent,
    certCard: CertCardContent,
    timelineNode: TimelineNodeContent,
    chartBlock: ChartBlockContent,
    mapLegend: MapLegendContent,
    quoteBlock: QuoteBlockContent,
    qrPlaceholder: QrPlaceholderContent,
    lineArrow: LineArrowContent,
  }
  return map[props.element.type] || TextContent
})

function emitSelect(additive) {
  emit('select', { id: props.element.id, additive })
}

function onPointerDown(event) {
  if (!props.editable) return
  emitSelect(event.shiftKey)
  if (props.element.locked) return
  emit('drag-start', { event, element: props.element })
}

function startResize(event, handle) {
  emit('resize-start', { event, element: props.element, handle })
}

const TextContent = {
  props: ['element'],
  render() {
    return h('div', {
      class: 'text-content',
      style: {
        fontSize: `${this.element.fontSize}px`,
        fontFamily: this.element.fontFamily,
        fontWeight: this.element.fontWeight,
        fontStyle: this.element.fontStyle,
        color: this.element.color,
        textAlign: this.element.textAlign,
        lineHeight: this.element.lineHeight,
        letterSpacing: `${this.element.letterSpacing || 0}px`,
      },
      innerHTML: sanitize(this.element.content || ''),
    })
  },
}

const ImageContent = {
  props: ['element'],
  render() {
    return h('img', {
      class: 'image-content',
      src: this.element.src,
      alt: this.element.content || '画布图片',
      draggable: 'false',
      style: {
        objectFit: this.element.objectFit || 'cover',
        objectPosition: `${this.element.objectPositionX ?? 50}% ${this.element.objectPositionY ?? 50}%`,
        borderRadius: `${this.element.borderRadius || 0}px`,
      },
    })
  },
}

const BadgeContent = {
  props: ['element'],
  render() {
    return h('div', {
      class: ['badge-content', this.element.style],
      style: {
        color: this.element.color,
        backgroundColor: this.element.bgColor,
        borderColor: this.element.color,
      },
    }, this.element.content)
  },
}

const DividerContent = {
  props: ['element'],
  render() {
    return h('div', {
      class: 'divider-content',
      style: {
        borderTop: `${this.element.thickness || 1}px ${this.element.style || 'solid'} ${this.element.color}`,
      },
    })
  },
}

const ShapeContent = {
  props: ['element'],
  render() {
    return h('div', {
      class: 'shape-content',
      style: {
        background: this.element.fill,
        border: `1px solid ${this.element.stroke || 'transparent'}`,
        borderRadius: this.element.shape === 'ellipse' ? '999px' : `${this.element.borderRadius || 0}px`,
      },
    })
  },
}

const MapContent = {
  props: ['element'],
  render() {
    return h('div', {
      class: 'map-content',
      style: {
        '--t-primary': this.element.color,
        '--t-accent': this.element.accent,
      },
    }, [
      h(StaticGeoMap, {
        targetProvince: this.element.province || '',
        nodes: this.element.nodes || [],
      }),
    ])
  },
}

const EvidenceContent = {
  props: ['element'],
  render() {
    return h('div', {
      class: 'evidence-content',
      style: {
        gridTemplateColumns: `repeat(${this.element.columns || 3}, minmax(0, 1fr))`,
        gap: `${this.element.gap || 10}px`,
      },
    }, (this.element.evidence || []).map(item => h('div', { key: item.label, class: 'metric-card' }, [
      h('span', { style: { color: this.element.labelColor } }, item.label),
      h('strong', { style: { color: this.element.valueColor } }, item.value),
    ])))
  },
}

const NarrativeContent = {
  props: ['element'],
  render() {
    return h('section', {
      class: 'narrative-content',
      style: {
        color: this.element.color,
        background: this.element.paper,
        '--n-accent': this.element.accent,
      },
    }, [
      h('span', this.element.kicker),
      h('h3', this.element.subtitle),
      h('p', { innerHTML: sanitize(this.element.content || '') }),
    ])
  },
}

const ICONS = {
  Award,
  BadgeCheck,
  BarChart3,
  FileText,
  Image: ImageIcon,
  Leaf,
  LineChart,
  MapPin,
  Package,
  QrCode,
  Quote,
  ShieldCheck,
  Type,
}

const IconContent = {
  props: ['element'],
  render() {
    const Icon = ICONS[this.element.iconName] || MapPin
    return h('div', { class: 'icon-content', style: { color: this.element.color } }, [
      h(Icon, {
        size: '100%',
        strokeWidth: this.element.strokeWidth || 1.8,
      }),
    ])
  },
}

const PillContent = {
  props: ['element'],
  render() {
    return h('div', {
      class: 'pill-content',
      style: {
        color: this.element.color,
        background: this.element.bgColor,
        borderColor: this.element.color,
        borderRadius: `${this.element.borderRadius || 999}px`,
      },
    }, this.element.content)
  },
}

const MetricCardContent = {
  props: ['element'],
  render() {
    return h('section', {
      class: 'metric-card-content',
      style: {
        background: this.element.paper,
        '--metric-main': this.element.valueColor,
        '--metric-muted': this.element.labelColor,
      },
    }, [
      h('span', this.element.label),
      h('strong', this.element.value),
      h('p', this.element.note),
    ])
  },
}

const CertCardContent = {
  props: ['element'],
  render() {
    const Icon = ICONS[this.element.iconName] || ShieldCheck
    return h('section', {
      class: 'cert-card-content',
      style: {
        background: this.element.paper,
        '--cert-main': this.element.color,
      },
    }, [
      h('div', { class: 'cert-card-mark' }, [h(Icon, { size: 22, strokeWidth: 1.8 })]),
      h('div', [h('span', this.element.org), h('strong', this.element.result), h('small', `REP: ${this.element.code}`)]),
    ])
  },
}

const TimelineNodeContent = {
  props: ['element'],
  render() {
    return h('section', {
      class: 'timeline-node-content',
      style: {
        '--node-main': this.element.color,
        '--node-muted': this.element.muted,
      },
    }, [
      h('i'),
      h('div', [h('strong', this.element.title), h('span', this.element.desc)]),
    ])
  },
}

const ChartBlockContent = {
  props: ['element'],
  render() {
    const ticks = this.element.chartKind === 'radar' ? [0, 1, 2, 3, 4] : [0, 1, 2, 3]
    return h('section', {
      class: ['chart-block-content', `chart-${this.element.chartKind || 'trend'}`],
      style: {
        background: this.element.paper,
        '--chart-main': this.element.color,
        '--chart-muted': this.element.muted,
      },
    }, [
      h('header', [h('span', this.element.title), h('small', this.element.chartKind || 'trend')]),
      h('div', { class: 'chart-visual' }, ticks.map(index => h('i', { key: index }))),
    ])
  },
}

const MapLegendContent = {
  props: ['element'],
  render() {
    return h('section', {
      class: 'map-legend-content',
      style: {
        background: this.element.paper,
        '--legend-main': this.element.color,
        '--legend-muted': this.element.muted,
      },
    }, [
      h('strong', this.element.title),
      h('span', this.element.subtitle),
      h('div', (this.element.nodes || []).slice(0, 3).map(node => h('p', { key: node.short || node.name }, [
        h('i'),
        h('span', node.short || node.name),
      ]))),
    ])
  },
}

const QuoteBlockContent = {
  props: ['element'],
  render() {
    return h('section', {
      class: 'quote-block-content',
      style: {
        background: this.element.paper,
        color: this.element.textColor,
        '--quote-main': this.element.color,
      },
    }, [
      h(Quote, { size: 22, strokeWidth: 1.5 }),
      h('p', { innerHTML: sanitize(this.element.content || '') }),
    ])
  },
}

const QrPlaceholderContent = {
  props: ['element'],
  render() {
    return h('section', {
      class: 'qr-placeholder-content',
      style: {
        color: this.element.color,
        '--qr-muted': this.element.muted,
      },
    }, [
      h('div', Array.from({ length: 9 }, (_, index) => h('i', { key: index }))),
      h('span', this.element.label),
    ])
  },
}

const LineArrowContent = {
  props: ['element'],
  render() {
    return h('div', {
      class: 'line-arrow-content',
      style: {
        color: this.element.color,
        '--line-thickness': `${this.element.thickness || 2}px`,
      },
    })
  },
}

function sanitize(value) {
  return String(value)
    .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
    .replace(/<(?!\/?span(?=>|\s.*>))[^>]+>/gi, '')
    .replace(/\n/g, '<br>')
}
</script>

<style>
.layout-element {
  position: absolute;
  z-index: 1;
  user-select: none;
  outline: none;
}

.layout-element.editable {
  cursor: grab;
}

.layout-element.locked {
  cursor: not-allowed;
}

.layout-element.editable:hover {
  box-shadow: inset 0 0 0 1px rgba(62, 120, 145, 0.28);
}

.layout-element.selected {
  box-shadow: inset 0 0 0 2px #3e7891, 0 0 0 1px rgba(255, 255, 255, 0.9);
}

.text-content,
.image-content,
.badge-content,
.divider-content,
.shape-content,
.map-content,
.evidence-content,
.narrative-content,
.icon-content,
.pill-content,
.metric-card-content,
.cert-card-content,
.timeline-node-content,
.chart-block-content,
.map-legend-content,
.quote-block-content,
.qr-placeholder-content,
.line-arrow-content {
  width: 100%;
  height: 100%;
}

.text-content {
  overflow: hidden;
  overflow-wrap: anywhere;
}

.image-content {
  display: block;
  pointer-events: none;
}

.badge-content {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  border: 1px solid currentColor;
  border-radius: 999px;
  padding: 0 10px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.badge-content.seal {
  width: 100%;
  border-radius: 4px;
}

.divider-content {
  position: absolute;
  top: 50%;
  left: 0;
}

.shape-content {
  pointer-events: none;
}

.map-content {
  color: var(--t-primary);
}

.evidence-content {
  display: grid;
  align-items: stretch;
  height: 100%;
}

.metric-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: center;
  border-top: 1px solid rgba(32, 27, 22, 0.12);
  padding-top: 8px;
}

.metric-card span {
  overflow: hidden;
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metric-card strong {
  margin-top: 6px;
  font-family: var(--font-serif);
  font-size: 18px;
  line-height: 1.1;
}

.narrative-content {
  overflow: hidden;
  border-radius: 8px;
  padding: 16px;
}

.narrative-content span {
  display: block;
  color: var(--n-accent);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.narrative-content h3 {
  margin: 5px 0 8px;
  color: var(--n-accent);
  font-size: 15px;
}

.narrative-content p {
  margin: 0;
  font-size: 12px;
  line-height: 1.7;
}

.narrative-content :deep(.hl),
.text-content :deep(.hl) {
  color: var(--n-accent, currentColor);
  font-weight: 800;
}

.icon-content {
  display: grid;
  place-items: center;
}

.pill-content {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid currentColor;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 850;
}

.metric-card-content,
.cert-card-content,
.chart-block-content,
.map-legend-content,
.quote-block-content,
.qr-placeholder-content {
  overflow: hidden;
  border: 1px solid rgba(32, 27, 22, 0.08);
  border-radius: 8px;
  padding: 14px;
}

.metric-card-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.metric-card-content span {
  color: var(--metric-muted);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.metric-card-content strong {
  margin-top: 8px;
  color: var(--metric-main);
  font-family: var(--font-serif);
  font-size: 26px;
  line-height: 1;
}

.metric-card-content p {
  margin: 8px 0 0;
  color: var(--metric-muted);
  font-size: 10px;
  line-height: 1.45;
}

.cert-card-content {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  color: var(--cert-main);
  background-image: radial-gradient(rgba(0, 0, 0, 0.08) 0.6px, transparent 0.6px);
  background-size: 5px 5px;
}

.cert-card-mark {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid currentColor;
  border-radius: 999px;
}

.cert-card-content span,
.cert-card-content small {
  display: block;
  color: rgba(32, 27, 22, 0.56);
  font-size: 10px;
}

.cert-card-content strong {
  display: block;
  margin: 5px 0;
  color: #222;
  font-size: 13px;
}

.timeline-node-content {
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr);
  gap: 10px;
  color: var(--node-main);
}

.timeline-node-content > i {
  position: relative;
  width: 9px;
  height: 9px;
  margin: 7px auto 0;
  border-radius: 999px;
  background: currentColor;
}

.timeline-node-content > i::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 12px;
  width: 1px;
  height: 58px;
  background: currentColor;
  opacity: 0.3;
}

.timeline-node-content strong {
  display: block;
  color: var(--node-main);
  font-size: 13px;
}

.timeline-node-content span {
  display: block;
  margin-top: 5px;
  color: var(--node-muted);
  font-size: 11px;
  line-height: 1.5;
}

.chart-block-content header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--chart-main);
  font-size: 12px;
  font-weight: 850;
}

.chart-block-content small {
  color: var(--chart-muted);
  font-size: 9px;
  text-transform: uppercase;
}

.chart-visual {
  position: relative;
  height: calc(100% - 28px);
  margin-top: 12px;
  border-bottom: 1px solid rgba(32, 27, 22, 0.12);
  border-left: 1px solid rgba(32, 27, 22, 0.1);
}

.chart-visual i {
  position: absolute;
  bottom: 0;
  width: 14%;
  border-radius: 3px 3px 0 0;
  background: var(--chart-main);
  opacity: 0.75;
}

.chart-visual i:nth-child(1) { left: 8%; height: 35%; }
.chart-visual i:nth-child(2) { left: 30%; height: 58%; }
.chart-visual i:nth-child(3) { left: 52%; height: 44%; }
.chart-visual i:nth-child(4) { left: 74%; height: 76%; }
.chart-visual i:nth-child(5) { left: 42%; bottom: 16%; width: 22%; height: 22%; border-radius: 999px; background: transparent; border: 2px solid var(--chart-main); }

.chart-radar .chart-visual {
  border: 0;
}

.map-legend-content {
  color: var(--legend-main);
}

.map-legend-content strong,
.map-legend-content span {
  display: block;
}

.map-legend-content strong {
  font-size: 13px;
}

.map-legend-content > span {
  margin-top: 4px;
  color: var(--legend-muted);
  font-size: 10px;
}

.map-legend-content p {
  display: flex;
  align-items: center;
  gap: 7px;
  margin: 9px 0 0;
  color: var(--legend-muted);
  font-size: 10px;
}

.map-legend-content i {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--legend-main);
}

.quote-block-content {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 10px;
}

.quote-block-content svg {
  color: var(--quote-main);
}

.quote-block-content p {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 14px;
  line-height: 1.65;
}

.qr-placeholder-content {
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  gap: 8px;
  text-align: center;
}

.qr-placeholder-content div {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
}

.qr-placeholder-content i {
  border-radius: 2px;
  background: currentColor;
  opacity: 0.22;
}

.qr-placeholder-content i:nth-child(1),
.qr-placeholder-content i:nth-child(3),
.qr-placeholder-content i:nth-child(5),
.qr-placeholder-content i:nth-child(8) {
  opacity: 0.85;
}

.qr-placeholder-content span {
  color: var(--qr-muted);
  font-size: 10px;
}

.line-arrow-content {
  position: relative;
}

.line-arrow-content::before {
  content: '';
  position: absolute;
  left: 0;
  right: 10px;
  top: calc(50% - var(--line-thickness) / 2);
  border-top: var(--line-thickness) solid currentColor;
}

.line-arrow-content::after {
  content: '';
  position: absolute;
  right: 0;
  top: calc(50% - 5px);
  width: 10px;
  height: 10px;
  border-right: var(--line-thickness) solid currentColor;
  border-top: var(--line-thickness) solid currentColor;
  transform: rotate(45deg);
}

.resize-handle {
  position: absolute;
  z-index: 20;
  width: 9px;
  height: 9px;
  border: 1px solid #3e7891;
  border-radius: 999px;
  background: #fff;
  cursor: pointer;
}

.handle-nw { top: -5px; left: -5px; cursor: nwse-resize; }
.handle-n { top: -5px; left: calc(50% - 5px); cursor: ns-resize; }
.handle-ne { top: -5px; right: -5px; cursor: nesw-resize; }
.handle-e { top: calc(50% - 5px); right: -5px; cursor: ew-resize; }
.handle-se { right: -5px; bottom: -5px; cursor: nwse-resize; }
.handle-s { bottom: -5px; left: calc(50% - 5px); cursor: ns-resize; }
.handle-sw { bottom: -5px; left: -5px; cursor: nesw-resize; }
.handle-w { top: calc(50% - 5px); left: -5px; cursor: ew-resize; }

.lock-mark {
  position: absolute;
  right: 4px;
  top: 4px;
  border-radius: 3px;
  background: rgba(32, 27, 22, 0.7);
  color: white;
  font-size: 8px;
  padding: 2px 4px;
}
</style>
