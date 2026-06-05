<template>
  <section class="ai-assistant">
    <div class="assistant-head">
      <div>
        <span>DeepSeek Assistant</span>
        <strong>{{ outputLabel }}编辑助手</strong>
      </div>
      <button type="button" :disabled="loading" @click="askWithPrompt(primaryPrompt)">
        智能优化
      </button>
    </div>

    <div class="quick-row">
      <button v-for="item in quickPrompts" :key="item" type="button" :disabled="loading" @click="askWithPrompt(item)">
        {{ item }}
      </button>
    </div>

    <div class="chat-log">
      <div v-for="message in messages" :key="message.id" class="chat-message" :class="message.role">
        <span>{{ message.role === 'assistant' ? 'AI' : '你' }}</span>
        <p>{{ message.content }}</p>
      </div>
      <div v-if="!messages.length" class="chat-empty">
        {{ emptyHint }}
      </div>
    </div>

    <div v-if="suggestions.length" class="suggestion-list">
      <div v-for="(item, index) in suggestions" :key="`${item.field}-${index}`" class="suggestion-card">
        <div>
          <strong>{{ fieldLabel(item.field) }}</strong>
          <p>{{ suggestionPreview(item) }}</p>
          <small>{{ item.reason }}</small>
        </div>
        <button type="button" @click="applySuggestion(item)">应用</button>
      </div>
    </div>

    <div v-if="styleOptions.length" class="style-options">
      <article v-for="item in styleOptions" :key="item.label || item.palette">
        <strong>{{ item.label || '风格方案' }}</strong>
        <span>{{ item.palette }}</span>
        <p>{{ item.layout || item.notes }}</p>
      </article>
    </div>

    <ul v-if="nextActions.length" class="next-actions">
      <li v-for="item in nextActions" :key="item">{{ item }}</li>
    </ul>

    <form class="chat-form" @submit.prevent="send">
      <textarea v-model="draft" :disabled="loading" :placeholder="placeholder" />
      <button type="submit" :disabled="loading || !draft.trim()">{{ loading ? '思考中' : '发送' }}</button>
    </form>
    <p v-if="error" class="assistant-error">{{ error }}</p>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStudioStore } from '../stores/studio'

const store = useStudioStore()
const draft = ref('')
const loading = ref(false)
const error = ref('')
const messages = ref([])
const suggestions = ref([])
const styleOptions = ref([])
const nextActions = ref([])

const activeOutput = computed(() => store.activeOutput)
const productContext = computed(() => store.activeProductCase || {})
const sourceAsset = computed(() => store.activeSourceAsset)
const outputContext = computed(() => ({
  poster: store.mergedPosterData,
  archive: store.mergedArchiveData,
  display: store.mergedDisplayData,
}[activeOutput.value] || {}))

const outputLabel = computed(() => ({
  poster: '海报',
  archive: '白皮书',
  display: '大屏',
}[activeOutput.value] || '产出'))

const quickPromptMap = {
  poster: [
    '强化产地高级感',
    '改成更年轻的社媒风格',
    '压缩叙事，增强标题',
    '给出三种色系和模板参数',
  ],
  archive: [
    '把摘要改成更适合招商材料',
    '指出白皮书还缺哪些证据',
    '优化结论，让它更谨慎可信',
    '只保留最有说服力的指标',
  ],
  display: [
    '优化大屏开场标题和字幕',
    '让大屏更适合展厅巡航',
    '强化传播路径叙事',
    '突出产地节点和证据卡片',
  ],
}

const quickPrompts = computed(() => quickPromptMap[activeOutput.value] || quickPromptMap.poster)
const primaryPrompt = computed(() => quickPrompts.value[0])
const emptyHint = computed(() => {
  if (activeOutput.value === 'archive') return '可以让 DeepSeek 帮你重写白皮书摘要、筛选证据指标、补充复核提示和优化结论。'
  if (activeOutput.value === 'display') return '可以让 DeepSeek 帮你设计大屏标题、巡航叙事、节点说明和传播路径展示策略。'
  return '可以让 DeepSeek 帮你改标题、换色系、调整模板参数、压缩叙事或增强海报高级感。'
})
const placeholder = computed(() => {
  if (activeOutput.value === 'archive') return '例如：帮我把这份白皮书改成更适合政府招商汇报'
  if (activeOutput.value === 'display') return '例如：帮我做一版更适合展厅自动巡航的大屏文案'
  return '例如：做一版更适合小红书封面的标题、色系和版式建议'
})

async function askWithPrompt(prompt) {
  draft.value = prompt
  await send()
}

async function send() {
  const content = draft.value.trim()
  if (!content || loading.value || !activeOutput.value) return
  const userMessage = { id: messageId(), role: 'user', content }
  messages.value.push(userMessage)
  draft.value = ''
  loading.value = true
  error.value = ''

  try {
    const res = await fetch('/api/assets/studio-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        output_type: activeOutput.value,
        messages: messages.value.map(({ role, content }) => ({ role, content })),
        output: outputContext.value,
        product: productContext.value,
        asset_package: sourceAsset.value?.assetPackage || {},
      }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
    messages.value.push({
      id: messageId(),
      role: 'assistant',
      content: data.reply || '已生成建议。',
    })
    suggestions.value = Array.isArray(data.suggestions) ? data.suggestions : []
    styleOptions.value = Array.isArray(data.style_options) ? data.style_options : []
    nextActions.value = Array.isArray(data.next_actions) ? data.next_actions : []
  } catch (err) {
    error.value = `AI 助手请求失败：${err.message}`
  } finally {
    loading.value = false
  }
}

function applySuggestion(item) {
  if (!item?.field || !activeOutput.value) return
  const field = item.field
  let value = item.value

  if (activeOutput.value === 'poster') {
    if (field === 'theme' && !['nature', 'heritage', 'indigo'].includes(value)) return
    if (field === 'imagePosY') value = Number(value)
    if (field === 'templateParams' && value && typeof value === 'object') {
      const current = store.activeProject?.outputs?.poster?.templateParams || {}
      value = { ...current, ...value }
    }
  }

  if (activeOutput.value === 'display') {
    if (field === 'interactionMode' && !['product', 'route'].includes(value)) return
    if (field === 'showTimeline') value = Boolean(value)
  }

  store.updateOutputField(activeOutput.value, field, value)
}

function suggestionPreview(item) {
  if (item.field === 'templateParams' && item.value && typeof item.value === 'object') {
    return Object.entries(item.value).map(([key, value]) => `${key}: ${value}`).join(' / ')
  }
  if (Array.isArray(item.value)) return item.value.join('、')
  return String(item.value ?? '')
}

function fieldLabel(field) {
  return {
    title: '标题',
    subtitle: '副标题',
    poeticLine: '短句',
    narrative: '叙事',
    theme: '主题',
    imagePosY: '图片焦点',
    templateParams: '模板参数',
    summary: '摘要',
    conclusion: '结论',
    visibleEvidence: '显示指标',
    caption: '展示说明',
    interactionMode: '交互模式',
    selectedRouteId: '传播路径',
    showTimeline: '时间线',
  }[field] || field
}

function messageId() {
  return typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`
}
</script>

<style scoped>
.ai-assistant {
  margin-bottom: 14px;
  border: 1px solid rgba(94, 123, 80, 0.22);
  border-radius: 7px;
  background: rgba(246, 250, 241, 0.78);
  padding: 12px;
}

.assistant-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.assistant-head span,
.assistant-head strong {
  display: block;
}

.assistant-head span {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
}

.assistant-head strong {
  margin-top: 3px;
  color: var(--leaf);
  font-size: 14px;
}

button {
  border: 0;
  border-radius: 4px;
  background: var(--leaf);
  color: #fffaf3;
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
  padding: 7px 10px;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.quick-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.quick-row button {
  background: rgba(94, 123, 80, 0.12);
  color: var(--leaf);
}

.chat-log {
  display: grid;
  gap: 8px;
  max-height: 210px;
  overflow-y: auto;
  margin-top: 10px;
  padding-right: 2px;
}

.chat-empty,
.chat-message {
  border: 1px solid rgba(74, 65, 55, 0.1);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.76);
  padding: 9px;
}

.chat-empty {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.55;
}

.chat-message span {
  color: var(--earth);
  font-size: 10px;
  font-weight: 850;
}

.chat-message.assistant span {
  color: var(--leaf);
}

.chat-message p {
  margin: 4px 0 0;
  color: var(--text-mid);
  font-size: 12px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.suggestion-list,
.style-options {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.suggestion-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  border: 1px solid rgba(94, 123, 80, 0.18);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.86);
  padding: 9px;
}

.suggestion-card strong,
.suggestion-card p,
.suggestion-card small {
  display: block;
}

.suggestion-card strong {
  color: var(--text);
  font-size: 12px;
}

.suggestion-card p {
  margin: 5px 0 0;
  color: var(--text-mid);
  font-size: 12px;
  line-height: 1.45;
}

.suggestion-card small {
  margin-top: 5px;
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.45;
}

.suggestion-card button {
  flex-shrink: 0;
}

.style-options article,
.next-actions li {
  border-left: 3px solid rgba(139, 94, 52, 0.4);
  background: rgba(255, 252, 247, 0.7);
  padding: 9px;
}

.style-options strong,
.style-options span,
.style-options p {
  display: block;
}

.style-options strong {
  color: var(--text);
  font-size: 12px;
}

.style-options span {
  margin-top: 4px;
  color: var(--earth);
  font-size: 11px;
  font-weight: 800;
}

.style-options p,
.next-actions li {
  margin: 5px 0 0;
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.45;
}

.next-actions {
  display: grid;
  gap: 7px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}

.chat-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  margin-top: 10px;
}

textarea {
  min-height: 52px;
  resize: vertical;
  border: 1px solid rgba(74, 65, 55, 0.14);
  border-radius: 5px;
  background: rgba(255, 252, 247, 0.9);
  color: var(--text);
  font: inherit;
  font-size: 12px;
  line-height: 1.5;
  outline: none;
  padding: 8px;
}

.assistant-error {
  margin: 8px 0 0;
  color: var(--carmine);
  font-size: 11px;
  line-height: 1.45;
}
</style>
