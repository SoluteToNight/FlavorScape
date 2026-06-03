<template>
  <div class="fixed top-navbar inset-x-0 bottom-0 bg-bg overflow-y-auto">
    <header class="lib-header sticky top-0 z-20 flex items-center gap-5 px-[60px] py-4 border-b border-glass-border">
      <span class="font-serif text-lg font-medium tracking-[0.08em]">风味基因库</span>
      <div class="flex gap-2">
        <button
          v-for="cat in categories"
          :key="cat"
          class="filter-btn px-4 py-[5px] rounded-[14px] text-xs tracking-[0.06em] cursor-pointer border border-glass-border bg-transparent text-text-mid font-sans transition-all"
          :class="{ active: activeCat === cat }"
          @click="activeCat = cat"
        >{{ cat }}</button>
      </div>
      <span class="ml-auto text-xs text-text-muted tracking-[0.08em]">{{ visible.length }} 个地域节点</span>
    </header>

    <div class="grid grid-cols-[repeat(auto-fill,minmax(270px,1fr))] gap-5 px-[60px] py-6 pb-[60px]">
      <div
        v-for="(d, i) in visible"
        :key="d.city"
        class="flavor-card bg-glass border border-glass-border rounded-lg p-6 cursor-pointer shadow-app-sm"
        :style="{ animationDelay: i * 0.07 + 's' }"
        @click="goToMap(d)"
      >
        <div class="font-serif text-3xl font-medium mb-0.5">{{ d.city }}</div>
        <div class="text-2xs text-text-muted tracking-[0.12em] mb-4">{{ d.region }} · {{ d.eco }}</div>
        <div class="flex items-center gap-3 mb-3">
          <div class="text-center">
            <div class="font-['Inter',sans-serif] text-2xl font-light leading-none" :style="{ color: d.color }">{{ d.vals[0].toFixed(2) }}</div>
            <div class="text-2xs text-text-muted tracking-[0.1em] mt-[3px]">{{ d.primary[0] }}</div>
          </div>
          <div class="text-lg text-glass-border">×</div>
          <div class="text-center">
            <div class="font-['Inter',sans-serif] text-2xl font-light leading-none" :style="{ color: d.color }">{{ d.vals[1].toFixed(2) }}</div>
            <div class="text-2xs text-text-muted tracking-[0.1em] mt-[3px]">{{ d.primary[1] }}</div>
          </div>
        </div>
        <div class="flex justify-center mt-1">
          <FlavorRadar :scores="d.scores" :color="d.color" :size="108" />
        </div>
        <div class="text-2xs text-text-muted tracking-[0.06em] mt-3.5 pt-3 border-t border-glass-border">{{ d.eco }}</div>
      </div>
    </div>
    <p class="text-center text-xs text-text-muted tracking-[0.1em] px-[60px] pb-10">点击任一节点，跳转至地图观察其基因来源与传播路径</p>
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
/* KEPT: backdrop-filter vendor prefix, hover effects, animation */
.lib-header {
  background: rgba(248,244,239,0.95);
  backdrop-filter: var(--blur-sm);
  -webkit-backdrop-filter: var(--blur-sm);
}

.filter-btn.active, .filter-btn:hover {
  background: var(--amber-soft);
  border-color: rgba(200,150,15,0.3);
  color: var(--amber);
}

.flavor-card {
  backdrop-filter: var(--blur-sm);
  -webkit-backdrop-filter: var(--blur-sm);
  transition: transform var(--transition), box-shadow var(--transition);
  animation: fadeUp 0.5s ease both;
}
.flavor-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
</style>
