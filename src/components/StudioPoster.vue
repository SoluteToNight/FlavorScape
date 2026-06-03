<template>
  <article
    class="marketing-poster relative"
    :class="[themeLayout, themeFont]"
    :style="{ ...cssVars, transform: `scale(${scale})`, transformOrigin: 'top center' }"
  >
    <div class="canvas-hairline-frame" />
    <div class="poster-layout-container relative z-[5] flex flex-col min-h-full px-8 py-10 gap-8">
      <!-- ── 主图区域 ── -->
      <header class="poster-section-hero">
        <div class="hero-image-frame relative bg-[var(--t-paper)] overflow-hidden">
          <img
            :src="heroImage"
            :alt="productName"
            class="visual-core-img w-full h-full object-cover block"
          />
          <div v-if="theme === 'indigo'" class="image-overlay" />
        </div>

        <div class="hero-text-cluster">
          <div class="title-wrap">
            <span v-if="theme === 'nature'" class="badge-tag">只做真实搬运 · 不做科技加工</span>
            <span v-if="theme === 'heritage'" class="badge-tag seal">印</span>
            <h1 class="brand-title">{{ creativeData.desc }}</h1>
          </div>
          <p class="product-summary-desc text-[13px] opacity-80 m-0 leading-[1.5]">{{ creativeData.desc }}</p>
          <div class="poetic-bar text-[12px] italic opacity-70">{{ creativeData.poeticLine }}</div>
        </div>
      </header>

      <!-- ── 叙事与地图区域 ── -->
      <section class="poster-section-narrative">
        <div class="narrative-text">
          <span class="text-[10px] uppercase tracking-[0.1em] opacity-50 font-sans block mb-1">{{ themeKicker }}</span>
          <h3>{{ themeSubtitle }}</h3>
          <p v-html="creativeData.narrative" />
        </div>
        <div class="map-component-inner">
          <StaticGeoMap :target-province="province" :nodes="spatialData.nodes" />
        </div>
      </section>

      <!-- ── 核心指标 ── -->
      <section class="poster-section-metrics">
        <div v-for="item in spatialData.evidence" :key="item.label" class="metric-block">
          <span class="m-label">{{ item.label }}</span>
          <strong class="m-value">{{ item.value }}</strong>
        </div>
      </section>

      <footer class="flex justify-between items-end mt-auto pt-6">
        <div class="footer-line" />
        <div>
          <strong class="block text-[12px] text-[var(--t-primary)] mb-0.5">FlavorScape 风物研究所</strong>
          <span class="text-[8px] opacity-50 font-[Arial,Helvetica,sans-serif] tracking-[0.05em]">ORIGIN TRACKING & QUALITY VERIFICATION</span>
        </div>
        <div class="w-9 h-9 border border-[var(--t-primary)] opacity-30" />
      </footer>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import StaticGeoMap from './StaticGeoMap.vue'

const props = defineProps({
  spatialData: { type: Object, required: true },
  creativeData: { type: Object, required: true },
  heroImage: { type: String, default: '' },
  scale: { type: Number, default: 1 },
  productName: { type: String, default: '' },
  province: { type: String, default: '' },
})

const theme = computed(() => props.creativeData?.theme || 'nature')

const themeLayout = computed(() => {
  const map = { nature: 'layout-nature', heritage: 'layout-heritage', indigo: 'layout-indigo' }
  return map[theme.value] || 'layout-nature'
})

const themeFont = computed(() => {
  const map = { nature: 'font-modern', heritage: 'font-classical', indigo: 'font-serif-modern' }
  return map[theme.value] || 'font-modern'
})

const themeSubtitle = computed(() => {
  const map = { nature: '好食溯源', heritage: '山河空间志', indigo: '原产地拓印' }
  return map[theme.value] || '好食溯源'
})

const themeKicker = computed(() => {
  const map = { nature: 'NATURE EXPLORATION', heritage: 'ORIENTAL HERITAGE', indigo: 'CYANOTYPE PRINT' }
  return map[theme.value] || 'NATURE EXPLORATION'
})

const cssVars = computed(() => {
  const t = theme.value
  const isIndigo = t === 'indigo'
  const isNature = t === 'nature'

  const colors = {
    nature:   { primary: '#2a4128', accent: '#708a68', bg: '#ffffff', paper: '#f4f5f2', text: '#333333' },
    heritage: { primary: '#3c3127', accent: '#a1352a', bg: '#f6f3eb', paper: '#efe9dd', text: '#595045' },
    indigo:   { primary: '#ffffff', accent: '#a6c6d9', bg: '#10223d', paper: '#19335a', text: '#dbeafe' },
  }
  const c = colors[t]

  return {
    '--t-primary': c.primary,
    '--t-accent': c.accent,
    '--t-bg': c.bg,
    '--t-paper': c.paper,
    '--t-text': c.text,
    '--map-base-fill': isIndigo ? 'rgba(255,255,255,0.06)' : isNature ? '#eef1eb' : '#eae3d5',
    '--map-base-stroke': isIndigo ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.08)',
    '--map-active-fill': isIndigo ? '#ffffff' : c.primary,
    '--map-active-stroke': isIndigo ? '#10223d' : '#ffffff',
  }
})
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════
   Design-system font stacks (applied dynamically via :class)
   ═══════════════════════════════════════════════════════════════ */
.font-modern { font-family: "PingFang SC", "Helvetica Neue", -apple-system, sans-serif; }
.font-classical { font-family: "Noto Serif SC", "Songti SC", STSong, serif; }
.font-serif-modern { font-family: "Optima", "Noto Serif SC", serif; }

/* ── Poster base ── */
.marketing-poster {
  width: 440px; min-height: 860px;
  background-color: var(--t-bg); color: var(--t-text);
  box-shadow: 0 40px 80px rgba(0,0,0,0.15);
  position: relative; overflow: hidden;
  transition: background-color 0.4s ease, color 0.4s ease;
}
.canvas-hairline-frame {
  position: absolute; inset: 16px;
  border: 1px solid var(--t-primary); opacity: 0.08;
  pointer-events: none; z-index: 10;
}
.brand-title { font-weight: 700; color: var(--t-primary); margin: 0; }
.footer-line {
  position: absolute; left: 32px; right: 32px; bottom: 85px;
  height: 1px; background: var(--t-primary); opacity: 0.15;
}

/* ═══════════════════════════════════════════════════════════════
   Theme variants
   ═══════════════════════════════════════════════════════════════ */

/* ── 🌿 极简自然绿 ── */
.layout-nature .hero-image-frame { width: 100%; height: 320px; border-radius: 8px; box-shadow: 0 12px 24px rgba(42, 65, 40, 0.08); margin-bottom: 24px; }
.layout-nature .badge-tag { font-size: 10px; color: var(--t-primary); display: inline-block; margin-bottom: 12px; border-bottom: 1px solid var(--t-primary); padding-bottom: 2px; }
.layout-nature .brand-title { font-size: 36px; letter-spacing: 1px; margin-bottom: 12px; }
.layout-nature .poster-section-narrative { display: grid; grid-template-columns: 1fr 140px; gap: 24px; align-items: center; background: var(--t-paper); padding: 20px; border-radius: 8px; }
.layout-nature .narrative-text h3 { font-size: 15px; margin: 0 0 8px 0; color: var(--t-primary); }
.layout-nature .narrative-text p { font-size: 12px; line-height: 1.6; margin: 0; color: var(--t-text); }
.layout-nature :deep(.hl) { font-weight: bold; color: var(--t-primary); }
.layout-nature .map-component-inner { height: 120px; }
.layout-nature .poster-section-metrics { display: flex; gap: 12px; }
.layout-nature .metric-block { flex: 1; padding: 12px 0; text-align: left; border-top: 1px solid rgba(0,0,0,0.06); }
.layout-nature .m-label { font-size: 10px; margin-bottom: 4px; }
.layout-nature .m-value { font-size: 15px; color: var(--t-primary); }

/* ── 📜 东方风物 ── */
.layout-heritage { padding: 10px; }
.layout-heritage .poster-layout-container { border: 1px solid rgba(60,49,39,0.2); padding: 36px 24px; background: url('https://www.transparenttextures.com/patterns/rice-paper.png'); }
.layout-heritage .poster-section-hero { display: flex; flex-direction: row-reverse; justify-content: space-between; align-items: flex-start; }
.layout-heritage .hero-image-frame { width: 180px; height: 260px; border-radius: 200px 200px 0 0; padding: 4px; border: 1px solid rgba(60,49,39,0.3); }
.layout-heritage .visual-core-img { border-radius: 196px 196px 0 0; }
.layout-heritage .hero-text-cluster { display: flex; flex-direction: row-reverse; writing-mode: vertical-rl; height: 260px; align-items: flex-start; }
.layout-heritage .brand-title { font-size: 42px; font-weight: 500; letter-spacing: 0.1em; color: var(--t-primary); }
.layout-heritage .seal { display: inline-block; width: 24px; height: 24px; background: var(--t-accent); color: #fff; text-align: center; line-height: 24px; border-radius: 2px; font-size: 12px; margin-bottom: 12px; writing-mode: horizontal-tb; }
.layout-heritage .product-summary-desc { font-size: 13px; letter-spacing: 0.1em; margin-right: 16px; opacity: 0.9; }
.layout-heritage .poetic-bar { font-size: 12px; margin-right: 12px; padding-right: 8px; border-right: 1px solid var(--t-accent); }
.layout-heritage .poster-section-narrative { margin-top: 24px; display: flex; flex-direction: column; gap: 16px; }
.layout-heritage .narrative-text { text-align: center; border-bottom: 1px dashed rgba(60,49,39,0.2); padding-bottom: 16px; }
.layout-heritage .narrative-text h3 { font-size: 18px; margin: 0 0 8px 0; font-weight: 500; }
.layout-heritage .narrative-text p { font-size: 12px; opacity: 0.8; margin: 0; }
.layout-heritage :deep(.hl) { color: var(--t-accent); font-weight: bold; }
.layout-heritage .map-component-inner { width: 100%; height: 200px; }
.layout-heritage .poster-section-metrics { display: flex; justify-content: center; gap: 32px; margin-top: 16px; }
.layout-heritage .metric-block { text-align: center; }
.layout-heritage .m-label { font-size: 10px; color: var(--t-text); margin-bottom: 6px; }
.layout-heritage .m-value { font-size: 16px; color: var(--t-accent); font-weight: bold; }

/* ── 🧵 蓝印花布 ── */
.layout-indigo { position: relative; }
.layout-indigo::before {
  content: ''; position: absolute; inset: 0; z-index: 1; pointer-events: none; mix-blend-mode: overlay; opacity: 0.4;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}
.layout-indigo .canvas-hairline-frame { border: 2px solid var(--t-primary); opacity: 0.8; inset: 20px; border-radius: 4px; }
.layout-indigo .poster-layout-container { padding: 48px 40px; }
.layout-indigo .hero-image-frame { width: 100%; height: 220px; border: 4px solid var(--t-primary); position: relative; }
.layout-indigo .image-overlay { position: absolute; inset: 0; background: var(--t-bg); mix-blend-mode: screen; opacity: 0.5; pointer-events: none; }
.layout-indigo .visual-core-img { filter: grayscale(100%) contrast(120%); }
.layout-indigo .hero-text-cluster { margin-top: 24px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 24px; }
.layout-indigo .brand-title { font-size: 38px; letter-spacing: 4px; margin-bottom: 12px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
.layout-indigo .poster-section-narrative { position: relative; margin-top: 12px; }
.layout-indigo .narrative-text { position: absolute; top: 0; left: 0; right: 0; z-index: 2; text-align: center; text-shadow: 0 2px 8px rgba(16,34,61, 0.8); }
.layout-indigo .narrative-text h3 { font-size: 16px; margin: 0 0 6px 0; color: var(--t-accent); letter-spacing: 2px; }
.layout-indigo .narrative-text p { font-size: 12px; margin: 0; }
.layout-indigo :deep(.hl) { color: #ffffff; text-decoration: underline; text-decoration-color: var(--t-accent); text-underline-offset: 4px; }
.layout-indigo .map-component-inner { width: 100%; height: 240px; margin-top: 40px; opacity: 0.9; }
.layout-indigo .poster-section-metrics { display: flex; gap: 8px; }
.layout-indigo .metric-block { flex: 1; border: 1px solid rgba(255,255,255,0.3); padding: 12px 8px; text-align: center; background: rgba(25, 51, 90, 0.4); backdrop-filter: blur(4px); }
.layout-indigo .m-label { font-size: 9px; color: var(--t-accent); }
.layout-indigo .m-value { font-size: 14px; margin-top: 4px; display: block; }
</style>
