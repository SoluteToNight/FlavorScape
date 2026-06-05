<template>
  <section class="project-manager border-b border-glass-border p-4">
    <div class="flex items-center justify-between mb-3">
      <div>
        <span class="text-2xs uppercase tracking-[0.12em] text-text-muted">Projects</span>
        <h2 class="font-serif text-lg text-earth mt-0.5">创作项目</h2>
      </div>
      <button
        type="button"
        class="h-8 px-3 rounded-sm border border-earth/25 text-xs text-earth font-bold bg-earth/5 cursor-pointer hover:bg-earth/10 transition-colors"
        @click="$emit('new-project')"
      >
        新建
      </button>
    </div>

    <div v-if="store.projectList.length === 0" class="py-6 text-center border border-dashed border-glass-border rounded-sm">
      <p class="text-xs text-text-mid">暂无项目</p>
      <p class="text-2xs text-text-muted mt-1">先选择输出形式创建项目</p>
    </div>

    <ul v-else class="space-y-1.5">
      <li
        v-for="project in store.projectList"
        :key="project.id"
        class="project-row rounded-sm border transition-colors"
        :class="project.isActive ? 'border-earth/30 bg-earth/10' : 'border-transparent hover:border-glass-border hover:bg-bg-warm'"
      >
        <div
          role="button"
          tabindex="0"
          class="w-full text-left px-2.5 py-2 cursor-pointer"
          @click="store.switchProject(project.id)"
          @keydown.enter.prevent="store.switchProject(project.id)"
        >
          <div class="flex items-start gap-2">
            <span class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" :class="stageClass(project.stage)" />
            <div class="min-w-0 flex-1">
              <template v-if="editingId === project.id">
                <input
                  v-model="draftName"
                  class="w-full h-7 px-2 border border-earth/30 bg-glass text-xs text-text outline-none rounded-sm"
                  maxlength="40"
                  @click.stop
                  @keydown.enter.stop.prevent="commitRename(project.id)"
                  @keydown.escape.stop.prevent="cancelRename"
                  @blur="commitRename(project.id)"
                />
              </template>
              <template v-else>
                <div class="text-xs text-text font-bold truncate">{{ project.name }}</div>
                <div class="text-2xs text-text-muted mt-0.5 flex items-center gap-1.5">
                  <span>{{ project.productName }}</span>
                  <span>·</span>
                  <span>{{ outputLabel(project.outputType) }}</span>
                  <span>·</span>
                  <span>{{ stageLabel(project.stage) }}</span>
                  <span v-if="project.sourceType" class="source-badge">AI资产包</span>
                </div>
              </template>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between px-2.5 pb-2">
          <span class="text-2xs text-text-muted">{{ formatDate(project.updatedAt) }}</span>
          <div class="flex items-center gap-1.5">
            <button
              type="button"
              class="text-2xs text-text-muted cursor-pointer hover:text-earth transition-colors"
              @click.stop="startRename(project)"
            >
              重命名
            </button>
            <button
              type="button"
              class="text-2xs text-text-muted cursor-pointer hover:text-earth transition-colors"
              @click.stop="store.duplicateProject(project.id)"
            >
              复制
            </button>
            <button
              type="button"
              class="text-2xs text-text-muted cursor-pointer hover:text-carmine transition-colors"
              @click.stop="deleteProject(project.id)"
            >
              删除
            </button>
          </div>
        </div>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useStudioStore } from '../stores/studio'

defineEmits(['new-project'])

const store = useStudioStore()
const editingId = ref(null)
const draftName = ref('')

function stageLabel(stage) {
  const labels = { draft: '草稿', editing: '编辑中', exported: '已导出' }
  return labels[stage] || '草稿'
}

function stageClass(stage) {
  const classes = { draft: 'bg-text-muted', editing: 'bg-amber', exported: 'bg-leaf' }
  return classes[stage] || 'bg-text-muted'
}

function outputLabel(type) {
  const labels = { poster: '海报', archive: '白皮书', display: '演示' }
  return labels[type] || '项目'
}

function formatDate(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

function startRename(project) {
  editingId.value = project.id
  draftName.value = project.name
}

function commitRename(id) {
  if (!editingId.value) return
  store.renameProject(id, draftName.value)
  editingId.value = null
  draftName.value = ''
}

function cancelRename() {
  editingId.value = null
  draftName.value = ''
}

function deleteProject(id) {
  if (window.confirm('确认删除此创作项目？本地保存的编辑内容也会删除。')) {
    store.deleteProject(id)
  }
}
</script>

<style scoped>
.source-badge {
  flex-shrink: 0;
  border-radius: 3px;
  background: rgba(94, 123, 80, 0.12);
  color: var(--leaf);
  font-size: 10px;
  font-weight: 800;
  padding: 1px 4px;
}
</style>
