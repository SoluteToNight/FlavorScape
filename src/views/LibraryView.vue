<template>
  <div class="library-page">
    <header class="lib-header">
      <span class="lib-title">风味基因库</span>
      <div class="filter-bar">
        <button
          v-for="cat in categories"
          :key="cat"
          class="filter-btn"
          :class="{ active: activeCat === cat }"
          @click="activeCat = cat"
        >{{ cat }}</button>
      </div>
      <span class="lib-count">{{ visible.length }} 个地域节点</span>
    </header>

    <div class="lib-grid">
      <div
        v-for="(d, i) in visible"
        :key="d.city"
        class="flavor-card"
        :style="{ animationDelay: i * 0.07 + 's' }"
        @click="goToMap(d)"
      >
        <div class="card-city">{{ d.city }}</div>
        <div class="card-region">{{ d.region }} · {{ d.eco }}</div>
        <div class="card-scores">
          <div class="score-item">
            <div class="score-val" :style="{ color: d.color }">{{ d.vals[0].toFixed(2) }}</div>
            <div class="score-label">{{ d.primary[0] }}</div>
          </div>
          <div class="score-sep">×</div>
          <div class="score-item">
            <div class="score-val" :style="{ color: d.color }">{{ d.vals[1].toFixed(2) }}</div>
            <div class="score-label">{{ d.primary[1] }}</div>
          </div>
        </div>
        <div class="card-radar">
          <FlavorRadar :scores="d.scores" :color="d.color" :size="108" />
        </div>
        <div class="card-eco">{{ d.eco }}</div>
      </div>
    </div>
    <p class="lib-footer">点击任一节点，跳转至地图观察其基因来源与传播路径</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app.js'
import FlavorRadar from '../components/FlavorRadar.vue'

const router = useRouter()
const appStore = useAppStore()
const flavors = ref([])
const activeCat = ref('全部')
const categories = ['全部', '辛辣', '鲜甜', '咸香', '酸鲜']

onMounted(async () => {
  const res = await fetch('/api/flavors')
  flavors.value = await res.json()
})

const visible = computed(() =>
  activeCat.value === '全部' ? flavors.value : flavors.value.filter(f => f.cat === activeCat.value)
)

function goToMap(d) {
  appStore.selectNode(d)
  router.push('/map')
}
</script>

<style scoped>
.library-page {
  position: fixed;
  top: var(--navbar-h); left: 0; right: 0; bottom: 0;
  background: var(--bg);
  overflow-y: auto;
}

.lib-header {
  position: sticky; top: 0;
  background: rgba(248,244,239,0.95);
  backdrop-filter: var(--blur-sm); -webkit-backdrop-filter: var(--blur-sm);
  padding: 16px 60px;
  z-index: 20;
  display: flex; align-items: center; gap: 20px;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--glass-border);
}
.lib-title { font-family: var(--font-serif); font-size: 16px; font-weight: 500; letter-spacing: 0.08em; }
.filter-bar { display: flex; flex-wrap: wrap; gap: 8px; }
.filter-btn {
  padding: 5px 16px; border-radius: 14px;
  font-size: 11px; letter-spacing: 0.06em;
  cursor: pointer; border: 1px solid var(--glass-border);
  background: transparent; color: var(--text-mid);
  font-family: var(--font-sans);
  transition: all var(--transition);
}
.filter-btn.active, .filter-btn:hover {
  background: var(--amber-soft);
  border-color: rgba(200,150,15,0.3);
  color: var(--amber);
}
.lib-count { margin-left: auto; font-size: 11px; color: var(--text-muted); letter-spacing: 0.08em; }

.lib-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 20px;
  padding: 24px 60px 60px;
}

@media (max-width: 860px) {
  .lib-header { padding: 16px 28px; }
  .lib-count { margin-left: 0; }
  .lib-grid { padding: 22px 28px 48px; }
}

.flavor-card {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  padding: 24px;
  cursor: pointer;
  backdrop-filter: var(--blur-sm); -webkit-backdrop-filter: var(--blur-sm);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition), box-shadow var(--transition);
  animation: fadeUp 0.5s ease both;
}
.flavor-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
.card-city { font-family: var(--font-serif); font-size: 22px; font-weight: 500; margin-bottom: 2px; }
.card-region { font-size: 10px; color: var(--text-muted); letter-spacing: 0.12em; margin-bottom: 16px; }
.card-scores { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.score-item { text-align: center; }
.score-val { font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 300; line-height: 1; }
.score-label { font-size: 10px; color: var(--text-muted); letter-spacing: 0.1em; margin-top: 3px; }
.score-sep { font-size: 16px; color: var(--glass-border); }
.card-radar { display: flex; justify-content: center; margin-top: 4px; }
.card-eco {
  font-size: 10px; color: var(--text-muted); letter-spacing: 0.06em;
  margin-top: 14px; padding-top: 12px;
  border-top: 1px solid var(--glass-border);
}
.lib-footer {
  text-align: center; font-size: 11px; color: var(--text-muted);
  letter-spacing: 0.1em; padding: 0 60px 40px;
}
</style>
