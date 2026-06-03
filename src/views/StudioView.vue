<template>
  <main class="fixed top-navbar inset-x-0 bottom-0 flex flex-col bg-bg">
    <!-- ═══════════════ 三栏主区域 ═══════════════ -->
    <div class="flex-1 grid grid-cols-[280px_1fr_260px] overflow-hidden">
      <!-- 左侧：编辑面板 -->
      <CreativeEditor />

      <!-- 中间：预览区 -->
      <section class="overflow-y-auto p-4 flex items-center justify-center">
        <EmptyGuide v-if="!hasProject" @select="onProductSelect" />
        <ImportFlow
          v-else-if="isImporting"
          :product-name="importingProduct?.name"
          :province="importingProduct?.province"
          :node-count="importingProduct?.marketing?.spatial?.nodes?.length || 0"
          @complete="onImportComplete"
        />
        <div v-else class="glass-panel px-14 py-12 text-center max-w-[420px]">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-earth/10 flex items-center justify-center">
            <span class="font-serif text-xl text-earth">预览</span>
          </div>
          <h3 class="font-serif text-lg text-earth mb-2">预览区</h3>
          <p class="text-sm text-text-muted leading-[1.6]">
            选择产品并完成导入后，<br />海报将在此区域实时渲染
          </p>
        </div>
      </section>

      <!-- 右侧：产出物清单 -->
      <OutputChecklist />
    </div>

    <!-- ═══════════════ 底部空间底板 ═══════════════ -->
    <SpatialFooter />
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import EmptyGuide from '../components/EmptyGuide.vue'
import ImportFlow from '../components/ImportFlow.vue'
import CreativeEditor from '../components/CreativeEditor.vue'
import OutputChecklist from '../components/OutputChecklist.vue'
import SpatialFooter from '../components/SpatialFooter.vue'
import { useStudioStore } from '../stores/studio'
import { useProductCases } from '../composables/useProductCases'

const studioStore = useStudioStore()
const { getById } = useProductCases()

const hasProject = computed(() => studioStore.hasAnyProject())
const isImporting = ref(false)
const importingProduct = ref(null)

function onProductSelect(productId) {
  importingProduct.value = getById(productId)
  isImporting.value = true
}

function onImportComplete() {
  studioStore.createProject(importingProduct.value.id, importingProduct.value.name)
  isImporting.value = false
  importingProduct.value = null
}
</script>
