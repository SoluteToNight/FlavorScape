<template>
  <main class="fixed top-navbar inset-x-0 bottom-0 overflow-hidden bg-[linear-gradient(135deg,rgba(248,244,239,0.98),rgba(239,232,220,0.92)_52%,rgba(248,244,239,0.98))]" aria-labelledby="not-found-title">
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <div class="grid-bg absolute -inset-[14%] bg-[length:72px_72px] rotate-[-5deg]" />
      <svg class="route-lines absolute inset-0 w-full h-full opacity-60" viewBox="0 0 1200 760" preserveAspectRatio="none">
        <path class="route route-amber" d="M-80 520 C 130 430, 210 270, 420 330 S 760 520, 980 300 S 1190 220, 1300 310" />
        <path class="route route-turq" d="M-70 260 C 150 310, 300 190, 470 240 S 760 380, 930 210 S 1110 110, 1280 170" />
        <path class="route route-red" d="M20 680 C 180 580, 300 610, 450 500 S 690 230, 850 350 S 1050 580, 1260 470" />
      </svg>
      <div class="specimen specimen-one absolute left-[9vw] top-[17vh] -rotate-[12deg]" />
      <div class="specimen specimen-two absolute right-[11vw] top-[12vh] scale-[0.76] rotate-[18deg]" />
      <div class="specimen specimen-three absolute right-[15vw] bottom-[13vh] scale-90 -rotate-[8deg]" />
    </div>

    <section class="not-found-content relative z-[1] w-[min(860px,calc(100%-40px))] min-h-full mx-auto py-[clamp(44px,8vh,82px)] pb-[42px] flex flex-col items-center justify-center text-center">
      <p class="eyebrow mb-3 text-[rgba(87,83,78,0.58)] text-[11px] font-normal tracking-[0.24em] uppercase">Lost Coordinate</p>
      <div class="code-mark flex items-center justify-center gap-[clamp(10px,2vw,18px)] font-serif text-[clamp(86px,15vw,168px)] font-medium leading-[0.92] text-[rgba(28,25,23,0.9)]" aria-hidden="true">
        <span>4</span>
        <span class="compass relative w-[0.74em] h-[0.74em]" />
        <span>4</span>
      </div>
      <h1 id="not-found-title" class="mt-[22px] text-[rgba(28,25,23,0.88)] font-serif text-[clamp(24px,3vw,38px)] font-medium tracking-[0.08em]">这条风味路线还没有被记录</h1>
      <p class="lead w-[min(620px,100%)] mt-4 text-[rgba(87,83,78,0.76)] text-[clamp(13px,1.35vw,16px)] font-light leading-[1.9] tracking-[0.04em]">
        {{ displayPath }} 没有对应的页面。可以回到地图重新定位，或进入风味基因库继续检索。
      </p>

      <div class="actions flex flex-wrap justify-center gap-3 mt-8" aria-label="页面操作">
        <button class="primary-action h-11 inline-flex items-center justify-center gap-[9px] px-5 rounded-full font-sans text-[13px] font-normal tracking-[0.08em] cursor-pointer transition-all" type="button" @click="router.push('/map')">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M9 18l-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Z" />
            <path d="M9 3v15M15 6v15" />
          </svg>
          探索地图
        </button>
        <button class="ghost-action h-11 inline-flex items-center justify-center gap-[9px] px-5 rounded-full font-sans text-[13px] font-normal tracking-[0.08em] cursor-pointer transition-all" type="button" @click="goBack">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          返回上一页
        </button>
      </div>

      <nav class="quick-links w-[min(660px,100%)] mt-[34px] grid grid-cols-3 gap-[10px]" aria-label="快速入口">
        <RouterLink to="/library" class="min-h-[52px] flex items-center justify-center gap-[9px] p-3 rounded-lg text-[12px] font-light tracking-[0.06em]">
          <span class="link-dot w-[7px] h-[7px] rounded-full shrink-0 bg-[var(--amber)]" />
          风味基因库
        </RouterLink>
        <RouterLink to="/narrative" class="min-h-[52px] flex items-center justify-center gap-[9px] p-3 rounded-lg text-[12px] font-light tracking-[0.06em]">
          <span class="link-dot w-[7px] h-[7px] rounded-full shrink-0 bg-[var(--carmine)]" />
          时空叙事馆
        </RouterLink>
        <RouterLink to="/about" class="min-h-[52px] flex items-center justify-center gap-[9px] p-3 rounded-lg text-[12px] font-light tracking-[0.06em]">
          <span class="link-dot w-[7px] h-[7px] rounded-full shrink-0 bg-[var(--turquoise)]" />
          关于方法论
        </RouterLink>
      </nav>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const displayPath = computed(() => {
  const path = route.fullPath || '/'
  return path.length > 42 ? `${path.slice(0, 39)}...` : path
})

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════
   KEPT — Tailwind cannot express these:
   mask-image, SVG animations, conic-gradient,
   pseudo-elements, text-shadow, complex button states,
   backdrop-filter, @keyframes, responsive overrides
   ═══════════════════════════════════════════════════════════════ */

/* KEPT: mask-image grid pattern */
.grid-bg {
  background:
    linear-gradient(rgba(92,75,57,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(92,75,57,0.035) 1px, transparent 1px);
  mask-image: radial-gradient(circle at 52% 46%, rgba(0,0,0,0.56), transparent 73%);
}

/* KEPT: SVG stroke animations */
.route {
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-dasharray: 9 15;
  animation: routeFlow 18s linear infinite;
}
.route-amber { stroke: rgba(200, 150, 15, 0.46); }
.route-turq  { stroke: rgba(15, 184, 154, 0.34); animation-duration: 21s; }
.route-red   { stroke: rgba(229, 57, 78, 0.30); animation-duration: 24s; }

/* KEPT: conic-gradient + pseudo-element decorative rings */
.specimen {
  width: clamp(86px, 10vw, 148px);
  aspect-ratio: 1;
  border: 1px solid rgba(180,165,140,0.28);
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 50%, rgba(255,252,248,0.72), transparent 58%),
    conic-gradient(from 30deg, rgba(232,169,23,0.24), rgba(15,184,154,0.20), rgba(229,57,78,0.18), rgba(232,169,23,0.24));
  box-shadow: 0 20px 60px rgba(83,62,36,0.08);
}
.specimen::before,
.specimen::after {
  content: '';
  position: absolute;
  inset: 18%;
  border-radius: 50%;
  border: 1px solid rgba(92,75,57,0.18);
}
.specimen::after {
  inset: 37%;
  background: rgba(255,252,248,0.64);
}

/* KEPT: conic-gradient + inset shadow + pseudo-element compass needle */
.compass {
  border: 1px solid rgba(200,150,15,0.45);
  border-radius: 50%;
  background:
    radial-gradient(circle, rgba(255,252,248,0.96) 0 29%, transparent 31%),
    conic-gradient(from 0deg, rgba(232,169,23,0.30), rgba(15,184,154,0.20), rgba(229,57,78,0.18), rgba(232,169,23,0.30));
  box-shadow:
    inset 0 0 0 10px rgba(255,252,248,0.44),
    0 16px 42px rgba(83,62,36,0.12);
}
.compass::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  width: 12%;
  height: 56%;
  border-radius: 999px;
  background: linear-gradient(to bottom, var(--carmine), var(--amber));
  transform-origin: 50% 88%;
  transform: translate(-50%, -88%) rotate(34deg);
  animation: seek 3.8s ease-in-out infinite;
}

/* KEPT: text-shadow — no Tailwind utility equivalent */
.code-mark {
  text-shadow: 0 1px 0 rgba(255,255,255,0.82);
}

/* KEPT: complex button colors + hover effects + SVG styles */
.primary-action {
  border: 1px solid rgba(200,150,15,0.42);
  background: rgba(200,150,15,0.90);
  color: #fffaf1;
  box-shadow: 0 14px 36px rgba(200,150,15,0.20);
}
.primary-action svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.primary-action:hover {
  background: rgba(183,123,8,0.94);
  transform: translateY(-1px);
  box-shadow: 0 18px 42px rgba(83,62,36,0.12);
}

.ghost-action {
  border: 1px solid rgba(180,165,140,0.34);
  background: rgba(255,252,248,0.72);
  color: rgba(87,83,78,0.86);
  backdrop-filter: blur(12px);
}
.ghost-action svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.ghost-action:hover {
  border-color: rgba(200,150,15,0.36);
  background: rgba(255,252,248,0.92);
  transform: translateY(-1px);
  box-shadow: 0 18px 42px rgba(83,62,36,0.12);
}

/* KEPT: backdrop-filter + hover effects on quick-link cards */
.quick-links a {
  border: 1px solid rgba(180,165,140,0.22);
  background: rgba(255,252,248,0.58);
  color: rgba(87,83,78,0.82);
  text-decoration: none;
  backdrop-filter: blur(12px);
  transition: color var(--transition), border-color var(--transition), background var(--transition), transform var(--transition);
}
.quick-links a:hover {
  color: var(--text);
  border-color: rgba(200,150,15,0.34);
  background: rgba(255,252,248,0.86);
  transform: translateY(-1px);
}

/* KEPT: @keyframes — Tailwind has no animation definition system */
@keyframes routeFlow {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -240; }
}
@keyframes seek {
  0%, 100% { transform: translate(-50%, -88%) rotate(34deg); }
  45% { transform: translate(-50%, -88%) rotate(62deg); }
  72% { transform: translate(-50%, -88%) rotate(20deg); }
}

/* KEPT: responsive overrides with complex selectors */
@media (max-width: 760px) {
  .not-found-content {
    width: min(520px, calc(100% - 32px));
    padding-top: 38px;
  }
  .specimen { opacity: 0.48; }
  .specimen-one { left: -28px; top: 16vh; }
  .specimen-two { right: -34px; top: 11vh; }
  .specimen-three { display: none; }
  h1 { letter-spacing: 0.04em; }
  .lead { line-height: 1.78; }
  .actions { width: 100%; }
  .primary-action,
  .ghost-action { flex: 1 1 180px; }
  .quick-links {
    grid-template-columns: 1fr;
    margin-top: 22px;
  }
}

@media (max-width: 420px) {
  .code-mark { font-size: 78px; }
  .actions { gap: 9px; }
  .primary-action,
  .ghost-action { width: 100%; }
}

@media (prefers-reduced-motion: reduce) {
  .route,
  .compass::after {
    animation: none;
  }
}
</style>
