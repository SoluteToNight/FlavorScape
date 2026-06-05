<template>
  <main class="studio-shell fixed top-navbar inset-x-0 bottom-0 bg-bg">
    <section v-if="waitingForProjects" class="creation-shell studio-loading">
      <div>
        <span class="ui-kicker">Xunwei Studio</span>
        <h1>正在加载你的工作台</h1>
        <p>项目、编辑状态和交付记录将从当前登录账号同步。</p>
      </div>
    </section>

    <section v-else-if="activeSection === 'import'" class="creation-shell">
      <header class="creation-header">
        <div>
          <span class="ui-kicker">Xunwei Studio · Asset Import</span>
          <h1>资产导入</h1>
          <p>上传检测报告、品牌资料和产地信息，生成营销海报、实证白皮书与智慧大屏。</p>
        </div>
        <button type="button" class="secondary-btn" @click="router.replace({ path: '/studio' })">
          返回工作台
        </button>
      </header>
      <AssetImport embedded />
    </section>

    <section v-else-if="showCreationFlow" class="creation-shell">
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

      <section v-else-if="showTemplateStep" class="template-step">
        <div class="step-bar">
          <div>
            <span class="ui-kicker">Step 2 / Creative Template</span>
            <h2>选择{{ selectedOutputOption?.label }}模板、尺寸和主题</h2>
          </div>
          <button type="button" class="secondary-btn" @click="cancelCreator">
            重选项目类型
          </button>
        </div>

        <div class="template-layout">
          <section class="template-library">
            <div class="template-library-head">
              <div>
                <span class="ui-kicker">Template Library</span>
                <h3>先选择版式起点</h3>
              </div>
              <small>{{ activeTemplateOptions.length }} 个模板</small>
            </div>
            <div class="template-card-grid">
              <button
                v-for="item in activeTemplateOptions"
                :key="item.id"
                type="button"
                class="template-card"
                :class="{ active: templateConfig.templateId === item.id }"
                @click="selectTemplateCard(item)"
              >
                <span class="template-preview" :class="`template-preview-${item.family}`">
                  <i /><i /><i />
                </span>
                <span class="template-card-copy">
                  <strong>{{ item.name }}</strong>
                  <small>{{ item.description }}</small>
                  <em>{{ item.tags.join(' / ') }}</em>
                </span>
              </button>
            </div>
          </section>

          <aside class="template-panel template-start">
            <span class="ui-kicker">Start Point</span>
            <h3>{{ selectedTemplate?.name }}</h3>
            <p>{{ selectedTemplate?.tone }} · {{ selectedTemplate?.description }}</p>
            <label class="project-name-field">
              <span>项目名称</span>
              <input
                v-model="pendingProjectName"
                maxlength="40"
                placeholder="给这个项目起个名字"
              />
            </label>

            <div class="template-pick-block">
              <div class="field-head">
                <label>尺寸</label>
                <span>{{ selectedCanvasPreset?.width }} × {{ selectedCanvasPreset?.height }}</span>
              </div>
              <div class="template-options compact">
                <button
                  v-for="item in activeCanvasPresets"
                  :key="item.id"
                  type="button"
                  class="template-option"
                  :class="{ active: templateConfig.presetId === item.id }"
                  @click="templateConfig.presetId = item.id"
                >
                  <strong>{{ item.name }}</strong>
                  <small>{{ item.group }} · {{ item.ratio }}</small>
                </button>
              </div>
            </div>

            <div class="template-pick-block">
              <div class="field-head">
                <label>主题</label>
                <span>{{ selectedTheme?.name }}</span>
              </div>
              <div class="template-options compact">
                <button
                  v-for="item in themeOptions"
                  :key="item.id"
                  type="button"
                  class="template-option theme-pick"
                  :class="{ active: templateConfig.themeId === item.id }"
                  @click="templateConfig.themeId = item.id"
                >
                  <span class="template-swatch" :style="{ background: item.swatch }" />
                  <strong>{{ item.name }}</strong>
                </button>
              </div>
            </div>
            <button type="button" class="confirm-btn template-next" @click="confirmTemplateStep">
              继续选择产品
            </button>
          </aside>
        </div>
      </section>

      <section v-else class="product-step">
        <div class="step-bar">
          <div>
            <span class="ui-kicker">{{ productStepKicker }}</span>
            <h2>选择{{ selectedOutputOption?.label }}项目的产品</h2>
          </div>
          <button type="button" class="secondary-btn" @click="cancelCreator">
            重选项目类型
          </button>
        </div>
        <label class="project-name-strip">
          <span>项目名称</span>
          <input
            v-model="pendingProjectName"
            maxlength="40"
            placeholder="给这个项目起个名字"
          />
        </label>
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
            <p>上传产品资料、检测报告和产地信息，AI 自动生成可编辑的品牌资产项目。</p>
            <div class="import-dropzone">
              <span>PDF / DOCX / XLSX / CSV / 图片</span>
              <small>支持拖放或选择文件，DeepSeek 智能分析</small>
            </div>
            <button type="button" class="enabled-import-btn" @click="openCustomImport">
              进入资产导入
            </button>
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
              <ProjectManager
                @new-project="openProductPicker"
                @select-project="openExistingProject"
              />
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
              <div v-if="sourceAssetLabel" class="source-asset-card">
                <span>Asset Source</span>
                <strong>{{ sourceAssetLabel }}</strong>
                <small>{{ sourceReviewLabel }}</small>
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
          <div ref="previewViewportEl" class="poster-scroll" :class="{ 'display-scroll': activeOutput === 'display' }">
            <div class="canvas-zoom-control" aria-label="预览缩放">
              <button
                v-for="item in zoomOptions"
                :key="item.label"
                type="button"
                :class="{ active: item.mode === 'fit' ? previewMode === 'fit' : (previewMode === 'fixed' && previewScale === item.value) }"
                @click="applyZoomOption(item)"
              >
                {{ item.label }}
              </button>
            </div>
            <div class="poster-preview-shell" :style="previewFrameStyle">
              <StudioPoster
                v-if="activeOutput === 'poster' && !activeLayout"
                :poster-data="posterData"
                :scale="previewScale"
              />
              <StudioArchive
                v-else-if="activeOutput === 'archive' && !activeLayout"
                :archive-data="archiveData"
                :scale="previewScale"
              />
              <FreeLayoutCanvas
                v-else-if="activeLayout && (activeOutput === 'poster' || activeOutput === 'archive')"
                :layout="activeLayout"
                :scale="previewScale"
                :selected-ids="store.selectedElementIds"
                editable
                @select="store.setSelectedElementIds"
                @clear-selection="store.setSelectedElementIds([])"
                @update-elements="updateLayoutElements"
                @history-point="store.updateLayout(activeOutput, {}, { history: true })"
                @delete-selected="store.removeElements(activeOutput)"
                @duplicate-selected="store.duplicateSelectedElements(activeOutput)"
                @undo="store.undoLayout"
                @redo="store.redoLayout"
                @drop-element="addDroppedElement"
              />
              <BrandDisplayExperience
                v-else-if="activeOutput === 'display'"
                :display-data="displayData"
                :route-data="activeRouteData"
                :route-options="displayRouteOptions"
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
            <span>Right Panel</span>
            <strong>{{ rightPanelTitle }}</strong>
          </div>
          <div class="right-tabs" aria-label="右侧面板">
            <button
              type="button"
              :class="{ active: activeRightTab === 'inspect' }"
              :disabled="!activeLayout || !['poster', 'archive'].includes(activeOutput)"
              @click="activeRightTab = 'inspect'"
            >
              图层
            </button>
            <button
              type="button"
              :class="{ active: activeRightTab === 'delivery' }"
              @click="activeRightTab = 'delivery'"
            >
              交付
            </button>
          </div>
        </div>
        <div class="panel-scroll">
          <template v-if="activeRightTab === 'inspect' && activeLayout && (activeOutput === 'poster' || activeOutput === 'archive')">
            <LayerPanel
              :layout="activeLayout"
              :selected-ids="store.selectedElementIds"
              @select="store.setSelectedElementIds"
              @toggle-visible="toggleLayerVisible"
              @toggle-lock="toggleLayerLock"
              @reorder="reorderSelectedLayer"
              @duplicate="store.duplicateSelectedElements(activeOutput)"
              @remove="store.removeElements(activeOutput)"
            />
            <PropertyInspector
              :element="store.selectedElements[0] || null"
              @update="updateSelectedElement"
              @upload-image="selectInspectorImage"
            />
          </template>
          <section v-else class="delivery-dock">
            <OutputChecklist
              :is-exporting="isExporting"
              :export-error="exportError"
              :export-scale="exportScale"
              @export-current="exportCurrent"
            />
          </section>
        </div>
      </aside>

    </div>

    <SpatialFooter />

    <input
      ref="inspectorFileInput"
      type="file"
      accept="image/*"
      class="hidden-file-input"
      @change="onInspectorImageUpload"
    />

    <div v-if="isExporting" class="export-layer" :style="exportLayerStyle" aria-hidden="true">
      <StudioPoster
        v-if="activeContentConfirmed && activeOutput === 'poster' && posterData && !activeLayout"
        ref="exportRef"
        :poster-data="posterData"
        :scale="1"
      />
      <StudioArchive
        v-else-if="activeContentConfirmed && activeOutput === 'archive' && archiveData && !activeLayout"
        ref="exportRef"
        :archive-data="archiveData"
        :scale="1"
      />
      <FreeLayoutCanvas
        v-else-if="activeContentConfirmed && activeLayout && (activeOutput === 'poster' || activeOutput === 'archive')"
        ref="exportRef"
        :layout="activeLayout"
        :scale="1"
      />
    </div>
  </main>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import html2canvas from 'html2canvas'
import AssetImport from '../components/AssetImport.vue'
import BrandDisplayExperience from '../components/BrandDisplayExperience.vue'
import CreativeEditor from '../components/CreativeEditor.vue'
import FreeLayoutCanvas from '../components/editor/FreeLayoutCanvas.vue'
import LayerPanel from '../components/editor/LayerPanel.vue'
import PropertyInspector from '../components/editor/PropertyInspector.vue'
import ImportFlow from '../components/ImportFlow.vue'
import OutputChecklist from '../components/OutputChecklist.vue'
import ProjectManager from '../components/ProjectManager.vue'
import SpatialFooter from '../components/SpatialFooter.vue'
import StudioArchive from '../components/StudioArchive.vue'
import StudioPoster from '../components/StudioPoster.vue'
import { canvasPresetOptions, defaultPresetId, defaultTemplateId, getTemplate, templateOptions } from '../data/layout-presets'
import { themeOptions } from '../data/themes'
import { useProductCases } from '../composables/useProductCases'
import { useSpreadRoutes } from '../composables/useSpreadRoutes'
import { useStudioStore } from '../stores/studio'

const store = useStudioStore()
const route = useRoute()
const router = useRouter()
const { cases: productCases, getById } = useProductCases()
const { routeOptions, loadRoutes, loadRoute, getRoute } = useSpreadRoutes()

const activeProject = computed(() => store.activeProject)
const activeProductName = computed(() => store.activeSourceAsset?.assetPackage?.product?.name || store.activeProductCase?.name || '未选择产品')
const activeOutput = computed(() => store.activeOutput)
const activeContentConfirmed = computed(() => store.activeContentConfirmed)
const activeSourceAsset = computed(() => store.activeSourceAsset)
const waitingForProjects = computed(() => store.loading && !store.remoteLoaded)
const posterData = computed(() => store.mergedPosterData)
const archiveData = computed(() => store.mergedArchiveData)
const displayData = computed(() => store.mergedDisplayData)
const activeLayout = computed(() => store.activeLayout)
const currentOutputData = computed(() => ({
  poster: posterData.value,
  archive: archiveData.value,
  display: displayData.value,
}[activeOutput.value]))
const activeRouteData = computed(() => displayData.value?.assetRouteData || getRoute(displayData.value?.selectedRouteId))
const displayRouteOptions = computed(() => displayData.value?.assetRouteOptions?.length ? displayData.value.assetRouteOptions : routeOptions.value)

const isImporting = ref(false)
const importingProduct = ref(null)
const showProductPicker = ref(false)
const pendingOutputType = ref(null)
const pendingProjectName = ref('')
const templateConfirmed = ref(false)
const templateConfig = ref({
  templateId: defaultTemplateId('poster'),
  presetId: defaultPresetId('poster'),
  themeId: 'nature',
})
const isExporting = ref(false)
const exportError = ref('')
const exportScale = ref(3)
const previewScale = ref(0.72)
const previewMode = ref('fit')
const exportRef = ref(null)
const activeSideTab = ref('edit')
const activeRightTab = ref('delivery')
const previewViewportEl = ref(null)
const inspectorFileInput = ref(null)
const pendingInspectorImageElementId = ref(null)
let previewResizeObserver = null
let routeProjectLoadSeq = 0

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
    description: '创建可在大屏预览区查看的动态地图、传播路径和巡航演示。',
    flow: '选择产品后配置大屏信息、空间节点和传播路径交互。',
  },
]

const zoomOptions = [
  { label: 'Fit', mode: 'fit' },
  { label: '72%', value: 0.72 },
  { label: '86%', value: 0.86 },
  { label: '100%', value: 1 },
]

const defaultPreviewScales = {
  poster: 0.72,
  archive: 0.61,
  display: 0.54,
}

const outputFrames = {
  poster: { width: 440, height: 860 },
  archive: { width: 760, height: 1040 },
  display: { width: 1280, height: 720 },
}

const activeSection = computed(() => route.query.section || null)

const showCreationFlow = computed(() =>
  isImporting.value || !activeProject.value || showProductPicker.value || Boolean(pendingOutputType.value)
)
const outputNeedsTemplate = computed(() => ['poster', 'archive'].includes(pendingOutputType.value))
const showTemplateStep = computed(() => pendingOutputType.value && outputNeedsTemplate.value && !templateConfirmed.value)
const activeCanvasPresets = computed(() => canvasPresetOptions(pendingOutputType.value))
const activeTemplateOptions = computed(() => templateOptions(pendingOutputType.value))
const selectedTemplate = computed(() => getTemplate(pendingOutputType.value, templateConfig.value.templateId))
const selectedCanvasPreset = computed(() =>
  activeCanvasPresets.value.find(item => item.id === templateConfig.value.presetId)
)
const selectedTheme = computed(() => themeOptions.find(item => item.id === templateConfig.value.themeId))
const activeFrame = computed(() => {
  if (activeLayout.value && activeOutput.value !== 'display') {
    return { width: activeLayout.value.width, height: activeLayout.value.height }
  }
  return outputFrames[activeOutput.value] || outputFrames.poster
})
const activeOutputLabel = computed(() => outputLabel(activeOutput.value))
const rightPanelTitle = computed(() => activeRightTab.value === 'inspect' ? '图层 / 属性' : '交付')
const selectedOutputOption = computed(() => outputOptions.find(item => item.type === pendingOutputType.value))
const productStepKicker = computed(() => outputNeedsTemplate.value ? 'Step 3 / Product Source' : 'Step 2 / Product Source')
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
  if (showTemplateStep.value) return `已选择${selectedOutputOption.value?.label || '可视化'}项目，先确定模板、尺寸、主题和项目名称。`
  if (pendingOutputType.value) return `已选择${selectedOutputOption.value?.label || '可视化'}项目，下一步选择具体产品。`
  return '先选择交付物形式，再选择模板、产品、配置模块和视觉风格。'
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
  if (store.lastError) return `保存失败：${store.lastError}`
  if (store.syncStatus === 'loading') return '正在加载'
  if (store.syncStatus === 'saving') return '保存中'
  const value = activeProject.value?.updatedAt
  if (!value) return '已保存'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '已保存'
  return `已保存 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
})

const sourceAssetLabel = computed(() => {
  const source = activeSourceAsset.value
  if (!source) return ''
  const productName = source.assetPackage?.product?.name
  return productName ? `DeepSeek 资产包：${productName}` : 'DeepSeek 资产包'
})

const sourceReviewLabel = computed(() => {
  const status = activeSourceAsset.value?.reviewStatus?.status || activeSourceAsset.value?.assetPackage?.review_status?.status
  const labels = {
    pending: '等待人工复核',
    needs_review: '需要重点复核',
    in_review: '复核进行中',
    approved: '已复核通过',
    rejected: '复核未通过',
  }
  return labels[status] || '证据来源已随项目保存'
})

function outputLabel(type) {
  return outputOptions.find(item => item.type === type)?.label || '产出'
}

function openProductPicker() {
  pendingOutputType.value = null
  showProductPicker.value = true
  pendingProjectName.value = ''
}

function openCustomImport() {
  router.push({ path: '/studio', query: { section: 'import' } })
}

function cancelCreator() {
  pendingOutputType.value = null
  showProductPicker.value = false
  templateConfirmed.value = false
  pendingProjectName.value = ''
}

function selectOutputIntent(type) {
  pendingOutputType.value = type
  pendingProjectName.value = `${outputLabel(type)}项目`
  templateConfirmed.value = !['poster', 'archive'].includes(type)
  showProductPicker.value = templateConfirmed.value
  templateConfig.value = {
    templateId: defaultTemplateId(type),
    presetId: defaultPresetId(type),
    themeId: type === 'poster' ? 'nature' : 'nature',
  }
}

function selectTemplateCard(template) {
  if (!template) return
  templateConfig.value = {
    templateId: template.id,
    presetId: template.recommendedPresetId || defaultPresetId(pendingOutputType.value, template.id),
    themeId: template.recommendedThemeId || templateConfig.value.themeId || 'nature',
  }
}

function confirmTemplateStep() {
  templateConfirmed.value = true
  showProductPicker.value = true
}

function openExistingProject(id) {
  store.switchProject(id)
  cancelCreator()
  replaceProjectQuery(id, { force: true })
}

function replaceProjectQuery(id, options = {}) {
  if (!id || route.name !== 'studio' || route.query.section === 'import') return
  const currentProjectId = queryValue(route.query.projectId)
  if (currentProjectId === id) return
  if (currentProjectId && !options.force) return
  router.replace({ path: '/studio', query: { ...route.query, section: undefined, projectId: id } })
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
    const projectId = store.createProject(importingProduct.value.id, {
      initialOutput: pendingOutputType.value || 'poster',
      name: pendingProjectName.value,
    })
    if (['poster', 'archive'].includes(pendingOutputType.value)) {
      store.initLayout(pendingOutputType.value, {
        templateId: templateConfig.value.templateId,
        presetId: templateConfig.value.presetId,
        themeId: templateConfig.value.themeId,
      })
    }
    if (projectId) router.replace({ path: '/studio', query: { projectId } })
  }
  pendingOutputType.value = null
  templateConfirmed.value = false
  pendingProjectName.value = ''
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

function calculateFitScale() {
  const viewport = previewViewportEl.value
  const frame = activeFrame.value
  if (!viewport || !frame) return defaultPreviewScales[activeOutput.value] || 0.72
  const availableWidth = Math.max(220, viewport.clientWidth - 40)
  const availableHeight = Math.max(220, viewport.clientHeight - 56)
  const nextScale = Math.min(1, availableWidth / frame.width, availableHeight / frame.height)
  const minScale = activeOutput.value === 'display' ? 0.34 : 0.42
  return Number(Math.max(minScale, nextScale).toFixed(2))
}

function syncPreviewScale() {
  if (previewMode.value !== 'fit') return
  previewScale.value = calculateFitScale()
}

function applyZoomOption(item) {
  if (item.mode === 'fit') {
    previewMode.value = 'fit'
    syncPreviewScale()
    return
  }
  previewMode.value = 'fixed'
  previewScale.value = item.value
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
  if (activeLayout.value && activeOutput.value !== 'display') return activeLayout.value.backgroundColor || '#ffffff'
  if (activeOutput.value === 'poster') return themeBackground(posterData.value?.theme)
  if (activeOutput.value === 'display') return '#081016'
  return '#fbfaf6'
}

function updateLayoutElements(patches, options = {}) {
  store.updateElements(activeOutput.value, patches, options)
}

function addDroppedElement(payload) {
  if (!payload?.elementType) return
  store.addElement(activeOutput.value, payload.elementType, {
    x: payload.x,
    y: payload.y,
    preset: payload.preset,
  })
}

function updateSelectedElement(patch) {
  const element = store.selectedElements[0]
  if (!element) return
  store.updateElement(activeOutput.value, element.id, patch)
}

function toggleLayerVisible(element) {
  store.updateElement(activeOutput.value, element.id, { visible: element.visible === false })
}

function toggleLayerLock(element) {
  store.updateElement(activeOutput.value, element.id, { locked: !element.locked })
}

function reorderSelectedLayer(action) {
  const id = store.selectedElementIds[0]
  if (!id) return
  store.reorderElement(activeOutput.value, id, action)
}

function selectInspectorImage(elementId) {
  pendingInspectorImageElementId.value = elementId
  inspectorFileInput.value?.click()
}

function onInspectorImageUpload(event) {
  const file = event.target.files?.[0]
  const elementId = pendingInspectorImageElementId.value
  if (!file || !elementId) return
  const reader = new FileReader()
  reader.onload = e => {
    store.updateElement(activeOutput.value, elementId, { src: e.target?.result || '' })
  }
  reader.readAsDataURL(file)
  event.target.value = ''
  pendingInspectorImageElementId.value = null
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
    exportError.value = '智慧大屏是动态演示，请通过产出中心打开预览或复制配置。'
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
      theme: activeLayout.value?.themeId || posterData.value?.theme,
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
  if (displayData.value?.assetRouteData || !displayData.value?.selectedRouteId) return
  await loadRoute(displayData.value.selectedRouteId)
}

function queryValue(value) {
  return Array.isArray(value) ? value[0] : value
}

async function syncProjectFromRoute() {
  const projectId = queryValue(route.query.projectId)
  if (!projectId) return
  const seq = ++routeProjectLoadSeq
  cancelCreator()
  if (store.activeProjectId === projectId) return
  const project = store.projectList.some(item => item.id === projectId)
    ? (store.switchProject(projectId), store.activeProject)
    : await store.loadProject(projectId)
  if (seq !== routeProjectLoadSeq || !project) return
  activeSideTab.value = 'edit'
  await nextTick()
  syncPreviewScale()
}

onMounted(async () => {
  await store.loadRemoteProjects()
  if (typeof route.query.project === 'string' && route.query.project) {
    await store.loadProject(route.query.project)
  }
  await syncProjectFromRoute()
  loadRoutes()
  ensureDisplayRoute()
  await nextTick()
  syncPreviewScale()
  previewResizeObserver = new ResizeObserver(() => syncPreviewScale())
  if (previewViewportEl.value) previewResizeObserver.observe(previewViewportEl.value)
  window.addEventListener('resize', syncPreviewScale)
})

watch(activeOutput, type => {
  previewMode.value = 'fit'
  previewScale.value = defaultPreviewScales[type] || 0.72
  activeRightTab.value = ['poster', 'archive'].includes(type) && activeLayout.value ? 'inspect' : 'delivery'
  nextTick(() => syncPreviewScale())
})

watch(currentOutputData, () => nextTick(() => syncPreviewScale()))

watch(activeLayout, layout => {
  if (layout && ['poster', 'archive'].includes(activeOutput.value)) activeRightTab.value = 'inspect'
  else activeRightTab.value = 'delivery'
})

watch(
  () => route.query.projectId,
  () => syncProjectFromRoute(),
)

watch(
  () => store.activeProjectId,
  id => replaceProjectQuery(id),
)

watch(
  () => [route.name, route.query.section, route.query.projectId],
  () => {
    if (route.name === 'studio' && route.query.section !== 'import' && !route.query.projectId) {
      replaceProjectQuery(store.activeProjectId)
    }
  },
)

watch(
  () => [displayData.value?.interactionMode, displayData.value?.selectedRouteId],
  ([mode]) => {
    if (mode === 'route') ensureDisplayRoute()
  },
)

onUnmounted(() => {
  previewResizeObserver?.disconnect()
  window.removeEventListener('resize', syncPreviewScale)
})
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
  padding: 26px var(--page-gutter) 30px;
  background:
    linear-gradient(rgba(32, 27, 22, 0.032) 1px, transparent 1px),
    linear-gradient(90deg, rgba(32, 27, 22, 0.026) 1px, transparent 1px),
    #f4f1ea;
  background-size: 30px 30px;
}

.studio-loading {
  display: grid;
  place-items: center;
  text-align: center;
}

.studio-loading h1 {
  margin: 8px 0 0;
  color: var(--text);
  font-size: 24px;
  font-weight: 850;
}

.studio-loading p {
  margin: 10px 0 0;
  color: var(--text-mid);
  font-size: 13px;
}

.creation-header,
.step-bar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  max-width: var(--content-narrow);
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
  max-width: var(--content-narrow);
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
  max-width: var(--content-narrow);
  margin: 0 auto;
}

.template-step {
  max-width: var(--content-narrow);
  margin: 0 auto;
}

.template-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 14px;
}

.template-library,
.template-panel {
  min-height: 280px;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 8px;
  background: rgba(255, 252, 247, 0.9);
  padding: 16px;
  box-shadow: 0 18px 44px rgba(32, 27, 22, 0.065);
}

.template-library {
  padding: 16px;
}

.template-library-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.template-panel h3 {
  margin: 6px 0 14px;
  color: var(--text);
  font-size: 18px;
  font-weight: 850;
}

.template-library-head h3 {
  margin: 6px 0 0;
  color: var(--text);
  font-size: 20px;
  font-weight: 850;
}

.template-library-head small,
.template-start p {
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.55;
}

.template-card-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.template-card {
  display: grid;
  grid-template-rows: 118px minmax(0, 1fr);
  min-height: 260px;
  overflow: hidden;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 8px;
  background: rgba(250, 247, 241, 0.76);
  color: var(--text);
  cursor: pointer;
  text-align: left;
  transition: border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
}

.template-card:hover,
.template-card.active {
  border-color: rgba(139, 94, 52, 0.48);
  background: rgba(255, 252, 247, 0.98);
  box-shadow: 0 14px 34px rgba(32, 27, 22, 0.09);
}

.template-card.active {
  box-shadow: inset 0 0 0 1px rgba(139, 94, 52, 0.22), 0 14px 34px rgba(32, 27, 22, 0.09);
}

.template-preview {
  position: relative;
  display: block;
  margin: 12px;
  overflow: hidden;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 6px;
  background:
    linear-gradient(135deg, rgba(139, 94, 52, 0.12), transparent 60%),
    #f6f1e6;
}

.template-preview i {
  position: absolute;
  display: block;
  border-radius: 4px;
  background: rgba(42, 65, 40, 0.78);
}

.template-preview i:nth-child(1) {
  left: 10%;
  top: 10%;
  width: 80%;
  height: 38%;
  opacity: 0.28;
}

.template-preview i:nth-child(2) {
  left: 12%;
  bottom: 30%;
  width: 58%;
  height: 12%;
}

.template-preview i:nth-child(3) {
  left: 12%;
  bottom: 12%;
  width: 76%;
  height: 10%;
  opacity: 0.55;
}

.template-preview-heritage {
  background: #efe4d2;
}

.template-preview-heritage i:nth-child(1) {
  left: 22%;
  top: 16%;
  width: 56%;
  height: 36%;
  border-radius: 999px;
}

.template-preview-indigo {
  background: #10223d;
}

.template-preview-indigo i {
  background: rgba(219, 234, 254, 0.76);
}

.template-preview-map i:nth-child(1),
.template-preview-landscape i:nth-child(2) {
  left: 12%;
  top: 18%;
  width: 54%;
  height: 56%;
  border-radius: 999px;
}

.template-preview-grid i:nth-child(1) {
  left: 10%;
  top: 18%;
  width: 36%;
  height: 24%;
}

.template-preview-grid i:nth-child(2) {
  left: 54%;
  top: 18%;
  width: 36%;
  height: 24%;
}

.template-preview-grid i:nth-child(3) {
  left: 10%;
  bottom: 18%;
  width: 80%;
  height: 24%;
}

.template-preview-split i:nth-child(1),
.template-preview-banner i:nth-child(1) {
  left: 8%;
  top: 12%;
  width: 43%;
  height: 76%;
}

.template-preview-blank i {
  opacity: 0;
}

.template-card-copy {
  display: block;
  padding: 0 12px 12px;
}

.template-card-copy strong,
.template-card-copy small,
.template-card-copy em {
  display: block;
}

.template-card-copy strong {
  color: var(--text);
  font-size: 14px;
  font-weight: 850;
}

.template-card-copy small {
  display: -webkit-box;
  overflow: hidden;
  margin-top: 7px;
  color: var(--text-mid);
  font-size: 11px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.template-card-copy em {
  margin-top: 8px;
  color: var(--earth);
  font-size: 10px;
  font-style: normal;
  font-weight: 850;
}

.template-options {
  display: grid;
  gap: 9px;
}

.template-options.compact {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}

.template-option {
  display: grid;
  gap: 5px;
  min-height: 68px;
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 6px;
  background: rgba(250, 247, 241, 0.72);
  color: var(--text);
  cursor: pointer;
  text-align: left;
  transition: border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
}

.template-option:hover,
.template-option.active {
  border-color: rgba(139, 94, 52, 0.46);
  background: rgba(139, 94, 52, 0.08);
}

.template-option.active {
  box-shadow: inset 0 0 0 1px rgba(139, 94, 52, 0.22);
}

.template-option strong,
.template-option small {
  display: block;
}

.template-option strong {
  font-size: 13px;
  font-weight: 850;
}

.template-option small {
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.5;
}

.theme-pick {
  grid-template-columns: 30px minmax(0, 1fr);
  align-items: center;
}

.theme-pick small {
  grid-column: 2;
}

.template-swatch {
  grid-row: span 2;
  width: 28px;
  height: 28px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 5px;
}

.template-start {
  display: flex;
  flex-direction: column;
}

.template-start p {
  margin: -8px 0 14px;
}

.template-pick-block {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(74, 65, 55, 0.12);
}

.project-name-field,
.project-name-strip {
  display: grid;
  gap: 7px;
}

.project-name-field {
  margin-bottom: 12px;
}

.project-name-strip {
  grid-template-columns: 82px minmax(0, 1fr);
  align-items: center;
  margin: -8px 0 14px;
  padding: 12px;
  border: 1px solid rgba(74, 65, 55, 0.12);
  border-radius: 8px;
  background: rgba(255, 252, 247, 0.82);
}

.project-name-field span,
.project-name-strip span {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.project-name-field input,
.project-name-strip input {
  width: 100%;
  min-height: 36px;
  border: 1px solid rgba(74, 65, 55, 0.14);
  border-radius: 5px;
  background: rgba(255, 252, 247, 0.92);
  color: var(--text);
  font-size: 13px;
  font-weight: 750;
  outline: none;
  padding: 0 10px;
  transition: border-color 180ms ease, box-shadow 180ms ease;
}

.project-name-field input:focus,
.project-name-strip input:focus {
  border-color: rgba(139, 94, 52, 0.48);
  box-shadow: 0 0 0 2px rgba(139, 94, 52, 0.08);
}

.template-next {
  width: 100%;
  margin-top: auto;
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

.enabled-import-btn {
  width: 100%;
  min-height: 36px;
  margin-top: 12px;
  border: 1px solid rgba(139, 94, 52, 0.32);
  border-radius: 5px;
  background: rgba(139, 94, 52, 0.12);
  color: var(--earth);
  cursor: pointer;
  font-size: 12px;
  font-weight: 850;
  transition: background 180ms ease, border-color 180ms ease;
}

.enabled-import-btn:hover {
  background: rgba(139, 94, 52, 0.22);
  border-color: rgba(139, 94, 52, 0.48);
}

.studio-grid {
  min-height: 0;
  flex: 1;
  display: grid;
  grid-template-columns: var(--sidebar-wide) minmax(680px, 1fr) var(--sidebar-secondary-wide);
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

.right-tabs {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 3px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 5px;
  background: rgba(246, 243, 235, 0.76);
}

.right-tabs button {
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

.right-tabs button.active {
  background: rgba(139, 94, 52, 0.12);
  color: var(--earth);
}

.right-tabs button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
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

.delivery-dock {
  border-top: 1px solid rgba(74, 65, 55, 0.12);
}

.hidden-file-input {
  position: fixed;
  left: -10000px;
  top: 0;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
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
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-width: 0;
  min-height: 0;
  overflow: auto;
  display: grid;
  place-items: start center;
  height: 100%;
  padding: var(--stage-padding) 20px calc(var(--stage-padding) + 10px);
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
  padding: var(--stage-padding);
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

@media (max-width: 1439px), (max-height: 800px) {
  .studio-grid {
    grid-template-columns: var(--sidebar-compact) minmax(560px, 1fr) var(--sidebar-secondary-compact);
  }

  .product-gallery {
    grid-template-columns: minmax(0, 1fr) 248px;
  }

  .template-layout {
    grid-template-columns: minmax(0, 1fr) 300px;
  }

  .template-card-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1440px) and (max-width: 1679px) and (min-height: 801px) {
  .studio-grid {
    grid-template-columns: var(--sidebar-standard) minmax(620px, 1fr) var(--sidebar-secondary-standard);
  }
}

.source-asset-card {
  margin: -2px 12px 12px;
  padding: 10px 12px;
  border: 1px solid rgba(94, 123, 80, 0.18);
  border-radius: 6px;
  background: rgba(94, 123, 80, 0.07);
}

.source-asset-card span,
.source-asset-card strong,
.source-asset-card small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.source-asset-card span {
  color: var(--leaf);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.source-asset-card strong {
  margin-top: 4px;
  color: var(--text);
  font-size: 12px;
}

.source-asset-card small {
  margin-top: 3px;
  color: var(--text-muted);
  font-size: 11px;
}
</style>
