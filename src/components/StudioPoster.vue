<template>
  <article
    class="marketing-poster relative"
    :class="[themeLayout, themeFont, paramLayout, paramDensity, paramImage, paramMetric]"
    :style="{ ...cssVars, transform: `scale(${scale})`, transformOrigin: 'top left' }"
  >
    <div class="canvas-hairline-frame" />
    <div class="poster-layout-container relative z-[5] flex flex-col h-full px-8 py-10 gap-8">
      <header class="poster-section-hero">
        <div
          v-if="posterData.modules?.mainImage !== false && posterData.heroImage"
          class="hero-image-frame relative bg-[var(--t-paper)] overflow-hidden"
          :style="{ height: imageHeight }"
        >
          <img
            :src="posterData.heroImage"
            :alt="posterData.title"
            class="visual-core-img w-full h-full object-cover block"
            :style="{ objectPosition: `center ${posterData.imagePosY ?? 50}%` }"
          />
          <div v-if="theme === 'indigo'" class="image-overlay" />
        </div>

        <div v-if="posterData.modules?.brandCopy !== false" class="hero-text-cluster">
          <div class="title-wrap">
            <span v-if="theme === 'nature'" class="badge-tag">{{ templateParams.badgeText }}</span>
            <span v-if="theme === 'heritage'" class="badge-tag seal">印</span>
            <h1 class="brand-title" :style="{ fontSize: titleFontSize }">{{ posterData.title }}</h1>
          </div>
          <p v-if="posterData.subtitle" class="product-summary-desc text-[13px] opacity-80 m-0 leading-[1.5]">{{ posterData.subtitle }}</p>
          <div v-if="posterData.poeticLine" class="poetic-bar text-[12px] italic opacity-70">{{ posterData.poeticLine }}</div>
        </div>
      </header>

      <section v-if="showNarrativeSection" class="poster-section-narrative">
        <div v-if="posterData.modules?.brandCopy !== false && posterData.narrative" class="narrative-text">
          <span class="text-[10px] uppercase tracking-[0.1em] opacity-50 font-sans block mb-1">{{ themeKicker }}</span>
          <h3>{{ themeSubtitle }}</h3>
          <p v-html="narrativeHtml" />
        </div>
        <div v-if="posterData.modules?.spatialMap !== false && posterData.spatial?.nodes?.length" class="map-component-inner">
          <StaticGeoMap :target-province="posterData.province" :nodes="posterData.spatial?.nodes || []" />
        </div>
      </section>

      <section v-if="posterData.modules?.evidenceMetrics !== false && posterData.spatial?.evidence?.length" class="poster-section-metrics">
        <div v-for="item in posterData.spatial?.evidence || []" :key="item.label" class="metric-block">
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
        <div class="qr-mark">
          <span />
          <span />
          <span />
          <span />
        </div>
      </footer>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import StaticGeoMap from './StaticGeoMap.vue'

const props = defineProps({
  posterData: { type: Object, required: true },
  scale: { type: Number, default: 1 },
})

const theme = computed(() => props.posterData?.theme || 'nature')
const templateParams = computed(() => ({
  layout: 'balanced',
  palette: 'default',
  density: 'normal',
  imageShape: 'standard',
  metricStyle: 'cards',
  titleScale: 100,
  badgeText: '真实产地 · 空间溯源 · 品牌资产',
  ...(props.posterData?.templateParams || {}),
}))

const themeLayout = computed(() => {
  const map = { nature: 'layout-nature', heritage: 'layout-heritage', indigo: 'layout-indigo' }
  return map[theme.value] || 'layout-nature'
})

const themeFont = computed(() => {
  const map = { nature: 'font-modern', heritage: 'font-classical', indigo: 'font-serif-modern' }
  return map[theme.value] || 'font-modern'
})

const paramLayout = computed(() => `param-layout-${templateParams.value.layout || 'balanced'}`)
const paramDensity = computed(() => `param-density-${templateParams.value.density || 'normal'}`)
const paramImage = computed(() => `param-image-${templateParams.value.imageShape || 'standard'}`)
const paramMetric = computed(() => `param-metric-${templateParams.value.metricStyle || 'cards'}`)

const themeSubtitle = computed(() => {
  const map = { nature: '好食溯源', heritage: '山河空间志', indigo: '原产地拓印' }
  return map[theme.value] || '好食溯源'
})

const themeKicker = computed(() => {
  const map = { nature: 'NATURE EXPLORATION', heritage: 'ORIENTAL HERITAGE', indigo: 'CYANOTYPE PRINT' }
  return map[theme.value] || 'NATURE EXPLORATION'
})

const showNarrativeSection = computed(() =>
  (props.posterData.modules?.brandCopy !== false && Boolean(props.posterData.narrative))
  || (props.posterData.modules?.spatialMap !== false && Boolean(props.posterData.spatial?.nodes?.length))
)

const narrativeHtml = computed(() => sanitizeNarrative(props.posterData?.narrative || ''))
const titleFontSize = computed(() => {
  const base = { nature: 36, heritage: 42, indigo: 38 }[theme.value] || 36
  const scale = Number(templateParams.value.titleScale || 100) / 100
  return `${Math.round(base * scale)}px`
})
const imageHeight = computed(() => {
  const base = { nature: 320, heritage: 260, indigo: 220 }[theme.value] || 320
  const densityDelta = { compact: -36, normal: 0, airy: 28 }[templateParams.value.density] || 0
  const shapeDelta = templateParams.value.imageShape === 'full' ? 42 : 0
  return `${Math.max(170, base + densityDelta + shapeDelta)}px`
})

function sanitizeNarrative(value) {
  return String(value)
    .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
    .replace(/<(?!\/?span(?=>|\s.*>))[^>]+>/gi, '')
    .replace(/<span(?!\s+class=["']hl["']\s*>)[^>]*>/gi, '<span>')
}

const cssVars = computed(() => {
  const colors = {
    nature:   { primary: '#2a4128', accent: '#708a68', bg: '#ffffff', paper: '#f4f5f2', text: '#333333' },
    heritage: { primary: '#3c3127', accent: '#a1352a', bg: '#f6f3eb', paper: '#efe9dd', text: '#595045' },
    indigo:   { primary: '#ffffff', accent: '#a6c6d9', bg: '#10223d', paper: '#19335a', text: '#dbeafe' },
  }
  const palettes = {
    default: {},
    fresh: { accent: '#6f9f7a', paper: '#eef4ec' },
    warm: { accent: '#b56b3c', paper: '#f4eadb' },
    noir: { primary: '#f8efe0', accent: '#d6b56d', bg: '#171411', paper: '#252018', text: '#f5ead8' },
  }
  const c = { ...(colors[theme.value] || colors.nature), ...(palettes[templateParams.value.palette] || {}) }
  const isIndigo = theme.value === 'indigo'
  const isNature = theme.value === 'nature'

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
.font-modern { font-family: "PingFang SC", "Helvetica Neue", -apple-system, sans-serif; }
.font-classical { font-family: "Noto Serif SC", "Songti SC", STSong, serif; }
.font-serif-modern { font-family: "Optima", "Noto Serif SC", serif; }

.marketing-poster {
  width: 440px;
  min-height: 860px;
  height: auto;
  background-color: var(--t-bg);
  color: var(--t-text);
  box-shadow: 0 40px 80px rgba(0,0,0,0.15);
  position: relative;
  overflow: hidden;
  transition: background-color 0.25s ease, color 0.25s ease;
}

.poster-layout-container {
  min-height: 860px;
  height: auto !important;
}

.canvas-hairline-frame {
  position: absolute;
  inset: 16px;
  border: 1px solid var(--t-primary);
  opacity: 0.08;
  pointer-events: none;
  z-index: 10;
}

.brand-title {
  font-weight: 700;
  color: var(--t-primary);
  margin: 0;
  overflow-wrap: anywhere;
}

.footer-line {
  position: absolute;
  left: 32px;
  right: 32px;
  bottom: 85px;
  height: 1px;
  background: var(--t-primary);
  opacity: 0.15;
}

.qr-mark {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 3px;
  width: 36px;
  height: 36px;
  border: 1px solid var(--t-primary);
  opacity: 0.32;
  padding: 5px;
}

.qr-mark span {
  background: var(--t-primary);
}

.layout-nature .hero-image-frame { width: 100%; height: 320px; border-radius: 8px; box-shadow: 0 12px 24px rgba(42, 65, 40, 0.08); margin-bottom: 24px; }
.layout-nature .badge-tag { font-size: 10px; color: var(--t-primary); display: inline-block; margin-bottom: 12px; border-bottom: 1px solid var(--t-primary); padding-bottom: 2px; }
.layout-nature .brand-title { font-size: 36px; margin-bottom: 12px; }
.layout-nature .poster-section-narrative { display: grid; grid-template-columns: 1fr 140px; gap: 24px; align-items: center; background: var(--t-paper); padding: 20px; border-radius: 8px; }
.layout-nature .narrative-text h3 { font-size: 15px; margin: 0 0 8px 0; color: var(--t-primary); }
.layout-nature .narrative-text p { font-size: 12px; line-height: 1.6; margin: 0; color: var(--t-text); }
.layout-nature :deep(.hl) { font-weight: bold; color: var(--t-primary); }
.layout-nature .map-component-inner { height: 120px; }
.layout-nature .poster-section-metrics { display: flex; gap: 12px; }
.layout-nature .metric-block { flex: 1; padding: 12px 0; text-align: left; border-top: 1px solid rgba(0,0,0,0.06); }
.layout-nature .m-label { font-size: 10px; margin-bottom: 4px; display: block; opacity: 0.68; }
.layout-nature .m-value { font-size: 15px; color: var(--t-primary); }

.layout-heritage { padding: 10px; }
.layout-heritage .poster-layout-container { border: 1px solid rgba(60,49,39,0.2); padding: 36px 24px; background: #f8f3e8; }
.layout-heritage .poster-layout-container::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.22;
  pointer-events: none;
  background-image: radial-gradient(rgba(60,49,39,0.18) 0.7px, transparent 0.7px);
  background-size: 9px 9px;
}
.layout-heritage .poster-section-hero { display: flex; flex-direction: row-reverse; justify-content: space-between; align-items: flex-start; }
.layout-heritage .hero-image-frame { width: 180px; height: 260px; border-radius: 200px 200px 0 0; padding: 4px; border: 1px solid rgba(60,49,39,0.3); }
.layout-heritage .visual-core-img { border-radius: 196px 196px 0 0; }
.layout-heritage .hero-text-cluster { display: flex; flex-direction: row-reverse; writing-mode: vertical-rl; height: 260px; align-items: flex-start; }
.layout-heritage .brand-title { font-size: 42px; font-weight: 500; letter-spacing: 0.08em; color: var(--t-primary); }
.layout-heritage .seal { display: inline-block; width: 24px; height: 24px; background: var(--t-accent); color: #fff; text-align: center; line-height: 24px; border-radius: 2px; font-size: 12px; margin-bottom: 12px; writing-mode: horizontal-tb; }
.layout-heritage .product-summary-desc { font-size: 13px; letter-spacing: 0.08em; margin-right: 16px; opacity: 0.9; }
.layout-heritage .poetic-bar { font-size: 12px; margin-right: 12px; padding-right: 8px; border-right: 1px solid var(--t-accent); }
.layout-heritage .poster-section-narrative { margin-top: 24px; display: flex; flex-direction: column; gap: 16px; }
.layout-heritage .narrative-text { text-align: center; border-bottom: 1px dashed rgba(60,49,39,0.2); padding-bottom: 16px; }
.layout-heritage .narrative-text h3 { font-size: 18px; margin: 0 0 8px 0; font-weight: 500; }
.layout-heritage .narrative-text p { font-size: 12px; opacity: 0.8; margin: 0; }
.layout-heritage :deep(.hl) { color: var(--t-accent); font-weight: bold; }
.layout-heritage .map-component-inner { width: 100%; height: 200px; }
.layout-heritage .poster-section-metrics { display: flex; justify-content: center; gap: 32px; margin-top: 16px; }
.layout-heritage .metric-block { text-align: center; }
.layout-heritage .m-label { font-size: 10px; color: var(--t-text); margin-bottom: 6px; display: block; opacity: 0.7; }
.layout-heritage .m-value { font-size: 16px; color: var(--t-accent); font-weight: bold; }

.layout-indigo { position: relative; }
.layout-indigo::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: 0.28;
  background-image: radial-gradient(rgba(255,255,255,0.22) 0.8px, transparent 0.8px);
  background-size: 7px 7px;
}
.layout-indigo .canvas-hairline-frame { border: 2px solid var(--t-primary); opacity: 0.8; inset: 20px; border-radius: 4px; }
.layout-indigo .poster-layout-container { padding: 48px 40px; }
.layout-indigo .hero-image-frame { width: 100%; height: 220px; border: 4px solid var(--t-primary); position: relative; }
.layout-indigo .image-overlay { position: absolute; inset: 0; background: var(--t-bg); mix-blend-mode: screen; opacity: 0.5; pointer-events: none; }
.layout-indigo .visual-core-img { filter: grayscale(100%) contrast(120%); }
.layout-indigo .hero-text-cluster { margin-top: 24px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 24px; }
.layout-indigo .brand-title { font-size: 38px; margin-bottom: 12px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
.layout-indigo .poster-section-narrative { position: relative; margin-top: 12px; }
.layout-indigo .narrative-text { position: absolute; top: 0; left: 0; right: 0; z-index: 2; text-align: center; text-shadow: 0 2px 8px rgba(16,34,61, 0.8); }
.layout-indigo .narrative-text h3 { font-size: 16px; margin: 0 0 6px 0; color: var(--t-accent); letter-spacing: 2px; }
.layout-indigo .narrative-text p { font-size: 12px; margin: 0; }
.layout-indigo :deep(.hl) { color: #ffffff; text-decoration: underline; text-decoration-color: var(--t-accent); text-underline-offset: 4px; }
.layout-indigo .map-component-inner { width: 100%; height: 240px; margin-top: 40px; opacity: 0.9; }
.layout-indigo .poster-section-metrics { display: flex; gap: 8px; }
.layout-indigo .metric-block { flex: 1; border: 1px solid rgba(255,255,255,0.3); padding: 12px 8px; text-align: center; background: rgba(25, 51, 90, 0.4); }
.layout-indigo .m-label { font-size: 9px; color: var(--t-accent); display: block; }
.layout-indigo .m-value { font-size: 14px; margin-top: 4px; display: block; }

.param-density-compact .poster-layout-container {
  gap: 18px;
  padding-top: 32px;
  padding-bottom: 32px;
}

.param-density-airy .poster-layout-container {
  gap: 34px;
}

.param-layout-editorial .poster-section-narrative {
  border-left: 4px solid color-mix(in srgb, var(--t-accent) 52%, transparent);
}

.param-layout-evidence .poster-section-metrics {
  order: 2;
}

.param-layout-evidence .metric-block {
  border-color: color-mix(in srgb, var(--t-accent) 34%, transparent);
  background: color-mix(in srgb, var(--t-paper) 84%, var(--t-accent) 16%);
  padding: 12px;
}

.param-image-arch .hero-image-frame {
  border-radius: 160px 160px 8px 8px !important;
}

.param-image-full .hero-image-frame {
  width: calc(100% + 64px) !important;
  margin-left: -32px;
  margin-right: -32px;
  border-radius: 0 !important;
}

.param-metric-inline .poster-section-metrics {
  display: grid;
  grid-template-columns: 1fr;
  gap: 6px;
}

.param-metric-inline .metric-block {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  min-width: 0;
  padding: 8px 0;
  text-align: left;
}

.param-metric-inline .m-label,
.param-metric-inline .m-value {
  margin: 0;
}
</style>
