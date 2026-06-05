import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { useProductCases } from '../composables/useProductCases'
import { applyThemeToLayout, createDefaultElement, createLayout, normalizeLayoutMeta } from '../data/layout-presets'
import { api } from '../utils/api.js'

const UI_STORAGE_KEY = 'xunwei-studio:ui'
const STORAGE_VERSION = 4
const OUTPUT_TYPES = ['poster', 'archive', 'display']
const DEFAULT_OUTPUT_TYPE = 'poster'
const OUTPUT_LABELS = {
  poster: '海报',
  archive: '白皮书',
  display: '演示',
}

const DEFAULT_TEMPLATE_PARAMS = {
  layout: 'balanced',
  palette: 'default',
  density: 'normal',
  imageShape: 'standard',
  metricStyle: 'cards',
  titleScale: 100,
  badgeText: '真实产地 · 空间溯源 · 品牌资产',
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

function inferProvince(value = '') {
  const text = String(value || '')
  const provinces = [
    '北京市', '天津市', '上海市', '重庆市',
    '河北省', '山西省', '辽宁省', '吉林省', '黑龙江省', '江苏省', '浙江省', '安徽省',
    '福建省', '江西省', '山东省', '河南省', '湖北省', '湖南省', '广东省', '海南省',
    '四川省', '贵州省', '云南省', '陕西省', '甘肃省', '青海省', '台湾省',
    '内蒙古自治区', '广西壮族自治区', '西藏自治区', '宁夏回族自治区', '新疆维吾尔自治区',
    '香港特别行政区', '澳门特别行政区',
  ]
  return provinces.find(name => text.includes(name) || text.includes(name.replace(/省|市|自治区|特别行政区/g, ''))) || ''
}

function normalizeTemplateParams(value = {}) {
  const params = { ...DEFAULT_TEMPLATE_PARAMS, ...(value || {}) }
  const options = {
    layout: ['balanced', 'editorial', 'evidence'],
    palette: ['default', 'fresh', 'warm', 'noir'],
    density: ['normal', 'compact', 'airy'],
    imageShape: ['standard', 'arch', 'full'],
    metricStyle: ['cards', 'inline'],
  }
  for (const [key, allowed] of Object.entries(options)) {
    if (!allowed.includes(params[key])) params[key] = DEFAULT_TEMPLATE_PARAMS[key]
  }
  params.titleScale = Number.isFinite(Number(params.titleScale))
    ? Math.min(130, Math.max(82, Number(params.titleScale)))
    : DEFAULT_TEMPLATE_PARAMS.titleScale
  params.badgeText = String(params.badgeText || DEFAULT_TEMPLATE_PARAMS.badgeText).slice(0, 28)
  return params
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
    templateParams: normalizeTemplateParams(),
    customImageDataUrl: null,
    imagePosY: 50,
    layout: null,
    updatedAt: null,
  })
}

function createArchiveDefaults(product) {
  return withContentDefaults('archive', {
    title: null,
    summary: null,
    conclusion: null,
    visibleEvidence: null,
    layout: null,
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
  const hasSourceAsset = project.sourceAsset && typeof project.sourceAsset === 'object'

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

  const normalizedPoster = normalizeOutput('poster', {
    ...defaults.poster,
    ...legacyPoster,
    ...(incoming.poster || {}),
  })
  normalizedPoster.imagePosY = Number.isFinite(Number(incoming.poster?.imagePosY ?? legacyPoster.imagePosY))
    ? Math.min(100, Math.max(0, Number(incoming.poster?.imagePosY ?? legacyPoster.imagePosY)))
    : 50
  normalizedPoster.templateParams = normalizeTemplateParams(incoming.poster?.templateParams || legacyPoster.templateParams)
  normalizedPoster.layout = normalizeLayoutMeta('poster', normalizedPoster.layout, {
    theme: normalizedPoster.theme,
  })

  const normalizedArchive = normalizeOutput('archive', {
    ...defaults.archive,
    ...(incoming.archive || {}),
  })
  normalizedArchive.layout = normalizeLayoutMeta('archive', normalizedArchive.layout)

  return {
    id: project.id || uid(),
    name: project.name || `${defaultTitle(product)} · ${OUTPUT_LABELS[outputType]}项目`,
    productId: product.id,
    outputType,
    activeOutput: outputType,
    createdAt: project.createdAt || nowIso(),
    updatedAt: project.updatedAt || project.createdAt || nowIso(),
    version: project.version || 1,
    _localRevision: project._localRevision || 0,
    outputs: {
      poster: normalizedPoster,
      archive: normalizedArchive,
      display: normalizeOutput('display', {
        ...defaults.display,
        ...(incoming.display || {}),
        selectedRouteId: incoming.display?.selectedRouteId ?? (hasSourceAsset ? null : defaultRouteId(product)),
      }),
    },
    exports: Array.isArray(project.exports) ? project.exports.slice(0, 20) : [],
    sourceAsset: hasSourceAsset ? project.sourceAsset : null,
  }
}

function stripTags(value) {
  return String(value || '').replace(/<[^>]+>/g, '')
}

function sourceAssetPackage(project) {
  const source = project?.sourceAsset
  return source?.assetPackage && typeof source.assetPackage === 'object' ? source.assetPackage : null
}

function isAssetProject(project) {
  return Boolean(sourceAssetPackage(project))
}

function firstAssetText(value, fallback = '') {
  const list = toAssetTextList(value)
  return list[0] || fallback
}

function toAssetTextList(value) {
  if (!Array.isArray(value)) return []
  return value.map(item => {
    if (typeof item === 'string') return item
    if (item && typeof item === 'object') {
      return item.title || item.name || item.label || item.desc || item.description || item.value || ''
    }
    return String(item || '')
  }).filter(Boolean)
}

function assetEvidenceItems(assetPackage, fallback = []) {
  const evidence = assetPackage?.evidence
  const hasAsset = Boolean(assetPackage)
  if (!evidence || typeof evidence !== 'object') return hasAsset ? [] : fallback
  const values = []
  for (const key of ['lab_indicators', 'certifications', 'origin_claims', 'process_steps']) {
    const items = Array.isArray(evidence[key]) ? evidence[key] : []
    for (const item of items) {
      if (typeof item === 'string') {
        continue
      } else if (item && typeof item === 'object') {
        const value = item.value || item.result || item.status
        if (!value) continue
        values.push({
          label: String(item.label || item.name || item.title || '证据').slice(0, 18),
          value: String(value).slice(0, 28),
        })
      }
    }
  }
  return values.length ? values.slice(0, 8) : hasAsset ? [] : fallback
}

function assetSpatialNodes(assetPackage, fallback = []) {
  const nodes = assetPackage?.visualization?.map_nodes
  const hasAsset = Boolean(assetPackage)
  if (!Array.isArray(nodes)) return hasAsset ? [] : fallback
  const normalized = nodes.map((item, index) => {
    if (!item || typeof item !== 'object') return null
    const coord = item.coord || item.coordinates || item.lnglat || (
      (item.lng ?? item.lon ?? item.longitude) !== undefined && (item.lat ?? item.latitude) !== undefined
        ? [item.lng ?? item.lon ?? item.longitude, item.lat ?? item.latitude]
        : null
    )
    if (!Array.isArray(coord) || coord.length < 2) return null
    return {
      short: String(item.short || item.name || item.label || `节点${index + 1}`).slice(0, 10),
      coord: [Number(coord[0]), Number(coord[1])],
      desc: String(item.desc || item.description || item.role || 'AI 资产包空间节点').slice(0, 80),
    }
  }).filter(item => item && item.coord.every(Number.isFinite))
  return normalized.length ? normalized.slice(0, 8) : hasAsset ? [] : fallback
}

function assetUnmappedNodes(assetPackage) {
  const nodes = assetPackage?.visualization?.map_nodes
  if (!Array.isArray(nodes)) return []
  return nodes.map((item, index) => {
    if (typeof item === 'string') return { name: item, reason: '缺少经纬度' }
    if (!item || typeof item !== 'object') return null
    const coord = item.coord || item.coordinates || item.lnglat || (
      (item.lng ?? item.lon ?? item.longitude) !== undefined && (item.lat ?? item.latitude) !== undefined
        ? [item.lng ?? item.lon ?? item.longitude, item.lat ?? item.latitude]
        : null
    )
    if (Array.isArray(coord) && coord.length >= 2 && coord.every(value => Number.isFinite(Number(value)))) return null
    return {
      name: String(item.short || item.name || item.label || `节点${index + 1}`),
      reason: '缺少可投影经纬度',
    }
  }).filter(Boolean).slice(0, 8)
}

function normalizeAssetEvent(item, index) {
  if (!item || typeof item !== 'object') return null
  const coord = item.coord || item.coordinates || item.lnglat || (
    (item.lng ?? item.lon ?? item.longitude) !== undefined && (item.lat ?? item.latitude) !== undefined
      ? [item.lng ?? item.lon ?? item.longitude, item.lat ?? item.latitude]
      : null
  )
  if (!Array.isArray(coord) || coord.length < 2) return null
  const coordinates = [Number(coord[0]), Number(coord[1])]
  if (!coordinates.every(Number.isFinite)) return null
  return {
    year: item.year ?? index + 1,
    dynasty: item.dynasty || item.period || item.stage || '资产节点',
    event_type: item.event_type || item.type || '空间节点',
    location: item.location || item.name || item.label || `节点${index + 1}`,
    coordinates,
    route: item.route || item.desc || item.description || item.summary || '',
    notes: item.notes || item.evidence || item.reason || '',
  }
}

function assetRouteData(assetPackage, fallbackName = 'AI 资产包路线') {
  if (!assetPackage) return null
  const visualization = assetPackage.visualization || {}
  const routes = Array.isArray(visualization.routes) ? visualization.routes : []
  const firstRoute = routes.find(item => item && typeof item === 'object') || null
  const routeEvents = firstRoute
    ? (firstRoute.timeline || firstRoute.events || firstRoute.nodes || firstRoute.points || [])
    : []
  const timelineSource = Array.isArray(routeEvents) && routeEvents.length
    ? routeEvents
    : Array.isArray(visualization.timeline)
      ? visualization.timeline
      : Array.isArray(visualization.map_nodes)
        ? visualization.map_nodes
        : []
  let timeline = timelineSource
    .map((item, index) => normalizeAssetEvent(item, index))
    .filter(Boolean)
  if (!timeline.length && Array.isArray(visualization.map_nodes)) {
    timeline = visualization.map_nodes
      .map((item, index) => normalizeAssetEvent(item, index))
      .filter(Boolean)
  }
  if (!timeline.length) return null
  return {
    id: firstRoute?.id || 'asset-route',
    name: firstRoute?.name || firstRoute?.title || fallbackName,
    summary: firstRoute?.summary || firstRoute?.desc || firstAssetText(assetPackage.brand_assets?.dashboard_cards, 'DeepSeek 资产包生成的空间路线。'),
    color: firstRoute?.color || '#b8d46c',
    timeline,
  }
}

function clone(value) {
  return JSON.parse(JSON.stringify(value))
}

function outputDataForType(type, posterData, archiveData) {
  return type === 'archive' ? archiveData.value : posterData.value
}

export const useStudioStore = defineStore('studio', () => {
  const { getById } = useProductCases()

  const projects = ref([])
  const activeProjectId = ref(null)
  const hydrated = ref(false)
  const remoteLoaded = ref(false)
  const loading = ref(false)
  const lastError = ref(null)
  const syncStatus = ref('idle')
  const lastSyncedAt = ref(null)
  const saveTimers = new Map()
  const selectedElementIds = ref([])
  const layoutHistory = ref({})

  const activeProject = computed(() =>
    projects.value.find(p => p.id === activeProjectId.value) || null
  )

  const activeOutput = computed(() => activeProject.value?.outputType || activeProject.value?.activeOutput || null)

  const activeSourceAsset = computed(() => activeProject.value?.sourceAsset || null)

  const activeLayout = computed(() => {
    const type = activeOutput.value
    return type ? activeProject.value?.outputs?.[type]?.layout || null : null
  })

  const selectedElements = computed(() => {
    const selected = new Set(selectedElementIds.value)
    return (activeLayout.value?.elements || []).filter(element => selected.has(element.id))
  })

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
      productName: sourceAssetPackage(project)?.product?.name || getById(project.productId)?.name || '未知产品',
      outputType: project.outputType || project.activeOutput || DEFAULT_OUTPUT_TYPE,
      updatedAt: project.updatedAt,
      exportCount: project.exports?.length || 0,
      isActive: project.id === activeProjectId.value,
      sourceType: project.sourceAsset?.type || '',
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
    const assetPackage = sourceAssetPackage(project)
    const assetProduct = assetPackage?.product || {}
    const assetBrand = assetPackage?.brand_assets || {}
    const assetProvince = inferProvince(assetProduct.origin || product.origin)
    const baseSpatial = product.marketing?.spatial || { nodes: [], evidence: [] }
    const isAsset = isAssetProject(project)
    const spatial = {
      ...baseSpatial,
      nodes: assetSpatialNodes(assetPackage, baseSpatial.nodes || []),
      evidence: assetEvidenceItems(assetPackage, baseSpatial.evidence || []),
      unmappedNodes: assetUnmappedNodes(assetPackage),
    }
    const productName = assetProduct.name || product.name
    const origin = assetProduct.origin || product.origin
    const category = assetProduct.category || product.category

    return {
      modules,
      title: modules.brandCopy ? poster.title ?? productName ?? defaultTitle(product) : productName,
      subtitle: modules.brandCopy ? poster.subtitle ?? firstAssetText(assetBrand.poster_copy, creative.desc?.default ?? '') : '',
      poeticLine: modules.brandCopy ? poster.poeticLine ?? assetBrand.slogan ?? creative.poeticLine?.default ?? '' : '',
      narrative: modules.brandCopy ? poster.narrative ?? firstAssetText(assetBrand.layout_direction, creative.narrative?.default ?? '') : '',
      theme,
      templateParams: normalizeTemplateParams(poster.templateParams),
      heroImage: modules.mainImage ? poster.customImageDataUrl || product.heroImage || '' : '',
      imagePosY: poster.imagePosY ?? 50,
      copy: {
        xiaohongshu: modules.brandCopy ? firstAssetText(assetBrand.poster_copy, creative.copy?.xiaohongshu?.default || '') : '',
        ecommerce: modules.brandCopy ? assetBrand.slogan || creative.copy?.ecommerce?.default || '' : '',
      },
      productName,
      province: isAsset ? assetProvince : product.province,
      origin,
      category,
      colors: product.colors || {},
      brandScenario: assetBrand.slogan || product.studio?.brandScenario || '',
      sourceAsset: project.sourceAsset || null,
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
    const assetPackage = sourceAssetPackage(project)
    const assetProduct = assetPackage?.product || {}
    const assetBrand = assetPackage?.brand_assets || {}
    const assetProvince = inferProvince(assetProduct.origin || product.origin)
    const isAsset = isAssetProject(project)
    const evidence = assetEvidenceItems(assetPackage, product.marketing?.spatial?.evidence || [])
    const visible = archive.visibleEvidence || evidence.map(item => item.label)
    const baseSpatial = product.marketing?.spatial || { nodes: [], evidence: [] }
    const spatial = {
      ...baseSpatial,
      nodes: assetSpatialNodes(assetPackage, baseSpatial.nodes || []),
      evidence,
      unmappedNodes: assetUnmappedNodes(assetPackage),
    }
    const productName = assetProduct.name || product.name

    return {
      modules,
      title: archive.title ?? `${productName} · 实证白皮书`,
      summary: archive.summary ?? firstAssetText(assetBrand.whitepaper_outline, `${assetProduct.origin || product.origin} 的空间节点、证据指标和品牌叙事被整理为一份可交付的溯源证明材料。`),
      conclusion: modules.conclusion ? archive.conclusion ?? firstAssetText(assetPackage?.next_actions, `${productName} 具备清晰的产地坐标、可解释的供应链节点和可展示的品质凭证。`) : '',
      productName: modules.originInfo ? productName : '',
      province: isAsset ? assetProvince : product.province,
      origin: modules.originInfo ? assetProduct.origin || product.origin : '',
      category: modules.originInfo ? assetProduct.category || product.category : '',
      colors: product.colors || {},
      sourceAsset: project.sourceAsset || null,
      citations: assetPackage?.citations || [],
      reviewStatus: assetPackage?.review_status || project.sourceAsset?.reviewStatus || null,
      spatial: {
        ...spatial,
        nodes: modules.nodeLinks || modules.spatialBase ? spatial.nodes || [] : [],
        unmappedNodes: spatial.unmappedNodes || [],
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
    const assetPackage = sourceAssetPackage(project)
    const assetProduct = assetPackage?.product || {}
    const assetBrand = assetPackage?.brand_assets || {}
    const isAsset = isAssetProject(project)
    const assetProvince = inferProvince(assetProduct.origin || product.origin)
    const customRoute = assetRouteData(assetPackage, `${assetProduct.name || product.name}空间路线`)
    const baseSpatial = product.marketing?.spatial || { nodes: [], evidence: [] }
    const spatial = {
      ...baseSpatial,
      nodes: assetSpatialNodes(assetPackage, baseSpatial.nodes || []),
      evidence: assetEvidenceItems(assetPackage, baseSpatial.evidence || []),
      unmappedNodes: assetUnmappedNodes(assetPackage),
    }
    const routeEnabled = modules.routeInteraction !== false
    const mode = routeEnabled ? display.interactionMode || (customRoute ? 'route' : 'product') : 'product'
    const productName = assetProduct.name || product.name
    const origin = assetProduct.origin || product.origin
    const category = assetProduct.category || product.category

    return {
      projectId: project.id,
      modules,
      title: modules.productInfo ? display.title ?? `${productName} · 智慧大屏` : productName,
      subtitle: modules.productInfo ? display.subtitle ?? assetBrand.slogan ?? product.studio?.brandScenario ?? category : '',
      caption: modules.productInfo ? display.caption ?? firstAssetText(assetBrand.dashboard_cards, '在产品空间节点大屏中增加传播路径交互，用于同时表达供应链证据与食材历史流动。') : '',
      interactionMode: mode,
      selectedRouteId: customRoute ? customRoute.id : isAsset ? null : display.selectedRouteId || defaultRouteId(product),
      selectedEventKey: display.selectedEventKey,
      showTimeline: display.showTimeline !== false,
      productName,
      brandName: productName,
      heroImage: product.heroImage || '',
      province: isAsset ? assetProvince : product.province,
      origin,
      category,
      brandScenario: assetBrand.slogan || product.studio?.brandScenario || '',
      colors: product.colors || {},
      sourceAsset: project.sourceAsset || null,
      assetRouteData: customRoute,
      assetRouteOptions: customRoute ? [{ id: customRoute.id, name: customRoute.name, eventCount: customRoute.timeline.length }] : [],
      needsSpatialData: isAsset && !spatial.nodes.length && !customRoute,
      routeInteractionEnabled: routeEnabled,
      spatial: {
        ...spatial,
        nodes: modules.spatialNodes ? spatial.nodes || [] : [],
        evidence: modules.evidenceMetrics ? spatial.evidence || [] : [],
      },
    }
  })

  function saveUiState() {
    const win = safeWindow()
    if (!win || !hydrated.value) return
    try {
      win.localStorage.setItem(UI_STORAGE_KEY, JSON.stringify({
        version: STORAGE_VERSION,
        activeProjectId: activeProjectId.value,
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
      const ui = JSON.parse(win.localStorage.getItem(UI_STORAGE_KEY) || '{}')
      activeProjectId.value = ui.activeProjectId || null

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

  function projectPayload(project) {
    const payload = JSON.parse(JSON.stringify(project))
    delete payload._localRevision
    return payload
  }

  function applyServerProject(project) {
    const normalized = normalizeProject(project, getById)
    if (!normalized) return null
    normalized.version = project.version || normalized.version || 1
    const index = projects.value.findIndex(item => item.id === normalized.id)
    if (index === -1) projects.value.unshift(normalized)
    else projects.value[index] = normalized
    lastSyncedAt.value = nowIso()
    syncStatus.value = 'saved'
    lastError.value = null
    return normalized
  }

  function applyServerMetadata(id, serverProject) {
    const project = projects.value.find(item => item.id === id)
    if (!project) return null
    project.version = serverProject.version || project.version || 1
    project.createdAt = serverProject.createdAt || project.createdAt
    project.updatedAt = serverProject.updatedAt || project.updatedAt
    lastSyncedAt.value = nowIso()
    syncStatus.value = 'saved'
    lastError.value = null
    return project
  }

  function markDirty(project) {
    if (!project) return
    project._localRevision = (project._localRevision || 0) + 1
  }

  function markLayoutDirty(project, type, options = {}) {
    touchOutput(project, type)
    markDirty(project)
    if (options.history !== false) pushLayoutHistory(project.id, type)
    scheduleSave(project)
  }

  function scheduleSave(project) {
    if (!project?.id || !remoteLoaded.value) return
    syncStatus.value = 'saving'
    clearTimeout(saveTimers.get(project.id))
    saveTimers.set(project.id, setTimeout(() => saveProject(project.id), 600))
  }

  async function saveProject(id) {
    const project = projects.value.find(item => item.id === id)
    if (!project?.version) return
    const revisionAtSend = project._localRevision || 0
    syncStatus.value = 'saving'
    try {
      const res = await api(`/api/studio/projects/${encodeURIComponent(id)}`, {
        method: 'PATCH',
        body: JSON.stringify({
          version: project.version,
          project: projectPayload(project),
        }),
      })
      if (!res.ok) throw new Error(res.error || '项目保存失败')
      const current = projects.value.find(item => item.id === id)
      if (current && (current._localRevision || 0) !== revisionAtSend) {
        applyServerMetadata(id, res.data.project)
        scheduleSave(current)
      } else {
        applyServerProject(res.data.project)
      }
    } catch (e) {
      syncStatus.value = 'error'
      lastError.value = e?.message || '项目保存失败'
    }
  }

  async function loadRemoteProjects() {
    if (loading.value) return
    loading.value = true
    syncStatus.value = 'loading'
    try {
      const res = await api('/api/studio/projects')
      if (!res.ok) throw new Error(res.error || '项目加载失败')
      projects.value = Array.isArray(res.data.projects)
        ? res.data.projects.map(project => normalizeProject(project, getById)).filter(Boolean).map(project => {
          const source = res.data.projects.find(item => item.id === project.id)
          return { ...project, version: source?.version || 1 }
        })
        : []
      activeProjectId.value = projects.value.some(project => project.id === activeProjectId.value)
        ? activeProjectId.value
        : projects.value[0]?.id || null
      remoteLoaded.value = true
      syncStatus.value = 'saved'
      lastSyncedAt.value = nowIso()
      lastError.value = null
    } catch (e) {
      syncStatus.value = 'error'
      lastError.value = e?.message || '项目加载失败'
    } finally {
      loading.value = false
    }
  }

  async function loadProject(id) {
    if (!id) return null
    const existing = projects.value.find(project => project.id === id)
    if (existing) {
      remoteLoaded.value = true
      activeProjectId.value = id
      return existing
    }
    try {
      const res = await api(`/api/studio/projects/${encodeURIComponent(id)}`)
      if (!res.ok) throw new Error(res.error || '项目加载失败')
      const project = applyServerProject(res.data.project)
      remoteLoaded.value = true
      if (project) activeProjectId.value = project.id
      return project
    } catch (e) {
      lastError.value = e?.message || '项目加载失败'
      syncStatus.value = 'error'
      return null
    }
  }

  function createProject(productId, options = {}) {
    const product = getById(productId)
    if (!product) return null
    const project = createProjectState(product, options.initialOutput)
    const customName = String(options.name || '').trim()
    if (customName) project.name = customName.slice(0, 40)
    project._localRevision = 0
    projects.value.unshift(project)
    activeProjectId.value = project.id
    const revisionAtSend = project._localRevision || 0
    syncStatus.value = 'saving'
    api('/api/studio/projects', {
      method: 'POST',
      body: JSON.stringify({ project: projectPayload(project) }),
    }).then(res => {
      if (!res.ok) throw new Error(res.error || '项目创建失败')
      const current = projects.value.find(item => item.id === project.id)
      if (current && (current._localRevision || 0) !== revisionAtSend) {
        applyServerMetadata(project.id, res.data.project)
        scheduleSave(current)
      } else {
        applyServerProject(res.data.project)
      }
    }).catch(e => {
      syncStatus.value = 'error'
      lastError.value = e?.message || '项目创建失败'
    })
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
    project.updatedAt = nowIso()
    markDirty(project)
    scheduleSave(project)
  }

  function chooseOutput(type) {
    const project = activeProject.value
    if (!project) return
    if (type === null || !OUTPUT_TYPES.includes(type)) return
    if (project.outputType && project.outputType !== type) return
    project.outputType = type
    project.activeOutput = type
    project.updatedAt = nowIso()
    markDirty(project)
    scheduleSave(project)
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
    markDirty(project)
    scheduleSave(project)
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
    markDirty(project)
    scheduleSave(project)
  }

  function renameProject(id, name) {
    const project = projects.value.find(p => p.id === id)
    const next = String(name || '').trim()
    if (!project || !next) return
    project.name = next.slice(0, 40)
    project.updatedAt = nowIso()
    markDirty(project)
    scheduleSave(project)
  }

  function deleteProject(id) {
    const index = projects.value.findIndex(p => p.id === id)
    if (index === -1) return
    const project = projects.value[index]
    projects.value.splice(index, 1)
    if (activeProjectId.value === id) activeProjectId.value = projects.value[0]?.id || null
    if (project.version) {
      api(`/api/studio/projects/${encodeURIComponent(id)}`, { method: 'DELETE' }).catch(e => {
        lastError.value = e?.message || '项目删除失败'
        syncStatus.value = 'error'
      })
    }
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
    clone.version = null
    clone._localRevision = 0
    clone.exports = []
    projects.value.unshift(clone)
    activeProjectId.value = clone.id
    const revisionAtSend = clone._localRevision || 0
    syncStatus.value = 'saving'
    api('/api/studio/projects', {
      method: 'POST',
      body: JSON.stringify({ project: projectPayload(clone) }),
    }).then(res => {
      if (!res.ok) throw new Error(res.error || '项目复制失败')
      const current = projects.value.find(item => item.id === clone.id)
      if (current && (current._localRevision || 0) !== revisionAtSend) {
        applyServerMetadata(clone.id, res.data.project)
        scheduleSave(current)
      } else {
        applyServerProject(res.data.project)
      }
    }).catch(e => {
      syncStatus.value = 'error'
      lastError.value = e?.message || '项目复制失败'
    })
    return clone.id
  }

  function updateOutputField(type, field, value) {
    const project = activeProject.value
    if (!project || !project.outputs?.[type] || !(field in project.outputs[type])) return
    project.outputs[type][field] = value
    touchOutput(project, type)
    markDirty(project)
    scheduleSave(project)
  }

  function isFreeLayout(type = activeOutput.value) {
    return Boolean(activeProject.value?.outputs?.[type]?.layout)
  }

  function historyKey(projectId, type) {
    return `${projectId}:${type}`
  }

  function ensureLayoutHistory(projectId, type) {
    const key = historyKey(projectId, type)
    if (!layoutHistory.value[key]) {
      layoutHistory.value[key] = { stack: [], index: -1 }
    }
    return layoutHistory.value[key]
  }

  function pushLayoutHistory(projectId, type) {
    const project = projects.value.find(item => item.id === projectId)
    const layout = project?.outputs?.[type]?.layout
    if (!project || !layout) return
    const history = ensureLayoutHistory(projectId, type)
    const snapshot = clone(layout)
    const current = history.stack[history.index]
    if (current && JSON.stringify(current) === JSON.stringify(snapshot)) return
    history.stack = history.stack.slice(0, history.index + 1)
    history.stack.push(snapshot)
    if (history.stack.length > 50) history.stack.shift()
    history.index = history.stack.length - 1
  }

  function restoreLayoutHistory(direction) {
    const project = activeProject.value
    const type = activeOutput.value
    if (!project || !type) return
    const history = ensureLayoutHistory(project.id, type)
    const nextIndex = history.index + direction
    if (nextIndex < 0 || nextIndex >= history.stack.length) return
    history.index = nextIndex
    project.outputs[type].layout = clone(history.stack[history.index])
    selectedElementIds.value = selectedElementIds.value.filter(id =>
      project.outputs[type].layout.elements.some(element => element.id === id)
    )
    touchOutput(project, type)
    markDirty(project)
    scheduleSave(project)
  }

  function undoLayout() {
    restoreLayoutHistory(-1)
  }

  function redoLayout() {
    restoreLayoutHistory(1)
  }

  function setSelectedElementIds(ids) {
    selectedElementIds.value = Array.from(new Set(ids || []))
  }

  function initLayout(type = activeOutput.value, options = {}) {
    const project = activeProject.value
    if (!project || !project.outputs?.[type]) return null
    const data = outputDataForType(type, mergedPosterData, mergedArchiveData)
    if (!data) return null
    const themeId = options.themeId || project.outputs.poster?.theme || data.theme || 'nature'
    project.outputs[type].layout = createLayout(type, data, {
      templateId: options.templateId,
      presetId: options.presetId,
      themeId,
    })
    if (type === 'poster') project.outputs.poster.theme = themeId
    selectedElementIds.value = []
    markLayoutDirty(project, type)
    return project.outputs[type].layout
  }

  function clearLayout(type = activeOutput.value) {
    const project = activeProject.value
    if (!project?.outputs?.[type]) return
    project.outputs[type].layout = null
    selectedElementIds.value = []
    touchOutput(project, type)
    markDirty(project)
    scheduleSave(project)
  }

  function updateLayout(type = activeOutput.value, patch = {}, options = {}) {
    const project = activeProject.value
    const layout = project?.outputs?.[type]?.layout
    if (!project || !layout) return
    project.outputs[type].layout = { ...layout, ...patch }
    markLayoutDirty(project, type, options)
  }

  function updateLayoutTheme(type = activeOutput.value, themeId = 'nature') {
    const project = activeProject.value
    const layout = project?.outputs?.[type]?.layout
    if (!project || !layout) return
    project.outputs[type].layout = applyThemeToLayout(layout, themeId, layout.themeOverrides || {})
    if (type === 'poster') project.outputs.poster.theme = themeId
    markLayoutDirty(project, type)
  }

  function addElement(type = activeOutput.value, elementType = 'text', options = {}) {
    const project = activeProject.value
    const layout = project?.outputs?.[type]?.layout
    const data = outputDataForType(type, mergedPosterData, mergedArchiveData)
    if (!project || !layout || !data) return null
    const element = createDefaultElement(elementType, layout, data, options)
    layout.elements.push(element)
    selectedElementIds.value = [element.id]
    markLayoutDirty(project, type)
    return element.id
  }

  function updateElement(type = activeOutput.value, elementId, patch = {}, options = {}) {
    const project = activeProject.value
    const layout = project?.outputs?.[type]?.layout
    if (!project || !layout || !elementId) return
    const element = layout.elements.find(item => item.id === elementId)
    if (!element) return
    Object.assign(element, patch)
    if (options.detachTheme !== false) {
      element._themeSlots = (element._themeSlots || []).filter(key => !(key in patch))
    }
    markLayoutDirty(project, type, options)
  }

  function updateElements(type = activeOutput.value, patches = [], options = {}) {
    const project = activeProject.value
    const layout = project?.outputs?.[type]?.layout
    if (!project || !layout || !Array.isArray(patches)) return
    patches.forEach(({ id, patch }) => {
      const element = layout.elements.find(item => item.id === id)
      if (!element) return
      Object.assign(element, patch)
      if (options.detachTheme !== false) {
        element._themeSlots = (element._themeSlots || []).filter(key => !(key in patch))
      }
    })
    markLayoutDirty(project, type, options)
  }

  function removeElements(type = activeOutput.value, ids = selectedElementIds.value) {
    const project = activeProject.value
    const layout = project?.outputs?.[type]?.layout
    if (!project || !layout) return
    const removeSet = new Set(ids)
    layout.elements = layout.elements.filter(element => !removeSet.has(element.id) || element.locked)
    selectedElementIds.value = selectedElementIds.value.filter(id => !removeSet.has(id))
    markLayoutDirty(project, type)
  }

  function duplicateSelectedElements(type = activeOutput.value) {
    const project = activeProject.value
    const layout = project?.outputs?.[type]?.layout
    if (!project || !layout || !selectedElementIds.value.length) return
    const selected = new Set(selectedElementIds.value)
    const clones = layout.elements
      .filter(element => selected.has(element.id) && !element.locked)
      .map(element => ({
        ...clone(element),
        id: uid('el'),
        x: Math.min(layout.width - element.w, element.x + 20),
        y: Math.min(layout.height - element.h, element.y + 20),
        zIndex: Math.max(0, ...(layout.elements || []).map(item => item.zIndex || 0)) + 10,
      }))
    layout.elements.push(...clones)
    selectedElementIds.value = clones.map(element => element.id)
    markLayoutDirty(project, type)
  }

  function reorderElement(type = activeOutput.value, elementId, action = 'front') {
    const project = activeProject.value
    const layout = project?.outputs?.[type]?.layout
    if (!project || !layout) return
    const element = layout.elements.find(item => item.id === elementId)
    if (!element) return
    const ordered = [...layout.elements].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
    const min = Math.min(...ordered.map(item => item.zIndex || 0))
    const max = Math.max(...ordered.map(item => item.zIndex || 0))
    if (action === 'front') element.zIndex = max + 10
    if (action === 'back') element.zIndex = min - 10
    if (action === 'up') element.zIndex = (element.zIndex || 0) + 10
    if (action === 'down') element.zIndex = (element.zIndex || 0) - 10
    markLayoutDirty(project, type)
  }

  function resetOutputField(type, field) {
    const project = activeProject.value
    const product = activeProductCase.value
    if (!project || !product || !project.outputs?.[type] || !(field in project.outputs[type])) return
    const defaults = createOutputDefaults(product)[type]
    project.outputs[type][field] = defaults[field]
    touchOutput(project, type)
    markDirty(project)
    scheduleSave(project)
  }

  function resetOutput(type) {
    const project = activeProject.value
    const product = activeProductCase.value
    if (!project || !product || !project.outputs?.[type]) return
    project.outputs[type] = createOutputDefaults(product)[type]
    if (activeOutput.value === type) project.outputs[type].contentConfirmed = false
    project.updatedAt = nowIso()
    markDirty(project)
    scheduleSave(project)
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
    markDirty(project)
    scheduleSave(project)
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
  watch(activeProjectId, () => saveUiState())

  return {
    projects,
    activeProjectId,
    hydrated,
    remoteLoaded,
    loading,
    lastError,
    syncStatus,
    lastSyncedAt,
    activeProject,
    activeOutput,
    activeLayout,
    activeContentConfirmed,
    activeProductCase,
    activeSourceAsset,
    contentModuleDefinitions: CONTENT_MODULES,
    outputStatuses,
    projectList,
    mergedPosterData,
    mergedArchiveData,
    mergedDisplayData,
    selectedElementIds,
    selectedElements,
    loadRemoteProjects,
    loadProject,
    saveProject,
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
    isFreeLayout,
    initLayout,
    clearLayout,
    updateLayout,
    updateLayoutTheme,
    addElement,
    updateElement,
    updateElements,
    removeElements,
    duplicateSelectedElements,
    reorderElement,
    undoLayout,
    redoLayout,
    setSelectedElementIds,
    updatePosterField,
    resetPosterField,
    resetPoster,
    recordExport,
    projectSnapshot,
    hasAnyProject,
  }
})
