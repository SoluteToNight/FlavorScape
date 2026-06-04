<template>
  <div class="narrative-page">
    <div class="left-nav">
      <div class="spine" />
      <div
        v-for="(ch, i) in chapters"
        :key="ch.id"
        class="chapter-dot"
        :class="{ active: i === appStore.currentChapter }"
        @click="appStore.setChapter(i)"
      >
        <span class="dot-circle" />
        <span class="dot-label">{{ ch.title }}</span>
      </div>
    </div>

    <div class="right-content">
      <div class="mini-map-wrap">
        <canvas ref="miniCanvas" class="mini-canvas" />
      </div>

      <div class="chapter-body" v-if="current">
        <Transition name="chapter" mode="out-in">
          <div :key="appStore.currentChapter">
            <div class="ch-title">{{ current.title }}</div>
            <div class="ch-date">{{ current.date }}</div>
            <p class="ch-body">{{ current.body }}</p>
            <blockquote class="ch-cite">{{ current.cite }}</blockquote>
            <div class="ch-source">—— {{ current.source }}</div>
            <div class="ch-footer">
              <div class="progress-dots">
                <span
                  v-for="(_, i) in chapters"
                  :key="i"
                  class="pdot"
                  :class="{ active: i === appStore.currentChapter }"
                />
              </div>
              <button
                v-if="appStore.currentChapter === chapters.length - 1"
                class="explore-btn"
                @click="router.push('/map')"
              >打开全地图自由探索</button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app.js'

const router = useRouter()
const appStore = useAppStore()
const chapters = ref([])
const routes = ref([])
const miniCanvas = ref(null)
let rafId = null

onMounted(async () => {
  const [chRes, rRes] = await Promise.all([
    fetch('/api/chapters'), fetch('/api/routes'),
  ])
  const chapterData = await chRes.json().catch(() => [])
  const routeData = await rRes.json().catch(() => [])
  chapters.value = Array.isArray(chapterData) ? chapterData : []
  routes.value = Array.isArray(routeData) ? routeData : []
  drawMiniMap()
})

onUnmounted(() => cancelAnimationFrame(rafId))

const current = computed(() => chapters.value[appStore.currentChapter])

watch(() => appStore.currentChapter, () => {
  cancelAnimationFrame(rafId)
  drawMiniMap()
})

function drawMiniMap() {
  const canvas = miniCanvas.value
  if (!canvas || !current.value) return
  const ctx = canvas.getContext('2d')
  const W = canvas.width = canvas.offsetWidth || 800
  const H = canvas.height = canvas.offsetHeight || 260

  const routeName = current.value.routeName
  const route = (Array.isArray(routes.value) ? routes.value : []).find(r => r?.name === routeName)
  if (!route?.path?.length) return

  // Compute bounding box for route
  const lngs = route.path.map(p => p[0])
  const lats = route.path.map(p => p[1])
  const minLng = Math.min(...lngs) - 15, maxLng = Math.max(...lngs) + 15
  const minLat = Math.min(...lats) - 10, maxLat = Math.max(...lats) + 10
  const proj = ([lng, lat]) => [
    ((lng - minLng) / (maxLng - minLng)) * (W * 0.85) + W * 0.075,
    (1 - (lat - minLat) / (maxLat - minLat)) * (H * 0.75) + H * 0.125,
  ]
  const pts = route.path.map(proj)
  if (pts.length < 2) return

  let t = 0
  function frame() {
    if (pts.length < 2) return
    try {
    ctx.clearRect(0, 0, W, H)
    ctx.fillStyle = '#EDE5D8'; ctx.fillRect(0, 0, W, H)
    // Base route line
    ctx.beginPath(); pts.forEach(([x,y],i) => i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y))
    ctx.strokeStyle = route.color + '44'
    ctx.lineWidth = 1.2
    if (route.type === 'sea') ctx.setLineDash([5, 10]); else ctx.setLineDash([])
    ctx.stroke(); ctx.setLineDash([])
    // Endpoints
    [pts[0], pts[pts.length-1]].forEach(([x,y]) => {
      ctx.beginPath(); ctx.arc(x,y,4,0,Math.PI*2)
      ctx.fillStyle = route.color; ctx.fill()
      ctx.strokeStyle = '#F8F4EF'; ctx.lineWidth = 1.5; ctx.stroke()
    })
    // Particle
    t = (t + 0.012) % 1
    const seg = Math.min(Math.floor(t * (pts.length-1)), pts.length-2)
    if (!pts[seg] || !pts[seg + 1]) return
    const lt = t * (pts.length-1) - seg
    const [px, py] = [pts[seg][0] + (pts[seg+1][0]-pts[seg][0])*lt, pts[seg][1] + (pts[seg+1][1]-pts[seg][1])*lt]
    const g = ctx.createRadialGradient(px,py,0,px,py,10)
    g.addColorStop(0, route.color + 'FF'); g.addColorStop(1, route.color + '00')
    ctx.beginPath(); ctx.arc(px,py,10,0,Math.PI*2); ctx.fillStyle = g; ctx.fill()
    ctx.beginPath(); ctx.arc(px,py,3,0,Math.PI*2); ctx.fillStyle = route.color; ctx.fill()
    rafId = requestAnimationFrame(frame)
    } catch {
      cancelAnimationFrame(rafId)
      rafId = null
    }
  }
  frame()
}
</script>

<style scoped>
.narrative-page {
  position: relative;
  min-height: calc(100vh - var(--navbar-h));
  margin-top: var(--navbar-h);
  background: var(--bg);
  display: flex;
  overflow: auto;
  padding-inline: var(--page-gutter);
}

.left-nav {
  width: 180px; padding: 40px 24px 40px 12px;
  display: flex; flex-direction: column;
  position: relative;
}
.spine {
  position: absolute; left: 52px; top: 60px; bottom: 60px;
  width: 1px;
  background: linear-gradient(to bottom, transparent, var(--glass-border) 10%, var(--glass-border) 90%, transparent);
}
.chapter-dot {
  position: relative; z-index: 2;
  display: flex; align-items: center; gap: 16px;
  margin-bottom: 48px; cursor: pointer;
}
.dot-circle {
  width: 8px; height: 8px; border-radius: 50%;
  background: transparent; border: 1.5px solid var(--text-muted);
  transition: all var(--transition); flex-shrink: 0;
}
.chapter-dot.active .dot-circle {
  background: var(--amber); border-color: var(--amber);
  box-shadow: 0 0 0 4px var(--amber-soft);
}
.dot-label { font-size: 11px; color: var(--text-muted); letter-spacing: 0.06em; transition: color var(--transition); white-space: nowrap; }
.chapter-dot.active .dot-label { color: var(--text); }
.chapter-dot:hover .dot-label { color: var(--text-mid); }

.right-content { flex: 1; min-width: 0; display: flex; flex-direction: column; padding: 40px 0 40px 12px; overflow: visible; }

@media (max-width: 860px) {
  .narrative-page { flex-direction: column; }
  .left-nav {
    width: 100%;
    padding: 24px 28px 0;
    flex-direction: row;
    gap: 22px;
    overflow-x: auto;
  }
  .spine { display: none; }
  .chapter-dot { margin-bottom: 20px; flex-shrink: 0; }
  .right-content { padding: 24px 28px 36px; }
}
.mini-map-wrap { flex: 0 0 260px; border-radius: var(--radius); overflow: hidden; background: #EDE5D8; margin-bottom: 28px; box-shadow: var(--shadow-sm); }
.mini-canvas { width: 100%; height: 260px; display: block; }

.chapter-body { flex: 1; overflow-y: auto; max-width: 680px; }
.ch-title { font-family: var(--font-serif); font-size: 22px; font-weight: 500; letter-spacing: 0.05em; margin-bottom: 4px; }
.ch-date { font-size: 11px; color: var(--amber); letter-spacing: 0.14em; margin-bottom: 20px; }
.ch-body { font-size: 14px; line-height: 2.1; color: var(--text-mid); font-weight: 300; letter-spacing: 0.04em; }
.ch-cite {
  margin-top: 20px; padding: 14px 18px;
  background: rgba(200,150,15,0.06);
  border-left: 2px solid rgba(200,150,15,0.4);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 12px; color: var(--text-mid); font-style: italic; line-height: 1.8;
}
.ch-source { margin-top: 10px; font-size: 10px; color: var(--text-muted); letter-spacing: 0.08em; }
.ch-footer { display: flex; align-items: center; gap: 20px; margin-top: 24px; }
.progress-dots { display: flex; gap: 8px; }
.pdot { width: 4px; height: 4px; border-radius: 50%; background: var(--glass-border); transition: background var(--transition); }
.pdot.active { background: var(--amber); }
.explore-btn {
  padding: 10px 28px; border: 1px solid rgba(200,150,15,0.35);
  border-radius: 20px; background: var(--amber-soft); color: var(--amber);
  font-family: var(--font-sans); font-size: 12px; letter-spacing: 0.1em;
  cursor: pointer; transition: all var(--transition);
}
.explore-btn:hover { background: rgba(200,150,15,0.2); box-shadow: 0 4px 16px rgba(200,150,15,0.2); }

.chapter-enter-active, .chapter-leave-active { transition: opacity 250ms ease, transform 250ms ease; }
.chapter-enter-from { opacity: 0; transform: translateY(10px); }
.chapter-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
