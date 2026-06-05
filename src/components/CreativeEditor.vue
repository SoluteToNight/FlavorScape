<template>
  <section v-if="product" class="creative-editor p-4">
    <header class="editor-head">
      <div>
        <span class="text-2xs uppercase tracking-[0.12em] text-text-muted">{{ editorKicker }}</span>
        <h2>{{ editorTitle }}</h2>
        <p>{{ product.origin }}</p>
      </div>
      <button type="button" class="reset-all-btn" @click="resetCurrentOutput">重置</button>
    </header>

    <AiStudioAssistant v-if="posterData" />

    <template v-if="activeOutput === 'poster' && posterData">
      <FreeLayoutControls v-if="layout" output-type="poster" :data="posterData" />
      <LegacyLayoutUpgrade v-else output-type="poster" :data="posterData" />
    </template>

    <template v-else-if="activeOutput === 'archive' && archiveData">
      <FreeLayoutControls v-if="layout" output-type="archive" :data="archiveData" />
      <LegacyLayoutUpgrade v-else output-type="archive" :data="archiveData" />
    </template>

    <template v-else-if="activeOutput === 'display' && displayData">
      <DisplayEditor />
    </template>
  </section>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { inferTemplateId } from '../data/layout-presets'
import { themeOptions } from '../data/themes'
import AiStudioAssistant from './AiStudioAssistant.vue'
import FreeLayoutControls from './editor/FreeLayoutControls.vue'
import { useSpreadRoutes } from '../composables/useSpreadRoutes'
import { useStudioStore } from '../stores/studio'
import { uploadStudioImage } from '../utils/api.js'

const store = useStudioStore()
const fileInput = ref(null)
const pendingImageElementId = ref(null)
const { routeOptions, error: routeError, loadRoutes } = useSpreadRoutes()

const product = computed(() => store.activeProductCase)
const activeOutput = computed(() => store.activeOutput)
const posterData = computed(() => store.mergedPosterData)
const archiveData = computed(() => store.mergedArchiveData)
const displayData = computed(() => store.mergedDisplayData)
const layout = computed(() => store.activeLayout)

onMounted(loadRoutes)

const editorKicker = computed(() => ({ poster: 'Poster Studio', archive: 'Dossier Studio', display: 'Display Editor' }[activeOutput.value]))
const editorTitle = computed(() => ({ poster: '创意工作台', archive: '白皮书工作台', display: '大屏编辑' }[activeOutput.value]))

const limits = computed(() => {
  const creative = product.value?.marketing?.creative || {}
  return {
    subtitle: creative.desc?.maxLength || 60,
    poeticLine: creative.poeticLine?.maxLength || 40,
    narrative: creative.narrative?.maxLength || 300,
  }
})

function field(type, name, fallback = '') {
  return computed({
    get: () => store[`merged${type[0].toUpperCase()}${type.slice(1)}Data`]?.[name] ?? fallback,
    set: value => store.updateOutputField(type, name, value),
  })
}

const title = field('poster', 'title')
const subtitle = field('poster', 'subtitle')
const poeticLine = field('poster', 'poeticLine')
const narrative = field('poster', 'narrative')
const posterTheme = field('poster', 'theme', 'nature')
const imagePosY = computed({
  get: () => posterData.value?.imagePosY ?? 50,
  set: value => store.updateOutputField('poster', 'imagePosY', Number(value)),
})

const archiveTitle = field('archive', 'title')
const archiveSummary = field('archive', 'summary')
const archiveConclusion = field('archive', 'conclusion')

const displayTitle = field('display', 'title')
const displaySubtitle = field('display', 'subtitle')
const displayCaption = field('display', 'caption')
const interactionMode = field('display', 'interactionMode', 'product')
const selectedRouteId = field('display', 'selectedRouteId', 'tea')
const showTimeline = field('display', 'showTimeline', true)

const visibleEvidence = computed(() => {
  const output = store.activeProject?.outputs?.archive
  return output?.visibleEvidence || archiveData.value?.allEvidence?.map(item => item.label) || []
})

const selectedElement = computed(() => store.selectedElements[0] || null)
const hasCustomImage = computed(() => Boolean(store.activeProject?.outputs?.poster?.customImageDataUrl))
const themeLabel = computed(() => themeOptions.find(t => t.id === posterTheme.value)?.name || '自然探索')

function ensureFreeLayout() {
  if (layout.value) return
  store.initLayout(activeOutput.value, {
    themeId: activeOutput.value === 'poster' ? posterTheme.value : 'nature',
    templateId: inferTemplateId(activeOutput.value, null, activeOutput.value === 'poster' ? posterData.value : archiveData.value),
  })
}

function resetCurrentOutput() {
  if (window.confirm('确认将当前产出恢复为默认内容？')) {
    store.resetOutput(activeOutput.value)
  }
}

function toggleEvidence(label) {
  const next = new Set(visibleEvidence.value)
  if (next.has(label)) next.delete(label)
  else next.add(label)
  store.updateOutputField('archive', 'visibleEvidence', [...next])
}

async function onLegacyImageUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  try {
    const url = await uploadStudioImage(file)
    store.updateOutputField('poster', 'customImageDataUrl', url)
    store.updateOutputField('poster', 'imagePosY', 50)
  } catch (e) {
    console.error('图片上传失败:', e)
  }
  event.target.value = ''
}

function selectElementImage(elementId) {
  pendingImageElementId.value = elementId
  fileInput.value?.click()
}

async function onElementImageUpload(event) {
  const file = event.target.files?.[0]
  const elementId = pendingImageElementId.value
  if (!file || !elementId) return
  try {
    const url = await uploadStudioImage(file)
    store.updateElement(activeOutput.value, elementId, { src: url })
  } catch (e) {
    console.error('图片上传失败:', e)
  }
  event.target.value = ''
  pendingImageElementId.value = null
}

const ClassicPosterEditor = defineComponent({
  setup() {
    return () => h('div', [
      posterData.value.modules?.brandCopy !== false && h('div', [
        fieldGroup('品牌标题', `${title.value.length}/32`, h('input', { value: title.value, maxlength: 32, class: 'field-input', onInput: e => { title.value = e.target.value } }), () => store.resetPosterField('title')),
        fieldGroup('产品描述', `${subtitle.value.length}/${limits.value.subtitle}`, h('input', { value: subtitle.value, maxlength: limits.value.subtitle, class: 'field-input', onInput: e => { subtitle.value = e.target.value } }), () => store.resetPosterField('subtitle')),
        fieldGroup('诗意短句', `${poeticLine.value.length}/${limits.value.poeticLine}`, h('input', { value: poeticLine.value, maxlength: limits.value.poeticLine, class: 'field-input', onInput: e => { poeticLine.value = e.target.value } }), () => store.resetPosterField('poeticLine')),
        fieldGroup('品牌叙事', `${narrative.value.length}/${limits.value.narrative}`, h('textarea', { value: narrative.value, maxlength: limits.value.narrative, rows: 6, class: 'field-textarea', onInput: e => { narrative.value = e.target.value } }), () => store.resetPosterField('narrative')),
      ]),
      h('div', { class: 'field-group' }, [
        h('div', { class: 'field-head' }, [h('label', '视觉主题'), h('span', themeLabel.value)]),
        h('div', { class: 'theme-grid' }, themeOptions.map(item => h('button', {
          type: 'button',
          class: ['theme-option', { active: posterTheme.value === item.id }],
          onClick: () => { posterTheme.value = item.id },
        }, [
          h('span', { class: 'theme-swatch', style: { background: item.swatch } }),
          h('span', [h('strong', item.name), h('small', item.id)]),
        ]))),
      ]),
      posterData.value.modules?.mainImage !== false && h('div', { class: 'field-group' }, [
        h('div', { class: 'field-head' }, [h('label', '主图资产'), h('span', hasCustomImage.value ? '自定义' : '默认')]),
        h('button', { type: 'button', class: 'upload-btn', onClick: () => legacyFileInput.value?.click() }, hasCustomImage.value ? '更换图片' : '上传图片'),
        h('input', { ref: legacyFileInput, type: 'file', accept: 'image/*', class: 'hidden', onChange: onLegacyImageUpload }),
        h('div', { class: 'mt-3' }, [
          h('div', { class: 'field-head mb-1' }, [h('label', '垂直焦点'), h('span', `${imagePosY.value}%`)]),
          h('input', { value: imagePosY.value, type: 'range', min: 0, max: 100, class: 'w-full cursor-pointer', onInput: e => { imagePosY.value = Number(e.target.value) } }),
        ]),
        hasCustomImage.value && h('button', { type: 'button', class: 'reset-btn', onClick: () => store.resetPosterField('customImageDataUrl') }, '恢复默认图'),
      ]),
    ])
  },
})

const LegacyLayoutUpgrade = defineComponent({
  props: {
    outputType: { type: String, required: true },
    data: { type: Object, required: true },
  },
  setup(props) {
    return () => h('section', { class: 'legacy-upgrade' }, [
      h('span', 'Legacy Template'),
      h('h3', `${props.outputType === 'poster' ? '经典海报' : '经典白皮书'}模板`),
      h('p', '这个项目还没有自由布局数据。使用当前经典内容生成一张可拖拽、可缩放、可改层级的自由画布。'),
      h('button', {
        type: 'button',
        class: 'upload-btn',
        onClick: () => store.initLayout(props.outputType, {
          templateId: inferTemplateId(props.outputType, null, props.data),
          themeId: props.outputType === 'poster' ? posterTheme.value : 'nature',
        }),
      }, '使用经典模板生成自由布局'),
    ])
  },
})

const legacyFileInput = ref(null)

const ClassicArchiveEditor = defineComponent({
  setup() {
    return () => h('div', [
      fieldGroup('报告标题', `${archiveTitle.value.length}/42`, h('input', { value: archiveTitle.value, maxlength: 42, class: 'field-input', onInput: e => { archiveTitle.value = e.target.value } })),
      fieldGroup('证明摘要', `${archiveSummary.value.length}/180`, h('textarea', { value: archiveSummary.value, maxlength: 180, rows: 5, class: 'field-textarea', onInput: e => { archiveSummary.value = e.target.value } })),
      archiveData.value.modules?.conclusion !== false && fieldGroup('结论说明', `${archiveConclusion.value.length}/160`, h('textarea', { value: archiveConclusion.value, maxlength: 160, rows: 4, class: 'field-textarea', onInput: e => { archiveConclusion.value = e.target.value } })),
      archiveData.value.modules?.evidenceMetrics !== false && h('div', { class: 'field-group' }, [
        h('div', { class: 'field-head' }, [h('label', '指标显隐'), h('span', `${visibleEvidence.value.length}/${archiveData.value.allEvidence.length}`)]),
        ...archiveData.value.allEvidence.map(item => h('label', { class: 'check-row', key: item.label }, [
          h('input', { type: 'checkbox', checked: visibleEvidence.value.includes(item.label), onChange: () => toggleEvidence(item.label) }),
          h('span', item.label),
        ])),
      ]),
    ])
  },
})

const DisplayEditor = defineComponent({
  setup() {
    return () => h('div', [
      displayData.value.routeInteractionEnabled && h('div', { class: 'field-group' }, [
        h('div', { class: 'field-head' }, [h('label', '大屏交互'), h('span', displayData.value.interactionMode === 'route' ? '传播路径' : '产品节点')]),
        h('div', { class: 'theme-grid' }, [
          toggleCard('产品空间节点', '展示产地、供应链节点和证据指标', interactionMode.value === 'product', () => { interactionMode.value = 'product' }),
          toggleCard('传播路径', '选择一条食材传播路径', interactionMode.value === 'route', () => { interactionMode.value = 'route' }),
        ]),
      ]),
      displayData.value.modules?.productInfo !== false && fieldGroup('大屏标题', `${displayTitle.value.length}/36`, h('input', { value: displayTitle.value, maxlength: 36, class: 'field-input', onInput: e => { displayTitle.value = e.target.value } })),
      displayData.value.modules?.productInfo !== false && fieldGroup('副标题', `${displaySubtitle.value.length}/48`, h('input', { value: displaySubtitle.value, maxlength: 48, class: 'field-input', onInput: e => { displaySubtitle.value = e.target.value } })),
      displayData.value.modules?.productInfo !== false && fieldGroup('展示说明', `${displayCaption.value.length}/160`, h('textarea', { value: displayCaption.value, maxlength: 160, rows: 4, class: 'field-textarea', onInput: e => { displayCaption.value = e.target.value } })),
      displayData.value.routeInteractionEnabled && interactionMode.value === 'route' && h('div', { class: 'field-group' }, [
        h('div', { class: 'field-head' }, [h('label', '传播路径'), h('span', `${routeOptions.value.length} 条`)]),
        h('select', { value: selectedRouteId.value, class: 'field-input', onChange: e => { selectedRouteId.value = e.target.value } }, routeOptions.value.map(route => h('option', { value: route.id, key: route.id }, `${route.name} · ${route.eventCount} 节点`))),
        routeError.value && h('p', { class: 'text-2xs text-carmine mt-2 leading-[1.5]' }, routeError.value),
      ]),
      (displayData.value.modules?.spatialNodes !== false || displayData.value.routeInteractionEnabled) && h('div', { class: 'field-group' }, [
        h('label', { class: 'check-row' }, [
          h('input', { type: 'checkbox', checked: showTimeline.value, onChange: e => { showTimeline.value = e.target.checked } }),
          h('span', '显示时间线/节点说明'),
        ]),
      ]),
    ])
  },
})

function propertyPanel(type, element) {
  return h('section', { class: 'field-group property-panel' }, [
    h('div', { class: 'field-head' }, [h('label', '元素属性'), h('span', element.type)]),
    gridInputs([
      numberInput('X', element.x, value => store.updateElement(type, element.id, { x: value })),
      numberInput('Y', element.y, value => store.updateElement(type, element.id, { y: value })),
      numberInput('W', element.w, value => store.updateElement(type, element.id, { w: Math.max(12, value) })),
      numberInput('H', element.h, value => store.updateElement(type, element.id, { h: Math.max(12, value) })),
    ]),
    element.type === 'text' && [
      labelled('内容', h('textarea', { value: element.content, rows: 4, class: 'field-textarea', onInput: e => store.updateElement(type, element.id, { content: e.target.value }) })),
      gridInputs([
        numberInput('字号', element.fontSize, value => store.updateElement(type, element.id, { fontSize: value })),
        numberInput('行高', element.lineHeight, value => store.updateElement(type, element.id, { lineHeight: value }), 0.1),
        colorInput('颜色', element.color, value => store.updateElement(type, element.id, { color: value })),
      ]),
      h('div', { class: 'segmented' }, ['left', 'center', 'right'].map(value => h('button', { type: 'button', class: { active: element.textAlign === value }, onClick: () => store.updateElement(type, element.id, { textAlign: value }) }, value))),
      h('div', { class: 'segmented' }, [
        h('button', { type: 'button', class: { active: Number(element.fontWeight) >= 700 }, onClick: () => store.updateElement(type, element.id, { fontWeight: Number(element.fontWeight) >= 700 ? 400 : 700 }) }, '加粗'),
        h('button', { type: 'button', class: { active: element.fontStyle === 'italic' }, onClick: () => store.updateElement(type, element.id, { fontStyle: element.fontStyle === 'italic' ? 'normal' : 'italic' }) }, '斜体'),
      ]),
    ],
    element.type === 'image' && [
      h('button', { type: 'button', class: 'upload-btn', onClick: () => selectElementImage(element.id) }, element.src ? '替换图片' : '上传图片'),
      labelled('填充方式', h('select', { value: element.objectFit, class: 'field-input', onChange: e => store.updateElement(type, element.id, { objectFit: e.target.value }) }, ['cover', 'contain', 'fill'].map(value => h('option', { value }, value)))),
      gridInputs([
        numberInput('焦点 X', element.objectPositionX ?? 50, value => store.updateElement(type, element.id, { objectPositionX: value })),
        numberInput('焦点 Y', element.objectPositionY ?? 50, value => store.updateElement(type, element.id, { objectPositionY: value })),
        numberInput('圆角', element.borderRadius || 0, value => store.updateElement(type, element.id, { borderRadius: value })),
      ]),
    ],
    element.type === 'badge' && [
      labelled('内容', h('input', { value: element.content, class: 'field-input', onInput: e => store.updateElement(type, element.id, { content: e.target.value }) })),
      gridInputs([
        colorInput('文字', element.color, value => store.updateElement(type, element.id, { color: value })),
        colorInput('背景', element.bgColor === 'transparent' ? '#ffffff' : element.bgColor, value => store.updateElement(type, element.id, { bgColor: value })),
      ]),
    ],
    ['divider', 'shape'].includes(element.type) && gridInputs([
      colorInput(element.type === 'shape' ? '填充' : '颜色', element.fill || element.color || '#201b16', value => store.updateElement(type, element.id, element.type === 'shape' ? { fill: value } : { color: value })),
      element.type === 'divider' ? numberInput('粗细', element.thickness || 1, value => store.updateElement(type, element.id, { thickness: value })) : numberInput('圆角', element.borderRadius || 0, value => store.updateElement(type, element.id, { borderRadius: value })),
    ]),
    ['mapBlock', 'evidenceBlock', 'narrativeBlock'].includes(element.type) && h('p', { class: 'property-note' }, '复合块内容来自产品空间数据，可调整位置、尺寸、颜色和层级。'),
    h('div', { class: 'segmented' }, [
      h('button', { type: 'button', onClick: () => store.reorderElement(type, element.id, 'front') }, '置顶'),
      h('button', { type: 'button', onClick: () => store.reorderElement(type, element.id, 'up') }, '上移'),
      h('button', { type: 'button', onClick: () => store.reorderElement(type, element.id, 'down') }, '下移'),
      h('button', { type: 'button', onClick: () => store.reorderElement(type, element.id, 'back') }, '置底'),
    ]),
    h('label', { class: 'check-row' }, [
      h('input', { type: 'checkbox', checked: element.locked, onChange: e => store.updateElement(type, element.id, { locked: e.target.checked }) }),
      h('span', '锁定元素'),
    ]),
    h('label', { class: 'check-row' }, [
      h('input', { type: 'checkbox', checked: element.visible !== false, onChange: e => store.updateElement(type, element.id, { visible: e.target.checked }) }),
      h('span', '显示元素'),
    ]),
    h('button', { type: 'button', class: 'danger-btn', onClick: () => store.removeElements(type, [element.id]) }, '删除元素'),
  ])
}

function fieldGroup(label, count, control, reset) {
  return h('div', { class: 'field-group' }, [
    h('div', { class: 'field-head' }, [h('label', label), count && h('span', count)]),
    control,
    reset && h('button', { type: 'button', class: 'reset-btn', onClick: reset }, '恢复默认'),
  ])
}

function toggleCard(titleText, hint, active, onClick) {
  return h('button', { type: 'button', class: ['theme-option', { active }], onClick }, [
    h('span', [h('strong', titleText), h('small', hint)]),
  ])
}

function elementButton(label, type) {
  return h('button', { type: 'button', onClick: () => store.addElement(activeOutput.value, type) }, label)
}

function layerTitle(element) {
  return element.content || element.subtitle || element.province || element.type
}

function labelled(label, control) {
  return h('label', { class: 'prop-label' }, [h('span', label), control])
}

function gridInputs(items) {
  return h('div', { class: 'prop-grid' }, items)
}

function numberInput(label, value, onValue, step = 1) {
  return labelled(label, h('input', { type: 'number', step, value, class: 'field-input', onInput: e => onValue(Number(e.target.value)) }))
}

function colorInput(label, value, onValue) {
  return labelled(label, h('input', { type: 'color', value: value || '#201b16', class: 'color-input', onInput: e => onValue(e.target.value) }))
}
</script>

<style>
.editor-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.editor-head h2 {
  margin: 2px 0 0;
  color: var(--earth);
  font-family: var(--font-serif);
  font-size: 18px;
}

.editor-head p {
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 10px;
  line-height: 1.5;
}

.segmented {
  display: inline-flex;
  width: 100%;
  gap: 2px;
  padding: 3px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 5px;
  background: rgba(246, 243, 235, 0.76);
  margin-bottom: 12px;
}

.segmented button {
  flex: 1;
  min-height: 28px;
  border: 0;
  border-radius: 3px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
}

.segmented button.active {
  background: rgba(139, 94, 52, 0.12);
  color: var(--earth);
}

.reset-all-btn {
  flex-shrink: 0;
  height: 28px;
  padding: 0 9px;
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.62);
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
}

.reset-all-btn:hover,
.danger-btn:hover {
  border-color: rgba(198, 61, 66, 0.35);
  color: var(--carmine);
}

.field-group {
  border-top: 1px solid var(--glass-border);
  padding: 14px 0;
}

.field-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 7px;
  color: var(--text-muted);
  font-size: 10px;
}

.field-head label {
  color: var(--text-mid);
  font-size: 11px;
  font-weight: 700;
}

.field-input,
.field-textarea {
  width: 100%;
  border: 1px solid var(--glass-border);
  background: rgba(255, 252, 247, 0.8);
  color: var(--text);
  border-radius: 4px;
  outline: none;
  font-size: 13px;
  line-height: 1.5;
  padding: 8px 10px;
  transition: border-color 180ms ease, box-shadow 180ms ease;
}

.field-input:focus,
.field-textarea:focus {
  border-color: rgba(139, 94, 52, 0.55);
  box-shadow: 0 0 0 2px rgba(139, 94, 52, 0.08);
}

.field-textarea {
  resize: vertical;
}

.reset-btn {
  margin-top: 7px;
  color: var(--text-muted);
  font-size: 10px;
  text-decoration: underline;
  cursor: pointer;
  background: transparent;
  border: 0;
}

.theme-grid {
  display: grid;
  gap: 8px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  padding: 9px;
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.62);
  color: var(--text-mid);
  cursor: pointer;
  text-align: left;
  transition: border-color 180ms ease, background 180ms ease;
}

.theme-option.active,
.theme-option:hover {
  border-color: rgba(139, 94, 52, 0.55);
  background: rgba(139, 94, 52, 0.08);
}

.theme-swatch {
  width: 26px;
  height: 26px;
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.theme-option strong {
  display: block;
  color: var(--text);
  font-size: 12px;
}

.theme-option small {
  display: block;
  margin-top: 2px;
  color: var(--text-muted);
  font-size: 10px;
}

.upload-btn,
.copy-btn,
.danger-btn {
  width: 100%;
  min-height: 34px;
  border: 1px solid rgba(139, 94, 52, 0.28);
  border-radius: 4px;
  background: rgba(139, 94, 52, 0.07);
  color: var(--earth);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: background 180ms ease;
}

.copy-btn {
  border-color: var(--glass-border);
  background: rgba(255, 252, 247, 0.66);
  color: var(--text-mid);
}

.danger-btn {
  margin-top: 10px;
  border-color: rgba(198, 61, 66, 0.2);
  background: rgba(198, 61, 66, 0.06);
  color: var(--carmine);
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}

.tool-grid button {
  min-height: 32px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.72);
  color: var(--text-mid);
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
}

.tool-grid button:hover {
  border-color: rgba(62, 120, 145, 0.4);
  color: var(--water);
}

.layer-list {
  display: grid;
  max-height: 220px;
  overflow: auto;
  gap: 6px;
}

.layer-row {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  width: 100%;
  min-height: 30px;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.58);
  cursor: pointer;
  text-align: left;
}

.layer-row.active {
  border-color: rgba(62, 120, 145, 0.48);
  background: rgba(62, 120, 145, 0.08);
}

.layer-row span {
  padding-left: 8px;
  color: var(--water);
  font-size: 10px;
  font-weight: 800;
}

.layer-row strong {
  overflow: hidden;
  color: var(--text-mid);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-property {
  margin-top: 12px;
  padding: 12px;
  border: 1px dashed rgba(74, 65, 55, 0.18);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.5);
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.65;
}

.legacy-upgrade {
  display: grid;
  gap: 10px;
  padding: 16px;
  border: 1px dashed rgba(139, 94, 52, 0.28);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(139, 94, 52, 0.08), transparent 58%),
    rgba(255, 252, 247, 0.68);
}

.legacy-upgrade > span {
  color: var(--earth);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.legacy-upgrade h3 {
  margin: 0;
  color: var(--text);
  font-size: 16px;
  font-weight: 850;
}

.legacy-upgrade p {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.65;
}

.prop-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 10px;
}

.prop-label {
  display: grid;
  gap: 5px;
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 700;
}

.color-input {
  width: 100%;
  height: 35px;
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.8);
  cursor: pointer;
}

.property-note {
  margin: 0 0 10px;
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.55;
}

.check-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 28px;
  color: var(--text-mid);
  font-size: 12px;
  cursor: pointer;
}

.hidden {
  display: none;
}
</style>
