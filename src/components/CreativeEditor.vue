<template>
  <section v-if="product" class="creative-editor">
    <header class="editor-head">
      <div>
        <span>{{ editorKicker }}</span>
        <h2>{{ editorTitle }}</h2>
        <p>{{ product.origin }}</p>
      </div>
      <button type="button" class="reset-all-btn" @click="resetCurrentOutput">重置</button>
    </header>

    <AiStudioAssistant v-if="currentOutputData" />

    <template v-if="activeOutput === 'poster' && posterData">
      <template v-if="posterData.modules?.brandCopy !== false">
        <FieldGroup label="品牌标题" :count="`${title.length}/32`">
          <input v-model="title" maxlength="32" class="field-input" />
          <button type="button" class="reset-btn" @click="store.resetPosterField('title')">恢复默认</button>
        </FieldGroup>

        <FieldGroup label="产品描述" :count="`${subtitle.length}/${limits.subtitle}`">
          <input v-model="subtitle" :maxlength="limits.subtitle" class="field-input" />
          <button type="button" class="reset-btn" @click="store.resetPosterField('subtitle')">恢复默认</button>
        </FieldGroup>

        <FieldGroup label="诗意短句" :count="`${poeticLine.length}/${limits.poeticLine}`">
          <input v-model="poeticLine" :maxlength="limits.poeticLine" class="field-input" />
          <button type="button" class="reset-btn" @click="store.resetPosterField('poeticLine')">恢复默认</button>
        </FieldGroup>

        <FieldGroup label="品牌叙事" :count="`${narrative.length}/${limits.narrative}`">
          <textarea v-model="narrative" :maxlength="limits.narrative" rows="6" class="field-textarea" />
          <button type="button" class="reset-btn" @click="store.resetPosterField('narrative')">恢复默认</button>
        </FieldGroup>
      </template>

      <FieldGroup label="视觉主题" :count="themeLabel">
        <div class="theme-grid">
          <button
            v-for="item in themes"
            :key="item.id"
            type="button"
            class="theme-option"
            :class="{ active: theme === item.id }"
            @click="theme = item.id"
          >
            <span class="theme-swatch" :style="{ background: item.swatch }" />
            <span><strong>{{ item.name }}</strong><small>{{ item.hint }}</small></span>
          </button>
        </div>
      </FieldGroup>

      <FieldGroup label="模板参数" :count="templateParamSummary">
        <div class="param-grid">
          <label class="mini-field">
            <span>布局</span>
            <select :value="templateParams.layout" @change="updateTemplateParam('layout', $event.target.value)">
              <option value="balanced">均衡</option>
              <option value="editorial">杂志</option>
              <option value="evidence">证据</option>
            </select>
          </label>
          <label class="mini-field">
            <span>色板</span>
            <select :value="templateParams.palette" @change="updateTemplateParam('palette', $event.target.value)">
              <option value="default">默认</option>
              <option value="fresh">清新</option>
              <option value="warm">暖调</option>
              <option value="noir">深色</option>
            </select>
          </label>
          <label class="mini-field">
            <span>密度</span>
            <select :value="templateParams.density" @change="updateTemplateParam('density', $event.target.value)">
              <option value="normal">标准</option>
              <option value="compact">紧凑</option>
              <option value="airy">留白</option>
            </select>
          </label>
          <label class="mini-field">
            <span>图片</span>
            <select :value="templateParams.imageShape" @change="updateTemplateParam('imageShape', $event.target.value)">
              <option value="standard">标准</option>
              <option value="arch">拱形</option>
              <option value="full">满版</option>
            </select>
          </label>
          <label class="mini-field">
            <span>指标</span>
            <select :value="templateParams.metricStyle" @change="updateTemplateParam('metricStyle', $event.target.value)">
              <option value="cards">卡片</option>
              <option value="inline">行内</option>
            </select>
          </label>
          <label class="mini-field">
            <span>标题比例 {{ templateParams.titleScale }}%</span>
            <input :value="templateParams.titleScale" type="range" min="82" max="130" @input="updateTemplateParam('titleScale', Number($event.target.value))" />
          </label>
        </div>
        <input
          :value="templateParams.badgeText"
          maxlength="28"
          class="field-input param-badge-input"
          placeholder="角标文案"
          @input="updateTemplateParam('badgeText', $event.target.value)"
        />
      </FieldGroup>

      <FieldGroup v-if="posterData.modules?.mainImage !== false" label="主图资产" :count="hasCustomImage ? '自定义' : '默认'">
        <button type="button" class="upload-btn" @click="fileInput?.click()">{{ hasCustomImage ? '更换图片' : '上传图片' }}</button>
        <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onImageUpload" />
        <div class="range-block">
          <div class="field-head"><label>垂直焦点</label><span>{{ imagePosY }}%</span></div>
          <input v-model.number="imagePosY" type="range" min="0" max="100" />
        </div>
        <button v-if="hasCustomImage" type="button" class="reset-btn" @click="store.resetPosterField('customImageDataUrl')">恢复默认图</button>
      </FieldGroup>
    </template>

    <template v-else-if="activeOutput === 'archive' && archiveData">
      <FieldGroup label="报告标题" :count="`${archiveTitle.length}/42`">
        <input v-model="archiveTitle" maxlength="42" class="field-input" />
      </FieldGroup>
      <FieldGroup label="证明摘要" :count="`${archiveSummary.length}/180`">
        <textarea v-model="archiveSummary" maxlength="180" rows="5" class="field-textarea" />
      </FieldGroup>
      <FieldGroup v-if="archiveData.modules?.conclusion !== false" label="结论说明" :count="`${archiveConclusion.length}/160`">
        <textarea v-model="archiveConclusion" maxlength="160" rows="4" class="field-textarea" />
      </FieldGroup>
      <FieldGroup v-if="archiveData.modules?.evidenceMetrics !== false" label="指标显示" :count="`${visibleEvidence.length}/${archiveData.allEvidence.length}`">
        <label v-for="item in archiveData.allEvidence" :key="item.label" class="check-row">
          <input type="checkbox" :checked="visibleEvidence.includes(item.label)" @change="toggleEvidence(item.label)" />
          <span>{{ item.label }}</span>
        </label>
      </FieldGroup>
    </template>

    <template v-else-if="activeOutput === 'display' && displayData">
      <FieldGroup v-if="displayData.routeInteractionEnabled" label="大屏交互" :count="displayData.interactionMode === 'route' ? '传播路径' : '产品节点'">
        <div class="theme-grid">
          <button class="theme-option" :class="{ active: interactionMode === 'product' }" type="button" @click="interactionMode = 'product'">
            <span><strong>产品空间节点</strong><small>展示产地、供应链节点和证据指标</small></span>
          </button>
          <button class="theme-option" :class="{ active: interactionMode === 'route' }" type="button" @click="interactionMode = 'route'">
            <span><strong>传播路径</strong><small>叠加食材历史流动路线</small></span>
          </button>
        </div>
      </FieldGroup>

      <FieldGroup v-if="displayData.modules?.productInfo !== false" label="大屏标题" :count="`${displayTitle.length}/36`">
        <input v-model="displayTitle" maxlength="36" class="field-input" />
      </FieldGroup>
      <FieldGroup v-if="displayData.modules?.productInfo !== false" label="副标题" :count="`${displaySubtitle.length}/48`">
        <input v-model="displaySubtitle" maxlength="48" class="field-input" />
      </FieldGroup>
      <FieldGroup v-if="displayData.modules?.productInfo !== false" label="展示说明" :count="`${displayCaption.length}/160`">
        <textarea v-model="displayCaption" maxlength="160" rows="4" class="field-textarea" />
      </FieldGroup>
      <FieldGroup v-if="displayData.routeInteractionEnabled && interactionMode === 'route'" label="传播路径" :count="`${routeOptions.length} 条`">
        <select v-model="selectedRouteId" class="field-input">
          <option v-for="route in routeOptions" :key="route.id" :value="route.id">
            {{ route.name }} / {{ route.eventCount }} 节点
          </option>
        </select>
        <p v-if="routeError" class="error-text">{{ routeError }}</p>
      </FieldGroup>
      <FieldGroup v-if="displayData.modules?.spatialNodes !== false || displayData.routeInteractionEnabled" label="时间线" count="显示控制">
        <label class="check-row">
          <input v-model="showTimeline" type="checkbox" />
          <span>显示时间线 / 节点说明</span>
        </label>
      </FieldGroup>
    </template>
  </section>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import AiStudioAssistant from './AiStudioAssistant.vue'
import { useSpreadRoutes } from '../composables/useSpreadRoutes'
import { useStudioStore } from '../stores/studio'

const FieldGroup = defineComponent({
  props: {
    label: { type: String, required: true },
    count: { type: String, default: '' },
  },
  setup(props, { slots }) {
    return () => h('div', { class: 'field-group' }, [
      h('div', { class: 'field-head' }, [
        h('label', props.label),
        h('span', props.count),
      ]),
      slots.default?.(),
    ])
  },
})

const store = useStudioStore()
const fileInput = ref(null)
const { routeOptions, error: routeError, loadRoutes } = useSpreadRoutes()

const product = computed(() => store.activeProductCase)
const activeOutput = computed(() => store.activeOutput)
const posterData = computed(() => store.mergedPosterData)
const archiveData = computed(() => store.mergedArchiveData)
const displayData = computed(() => store.mergedDisplayData)
const currentOutputData = computed(() => ({
  poster: posterData.value,
  archive: archiveData.value,
  display: displayData.value,
}[activeOutput.value]))

onMounted(loadRoutes)

const editorKicker = computed(() => ({ poster: 'Poster Editor', archive: 'Archive Editor', display: 'Display Editor' }[activeOutput.value]))
const editorTitle = computed(() => ({ poster: '海报编辑', archive: '白皮书编辑', display: '大屏编辑' }[activeOutput.value]))

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
const theme = field('poster', 'theme', 'nature')
const imagePosY = computed({
  get: () => posterData.value?.imagePosY ?? 50,
  set: value => store.updateOutputField('poster', 'imagePosY', Number(value)),
})
const templateParams = computed(() => posterData.value?.templateParams || {})

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

const hasCustomImage = computed(() => Boolean(store.activeProject?.outputs?.poster?.customImageDataUrl))

const themes = [
  { id: 'nature', name: '自然绿', hint: '留白、干净、供应链可信', swatch: 'linear-gradient(135deg, #ffffff 0%, #2a4128 100%)' },
  { id: 'heritage', name: '东方红', hint: '风物、地理标志、礼盒感', swatch: 'linear-gradient(135deg, #f6f3eb 0%, #a1352a 100%)' },
  { id: 'indigo', name: '蓝印花', hint: '非遗、展陈、强识别', swatch: 'linear-gradient(135deg, #10223d 0%, #a6c6d9 100%)' },
]

const themeLabel = computed(() => themes.find(item => item.id === theme.value)?.name || '自然绿')
const templateParamSummary = computed(() => {
  const layout = { balanced: '均衡', editorial: '杂志', evidence: '证据' }[templateParams.value.layout] || '均衡'
  const palette = { default: '默认', fresh: '清新', warm: '暖调', noir: '深色' }[templateParams.value.palette] || '默认'
  return `${layout} / ${palette}`
})

function updateTemplateParam(key, value) {
  const current = store.activeProject?.outputs?.poster?.templateParams || {}
  store.updateOutputField('poster', 'templateParams', {
    ...current,
    [key]: value,
  })
}

function toggleEvidence(label) {
  const next = new Set(visibleEvidence.value)
  if (next.has(label)) next.delete(label)
  else next.add(label)
  store.updateOutputField('archive', 'visibleEvidence', [...next])
}

function onImageUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = e => {
    store.updateOutputField('poster', 'customImageDataUrl', e.target?.result || null)
    store.updateOutputField('poster', 'imagePosY', 50)
  }
  reader.readAsDataURL(file)
  event.target.value = ''
}

function resetCurrentOutput() {
  if (window.confirm('确认将当前产出恢复为默认内容？')) {
    store.resetOutput(activeOutput.value)
  }
}
</script>

<style scoped>
.creative-editor {
  padding: 14px;
}

.editor-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.editor-head span {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 850;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.editor-head h2 {
  margin: 3px 0 0;
  color: var(--earth);
  font-family: var(--font-serif);
  font-size: 18px;
}

.editor-head p {
  margin: 3px 0 0;
  color: var(--text-muted);
  font-size: 11px;
}

.reset-all-btn,
.reset-btn,
.upload-btn {
  cursor: pointer;
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
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.8);
  color: var(--text);
  font: inherit;
  font-size: 13px;
  line-height: 1.5;
  outline: none;
  padding: 8px 10px;
}

.field-textarea {
  resize: vertical;
}

.reset-btn {
  margin-top: 7px;
  border: 0;
  background: transparent;
  color: var(--text-muted);
  font-size: 10px;
  text-decoration: underline;
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
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.62);
  color: var(--text-mid);
  cursor: pointer;
  padding: 9px;
  text-align: left;
}

.theme-option.active {
  border-color: rgba(139, 94, 52, 0.55);
  background: rgba(139, 94, 52, 0.08);
}

.theme-swatch {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 4px;
}

.theme-option strong,
.theme-option small {
  display: block;
}

.theme-option strong {
  color: var(--text);
  font-size: 12px;
}

.theme-option small {
  margin-top: 2px;
  color: var(--text-muted);
  font-size: 10px;
}

.param-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.mini-field {
  display: grid;
  gap: 5px;
  min-width: 0;
}

.mini-field span {
  overflow: hidden;
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-field select {
  width: 100%;
  height: 30px;
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.82);
  color: var(--text-mid);
  font-size: 12px;
  outline: none;
  padding: 0 8px;
}

.mini-field input[type="range"] {
  width: 100%;
  cursor: pointer;
}

.param-badge-input {
  margin-top: 8px;
}

.upload-btn {
  width: 100%;
  height: 34px;
  border: 1px solid rgba(139, 94, 52, 0.28);
  border-radius: 4px;
  background: rgba(139, 94, 52, 0.07);
  color: var(--earth);
  font-size: 12px;
  font-weight: 700;
}

.range-block {
  margin-top: 12px;
}

.range-block input {
  width: 100%;
  cursor: pointer;
}

.check-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 28px;
  color: var(--text-mid);
  cursor: pointer;
  font-size: 12px;
}

.hidden {
  display: none;
}

.error-text {
  margin: 8px 0 0;
  color: var(--carmine);
  font-size: 11px;
  line-height: 1.5;
}
</style>
