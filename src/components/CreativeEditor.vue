<template>
  <section v-if="product" class="creative-editor p-4">
    <div class="mb-4">
      <div class="flex items-start justify-between gap-3">
        <div>
          <span class="text-2xs uppercase tracking-[0.12em] text-text-muted">{{ editorKicker }}</span>
          <h2 class="font-serif text-lg text-earth mt-0.5">{{ editorTitle }}</h2>
          <p class="text-2xs text-text-muted mt-1 leading-[1.5]">{{ product.origin }}</p>
        </div>
        <button type="button" class="reset-all-btn" @click="resetCurrentOutput">
          重置
        </button>
      </div>
    </div>

    <template v-if="activeOutput === 'poster' && posterData">
      <template v-if="posterData.modules?.brandCopy !== false">
      <div class="field-group">
        <div class="field-head"><label>品牌标题</label><span>{{ title.length }}/32</span></div>
        <input v-model="title" maxlength="32" class="field-input" />
        <button type="button" class="reset-btn" @click="store.resetPosterField('title')">恢复默认</button>
      </div>

      <div class="field-group">
        <div class="field-head"><label>产品描述</label><span>{{ subtitle.length }}/{{ limits.subtitle }}</span></div>
        <input v-model="subtitle" :maxlength="limits.subtitle" class="field-input" />
        <button type="button" class="reset-btn" @click="store.resetPosterField('subtitle')">恢复默认</button>
      </div>

      <div class="field-group">
        <div class="field-head"><label>诗意短句</label><span>{{ poeticLine.length }}/{{ limits.poeticLine }}</span></div>
        <input v-model="poeticLine" :maxlength="limits.poeticLine" class="field-input" />
        <button type="button" class="reset-btn" @click="store.resetPosterField('poeticLine')">恢复默认</button>
      </div>

      <div class="field-group">
        <div class="field-head"><label>品牌叙事</label><span>{{ narrative.length }}/{{ limits.narrative }}</span></div>
        <textarea v-model="narrative" :maxlength="limits.narrative" rows="6" class="field-textarea" />
        <button type="button" class="reset-btn" @click="store.resetPosterField('narrative')">恢复默认</button>
      </div>
      </template>

      <div class="field-group">
        <div class="field-head"><label>视觉主题</label><span>{{ themeLabel }}</span></div>
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
      </div>

      <div v-if="posterData.modules?.mainImage !== false" class="field-group">
        <div class="field-head"><label>主图资产</label><span>{{ hasCustomImage ? '自定义' : '默认' }}</span></div>
        <button type="button" class="upload-btn" @click="fileInput?.click()">{{ hasCustomImage ? '更换图片' : '上传图片' }}</button>
        <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onImageUpload" />
        <div class="mt-3">
          <div class="field-head mb-1"><label>垂直焦点</label><span>{{ imagePosY }}%</span></div>
          <input v-model.number="imagePosY" type="range" min="0" max="100" class="w-full cursor-pointer" />
        </div>
        <button v-if="hasCustomImage" type="button" class="reset-btn" @click="store.resetPosterField('customImageDataUrl')">恢复默认图</button>
      </div>
    </template>

    <template v-else-if="activeOutput === 'archive' && archiveData">
      <div class="field-group">
        <div class="field-head"><label>报告标题</label><span>{{ archiveTitle.length }}/42</span></div>
        <input v-model="archiveTitle" maxlength="42" class="field-input" />
      </div>
      <div class="field-group">
        <div class="field-head"><label>证明摘要</label><span>{{ archiveSummary.length }}/180</span></div>
        <textarea v-model="archiveSummary" maxlength="180" rows="5" class="field-textarea" />
      </div>
      <div v-if="archiveData.modules?.conclusion !== false" class="field-group">
        <div class="field-head"><label>结论说明</label><span>{{ archiveConclusion.length }}/160</span></div>
        <textarea v-model="archiveConclusion" maxlength="160" rows="4" class="field-textarea" />
      </div>
      <div v-if="archiveData.modules?.evidenceMetrics !== false" class="field-group">
        <div class="field-head"><label>指标显隐</label><span>{{ visibleEvidence.length }}/{{ archiveData.allEvidence.length }}</span></div>
        <label v-for="item in archiveData.allEvidence" :key="item.label" class="check-row">
          <input type="checkbox" :checked="visibleEvidence.includes(item.label)" @change="toggleEvidence(item.label)" />
          <span>{{ item.label }}</span>
        </label>
      </div>
    </template>

    <template v-else-if="activeOutput === 'display' && displayData">
      <div v-if="displayData.routeInteractionEnabled" class="field-group">
        <div class="field-head"><label>大屏交互</label><span>{{ displayData.interactionMode === 'route' ? '传播路径' : '产品节点' }}</span></div>
        <div class="theme-grid">
          <button class="theme-option" :class="{ active: interactionMode === 'product' }" type="button" @click="interactionMode = 'product'">
            <span><strong>产品空间节点</strong><small>展示产地、供应链节点和证据指标</small></span>
          </button>
          <button class="theme-option" :class="{ active: interactionMode === 'route' }" type="button" @click="interactionMode = 'route'">
            <span><strong>传播路径</strong><small>新增交互：选择一条食材传播路径</small></span>
          </button>
        </div>
      </div>

      <div v-if="displayData.modules?.productInfo !== false" class="field-group">
        <div class="field-head"><label>大屏标题</label><span>{{ displayTitle.length }}/36</span></div>
        <input v-model="displayTitle" maxlength="36" class="field-input" />
      </div>
      <div v-if="displayData.modules?.productInfo !== false" class="field-group">
        <div class="field-head"><label>副标题</label><span>{{ displaySubtitle.length }}/48</span></div>
        <input v-model="displaySubtitle" maxlength="48" class="field-input" />
      </div>
      <div v-if="displayData.modules?.productInfo !== false" class="field-group">
        <div class="field-head"><label>展示说明</label><span>{{ displayCaption.length }}/160</span></div>
        <textarea v-model="displayCaption" maxlength="160" rows="4" class="field-textarea" />
      </div>
      <div class="field-group" v-if="displayData.routeInteractionEnabled && interactionMode === 'route'">
        <div class="field-head"><label>传播路径</label><span>{{ routeOptions.length }} 条</span></div>
        <select v-model="selectedRouteId" class="field-input">
          <option v-for="route in routeOptions" :key="route.id" :value="route.id">
            {{ route.name }} · {{ route.eventCount }} 节点
          </option>
        </select>
        <p v-if="routeError" class="text-2xs text-carmine mt-2 leading-[1.5]">{{ routeError }}</p>
      </div>
      <div v-if="displayData.modules?.spatialNodes !== false || displayData.routeInteractionEnabled" class="field-group">
        <label class="check-row">
          <input v-model="showTimeline" type="checkbox" />
          <span>显示时间线/节点说明</span>
        </label>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useSpreadRoutes } from '../composables/useSpreadRoutes'
import { useStudioStore } from '../stores/studio'

const store = useStudioStore()
const fileInput = ref(null)
const { routeOptions, error: routeError, loadRoutes } = useSpreadRoutes()

const product = computed(() => store.activeProductCase)
const activeOutput = computed(() => store.activeOutput)
const posterData = computed(() => store.mergedPosterData)
const archiveData = computed(() => store.mergedArchiveData)
const displayData = computed(() => store.mergedDisplayData)

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
  { id: 'heritage', name: '东方米', hint: '风物、地理标志、礼盒感', swatch: 'linear-gradient(135deg, #f6f3eb 0%, #a1352a 100%)' },
  { id: 'indigo', name: '蓝印花', hint: '非遗、展陈、强识别', swatch: 'linear-gradient(135deg, #10223d 0%, #a6c6d9 100%)' },
]

const themeLabel = computed(() => themes.find(t => t.id === theme.value)?.name || '自然绿')

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

.reset-all-btn:hover {
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

.reset-btn:hover {
  color: var(--earth);
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

.theme-option.active {
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

.upload-btn {
  width: 100%;
  height: 34px;
  border: 1px solid rgba(139, 94, 52, 0.28);
  border-radius: 4px;
  background: rgba(139, 94, 52, 0.07);
  color: var(--earth);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: background 180ms ease;
}

.upload-btn:hover {
  background: rgba(139, 94, 52, 0.12);
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
