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
    <section class="hero-section">
    <div class="content">
      <p class="eyebrow">Flavor Geography Product Studio</p>
      <h1 class="tagline">寻味地理</h1>
      <p class="identity-line">地方食材可视化产品生成器</p>
      <p class="subtitle">
        把产地、加工、流通、历史传播和餐桌应用组织成可展示、可嵌入、可导出的品牌故事地图、溯源公示牌和产业图谱。
      </p>
      <p class="poetic-line">从空间证据到商业叙事，把地方风味做成一份可交付产品。</p>
      <div class="hero-actions">
        <button class="cta-btn primary" @click="router.push('/brand')">进入产品生成器</button>
        <button class="cta-btn secondary" @click="router.push('/spread')">查看传播图谱</button>
      </div>
    </div>
    <div class="product-preview" aria-label="产品输出预览">
      <div class="preview-map">
        <span v-for="dot in previewDots" :key="dot.label" :style="{ left: dot.x, top: dot.y, background: dot.color }" />
      </div>
      <div class="preview-body">
        <span class="preview-label">Traceability Report</span>
        <strong>汉源花椒可信产地报告</strong>
        <p>产区、加工、城市集散和餐桌应用已组织为一份可嵌入报告。</p>
      </div>
      <div class="preview-output">
        <span>H5</span>
        <span>PDF</span>
        <span>PNG</span>
      </div>
    </div>
    </section>
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
    type: '产品模板',
    title: '品牌故事地图、溯源公示牌、产业图谱',
    body: '同一份食材数据可以输出多种展示形态，服务品牌官网、展厅、汇报和电商详情页。',
  },
  {
    type: '空间证据',
    title: '产地、加工、流通、餐桌节点',
    body: 'GIS 不只画地图，而是把地方食材的可信来源和使用场景转化为可阅读证据链。',
  },
  {
    type: '批量生成',
    title: '风格预设与报告输出',
    body: '先支持地理志、公示牌和产业图谱三类视觉模板，后续可扩展到更多地方食材。',
  },
]

const previewDots = [
  { label: 'origin', x: '21%', y: '58%', color: '#5E7B50' },
  { label: 'process', x: '34%', y: '48%', color: '#A96535' },
  { label: 'hub', x: '56%', y: '54%', color: '#3E7891' },
  { label: 'market', x: '76%', y: '38%', color: '#C63D42' },
]
let rafId = null
let cleanupHomeCanvas = () => {}

const pathDefs = [
  { pts: [[0.1,0.5],[0.3,0.3],[0.5,0.4],[0.7,0.35],[0.9,0.5]], col: '#E8A917' },
  { pts: [[0.0,0.3],[0.2,0.45],[0.4,0.5],[0.6,0.4],[0.85,0.55]], col: '#0FB89A' },
  { pts: [[0.15,0.7],[0.35,0.55],[0.55,0.6],[0.75,0.5],[0.95,0.65]], col: '#E5394E' },
  { pts: [[0.05,0.2],[0.25,0.35],[0.5,0.25],[0.75,0.4],[0.9,0.3]], col: '#3D6F87' },
  { pts: [[0.2,0.8],[0.4,0.65],[0.6,0.7],[0.8,0.6],[1.0,0.75]], col: '#7FA961' },
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
    radial-gradient(circle at 18% 18%, rgba(94,123,80,0.18), transparent 32%),
    radial-gradient(circle at 82% 28%, rgba(62,120,145,0.14), transparent 30%),
    linear-gradient(135deg, #fbf7ef 0%, #eef3ed 48%, #f7efe3 100%);
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
.specimen-chili path { stroke: rgba(177, 47, 58, 0.62); }
.specimen-star path { stroke: rgba(156, 112, 22, 0.58); }
.specimen-rice path { stroke: rgba(78, 119, 80, 0.62); }
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

.hero-section {
  position: relative;
  z-index: 2;
  width: min(1180px, calc(100% - 72px));
  min-height: calc(100vh - 230px);
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 56px;
  align-items: center;
  padding: 86px 0 36px;
}

.content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
  padding: 0;
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
  font-size: clamp(54px, 7vw, 92px);
  font-weight: 500;
  color: var(--text);
  letter-spacing: 0.14em;
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
  max-width: 720px;
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
  pointer-events: all;
  padding: 13px 28px;
  background: rgba(255,252,248,0.88);
  border: 1px solid rgba(232,169,23,0.42);
  border-radius: 999px;
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 400;
  letter-spacing: 0.16em;
  color: #724b2e;
  cursor: pointer;
  backdrop-filter: var(--blur-sm); -webkit-backdrop-filter: var(--blur-sm);
  box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.70);
  transition: all var(--transition);
  animation: fadeUp 1.2s ease 1s both;
}
.cta-btn:hover {
  background: rgba(255,252,248,0.98);
  box-shadow: var(--shadow-md), 0 0 24px rgba(232,169,23,0.15);
  transform: translateY(-1px);
  border-color: rgba(232,169,23,0.55);
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 34px;
  pointer-events: all;
}

.cta-btn.primary {
  background: linear-gradient(135deg, var(--earth), var(--leaf));
  color: #fffaf2;
  border-color: transparent;
  box-shadow: 0 14px 34px rgba(67, 92, 60, 0.18);
}

.cta-btn.secondary {
  background: rgba(255,252,248,0.68);
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
  border-radius: 8px;
  background: rgba(255,252,248,0.68);
  box-shadow: 0 12px 38px rgba(83,62,36,0.07), inset 0 1px 0 rgba(255,255,255,0.64);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  animation: fadeUp 1s ease both;
}

.product-preview {
  position: relative;
  z-index: 2;
  width: 100%;
  min-width: 0;
  border: 1px solid rgba(116, 92, 62, 0.16);
  border-radius: 12px;
  background: rgba(255, 252, 247, 0.72);
  box-shadow: 0 24px 70px rgba(58, 42, 24, 0.12), inset 0 1px 0 rgba(255,255,255,0.72);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  pointer-events: none;
  animation: fadeUp 1.2s ease 0.92s both;
}

.preview-map {
  position: relative;
  height: 150px;
  overflow: hidden;
  border-radius: 12px 12px 0 0;
  background:
    linear-gradient(120deg, rgba(94,123,80,0.14), transparent 38%),
    linear-gradient(35deg, transparent 48%, rgba(62,120,145,0.18) 49%, transparent 52%),
    linear-gradient(160deg, transparent 44%, rgba(169,101,53,0.18) 45%, transparent 48%),
    #e6eee5;
}

.preview-map::before {
  content: '';
  position: absolute;
  inset: 24px 28px;
  border-top: 2px solid rgba(169,101,53,0.46);
  border-right: 2px solid rgba(62,120,145,0.44);
  border-radius: 60% 42% 54% 46%;
  transform: rotate(-9deg);
}

.preview-map span {
  position: absolute;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  box-shadow: 0 0 0 4px rgba(255,252,248,0.82), 0 10px 22px rgba(58,42,24,0.18);
}

.preview-body {
  padding: 16px 18px 12px;
}

.preview-label {
  color: rgba(92,75,57,0.56);
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.preview-body strong {
  display: block;
  margin-top: 7px;
  color: var(--text);
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 500;
}

.preview-body p {
  margin-top: 8px;
  color: rgba(87,83,78,0.72);
  font-size: 12px;
  line-height: 1.7;
}

.preview-output {
  display: flex;
  gap: 6px;
  padding: 0 18px 16px;
}

.preview-output span {
  padding: 4px 9px;
  border-radius: 999px;
  background: rgba(94,123,80,0.1);
  color: #5e7b50;
  font-size: 10px;
  font-weight: 700;
}
.sample-card:nth-child(1) { animation-delay: 1.05s; }
.sample-card:nth-child(2) { animation-delay: 1.15s; }
.sample-card:nth-child(3) { animation-delay: 1.25s; }
.sample-card:nth-child(1) { border-top-color: rgba(229,57,78,0.34); }
.sample-card:nth-child(2) { border-top-color: rgba(15,184,154,0.34); }
.sample-card:nth-child(3) { border-top-color: rgba(127,169,97,0.34); }
.sample-type {
  display: block;
  margin-bottom: 9px;
  color: rgba(148,106,18,0.82);
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
  .hero-section {
    min-height: calc(100vh - 250px);
    width: min(560px, calc(100% - 40px));
    grid-template-columns: 1fr;
    padding-top: 76px;
  }
  .content {
    padding-bottom: 0;
  }
  .sample-strip {
    grid-template-columns: 1fr;
    width: min(520px, calc(100% - 40px));
    bottom: 22px;
    gap: 8px;
  }
  .product-preview {
    display: none;
  }
  .sample-card {
    min-height: auto;
    padding: 11px 14px 12px;
  }
  .sample-card:nth-child(3) {
    display: none;
  }
}

@media (max-width: 1200px) {
  .hero-section {
    grid-template-columns: 1fr;
    min-height: calc(100vh - 220px);
  }
  .product-preview {
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
    padding: 0;
  }
  .hero-actions {
    flex-direction: column;
    width: min(280px, 100%);
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
