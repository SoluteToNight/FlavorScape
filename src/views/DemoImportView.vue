<template>
  <main class="import-page">
    <section class="hero-strip">
      <div>
        <span class="eyebrow">Spatial Brand Asset Package</span>
        <h1>空间品牌资产生成器</h1>
        <p>上传检测报告、品牌资料和产地信息，生成营销海报、实证白皮书与智慧大屏。</p>
      </div>
      <div class="status-badge">资产生成器</div>
    </section>

    <section class="workspace-grid">
      <div class="upload-panel">
        <div class="template-block">
          <div class="section-title">
            <span>选择案例模板</span>
            <small>{{ selectedTemplate.origin }}</small>
          </div>
          <div class="template-grid">
            <button
              v-for="item in productTemplates"
              :key="item.id"
              type="button"
              class="template-card"
              :class="{ active: item.id === selectedTemplateId }"
              @click="selectTemplate(item.id)"
            >
              <strong>{{ item.name }}</strong>
              <span>{{ item.origin }}</span>
            </button>
          </div>
        </div>

        <div
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
            accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.png,.jpg,.jpeg"
            @change="onFileInput"
          />
          <div class="upload-icon">↑</div>
          <h2>拖拽资料到这里</h2>
          <p>支持检测报告、品牌介绍、产地证明、产品图片等材料，系统将根据资料类型生成品牌资产包。</p>
          <button type="button" @click="fileInput?.click()">选择本地文件</button>
        </div>

        <div class="file-list">
          <div class="section-title">
            <span>资料清单</span>
            <button v-if="files.length" type="button" @click="clearFiles">清空</button>
          </div>
          <div v-if="!files.length" class="empty-state">也可以先使用当前案例模板资料，快速生成一套空间品牌资产包。</div>
          <div v-for="file in files" :key="file.id" class="file-row">
            <div>
              <strong>{{ file.name }}</strong>
              <small>{{ file.size }} · {{ file.type }}</small>
            </div>
            <span>{{ file.stage }}</span>
          </div>
        </div>

        <div class="ai-panel">
          <div class="section-title">
            <span>DeepSeek 文档分析</span>
            <button type="button" @click="fillTemplateText">填入模板示例</button>
          </div>
          <textarea
            v-model="documentText"
            placeholder="粘贴产品说明、检测报告摘要、品牌资料、产地证明或工艺流程文本。当前版本先分析文本；PDF/DOCX 自动解析可在后端继续扩展。"
          ></textarea>
          <div class="ai-actions">
            <small>模型会输出产品、证据、空间可视化、品牌资产与风险评分。</small>
            <button type="button" :disabled="isAnalyzing" @click="analyzeDocumentText">
              {{ isAnalyzing ? '分析中...' : 'DeepSeek 分析文档' }}
            </button>
          </div>
          <p v-if="analysisError" class="error-text">{{ analysisError }}</p>
        </div>
      </div>

      <aside class="process-panel">
        <div class="notice">
          当前流程不会保存原始文件，生成结果将进入营销海报、实证白皮书与智慧大屏模块。
        </div>

        <div class="score-card">
          <div>
            <span class="score-label">{{ aiPackage ? 'AI 可视化适配度' : '资料完整度' }}</span>
            <strong>{{ completenessScore }}%</strong>
          </div>
          <div class="score-track">
            <div class="score-fill" :style="{ width: `${completenessScore}%` }"></div>
          </div>
          <p>{{ completenessHint }}</p>
        </div>

        <div v-if="aiPackage" class="ai-summary">
          <div class="package-head">
            <div>
              <span>识别产品</span>
              <strong>{{ aiProductName }}</strong>
            </div>
            <small>{{ aiPackage.product.origin || selectedTemplate.origin }}</small>
          </div>
          <div class="score-grid">
            <div v-for="item in aiScores" :key="item.label">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
          <div class="insight-list">
            <strong>可视化建议</strong>
            <p v-for="item in visualizationHints" :key="item">{{ item }}</p>
          </div>
        </div>

        <div class="requirements">
          <div v-for="item in materialChecks" :key="item.key" class="requirement-card" :class="{ ready: item.ready }">
            <span>{{ item.index }}</span>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.ready ? '已具备，可参与资产生成。' : item.desc }}</p>
            </div>
          </div>
        </div>

        <button class="generate-btn" type="button" :disabled="isGenerating" @click="startGeneration">
          {{ isGenerating ? '生成中...' : '生成空间品牌资产包' }}
        </button>

        <div v-if="isGenerating || completed" class="progress-box">
          <div class="progress-head">
            <span>{{ activeStep }}</span>
            <strong>{{ progress }}%</strong>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
          </div>
          <ol>
            <li
              v-for="(step, index) in steps"
              :key="step"
              :class="{ active: index === currentStepIndex, done: index < currentStepIndex || completed }"
            >
              {{ step }}
            </li>
          </ol>
        </div>

        <div v-if="completed" class="result-box">
          <div class="package-head">
            <div>
              <span>资产包编号</span>
              <strong>{{ packageId }}</strong>
            </div>
            <small>{{ aiProductName || selectedTemplate.name }}</small>
          </div>
          <p>{{ aiSummary || selectedTemplate.summary }}</p>
          <div class="asset-grid">
            <div v-for="asset in generatedAssets" :key="asset.title" class="asset-card">
              <strong>{{ asset.title }}</strong>
              <span>{{ asset.desc }}</span>
            </div>
          </div>
          <div class="result-actions">
            <button type="button" @click="openOutput('/marketing')">查看营销海报</button>
            <button type="button" @click="openOutput('/archive')">查看实证白皮书</button>
            <button type="button" @click="openOutput('/brand')">查看智慧大屏</button>
          </div>
        </div>
      </aside>
    </section>
  </main>
</template>

<script setup>
import { computed, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const fileInput = ref(null)
const files = ref([])
const isDragging = ref(false)
const isGenerating = ref(false)
const isAnalyzing = ref(false)
const completed = ref(false)
const progress = ref(0)
const currentStepIndex = ref(0)
const selectedTemplateId = ref('jasmine')
const documentText = ref('')
const analysisError = ref('')
const aiPackage = ref(null)
let timer = null

const productTemplates = [
  { id: 'jasmine', name: '茉莉风味产品', origin: '广西横州', summary: '围绕茉莉花窨制、香气证据和产地场景生成一套空间品牌表达。' },
  { id: 'coconut', name: '生椰风味产品', origin: '海南文昌', summary: '围绕热带原料、冷链加工和年轻消费场景生成品牌资产。' },
  { id: 'pepper', name: '汉源花椒', origin: '四川雅安', summary: '围绕贡椒产地、山地生态和麻香指标生成实证型品牌资产。' },
  { id: 'ham', name: '宣威火腿', origin: '云南宣威', summary: '围绕发酵工艺、山地气候和非遗叙事生成传播资产。' },
]

const steps = ['读取资料包', '提取产地与检测指标', '匹配空间节点', '生成海报、白皮书与智慧大屏']

const selectedTemplate = computed(() => productTemplates.find((item) => item.id === selectedTemplateId.value) || productTemplates[0])
const activeStep = computed(() => steps[currentStepIndex.value] || '生成完成')
const packageId = computed(() => `PKG-${selectedTemplate.value.id.toUpperCase()}-${new Date().getFullYear()}`)

const materialChecks = computed(() => {
  const hasReport = hasType('检测报告')
  const hasBrand = hasType('品牌资料')
  const hasOrigin = hasType('产地信息')
  return [
    { key: 'report', index: '01', title: '检测报告', desc: '缺少检测报告时，实证背书会偏弱。', ready: hasReport },
    { key: 'brand', index: '02', title: '品牌资料', desc: '缺少品牌资料时，营销文案会偏模板化。', ready: hasBrand },
    { key: 'origin', index: '03', title: '产地信息', desc: '缺少产地信息时，空间叙事会偏弱。', ready: hasOrigin },
  ]
})

const completenessScore = computed(() => {
  if (aiPackage.value) return aiPackage.value.scores.visualization_fit
  if (!files.value.length) return 100
  const readyCount = materialChecks.value.filter((item) => item.ready).length
  return Math.round((readyCount / materialChecks.value.length) * 100)
})

const completenessHint = computed(() => {
  if (aiPackage.value) {
    return `AI 已完成结构化分析：证据强度 ${aiPackage.value.scores.evidence_strength}%，资料完整度 ${aiPackage.value.scores.completeness}%，风险 ${aiPackage.value.scores.risk}%。`
  }
  if (!files.value.length) return '当前将使用案例模板资料，快速生成完整资产包。'
  if (completenessScore.value === 100) return '资料类型完整，可生成完整资产包。'
  if (completenessScore.value >= 67) return '资料基本可用，但部分成果会使用模板补全。'
  return '资料不足，建议补充检测、品牌或产地材料。'
})

const aiProductName = computed(() => aiPackage.value?.product?.name || '')

const aiSummary = computed(() => {
  if (!aiPackage.value) return ''
  const slogan = aiPackage.value.brand_assets.slogan
  if (slogan) return slogan
  return `${aiProductName.value || selectedTemplate.value.name}适合围绕产地、工艺、检测证据与传播路径生成空间品牌资产。`
})

const aiScores = computed(() => {
  const scores = aiPackage.value?.scores || {}
  return [
    { label: '完整度', value: `${scores.completeness ?? 0}%` },
    { label: '证据强度', value: `${scores.evidence_strength ?? 0}%` },
    { label: '可视化', value: `${scores.visualization_fit ?? 0}%` },
    { label: '风险', value: `${scores.risk ?? 0}%` },
  ]
})

const visualizationHints = computed(() => {
  if (!aiPackage.value) return []
  const data = aiPackage.value.visualization
  return [
    ...toTextList(data.map_nodes).slice(0, 2).map((item) => `地图节点：${item}`),
    ...toTextList(data.routes).slice(0, 2).map((item) => `传播路线：${item}`),
    ...toTextList(data.timeline).slice(0, 2).map((item) => `时间轴：${item}`),
  ].slice(0, 5)
})

const generatedAssets = computed(() => {
  if (!aiPackage.value) {
    return [
      { title: '营销海报', desc: `${selectedTemplate.value.name}传播封面、卖点文案与视觉锚点。` },
      { title: '实证白皮书', desc: '检测指标、产地证据、工艺说明与可信背书。' },
      { title: '智慧大屏', desc: `${selectedTemplate.value.origin}空间节点、路径与品牌叙事。` },
      { title: '分享资产', desc: '分享链接、嵌入代码与后续导出入口。' },
    ]
  }
  const assets = aiPackage.value.brand_assets
  const evidence = aiPackage.value.evidence
  return [
    { title: '营销海报', desc: firstText(assets.poster_copy) || `${aiProductName.value}传播封面、卖点文案与视觉锚点。` },
    { title: '实证白皮书', desc: firstText(assets.whitepaper_outline) || firstText(evidence.lab_indicators) || '检测指标、产地证据、工艺说明与可信背书。' },
    { title: '智慧大屏', desc: firstText(assets.dashboard_cards) || firstText(aiPackage.value.visualization.map_nodes) || `${selectedTemplate.value.origin}空间节点、路径与品牌叙事。` },
    { title: '风险与审核', desc: firstText(aiPackage.value.risks) || '未发现明显高风险项，建议进入人工复核。' },
  ]
})

function selectTemplate(id) {
  selectedTemplateId.value = id
  completed.value = false
  aiPackage.value = null
  analysisError.value = ''
}

function clearFiles() {
  files.value = []
  completed.value = false
  aiPackage.value = null
  analysisError.value = ''
}

function onDrop(event) {
  isDragging.value = false
  addFiles(event.dataTransfer.files)
}

function onFileInput(event) {
  addFiles(event.target.files)
  event.target.value = ''
}

function addFiles(fileList) {
  const incoming = Array.from(fileList).map((file) => ({
    id: `${file.name}-${file.size}-${file.lastModified}`,
    name: file.name,
    size: formatSize(file.size),
    type: inferType(file.name),
    stage: '待识别',
  }))
  files.value = [...files.value, ...incoming]
  completed.value = false
}

async function analyzeDocumentText() {
  analysisError.value = ''
  const text = documentText.value.trim()
  if (text.length < 20) {
    analysisError.value = '请先粘贴至少 20 个字的产品文档文本，或使用模板示例。'
    return false
  }

  isAnalyzing.value = true
  try {
    const res = await fetch('/api/assets/analyze-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        template_id: selectedTemplate.value.id,
        product_hint: selectedTemplate.value.name,
        origin_hint: selectedTemplate.value.origin,
        file_names: files.value.map((file) => file.name),
      }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      throw new Error(data.detail || `HTTP ${res.status}`)
    }
    aiPackage.value = data.asset_package
    completed.value = true
    progress.value = 100
    currentStepIndex.value = steps.length
    return true
  } catch (err) {
    analysisError.value = `DeepSeek 分析失败：${err.message}`
    return false
  } finally {
    isAnalyzing.value = false
  }
}

async function startGeneration() {
  if (isGenerating.value) return
  if (!files.value.length) addTemplateFiles()
  if (documentText.value.trim() && !aiPackage.value) {
    const ok = await analyzeDocumentText()
    if (!ok) return
  }

  completed.value = false
  isGenerating.value = true
  progress.value = 0
  currentStepIndex.value = 0
  clearInterval(timer)

  timer = setInterval(() => {
    progress.value = Math.min(progress.value + 4, 100)
    currentStepIndex.value = Math.min(Math.floor(progress.value / 25), steps.length - 1)
    if (progress.value >= 100) {
      clearInterval(timer)
      isGenerating.value = false
      completed.value = true
      currentStepIndex.value = steps.length
    }
  }, 140)
}

function addTemplateFiles() {
  const prefix = selectedTemplate.value.name
  files.value = [
    { id: 'template-report', name: `${prefix}_风味检测报告.pdf`, size: '2.4 MB', type: '检测报告', stage: '模板资料' },
    { id: 'template-brand', name: `${prefix}_品牌故事与包装资料.docx`, size: '860 KB', type: '品牌资料', stage: '模板资料' },
    { id: 'template-origin', name: `${prefix}_产地与工艺节点.xlsx`, size: '512 KB', type: '产地信息', stage: '模板资料' },
  ]
}

function fillTemplateText() {
  documentText.value = `${selectedTemplate.value.name}产自${selectedTemplate.value.origin}。产品资料包含产地环境、核心原料、传统工艺、检测指标和品牌故事。产地具有稳定供应基础，工艺节点包括原料采收、分级筛选、关键加工、品质检测和冷链仓储。品牌希望突出地方风味、真实产地、工艺传承和现代消费场景，并生成营销海报、实证白皮书和智慧大屏。`
  analysisError.value = ''
}

function openOutput(path) {
  router.push({
    path,
    query: {
      case: selectedTemplate.value.id,
      package: packageId.value,
    },
  })
}

function hasType(type) {
  if (!files.value.length) return true
  return files.value.some((file) => file.type === type)
}

function inferType(name) {
  if (/检测|报告|report/i.test(name)) return '检测报告'
  if (/品牌|包装|brand/i.test(name)) return '品牌资料'
  if (/产地|基地|工艺|origin|craft/i.test(name)) return '产地信息'
  if (/\.(png|jpg|jpeg)$/i.test(name)) return '产品图片'
  return '待识别材料'
}

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function firstText(value) {
  const item = toTextList(value)[0]
  return item || ''
}

function toTextList(value) {
  if (!Array.isArray(value)) return []
  return value.map((item) => {
    if (typeof item === 'string') return item
    if (item && typeof item === 'object') {
      return item.title || item.name || item.label || item.desc || item.description || JSON.stringify(item)
    }
    return String(item)
  }).filter(Boolean)
}

onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.import-page {
  min-height: 100vh;
  padding: calc(var(--navbar-h) + 42px) clamp(42px, 6vw, 96px) 56px;
  background: #f6f0e7;
  color: #2f2a22;
  font-family: var(--font-sans);
}

.hero-strip {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 32px;
  margin-bottom: 28px;
  border-bottom: 1px solid rgba(101, 86, 62, 0.18);
  padding-bottom: 24px;
}

.eyebrow {
  display: block;
  margin-bottom: 10px;
  color: #9f4a2d;
  font-family: Georgia, serif;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: clamp(38px, 4vw, 62px);
  letter-spacing: 0;
}

.hero-strip p {
  max-width: 760px;
  margin: 16px 0 0;
  color: #6b6254;
  font-size: 17px;
  line-height: 1.8;
}

.status-badge {
  flex-shrink: 0;
  border: 1px solid rgba(159, 74, 45, 0.28);
  background: #fff8eb;
  color: #9f4a2d;
  border-radius: 999px;
  padding: 11px 18px;
  font-weight: 700;
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(560px, 1.2fr) minmax(430px, 0.8fr);
  gap: 24px;
}

.upload-panel,
.process-panel {
  border: 1px solid rgba(101, 86, 62, 0.14);
  background: rgba(255, 252, 247, 0.72);
  box-shadow: 0 18px 42px rgba(70, 54, 32, 0.08);
}

.upload-panel,
.process-panel {
  padding: 22px;
}

.template-block {
  margin-bottom: 18px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  color: #4b5637;
  font-weight: 800;
}

.section-title small {
  color: #9f4a2d;
  font-weight: 700;
}

.section-title button {
  border: none;
  background: transparent;
  color: #9f4a2d;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.template-card {
  min-height: 82px;
  padding: 13px;
  border: 1px solid rgba(101, 86, 62, 0.15);
  border-radius: 6px;
  background: rgba(244, 239, 230, 0.62);
  color: #2f2a22;
  text-align: left;
}

.template-card.active {
  border-color: rgba(159, 74, 45, 0.5);
  background: #fff6e6;
  box-shadow: inset 0 0 0 1px rgba(159, 74, 45, 0.2);
}

.template-card strong,
.template-card span {
  display: block;
}

.template-card span {
  margin-top: 8px;
  color: #7b7162;
  font-size: 12px;
}

.dropzone {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 310px;
  text-align: center;
  border: 1.5px dashed rgba(79, 86, 55, 0.38);
  background:
    linear-gradient(135deg, rgba(255, 250, 240, 0.9), rgba(238, 230, 211, 0.55)),
    repeating-linear-gradient(45deg, rgba(159, 74, 45, 0.04) 0 1px, transparent 1px 12px);
  transition: border-color 180ms ease, background 180ms ease;
}

.dropzone.dragging {
  border-color: #9f4a2d;
  background: #fff6e6;
}

.dropzone input {
  display: none;
}

.upload-icon {
  width: 62px;
  height: 62px;
  display: grid;
  place-items: center;
  margin-bottom: 14px;
  border-radius: 50%;
  background: #4b5637;
  color: #fff8e9;
  font-size: 34px;
  line-height: 1;
}

.dropzone h2 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 30px;
}

.dropzone p {
  max-width: 560px;
  margin: 12px auto 22px;
  color: #756b5b;
  line-height: 1.7;
}

button {
  cursor: pointer;
  font-family: inherit;
}

.dropzone button,
.generate-btn,
.result-actions button {
  height: 44px;
  border: none;
  border-radius: 6px;
  background: #9f4a2d;
  color: #fff8e9;
  padding: 0 22px;
  font-weight: 700;
}

.file-list {
  margin-top: 20px;
}

.ai-panel {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid rgba(101, 86, 62, 0.12);
}

.ai-panel textarea {
  display: block;
  width: 100%;
  min-height: 190px;
  resize: vertical;
  border: 1px solid rgba(101, 86, 62, 0.18);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.82);
  color: #2f2a22;
  padding: 14px;
  font: inherit;
  line-height: 1.7;
  outline: none;
}

.ai-panel textarea:focus {
  border-color: rgba(159, 74, 45, 0.45);
  box-shadow: 0 0 0 3px rgba(159, 74, 45, 0.08);
}

.ai-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-top: 12px;
}

.ai-actions small {
  color: #7d7466;
  line-height: 1.6;
}

.ai-actions button {
  flex-shrink: 0;
  height: 42px;
  border: none;
  border-radius: 6px;
  background: #4b5637;
  color: #fff8e9;
  padding: 0 18px;
  font-weight: 800;
}

.ai-actions button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.error-text {
  margin: 10px 0 0;
  color: #9f4a2d;
  line-height: 1.6;
}

.empty-state,
.file-row {
  border-top: 1px solid rgba(101, 86, 62, 0.12);
  padding: 14px 2px;
}

.empty-state {
  color: #897f70;
}

.file-row {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.file-row strong,
.file-row small {
  display: block;
}

.file-row small {
  margin-top: 5px;
  color: #7d7466;
}

.file-row span {
  color: #9f4a2d;
  white-space: nowrap;
}

.notice {
  padding: 14px 16px;
  border-left: 4px solid #9f4a2d;
  background: #fff6e7;
  color: #675846;
  line-height: 1.7;
}

.score-card {
  margin-top: 18px;
  padding: 18px;
  background: #fffaf2;
  border: 1px solid rgba(101, 86, 62, 0.14);
}

.score-card > div:first-child,
.progress-head,
.package-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.score-label,
.package-head span {
  color: #7b7162;
  font-size: 12px;
}

.score-card strong {
  font-family: Georgia, serif;
  font-size: 28px;
  color: #4b5637;
}

.score-track,
.progress-track {
  height: 8px;
  overflow: hidden;
  margin-top: 10px;
  background: #e6dccb;
  border-radius: 999px;
}

.score-fill,
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #9f4a2d, #d6a24a);
  transition: width 160ms linear;
}

.score-card p {
  margin: 12px 0 0;
  color: #746b5d;
  line-height: 1.6;
}

.ai-summary {
  margin-top: 18px;
  padding: 18px;
  background: #fffaf2;
  border: 1px solid rgba(101, 86, 62, 0.14);
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.score-grid div {
  padding: 12px;
  background: rgba(244, 239, 230, 0.72);
  border: 1px solid rgba(101, 86, 62, 0.1);
}

.score-grid span,
.insight-list strong {
  display: block;
  color: #7b7162;
  font-size: 12px;
}

.score-grid strong {
  display: block;
  margin-top: 6px;
  color: #4b5637;
  font-family: Georgia, serif;
  font-size: 22px;
}

.insight-list {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(101, 86, 62, 0.12);
}

.insight-list p {
  margin: 8px 0 0;
  color: #746b5d;
  line-height: 1.6;
}

.requirements {
  display: grid;
  gap: 12px;
  margin: 18px 0;
}

.requirement-card {
  display: flex;
  gap: 14px;
  padding: 16px;
  background: rgba(244, 239, 230, 0.7);
  border: 1px solid rgba(101, 86, 62, 0.1);
}

.requirement-card.ready {
  border-color: rgba(75, 86, 55, 0.25);
  background: rgba(234, 241, 222, 0.68);
}

.requirement-card span {
  color: #9f4a2d;
  font-family: Georgia, serif;
  font-weight: 800;
}

.requirement-card strong {
  display: block;
  margin-bottom: 6px;
}

.requirement-card p {
  margin: 0;
  color: #786f61;
  line-height: 1.6;
}

.generate-btn {
  width: 100%;
  height: 50px;
  background: #4b5637;
}

.generate-btn:disabled {
  opacity: 0.72;
  cursor: wait;
}

.progress-box,
.result-box {
  margin-top: 18px;
  padding: 18px;
  background: #fffaf2;
  border: 1px solid rgba(101, 86, 62, 0.14);
}

ol {
  display: grid;
  gap: 8px;
  margin: 16px 0 0;
  padding-left: 20px;
  color: #8a8071;
}

li.active {
  color: #9f4a2d;
  font-weight: 800;
}

li.done {
  color: #4b5637;
}

.package-head strong {
  display: block;
  margin-top: 5px;
  color: #4b5637;
}

.package-head small {
  color: #9f4a2d;
  font-weight: 800;
}

.result-box p {
  margin: 14px 0;
  color: #746b5d;
  line-height: 1.7;
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.asset-card {
  min-height: 86px;
  padding: 14px;
  background: rgba(244, 239, 230, 0.65);
  border: 1px solid rgba(101, 86, 62, 0.1);
}

.asset-card strong,
.asset-card span {
  display: block;
}

.asset-card span {
  margin-top: 8px;
  color: #766d5f;
  font-size: 13px;
  line-height: 1.55;
}

.result-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.result-actions button {
  background: #9f4a2d;
}

@media (max-width: 1180px) {
  .workspace-grid,
  .template-grid,
  .score-grid {
    grid-template-columns: 1fr;
  }

  .ai-actions {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
