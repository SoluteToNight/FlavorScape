<template>
  <main class="fixed top-navbar inset-x-0 bottom-0 flex flex-col bg-bg">
    <!-- ═══════════════ 三栏主区域 ═══════════════ -->
    <div class="flex-1 grid grid-cols-[280px_1fr_260px] overflow-hidden">
      <!-- 左侧：编辑面板 -->
      <aside class="overflow-y-auto border-r border-glass-border p-4">
        <div class="mb-5">
          <span class="text-2xs uppercase tracking-[0.12em] text-text-muted">创意编辑</span>
          <h2 class="font-serif text-lg text-earth mt-0.5">编辑面板</h2>
        </div>

        <div class="glass-panel p-4 mb-3">
          <h3 class="font-sans text-xs text-text-mid font-bold mb-1.5">产品文案</h3>
          <p class="text-2xs text-text-muted leading-[1.5]">标题、描述与诗意短句编辑控件</p>
        </div>

        <div class="glass-panel p-4 mb-3">
          <h3 class="font-sans text-xs text-text-mid font-bold mb-1.5">视觉风格</h3>
          <p class="text-2xs text-text-muted leading-[1.5]">主题选择器与色彩偏好控制</p>
        </div>

        <div class="glass-panel p-4">
          <h3 class="font-sans text-xs text-text-mid font-bold mb-1.5">品牌叙事</h3>
          <p class="text-2xs text-text-muted leading-[1.5]">叙事文案与产品故事编辑区</p>
        </div>
      </aside>

      <!-- 中间：预览区 -->
      <section class="overflow-y-auto p-4 flex items-center justify-center">
        <div class="glass-panel px-14 py-12 text-center max-w-[420px]">
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
      <aside class="overflow-y-auto border-l border-glass-border p-4">
        <div class="mb-5">
          <span class="text-2xs uppercase tracking-[0.12em] text-text-muted">资产导出</span>
          <h2 class="font-serif text-lg text-earth mt-0.5">产出物清单</h2>
        </div>

        <div class="glass-panel p-4 mb-3">
          <h3 class="font-sans text-xs text-text-mid font-bold mb-1.5">营销海报</h3>
          <p class="text-2xs text-text-muted leading-[1.5]">品牌视觉海报 PNG 导出</p>
        </div>

        <div class="glass-panel p-4 mb-3">
          <h3 class="font-sans text-xs text-text-mid font-bold mb-1.5">科学白皮书</h3>
          <p class="text-2xs text-text-muted leading-[1.5]">溯源数据与实验室实证看板</p>
        </div>

        <div class="glass-panel p-4 mb-3">
          <h3 class="font-sans text-xs text-text-mid font-bold mb-1.5">传播图谱</h3>
          <p class="text-2xs text-text-muted leading-[1.5]">食材历史传播路径可视化</p>
        </div>

        <div class="glass-panel p-4">
          <h3 class="font-sans text-xs text-text-mid font-bold mb-1.5">地理志大屏</h3>
          <p class="text-2xs text-text-muted leading-[1.5]">原产地遥感与风土数据看板</p>
        </div>
      </aside>
    </div>

    <!-- ═══════════════ 底部空间底板 ═══════════════ -->
    <footer class="h-[48px] flex-shrink-0 border-t border-glass-border bg-glass flex items-center px-4 gap-4">
      <span class="text-2xs text-text-muted font-sans uppercase tracking-[0.1em] whitespace-nowrap">空间底板</span>
      <span class="w-px h-4 bg-glass-border flex-shrink-0" />
      <span class="text-2xs text-text-mid font-sans truncate">
        产地数据、品种信息、品牌场景等只读 GIS 元数据将在此显示
      </span>
    </footer>
  </main>
</template>

<script setup>
// Layout skeleton — sub-components (EmptyGuide, CreativeEditor, StudioPoster,
// OutputChecklist, SpatialFooter) will be wired in later tasks.
</script>
