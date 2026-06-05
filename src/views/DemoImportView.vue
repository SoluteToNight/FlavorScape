<template>
  <main class="asset-page">
    <section class="asset-header">
      <div>
        <span class="eyebrow">Spatial Brand Asset Package</span>
        <h1>空间品牌资产生成器</h1>
        <p>上传产品资料、检测报告、产地证明、表格和品牌文档，让 DeepSeek 提取证据、空间节点、视觉方向和可交付资产。</p>
      </div>
      <div class="format-strip">
        <span v-for="item in supportedFormats" :key="item">{{ item }}</span>
      </div>
    </section>

    <section class="asset-workspace">
      <aside class="input-panel">
        <div class="panel-head">
          <div>
            <span class="eyebrow">Source</span>
            <h2>资料输入</h2>
          </div>
          <button v-if="files.length || manualText" type="button" class="ghost-btn" @click="resetAll">清空</button>
        </div>

        <div class="template-grid">
          <button
            v-for="item in templates"
            :key="item.id"
            type="button"
            class="template-card"
            :class="{ active: item.id === selectedTemplateId }"
            @click="selectedTemplateId = item.id"
          >
            <strong>{{ item.name }}</strong>
            <span>{{ item.origin }}</span>
          </button>
        </div>

        <label
          class="dropzone"
          :class="{ dragging: isDragging }"
          @dragenter.prevent="isDragging = true"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
        >
          <input
            ref="fileInput"
            type="file"
            multiple
            accept=".pdf,.docx,.xlsx,.xls,.csv,.txt,.md,.markdown,.json,.png,.jpg,.jpeg,.webp"
            @change="onFileInput"
          />
          <span class="upload-mark">+</span>
          <strong>拖放资料到这里，或点击选择</strong>
          <small>支持 PDF、DOCX、XLSX、CSV、TXT、Markdown、JSON 和图片素材。图片会作为视觉素材记录，暂不做 OCR。</small>
        </label>

        <div class="file-list">
          <div class="section-title">
            <span>文件队列</span>
            <small>{{ files.length }} 个文件</small>
          </div>
          <div v-if="!files.length" class="empty-box">还没有文件。你也可以只填写下方文字说明，让 DeepSeek 先生成一版资产方案。</div>
          <div v-for="file in files" :key="file.id" class="file-row">
            <div>
              <strong>{{ file.name }}</strong>
              <small>{{ file.kind }} / {{ file.size }}</small>
            </div>
            <button type="button" @click="removeFile(file.id)">移除</button>
          </div>
        </div>

        <div class="manual-block">
          <div class="section-title">
            <span>补充说明</span>
            <button type="button" @click="fillTemplateText">填入示例</button>
          </div>
          <textarea
            v-model="manualText"
            placeholder="可补充产品名称、产地、检测指标、品牌定位、希望的视觉风格、目标渠道等。"
          />
        </div>

        <button class="primary-btn" type="button" :disabled="isAnalyzing || !canAnalyze" @click="analyzeAssets">
          {{ isAnalyzing ? 'DeepSeek 分析中...' : '开始生成资产分析' }}
        </button>
        <p v-if="errorText" class="error-text">{{ errorText }}</p>
      </aside>

      <section class="output-panel">
        <div class="progress-card">
          <div class="panel-head compact">
            <div>
              <span class="eyebrow">AI Workflow</span>
              <h2>可视化反馈</h2>
            </div>
            <strong>{{ progressPercent }}%</strong>
          </div>
          <div class="progress-track"><span :style="{ width: `${progressPercent}%` }" /></div>
          <ol class="timeline">
            <li v-for="step in visibleSteps" :key="step.key" :class="step.status">
              <span>{{ step.index }}</span>
              <div>
                <strong>{{ step.title }}</strong>
                <small>{{ step.detail }}</small>
              </div>
            </li>
          </ol>
        </div>

        <div v-if="analysis" class="result-grid">
          <section class="result-card hero-result">
            <span class="eyebrow">Product</span>
            <h2>{{ productName }}</h2>
            <p>{{ packageData.brand_assets.slogan || selectedTemplate.summary }}</p>
            <div class="score-grid">
              <div v-for="score in scoreCards" :key="score.label">
                <span>{{ score.label }}</span>
                <strong>{{ score.value }}%</strong>
              </div>
            </div>
          </section>

          <section class="result-card">
            <span class="eyebrow">DeepSeek 可见分析</span>
            <ul class="plain-list">
              <li v-for="item in thinkingTrace" :key="item">{{ item }}</li>
            </ul>
          </section>

          <section class="result-card">
            <span class="eyebrow">文件解析结果</span>
            <div v-for="file in extractionFiles" :key="file.name" class="extract-row">
              <strong>{{ file.name }}</strong>
              <small>{{ file.status }} / {{ file.chars }} chars</small>
              <p>{{ file.preview || file.note }}</p>
            </div>
          </section>

          <section class="result-card">
            <span class="eyebrow">证据与风险</span>
            <h3>可用证据</h3>
            <ul class="plain-list">
              <li v-for="item in evidenceList" :key="item">{{ item }}</li>
            </ul>
            <h3>风险提示</h3>
            <ul class="plain-list warning">
              <li v-for="item in riskList" :key="item">{{ item }}</li>
            </ul>
          </section>

          <section class="result-card">
            <span class="eyebrow">引用定位</span>
            <div v-if="citationList.length" class="citation-list">
              <article v-for="item in citationList" :key="item.id || `${item.source}-${item.locator}`">
                <div>
                  <strong>{{ item.claim || '证据引用' }}</strong>
                  <small>{{ item.source || '未标注来源' }} · {{ item.locator || '未标注位置' }}</small>
                </div>
                <p>{{ item.quote || 'DeepSeek 未返回原文摘录，建议打开原始资料复核。' }}</p>
                <span>{{ Math.round((item.confidence || 0) * 100) }}%</span>
              </article>
            </div>
            <div v-else class="empty-box">DeepSeek 暂未返回引用定位。建议在补充说明中明确报告页码、表格名称或认证编号后重新分析。</div>
          </section>

          <section class="result-card">
            <span class="eyebrow">人工复核</span>
            <div class="review-summary">
              <strong>{{ reviewStatusLabel }}</strong>
              <p>{{ reviewStatus.summary || '证据尚未人工复核。' }}</p>
              <small>{{ reviewedCount }} / {{ reviewItems.length }} 项已标记复核</small>
            </div>
            <div v-if="reviewItems.length" class="review-list">
              <label v-for="(item, index) in reviewItems" :key="reviewKey(item, index)">
                <input
                  type="checkbox"
                  :checked="isReviewed(item, index)"
                  @change="toggleReview(item, index, $event.target.checked)"
                />
                <span>
                  <strong>{{ item.label }}</strong>
                  <small>{{ reviewItemLabel(item, index) }} · {{ item.reason || '请核验原件、编号、日期和批次。' }}</small>
                </span>
              </label>
            </div>
            <div v-else class="empty-box">当前资产包没有返回具体复核项，建议至少人工核验产地证明、检测报告和宣传表述。</div>
          </section>

          <section class="result-card wide">
            <span class="eyebrow">资产产出建议</span>
            <div class="asset-grid">
              <article v-for="asset in generatedAssets" :key="asset.title">
                <strong>{{ asset.title }}</strong>
                <p>{{ asset.desc }}</p>
              </article>
            </div>
            <div class="action-row">
              <button type="button" :disabled="studioCreating" @click="createStudioProject('poster')">
                {{ studioCreating ? '创建中...' : '一键生成海报项目' }}
              </button>
              <button type="button" :disabled="studioCreating" @click="createStudioProject('archive')">生成白皮书项目</button>
              <button type="button" :disabled="studioCreating" @click="createStudioProject('display')">生成大屏项目</button>
              <button type="button" @click="openOutput('/marketing')">查看营销海报</button>
              <button type="button" @click="openOutput('/archive')">查看白皮书</button>
              <button type="button" @click="openOutput('/brand')">查看智慧大屏</button>
            </div>
            <p v-if="studioStatus" class="status-text">{{ studioStatus }}</p>
            <p v-if="studioError" class="error-text">{{ studioError }}</p>
          </section>

          <section class="result-card wide">
            <span class="eyebrow">业务流转</span>
            <div class="business-flow">
              <article v-for="step in businessSteps" :key="step.title" :class="{ ready: step.ready }">
                <span>{{ step.index }}</span>
                <strong>{{ step.title }}</strong>
                <p>{{ step.detail }}</p>
              </article>
            </div>
            <div class="action-row">
              <button type="button" @click="copyPackage">复制资产包 JSON</button>
              <button type="button" @click="downloadPackage">下载资产包 JSON</button>
            </div>
            <p v-if="copyStatus" class="status-text">{{ copyStatus }}</p>
          </section>

          <section class="result-card wide ai-chat-card">
            <div class="chat-head">
              <div>
                <span class="eyebrow">DeepSeek Co-pilot</span>
                <h2>和 AI 继续共创资产包</h2>
              </div>
              <button type="button" :disabled="chatLoading" @click="askAssetQuestion('请根据当前资产包，告诉我下一步最应该补齐哪些资料。')">
                资料补齐建议
              </button>
            </div>

            <div class="quick-chat">
              <button v-for="prompt in assetPrompts" :key="prompt" type="button" :disabled="chatLoading" @click="askAssetQuestion(prompt)">
                {{ prompt }}
              </button>
            </div>

            <div class="asset-chat-log">
              <div v-for="message in assetMessages" :key="message.id" class="asset-message" :class="message.role">
                <span>{{ message.role === 'assistant' ? 'AI' : '你' }}</span>
                <p>{{ message.content }}</p>
              </div>
              <div v-if="!assetMessages.length" class="chat-placeholder">
                分析完成后可以继续追问，例如：如何做成小红书海报、白皮书还缺什么证据、智慧大屏应突出哪些节点。
              </div>
            </div>

            <div v-if="chatRecommendations.length" class="recommendation-grid">
              <article v-for="item in chatRecommendations" :key="`${item.target}-${item.title}`">
                <span>{{ item.priority || 'medium' }}</span>
                <strong>{{ item.title }}</strong>
                <p>{{ item.detail }}</p>
              </article>
            </div>

            <ul v-if="chatNextActions.length" class="plain-list">
              <li v-for="item in chatNextActions" :key="item">{{ item }}</li>
            </ul>

            <form class="asset-chat-form" @submit.prevent="sendAssetChat">
              <textarea v-model="assetDraft" :disabled="chatLoading" placeholder="继续询问 DeepSeek：例如，帮我把这个资产包转成高端礼盒海报方向" />
              <button type="submit" :disabled="chatLoading || !assetDraft.trim()">{{ chatLoading ? '思考中' : '发送' }}</button>
            </form>
            <p v-if="chatError" class="error-text">{{ chatError }}</p>
          </section>
        </div>

        <div v-else class="empty-preview">
          <span class="eyebrow">Ready</span>
          <h2>等待资料分析</h2>
          <p>完成分析后，这里会显示 DeepSeek 的可见处理步骤、文件解析情况、证据卡片、风险提示和资产产出建议。</p>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../utils/api.js'

const router = useRouter()
const fileInput = ref(null)
const files = ref([])
const manualText = ref('')
const isDragging = ref(false)
const isAnalyzing = ref(false)
const errorText = ref('')
const analysis = ref(null)
const workflowState = ref('idle')
const selectedTemplateId = ref('jasmine')
const assetDraft = ref('')
const assetMessages = ref([])
const chatLoading = ref(false)
const chatError = ref('')
const chatRecommendations = ref([])
const chatNextActions = ref([])
const copyStatus = ref('')
const studioCreating = ref(false)
const studioError = ref('')
const studioStatus = ref('')
const reviewChecks = ref({})

const supportedFormats = ['PDF', 'DOCX', 'XLSX', 'CSV', 'TXT', 'MD', 'JSON', 'IMG']
const assetPrompts = [
  '帮我规划海报、白皮书和大屏的生产顺序',
  '把这个资产包改成更适合招商路演',
  '指出当前证据链最大的风险',
  '给我三种视觉风格和色系方向',
]

const templates = [
  { id: 'jasmine', name: '茉莉茶饮', origin: '广西横州 / 福建宁德', summary: '围绕窨制工艺、花茶双产地和现代茶饮渠道生成品牌资产。' },
  { id: 'coconut', name: '生椰饮品', origin: '海南文昌', summary: '围绕热带原料、冷链加工和年轻消费场景生成品牌资产。' },
  { id: 'pepper', name: '汉源花椒', origin: '四川雅安', summary: '围绕贡椒产地、山地生态和麻香指标生成实证型品牌资产。' },
  { id: 'rice', name: '五常大米', origin: '黑龙江五常', summary: '围绕寒地黑土、稻作周期和食味指标生成空间叙事。' },
]

const selectedTemplate = computed(() => templates.find(item => item.id === selectedTemplateId.value) || templates[0])
const canAnalyze = computed(() => files.value.length > 0 || manualText.value.trim().length >= 20)
const packageData = computed(() => analysis.value?.asset_package || emptyPackage())
const thinkingTrace = computed(() => analysis.value?.thinking_trace || [])
const extractionFiles = computed(() => analysis.value?.extraction?.files || [])
const productName = computed(() => packageData.value.product.name || selectedTemplate.value.name)
const citationList = computed(() => Array.isArray(packageData.value.citations) ? packageData.value.citations : [])
const reviewStatus = computed(() => packageData.value.review_status || { status: 'pending', summary: '证据尚未人工复核。', required_items: [] })
const reviewItems = computed(() => Array.isArray(reviewStatus.value.required_items) ? reviewStatus.value.required_items : [])
const reviewedCount = computed(() => reviewItems.value.filter((item, index) => isReviewed(item, index)).length)

const progressPercent = computed(() => {
  const map = { idle: 0, uploading: 22, extracting: 45, thinking: 72, done: 100, error: 0 }
  return map[workflowState.value] ?? 0
})

const visibleSteps = computed(() => {
  const order = ['uploading', 'extracting', 'thinking', 'done']
  const activeIndex = order.indexOf(workflowState.value)
  const doneIndex = workflowState.value === 'done' ? order.length : activeIndex
  return [
    { key: 'uploading', index: '01', title: '接收资料', detail: `${files.value.length} 个文件，${manualText.value.trim() ? '含补充说明' : '无补充说明'}` },
    { key: 'extracting', index: '02', title: '解析格式', detail: '提取 PDF/DOCX/XLSX/CSV/文本内容，记录图片素材。' },
    { key: 'thinking', index: '03', title: 'DeepSeek 分析', detail: '生成用户可见的分析步骤、证据、风险和视觉方向。' },
    { key: 'done', index: '04', title: '资产包产出', detail: '沉淀为海报、白皮书、大屏和 Studio 编辑建议。' },
  ].map((step, index) => ({
    ...step,
    status: workflowState.value === step.key ? 'active' : index < doneIndex ? 'done' : 'pending',
  }))
})

const scoreCards = computed(() => {
  const scores = packageData.value.scores
  return [
    { label: '资料完整度', value: scores.completeness },
    { label: '证据强度', value: scores.evidence_strength },
    { label: '可视化适配', value: scores.visualization_fit },
    { label: '风险', value: scores.risk },
  ]
})

const evidenceList = computed(() => [
  ...toTextList(packageData.value.evidence.lab_indicators),
  ...toTextList(packageData.value.evidence.certifications),
  ...toTextList(packageData.value.evidence.origin_claims),
  ...toTextList(packageData.value.evidence.process_steps),
].slice(0, 8))

const riskList = computed(() => {
  const risks = toTextList(packageData.value.risks)
  return risks.length ? risks : ['暂无高风险项，但仍建议人工复核检测指标、产地证明和宣传表述。']
})

const generatedAssets = computed(() => {
  const brand = packageData.value.brand_assets
  return [
    { title: '营销海报', desc: firstText(brand.poster_copy) || '提炼主视觉、卖点文案、短句和传播标题。' },
    { title: '实证白皮书', desc: firstText(brand.whitepaper_outline) || '组织检测指标、产地证据、工艺流程和风险说明。' },
    { title: '智慧大屏', desc: firstText(brand.dashboard_cards) || firstText(packageData.value.visualization.map_nodes) || '生成空间节点、时间线和证据面板。' },
    { title: '视觉方向', desc: firstText(brand.style_direction) || firstText(brand.layout_direction) || '给出色系、版式、材质和渠道适配建议。' },
  ]
})

const businessSteps = computed(() => {
  const scores = packageData.value.scores
  return [
    {
      index: '01',
      title: '资料解析',
      detail: `${extractionFiles.value.length} 个资料源已进入解析记录。`,
      ready: extractionFiles.value.length > 0,
    },
    {
      index: '02',
      title: '证据审核',
      detail: scores.evidence_strength >= 60 ? '证据强度可进入内容生产。' : '建议补充检测报告、认证或产地证明。',
      ready: scores.evidence_strength >= 60,
    },
    {
      index: '03',
      title: 'AI 共创',
      detail: assetMessages.value.length ? '已有对话建议，可继续细化输出方向。' : '使用下方对话框继续细化海报、白皮书和大屏。',
      ready: assetMessages.value.length > 0,
    },
    {
      index: '04',
      title: 'Studio 编辑',
      detail: '进入 Studio 后可继续编辑海报文案、主题、图片焦点和导出结果。',
      ready: scores.visualization_fit >= 50,
    },
    {
      index: '05',
      title: '交付导出',
      detail: '复制或下载 JSON，作为资产包记录和后续人工复核依据。',
      ready: Boolean(analysis.value),
    },
  ]
})

const reviewStatusLabel = computed(() => {
  const labels = {
    pending: '等待人工复核',
    needs_review: '需要重点复核',
    in_review: '复核进行中',
    approved: '已复核通过',
    rejected: '复核未通过',
  }
  return labels[reviewStatus.value.status] || '等待人工复核'
})

function onDrop(event) {
  isDragging.value = false
  addFiles(event.dataTransfer.files)
}

function onFileInput(event) {
  addFiles(event.target.files)
  event.target.value = ''
}

function addFiles(fileList) {
  const incoming = Array.from(fileList || []).map(file => ({
    id: `${file.name}-${file.size}-${file.lastModified}`,
    file,
    name: file.name,
    size: formatSize(file.size),
    kind: inferKind(file.name),
  }))
  files.value = [...files.value, ...incoming]
  analysis.value = null
  errorText.value = ''
  workflowState.value = 'idle'
}

function removeFile(id) {
  files.value = files.value.filter(file => file.id !== id)
}

function resetAll() {
  files.value = []
  manualText.value = ''
  analysis.value = null
  errorText.value = ''
  workflowState.value = 'idle'
}

async function analyzeAssets() {
  if (!canAnalyze.value || isAnalyzing.value) return
  isAnalyzing.value = true
  errorText.value = ''
  analysis.value = null
  workflowState.value = 'uploading'

  try {
    const form = new FormData()
    files.value.forEach(item => form.append('files', item.file))
    form.append('manual_text', manualText.value)
    form.append('template_id', selectedTemplate.value.id)
    form.append('product_hint', selectedTemplate.value.name)
    form.append('origin_hint', selectedTemplate.value.origin)

    workflowState.value = 'extracting'
    const response = await fetch('/api/assets/analyze-files', {
      method: 'POST',
      body: form,
    })

    workflowState.value = 'thinking'
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`)

    analysis.value = data
    assetMessages.value = []
    chatRecommendations.value = []
    chatNextActions.value = []
    studioError.value = ''
    studioStatus.value = ''
    reviewChecks.value = {}
    workflowState.value = 'done'
  } catch (error) {
    workflowState.value = 'error'
    errorText.value = `分析失败：${error.message}`
  } finally {
    isAnalyzing.value = false
  }
}

async function createStudioProject(outputType = 'poster') {
  if (!analysis.value || studioCreating.value) return
  studioError.value = ''
  studioStatus.value = ''

  if (!localStorage.getItem('auth_token')) {
    studioError.value = '需要先登录，才能把资产包保存为 Studio 项目。登录后请回到本页重新点击创建。'
    return
  }

  studioCreating.value = true
  try {
    const response = await api('/api/studio/projects/from-asset-package', {
      method: 'POST',
      body: JSON.stringify({
        asset_package: packageData.value,
        extraction: analysis.value.extraction || {},
        template_id: selectedTemplate.value.id,
        output_type: outputType,
        name: `${productName.value} · ${outputLabel(outputType)}项目`,
      }),
    })
    if (!response.ok) throw new Error(response.error || response.detail || 'Studio 项目创建失败')
    const projectId = response.data?.project?.id
    studioStatus.value = 'Studio 项目已创建，正在打开编辑器。'
    router.push({
      path: '/studio',
      query: {
        project: projectId,
        source: 'asset-generator',
      },
    })
  } catch (error) {
    studioError.value = `创建 Studio 项目失败：${error.message}`
  } finally {
    studioCreating.value = false
  }
}

async function askAssetQuestion(prompt) {
  assetDraft.value = prompt
  await sendAssetChat()
}

async function sendAssetChat() {
  const content = assetDraft.value.trim()
  if (!content || chatLoading.value || !analysis.value) return
  const userMessage = { id: crypto.randomUUID(), role: 'user', content }
  assetMessages.value.push(userMessage)
  assetDraft.value = ''
  chatLoading.value = true
  chatError.value = ''

  try {
    const response = await fetch('/api/assets/asset-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: assetMessages.value.map(({ role, content }) => ({ role, content })),
        asset_package: packageData.value,
        extraction: analysis.value.extraction,
      }),
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`)
    assetMessages.value.push({
      id: crypto.randomUUID(),
      role: 'assistant',
      content: data.reply || '我已经根据当前资产包生成建议。',
    })
    chatRecommendations.value = Array.isArray(data.recommendations) ? data.recommendations : []
    chatNextActions.value = Array.isArray(data.next_actions) ? data.next_actions : []
  } catch (error) {
    chatError.value = `AI 对话失败：${error.message}`
  } finally {
    chatLoading.value = false
  }
}

async function copyPackage() {
  if (!analysis.value) return
  const text = JSON.stringify(analysis.value, null, 2)
  try {
    await navigator.clipboard.writeText(text)
    copyStatus.value = '资产包 JSON 已复制。'
  } catch {
    copyStatus.value = '复制失败，请使用下载 JSON。'
  } finally {
    setTimeout(() => { copyStatus.value = '' }, 1800)
  }
}

function downloadPackage() {
  if (!analysis.value) return
  const blob = new Blob([JSON.stringify(analysis.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${selectedTemplate.value.id}-asset-package.json`
  link.click()
  URL.revokeObjectURL(url)
}

function fillTemplateText() {
  manualText.value = `${selectedTemplate.value.name}来自${selectedTemplate.value.origin}。资料包含产地环境、核心原料、加工工艺、检测指标、品牌定位和目标消费场景。希望生成一套空间品牌资产：营销海报突出风味卖点和视觉记忆点，白皮书突出检测指标和产地证据，智慧大屏突出产地节点、传播路径和供应链可信度。`
}

function openOutput(path) {
  router.push({
    path,
    query: {
      case: selectedTemplate.value.id,
      source: 'asset-generator',
    },
  })
}

function outputLabel(type) {
  return {
    poster: '海报',
    archive: '白皮书',
    display: '大屏',
  }[type] || '产出'
}

function reviewKey(item, index) {
  return `${item.label || 'review'}-${index}`
}

function isReviewed(item, index) {
  return Boolean(reviewChecks.value[reviewKey(item, index)])
}

function toggleReview(item, index, checked) {
  reviewChecks.value = {
    ...reviewChecks.value,
    [reviewKey(item, index)]: Boolean(checked),
  }
}

function reviewItemLabel(item, index) {
  if (isReviewed(item, index)) return '已标记复核'
  const labels = {
    pending: '待复核',
    needs_review: '需重点复核',
    in_review: '复核中',
    approved: '模型判断通过',
    rejected: '模型判断不通过',
  }
  return labels[item.status] || '待复核'
}

function inferKind(name) {
  const suffix = name.split('.').pop()?.toUpperCase() || 'FILE'
  if (['PNG', 'JPG', 'JPEG', 'WEBP'].includes(suffix)) return 'IMG'
  return suffix
}

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function firstText(value) {
  return toTextList(value)[0] || ''
}

function toTextList(value) {
  if (!Array.isArray(value)) return []
  return value.map(item => {
    if (typeof item === 'string') return item
    if (item && typeof item === 'object') {
      return item.title || item.name || item.label || item.desc || item.description || JSON.stringify(item)
    }
    return String(item)
  }).filter(Boolean)
}

function emptyPackage() {
  return {
    product: {},
    evidence: { lab_indicators: [], certifications: [], origin_claims: [], process_steps: [] },
    visualization: { map_nodes: [], routes: [], timeline: [], radar_metrics: [] },
    brand_assets: { poster_copy: [], whitepaper_outline: [], dashboard_cards: [], style_direction: [], layout_direction: [] },
    scores: { completeness: 0, evidence_strength: 0, visualization_fit: 0, risk: 0 },
    risks: [],
    citations: [],
    review_status: { status: 'pending', summary: '证据尚未人工复核。', required_items: [] },
  }
}
</script>

<style scoped>
.asset-page {
  min-height: 100vh;
  padding: calc(var(--navbar-h) + 32px) clamp(32px, 4vw, 64px) 42px;
  background: #f5f1e9;
  color: var(--text);
}

.asset-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 28px;
  margin-bottom: 22px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(74, 65, 55, 0.14);
}

.asset-header h1,
.panel-head h2,
.result-card h2 {
  margin: 4px 0 0;
  font-family: var(--font-serif);
  color: var(--text);
}

.asset-header h1 {
  font-size: 42px;
}

.asset-header p {
  max-width: 780px;
  margin: 10px 0 0;
  color: var(--text-mid);
  line-height: 1.7;
}

.eyebrow {
  color: var(--earth);
  font-size: 10px;
  font-weight: 850;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.format-strip {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  max-width: 360px;
}

.format-strip span {
  border: 1px solid rgba(139, 94, 52, 0.22);
  border-radius: 999px;
  padding: 6px 10px;
  background: rgba(255, 252, 247, 0.72);
  color: var(--earth);
  font-size: 11px;
  font-weight: 800;
}

.asset-workspace {
  display: grid;
  grid-template-columns: 430px minmax(0, 1fr);
  gap: 18px;
}

.input-panel,
.output-panel > *,
.result-card {
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 8px;
  background: rgba(255, 252, 247, 0.84);
  box-shadow: 0 16px 42px rgba(32, 27, 22, 0.07);
}

.input-panel {
  padding: 16px;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.panel-head.compact {
  align-items: center;
}

.panel-head h2 {
  font-size: 22px;
}

.ghost-btn,
.section-title button,
.file-row button {
  border: 0;
  background: transparent;
  color: var(--earth);
  cursor: pointer;
  font-size: 12px;
  font-weight: 800;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}

.template-card {
  min-height: 74px;
  border: 1px solid rgba(74, 65, 55, 0.14);
  border-radius: 6px;
  background: rgba(246, 243, 235, 0.7);
  color: var(--text);
  cursor: pointer;
  padding: 11px;
  text-align: left;
}

.template-card.active {
  border-color: rgba(139, 94, 52, 0.42);
  background: rgba(139, 94, 52, 0.08);
}

.template-card strong,
.template-card span {
  display: block;
}

.template-card span {
  margin-top: 6px;
  color: var(--text-muted);
  font-size: 11px;
}

.dropzone {
  display: grid;
  place-items: center;
  min-height: 220px;
  border: 1.5px dashed rgba(94, 123, 80, 0.35);
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(255, 252, 247, 0.9), rgba(234, 230, 219, 0.65));
  cursor: pointer;
  padding: 20px;
  text-align: center;
}

.dropzone.dragging {
  border-color: var(--earth);
  background: rgba(139, 94, 52, 0.08);
}

.dropzone input {
  display: none;
}

.upload-mark {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 999px;
  background: var(--leaf);
  color: #fffaf3;
  font-size: 28px;
  font-weight: 300;
}

.dropzone strong {
  margin-top: 12px;
}

.dropzone small {
  max-width: 320px;
  margin-top: 8px;
  color: var(--text-muted);
  line-height: 1.6;
}

.file-list,
.manual-block {
  margin-top: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
  color: var(--text-mid);
  font-size: 12px;
  font-weight: 850;
}

.section-title small {
  color: var(--text-muted);
  font-weight: 700;
}

.empty-box,
.file-row,
.extract-row {
  border: 1px solid rgba(74, 65, 55, 0.1);
  border-radius: 6px;
  background: rgba(246, 243, 235, 0.58);
  padding: 10px;
}

.empty-box {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.6;
}

.file-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
}

.file-row strong,
.file-row small {
  display: block;
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-row small {
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 11px;
}

textarea {
  width: 100%;
  min-height: 130px;
  resize: vertical;
  border: 1px solid rgba(74, 65, 55, 0.15);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.9);
  color: var(--text);
  font: inherit;
  line-height: 1.6;
  outline: none;
  padding: 10px;
}

.primary-btn,
.action-row button {
  min-height: 42px;
  border: 0;
  border-radius: 6px;
  background: var(--text);
  color: #fffaf3;
  cursor: pointer;
  font-weight: 850;
  padding: 0 14px;
}

.primary-btn {
  width: 100%;
  margin-top: 14px;
}

.primary-btn:disabled {
  cursor: not-allowed;
  opacity: 0.48;
}

.action-row button:disabled {
  cursor: not-allowed;
  opacity: 0.52;
}

.error-text {
  margin: 10px 0 0;
  color: var(--carmine);
  font-size: 12px;
  line-height: 1.6;
}

.output-panel {
  min-width: 0;
}

.progress-card {
  padding: 16px;
}

.progress-card strong {
  color: var(--earth);
}

.progress-track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(74, 65, 55, 0.12);
}

.progress-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--earth), var(--leaf));
  transition: width 220ms ease;
}

.timeline {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.timeline li {
  display: flex;
  gap: 10px;
  min-height: 76px;
  border: 1px solid rgba(74, 65, 55, 0.1);
  border-radius: 6px;
  background: rgba(246, 243, 235, 0.55);
  padding: 10px;
}

.timeline li.active {
  border-color: rgba(139, 94, 52, 0.4);
  background: rgba(139, 94, 52, 0.08);
}

.timeline li.done {
  border-color: rgba(94, 123, 80, 0.28);
  background: rgba(94, 123, 80, 0.08);
}

.timeline span {
  color: var(--earth);
  font-family: Georgia, serif;
  font-weight: 850;
}

.timeline strong,
.timeline small {
  display: block;
}

.timeline small {
  margin-top: 5px;
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.45;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 14px;
}

.result-card {
  min-width: 0;
  padding: 16px;
}

.result-card.wide,
.hero-result {
  grid-column: 1 / -1;
}

.hero-result p {
  margin: 10px 0 0;
  color: var(--text-mid);
  line-height: 1.6;
}

.score-grid,
.asset-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.score-grid div,
.asset-grid article {
  border: 1px solid rgba(74, 65, 55, 0.1);
  border-radius: 6px;
  background: rgba(246, 243, 235, 0.64);
  padding: 12px;
}

.score-grid span,
.score-grid strong {
  display: block;
}

.score-grid span {
  color: var(--text-muted);
  font-size: 11px;
}

.score-grid strong {
  margin-top: 6px;
  color: var(--leaf);
  font-size: 22px;
}

.plain-list {
  display: grid;
  gap: 8px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}

.plain-list li {
  border-left: 3px solid rgba(94, 123, 80, 0.36);
  background: rgba(246, 243, 235, 0.64);
  color: var(--text-mid);
  padding: 8px 10px;
  line-height: 1.55;
}

.plain-list.warning li {
  border-left-color: rgba(198, 61, 66, 0.42);
}

.citation-list,
.review-list {
  display: grid;
  gap: 9px;
  margin-top: 10px;
}

.citation-list article {
  position: relative;
  border: 1px solid rgba(74, 65, 55, 0.11);
  border-radius: 6px;
  background: rgba(246, 243, 235, 0.64);
  padding: 10px 48px 10px 10px;
}

.citation-list strong,
.citation-list small,
.citation-list p,
.citation-list span {
  display: block;
}

.citation-list strong {
  color: var(--text);
  font-size: 12px;
}

.citation-list small {
  margin-top: 4px;
  color: var(--earth);
  font-size: 10px;
  font-weight: 800;
}

.citation-list p {
  margin: 8px 0 0;
  color: var(--text-mid);
  font-size: 12px;
  line-height: 1.55;
}

.citation-list > article > span {
  position: absolute;
  top: 10px;
  right: 10px;
  border-radius: 4px;
  background: rgba(94, 123, 80, 0.12);
  color: var(--leaf);
  font-size: 10px;
  font-weight: 850;
  padding: 4px 6px;
}

.review-summary {
  border: 1px solid rgba(94, 123, 80, 0.16);
  border-radius: 6px;
  background: rgba(94, 123, 80, 0.07);
  padding: 10px;
}

.review-summary strong,
.review-summary p,
.review-summary small {
  display: block;
}

.review-summary strong {
  color: var(--leaf);
  font-size: 13px;
}

.review-summary p {
  margin: 6px 0 0;
  color: var(--text-mid);
  font-size: 12px;
  line-height: 1.55;
}

.review-summary small {
  margin-top: 7px;
  color: var(--text-muted);
  font-size: 11px;
}

.review-list label {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  border: 1px solid rgba(74, 65, 55, 0.1);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.7);
  padding: 9px;
  cursor: pointer;
}

.review-list input {
  margin-top: 3px;
  accent-color: var(--leaf);
}

.review-list strong,
.review-list small {
  display: block;
}

.review-list strong {
  color: var(--text);
  font-size: 12px;
}

.review-list small {
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.45;
}

.extract-row {
  margin-top: 8px;
}

.extract-row strong,
.extract-row small {
  display: block;
}

.extract-row small {
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 11px;
}

.extract-row p,
.asset-grid p {
  margin: 8px 0 0;
  color: var(--text-mid);
  font-size: 12px;
  line-height: 1.55;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.business-flow {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.business-flow article {
  min-height: 132px;
  border: 1px solid rgba(74, 65, 55, 0.1);
  border-radius: 6px;
  background: rgba(246, 243, 235, 0.64);
  padding: 12px;
}

.business-flow article.ready {
  border-color: rgba(94, 123, 80, 0.28);
  background: rgba(94, 123, 80, 0.08);
}

.business-flow span,
.business-flow strong,
.business-flow p {
  display: block;
}

.business-flow span {
  color: var(--earth);
  font-family: Georgia, serif;
  font-weight: 850;
}

.business-flow strong {
  margin-top: 8px;
  color: var(--text);
  font-size: 13px;
}

.business-flow p {
  margin: 8px 0 0;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.5;
}

.status-text {
  margin: 10px 0 0;
  color: var(--leaf);
  font-size: 12px;
  font-weight: 800;
}

.ai-chat-card {
  background: rgba(249, 252, 245, 0.88);
}

.chat-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.chat-head h2 {
  margin: 5px 0 0;
  color: var(--leaf);
  font-family: var(--font-serif);
  font-size: 22px;
}

.chat-head button,
.quick-chat button,
.asset-chat-form button {
  border: 0;
  border-radius: 5px;
  background: var(--leaf);
  color: #fffaf3;
  cursor: pointer;
  font-size: 12px;
  font-weight: 850;
  padding: 9px 12px;
}

.chat-head button:disabled,
.quick-chat button:disabled,
.asset-chat-form button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.quick-chat {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.quick-chat button {
  background: rgba(94, 123, 80, 0.12);
  color: var(--leaf);
}

.asset-chat-log {
  display: grid;
  gap: 8px;
  max-height: 260px;
  overflow-y: auto;
  margin-top: 12px;
}

.asset-message,
.chat-placeholder {
  border: 1px solid rgba(74, 65, 55, 0.1);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.78);
  padding: 10px;
}

.chat-placeholder {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.6;
}

.asset-message.assistant {
  border-color: rgba(94, 123, 80, 0.2);
}

.asset-message span {
  color: var(--earth);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.asset-message.assistant span {
  color: var(--leaf);
}

.asset-message p {
  margin: 5px 0 0;
  color: var(--text-mid);
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.recommendation-grid article {
  border-left: 3px solid rgba(94, 123, 80, 0.42);
  background: rgba(255, 252, 247, 0.72);
  padding: 10px;
}

.recommendation-grid span,
.recommendation-grid strong,
.recommendation-grid p {
  display: block;
}

.recommendation-grid span {
  color: var(--earth);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.recommendation-grid strong {
  margin-top: 5px;
  color: var(--text);
}

.recommendation-grid p {
  margin: 7px 0 0;
  color: var(--text-mid);
  font-size: 12px;
  line-height: 1.55;
}

.asset-chat-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  margin-top: 12px;
}

.asset-chat-form textarea {
  min-height: 62px;
}

.empty-preview {
  display: grid;
  place-items: center;
  min-height: 420px;
  padding: 40px;
  text-align: center;
}

.empty-preview h2 {
  margin: 8px 0 0;
  font-family: var(--font-serif);
  font-size: 30px;
}

.empty-preview p {
  max-width: 440px;
  color: var(--text-muted);
  line-height: 1.7;
}
</style>
