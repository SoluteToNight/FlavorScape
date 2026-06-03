<template>
  <footer
    v-if="activeProductCase"
    class="h-[48px] flex-shrink-0 border-t border-glass-border bg-glass flex items-center px-4 gap-3"
  >
    <span class="text-2xs text-text-muted font-sans uppercase tracking-[0.1em] whitespace-nowrap">空间底板</span>
    <span class="w-px h-4 bg-glass-border flex-shrink-0" />

    <span class="text-2xs text-text-mid font-sans truncate">
      {{ activeProductCase.province }} · {{ activeProductCase.origin }}
    </span>

    <span class="w-px h-4 bg-glass-border flex-shrink-0" />

    <span class="text-2xs text-text-muted uppercase tracking-[0.08em] flex-shrink-0">
      {{ activeProductCase.category }}
    </span>

    <span class="w-px h-4 bg-glass-border flex-shrink-0" />

    <span class="flex items-center gap-1.5 flex-shrink-0">
      <span
        class="w-2.5 h-2.5 rounded-full flex-shrink-0"
        :style="{ backgroundColor: activeProductCase.colors?.primary || '#8B5E34' }"
      />
      <span class="text-2xs text-text-muted font-mono uppercase">
        {{ activeProductCase.colors?.primary || '—' }}
      </span>
    </span>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useStudioStore } from '../stores/studio'
import { useProductCases } from '../composables/useProductCases'

const store = useStudioStore()
const { getById } = useProductCases()

const activeProductCase = computed(() => {
  const p = store.activeProject
  if (!p) return null
  return getById(p.productId)
})
</script>
