<template>
  <div class="fixed top-navbar inset-x-0 bottom-0 bg-bg flex items-center justify-center overflow-y-auto">
    <div class="about-glass glass-panel max-w-[640px] w-[90%] rounded-lg px-[52px] py-12">
      <h2 class="font-serif text-2xl font-medium tracking-[0.1em] mb-1">关于 · 方法论</h2>
      <p class="text-xs text-text-muted tracking-[0.15em] uppercase mb-8">数据来源 &amp; 量化逻辑</p>

      <div class="flex flex-col">
        <a
          v-for="(ds, i) in sources"
          :key="ds.name"
          class="source-item flex gap-[18px] items-start py-4 border-b border-glass-border no-underline text-inherit transition-colors last:border-b-0"
          :href="ds.url"
          target="_blank"
          rel="noopener"
        >
          <div class="flex flex-col items-center pt-1 w-3 shrink-0">
            <div class="ds-dot w-2 h-2 rounded-full" :style="{ background: ds.color }" />
            <div v-if="i < sources.length - 1" class="w-px flex-1 min-h-4 bg-glass-border mt-1.5" />
          </div>
          <div class="flex-1">
            <div class="ds-name text-sm font-normal text-text mb-[3px]">{{ ds.name }}</div>
            <div class="text-xs text-text-muted leading-[1.7]">{{ ds.desc }}</div>
          </div>
          <svg class="ds-arrow text-text-muted mt-1 opacity-0 shrink-0" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M7 17L17 7M17 7H7M17 7v10"/>
          </svg>
        </a>
      </div>

      <div class="mt-6 pt-5 border-t border-glass-border">
        <button class="acc-toggle flex items-center gap-2.5 cursor-pointer text-xs text-text-mid tracking-[0.06em] bg-transparent border-none font-sans w-full text-left" @click="open = !open">
          <div class="acc-icon w-[18px] h-[18px] rounded-full border border-glass-border flex items-center justify-center text-xs text-text-muted shrink-0 leading-none" :class="{ open }">+</div>
          LLM 辅助清洗说明
        </button>
        <Transition name="acc">
          <div v-show="open" class="mt-3.5 text-xs text-text-muted leading-[1.9] tracking-[0.04em] overflow-hidden">
            通过 LLM 对古籍文献进行结构化处理：将《饮食志》《茶经》《本草纲目》等历史文献中的风味描述词映射为数值向量（0–1 区间）；再结合 WWF 生态区物理参数（年均温、降水量、海拔）进行多元回归，生成「生态-风味」关联矩阵。最终每个地域节点携带 6 维风味向量与 1 组气候时序曲线，全部以 GeoJSON 属性储存，可通过探索地图直接检索。
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const sources = ref([])
const open = ref(false)
onMounted(async () => {
  const res = await fetch('/api/data-sources')
  sources.value = await res.json()
})
</script>

<style scoped>
/* KEPT: hover cascades, Vue transitions */
.source-item:hover .ds-name { color: var(--amber); }
.source-item:hover .ds-arrow { opacity: 1; }
.ds-name { transition: color var(--transition); }
.ds-arrow { transition: opacity var(--transition); }

.acc-icon.open { transform: rotate(45deg); }
.acc-icon { transition: transform var(--transition); }

.acc-enter-active, .acc-leave-active { transition: opacity 300ms ease; }
.acc-enter-from, .acc-leave-to { opacity: 0; }
</style>
