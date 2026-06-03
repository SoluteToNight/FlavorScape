<template>
  <div class="fixed top-navbar inset-x-0 bottom-0 bg-bg flex">
    <div class="left-nav w-[200px] px-10 py-12 flex flex-col relative">
      <div class="spine absolute left-[52px] top-[60px] bottom-[60px] w-px" />
      <div
        v-for="(ch, i) in chapters"
        :key="ch.id"
        class="chapter-dot relative z-[2] flex items-center gap-4 mb-12 cursor-pointer"
        :class="{ active: i === appStore.currentChapter }"
        @click="appStore.setChapter(i)"
      >
        <span class="dot-circle w-2 h-2 rounded-full bg-transparent border-[1.5px] border-text-muted shrink-0 transition-all" />
        <span class="dot-label text-xs text-text-muted tracking-[0.06em] whitespace-nowrap transition-colors">{{ ch.title }}</span>
      </div>
    </div>

    <div class="flex-1 flex flex-col py-10 pr-[60px] pl-5 overflow-hidden">
      <div class="mini-map-wrap shrink-0 h-[260px] rounded-lg overflow-hidden bg-[#EDE5D8] mb-7 shadow-app-sm">
        <canvas ref="miniCanvas" class="w-full h-[260px] block" />
      </div>

      <div class="flex-1 overflow-y-auto max-w-[680px]" v-if="current">
        <Transition name="chapter" mode="out-in">
          <div :key="appStore.currentChapter">
            <div class="font-serif text-3xl font-medium tracking-[0.05em] mb-1">{{ current.title }}</div>
            <div class="text-xs text-amber tracking-[0.14em] mb-5">{{ current.date }}</div>
            <p class="text-base font-light leading-[2.1] text-text-mid tracking-[0.04em]">{{ current.body }}</p>
            <blockquote class="ch-cite mt-5 px-[18px] py-3.5 bg-[rgba(200,150,15,0.06)] border-l-2 border-[rgba(200,150,15,0.4)] rounded-r-sm text-xs text-text-mid italic leading-[1.8]">{{ current.cite }}</blockquote>
            <div class="mt-2.5 text-2xs text-text-muted tracking-[0.08em]">—— {{ current.source }}</div>
            <div class="flex items-center gap-5 mt-6">
              <div class="flex gap-2">
                <span
                  v-for="(_, i) in chapters"
                  :key="i"
                  class="pdot w-1 h-1 rounded-full bg-glass-border transition-colors"
                  :class="{ active: i === appStore.currentChapter }"
                />
              </div>
              <button
                v-if="appStore.currentChapter === chapters.length - 1"
                class="explore-btn px-7 py-2.5 border border-[rgba(200,150,15,0.35)] rounded-[20px] bg-amber-soft text-amber font-sans text-xs tracking-[0.1em] cursor-pointer transition-all"
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
  chapters.value = await chRes.json()
  routes.value = await rRes.json()
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
  const route = routes.value.find(r => r.name === routeName)
  if (!route) return

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

  let t = 0
  function frame() {
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
    const lt = t * (pts.length-1) - seg
    const [px, py] = [pts[seg][0] + (pts[seg+1][0]-pts[seg][0])*lt, pts[seg][1] + (pts[seg+1][1]-pts[seg][1])*lt]
    const g = ctx.createRadialGradient(px,py,0,px,py,10)
    g.addColorStop(0, route.color + 'FF'); g.addColorStop(1, route.color + '00')
    ctx.beginPath(); ctx.arc(px,py,10,0,Math.PI*2); ctx.fillStyle = g; ctx.fill()
    ctx.beginPath(); ctx.arc(px,py,3,0,Math.PI*2); ctx.fillStyle = route.color; ctx.fill()
    rafId = requestAnimationFrame(frame)
  }
  frame()
}
</script>

<style scoped>
/* KEPT: gradient, hover cascades, active states, Vue transitions */
.spine {
  background: linear-gradient(to bottom, transparent, var(--glass-border) 10%, var(--glass-border) 90%, transparent);
}

.dot-circle { transition: all var(--transition); }
.chapter-dot.active .dot-circle {
  background: var(--amber); border-color: var(--amber);
  box-shadow: 0 0 0 4px var(--amber-soft);
}
.chapter-dot.active .dot-label { color: var(--text); }
.chapter-dot:hover .dot-label { color: var(--text-mid); }

.pdot.active { background: var(--amber); }

.explore-btn:hover { background: rgba(200,150,15,0.2); box-shadow: 0 4px 16px rgba(200,150,15,0.2); }

.chapter-enter-active, .chapter-leave-active { transition: opacity 250ms ease, transform 250ms ease; }
.chapter-enter-from { opacity: 0; transform: translateY(10px); }
.chapter-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
