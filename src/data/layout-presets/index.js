import { getTheme, resolveToken } from '../themes'

const CANVAS_PRESETS = {
  poster: [
    { id: 'poster-440x860', name: '经典竖版', width: 440, height: 860, ratio: '9:18', group: '印刷' },
    { id: 'poster-600x900', name: '大竖版', width: 600, height: 900, ratio: '2:3', group: '印刷' },
    { id: 'poster-1080x1350', name: '社媒竖图', width: 1080, height: 1350, ratio: '4:5', group: '社媒' },
    { id: 'poster-1080x1080', name: '方形社媒', width: 1080, height: 1080, ratio: '1:1', group: '社媒' },
    { id: 'poster-1080x1920', name: '故事长图', width: 1080, height: 1920, ratio: '9:16', group: '社媒' },
    { id: 'poster-1200x628', name: '信息流横图', width: 1200, height: 628, ratio: '1.91:1', group: '社媒' },
    { id: 'poster-1200x600', name: '横版 Banner', width: 1200, height: 600, ratio: '2:1', group: '传播' },
  ],
  archive: [
    { id: 'archive-760x1040', name: '经典白皮书', width: 760, height: 1040, ratio: '19:26', group: '报告' },
    { id: 'archive-a4', name: 'A4 竖版', width: 595, height: 842, ratio: 'A4', group: '印刷' },
    { id: 'archive-a4-landscape', name: 'A4 横版', width: 842, height: 595, ratio: 'A4', group: '演示' },
    { id: 'archive-1200x800', name: '横版宽幅', width: 1200, height: 800, ratio: '3:2', group: '演示' },
    { id: 'archive-1600x900', name: '16:9 简报', width: 1600, height: 900, ratio: '16:9', group: '演示' },
  ],
}

const TEMPLATE_LIBRARY = {
  poster: [
    {
      id: 'poster-classic-modern',
      name: '经典现代',
      description: '原有经典海报模板化版本，主图、标题、故事和证据指标均衡呈现。',
      tags: ['经典', '品牌传播', '竖版'],
      recommendedPresetId: 'poster-440x860',
      recommendedThemeId: 'nature',
      tone: '稳妥清晰',
      family: 'classic',
    },
    {
      id: 'poster-heritage-vertical',
      name: '东方竖排',
      description: '把经典传承视觉转成自由布局，适合地域符号、老字号和礼盒物料。',
      tags: ['东方', '礼盒', '印刷'],
      recommendedPresetId: 'poster-600x900',
      recommendedThemeId: 'heritage',
      tone: '克制叙事',
      family: 'heritage',
    },
    {
      id: 'poster-indigo-cyanotype',
      name: '靛蓝拓印',
      description: '深色拓印质感模板，突出空间证据、地图和冷调专业感。',
      tags: ['深色', '地图', '质感'],
      recommendedPresetId: 'poster-1080x1350',
      recommendedThemeId: 'indigo',
      tone: '专业冷静',
      family: 'indigo',
    },
    {
      id: 'poster-hero-cover',
      name: '主图封面',
      description: '大面积产品图搭配强标题，适合社媒首图、活动 KV 和招商封面。',
      tags: ['主视觉', '社媒', '强标题'],
      recommendedPresetId: 'poster-1080x1350',
      recommendedThemeId: 'nature',
      tone: '直接有力',
      family: 'hero',
    },
    {
      id: 'poster-map-led',
      name: '地图主视觉',
      description: '以产地空间和节点关系作为主角，适合强调地理背书和溯源链路。',
      tags: ['地图', '溯源', '节点'],
      recommendedPresetId: 'poster-1080x1080',
      recommendedThemeId: 'indigo',
      tone: '证据导向',
      family: 'map',
    },
    {
      id: 'poster-evidence-grid',
      name: '证据网格',
      description: '用指标和短文案构成栅格，适合检测报告提炼和电商详情入口。',
      tags: ['指标', '网格', '电商'],
      recommendedPresetId: 'poster-1080x1080',
      recommendedThemeId: 'nature',
      tone: '理性可信',
      family: 'grid',
    },
    {
      id: 'poster-editorial-split',
      name: '图文分栏',
      description: '图片和文本左右分区，适合横版渠道、PPT 封面和品牌长图局部。',
      tags: ['分栏', '横版', '编辑感'],
      recommendedPresetId: 'poster-1200x628',
      recommendedThemeId: 'heritage',
      tone: '杂志编辑',
      family: 'split',
    },
    {
      id: 'poster-banner-route',
      name: '横幅传播',
      description: '为横幅广告和展陈屏幕准备，标题、主图和证据横向展开。',
      tags: ['Banner', '展陈', '横版'],
      recommendedPresetId: 'poster-1200x600',
      recommendedThemeId: 'nature',
      tone: '快速识别',
      family: 'banner',
    },
    {
      id: 'poster-blank',
      name: '空白画布',
      description: '只创建尺寸和主题，不生成任何元素，适合完全自由设计。',
      tags: ['空白', '自由设计'],
      recommendedPresetId: 'poster-1080x1350',
      recommendedThemeId: 'nature',
      tone: '从零开始',
      family: 'blank',
    },
  ],
  archive: [
    {
      id: 'archive-classic-dossier',
      name: '经典实证',
      description: '原有白皮书模板化版本，摘要、地图、指标、链路和结论完整保留。',
      tags: ['经典', '实证', '竖版'],
      recommendedPresetId: 'archive-760x1040',
      recommendedThemeId: 'nature',
      tone: '完整报告',
      family: 'classic',
    },
    {
      id: 'archive-map-evidence',
      name: '地图证据页',
      description: '地图占据主体，右侧承载指标和节点说明，适合溯源证明单页。',
      tags: ['地图', '证据', '单页'],
      recommendedPresetId: 'archive-a4',
      recommendedThemeId: 'indigo',
      tone: '空间背书',
      family: 'map',
    },
    {
      id: 'archive-two-column-report',
      name: '双栏报告',
      description: '传统报告双栏阅读结构，适合招商材料、资料包和打印交付。',
      tags: ['双栏', '印刷', '报告'],
      recommendedPresetId: 'archive-a4',
      recommendedThemeId: 'heritage',
      tone: '严谨阅读',
      family: 'columns',
    },
    {
      id: 'archive-metric-led',
      name: '指标优先',
      description: '把证据指标前置为主视觉，适合检测结论和卖点说明页。',
      tags: ['指标', '结论', '可信'],
      recommendedPresetId: 'archive-760x1040',
      recommendedThemeId: 'nature',
      tone: '结论先行',
      family: 'metrics',
    },
    {
      id: 'archive-cover-summary',
      name: '封面摘要',
      description: '白皮书封面式结构，适合项目首页、PDF 封面和汇报起始页。',
      tags: ['封面', '摘要', 'PDF'],
      recommendedPresetId: 'archive-a4',
      recommendedThemeId: 'heritage',
      tone: '正式交付',
      family: 'cover',
    },
    {
      id: 'archive-landscape-brief',
      name: '横版简报',
      description: '适配横版演示和会议屏幕，地图、指标、结论同屏展示。',
      tags: ['16:9', '汇报', '横版'],
      recommendedPresetId: 'archive-1600x900',
      recommendedThemeId: 'indigo',
      tone: '汇报友好',
      family: 'landscape',
    },
    {
      id: 'archive-blank',
      name: '空白画布',
      description: '只创建报告画布和主题，不生成内容元素。',
      tags: ['空白', '自由设计'],
      recommendedPresetId: 'archive-a4',
      recommendedThemeId: 'nature',
      tone: '从零开始',
      family: 'blank',
    },
  ],
}

export function canvasPresetOptions(type) {
  return CANVAS_PRESETS[type] || []
}

export function templateOptions(type) {
  return TEMPLATE_LIBRARY[type] || []
}

export function getTemplate(type, templateId) {
  return templateOptions(type).find(item => item.id === templateId) || templateOptions(type)[0]
}

export function defaultTemplateId(type) {
  return templateOptions(type)[0]?.id || 'poster-classic-modern'
}

export function defaultPresetId(type, templateId = null) {
  const template = templateId ? getTemplate(type, templateId) : null
  return template?.recommendedPresetId || canvasPresetOptions(type)[0]?.id || 'poster-440x860'
}

export function inferTemplateId(type, layout = null, data = null) {
  if (layout?.templateId) return layout.templateId
  if (type === 'archive') return 'archive-classic-dossier'
  const themeId = layout?.themeId || data?.theme
  if (themeId === 'heritage') return 'poster-heritage-vertical'
  if (themeId === 'indigo') return 'poster-indigo-cyanotype'
  return 'poster-classic-modern'
}

export function createLayout(type, data, options = {}) {
  const templateId = options.templateId || (options.blank ? `${type}-blank` : inferTemplateId(type, null, data))
  const template = getTemplate(type, templateId)
  const presetId = options.presetId || template?.recommendedPresetId || defaultPresetId(type)
  const preset = canvasPresetOptions(type).find(item => item.id === presetId) || canvasPresetOptions(type)[0]
  const themeId = options.themeId || template?.recommendedThemeId || data?.theme || 'nature'
  const theme = getTheme(themeId)

  return {
    version: 1,
    templateId: template.id,
    templateName: template.name,
    presetId: preset.id,
    width: preset.width,
    height: preset.height,
    backgroundColor: theme.canvas.backgroundColor,
    themeId,
    themeOverrides: {},
    elements: template.family === 'blank' ? [] : createTemplateElements(type, template, preset, data, theme),
  }
}

export function normalizeLayoutMeta(type, layout, data = null) {
  if (!layout) return layout
  const preset = canvasPresetOptions(type).find(item => item.id === layout.presetId)
  const templateId = inferTemplateId(type, layout, data)
  const template = getTemplate(type, templateId)
  return {
    ...layout,
    templateId,
    templateName: layout.templateName || template?.name,
    width: Number(layout.width) || preset?.width || layout.width,
    height: Number(layout.height) || preset?.height || layout.height,
  }
}

export function applyThemeToLayout(layout, themeId, overrides = {}) {
  const theme = getTheme(themeId, overrides)
  const next = {
    ...layout,
    themeId,
    themeOverrides: overrides,
    backgroundColor: theme.canvas.backgroundColor,
    elements: (layout.elements || []).map(element => applyThemeToElement(element, theme)),
  }
  return next
}

export function applyThemeToElement(element, theme) {
  const next = { ...element }
  Object.entries(next._themeRefs || {}).forEach(([key, ref]) => {
    if ((next._themeSlots || []).includes(key)) next[key] = resolveToken(theme, ref, next[key])
  })
  if (Array.isArray(next.children)) next.children = next.children.map(child => applyThemeToElement(child, theme))
  return next
}

export function createDefaultElement(type, layout, data, options = {}) {
  const theme = getTheme(layout?.themeId || data?.theme || 'nature', layout?.themeOverrides)
  const cx = Number.isFinite(Number(options.x)) ? Number(options.x) : Math.max(20, Math.round((layout?.width || 440) / 2 - 90))
  const cy = Number.isFinite(Number(options.y)) ? Number(options.y) : Math.max(20, Math.round((layout?.height || 860) / 2 - 42))
  const base = baseElement(layout, { x: cx, y: cy, w: 180, h: 64, zIndex: nextZIndex(layout) })
  const evidence = data?.spatial?.evidence || data?.evidence || []
  const nodes = data?.spatial?.nodes || []
  const map = {
    text: themed({
      ...base,
      type: 'text',
      content: '新的文本',
      fontSize: 22,
      fontFamily: resolveToken(theme, 'typography.titleFont'),
      fontWeight: 700,
      fontStyle: 'normal',
      color: resolveToken(theme, 'colors.primary'),
      textAlign: 'left',
      lineHeight: 1.3,
      letterSpacing: 0,
    }, { fontFamily: 'typography.titleFont', color: 'colors.primary' }),
    image: {
      ...base,
      type: 'image',
      w: 220,
      h: 160,
      src: data?.heroImage || '',
      objectFit: 'cover',
      objectPositionX: 50,
      objectPositionY: data?.imagePosY ?? 50,
      borderRadius: 12,
    },
    badge: themed({
      ...base,
      type: 'badge',
      w: 150,
      h: 30,
      content: '空间溯源',
      style: 'tag',
      color: resolveToken(theme, 'colors.primary'),
      bgColor: 'transparent',
    }, { color: 'colors.primary' }),
    divider: themed({
      ...base,
      type: 'divider',
      w: 180,
      h: 12,
      style: 'solid',
      color: resolveToken(theme, 'colors.primary'),
      thickness: 1,
    }, { color: 'colors.primary' }),
    shape: themed({
      ...base,
      type: 'shape',
      w: 120,
      h: 120,
      shape: 'rect',
      fill: resolveToken(theme, 'colors.paper'),
      stroke: resolveToken(theme, 'colors.primary'),
      borderRadius: 18,
    }, { fill: 'colors.paper', stroke: 'colors.primary' }),
    mapBlock: themed({
      ...base,
      type: 'mapBlock',
      w: 210,
      h: 180,
      province: data?.province || '',
      nodes: data?.spatial?.nodes || [],
      color: resolveToken(theme, 'colors.primary'),
      accent: resolveToken(theme, 'colors.accent'),
    }, { color: 'colors.primary', accent: 'colors.accent' }),
    evidenceBlock: themed({
      ...base,
      type: 'evidenceBlock',
      w: 300,
      h: 96,
      evidence: data?.spatial?.evidence || data?.evidence || [],
      columns: 3,
      gap: 10,
      labelColor: resolveToken(theme, 'colors.muted'),
      valueColor: resolveToken(theme, 'colors.primary'),
    }, { labelColor: 'colors.muted', valueColor: 'colors.primary' }),
    richText: themed({
      ...base,
      type: 'richText',
      content: '重点说明\n支持多行排版',
      fontSize: 18,
      fontFamily: resolveToken(theme, 'typography.bodyFont'),
      fontWeight: 500,
      fontStyle: 'normal',
      color: resolveToken(theme, 'colors.text'),
      textAlign: 'left',
      lineHeight: 1.55,
      letterSpacing: 0,
    }, { fontFamily: 'typography.bodyFont', color: 'colors.text' }),
    icon: themed({
      ...base,
      type: 'icon',
      w: 52,
      h: 52,
      iconName: options.preset === 'cert' ? 'ShieldCheck' : 'MapPin',
      color: resolveToken(theme, 'colors.primary'),
      strokeWidth: 1.8,
    }, { color: 'colors.primary' }),
    labelPill: themed({
      ...base,
      type: 'labelPill',
      w: 170,
      h: 34,
      content: data?.origin || '原产地实证',
      color: resolveToken(theme, 'colors.primary'),
      bgColor: resolveToken(theme, 'colors.paper'),
      borderRadius: 999,
    }, { color: 'colors.primary', bgColor: 'colors.paper' }),
    metricCard: themed({
      ...base,
      type: 'metricCard',
      w: 210,
      h: 116,
      label: evidence[0]?.label || '核心指标',
      value: evidence[0]?.value || '0 检出',
      note: evidence[0]?.note || '来自项目证据数据',
      labelColor: resolveToken(theme, 'colors.muted'),
      valueColor: resolveToken(theme, 'colors.primary'),
      paper: resolveToken(theme, 'colors.paper'),
    }, { labelColor: 'colors.muted', valueColor: 'colors.primary', paper: 'colors.paper' }),
    certCard: themed({
      ...base,
      type: 'certCard',
      w: 260,
      h: 118,
      org: 'SGS 通标标准技术',
      result: '检测结果：符合标准',
      code: 'REP-TRACE-0001',
      iconName: 'ShieldCheck',
      color: resolveToken(theme, 'colors.primary'),
      paper: resolveToken(theme, 'colors.paper'),
    }, { color: 'colors.primary', paper: 'colors.paper' }),
    timelineNode: themed({
      ...base,
      type: 'timelineNode',
      w: 260,
      h: 86,
      title: nodes[0]?.short || nodes[0]?.name || '空间节点',
      desc: nodes[0]?.desc || '记录采样、仓储或交付过程',
      color: resolveToken(theme, 'colors.primary'),
      muted: resolveToken(theme, 'colors.muted'),
    }, { color: 'colors.primary', muted: 'colors.muted' }),
    chartBlock: themed({
      ...base,
      type: 'chartBlock',
      w: 260,
      h: 170,
      title: options.preset === 'radar' ? '品质对标国标' : '气候风土因子',
      chartKind: options.preset === 'radar' ? 'radar' : options.preset === 'bar' ? 'bar' : 'trend',
      color: resolveToken(theme, 'colors.primary'),
      muted: resolveToken(theme, 'colors.muted'),
      paper: resolveToken(theme, 'colors.paper'),
    }, { color: 'colors.primary', muted: 'colors.muted', paper: 'colors.paper' }),
    mapLegend: themed({
      ...base,
      type: 'mapLegend',
      w: 280,
      h: 140,
      title: data?.origin || '原产地坐标',
      subtitle: data?.province || '',
      nodes,
      color: resolveToken(theme, 'colors.primary'),
      muted: resolveToken(theme, 'colors.muted'),
      paper: resolveToken(theme, 'colors.paper'),
    }, { color: 'colors.primary', muted: 'colors.muted', paper: 'colors.paper' }),
    quoteBlock: themed({
      ...base,
      type: 'quoteBlock',
      w: 260,
      h: 118,
      content: data?.narrative || data?.summary || '把产地证据转化为可阅读的品牌叙事。',
      color: resolveToken(theme, 'colors.primary'),
      textColor: resolveToken(theme, 'colors.text'),
      paper: resolveToken(theme, 'colors.paper'),
    }, { color: 'colors.primary', textColor: 'colors.text', paper: 'colors.paper' }),
    qrPlaceholder: themed({
      ...base,
      type: 'qrPlaceholder',
      w: 118,
      h: 142,
      label: '扫码查看溯源',
      color: resolveToken(theme, 'colors.primary'),
      muted: resolveToken(theme, 'colors.muted'),
    }, { color: 'colors.primary', muted: 'colors.muted' }),
    lineArrow: themed({
      ...base,
      type: 'lineArrow',
      w: 180,
      h: 24,
      color: resolveToken(theme, 'colors.primary'),
      thickness: 2,
    }, { color: 'colors.primary' }),
  }
  return { ...(map[type] || map.text), ...(options.patch || {}) }
}

function createTemplateElements(type, template, preset, data, theme) {
  const ctx = makeContext(preset)
  if (type === 'archive') return archiveTemplateElements(template.family, ctx, data, theme)
  return posterTemplateElements(template.family, ctx, data, theme)
}

function posterTemplateElements(family, ctx, data, theme) {
  const builders = {
    classic: posterClassic,
    heritage: posterHeritage,
    indigo: posterIndigo,
    hero: posterHero,
    map: posterMap,
    grid: posterGrid,
    split: posterSplit,
    banner: posterBanner,
  }
  return (builders[family] || posterClassic)(ctx, data, theme)
}

function archiveTemplateElements(family, ctx, data, theme) {
  const builders = {
    classic: archiveClassic,
    map: archiveMap,
    columns: archiveColumns,
    metrics: archiveMetrics,
    cover: archiveCover,
    landscape: archiveLandscape,
  }
  return (builders[family] || archiveClassic)(ctx, data, theme)
}

function makeContext(preset) {
  const width = preset.width
  const height = preset.height
  const min = Math.min(width, height)
  const landscape = width / height > 1.25
  const square = Math.abs(width - height) / Math.max(width, height) < 0.12
  const m = Math.round(min * (landscape ? 0.06 : 0.075))
  return { width, height, min, m, landscape, square }
}

function box(ctx, x, y, w, h) {
  return {
    x: Math.round(ctx.width * x),
    y: Math.round(ctx.height * y),
    w: Math.round(ctx.width * w),
    h: Math.round(ctx.height * h),
  }
}

function posterClassic(ctx, data, theme) {
  if (ctx.landscape) return posterBanner(ctx, data, theme)
  const elements = []
  addHeroImage(elements, ctx, data, box(ctx, 0.075, 0.055, 0.85, ctx.square ? 0.42 : 0.34), 10)
  addBadge(elements, ctx, data?.origin || '真实产地 · 空间溯源', box(ctx, 0.075, ctx.square ? 0.52 : 0.435, 0.52, 0.035), theme, 20)
  addTitle(elements, ctx, data?.title || '未命名产品', box(ctx, 0.075, ctx.square ? 0.57 : 0.485, 0.82, 0.1), theme, 34, 22)
  if (data?.subtitle) addBodyText(elements, data.subtitle, box(ctx, 0.075, ctx.square ? 0.68 : 0.59, 0.78, 0.06), theme, 13, 22)
  if (data?.narrative) addNarrative(elements, data.narrative, box(ctx, 0.075, ctx.square ? 0.76 : 0.69, 0.54, 0.16), theme, 18)
  addMap(elements, ctx, data, box(ctx, 0.66, ctx.square ? 0.765 : 0.695, 0.25, 0.16), theme, 19)
  addEvidence(elements, ctx, data, box(ctx, 0.075, 0.88, 0.85, 0.075), theme, 22, 3)
  addDivider(elements, ctx, box(ctx, 0.075, 0.965, 0.85, 0.01), theme, 5)
  return elements
}

function posterHeritage(ctx, data, theme) {
  const elements = []
  addShape(elements, box(ctx, 0.055, 0.045, 0.89, 0.91), theme, 1, 24, 0.32)
  addHeroImage(elements, ctx, data, ctx.landscape ? box(ctx, 0.07, 0.16, 0.4, 0.64) : box(ctx, 0.12, 0.22, 0.76, 0.32), 8, 999)
  addBadge(elements, ctx, 'PROVENANCE', box(ctx, 0.1, 0.09, 0.36, 0.035), theme, 20)
  addTitle(elements, ctx, data?.title || '未命名产品', ctx.landscape ? box(ctx, 0.53, 0.18, 0.36, 0.18) : box(ctx, 0.13, 0.58, 0.76, 0.12), theme, 38, 24)
  addBodyText(elements, data?.poeticLine || data?.subtitle || data?.origin || '', ctx.landscape ? box(ctx, 0.53, 0.4, 0.34, 0.08) : box(ctx, 0.13, 0.72, 0.72, 0.06), theme, 15, 21)
  addNarrative(elements, data?.narrative || data?.subtitle || '', ctx.landscape ? box(ctx, 0.53, 0.54, 0.32, 0.22) : box(ctx, 0.13, 0.8, 0.72, 0.12), theme, 18)
  addDivider(elements, ctx, box(ctx, 0.1, 0.94, 0.8, 0.012), theme, 5)
  return elements
}

function posterIndigo(ctx, data, theme) {
  const elements = []
  addShape(elements, box(ctx, 0.06, 0.06, 0.88, 0.88), theme, 1, 18, 0.24)
  addMap(elements, ctx, data, ctx.landscape ? box(ctx, 0.06, 0.12, 0.45, 0.62) : box(ctx, 0.12, 0.12, 0.76, 0.34), theme, 12)
  addBadge(elements, ctx, data?.province || 'GEOGRAPHIC PROOF', ctx.landscape ? box(ctx, 0.56, 0.15, 0.32, 0.04) : box(ctx, 0.12, 0.51, 0.5, 0.035), theme, 22)
  addTitle(elements, ctx, data?.title || '未命名产品', ctx.landscape ? box(ctx, 0.56, 0.23, 0.36, 0.18) : box(ctx, 0.12, 0.57, 0.76, 0.12), theme, 38, 24)
  addBodyText(elements, data?.subtitle || data?.origin || '', ctx.landscape ? box(ctx, 0.56, 0.45, 0.33, 0.08) : box(ctx, 0.12, 0.7, 0.72, 0.06), theme, 13, 23)
  addEvidence(elements, ctx, data, ctx.landscape ? box(ctx, 0.56, 0.62, 0.36, 0.18) : box(ctx, 0.12, 0.8, 0.76, 0.1), theme, 24, ctx.landscape ? 1 : 3)
  return elements
}

function posterHero(ctx, data, theme) {
  const elements = []
  addHeroImage(elements, ctx, data, ctx.landscape ? box(ctx, 0.45, 0.08, 0.48, 0.84) : box(ctx, 0.06, 0.06, 0.88, 0.58), 8, 20)
  addShape(elements, ctx.landscape ? box(ctx, 0.06, 0.14, 0.44, 0.68) : box(ctx, 0.1, 0.55, 0.8, 0.28), theme, 9, 18, 0.92)
  addBadge(elements, ctx, data?.origin || 'ORIGIN STORY', ctx.landscape ? box(ctx, 0.1, 0.2, 0.28, 0.04) : box(ctx, 0.15, 0.61, 0.42, 0.035), theme, 20)
  addTitle(elements, ctx, data?.title || '未命名产品', ctx.landscape ? box(ctx, 0.1, 0.29, 0.34, 0.2) : box(ctx, 0.15, 0.66, 0.7, 0.12), theme, 42, 22)
  addBodyText(elements, data?.subtitle || '', ctx.landscape ? box(ctx, 0.1, 0.55, 0.32, 0.1) : box(ctx, 0.15, 0.79, 0.68, 0.06), theme, 14, 23)
  addEvidence(elements, ctx, data, ctx.landscape ? box(ctx, 0.1, 0.71, 0.34, 0.1) : box(ctx, 0.15, 0.88, 0.7, 0.07), theme, 24, 3)
  return elements
}

function posterMap(ctx, data, theme) {
  const elements = []
  addMap(elements, ctx, data, ctx.landscape ? box(ctx, 0.08, 0.14, 0.5, 0.62) : box(ctx, 0.12, 0.16, 0.76, 0.46), theme, 12)
  addBadge(elements, ctx, 'SPATIAL ORIGIN', ctx.landscape ? box(ctx, 0.64, 0.18, 0.26, 0.04) : box(ctx, 0.12, 0.08, 0.42, 0.035), theme, 22)
  addTitle(elements, ctx, data?.title || '未命名产品', ctx.landscape ? box(ctx, 0.64, 0.28, 0.28, 0.16) : box(ctx, 0.12, 0.66, 0.76, 0.1), theme, 34, 24)
  addBodyText(elements, data?.subtitle || data?.origin || '', ctx.landscape ? box(ctx, 0.64, 0.48, 0.27, 0.09) : box(ctx, 0.12, 0.77, 0.72, 0.06), theme, 13, 23)
  addEvidence(elements, ctx, data, ctx.landscape ? box(ctx, 0.64, 0.64, 0.28, 0.16) : box(ctx, 0.12, 0.86, 0.76, 0.08), theme, 24, ctx.landscape ? 1 : 3)
  return elements
}

function posterGrid(ctx, data, theme) {
  const elements = []
  addBadge(elements, ctx, 'EVIDENCE GRID', box(ctx, 0.08, 0.08, 0.34, 0.035), theme, 22)
  addTitle(elements, ctx, data?.title || '未命名产品', box(ctx, 0.08, 0.14, 0.78, 0.12), theme, 36, 23)
  addBodyText(elements, data?.subtitle || '', box(ctx, 0.08, 0.28, 0.72, 0.06), theme, 13, 23)
  addEvidence(elements, ctx, data, ctx.landscape ? box(ctx, 0.08, 0.43, 0.42, 0.34) : box(ctx, 0.08, 0.4, 0.84, 0.18), theme, 24, ctx.landscape ? 1 : 3)
  addMap(elements, ctx, data, ctx.landscape ? box(ctx, 0.56, 0.36, 0.34, 0.42) : box(ctx, 0.1, 0.64, 0.38, 0.22), theme, 18)
  addNarrative(elements, data?.narrative || data?.origin || '', ctx.landscape ? box(ctx, 0.56, 0.78, 0.34, 0.12) : box(ctx, 0.54, 0.64, 0.36, 0.22), theme, 19)
  return elements
}

function posterSplit(ctx, data, theme) {
  const elements = []
  addHeroImage(elements, ctx, data, ctx.landscape ? box(ctx, 0.06, 0.08, 0.46, 0.84) : box(ctx, 0.08, 0.08, 0.84, 0.36), 8, 18)
  addBadge(elements, ctx, data?.category || 'EDITORIAL', ctx.landscape ? box(ctx, 0.58, 0.14, 0.25, 0.04) : box(ctx, 0.1, 0.5, 0.36, 0.035), theme, 20)
  addTitle(elements, ctx, data?.title || '未命名产品', ctx.landscape ? box(ctx, 0.58, 0.23, 0.34, 0.2) : box(ctx, 0.1, 0.56, 0.78, 0.11), theme, 38, 23)
  addNarrative(elements, data?.narrative || data?.subtitle || '', ctx.landscape ? box(ctx, 0.58, 0.5, 0.32, 0.22) : box(ctx, 0.1, 0.7, 0.78, 0.12), theme, 18)
  addEvidence(elements, ctx, data, ctx.landscape ? box(ctx, 0.58, 0.78, 0.34, 0.1) : box(ctx, 0.1, 0.86, 0.78, 0.08), theme, 24, 3)
  return elements
}

function posterBanner(ctx, data, theme) {
  const elements = []
  addHeroImage(elements, ctx, data, box(ctx, 0.055, 0.09, 0.43, 0.78), 8, 18)
  addBadge(elements, ctx, data?.origin || 'TRACEABLE ORIGIN', box(ctx, 0.54, 0.14, 0.3, 0.045), theme, 20)
  addTitle(elements, ctx, data?.title || '未命名产品', box(ctx, 0.54, 0.24, 0.36, 0.2), theme, 38, 22)
  addBodyText(elements, data?.subtitle || '', box(ctx, 0.54, 0.48, 0.34, 0.09), theme, 14, 22)
  addMap(elements, ctx, data, box(ctx, 0.77, 0.62, 0.15, 0.22), theme, 18)
  addEvidence(elements, ctx, data, box(ctx, 0.54, 0.68, 0.36, 0.15), theme, 24, 3)
  return elements
}

function archiveClassic(ctx, data, theme) {
  const elements = []
  addTitle(elements, ctx, data?.title || '实证白皮书', box(ctx, 0.06, 0.055, 0.88, 0.075), theme, 34, 22)
  addBodyText(elements, data?.summary || '', box(ctx, 0.06, 0.13, 0.88, 0.085), theme, 14, 22)
  addMap(elements, ctx, data, box(ctx, 0.06, 0.26, 0.5, 0.24), theme, 16)
  addEvidence(elements, ctx, data, box(ctx, 0.59, 0.26, 0.35, 0.24), theme, 17, 1)
  addNarrative(elements, nodeNarrative(data), box(ctx, 0.06, 0.535, 0.88, 0.2), theme, 18)
  addBodyText(elements, data?.conclusion || '', box(ctx, 0.06, 0.79, 0.88, 0.11), theme, 13, 20)
  return elements
}

function archiveMap(ctx, data, theme) {
  const elements = []
  addBadge(elements, ctx, 'PROVENANCE DOSSIER', box(ctx, 0.06, 0.055, 0.32, 0.03), theme, 21)
  addTitle(elements, ctx, data?.title || '实证白皮书', box(ctx, 0.06, 0.095, 0.62, 0.075), theme, 32, 22)
  addMap(elements, ctx, data, ctx.landscape ? box(ctx, 0.06, 0.23, 0.55, 0.58) : box(ctx, 0.06, 0.22, 0.88, 0.38), theme, 15)
  addEvidence(elements, ctx, data, ctx.landscape ? box(ctx, 0.66, 0.23, 0.28, 0.28) : box(ctx, 0.06, 0.64, 0.88, 0.12), theme, 18, ctx.landscape ? 1 : 3)
  addNarrative(elements, nodeNarrative(data), ctx.landscape ? box(ctx, 0.66, 0.56, 0.28, 0.25) : box(ctx, 0.06, 0.79, 0.88, 0.13), theme, 19)
  return elements
}

function archiveColumns(ctx, data, theme) {
  const elements = []
  addTitle(elements, ctx, data?.title || '实证白皮书', box(ctx, 0.07, 0.06, 0.76, 0.08), theme, 31, 22)
  addDivider(elements, ctx, box(ctx, 0.07, 0.165, 0.86, 0.01), theme, 5)
  addBodyText(elements, data?.summary || '', box(ctx, 0.07, 0.2, 0.4, 0.22), theme, 13, 18)
  addNarrative(elements, nodeNarrative(data), box(ctx, 0.53, 0.2, 0.4, 0.22), theme, 18)
  addMap(elements, ctx, data, box(ctx, 0.07, 0.48, 0.4, 0.28), theme, 16)
  addEvidence(elements, ctx, data, box(ctx, 0.53, 0.48, 0.4, 0.28), theme, 17, 1)
  addBodyText(elements, data?.conclusion || '', box(ctx, 0.07, 0.82, 0.86, 0.1), theme, 13, 20)
  return elements
}

function archiveMetrics(ctx, data, theme) {
  const elements = []
  addBadge(elements, ctx, 'KEY FINDINGS', box(ctx, 0.07, 0.06, 0.28, 0.03), theme, 21)
  addTitle(elements, ctx, data?.title || '实证白皮书', box(ctx, 0.07, 0.1, 0.78, 0.08), theme, 33, 22)
  addEvidence(elements, ctx, data, box(ctx, 0.07, 0.23, 0.86, 0.22), theme, 24, 3)
  addMap(elements, ctx, data, box(ctx, 0.07, 0.51, 0.4, 0.27), theme, 16)
  addNarrative(elements, data?.summary || nodeNarrative(data), box(ctx, 0.53, 0.51, 0.4, 0.27), theme, 18)
  addBodyText(elements, data?.conclusion || '', box(ctx, 0.07, 0.84, 0.86, 0.09), theme, 13, 20)
  return elements
}

function archiveCover(ctx, data, theme) {
  const elements = []
  addShape(elements, box(ctx, 0.07, 0.07, 0.86, 0.86), theme, 1, 22, 0.42)
  addBadge(elements, ctx, data?.origin || 'TRACEABLE FOOD', box(ctx, 0.13, 0.15, 0.42, 0.035), theme, 21)
  addTitle(elements, ctx, data?.title || '实证白皮书', box(ctx, 0.13, 0.23, 0.74, 0.14), theme, 40, 22)
  addBodyText(elements, data?.summary || '', box(ctx, 0.13, 0.42, 0.68, 0.13), theme, 15, 20)
  addMap(elements, ctx, data, box(ctx, 0.13, 0.62, 0.36, 0.2), theme, 16)
  addEvidence(elements, ctx, data, box(ctx, 0.54, 0.62, 0.33, 0.2), theme, 18, 1)
  return elements
}

function archiveLandscape(ctx, data, theme) {
  const elements = []
  addBadge(elements, ctx, 'BRIEFING PAGE', box(ctx, 0.05, 0.08, 0.22, 0.035), theme, 21)
  addTitle(elements, ctx, data?.title || '实证白皮书', box(ctx, 0.05, 0.15, 0.36, 0.16), theme, 35, 22)
  addBodyText(elements, data?.summary || '', box(ctx, 0.05, 0.38, 0.32, 0.15), theme, 13, 19)
  addEvidence(elements, ctx, data, box(ctx, 0.05, 0.62, 0.32, 0.22), theme, 24, 1)
  addMap(elements, ctx, data, box(ctx, 0.43, 0.12, 0.32, 0.68), theme, 16)
  addNarrative(elements, nodeNarrative(data) || data?.conclusion || '', box(ctx, 0.78, 0.14, 0.17, 0.66), theme, 18)
  return elements
}

function addTitle(elements, ctx, content, rect, theme, maxSize, zIndex) {
  elements.push(themed(textElement({
    content,
    ...rect,
    zIndex,
    fontSize: clamp(Math.round(ctx.min * 0.075), 24, maxSize),
    fontFamily: resolveToken(theme, 'typography.titleFont'),
    fontWeight: resolveToken(theme, 'typography.titleWeight', 700),
    color: resolveToken(theme, 'colors.primary'),
    lineHeight: 1.15,
  }), { fontFamily: 'typography.titleFont', fontWeight: 'typography.titleWeight', color: 'colors.primary' }))
}

function addBodyText(elements, content, rect, theme, size, zIndex) {
  if (!content) return
  elements.push(themed(textElement({
    content,
    ...rect,
    zIndex,
    fontSize: clamp(Math.round(rect.w * 0.035), 12, size),
    fontFamily: resolveToken(theme, 'typography.bodyFont'),
    color: resolveToken(theme, 'colors.text'),
    lineHeight: resolveToken(theme, 'typography.bodyLineHeight', 1.6),
  }), { fontFamily: 'typography.bodyFont', color: 'colors.text', lineHeight: 'typography.bodyLineHeight' }))
}

function addHeroImage(elements, ctx, data, rect, zIndex, radius = 12) {
  if (data?.modules?.mainImage === false || !data?.heroImage) return
  elements.push({
    ...baseElement(null, rect),
    type: 'image',
    zIndex,
    src: data.heroImage,
    objectFit: 'cover',
    objectPositionX: 50,
    objectPositionY: data.imagePosY ?? 50,
    borderRadius: Math.round(ctx.min * (radius / 1000)),
  })
}

function addBadge(elements, ctx, content, rect, theme, zIndex) {
  elements.push(themed({
    ...baseElement(null, rect),
    type: 'badge',
    content,
    style: 'tag',
    zIndex,
    color: resolveToken(theme, 'colors.primary'),
    bgColor: 'transparent',
  }, { color: 'colors.primary' }))
}

function addDivider(elements, ctx, rect, theme, zIndex) {
  elements.push(themed({
    ...baseElement(null, rect),
    type: 'divider',
    zIndex,
    opacity: 0.45,
    style: 'solid',
    color: resolveToken(theme, 'colors.primary'),
    thickness: Math.max(1, Math.round(ctx.min * 0.002)),
  }, { color: 'colors.primary' }))
}

function addShape(elements, rect, theme, zIndex, radius = 18, opacity = 1) {
  elements.push(themed({
    ...baseElement(null, rect),
    type: 'shape',
    zIndex,
    opacity,
    shape: 'rect',
    fill: resolveToken(theme, 'colors.paper'),
    stroke: resolveToken(theme, 'colors.primary'),
    borderRadius: radius,
  }, { fill: 'colors.paper', stroke: 'colors.primary' }))
}

function addMap(elements, ctx, data, rect, theme, zIndex) {
  if (data?.modules?.spatialMap === false || data?.modules?.spatialBase === false) return
  elements.push(themed({
    ...baseElement(null, rect),
    type: 'mapBlock',
    zIndex,
    province: data?.province || '',
    nodes: data?.spatial?.nodes || [],
    color: resolveToken(theme, 'colors.primary'),
    accent: resolveToken(theme, 'colors.accent'),
  }, { color: 'colors.primary', accent: 'colors.accent' }))
}

function addEvidence(elements, ctx, data, rect, theme, zIndex, columns = 3) {
  if (data?.modules?.evidenceMetrics === false) return
  const evidence = data?.spatial?.evidence || data?.evidence || []
  if (!evidence.length) return
  elements.push(themed({
    ...baseElement(null, rect),
    type: 'evidenceBlock',
    zIndex,
    evidence,
    columns,
    gap: Math.max(8, Math.round(ctx.min * 0.012)),
    labelColor: resolveToken(theme, 'colors.muted'),
    valueColor: resolveToken(theme, 'colors.primary'),
  }, { labelColor: 'colors.muted', valueColor: 'colors.primary' }))
}

function addNarrative(elements, content, rect, theme, zIndex) {
  if (!content) return
  elements.push(themed({
    ...baseElement(null, rect),
    type: 'narrativeBlock',
    zIndex,
    kicker: 'PROVENANCE DOSSIER',
    subtitle: '空间节点链路',
    content,
    color: resolveToken(theme, 'colors.text'),
    accent: resolveToken(theme, 'colors.primary'),
    paper: resolveToken(theme, 'colors.paper'),
  }, { color: 'colors.text', accent: 'colors.primary', paper: 'colors.paper' }))
}

function baseElement(layout, overrides = {}) {
  return {
    id: uid('el'),
    x: 0,
    y: 0,
    w: 120,
    h: 60,
    zIndex: nextZIndex(layout),
    locked: false,
    visible: true,
    opacity: 1,
    _themeSlots: [],
    _themeRefs: {},
    ...overrides,
  }
}

function textElement(overrides) {
  return {
    ...baseElement(null),
    type: 'text',
    content: '',
    fontSize: 16,
    fontFamily: '"Noto Sans SC", sans-serif',
    fontWeight: 400,
    fontStyle: 'normal',
    color: '#201b16',
    textAlign: 'left',
    lineHeight: 1.4,
    letterSpacing: 0,
    ...overrides,
  }
}

function themed(element, refs) {
  return {
    ...element,
    _themeSlots: Array.from(new Set([...(element._themeSlots || []), ...Object.keys(refs || {})])),
    _themeRefs: { ...(element._themeRefs || {}), ...(refs || {}) },
  }
}

function nodeNarrative(data) {
  const nodes = data?.spatial?.nodes || []
  if (!nodes.length) return data?.conclusion || ''
  return nodes.map((node, index) => `${index + 1}. ${node.short || node.name}: ${node.desc || ''}`).join('\n')
}

function nextZIndex(layout) {
  return Math.max(0, ...(layout?.elements || []).map(item => item.zIndex || 0)) + 10
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function uid(prefix = 'layout') {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}
