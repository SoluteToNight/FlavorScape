<template>
  <div class="about-page">
    <div class="about-glass glass-panel">
      <h2 class="about-title">关于 · 方法论</h2>
      <p class="about-lead">数据来源 &amp; 量化逻辑</p>

      <div class="source-list">
        <a
          v-for="(ds, i) in sources"
          :key="ds.name"
          class="source-item"
          :href="ds.url"
          target="_blank"
          rel="noopener"
        >
          <div class="ds-indicator">
            <div class="ds-dot" :style="{ background: ds.color }" />
            <div v-if="i < sources.length - 1" class="ds-line" />
          </div>
          <div class="ds-content">
            <div class="ds-name">{{ ds.name }}</div>
            <div class="ds-desc">{{ ds.desc }}</div>
          </div>
          <svg class="ds-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M7 17L17 7M17 7H7M17 7v10"/>
          </svg>
        </a>
      </div>

      <div class="accordion">
        <button class="acc-toggle" @click="open = !open">
          <div class="acc-icon" :class="{ open }">+</div>
          LLM 辅助清洗说明
        </button>
        <Transition name="acc">
          <div v-show="open" class="acc-body">
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
.about-page {
  position: fixed;
  top: var(--navbar-h); left: 0; right: 0; bottom: 0;
  background: var(--bg);
  display: flex; align-items: flex-start; justify-content: center;
  padding: 32px var(--page-gutter) 48px;
  overflow-y: auto;
}
.about-glass {
  max-width: 760px; width: min(100%, 760px);
  border-radius: var(--radius);
  padding: clamp(28px, 3vw, 48px) clamp(24px, 3vw, 52px);
}
.about-title { font-family: var(--font-serif); font-size: 20px; font-weight: 500; letter-spacing: 0.1em; margin-bottom: 4px; }
.about-lead { font-size: 11px; color: var(--text-muted); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 32px; }

.source-list { display: flex; flex-direction: column; }
.source-item {
  display: flex; gap: 18px; align-items: flex-start;
  padding: 16px 0; border-bottom: 1px solid var(--glass-border);
  text-decoration: none; color: inherit;
  transition: background var(--transition);
}
.source-item:last-child { border-bottom: none; }
.source-item:hover .ds-name { color: var(--amber); }
.ds-indicator { display: flex; flex-direction: column; align-items: center; padding-top: 4px; width: 12px; flex-shrink: 0; }
.ds-dot { width: 8px; height: 8px; border-radius: 50%; }
.ds-line { width: 1px; flex: 1; min-height: 16px; background: var(--glass-border); margin-top: 6px; }
.ds-name { font-size: 13px; font-weight: 400; color: var(--text); margin-bottom: 3px; transition: color var(--transition); }
.ds-desc { font-size: 11px; color: var(--text-muted); line-height: 1.7; }
.ds-content { flex: 1; }
.ds-arrow { color: var(--text-muted); margin-top: 4px; opacity: 0; transition: opacity var(--transition); flex-shrink: 0; }
.source-item:hover .ds-arrow { opacity: 1; }

.accordion { margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--glass-border); }
.acc-toggle {
  display: flex; align-items: center; gap: 10px;
  cursor: pointer; font-size: 12px; color: var(--text-mid);
  letter-spacing: 0.06em; background: none; border: none;
  font-family: var(--font-sans); width: 100%; text-align: left;
}
.acc-icon {
  width: 18px; height: 18px; border-radius: 50%;
  border: 1px solid var(--glass-border);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; color: var(--text-muted);
  transition: transform var(--transition); flex-shrink: 0;
  line-height: 1;
}
.acc-icon.open { transform: rotate(45deg); }
.acc-body {
  margin-top: 14px; font-size: 12px; color: var(--text-muted);
  line-height: 1.9; letter-spacing: 0.04em; overflow: hidden;
}
.acc-enter-active, .acc-leave-active { transition: opacity 300ms ease; }
.acc-enter-from, .acc-leave-to { opacity: 0; }
</style>
