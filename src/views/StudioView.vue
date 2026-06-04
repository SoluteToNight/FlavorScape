<template>
  <main class="studio-shell fixed top-navbar inset-x-0 bottom-0 bg-bg">
    <section v-if="showCreationFlow" class="creation-shell">
      <header class="creation-header">
        <div>
          <span class="ui-kicker">Xunwei Studio</span>
          <h1>创建可视化产品项目</h1>
          <p>{{ creationLead }}</p>
        </div>
        <button
          v-if="activeProject && !isImporting"
          type="button"
          class="secondary-btn"
          @click="cancelCreator"
        >
          返回当前项目
        </button>
      </header>

      <ImportFlow
        v-if="isImporting && importingProduct"
        class="creation-import"
        :product-name="importingProduct.name"
        :province="importingProduct.province"
        :node-count="importingProduct.marketing?.spatial?.nodes?.length || 0"
        @complete="completeImport"
      />

      <section v-else-if="!pendingOutputType" class="launchpad">
        <div class="launchpad-grid">
          <button
            v-for="item in outputOptions"
            :key="item.type"
            type="button"
            class="launch-card"
            @click="selectOutputIntent(item.type)"
          >
            <span>{{ item.kicker }}</span>
            <strong>{{ item.label }}项目</strong>
            <small>{{ item.description }}</small>
            <em>{{ item.flow }}</em>
          </button>
        </div>

        <div v-if="store.projectList.length" class="recent-projects">
          <div class="recent-head">
            <span class="ui-kicker">Recent Projects</span>
            <strong>继续编辑</strong>
          </div>
          <button
            v-for="project in store.projectList.slice(0, 4)"
            :key="project.id"
            type="button"
            class="recent-row"
            @click="openExistingProject(project.id)"
          >
            <span>{{ outputLabel(project.outputType) }}</span>
            <strong>{{ project.name }}</strong>
            <small>{{ project.productName }}</small>
          </button>
        </div>
      </section>

      <section v-else class="product-step">
        <div class="step-bar">
          <div>
            <span class="ui-kicker">Step 2 / Product Source</span>
            <h2>选择{{ selectedOutputOption?.label }}项目的产品</h2>
          </div>
          <button type="button" class="secondary-btn" @click="pendingOutputType = null">
            重选项目类型
          </button>
        </div>
        <div class="product-gallery">
          <section class="library-gallery">
            <div class="gallery-head">
              <div>
                <span class="ui-kicker">Product Library</span>
                <strong>从产品库选择</strong>
              </div>
              <small>{{ productCases.length }} 个案例</small>
            </div>
            <div class="product-grid">
              <button
                v-for="pc in productCases"
                :key="pc.id"
                type="button"
                class="product-card"
                @click="startImport(pc.id)"
              >
                <img :src="pc.heroImage" :alt="pc.name" />
                <span :style="{ backgroundColor: pc.colors?.primary || '#8B5E34' }" />
                <div>
                  <strong>{{ pc.studio?.brandName || pc.name }}</strong>
                  <small>{{ pc.category }} / {{ pc.province }}</small>
                  <p>{{ pc.origin }}</p>
                </div>
              </button>
            </div>
          </section>

          <aside class="custom-import-panel" aria-label="用户自定义导入">
            <span class="ui-kicker">Custom Import</span>
            <strong>用户自定义导入</strong>
            <p>导入产品资料、主图和空间节点数据，生成可编辑项目。当前仅展示入口，功能暂未启用。</p>
            <div class="import-dropzone">
              <span>JSON / CSV / 图片资产</span>
              <small>拖放或选择文件</small>
            </div>
            <button type="button" class="disabled-import-btn" disabled>导入功能待接入</button>
          </aside>
        </div>
      </section>
    </section>

    <div v-else class="studio-grid">
      <aside class="studio-panel studio-left border-r border-glass-border">
          <div class="panel-chrome tool-chrome">
            <div>
              <span>Workbench</span>
              <strong>{{ activeOutputLabel }}项目</strong>
            </div>
            <div class="side-tabs" aria-label="工作面板">
              <button
                type="button"
                :class="{ active: activeSideTab === 'directory' }"
                @click="activeSideTab = 'directory'"
              >
                目录
              </button>
              <button
                type="button"
                :class="{ active: activeSideTab === 'edit' }"
                @click="activeSideTab = 'edit'"
              >
                编辑
              </button>
            </div>
          </div>

          <div class="panel-scroll">
            <template v-if="activeSideTab === 'directory'">
              <ProjectManager @new-project="openProductPicker" />
              <div class="studio-empty-note">
                项目类型已锁定为{{ activeOutputLabel }}。如需创建其他形式，请新建项目。
              </div>
            </template>

            <template v-else>
              <div class="inspector-summary">
                <span>{{ activeProductName }}</span>
                <strong>{{ activeProject?.name }}</strong>
                <small>{{ activeContentConfirmed ? '正在编辑交付物' : '等待模块确认' }}</small>
              </div>
              <CreativeEditor v-if="activeContentConfirmed" />
              <div v-else class="studio-empty-note">
                确认内容模块后，这里会出现{{ activeOutputLabel }}的文案、视觉风格和交互设置。
              </div>
            </template>
          </div>
      </aside>

      <section class="studio-stage">
        <header class="canvas-topbar">
          <div class="canvas-title">
            <span>{{ activeOutputLabel }}项目 / {{ activeProductName }}</span>
            <h1>{{ currentOutputData?.title || activeProject?.name }}</h1>
          </div>
          <div class="canvas-controls">
            <span class="type-pill">{{ activeOutputLabel }}</span>
            <span class="save-indicator">{{ saveStateLabel }}</span>
          </div>
        </header>

        <section v-if="!activeContentConfirmed" class="module-setup">
          <div class="module-head">
            <div>
              <span class="ui-kicker">Step 3 / Content Modules</span>
              <h2>选择{{ activeOutputLabel }}内容模块</h2>
              <p>关闭的模块不会进入预览、交付动作和复制内容。</p>
            </div>
            <span>{{ selectedModuleCount }} / {{ activeOutputModules.length }}</span>
          </div>

          <div class="module-grid">
            <label
              v-for="item in activeOutputModules"
              :key="item.key"
              class="module-card"
              :class="{ active: activeOutputModuleState[item.key] }"
            >
              <input
                type="checkbox"
                :checked="activeOutputModuleState[item.key]"
                @change="store.updateContentModule(activeOutput, item.key, $event.target.checked)"
              />
              <span>
                <strong>{{ item.label }}</strong>
                <small>{{ item.description }}</small>
              </span>
            </label>
          </div>

          <div class="module-actions">
            <button
              type="button"
              class="confirm-btn"
              :disabled="selectedModuleCount === 0"
              @click="store.confirmContent(activeOutput)"
            >
              确认模块并进入编辑器
            </button>
          </div>
        </section>

        <div v-else-if="currentOutputData" class="preview-workspace">
          <div class="poster-scroll" :class="{ 'display-scroll': activeOutput === 'display' }">
            <div class="canvas-zoom-control" aria-label="预览缩放">
              <button
                v-for="item in zoomOptions"
                :key="item.value"
                type="button"
                :class="{ active: previewScale === item.value }"
                @click="previewScale = item.value"
              >
                {{ item.label }}
              </button>
            </div>
            <div class="poster-preview-shell" :style="previewFrameStyle">
              <StudioPoster
                v-if="activeOutput === 'poster'"
                :poster-data="posterData"
                :scale="previewScale"
              />
              <StudioArchive
                v-else-if="activeOutput === 'archive'"
                :archive-data="archiveData"
                :scale="previewScale"
              />
              <BrandDisplayExperience
                v-else-if="activeOutput === 'display'"
                :display-data="displayData"
                :route-data="activeRouteData"
                :route-options="routeOptions"
                :scale="previewScale"
                framed
                @select-event="selectDisplayEvent"
                @select-route="selectDisplayRoute"
              />
            </div>
          </div>
        </div>
      </section>

      <aside class="studio-panel studio-right border-l border-glass-border">
        <div class="panel-chrome">
          <div>
            <span>Delivery</span>
            <strong>交付</strong>
          </div>
          <small>{{ activeOutputLabel }}</small>
        </div>
        <div class="panel-scroll">
          <OutputChecklist
            :is-exporting="isExporting"
            :export-error="exportError"
            :export-scale="exportScale"
            @export-current="exportCurrent"
          />
        </div>
      </aside>

    </div>

    <SpatialFooter />

    <div v-if="isExporting" class="export-layer" :style="exportLayerStyle" aria-hidden="true">
      <StudioPoster
        v-if="activeContentConfirmed && activeOutput === 'poster' && posterData"
        ref="exportRef"
        :poster-data="posterData"
        :scale="1"
      />
      <StudioArchive
        v-else-if="activeContentConfirmed && activeOutput === 'archive' && archiveData"
        ref="exportRef"
        :archive-data="archiveData"
        :scale="1"
      />
    </div>
  </main>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import html2canvas from 'html2canvas'
import BrandDisplayExperience from '../components/BrandDisplayExperience.vue'
import CreativeEditor from '../components/CreativeEditor.vue'
import ImportFlow from '../components/ImportFlow.vue'
import OutputChecklist from '../components/OutputChecklist.vue'
import ProjectManager from '../components/ProjectManager.vue'
import SpatialFooter from '../components/SpatialFooter.vue'
import StudioArchive from '../components/StudioArchive.vue'
import StudioPoster from '../components/StudioPoster.vue'
import { useProductCases } from '../composables/useProductCases'
import { useSpreadRoutes } from '../composables/useSpreadRoutes'
import { useStudioStore } from '../stores/studio'

const store = useStudioStore()
const { cases: productCases, getById } = useProductCases()
const { routeOptions, loadRoutes, loadRoute, getRoute } = useSpreadRoutes()

const activeProject = computed(() => store.activeProject)
const activeProductName = computed(() => store.activeProductCase?.name || '未选择产品')
const activeOutput = computed(() => store.activeOutput)
const activeContentConfirmed = computed(() => store.activeContentConfirmed)
const posterData = computed(() => store.mergedPosterData)
const archiveData = computed(() => store.mergedArchiveData)
const displayData = computed(() => store.mergedDisplayData)
const currentOutputData = computed(() => ({
  poster: posterData.value,
  archive: archiveData.value,
  display: displayData.value,
}[activeOutput.value]))
const activeRouteData = computed(() => getRoute(displayData.value?.selectedRouteId))

const isImporting = ref(false)
const importingProduct = ref(null)
const showProductPicker = ref(false)
const pendingOutputType = ref(null)
const isExporting = ref(false)
const exportError = ref('')
const exportScale = ref(3)
const previewScale = ref(0.72)
const exportRef = ref(null)
const activeSideTab = ref('edit')

const outputOptions = [
  {
    type: 'poster',
    label: '海报',
    kicker: 'Poster',
    description: '创建适合品牌传播、活动物料和社媒视觉的静态画面。',
    flow: '选择产品后配置主图、品牌文案、空间地图和证据指标。',
  },
  {
    type: 'archive',
    label: '白皮书',
    kicker: 'Dossier',
    description: '创建适合溯源证明、招商材料和交接文档的报告资产。',
    flow: '选择产品后配置产地信息、空间底板、证据指标和结论说明。',
  },
  {
    type: 'display',
    label: '演示',
    kicker: 'Display',
    description: '创建可在 /brand 打开的动态地图、传播路径和巡航演示。',
    flow: '选择产品后配置大屏信息、空间节点和传播路径交互。',
  },
]

const zoomOptions = [
  { label: 'Fit', value: 0.61 },
  { label: '72%', value: 0.72 },
  { label: '86%', value: 0.86 },
  { label: '100%', value: 1 },
]

const defaultPreviewScales = {
  poster: 0.72,
  archive: 0.61,
  display: 0.61,
}

const outputFrames = {
  poster: { width: 440, height: 860 },
  archive: { width: 760, height: 1040 },
  display: { width: 1280, height: 720 },
}

const showCreationFlow = computed(() =>
  isImporting.value || !activeProject.value || showProductPicker.value || Boolean(pendingOutputType.value)
)
const activeFrame = computed(() => outputFrames[activeOutput.value] || outputFrames.poster)
const activeOutputLabel = computed(() => outputLabel(activeOutput.value))
const selectedOutputOption = computed(() => outputOptions.find(item => item.type === pendingOutputType.value))
const activeOutputModules = computed(() => store.contentModuleDefinitions[activeOutput.value] || [])
const activeOutputModuleState = computed(() => {
  const type = activeOutput.value
  if (!type) return {}
  return store.activeProject?.outputs?.[type]?.contentModules || {}
})
const selectedModuleCount = computed(() =>
  activeOutputModules.value.filter(item => activeOutputModuleState.value[item.key]).length
)

const creationLead = computed(() => {
  if (isImporting.value) return '正在把产品数据整理为项目资产。'
  if (pendingOutputType.value) return `已选择${selectedOutputOption.value?.label || '可视化'}项目，下一步选择具体产品。`
  return '先选择交付物形式，再选择产品、配置模块和视觉风格。'
})

const previewFrameStyle = computed(() => ({
  width: `${activeFrame.value.width * previewScale.value}px`,
  height: `${activeFrame.value.height * previewScale.value}px`,
}))

const exportLayerStyle = computed(() => ({
  width: `${activeFrame.value.width}px`,
  height: `${activeFrame.value.height}px`,
}))

const saveStateLabel = computed(() => {
  if (store.lastError) return `本地保存失败：${store.lastError}`
  const value = activeProject.value?.updatedAt
  if (!value) return '已保存到本地'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '已保存到本地'
  return `已保存 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
})

function outputLabel(type) {
  return outputOptions.find(item => item.type === type)?.label || '产出'
}

function openProductPicker() {
  pendingOutputType.value = null
  showProductPicker.value = true
}

function cancelCreator() {
  pendingOutputType.value = null
  showProductPicker.value = false
}

function selectOutputIntent(type) {
  pendingOutputType.value = type
  showProductPicker.value = true
}

function openExistingProject(id) {
  store.switchProject(id)
  cancelCreator()
}

function startImport(productId) {
  const product = getById(productId)
  if (!product) return
  importingProduct.value = product
  isImporting.value = true
  showProductPicker.value = false
}

function completeImport() {
  if (importingProduct.value) {
    store.createProject(importingProduct.value.id, {
      initialOutput: pendingOutputType.value || 'poster',
    })
  }
  pendingOutputType.value = null
  importingProduct.value = null
  isImporting.value = false
}

function themeBackground(theme) {
  const map = {
    nature: '#ffffff',
    heritage: '#f6f3eb',
    indigo: '#10223d',
  }
  return map[theme] || '#ffffff'
}

function exportFilename() {
  const data = currentOutputData.value
  const title = data?.title || 'studio-output'
  const suffix = activeOutput.value === 'poster'
    ? data?.theme || 'nature'
    : activeOutput.value === 'display'
      ? data?.interactionMode || 'product'
      : 'archive'
  const label = outputLabel(activeOutput.value)
  return `${title}-${label}-${suffix}.png`.replace(/[\\/:*?"<>|]/g, '-')
}

function exportBackground() {
  if (activeOutput.value === 'poster') return themeBackground(posterData.value?.theme)
  if (activeOutput.value === 'display') return '#081016'
  return '#fbfaf6'
}

async function waitForImages(root) {
  const images = Array.from(root.querySelectorAll('img'))
  await Promise.all(images.map(img => {
    if (img.complete && img.naturalWidth > 0) return Promise.resolve()
    return new Promise(resolve => {
      img.onload = resolve
      img.onerror = resolve
    })
  }))
}

async function exportCurrent(scale = 3) {
  if (activeOutput.value === 'display') {
    exportError.value = '智慧大屏是动态演示，请打开 /brand 预览或复制配置。'
    return
  }
  if (isExporting.value || !currentOutputData.value || !activeContentConfirmed.value) return
  exportScale.value = scale
  exportError.value = ''
  isExporting.value = true

  try {
    await nextTick()
    const component = exportRef.value
    const el = component?.$el || component
    if (!el) throw new Error('导出画布尚未准备好')

    await waitForImages(el)
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))

    const canvas = await html2canvas(el, {
      scale,
      useCORS: true,
      backgroundColor: exportBackground(),
      logging: false,
      width: activeFrame.value.width,
      height: activeFrame.value.height,
      windowWidth: activeFrame.value.width,
      windowHeight: activeFrame.value.height,
    })

    const filename = exportFilename()
    const link = document.createElement('a')
    link.download = filename
    link.href = canvas.toDataURL('image/png', 1)
    link.click()
    store.recordExport(activeOutput.value, {
      filename,
      theme: posterData.value?.theme,
      scale,
    })
  } catch (e) {
    exportError.value = e?.message || '导出失败'
  } finally {
    isExporting.value = false
  }
}

function selectDisplayEvent(key) {
  if (!displayData.value?.routeInteractionEnabled) return
  store.updateOutputField('display', 'selectedEventKey', key)
}

function selectDisplayRoute(id) {
  if (!displayData.value?.routeInteractionEnabled) return
  store.updateOutputField('display', 'selectedRouteId', id)
  store.updateOutputField('display', 'selectedEventKey', null)
}

async function ensureDisplayRoute() {
  if (!displayData.value?.selectedRouteId) return
  await loadRoute(displayData.value.selectedRouteId)
}

onMounted(() => {
  loadRoutes()
  ensureDisplayRoute()
  previewScale.value = defaultPreviewScales[activeOutput.value] || 0.72
})

watch(activeOutput, type => {
  previewScale.value = defaultPreviewScales[type] || 0.72
})

watch(
  () => [displayData.value?.interactionMode, displayData.value?.selectedRouteId],
  ([mode]) => {
    if (mode === 'route') ensureDisplayRoute()
  },
)
</script>

<style scoped>
.studio-shell {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: var(--text);
  background: #f5f2eb;
}

.studio-shell *,
.studio-shell *::before,
.studio-shell *::after {
  box-sizing: border-box;
}

.creation-shell {
  min-height: 0;
  flex: 1;
  overflow: auto;
  padding: 26px 34px 30px;
  background:
    linear-gradient(rgba(32, 27, 22, 0.032) 1px, transparent 1px),
    linear-gradient(90deg, rgba(32, 27, 22, 0.026) 1px, transparent 1px),
    #f4f1ea;
  background-size: 30px 30px;
}

.creation-header,
.step-bar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  max-width: 1120px;
  margin: 0 auto 22px;
}

.creation-header h1,
.step-bar h2 {
  margin: 4px 0 0;
  color: var(--text);
  font-size: 26px;
  font-weight: 850;
}

.creation-header p {
  max-width: 620px;
  margin: 7px 0 0;
  color: var(--text-mid);
  font-size: 13px;
  line-height: 1.6;
}

.ui-kicker {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.secondary-btn {
  flex-shrink: 0;
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid rgba(74, 65, 55, 0.16);
  border-radius: 5px;
  background: rgba(255, 252, 247, 0.86);
  color: var(--text-mid);
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: border-color 180ms ease, color 180ms ease;
}

.secondary-btn:hover {
  border-color: rgba(139, 94, 52, 0.38);
  color: var(--earth);
}

.launchpad {
  max-width: 1120px;
  margin: 0 auto;
}

.launchpad-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.launch-card {
  min-height: 250px;
  padding: 20px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 8px;
  background: rgba(255, 252, 247, 0.9);
  color: var(--text);
  cursor: pointer;
  text-align: left;
  transition: border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
}

.launch-card:hover {
  border-color: rgba(139, 94, 52, 0.42);
  background: rgba(255, 252, 247, 0.98);
  box-shadow: 0 18px 44px rgba(32, 27, 22, 0.08);
}

.launch-card span {
  color: var(--earth);
  font-size: 11px;
  font-weight: 850;
  text-transform: uppercase;
}

.launch-card strong {
  display: block;
  margin-top: 22px;
  font-size: 24px;
  font-weight: 850;
}

.launch-card small,
.launch-card em {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
  font-style: normal;
  line-height: 1.65;
}

.launch-card small {
  margin-top: 12px;
  color: var(--text-mid);
}

.launch-card em {
  margin-top: 22px;
  padding-top: 14px;
  border-top: 1px solid rgba(74, 65, 55, 0.12);
}

.recent-projects {
  display: grid;
  grid-template-columns: 180px repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.recent-head,
.recent-row {
  min-height: 72px;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 7px;
  background: rgba(255, 252, 247, 0.72);
  padding: 12px;
}

.recent-head strong,
.recent-row strong,
.recent-row span,
.recent-row small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-head strong {
  margin-top: 4px;
  font-size: 14px;
}

.recent-row {
  color: var(--text);
  cursor: pointer;
  text-align: left;
}

.recent-row span {
  color: var(--earth);
  font-size: 11px;
  font-weight: 850;
}

.recent-row strong {
  margin-top: 4px;
  font-size: 12px;
}

.recent-row small {
  margin-top: 3px;
  color: var(--text-muted);
  font-size: 11px;
}

.product-step {
  max-width: 1120px;
  margin: 0 auto;
}

.creation-import {
  max-width: 780px;
  margin: 54px auto 0;
}

.product-gallery {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 14px;
}

.library-gallery,
.custom-import-panel {
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 8px;
  background: rgba(255, 252, 247, 0.9);
  box-shadow: 0 18px 44px rgba(32, 27, 22, 0.065);
}

.library-gallery {
  padding: 14px;
}

.gallery-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.gallery-head strong {
  display: block;
  margin-top: 3px;
  color: var(--text);
  font-size: 15px;
  font-weight: 850;
}

.gallery-head small {
  color: var(--text-muted);
  font-size: 11px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.product-card {
  position: relative;
  min-height: 234px;
  overflow: hidden;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 7px;
  background: rgba(250, 247, 241, 0.76);
  color: var(--text);
  cursor: pointer;
  text-align: left;
  transition: border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
}

.product-card:hover {
  border-color: rgba(139, 94, 52, 0.42);
  background: rgba(255, 252, 247, 0.98);
  box-shadow: 0 12px 30px rgba(32, 27, 22, 0.08);
}

.product-card img {
  display: block;
  width: 100%;
  height: 116px;
  object-fit: cover;
}

.product-card > span {
  position: absolute;
  top: 104px;
  right: 12px;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 252, 247, 0.95);
  border-radius: 999px;
}

.product-card div {
  padding: 12px;
}

.product-card strong,
.product-card small,
.product-card p {
  display: block;
  overflow: hidden;
}

.product-card strong {
  color: var(--text);
  font-size: 14px;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-card small {
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-card p {
  display: -webkit-box;
  margin: 9px 0 0;
  color: var(--text-mid);
  font-size: 12px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.custom-import-panel {
  align-self: start;
  padding: 16px;
}

.custom-import-panel strong {
  display: block;
  margin-top: 8px;
  color: var(--text);
  font-size: 18px;
  font-weight: 850;
}

.custom-import-panel p {
  margin: 9px 0 0;
  color: var(--text-mid);
  font-size: 12px;
  line-height: 1.65;
}

.import-dropzone {
  display: grid;
  place-items: center;
  min-height: 128px;
  margin-top: 16px;
  border: 1px dashed rgba(74, 65, 55, 0.22);
  border-radius: 7px;
  background: rgba(246, 243, 235, 0.58);
  text-align: center;
}

.import-dropzone span,
.import-dropzone small {
  display: block;
}

.import-dropzone span {
  color: var(--text);
  font-size: 12px;
  font-weight: 850;
}

.import-dropzone small {
  margin-top: 5px;
  color: var(--text-muted);
  font-size: 11px;
}

.disabled-import-btn {
  width: 100%;
  min-height: 36px;
  margin-top: 12px;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 5px;
  background: rgba(74, 65, 55, 0.08);
  color: var(--text-muted);
  cursor: not-allowed;
  font-size: 12px;
  font-weight: 850;
}

.studio-grid {
  min-height: 0;
  flex: 1;
  display: grid;
  grid-template-columns: 360px minmax(620px, 1fr) 340px;
}

.studio-panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-height: 0;
  background: rgba(250, 247, 241, 0.82);
}

.panel-chrome {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-width: 0;
  min-height: 52px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(74, 65, 55, 0.12);
  background: rgba(255, 252, 247, 0.62);
}

.panel-chrome span {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
}

.panel-chrome strong {
  display: block;
  margin-top: 2px;
  color: var(--text);
  font-size: 13px;
  font-weight: 850;
}

.panel-chrome small {
  overflow: hidden;
  max-width: 138px;
  color: var(--text-muted);
  font-size: 11px;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tool-chrome {
  align-items: center;
}

.side-tabs {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 3px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 5px;
  background: rgba(246, 243, 235, 0.76);
}

.side-tabs button {
  min-width: 42px;
  height: 26px;
  border: 0;
  border-radius: 3px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
}

.side-tabs button.active {
  background: rgba(139, 94, 52, 0.12);
  color: var(--earth);
}

.panel-scroll {
  min-height: 0;
  overflow-y: auto;
}

.studio-empty-note {
  margin: 12px;
  padding: 12px;
  border: 1px dashed rgba(74, 65, 55, 0.18);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.5);
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.65;
}

.studio-stage {
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  background:
    linear-gradient(rgba(32, 27, 22, 0.034) 1px, transparent 1px),
    linear-gradient(90deg, rgba(32, 27, 22, 0.03) 1px, transparent 1px),
    #f2eee6;
  background-size: 30px 30px, 30px 30px, auto;
}

.canvas-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 52px;
  padding: 8px 14px;
  border-bottom: 1px solid rgba(74, 65, 55, 0.13);
  background: rgba(255, 252, 247, 0.74);
}

.canvas-title {
  min-width: 0;
}

.canvas-title span,
.canvas-title h1 {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.canvas-title span {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
}

.canvas-title h1 {
  margin: 2px 0 0;
  color: var(--text);
  font-size: 15px;
  font-weight: 850;
}

.canvas-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-pill {
  min-width: 48px;
  border-radius: 4px;
  background: rgba(94, 123, 80, 0.14);
  color: var(--leaf);
  font-size: 11px;
  font-weight: 850;
  padding: 5px 9px;
  text-align: center;
}

.save-indicator {
  color: var(--text-muted);
  font-size: 11px;
  white-space: nowrap;
}

.module-setup {
  align-self: start;
  justify-self: center;
  width: min(780px, calc(100% - 48px));
  margin-top: 42px;
  padding: 24px;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 8px;
  background: rgba(255, 252, 247, 0.94);
  box-shadow: 0 18px 48px rgba(32, 27, 22, 0.075);
}

.module-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.module-head h2 {
  margin: 6px 0 0;
  color: var(--text);
  font-size: 22px;
  font-weight: 850;
}

.module-head p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 12px;
}

.module-head > span {
  flex-shrink: 0;
  color: var(--earth);
  font-size: 12px;
  font-weight: 850;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.module-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-height: 78px;
  padding: 12px;
  border: 1px solid rgba(74, 65, 55, 0.14);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.68);
  cursor: pointer;
  transition: border-color 180ms ease, background 180ms ease;
}

.module-card:hover,
.module-card.active {
  border-color: rgba(139, 94, 52, 0.44);
  background: rgba(139, 94, 52, 0.08);
}

.module-card input {
  margin-top: 2px;
  accent-color: var(--earth);
  cursor: pointer;
}

.module-card strong {
  display: block;
  color: var(--text);
  font-size: 13px;
}

.module-card small {
  display: block;
  margin-top: 8px;
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.6;
}

.module-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid rgba(74, 65, 55, 0.13);
}

.confirm-btn {
  min-height: 36px;
  border: 1px solid #201b16;
  border-radius: 5px;
  background: #201b16;
  color: #fffaf3;
  cursor: pointer;
  font-size: 12px;
  font-weight: 850;
  padding: 0 14px;
}

.confirm-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.preview-workspace {
  width: 100%;
  height: 100%;
  min-height: 0;
}

.poster-scroll {
  position: relative;
  min-height: 0;
  overflow: auto;
  display: grid;
  place-items: start center;
  height: 100%;
  padding: 28px 0 36px;
  background:
    linear-gradient(rgba(32, 27, 22, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(32, 27, 22, 0.046) 1px, transparent 1px),
    rgba(246, 243, 235, 0.7);
  background-size: 24px 24px;
  box-shadow: inset 0 1px 0 rgba(255, 252, 247, 0.72);
}

.poster-scroll.display-scroll {
  overflow: hidden;
  place-items: center;
  padding: 18px;
}

.canvas-zoom-control {
  position: absolute;
  right: 14px;
  bottom: 14px;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 3px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 5px;
  background: rgba(255, 252, 247, 0.86);
  box-shadow: 0 10px 26px rgba(32, 27, 22, 0.09);
}

.canvas-zoom-control button {
  min-width: 44px;
  height: 28px;
  border: 0;
  border-radius: 3px;
  background: transparent;
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
}

.canvas-zoom-control button.active {
  background: rgba(139, 94, 52, 0.12);
  color: var(--earth);
}

.poster-preview-shell {
  flex-shrink: 0;
  filter: drop-shadow(0 22px 36px rgba(32, 27, 22, 0.16));
}

.inspector-summary {
  margin: 12px;
  padding: 12px;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.58);
}

.inspector-summary span,
.inspector-summary strong,
.inspector-summary small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inspector-summary span {
  color: var(--earth);
  font-size: 11px;
  font-weight: 850;
}

.inspector-summary strong {
  margin-top: 4px;
  color: var(--text);
  font-size: 13px;
}

.inspector-summary small {
  margin-top: 3px;
  color: var(--text-muted);
  font-size: 11px;
}

.export-layer {
  position: fixed;
  left: -10000px;
  top: 0;
  overflow: hidden;
  pointer-events: none;
}
</style>
