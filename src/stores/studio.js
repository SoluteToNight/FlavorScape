import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { useProductCases } from '../composables/useProductCases'

const STORAGE_KEY = 'xunwei-studio:v1'
const STORAGE_VERSION = 4
const OUTPUT_TYPES = ['poster', 'archive', 'display']
const DEFAULT_OUTPUT_TYPE = 'poster'
const OUTPUT_LABELS = {
  poster: '海报',
  archive: '白皮书',
  display: '演示',
}
const CONTENT_MODULES = {
  poster: [
    { key: 'mainImage', label: '主图', description: '产品主视觉与图片焦点' },
    { key: 'brandCopy', label: '品牌文案', description: '标题、描述、短句与品牌叙事' },
    { key: 'spatialMap', label: '空间地图', description: '产地空间底板与节点地图' },
    { key: 'evidenceMetrics', label: '证据指标', description: '核心产地和品质指标' },
  ],
  archive: [
    { key: 'originInfo', label: '产地信息', description: '产品、产地与品类信息' },
    { key: 'spatialBase', label: '空间底板', description: '产地地图与空间底板' },
    { key: 'evidenceMetrics', label: '证据指标', description: '核心证明指标' },
    { key: 'nodeLinks', label: '节点链路', description: '空间节点链路说明' },
    { key: 'conclusion', label: '结论说明', description: '报告结论段落' },
  ],
  display: [
    { key: 'productInfo', label: '产品信息', description: '产品标题、副标题和说明' },
    { key: 'evidenceMetrics', label: '证据指标', description: '大屏指标面板' },
    { key: 'spatialNodes', label: '空间节点', description: '产品空间节点卡片' },
    { key: 'routeInteraction', label: '传播路径交互', description: '路径模式、路径选择和时间线交互' },
  ],
}

const PRODUCT_ROUTE_DEFAULTS = {
  'hanyuan-pepper': 'pepper',
  'hotpot-base': 'pepper',
  'wuchang-rice': 'rice',
  'jasmine-tea': 'tea',
  'longjing-tea': 'tea',
}

function nowIso() {
  return new Date().toISOString()
}

function uid(prefix = 'project') {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}

function safeWindow() {
  return typeof window !== 'undefined' ? window : null
}

function defaultTheme(product) {
  return product?.marketing?.creative?.theme?.default || 'nature'
}

function defaultTitle(product) {
  return product?.studio?.brandName || product?.name || '未命名产品'
}

function defaultRouteId(product) {
  return PRODUCT_ROUTE_DEFAULTS[product?.id] || 'tea'
}

function defaultContentModules(type) {
  return Object.fromEntries((CONTENT_MODULES[type] || []).map(item => [item.key, true]))
}

function safeOutputType(type, fallback = null) {
  return OUTPUT_TYPES.includes(type) ? type : fallback
}

function withContentDefaults(type, output, contentConfirmed = false) {
  return {
    ...output,
    contentModules: defaultContentModules(type),
    contentConfirmed,
  }
}

function createPosterDefaults(product) {
  return withContentDefaults('poster', {
    title: null,
    subtitle: null,
    poeticLine: null,
    narrative: null,
    theme: defaultTheme(product),
    customImageDataUrl: null,
    imagePosY: 50,
    updatedAt: null,
  })
}

function createArchiveDefaults(product) {
  return withContentDefaults('archive', {
    title: null,
    summary: null,
    conclusion: null,
    visibleEvidence: null,
    updatedAt: null,
  })
}

function createDisplayDefaults(product) {
  return withContentDefaults('display', {
    title: null,
    subtitle: null,
    caption: null,
    interactionMode: 'route',
    selectedRouteId: defaultRouteId(product),
    selectedEventKey: null,
    showTimeline: true,
    updatedAt: null,
  })
}

function createOutputDefaults(product) {
  return {
    poster: createPosterDefaults(product),
    archive: createArchiveDefaults(product),
    display: createDisplayDefaults(product),
  }
}

function createProjectState(product, initialOutput = null) {
  const createdAt = nowIso()
  const outputType = safeOutputType(initialOutput, DEFAULT_OUTPUT_TYPE)
  return {
    id: uid(),
    name: `${defaultTitle(product)} · ${OUTPUT_LABELS[outputType]}项目`,
    productId: product.id,
    outputType,
    activeOutput: outputType,
    createdAt,
    updatedAt: createdAt,
    outputs: createOutputDefaults(product),
    exports: [],
  }
}

function normalizeProject(project, getById) {
  const product = getById(project?.productId)
  if (!product) return null
  const defaults = createOutputDefaults(product)
  const legacyPoster = project.poster || {}
  const incoming = project.outputs || {}
  const hasLegacyActiveOutput = OUTPUT_TYPES.includes(project.activeOutput)
  const outputType = safeOutputType(project.outputType, hasLegacyActiveOutput ? project.activeOutput : DEFAULT_OUTPUT_TYPE)

  function normalizeOutput(type, value) {
    const confirmed = value?.contentConfirmed ?? (hasLegacyActiveOutput && type === outputType)
    return {
      ...value,
      contentModules: {
        ...defaultContentModules(type),
        ...(value?.contentModules || {}),
      },
      contentConfirmed: Boolean(confirmed),
    }
  }

  return {
    id: project.id || uid(),
    name: project.name || `${defaultTitle(product)} · ${OUTPUT_LABELS[outputType]}项目`,
    productId: product.id,
    outputType,
    activeOutput: outputType,
    createdAt: project.createdAt || nowIso(),
    updatedAt: project.updatedAt || project.createdAt || nowIso(),
    outputs: {
      poster: {
        ...normalizeOutput('poster', {
          ...defaults.poster,
          ...legacyPoster,
          ...(incoming.poster || {}),
        }),
        imagePosY: Number.isFinite(Number(incoming.poster?.imagePosY ?? legacyPoster.imagePosY))
          ? Math.min(100, Math.max(0, Number(incoming.poster?.imagePosY ?? legacyPoster.imagePosY)))
          : 50,
      },
      archive: normalizeOutput('archive', {
        ...defaults.archive,
        ...(incoming.archive || {}),
      }),
      display: normalizeOutput('display', {
        ...defaults.display,
        ...(incoming.display || {}),
        selectedRouteId: incoming.display?.selectedRouteId || defaultRouteId(product),
      }),
    },
    exports: Array.isArray(project.exports) ? project.exports.slice(0, 20) : [],
  }
}

function stripTags(value) {
  return String(value || '').replace(/<[^>]+>/g, '')
}

export const useStudioStore = defineStore('studio', () => {
  const { getById } = useProductCases()

  const projects = ref([])
  const activeProjectId = ref(null)
  const hydrated = ref(false)
  const lastError = ref(null)

  const activeProject = computed(() =>
    projects.value.find(p => p.id === activeProjectId.value) || null
  )

  const activeOutput = computed(() => activeProject.value?.outputType || activeProject.value?.activeOutput || null)

  const activeContentConfirmed = computed(() => {
    const project = activeProject.value
    const type = activeOutput.value
    return Boolean(project && type && project.outputs?.[type]?.contentConfirmed)
  })

  const activeProductCase = computed(() => {
    if (!activeProject.value) return null
    return getById(activeProject.value.productId)
  })

  const outputStatuses = computed(() => {
    const project = activeProject.value
    if (!project) return []
    const type = activeOutput.value
    if (!type) return []
    return [type].map(type => {
      const exported = project.exports?.some(item => item.type === type)
      const edited = Boolean(project.outputs?.[type]?.updatedAt)
      return { type, status: exported ? 'exported' : edited ? 'edited' : 'draft' }
    })
  })

  const projectList = computed(() =>
    projects.value.map(project => ({
      id: project.id,
      name: project.name,
      productId: project.productId,
      productName: getById(project.productId)?.name || '未知产品',
      outputType: project.outputType || project.activeOutput || DEFAULT_OUTPUT_TYPE,
      updatedAt: project.updatedAt,
      exportCount: project.exports?.length || 0,
      isActive: project.id === activeProjectId.value,
      stage: project.exports?.length
        ? 'exported'
        : project.outputs?.[project.outputType || project.activeOutput || DEFAULT_OUTPUT_TYPE]?.updatedAt ? 'editing' : 'draft',
    }))
  )

  const mergedPosterData = computed(() => {
    const project = activeProject.value
    const product = activeProductCase.value
    if (!project || !product) return null

    const creative = product.marketing?.creative || {}
    const poster = project.outputs?.poster || {}
    const modules = poster.contentModules || defaultContentModules('poster')
    const theme = poster.theme || creative.theme?.default || 'nature'
    const spatial = product.marketing?.spatial || { nodes: [], evidence: [] }

    return {
      modules,
      title: modules.brandCopy ? poster.title ?? defaultTitle(product) : defaultTitle(product),
      subtitle: modules.brandCopy ? poster.subtitle ?? creative.desc?.default ?? '' : '',
      poeticLine: modules.brandCopy ? poster.poeticLine ?? creative.poeticLine?.default ?? '' : '',
      narrative: modules.brandCopy ? poster.narrative ?? creative.narrative?.default ?? '' : '',
      theme,
      heroImage: modules.mainImage ? poster.customImageDataUrl || product.heroImage || '' : '',
      imagePosY: poster.imagePosY ?? 50,
      copy: {
        xiaohongshu: modules.brandCopy ? creative.copy?.xiaohongshu?.default || '' : '',
        ecommerce: modules.brandCopy ? creative.copy?.ecommerce?.default || '' : '',
      },
      productName: product.name,
      province: product.province,
      origin: product.origin,
      category: product.category,
      colors: product.colors || {},
      brandScenario: product.studio?.brandScenario || '',
      spatial: {
        ...spatial,
        nodes: modules.spatialMap ? spatial.nodes || [] : [],
        evidence: modules.evidenceMetrics ? spatial.evidence || [] : [],
      },
    }
  })

  const mergedArchiveData = computed(() => {
    const project = activeProject.value
    const product = activeProductCase.value
    const poster = mergedPosterData.value
    if (!project || !product || !poster) return null
    const archive = project.outputs?.archive || {}
    const modules = archive.contentModules || defaultContentModules('archive')
    const evidence = product.marketing?.spatial?.evidence || []
    const visible = archive.visibleEvidence || evidence.map(item => item.label)
    const spatial = product.marketing?.spatial || { nodes: [], evidence: [] }

    return {
      modules,
      title: archive.title ?? `${defaultTitle(product)} · 实证白皮书`,
      summary: archive.summary ?? `${product.origin} 的空间节点、证据指标和品牌叙事被整理为一份可交付的溯源证明材料。`,
      conclusion: modules.conclusion ? archive.conclusion ?? `${defaultTitle(product)} 具备清晰的产地坐标、可解释的供应链节点和可展示的品质凭证。` : '',
      productName: modules.originInfo ? product.name : '',
      province: product.province,
      origin: modules.originInfo ? product.origin : '',
      category: modules.originInfo ? product.category : '',
      colors: product.colors || {},
      spatial: {
        ...spatial,
        nodes: modules.nodeLinks || modules.spatialBase ? spatial.nodes || [] : [],
      },
      evidence: modules.evidenceMetrics ? evidence.filter(item => visible.includes(item.label)) : [],
      allEvidence: evidence,
      posterSubtitle: poster.subtitle,
      narrativeText: stripTags(poster.narrative),
    }
  })

  const mergedDisplayData = computed(() => {
    const project = activeProject.value
    const product = activeProductCase.value
    if (!project || !product) return null
    const display = project.outputs?.display || {}
    const modules = display.contentModules || defaultContentModules('display')
    const spatial = product.marketing?.spatial || { nodes: [], evidence: [] }
    const routeEnabled = modules.routeInteraction !== false
    const mode = routeEnabled ? display.interactionMode || 'product' : 'product'

    return {
      projectId: project.id,
      modules,
      title: modules.productInfo ? display.title ?? `${defaultTitle(product)} · 智慧大屏` : defaultTitle(product),
      subtitle: modules.productInfo ? display.subtitle ?? product.studio?.brandScenario ?? product.category : '',
      caption: modules.productInfo ? display.caption ?? '在产品空间节点大屏中增加传播路径交互，用于同时表达供应链证据与食材历史流动。' : '',
      interactionMode: mode,
      selectedRouteId: display.selectedRouteId || defaultRouteId(product),
      selectedEventKey: display.selectedEventKey,
      showTimeline: display.showTimeline !== false,
      productName: product.name,
      brandName: defaultTitle(product),
      heroImage: product.heroImage || '',
      province: product.province,
      origin: product.origin,
      category: product.category,
      brandScenario: product.studio?.brandScenario || '',
      colors: product.colors || {},
      routeInteractionEnabled: routeEnabled,
      spatial: {
        ...spatial,
        nodes: modules.spatialNodes ? spatial.nodes || [] : [],
        evidence: modules.evidenceMetrics ? spatial.evidence || [] : [],
      },
    }
  })

  function persist() {
    const win = safeWindow()
    if (!win || !hydrated.value) return
    try {
      win.localStorage.setItem(STORAGE_KEY, JSON.stringify({
        version: STORAGE_VERSION,
        activeProjectId: activeProjectId.value,
        projects: projects.value,
      }))
      lastError.value = null
    } catch (e) {
      lastError.value = e?.message || '保存失败'
    }
  }

  function hydrate() {
    if (hydrated.value) return
    const win = safeWindow()
    if (!win) {
      hydrated.value = true
      return
    }

    try {
      const raw = win.localStorage.getItem(STORAGE_KEY)
      if (!raw) {
        hydrated.value = true
        return
      }
      const parsed = JSON.parse(raw)
      const list = Array.isArray(parsed.projects) ? parsed.projects : []
      projects.value = list
        .map(project => normalizeProject(project, getById))
        .filter(Boolean)
      activeProjectId.value = projects.value.some(p => p.id === parsed.activeProjectId)
        ? parsed.activeProjectId
        : projects.value[0]?.id || null
      lastError.value = null
    } catch (e) {
      lastError.value = e?.message || '无法读取本地项目'
      projects.value = []
      activeProjectId.value = null
    } finally {
      hydrated.value = true
    }
  }

  function touchOutput(project, type) {
    const stamp = nowIso()
    project.updatedAt = stamp
    if (project.outputs?.[type]) project.outputs[type].updatedAt = stamp
  }

  function createProject(productId, options = {}) {
    const product = getById(productId)
    if (!product) return null
    const project = createProjectState(product, options.initialOutput)
    projects.value.unshift(project)
    activeProjectId.value = project.id
    return project.id
  }

  function switchProject(id) {
    if (projects.value.some(p => p.id === id)) activeProjectId.value = id
  }

  function setActiveOutput(type) {
    const project = activeProject.value
    if (!project || !OUTPUT_TYPES.includes(type)) return
    if (project.outputType && project.outputType !== type) return
    project.outputType = type
    project.activeOutput = type
  }

  function chooseOutput(type) {
    const project = activeProject.value
    if (!project) return
    if (type === null || !OUTPUT_TYPES.includes(type)) return
    if (project.outputType && project.outputType !== type) return
    project.outputType = type
    project.activeOutput = type
    project.updatedAt = nowIso()
  }

  function updateContentModule(type, key, enabled) {
    const project = activeProject.value
    const output = project?.outputs?.[type]
    if (!output || !CONTENT_MODULES[type]?.some(item => item.key === key)) return
    output.contentModules = {
      ...defaultContentModules(type),
      ...(output.contentModules || {}),
      [key]: Boolean(enabled),
    }
    if (type === 'display' && key === 'routeInteraction' && !enabled) {
      output.interactionMode = 'product'
      output.selectedEventKey = null
    }
    output.contentConfirmed = false
    project.updatedAt = nowIso()
  }

  function confirmContent(type) {
    const project = activeProject.value
    const output = project?.outputs?.[type]
    if (!output) return
    output.contentModules = {
      ...defaultContentModules(type),
      ...(output.contentModules || {}),
    }
    output.contentConfirmed = true
    touchOutput(project, type)
  }

  function renameProject(id, name) {
    const project = projects.value.find(p => p.id === id)
    const next = String(name || '').trim()
    if (!project || !next) return
    project.name = next.slice(0, 40)
    project.updatedAt = nowIso()
  }

  function deleteProject(id) {
    const index = projects.value.findIndex(p => p.id === id)
    if (index === -1) return
    projects.value.splice(index, 1)
    if (activeProjectId.value === id) activeProjectId.value = projects.value[0]?.id || null
  }

  function duplicateProject(id) {
    const source = projects.value.find(p => p.id === id)
    if (!source) return null
    const stamp = nowIso()
    const clone = JSON.parse(JSON.stringify(source))
    clone.id = uid()
    clone.name = `${source.name} 副本`.slice(0, 40)
    clone.createdAt = stamp
    clone.updatedAt = stamp
    clone.exports = []
    projects.value.unshift(clone)
    activeProjectId.value = clone.id
    return clone.id
  }

  function updateOutputField(type, field, value) {
    const project = activeProject.value
    if (!project || !project.outputs?.[type] || !(field in project.outputs[type])) return
    project.outputs[type][field] = value
    touchOutput(project, type)
  }

  function resetOutputField(type, field) {
    const project = activeProject.value
    const product = activeProductCase.value
    if (!project || !product || !project.outputs?.[type] || !(field in project.outputs[type])) return
    const defaults = createOutputDefaults(product)[type]
    project.outputs[type][field] = defaults[field]
    touchOutput(project, type)
  }

  function resetOutput(type) {
    const project = activeProject.value
    const product = activeProductCase.value
    if (!project || !product || !project.outputs?.[type]) return
    project.outputs[type] = createOutputDefaults(product)[type]
    if (activeOutput.value === type) project.outputs[type].contentConfirmed = false
    project.updatedAt = nowIso()
  }

  function updatePosterField(field, value) {
    updateOutputField('poster', field, value)
  }

  function resetPosterField(field) {
    resetOutputField('poster', field)
  }

  function resetPoster() {
    resetOutput('poster')
  }

  function recordExport(type = activeOutput.value, meta = {}) {
    const project = activeProject.value
    if (!project) return
    const record = {
      id: uid('export'),
      type,
      filename: meta.filename || `${type}.png`,
      theme: meta.theme || project.outputs?.poster?.theme || 'nature',
      scale: meta.scale || 2,
      createdAt: nowIso(),
    }
    project.exports.unshift(record)
    project.exports = project.exports.slice(0, 20)
    project.updatedAt = record.createdAt
  }

  function projectSnapshot() {
    const project = activeProject.value
    const product = activeProductCase.value
    if (!project || !product) return null
    return {
      version: STORAGE_VERSION,
      exportedAt: nowIso(),
      project: JSON.parse(JSON.stringify(project)),
      product: JSON.parse(JSON.stringify(product)),
      poster: mergedPosterData.value,
      archive: mergedArchiveData.value,
      display: mergedDisplayData.value,
    }
  }

  function hasAnyProject() {
    return projects.value.length > 0
  }

  hydrate()
  let persistTimer = null
  function debouncedPersist() {
    if (!hydrated.value) return
    clearTimeout(persistTimer)
    persistTimer = setTimeout(() => persist(), 300)
  }
  watch([projects, activeProjectId], debouncedPersist, { deep: true })

  return {
    projects,
    activeProjectId,
    hydrated,
    lastError,
    activeProject,
    activeOutput,
    activeContentConfirmed,
    activeProductCase,
    contentModuleDefinitions: CONTENT_MODULES,
    outputStatuses,
    projectList,
    mergedPosterData,
    mergedArchiveData,
    mergedDisplayData,
    createProject,
    switchProject,
    setActiveOutput,
    chooseOutput,
    updateContentModule,
    confirmContent,
    renameProject,
    deleteProject,
    duplicateProject,
    updateOutputField,
    resetOutputField,
    resetOutput,
    updatePosterField,
    resetPosterField,
    resetPoster,
    recordExport,
    projectSnapshot,
    hasAnyProject,
  }
})
