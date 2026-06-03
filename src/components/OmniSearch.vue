<template>
  <div class="omni-search fixed z-[80] transition-all duration-[400ms]" :class="positionClass">
    <input
      ref="inputEl"
      v-model="query"
      class="search-input block w-80 h-11 bg-glass border border-glass-border rounded-[22px] px-5 font-sans text-sm font-light text-text tracking-[0.02em] outline-none shadow-app-sm backdrop-blur-sm"
      type="text"
      placeholder="输入食物、地域或风味…"
      autocomplete="off"
      @input="onInput"
      @blur="hideDropdown"
    />
    <Transition name="dropdown">
      <div v-if="results.length && showDropdown" class="dropdown absolute top-[calc(100%+8px)] inset-x-0 bg-glass border border-glass-border rounded-sm shadow-app-md backdrop-blur-[24px] overflow-hidden">
        <div
          v-for="item in results"
          :key="item.label"
          class="result-item flex items-center gap-2.5 px-4 py-2.5 text-xs text-text-mid cursor-pointer transition-colors"
          @mousedown.prevent="selectItem(item)"
        >
          <span class="result-dot w-1.5 h-1.5 rounded-full shrink-0" :style="{ background: item.color }" />
          <span class="result-label">
            {{ item.label }}
            <span class="text-2xs text-text-muted font-light">· {{ item.sub }}</span>
          </span>
          <span class="ml-auto text-2xs text-amber opacity-80">在地图中查看 →</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/app.js'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const query = ref('')
const results = ref([])
const showDropdown = ref(false)
let debounceTimer = null

const positionClass = computed(() => {
  if (route.name === 'map') return 'pos-topleft'
  return 'pos-topcenter'
})

async function onInput() {
  clearTimeout(debounceTimer)
  if (!query.value.trim()) {
    results.value = []
    showDropdown.value = false
    return
  }
  debounceTimer = setTimeout(async () => {
    const res = await fetch(`/api/search?q=${encodeURIComponent(query.value)}`)
    results.value = await res.json()
    showDropdown.value = true
  }, 200)
}

function hideDropdown() {
  setTimeout(() => { showDropdown.value = false }, 150)
}

function selectItem(item) {
  query.value = item.label
  showDropdown.value = false
  if (item.type === 'node') appStore.selectNode(item.data)
  if (item.type === 'route') appStore.selectRoute(item.data)
  router.push({ name: 'map' })
}
</script>

<style scoped>
/* KEPT: vendor-prefixed backdrop-filter, focus effects, Vue transitions */
.pos-topleft  { top: 28px; left: 28px; }
.pos-topcenter { top: 28px; left: 50%; transform: translateX(-50%); }

.search-input {
  -webkit-backdrop-filter: var(--blur-sm);
}
.search-input::placeholder { color: var(--text-muted); }
.search-input:focus {
  background: rgba(255, 252, 248, 0.98);
  box-shadow: var(--shadow-md), 0 0 0 2px var(--amber-soft);
  width: 360px;
}

.dropdown {
  -webkit-backdrop-filter: var(--blur);
}

.result-item:hover { background: var(--amber-soft); }

.dropdown-enter-active, .dropdown-leave-active { transition: opacity 150ms ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; }
</style>
