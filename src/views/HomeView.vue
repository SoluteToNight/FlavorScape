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

    <section class="hero-section" aria-labelledby="home-title">
      <div class="hero-copy">
        <p class="eyebrow">FlavorScape Atlas / Origin & Taste</p>
        <h1 id="home-title" class="tagline" aria-label="寻味地理">
          <span class="tagline-main">寻味</span>
          <span class="tagline-sub">地理</span>
        </h1>
        <p class="identity-line">把地方风味写成一册可漫游的地理志</p>
        <p class="subtitle">
          从 <mark>产地证据</mark> 到 <mark>传播路线</mark>，从食材档案到品牌公示，
          在流动的地图、路径与风物标本之间，重新组织一座地方的味觉记忆。
        </p>

        <div class="hero-actions" aria-label="首页主要入口">
          <button class="entry-btn" @click="router.push('/brand')">
            <span>进入品牌生成器</span>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 12h13M13 6l6 6-6 6" />
            </svg>
          </button>
          <button class="ghost-btn" @click="router.push('/spread')">
            查看传播图谱
          </button>
        </div>

        <div class="hero-meta" aria-label="产品能力摘要">
          <span><b>03</b> 产品入口</span>
          <span><b>GIS</b> 空间证据</span>
          <span><b>PNG</b> 品牌导出</span>
        </div>
      </div>

      <div class="atlas-illustration" aria-hidden="true">
        <div class="board-watermark">FLAVORSCAPE</div>
        <div class="taste-orbit">
          <span class="orbit-ring orbit-one" />
          <span class="orbit-ring orbit-two" />
          <span class="orbit-ring orbit-three" />
          <svg viewBox="0 0 520 520">
            <path class="terrain terrain-one" d="M72 334 C132 218 196 296 258 168 C318 46 408 104 464 56" />
            <path class="terrain terrain-two" d="M46 232 C126 150 184 186 254 246 C344 324 412 256 486 372" />
            <path class="route route-red" d="M74 352 C152 246 205 276 270 184 C333 95 395 112 462 70" />
            <path class="route route-green" d="M66 188 C142 228 190 164 260 230 C326 294 384 268 470 356" />
            <circle class="node node-a" cx="74" cy="352" r="8" />
            <circle class="node node-b" cx="270" cy="184" r="8" />
            <circle class="node node-c" cx="462" cy="70" r="8" />
            <circle class="node node-d" cx="470" cy="356" r="8" />
          </svg>
          <span class="seal seal-origin">ORIGIN</span>
          <span class="seal seal-route">ROUTE</span>
          <span class="seal seal-taste">TASTE</span>
        </div>
        <p class="map-caption">产地 · 路径 · 风物证据</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const canvasEl = ref(null)

let rafId = null
let cleanupHomeCanvas = () => {}

const pathDefs = [
  { pts: [[0.08,0.46],[0.26,0.27],[0.48,0.38],[0.70,0.32],[0.92,0.48]], col: '#E8A917' },
  { pts: [[0.02,0.31],[0.22,0.47],[0.42,0.50],[0.62,0.40],[0.88,0.56]], col: '#0FB89A' },
  { pts: [[0.12,0.72],[0.34,0.56],[0.55,0.62],[0.76,0.50],[0.96,0.66]], col: '#E5394E' },
  { pts: [[0.04,0.20],[0.25,0.36],[0.52,0.24],[0.76,0.40],[0.92,0.30]], col: '#3D6F87' },
  { pts: [[0.18,0.83],[0.40,0.66],[0.60,0.71],[0.81,0.60],[1.00,0.77]], col: '#7FA961' },
]

function catmull(pts, t, W, H) {
  const n = pts.length - 1
  const seg = Math.min(Math.floor(t * n), n - 1)
  const lt = t * n - seg
  const p0 = pts[Math.max(0, seg - 1)]
  const p1 = pts[seg]
  const p2 = pts[Math.min(n, seg + 1)]
  const p3 = pts[Math.min(n, seg + 2)]
  const t2 = lt * lt
  const t3 = t2 * lt

  return [
    0.5 * ((2*p1[0]) + (-p0[0]+p2[0])*lt + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3) * W,
    0.5 * ((2*p1[1]) + (-p0[1]+p2[1])*lt + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3) * H,
  ]
}

function extractCoastlineLines(collection) {
  const lines = []

  collection.features?.forEach(feature => {
    const geometry = feature.geometry
    if (!geometry) return

    if (geometry.type === 'LineString') {
      lines.push(geometry.coordinates)
    }

    if (geometry.type === 'MultiLineString') {
      geometry.coordinates.forEach(line => lines.push(line))
    }
  })

  return lines.filter(line => line.length > 1)
}

function projectCoastlinePoint(lon, lat, W, H) {
  const mapW = Math.min(W * 0.92, H * 1.72)
  const mapH = mapW / 2
  const left = (W - mapW) / 2
  const top = H * 0.50 - mapH * 0.52

  return [
    left + ((lon + 180) / 360) * mapW,
    top + ((90 - lat) / 180) * mapH,
  ]
}

function drawCoastlineMap(ctx, coastlineLines, W, H) {
  if (!coastlineLines.length) return

  const strokeLines = (strokeStyle, lineWidth) => {
    ctx.strokeStyle = strokeStyle
    ctx.lineWidth = lineWidth
    coastlineLines.forEach(line => {
      let started = false
      ctx.beginPath()
      line.forEach(point => {
        const [lon, lat] = point
        if (!Number.isFinite(lon) || !Number.isFinite(lat)) return
        const [x, y] = projectCoastlinePoint(lon, lat, W, H)
        if (!started) {
          ctx.moveTo(x, y)
          started = true
        } else {
          ctx.lineTo(x, y)
        }
      })
      if (started) ctx.stroke()
    })
  }

  ctx.save()
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  strokeLines('rgba(255,252,248,0.54)', Math.max(2.4, W / 520))
  strokeLines('rgba(62,78,65,0.26)', Math.max(0.75, W / 1680))
  ctx.restore()
}

onMounted(() => {
  const canvas = canvasEl.value
  const ctx = canvas.getContext('2d')
  let W, H, mouseX, mouseY
  let coastlineLines = []
  const coastlineAbort = new AbortController()

  const resize = () => {
    W = canvas.width = window.innerWidth
    H = canvas.height = window.innerHeight
    mouseX = W / 2
    mouseY = H / 2
  }
  resize()

  window.addEventListener('resize', resize)
  const onMouseMove = e => {
    mouseX = e.clientX
    mouseY = e.clientY
  }
  window.addEventListener('mousemove', onMouseMove)

  fetch('/geo/coastline-110m.geojson', { signal: coastlineAbort.signal })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return res.json()
    })
    .then(data => {
      coastlineLines = extractCoastlineLines(data)
    })
    .catch(err => {
      if (err.name !== 'AbortError') console.warn('[Home coastline]', err.message)
    })

  const particles = pathDefs.flatMap((pd, pi) =>
    Array.from({ length: 5 }, () => ({
      pi,
      t: Math.random(),
      speed: 0.00055 + Math.random() * 0.00038,
      col: pd.col,
      size: 1.5 + Math.random() * 1.7,
      trail: [],
      trailLen: 20 + Math.floor(Math.random() * 14),
    }))
  )

  function draw() {
    ctx.clearRect(0, 0, W, H)
    drawCoastlineMap(ctx, coastlineLines, W, H)

    ctx.save()
    ctx.strokeStyle = 'rgba(180,160,130,0.08)'
    ctx.lineWidth = 0.5
    ctx.setLineDash([4, 12])
    ;[[0.08,0.38,0.92,0.42],[0.00,0.58,1.00,0.62],[0.15,0.22,0.85,0.28]].forEach(([x1,y1,x2,y2]) => {
      ctx.beginPath()
      ctx.moveTo(x1*W, y1*H)
      ctx.lineTo(x2*W, y2*H)
      ctx.stroke()
    })
    ctx.setLineDash([])
    ctx.restore()

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
      ctx.beginPath()
      ctx.arc(fx, fy, p.size * 1.2, 0, Math.PI * 2)
      ctx.fillStyle = p.col
      ctx.globalAlpha = 0.9
      ctx.fill()
      ctx.globalAlpha = 1
    })

    rafId = requestAnimationFrame(draw)
  }

  draw()

  cleanupHomeCanvas = () => {
    coastlineAbort.abort()
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
    radial-gradient(circle at 50% 44%, rgba(255, 252, 248, 0.74), transparent 30%),
    radial-gradient(circle at 18% 18%, rgba(94,123,80,0.20), transparent 34%),
    radial-gradient(circle at 82% 24%, rgba(62,120,145,0.15), transparent 32%),
    radial-gradient(circle at 50% 100%, rgba(169,101,53,0.13), transparent 38%),
    linear-gradient(135deg, #fbf7ef 0%, #eef3ed 48%, #f7efe3 100%);
}

.home-page::before {
  content: '';
  position: absolute;
  inset: -18%;
  background:
    linear-gradient(rgba(92,75,57,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(92,75,57,0.028) 1px, transparent 1px);
  background-size: 92px 92px;
  mask-image: radial-gradient(circle at 50% 48%, rgba(0,0,0,0.48), transparent 72%);
  transform: rotate(-6deg);
}

.home-page::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  width: min(76vw, 820px);
  aspect-ratio: 1;
  border: 1px solid rgba(139, 94, 52, 0.12);
  border-radius: 50%;
  box-shadow:
    0 0 0 22px rgba(255, 252, 248, 0.10),
    0 0 0 86px rgba(94, 123, 80, 0.035),
    inset 0 0 110px rgba(255, 252, 248, 0.42);
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.atlas-layer {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.specimen {
  position: absolute;
  opacity: 0.18;
  filter: drop-shadow(0 12px 24px rgba(83,62,36,0.05));
  animation: fadeUp 1.4s ease 0.35s both;
}

.specimen path {
  fill: none;
  stroke: rgba(92,75,57,0.72);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.specimen-chili path { stroke: rgba(177, 47, 58, 0.62); }
.specimen-star path { stroke: rgba(156, 112, 22, 0.58); }
.specimen-rice path { stroke: rgba(78, 119, 80, 0.62); }

.specimen-chili {
  left: clamp(24px, 8vw, 132px);
  top: 22vh;
  width: clamp(72px, 7vw, 104px);
  transform: rotate(-10deg);
}

.specimen-star {
  right: clamp(28px, 9vw, 150px);
  top: 18vh;
  width: clamp(92px, 8vw, 132px);
  transform: rotate(14deg);
}

.specimen-rice {
  right: clamp(34px, 10vw, 170px);
  bottom: 18vh;
  width: clamp(112px, 9vw, 158px);
  transform: rotate(-8deg);
}

.bg-canvas {
  position: absolute;
  inset: 0;
  z-index: 1;
  width: 100%;
  height: 100%;
  opacity: 0.82;
  mix-blend-mode: multiply;
}

.hero-section {
  position: relative;
  z-index: 3;
  min-height: 100vh;
  width: min(1320px, calc(100% - 72px));
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(420px, 0.95fr);
  align-items: center;
  gap: clamp(40px, 6vw, 92px);
  justify-content: center;
  padding: calc(var(--navbar-h) + 24px) 0 44px;
}

.hero-copy {
  position: relative;
  max-width: 720px;
  padding: 26px 0 22px;
}

.hero-copy::before {
  content: '';
  position: absolute;
  left: -28px;
  top: 10px;
  width: 3px;
  height: 72%;
  border-radius: 999px;
  background: linear-gradient(180deg, transparent, var(--carmine), var(--saffron), transparent);
  opacity: 0.68;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-bottom: clamp(16px, 2vw, 28px);
  color: rgba(87,83,78,0.72);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  animation: fadeUp 1s ease 0.34s both;
}

.eyebrow::before {
  content: '';
  width: 42px;
  height: 1px;
  background: linear-gradient(90deg, var(--carmine), rgba(201,166,70,0.36));
}

.tagline {
  margin: 0;
  position: relative;
  display: grid;
  width: fit-content;
  font-family: var(--font-serif);
  line-height: 0.86;
  text-shadow: 0 30px 86px rgba(83,62,36,0.18);
  animation: fadeUp 1.2s ease 0.48s both;
}

.tagline::after {
  content: 'ATLAS';
  position: absolute;
  right: -76px;
  bottom: 6px;
  color: rgba(166, 105, 53, 0.18);
  font-family: var(--font-sans);
  font-size: clamp(46px, 5.6vw, 82px);
  font-weight: 500;
  letter-spacing: 0.16em;
  transform: rotate(-90deg);
  transform-origin: right bottom;
}

.tagline-main,
.tagline-sub {
  display: block;
  color: var(--text);
}

.tagline-main {
  font-size: clamp(88px, 10vw, 154px);
  font-weight: 600;
  letter-spacing: clamp(0.08em, 0.92vw, 0.15em);
}

.tagline-sub {
  margin-left: clamp(70px, 8vw, 124px);
  margin-top: clamp(2px, 0.6vw, 10px);
  color: transparent;
  font-size: clamp(74px, 8.2vw, 128px);
  font-weight: 500;
  letter-spacing: clamp(0.14em, 1.4vw, 0.24em);
  background: linear-gradient(118deg, var(--earth) 0%, var(--carmine) 54%, var(--saffron) 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.identity-line {
  margin-top: clamp(28px, 3vw, 38px);
  color: rgba(28,25,23,0.84);
  font-family: var(--font-serif);
  font-size: clamp(22px, 2.25vw, 32px);
  font-weight: 500;
  letter-spacing: 0.10em;
  animation: fadeUp 1.1s ease 0.62s both;
}

.subtitle {
  max-width: 640px;
  margin: 20px 0 0;
  color: rgba(72,64,55,0.82);
  font-size: clamp(14px, 1.45vw, 18px);
  font-weight: 400;
  line-height: 2.05;
  letter-spacing: 0.055em;
  animation: fadeUp 1.1s ease 0.74s both;
}

.subtitle mark {
  padding: 0 0.18em;
  background: linear-gradient(180deg, transparent 54%, rgba(201,166,70,0.32) 54%);
  color: #743b2b;
  font-family: var(--font-serif);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
  margin-top: clamp(32px, 4vw, 50px);
  animation: fadeUp 1.1s ease 0.92s both;
}

.entry-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-width: 210px;
  min-height: 52px;
  padding: 15px 30px 15px 34px;
  border: 1px solid rgba(139, 94, 52, 0.14);
  border-radius: 999px;
  background: linear-gradient(135deg, #8f4e37 0%, var(--earth) 45%, var(--leaf) 100%);
  box-shadow:
    0 18px 44px rgba(67, 92, 60, 0.20),
    inset 0 1px 0 rgba(255,255,255,0.22);
  color: #fffaf2;
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.18em;
  transition: transform var(--transition), box-shadow var(--transition), filter var(--transition);
}

.ghost-btn {
  min-height: 52px;
  padding: 14px 24px;
  border: 1px solid rgba(118, 96, 68, 0.18);
  border-radius: 999px;
  background: rgba(255,252,248,0.62);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.62), 0 12px 34px rgba(51,37,22,0.07);
  color: var(--text-mid);
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.13em;
  transition: transform var(--transition), background var(--transition), color var(--transition), border-color var(--transition);
}

.ghost-btn:hover {
  transform: translateY(-2px);
  border-color: rgba(198,61,66,0.22);
  background: rgba(255,252,248,0.86);
  color: var(--text);
}

.entry-btn:hover {
  transform: translateY(-2px);
  filter: saturate(1.05);
  box-shadow:
    0 24px 58px rgba(67, 92, 60, 0.26),
    0 0 32px rgba(201,166,70,0.18),
    inset 0 1px 0 rgba(255,255,255,0.26);
}

.entry-btn:focus-visible {
  outline: 3px solid rgba(62,120,145,0.34);
  outline-offset: 4px;
}

.entry-btn svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: transform var(--transition);
}

.entry-btn:hover svg {
  transform: translateX(3px);
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 24px;
  animation: fadeUp 1s ease 1.02s both;
}

.hero-meta span {
  display: inline-flex;
  align-items: baseline;
  gap: 7px;
  padding: 8px 12px;
  border: 1px solid rgba(118, 96, 68, 0.14);
  border-radius: 999px;
  background: rgba(255,252,248,0.46);
  color: rgba(92,81,71,0.78);
  font-size: 12px;
  letter-spacing: 0.04em;
}

.hero-meta b {
  color: var(--carmine);
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 600;
}

.atlas-illustration {
  position: relative;
  min-height: 620px;
  animation: fadeUp 1.2s ease 0.58s both;
}

.board-watermark {
  position: absolute;
  right: -24px;
  top: 28px;
  color: rgba(32,27,22,0.06);
  font-size: clamp(58px, 6.8vw, 108px);
  font-weight: 500;
  letter-spacing: 0.12em;
  transform: rotate(8deg);
  pointer-events: none;
}

.taste-orbit {
  position: absolute;
  left: 50%;
  top: 50%;
  width: min(44vw, 610px);
  aspect-ratio: 1;
  transform: translate(-50%, -50%) rotate(1deg);
}

.taste-orbit::before {
  content: '';
  position: absolute;
  inset: 8%;
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 50%, rgba(255,252,248,0.44), transparent 35%),
    conic-gradient(from 120deg, rgba(198,61,66,0.18), rgba(201,166,70,0.20), rgba(94,123,80,0.16), rgba(62,120,145,0.15), rgba(198,61,66,0.18));
  filter: blur(0.2px);
  opacity: 0.9;
}

.orbit-ring {
  position: absolute;
  border: 1px solid rgba(139,94,52,0.16);
  border-radius: 50%;
}

.orbit-one {
  inset: 5%;
  box-shadow: 0 0 0 26px rgba(255,252,248,0.09);
}

.orbit-two {
  inset: 19%;
  border-style: dashed;
  transform: rotate(18deg);
}

.orbit-three {
  inset: 34%;
  border-color: rgba(198,61,66,0.18);
}

.taste-orbit svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 22px 32px rgba(83,62,36,0.12));
}

.terrain,
.route {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.terrain {
  stroke: rgba(92,75,57,0.20);
  stroke-width: 2;
  stroke-dasharray: 7 12;
}

.route {
  stroke-width: 5;
}

.route-red { stroke: rgba(198,61,66,0.82); }
.route-green { stroke: rgba(94,123,80,0.76); }
.node { fill: #fffaf2; stroke-width: 4; }
.node-a, .node-c { stroke: var(--carmine); }
.node-b, .node-d { stroke: var(--leaf); }

.seal {
  position: absolute;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 84px;
  aspect-ratio: 1;
  border: 1px solid currentColor;
  border-radius: 50%;
  background: rgba(255,252,248,0.28);
  color: rgba(116,59,43,0.68);
  font-family: var(--font-serif);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.12em;
  transform: rotate(-12deg);
}

.seal-origin { left: 5%; top: 18%; }
.seal-route { right: 4%; top: 38%; color: rgba(94,123,80,0.68); transform: rotate(10deg); }
.seal-taste { left: 35%; bottom: 2%; color: rgba(166,105,53,0.7); transform: rotate(-4deg); }

.map-caption {
  position: absolute;
  right: 9%;
  bottom: 9%;
  color: rgba(92,81,71,0.72);
  font-family: var(--font-serif);
  font-size: clamp(16px, 1.5vw, 22px);
  letter-spacing: 0.18em;
  writing-mode: vertical-rl;
}

.ghost-btn:focus-visible {
  outline: 3px solid rgba(62,120,145,0.34);
  outline-offset: 4px;
}

@media (max-width: 900px) {
  .hero-section {
    width: min(760px, calc(100% - 40px));
    grid-template-columns: 1fr;
    gap: 28px;
    padding: calc(var(--navbar-h) + 18px) 0 28px;
  }

  .hero-copy {
    max-width: 100%;
  }

  .hero-copy::before,
  .tagline::after,
  .board-watermark {
    display: none;
  }

  .tagline-main {
    font-size: clamp(70px, 12vw, 116px);
  }

  .tagline-sub {
    margin-left: clamp(42px, 5vw, 72px);
    font-size: clamp(58px, 10vw, 92px);
  }

  .atlas-illustration {
    min-height: 420px;
  }

  .taste-orbit {
    width: min(72vw, 460px);
  }

  .subtitle {
    max-width: 580px;
  }
}

@media (max-width: 640px) {
  .home-page::after {
    width: 96vw;
    box-shadow:
      0 0 0 14px rgba(255, 252, 248, 0.10),
      0 0 0 52px rgba(94, 123, 80, 0.035),
      inset 0 0 80px rgba(255, 252, 248, 0.42);
  }

  .specimen {
    opacity: 0.12;
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

  .eyebrow {
    letter-spacing: 0.14em;
  }

  .tagline-main {
    font-size: clamp(58px, 18vw, 88px);
  }

  .tagline-sub {
    margin-left: clamp(28px, 8vw, 42px);
    font-size: clamp(50px, 16vw, 72px);
    letter-spacing: 0.14em;
  }

  .identity-line {
    font-size: 18px;
    letter-spacing: 0.08em;
  }

  .subtitle {
    font-size: 13px;
    line-height: 1.86;
    letter-spacing: 0.04em;
  }

  .hero-actions {
    align-items: stretch;
  }

  .entry-btn,
  .ghost-btn {
    width: min(282px, 100%);
  }

  .atlas-illustration {
    min-height: 320px;
  }

  .taste-orbit {
    width: min(86vw, 340px);
  }

  .seal {
    width: 64px;
    font-size: 10px;
  }

  .map-caption {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .bg-canvas {
    display: none;
  }
}
</style>
