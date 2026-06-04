<template>
  <section v-if="activeProject" class="output-center p-4">
    <div class="mb-4">
      <span class="text-2xs uppercase tracking-[0.12em] text-text-muted">Production</span>
      <h2 class="font-serif text-lg text-earth mt-0.5">产出中心</h2>
      <p class="text-2xs text-text-muted mt-1 leading-[1.5]">管理当前{{ activeLabel }}项目的导出、复制与交接。</p>
    </div>

    <div v-if="!activeOutput" class="output-block">
      <h3 class="text-sm text-text font-bold mb-2">等待项目类型</h3>
      <p class="text-2xs text-text-muted leading-[1.6]">
        创建项目后，这里会显示导出和交接操作。
      </p>
    </div>

    <div v-else class="output-block">
      <div class="flex items-center justify-between gap-2 mb-3">
        <div>
          <h3 class="text-sm text-text font-bold">{{ isDisplayOutput ? `${activeLabel}完整预览` : `${activeLabel} PNG` }}</h3>
          <p class="text-2xs text-text-muted mt-0.5">{{ isDisplayOutput ? brandPreviewUrl : filename }}</p>
        </div>
        <span class="status-pill">{{ activeStatusLabel }}</span>
      </div>

      <label v-if="!isDisplayOutput" class="text-2xs text-text-muted block mb-1">导出倍率</label>
      <select v-if="!isDisplayOutput" v-model.number="localScale" class="select-input">
        <option :value="2">2x · 快速预览</option>
        <option :value="3">3x · 高清交付</option>
      </select>

      <button
        v-if="!isDisplayOutput"
        type="button"
        class="export-btn"
        :disabled="isExporting || !activeContentConfirmed"
        @click="$emit('export-current', localScale)"
      >
        {{ exportButtonLabel }}
      </button>
      <button
        v-else
        type="button"
        class="export-btn"
        :disabled="!activeContentConfirmed"
        @click="openBrandPreview"
      >
        {{ activeContentConfirmed ? '打开完整预览页面' : '内容模块未确认' }}
      </button>
      <p v-if="isDisplayOutput" class="text-2xs text-text-muted mt-2 leading-[1.5]">
        智慧大屏是动态演示，不生成 PNG；完整预览挂载在 /brand。
      </p>
      <p v-if="!activeContentConfirmed" class="text-2xs text-text-muted mt-2 leading-[1.5]">先确认内容模块后才能生成交付动作。</p>
      <p v-if="exportError" class="text-2xs text-carmine mt-2 leading-[1.5]">{{ exportError }}</p>
    </div>

    <div v-if="activeOutput" class="output-block">
      <h3 class="text-sm text-text font-bold mb-3">{{ copyTitle }}</h3>
      <template v-if="activeOutput === 'poster'">
        <button type="button" class="copy-btn" :disabled="!activeContentConfirmed" @click="copyText('xiaohongshu')">复制小红书文案</button>
        <button type="button" class="copy-btn mt-2" :disabled="!activeContentConfirmed" @click="copyText('ecommerce')">复制电商文案</button>
        <button type="button" class="copy-btn mt-2" :disabled="!activeContentConfirmed" @click="copyText('brief')">复制海报 Brief</button>
      </template>
      <template v-else-if="activeOutput === 'archive'">
        <button type="button" class="copy-btn" :disabled="!activeContentConfirmed" @click="copyText('archive')">复制白皮书摘要</button>
      </template>
      <template v-else>
        <button type="button" class="copy-btn" :disabled="!activeContentConfirmed" @click="copyText('display')">复制大屏配置 JSON</button>
      </template>
      <p v-if="!activeContentConfirmed" class="text-2xs text-text-muted mt-2 leading-[1.5]">先完成内容选择，复制内容会按已选模块生成。</p>
      <p v-if="copyStatus" class="text-2xs text-leaf mt-2">{{ copyStatus }}</p>
    </div>

    <div class="output-block">
      <h3 class="text-sm text-text font-bold mb-3">项目交接</h3>
      <button type="button" class="copy-btn" @click="downloadProjectJson">下载项目 JSON</button>
      <p class="text-2xs text-text-muted mt-2 leading-[1.5]">
        JSON 包含项目类型、编辑覆盖值、产品空间底板和合并后的交付数据。
      </p>
    </div>

    <div class="output-block">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm text-text font-bold">最近导出</h3>
        <span class="text-2xs text-text-muted">{{ activeProject.exports.length }} 条</span>
      </div>
      <div v-if="!activeProject.exports.length" class="empty-history">导出后会在这里记录文件名和时间</div>
      <ul v-else class="space-y-2">
        <li v-for="item in activeProject.exports.slice(0, 7)" :key="item.id" class="history-row">
          <span class="type-badge">{{ labelOf(item.type) }}</span>
          <span class="truncate">{{ item.filename }}</span>
          <time>{{ formatTime(item.createdAt) }}</time>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStudioStore } from '../stores/studio'

const props = defineProps({
  isExporting: { type: Boolean, default: false },
  exportError: { type: String, default: '' },
  exportScale: { type: Number, default: 3 },
})

defineEmits(['export-current'])

const store = useStudioStore()
const router = useRouter()
const localScale = ref(props.exportScale)
const copyStatus = ref('')

const activeProject = computed(() => store.activeProject)
const activeOutput = computed(() => store.activeOutput)
const activeContentConfirmed = computed(() => store.activeContentConfirmed)
const posterData = computed(() => store.mergedPosterData)
const archiveData = computed(() => store.mergedArchiveData)
const displayData = computed(() => store.mergedDisplayData)

const labels = {
  poster: '海报',
  archive: '白皮书',
  display: '大屏',
}

const statusLabels = {
  draft: '待完善',
  edited: '已编辑',
  exported: '已导出',
}

const currentData = computed(() => ({
  poster: posterData.value,
  archive: archiveData.value,
  display: displayData.value,
}[activeOutput.value]))

const activeLabel = computed(() => labels[activeOutput.value] || '产出')
const isDisplayOutput = computed(() => activeOutput.value === 'display')
const activeStatusLabel = computed(() =>
  statusLabels[store.outputStatuses.find(item => item.type === activeOutput.value)?.status || 'draft']
)

const filename = computed(() => {
  const title = currentData.value?.title || activeLabel.value
  const suffix = activeOutput.value === 'poster'
    ? currentData.value?.theme || 'nature'
    : activeOutput.value === 'display'
      ? currentData.value?.interactionMode || 'product'
      : 'archive'
  return `${title}-${activeLabel.value}-${suffix}.png`.replace(/[\\/:*?"<>|]/g, '-')
})

const copyTitle = computed(() => {
  if (activeOutput.value === 'poster') return '营销文案'
  if (activeOutput.value === 'archive') return '白皮书摘要'
  return '大屏配置'
})

const brandPreviewUrl = computed(() =>
  activeProject.value ? `/brand?project=${encodeURIComponent(activeProject.value.id)}` : '/brand'
)

const exportButtonLabel = computed(() => {
  if (props.isExporting) return '正在生成 PNG...'
  if (!activeContentConfirmed.value) return '内容模块未确认'
  return `导出当前${activeLabel.value} PNG`
})

watch(() => props.exportScale, value => {
  localScale.value = value
})

async function copyText(type) {
  if (!activeContentConfirmed.value) return
  const text = copyPayload(type)
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    const area = document.createElement('textarea')
    area.value = text
    document.body.appendChild(area)
    area.select()
    document.execCommand('copy')
    document.body.removeChild(area)
  }
  copyStatus.value = copyLabel(type)
  window.setTimeout(() => { copyStatus.value = '' }, 1800)
}

function copyPayload(type) {
  if (type === 'xiaohongshu' || type === 'ecommerce') return posterData.value?.copy?.[type] || ''
  if (type === 'brief') return posterBrief.value
  if (type === 'archive') return archiveBrief.value
  if (type === 'display') return JSON.stringify(displayData.value, null, 2)
  return ''
}

const posterBrief = computed(() => {
  if (!posterData.value || !activeProject.value) return ''
  return [
    `项目：${activeProject.value.name}`,
    `产品：${posterData.value.productName}`,
    `标题：${posterData.value.title}`,
    `描述：${posterData.value.subtitle}`,
    `短句：${posterData.value.poeticLine}`,
    `主题：${posterData.value.theme}`,
    `产地：${posterData.value.province} · ${posterData.value.origin}`,
    `叙事：${String(posterData.value.narrative).replace(/<[^>]+>/g, '')}`,
  ].join('\n')
})

const archiveBrief = computed(() => {
  if (!archiveData.value) return ''
  return [
    `标题：${archiveData.value.title}`,
    `产品：${archiveData.value.productName}`,
    `摘要：${archiveData.value.summary}`,
    `证据：${archiveData.value.evidence.map(item => `${item.label} ${item.value}`).join('；')}`,
    `结论：${archiveData.value.conclusion}`,
  ].join('\n')
})

function copyLabel(type) {
  if (type === 'xiaohongshu') return '已复制小红书文案'
  if (type === 'ecommerce') return '已复制电商文案'
  if (type === 'archive') return '已复制白皮书摘要'
  if (type === 'display') return '已复制大屏配置'
  return '已复制海报 Brief'
}

function openBrandPreview() {
  if (!activeContentConfirmed.value) return
  router.push(brandPreviewUrl.value)
}

function downloadProjectJson() {
  const snapshot = store.projectSnapshot()
  if (!snapshot) return
  const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const title = currentData.value?.title || activeProject.value?.name || 'studio-project'
  link.download = `${title}-studio-project.json`.replace(/[\\/:*?"<>|]/g, '-')
  link.href = url
  link.click()
  URL.revokeObjectURL(url)
}

function labelOf(type) {
  return labels[type] || '产出'
}

function formatTime(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.output-block {
  border-top: 1px solid var(--glass-border);
  padding: 14px 0;
}

.status-pill,
.type-badge {
  flex-shrink: 0;
  border-radius: 3px;
  background: rgba(94, 123, 80, 0.14);
  color: var(--leaf);
  font-size: 10px;
  font-weight: 700;
  padding: 3px 7px;
}

.type-badge {
  background: rgba(139, 94, 52, 0.1);
  color: var(--earth);
}

.select-input {
  width: 100%;
  height: 34px;
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.8);
  color: var(--text);
  font-size: 12px;
  padding: 0 9px;
  outline: none;
}

.export-btn,
.copy-btn {
  width: 100%;
  min-height: 36px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 180ms ease, border-color 180ms ease, opacity 180ms ease;
}

.export-btn {
  margin-top: 12px;
  border: 1px solid #201b16;
  background: #201b16;
  color: #fffaf3;
  font-size: 13px;
  font-weight: 800;
}

.export-btn:disabled {
  opacity: 0.55;
  cursor: wait;
}

.copy-btn {
  border: 1px solid var(--glass-border);
  background: rgba(255, 252, 247, 0.66);
  color: var(--text-mid);
  font-size: 12px;
  font-weight: 700;
}

.copy-btn:hover {
  border-color: rgba(139, 94, 52, 0.38);
  color: var(--earth);
}

.copy-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-history {
  border: 1px dashed var(--glass-border);
  border-radius: 4px;
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.5;
  padding: 12px;
  text-align: center;
}

.history-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
  color: var(--text-mid);
  font-size: 11px;
}

.history-row time {
  color: var(--text-muted);
  font-size: 10px;
}
</style>
