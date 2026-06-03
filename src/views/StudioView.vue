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
        <StudioPoster
          v-else-if="studioStore.mergedMarketingData"
          :spatial-data="studioStore.mergedMarketingData.spatial"
          :creative-data="studioStore.mergedMarketingData.creative"
          :hero-image="studioStore.mergedMarketingData.heroImage"
          :product-name="studioStore.mergedMarketingData.name"
          :province="activeProductCase?.province"
          :scale="0.5"
        />
        <div v-else class="glass-panel px-14 py-12 text-center max-w-[420px]">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-earth/10 flex items-center justify-center">
            <span class="font-serif text-xl text-earth">预览</span>
          </div>
          <h3 class="font-serif text-lg text-earth mb-2">预览区</h3>
          <p class="text-sm text-text-muted leading-[1.6]">
            产品已导入，但数据尚未加载
          </p>
        </div>

        <!-- 隐藏的导出用海报 (scale=1, 不能display:none) -->
        <div style="position: absolute; left: -9999px; top: 0;">
          <StudioPoster
            v-if="studioStore.mergedMarketingData"
            ref="exportPosterRef"
            :spatial-data="studioStore.mergedMarketingData.spatial"
            :creative-data="studioStore.mergedMarketingData.creative"
            :hero-image="studioStore.mergedMarketingData.heroImage"
            :product-name="studioStore.mergedMarketingData.name"
            :province="activeProductCase?.province"
          />
        </div>
      </section>

      <!-- 右侧：产出物清单 -->
      <OutputChecklist @export-poster="exportPoster" />
    </div>

    <!-- ═══════════════ 底部空间底板 ═══════════════ -->
    <SpatialFooter />
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import html2canvas from 'html2canvas'
import EmptyGuide from '../components/EmptyGuide.vue'
import ImportFlow from '../components/ImportFlow.vue'
import CreativeEditor from '../components/CreativeEditor.vue'
import OutputChecklist from '../components/OutputChecklist.vue'
import SpatialFooter from '../components/SpatialFooter.vue'
import StudioPoster from '../components/StudioPoster.vue'
import { useStudioStore } from '../stores/studio'
import { useProductCases } from '../composables/useProductCases'

const studioStore = useStudioStore()
const { getById } = useProductCases()

const hasProject = computed(() => studioStore.hasAnyProject())
const isImporting = ref(false)
const importingProduct = ref(null)
const isExporting = ref(false)
const exportPosterRef = ref(null)

const activeProductCase = computed(() => {
  const proj = studioStore.activeProject
  if (!proj) return null
  return getById(proj.productId)
})

function onProductSelect(productId) {
  importingProduct.value = getById(productId)
  isImporting.value = true
}

function onImportComplete() {
  studioStore.createProject(importingProduct.value.id, importingProduct.value.name)
  isImporting.value = false
  importingProduct.value = null
}

async function exportPoster() {
  if (!exportPosterRef.value || isExporting.value) return
  isExporting.value = true
  try {
    const el = exportPosterRef.value.$el || exportPosterRef.value
    const canvas = await html2canvas(el, {
      scale: 2,
      useCORS: true,
      backgroundColor: null,
      logging: false,
    })
    const link = document.createElement('a')
    const name = studioStore.mergedMarketingData?.name || '海报'
    const theme = studioStore.mergedMarketingData?.creative?.theme || 'nature'
    link.download = `${name}-海报-${theme}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (e) {
    alert('导出失败: ' + e.message)
  } finally {
    isExporting.value = false
  }
}
</script>
