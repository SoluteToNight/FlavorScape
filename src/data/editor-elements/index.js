export const ICON_OPTIONS = [
  { name: 'MapPin', label: '定位' },
  { name: 'FileText', label: '报告' },
  { name: 'Award', label: '认证' },
  { name: 'ShieldCheck', label: '安全' },
  { name: 'BadgeCheck', label: '通过' },
  { name: 'BarChart3', label: '指标' },
  { name: 'LineChart', label: '趋势' },
  { name: 'Leaf', label: '风土' },
  { name: 'Package', label: '批次' },
  { name: 'QrCode', label: '二维码' },
  { name: 'Quote', label: '引文' },
]

export const ELEMENT_TYPE_LABELS = {
  text: '文本',
  richText: '富文本',
  image: '图片',
  badge: '徽章',
  labelPill: '标签',
  divider: '分割线',
  lineArrow: '箭头线',
  shape: '形状',
  icon: '图标',
  mapBlock: '地图',
  mapLegend: '地图图例',
  evidenceBlock: '证据组',
  metricCard: '指标卡',
  certCard: '凭证卡',
  timelineNode: '节点线',
  chartBlock: '图表块',
  narrativeBlock: '叙事块',
  quoteBlock: '引用',
  qrPlaceholder: '二维码',
}

export const EDITOR_ELEMENT_GROUPS = [
  {
    id: 'base',
    label: '基础元素',
    items: [
      { type: 'text', label: '文本', hint: '标题、说明、注释' },
      { type: 'richText', label: '富文本', hint: '支持换行与重点词' },
      { type: 'image', label: '图片', hint: '产品图、纹理、背景' },
      { type: 'shape', label: '形状', hint: '色块、底板、装饰' },
      { type: 'divider', label: '分割线', hint: '细线与段落分隔' },
      { type: 'lineArrow', label: '箭头线', hint: '流程与指向' },
    ],
  },
  {
    id: 'brand',
    label: '品牌组件',
    items: [
      { type: 'badge', label: '徽章', hint: '圆角标签/印章' },
      { type: 'labelPill', label: '标签胶囊', hint: '产地、品类、状态' },
      { type: 'quoteBlock', label: '引文', hint: '品牌叙事重点句' },
      { type: 'qrPlaceholder', label: '二维码占位', hint: '溯源扫码入口' },
      { type: 'icon', label: '图标', hint: 'Lucide 线性图标' },
    ],
  },
  {
    id: 'data',
    label: '数据组件',
    items: [
      { type: 'metricCard', label: '指标卡', hint: '单个核心数据' },
      { type: 'evidenceBlock', label: '证据组', hint: '多指标栅格' },
      { type: 'chartBlock', label: '图表块', hint: '静态趋势/雷达容器' },
      { type: 'mapBlock', label: '空间地图', hint: '产地节点底图' },
    ],
  },
  {
    id: 'archive',
    label: '白皮书组件',
    items: [
      { type: 'certCard', label: '实验室凭证', hint: '机构、结果、报告编号' },
      { type: 'timelineNode', label: '节点链路', hint: '采样/仓储/交付流程' },
      { type: 'mapLegend', label: '地图图例', hint: '原产地坐标与节点摘要' },
      { type: 'chartBlock', preset: 'climate', label: '气候图表', hint: '降水/温度证据容器' },
      { type: 'chartBlock', preset: 'radar', label: '雷达图表', hint: '品质对标容器' },
    ],
  },
]

export function labelForElementType(type) {
  return ELEMENT_TYPE_LABELS[type] || type || '元素'
}

export function titleForElement(element) {
  return element.name
    || element.content
    || element.label
    || element.subtitle
    || element.province
    || labelForElementType(element.type)
}
