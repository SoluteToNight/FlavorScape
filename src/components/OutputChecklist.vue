<template>
  <aside v-if="activeProject" class="overflow-y-auto border-l border-glass-border p-4">
    <div class="mb-5">
      <span class="text-2xs uppercase tracking-[0.12em] text-text-muted">资产导出</span>
      <h2 class="font-serif text-lg text-earth mt-0.5">产出物清单</h2>
    </div>

    <ul class="space-y-2.5">
      <li
        v-for="item in items"
        :key="item.key"
        class="glass-panel p-3 flex items-center justify-between"
      >
        <div class="flex items-center gap-2.5 min-w-0">
          <span
            class="w-1.5 h-1.5 rounded-full flex-shrink-0"
            :class="statusDotClass(item.key)"
          />
          <div class="min-w-0">
            <h3 class="font-sans text-xs text-text-mid font-bold mb-0.5">{{ item.label }}</h3>
            <p class="text-2xs text-text-muted leading-[1.5] truncate">{{ item.hint }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0 ml-3">
          <span
            class="text-2xs font-bold px-2 py-0.5 rounded-sm"
            :class="statusBadgeClass(item.key)"
          >
            {{ statusLabel(item.key) }}
          </span>
          <button
            v-if="outputStatus[item.key] !== 'skipped'"
            class="text-2xs text-text-muted underline cursor-pointer hover:text-earth transition-colors whitespace-nowrap"
            @click="store.setOutputStatus(item.key, 'skipped')"
          >
            跳过
          </button>
        </div>
      </li>
    </ul>

    <div class="mt-4">
      <button
        class="w-full glass-panel px-4 py-2.5 text-sm text-earth font-bold cursor-pointer hover:shadow-app-sm transition-shadow"
      >
        一键导出全部
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useStudioStore } from '../stores/studio'

const store = useStudioStore()
const activeProject = computed(() => store.activeProject)
const outputStatus = computed(() => activeProject.value?.outputStatus || {})

const items = [
  { key: 'poster', label: '营销海报', hint: '品牌视觉海报 PNG 导出' },
  { key: 'archive', label: '科学白皮书', hint: '溯源数据与实验室实证看板' },
  { key: 'display', label: '智慧大屏', hint: '原产地遥感与风土数据看板' },
  { key: 'spread', label: '传播图谱', hint: '食材历史传播路径可视化' },
]

function statusLabel(key) {
  const s = outputStatus.value[key]
  if (s === 'edited') return '已编辑'
  if (s === 'skipped') return '已跳过'
  return '待编辑'
}

function statusDotClass(key) {
  const s = outputStatus.value[key]
  if (s === 'edited') return 'bg-leaf'
  if (s === 'skipped') return 'bg-text-muted'
  return 'bg-amber'
}

function statusBadgeClass(key) {
  const s = outputStatus.value[key]
  if (s === 'edited') return 'bg-leaf/15 text-leaf'
  if (s === 'skipped') return 'bg-text-muted/15 text-text-muted'
  return 'bg-amber/15 text-amber'
}
</script>
