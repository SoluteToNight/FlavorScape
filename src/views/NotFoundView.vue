<template>
  <main class="not-found-page" aria-labelledby="not-found-title">
    <div class="map-field" aria-hidden="true">
      <div class="grid" />
      <svg class="route-lines" viewBox="0 0 1200 760" preserveAspectRatio="none">
        <path class="route route-amber" d="M-80 520 C 130 430, 210 270, 420 330 S 760 520, 980 300 S 1190 220, 1300 310" />
        <path class="route route-turq" d="M-70 260 C 150 310, 300 190, 470 240 S 760 380, 930 210 S 1110 110, 1280 170" />
        <path class="route route-red" d="M20 680 C 180 580, 300 610, 450 500 S 690 230, 850 350 S 1050 580, 1260 470" />
      </svg>
      <div class="specimen specimen-one" />
      <div class="specimen specimen-two" />
      <div class="specimen specimen-three" />
    </div>

    <section class="not-found-content">
      <p class="eyebrow">Lost Coordinate</p>
      <div class="code-mark" aria-hidden="true">
        <span>4</span>
        <span class="compass">
          <span class="needle" />
        </span>
        <span>4</span>
      </div>
      <h1 id="not-found-title">这条风味路线还没有被记录</h1>
      <p class="lead">
        {{ displayPath }} 没有对应的页面。可以回到地图重新定位，或进入风味基因库继续检索。
      </p>

      <div class="actions" aria-label="页面操作">
        <button class="primary-action" type="button" @click="router.push('/map')">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M9 18l-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Z" />
            <path d="M9 3v15M15 6v15" />
          </svg>
          探索地图
        </button>
        <button class="ghost-action" type="button" @click="goBack">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          返回上一页
        </button>
      </div>

      <nav class="quick-links" aria-label="快速入口">
        <RouterLink to="/library">
          <span class="link-dot dot-amber" />
          风味基因库
        </RouterLink>
        <RouterLink to="/narrative">
          <span class="link-dot dot-red" />
          时空叙事馆
        </RouterLink>
        <RouterLink to="/about">
          <span class="link-dot dot-turq" />
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
.not-found-page {
  position: fixed;
  top: var(--navbar-h);
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(248,244,239,0.98), rgba(239,232,220,0.92) 52%, rgba(248,244,239,0.98)),
    var(--bg);
}

.map-field {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.grid {
  position: absolute;
  inset: -14%;
  background:
    linear-gradient(rgba(92,75,57,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(92,75,57,0.035) 1px, transparent 1px);
  background-size: 72px 72px;
  mask-image: radial-gradient(circle at 52% 46%, rgba(0,0,0,0.56), transparent 73%);
  transform: rotate(-5deg);
}

.route-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.64;
}

.route {
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-dasharray: 9 15;
  animation: routeFlow 18s linear infinite;
}

.route-amber { stroke: rgba(200, 150, 15, 0.46); }
.route-turq { stroke: rgba(15, 184, 154, 0.34); animation-duration: 21s; }
.route-red { stroke: rgba(229, 57, 78, 0.30); animation-duration: 24s; }

.specimen {
  position: absolute;
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

.specimen-one {
  left: 9vw;
  top: 17vh;
  transform: rotate(-12deg);
}

.specimen-two {
  right: 11vw;
  top: 12vh;
  transform: scale(0.76) rotate(18deg);
}

.specimen-three {
  right: 15vw;
  bottom: 13vh;
  transform: scale(0.9) rotate(-8deg);
}

.not-found-content {
  position: relative;
  z-index: 1;
  width: min(860px, calc(100% - 40px));
  min-height: 100%;
  margin: 0 auto;
  padding: clamp(44px, 8vh, 82px) 0 42px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.eyebrow {
  margin-bottom: 12px;
  color: rgba(87,83,78,0.58);
  font-size: 11px;
  font-weight: 400;
  letter-spacing: 0.24em;
  text-transform: uppercase;
}

.code-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(10px, 2vw, 18px);
  color: rgba(28,25,23,0.90);
  font-family: var(--font-serif);
  font-size: clamp(86px, 15vw, 168px);
  font-weight: 500;
  line-height: 0.92;
  text-shadow: 0 1px 0 rgba(255,255,255,0.82);
}

.compass {
  position: relative;
  width: 0.74em;
  height: 0.74em;
  border: 1px solid rgba(200,150,15,0.45);
  border-radius: 50%;
  background:
    radial-gradient(circle, rgba(255,252,248,0.96) 0 29%, transparent 31%),
    conic-gradient(from 0deg, rgba(232,169,23,0.30), rgba(15,184,154,0.20), rgba(229,57,78,0.18), rgba(232,169,23,0.30));
  box-shadow:
    inset 0 0 0 10px rgba(255,252,248,0.44),
    0 16px 42px rgba(83,62,36,0.12);
}

.needle {
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

h1 {
  margin-top: 22px;
  color: rgba(28,25,23,0.88);
  font-family: var(--font-serif);
  font-size: clamp(24px, 3vw, 38px);
  font-weight: 500;
  letter-spacing: 0.08em;
}

.lead {
  width: min(620px, 100%);
  margin-top: 16px;
  color: rgba(87,83,78,0.76);
  font-size: clamp(13px, 1.35vw, 16px);
  font-weight: 300;
  line-height: 1.9;
  letter-spacing: 0.04em;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 32px;
}

.primary-action,
.ghost-action {
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  padding: 0 20px;
  border-radius: 999px;
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 400;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: transform var(--transition), box-shadow var(--transition), background var(--transition), border-color var(--transition);
}

.primary-action svg,
.ghost-action svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.primary-action {
  border: 1px solid rgba(200,150,15,0.42);
  background: rgba(200,150,15,0.90);
  color: #fffaf1;
  box-shadow: 0 14px 36px rgba(200,150,15,0.20);
}

.ghost-action {
  border: 1px solid rgba(180,165,140,0.34);
  background: rgba(255,252,248,0.72);
  color: rgba(87,83,78,0.86);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.primary-action:hover,
.ghost-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 42px rgba(83,62,36,0.12);
}

.primary-action:hover {
  background: rgba(183,123,8,0.94);
}

.ghost-action:hover {
  border-color: rgba(200,150,15,0.36);
  background: rgba(255,252,248,0.92);
}

.quick-links {
  width: min(660px, 100%);
  margin-top: 34px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.quick-links a {
  min-height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  padding: 12px;
  border: 1px solid rgba(180,165,140,0.22);
  border-radius: 8px;
  background: rgba(255,252,248,0.58);
  color: rgba(87,83,78,0.82);
  text-decoration: none;
  font-size: 12px;
  font-weight: 300;
  letter-spacing: 0.06em;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: color var(--transition), border-color var(--transition), background var(--transition), transform var(--transition);
}

.quick-links a:hover {
  color: var(--text);
  border-color: rgba(200,150,15,0.34);
  background: rgba(255,252,248,0.86);
  transform: translateY(-1px);
}

.link-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex: 0 0 auto;
}

.dot-amber { background: var(--amber); }
.dot-red { background: var(--carmine); }
.dot-turq { background: var(--turquoise); }

@keyframes routeFlow {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -240; }
}

@keyframes seek {
  0%, 100% { transform: translate(-50%, -88%) rotate(34deg); }
  45% { transform: translate(-50%, -88%) rotate(62deg); }
  72% { transform: translate(-50%, -88%) rotate(20deg); }
}

@media (max-width: 760px) {
  .not-found-content {
    width: min(520px, calc(100% - 32px));
    padding-top: 38px;
  }

  .specimen {
    opacity: 0.48;
  }

  .specimen-one {
    left: -28px;
    top: 16vh;
  }

  .specimen-two {
    right: -34px;
    top: 11vh;
  }

  .specimen-three {
    display: none;
  }

  h1 {
    letter-spacing: 0.04em;
  }

  .lead {
    line-height: 1.78;
  }

  .actions {
    width: 100%;
  }

  .primary-action,
  .ghost-action {
    flex: 1 1 180px;
  }

  .quick-links {
    grid-template-columns: 1fr;
    margin-top: 22px;
  }
}

@media (max-width: 420px) {
  .code-mark {
    font-size: 78px;
  }

  .actions {
    gap: 9px;
  }

  .primary-action,
  .ghost-action {
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .route,
  .needle {
    animation: none;
  }
}
</style>
