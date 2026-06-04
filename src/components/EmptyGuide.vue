<template>
  <section class="empty-guide w-full max-w-[1040px] px-8 py-7">
    <div class="flex items-end justify-between gap-8 mb-6">
      <div>
        <span class="text-2xs uppercase tracking-[0.14em] text-text-muted">Start From Product Case</span>
        <h1 class="font-serif text-3xl text-earth mt-1">选择产品，生成内容资产</h1>
        <p class="text-sm text-text-mid mt-2 max-w-[560px]">
          以产品 JSON 中的空间事实和默认文案作为起点，进入工作台后可编辑标题、叙事、主题、证据和传播路径。
        </p>
      </div>
      <button
        v-if="mode === 'first'"
        class="h-9 px-4 rounded-sm border border-glass-border text-xs text-text-mid bg-glass cursor-pointer hover:border-earth hover:text-earth transition-colors"
        type="button"
        @click="onImportClick"
      >
        导入已有资料
      </button>
    </div>

    <div class="grid grid-cols-5 gap-3">
      <button
        v-for="pc in productCases"
        :key="pc.id"
        type="button"
        class="product-card text-left bg-glass border border-glass-border rounded-sm overflow-hidden cursor-pointer transition-[border-color,box-shadow,transform] duration-200 hover:border-earth hover:shadow-app-md focus:outline-none focus:border-earth"
        @click="$emit('select', pc.id)"
      >
        <div class="h-[118px] bg-bg-warm overflow-hidden">
          <img
            :src="pc.heroImage"
            :alt="pc.name"
            class="w-full h-full object-cover block"
          />
        </div>
        <div class="p-3">
          <div class="flex items-center justify-between gap-2">
            <h2 class="font-serif text-base text-text truncate">{{ pc.studio?.brandName || pc.name }}</h2>
            <span
              class="w-2.5 h-2.5 rounded-full flex-shrink-0"
              :style="{ backgroundColor: pc.colors?.primary || '#8B5E34' }"
            />
          </div>
          <p class="text-2xs text-text-muted mt-1">{{ pc.category }}</p>
          <p class="text-xs text-text-mid mt-2 leading-[1.5] line-clamp-2">{{ pc.origin }}</p>
        </div>
      </button>
    </div>
  </section>
</template>

<script setup>
import { useProductCases } from '../composables/useProductCases'

defineEmits(['select'])
defineProps({
  mode: { type: String, default: 'first' },
})

const { cases: productCases, loadAll } = useProductCases()
loadAll()

function onImportClick() {
  window.alert('此功能即将上线，当前先从产品案例创建内容项目。')
}
</script>

<style scoped>
.empty-guide {
  background: rgba(255, 252, 247, 0.72);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-md);
  backdrop-filter: var(--blur-sm);
  -webkit-backdrop-filter: var(--blur-sm);
}

.product-card:hover {
  transform: translateY(-2px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
