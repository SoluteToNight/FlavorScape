<template>
  <div class="home-page">
    <canvas ref="canvasEl" class="bg-canvas" />
    <div class="content">
      <p class="eyebrow">寻味地理 · Flavor Geography</p>
      <h1 class="tagline">
        探寻同一种食物，<br>在不同水土中写下的味道基因。
      </h1>
      <button class="cta-btn" @click="router.push('/map')">开&ensp;启&ensp;地&ensp;图</button>
    </div>
    <div class="ticker">{{ tickerText }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const canvasEl = ref(null)

const tickerItems = [
  '成都·麻度 0.90 → 顺德·麻度 0.05',
  '云南·酸度 0.60 → 新疆·甜度 0.60',
  '潮汕·鲜度 0.90 → 北京·咸度 0.80',
  '辣椒入华 1570 年 → 川菜定型 1800 年',
  '大运河漕运年输三百万石',
]
const tickerText = ref(tickerItems[0])
let tickerIdx = 0
let tickerTimer = null
let rafId = null

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
  window.addEventListener('mousemove', e => { mouseX = e.clientX; mouseY = e.clientY })

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
    // subtle terrain lines
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
      if (p.t < prevT) p.trail = []   // wrapped around — clear stale tail
      const [x, y] = catmull(pathDefs[p.pi].pts, p.t, W, H)
      const fx = x + (mouseX - W/2) * 0.008 * (1 - p.t)
      const fy = y + (mouseY - H/2) * 0.008 * (1 - p.t)
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

  tickerTimer = setInterval(() => {
    tickerIdx = (tickerIdx + 1) % tickerItems.length
    tickerText.value = tickerItems[tickerIdx]
  }, 3200)
})

onUnmounted(() => {
  cancelAnimationFrame(rafId)
  clearInterval(tickerTimer)
})
</script>

<style scoped>
.home-page {
  position: fixed;
  inset: 0;
  background: var(--bg);
}
.bg-canvas { position: absolute; inset: 0; width: 100%; height: 100%; }

.content {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 0; pointer-events: none;
}
.eyebrow {
  font-size: 11px; letter-spacing: 0.25em;
  color: var(--text-muted); font-weight: 300;
  text-transform: uppercase; margin-bottom: 28px;
  animation: fadeUp 1s ease 0.4s both;
}
.tagline {
  font-family: var(--font-serif);
  font-size: clamp(18px, 2.2vw, 26px);
  font-weight: 400; color: var(--text);
  letter-spacing: 0.08em; line-height: 2;
  text-align: center; max-width: 580px;
  animation: fadeUp 1.2s ease 0.6s both;
}
.cta-btn {
  margin-top: 40px;
  pointer-events: all;
  padding: 13px 36px;
  background: var(--glass);
  border: 1px solid rgba(200,150,15,0.35);
  border-radius: 28px;
  font-family: var(--font-sans);
  font-size: 13px; font-weight: 400;
  letter-spacing: 0.14em; color: var(--amber);
  cursor: pointer;
  backdrop-filter: var(--blur-sm); -webkit-backdrop-filter: var(--blur-sm);
  box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(200,150,15,0.12);
  transition: all var(--transition);
  animation: fadeUp 1.2s ease 1s both;
}
.cta-btn:hover {
  background: rgba(255,252,248,0.98);
  box-shadow: var(--shadow-md), 0 0 24px rgba(200,150,15,0.15);
  transform: translateY(-1px);
  border-color: rgba(200,150,15,0.55);
}
.ticker {
  position: fixed; bottom: 40px; left: 50%; transform: translateX(-50%);
  font-size: 11px; font-weight: 300; letter-spacing: 0.15em;
  color: var(--text-muted); white-space: nowrap; z-index: 10;
  pointer-events: none;
  transition: opacity 0.4s ease;
}
</style>
