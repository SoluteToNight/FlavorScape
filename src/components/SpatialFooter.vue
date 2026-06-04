<template>
  <footer
    v-if="product"
    class="spatial-footer h-[50px] flex-shrink-0 border-t border-glass-border bg-glass flex items-center px-4 gap-3"
  >
    <span class="text-2xs text-text-muted font-sans uppercase tracking-[0.1em] whitespace-nowrap">空间底板</span>
    <span class="divider" />

    <span class="text-2xs text-text-mid font-sans truncate">
      {{ product.province }} · {{ product.origin }}
    </span>

    <span class="divider" />

    <span class="text-2xs text-text-muted uppercase tracking-[0.08em] flex-shrink-0">
      {{ product.category }}
    </span>

    <span class="divider" />

    <span class="flex items-center gap-1.5 flex-shrink-0">
      <span
        class="w-2.5 h-2.5 rounded-full flex-shrink-0"
        :style="{ backgroundColor: product.colors?.primary || '#8B5E34' }"
      />
      <span class="text-2xs text-text-muted font-mono uppercase">
        {{ product.colors?.primary || '--' }}
      </span>
    </span>

    <span class="divider" />

    <span class="text-2xs text-text-muted truncate">
      {{ product.studio?.brandScenario || '地方食材品牌资产' }}
    </span>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useStudioStore } from '../stores/studio'

const store = useStudioStore()
const product = computed(() => store.activeProductCase)
</script>

<style scoped>
.spatial-footer {
  backdrop-filter: var(--blur-sm);
  -webkit-backdrop-filter: var(--blur-sm);
}

.divider {
  width: 1px;
  height: 16px;
  background: var(--glass-border);
  flex-shrink: 0;
}
</style>
