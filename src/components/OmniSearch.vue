<template>
  <div class="omni-search" :class="positionClass">
    <input
      ref="inputEl"
      v-model="query"
      class="search-input"
      type="text"
      placeholder="输入食物、地域或风味…"
      autocomplete="off"
      @input="onInput"
      @blur="hideDropdown"
    />
    <Transition name="dropdown">
      <div v-if="results.length && showDropdown" class="dropdown">
        <div
          v-for="item in results"
          :key="item.label"
          class="result-item"
          @mousedown.prevent="selectItem(item)"
        >
          <span class="result-dot" :style="{ background: item.color }" />
          <span class="result-label">
            {{ item.label }}
            <span class="result-sub">· {{ item.sub }}</span>
          </span>
          <span class="result-tag">在地图中查看 →</span>
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
.omni-search {
  position: fixed;
  z-index: 80;
  transition: all 400ms cubic-bezier(0.4, 0, 0.2, 1);
}
.pos-topleft  { top: 28px; left: 28px; }
.pos-topcenter { top: 28px; left: 50%; transform: translateX(-50%); }

.search-input {
  width: 320px;
  height: 44px;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 22px;
  padding: 0 20px;
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 300;
  color: var(--text);
  letter-spacing: 0.02em;
  outline: none;
  box-shadow: var(--shadow-sm);
  backdrop-filter: var(--blur-sm);
  -webkit-backdrop-filter: var(--blur-sm);
  transition: all var(--transition);
  display: block;
}
.search-input::placeholder { color: var(--text-muted); }
.search-input:focus {
  background: rgba(255, 252, 248, 0.98);
  box-shadow: var(--shadow-md), 0 0 0 2px var(--amber-soft);
  width: 360px;
}

.dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0; right: 0;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-md);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  overflow: hidden;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  font-size: 12px;
  color: var(--text-mid);
  cursor: pointer;
  transition: background var(--transition);
}
.result-item:hover { background: var(--amber-soft); }

.result-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.result-sub { color: var(--text-muted); font-weight: 300; font-size: 10px; }
.result-tag { margin-left: auto; font-size: 10px; color: var(--amber); opacity: 0.8; }

.dropdown-enter-active, .dropdown-leave-active { transition: opacity 150ms ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; }
</style>
