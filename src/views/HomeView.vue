<template>
  <div class="home-page">
    <div class="atlas-layer" aria-hidden="true">
      <svg class="specimen specimen-chili" viewBox="0 0 90 170" aria-hidden="true">
        <path d="M47 15 C62 50 66 91 48 128 C41 143 30 153 18 159 C31 137 30 111 22 84 C14 57 24 31 47 15 Z" />
        <path d="M50 18 C55 10 62 7 72 9" />
      </svg>
      <svg class="specimen specimen-star" viewBox="0 0 150 150" aria-hidden="true">
        <path d="M75 18 L88 58 L128 52 L96 78 L114 116 L76 94 L41 118 L55 78 L22 52 L63 58 Z" />
        <path d="M75 18 L76 94 M22 52 L96 78 M128 52 L55 78 M41 118 L88 58 M114 116 L63 58" />
      </svg>
      <svg class="specimen specimen-rice" viewBox="0 0 150 130" aria-hidden="true">
        <path d="M28 102 C48 64 79 42 123 27" />
        <path d="M48 74 C39 60 40 45 50 32 C61 47 60 62 48 74 Z" />
        <path d="M73 56 C64 41 66 29 78 18 C88 34 86 47 73 56 Z" />
        <path d="M96 44 C89 31 94 18 108 12 C113 28 109 38 96 44 Z" />
      </svg>
    </div>
    <canvas ref="canvasEl" class="bg-canvas" />
    <div class="content">
      <p class="eyebrow">Flavor Geography · 食物地理博物志</p>
      <h1 class="tagline">寻味地理</h1>
      <p class="identity-line">一座食物的地理博物志</p>
      <p class="subtitle">
        从水系、山脉、贸易路线到风味基因，观察同一种食物如何在不同地方长出不同味道。
      </p>
      <p class="poetic-line">探寻同一种食物，在不同水土中写下的味道基因。</p>
      <button class="cta-btn" @click="router.push('/map')">开&ensp;启&ensp;地&ensp;图</button>
    </div>
    <div class="sample-strip" aria-label="首页数据样本">
      <article v-for="sample in sampleCards" :key="sample.title" class="sample-card">
        <span class="sample-type">{{ sample.type }}</span>
        <h2>{{ sample.title }}</h2>
        <p>{{ sample.body }}</p>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const canvasEl = ref(null)

const sampleCards = [
  {
    type: '火锅样本',
    title: '成都：麻 0.90 / 辣 0.95',
    body: '顺德：鲜 0.82 / 麻 0.05，同一饮食类型在不同水土中改写风味重心。',
  },
  {
    type: '传播线索',
    title: '辣椒入华 → 长江上游',
    body: '路线、港口与山地通道共同决定食材进入地方菜系的速度。',
  },
  {
    type: '生态影响',
    title: '湿热盆地提高辛香依赖',
    body: '气候、水系和盐业网络会改变保存方式、调味偏好与味觉表达。',
  },
]
let rafId = null
let cleanupHomeCanvas = () => {}

const pathDefs = [
  { pts: [[0.1,0.5],[0.3,0.3],[0.5,0.4],[0.7,0.35],[0.9,0.5]], col: '#C8960F' },
  { pts: [[0.0,0.3],[0.2,0.45],[0.4,0.5],[0.6,0.4],[0.85,0.55]], col: '#2BB89C' },
  { pts: [[0.15,0.7],[0.35,0.55],[0.55,0.6],[0.75,0.5],[0.95,0.65]], col: '#C84B4B' },
  { pts: [[0.05,0.2],[0.25,0.35],[0.5,0.25],[0.75,0.4],[0.9,0.3]], col: '#C8960F' },
  { pts: [[0.2,0.8],[0.4,0.65],[0.6,0.7],[0.8,0.6],[1.0,0.75]], col: '#7B9E5A' },
]

function catmull(pts, t, W, H) {
  const n = pts.length - 1
  const seg = Math.min(Math.floor(t * n), n - 1)
  const lt = t * n - seg
  const p0 = pts[Math.max(0, seg - 1)]
  const p1 = pts[seg]
  const p2 = pts[Math.min(n, seg + 1)]
  const p3 = pts[Math.min(n, seg + 2)]
  const t2 = lt * lt, t3 = t2 * lt
  return [
    0.5 * ((2*p1[0]) + (-p0[0]+p2[0])*lt + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3) * W,
    0.5 * ((2*p1[1]) + (-p0[1]+p2[1])*lt + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3) * H,
  ]
}

onMounted(() => {
  const canvas = canvasEl.value
  const ctx = canvas.getContext('2d')
  let W, H, mouseX, mouseY

  const resize = () => {
    W = canvas.width = window.innerWidth
    H = canvas.height = window.innerHeight
    mouseX = W / 2; mouseY = H / 2
  }
  resize()

  window.addEventListener('resize', resize)
  const onMouseMove = e => { mouseX = e.clientX; mouseY = e.clientY }
  window.addEventListener('mousemove', onMouseMove)

  const particles = pathDefs.flatMap((pd, pi) =>
    Array.from({ length: 5 }, () => ({
      pi, t: Math.random(),
      speed: 0.0006 + Math.random() * 0.0004,
      col: pd.col,
      size: 1.5 + Math.random() * 1.5,
      trail: [], trailLen: 18 + Math.floor(Math.random() * 12),
    }))
  )

  function draw() {
    ctx.clearRect(0, 0, W, H)
    // Subtle terrain traces keep the particle field grounded without becoming a map.
    ctx.save()
    ctx.strokeStyle = 'rgba(180,160,130,0.08)'
    ctx.lineWidth = 0.5
    ctx.setLineDash([4, 10])
    ;[[0.1,0.38,0.9,0.42],[0.0,0.58,1.0,0.62],[0.15,0.22,0.85,0.28]].forEach(([x1,y1,x2,y2]) => {
      ctx.beginPath(); ctx.moveTo(x1*W, y1*H); ctx.lineTo(x2*W, y2*H); ctx.stroke()
    })
    ctx.setLineDash([]); ctx.restore()

    particles.forEach(p => {
      const prevT = p.t
      p.t = (p.t + p.speed) % 1
      if (p.t < prevT) p.trail = []
      const [x, y] = catmull(pathDefs[p.pi].pts, p.t, W, H)
      const drift = 0.008
      const fx = x + (mouseX - W/2) * drift * (1 - p.t)
      const fy = y + (mouseY - H/2) * drift * (1 - p.t)
      p.trail.push([fx, fy])
      if (p.trail.length > p.trailLen) p.trail.shift()
      for (let i = 1; i < p.trail.length; i++) {
        const a = (i / p.trail.length) * 0.55
        ctx.beginPath()
        ctx.moveTo(p.trail[i-1][0], p.trail[i-1][1])
        ctx.lineTo(p.trail[i][0], p.trail[i][1])
        ctx.strokeStyle = p.col + Math.floor(a * 255).toString(16).padStart(2, '0')
        ctx.lineWidth = p.size * (i / p.trail.length)
        ctx.stroke()
      }
      ctx.beginPath(); ctx.arc(fx, fy, p.size * 1.2, 0, Math.PI * 2)
      ctx.fillStyle = p.col; ctx.globalAlpha = 0.9; ctx.fill(); ctx.globalAlpha = 1
    })
    rafId = requestAnimationFrame(draw)
  }

  draw()

  cleanupHomeCanvas = () => {
    window.removeEventListener('resize', resize)
    window.removeEventListener('mousemove', onMouseMove)
  }
})

onUnmounted(() => {
  cancelAnimationFrame(rafId)
  cleanupHomeCanvas()
  cleanupHomeCanvas = () => {}
})
</script>

<style scoped>
.home-page {
  position: fixed;
  inset: 0;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 42%, rgba(255,252,248,0.94) 0, rgba(248,244,239,0.72) 36%, transparent 62%),
    linear-gradient(135deg, #f8f4ef 0%, #f1e8dc 48%, #f8f4ef 100%);
}
.home-page::before {
  content: '';
  position: absolute;
  inset: -18%;
  background:
    linear-gradient(rgba(92,75,57,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(92,75,57,0.028) 1px, transparent 1px);
  background-size: 84px 84px;
  mask-image: radial-gradient(circle at 50% 48%, rgba(0,0,0,0.50), transparent 70%);
  transform: rotate(-6deg);
}
.atlas-layer {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
.specimen path {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.specimen {
  position: absolute;
  opacity: 0.24;
  filter: drop-shadow(0 12px 24px rgba(83,62,36,0.05));
  animation: fadeUp 1.4s ease 0.35s both;
}
.specimen path {
  stroke: rgba(92,75,57,0.72);
  stroke-width: 2;
}
.specimen-chili {
  left: clamp(22px, 7vw, 104px);
  top: 20vh;
  width: 72px;
  transform: rotate(-10deg);
}
.specimen-star {
  right: clamp(28px, 8vw, 126px);
  top: 18vh;
  width: 94px;
  transform: rotate(14deg);
}
.specimen-rice {
  right: clamp(34px, 9vw, 150px);
  bottom: 22vh;
  width: 112px;
  transform: rotate(-8deg);
}
.bg-canvas {
  position: absolute;
  inset: 0;
  z-index: 1;
  width: 100%;
  height: 100%;
  opacity: 0.92;
  mix-blend-mode: multiply;
}

.content {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  padding: 86px 24px 190px;
}
.eyebrow {
  font-size: 11px;
  letter-spacing: 0.28em;
  color: rgba(87,83,78,0.62);
  font-weight: 300;
  text-transform: uppercase;
  margin-bottom: 22px;
  animation: fadeUp 1s ease 0.4s both;
}
.tagline {
  font-family: var(--font-serif);
  font-size: clamp(52px, 8vw, 104px);
  font-weight: 500;
  color: var(--text);
  letter-spacing: 0.18em;
  line-height: 1.05;
  text-align: center;
  max-width: 860px;
  text-shadow: 0 1px 0 rgba(255,255,255,0.76);
  animation: fadeUp 1.2s ease 0.6s both;
}
.identity-line {
  margin-top: 24px;
  font-family: var(--font-serif);
  font-size: clamp(18px, 2.2vw, 28px);
  font-weight: 400;
  letter-spacing: 0.18em;
  color: rgba(28,25,23,0.78);
  animation: fadeUp 1.1s ease 0.68s both;
}
.subtitle {
  max-width: 680px;
  margin-top: 18px;
  font-size: clamp(14px, 1.45vw, 17px);
  font-weight: 300;
  line-height: 2;
  letter-spacing: 0.06em;
  color: rgba(87,83,78,0.78);
  text-align: center;
  animation: fadeUp 1.1s ease 0.74s both;
}
.poetic-line {
  margin-top: 11px;
  font-family: var(--font-serif);
  font-size: clamp(13px, 1.15vw, 15px);
  font-weight: 300;
  letter-spacing: 0.12em;
  color: rgba(168,162,158,0.86);
  animation: fadeUp 1.1s ease 0.86s both;
}
.cta-btn {
  margin-top: 34px;
  pointer-events: all;
  padding: 14px 38px;
  background: rgba(255,252,248,0.88);
  border: 1px solid rgba(200,150,15,0.42);
  border-radius: 999px;
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 400;
  letter-spacing: 0.16em;
  color: #b77b08;
  cursor: pointer;
  backdrop-filter: var(--blur-sm); -webkit-backdrop-filter: var(--blur-sm);
  box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.70);
  transition: all var(--transition);
  animation: fadeUp 1.2s ease 1s both;
}
.cta-btn:hover {
  background: rgba(255,252,248,0.98);
  box-shadow: var(--shadow-md), 0 0 24px rgba(200,150,15,0.15);
  transform: translateY(-1px);
  border-color: rgba(200,150,15,0.55);
}
.sample-strip {
  position: fixed;
  left: 50%;
  bottom: 34px;
  z-index: 3;
  width: min(960px, calc(100% - 64px));
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  transform: translateX(-50%);
}
.sample-card {
  min-height: 108px;
  padding: 15px 17px 16px;
  border: 1px solid rgba(180,165,140,0.22);
  border-radius: 18px;
  background: rgba(255,252,248,0.68);
  box-shadow: 0 12px 38px rgba(83,62,36,0.07), inset 0 1px 0 rgba(255,255,255,0.64);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  animation: fadeUp 1s ease both;
}
.sample-card:nth-child(1) { animation-delay: 1.05s; }
.sample-card:nth-child(2) { animation-delay: 1.15s; }
.sample-card:nth-child(3) { animation-delay: 1.25s; }
.sample-type {
  display: block;
  margin-bottom: 9px;
  color: rgba(200,150,15,0.78);
  font-size: 10px;
  font-weight: 400;
  letter-spacing: 0.16em;
}
.sample-card h2 {
  margin-bottom: 8px;
  color: rgba(28,25,23,0.84);
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.06em;
}
.sample-card p {
  color: rgba(87,83,78,0.70);
  font-size: 11px;
  font-weight: 300;
  line-height: 1.75;
  letter-spacing: 0.04em;
}

@media (max-width: 900px) {
  .content {
    padding-bottom: 238px;
  }
  .sample-strip {
    grid-template-columns: 1fr;
    width: min(520px, calc(100% - 40px));
    bottom: 22px;
    gap: 8px;
  }
  .sample-card {
    min-height: auto;
    padding: 11px 14px 12px;
  }
  .sample-card:nth-child(3) {
    display: none;
  }
}

@media (max-width: 640px) {
  .specimen {
    opacity: 0.14;
  }
  .specimen-chili {
    left: 18px;
    top: 18vh;
  }
  .specimen-star {
    right: 16px;
    top: 17vh;
  }
  .specimen-rice {
    display: none;
  }
  .content {
    padding: 76px 20px 250px;
  }
  .eyebrow {
    letter-spacing: 0.20em;
    margin-bottom: 18px;
  }
  .tagline {
    font-size: clamp(54px, 16vw, 72px);
    letter-spacing: 0.12em;
    line-height: 1.28;
  }
  .identity-line {
    margin-top: 18px;
    font-size: 18px;
    letter-spacing: 0.12em;
  }
  .subtitle {
    margin-top: 20px;
    font-size: 13px;
    line-height: 1.82;
  }
  .poetic-line {
    display: none;
  }
  .sample-card h2 {
    font-size: 14px;
  }
  .sample-card p {
    font-size: 10px;
    line-height: 1.65;
  }
}

@media (prefers-reduced-motion: reduce) {
  .bg-canvas {
    display: none;
  }
}
</style>
