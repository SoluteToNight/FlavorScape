<template>
  <div class="fixed z-[80] transition-all duration-[400ms]" :class="positionClass">
    <input
      ref="inputEl"
      v-model="query"
      class="block h-11 w-80 rounded-[22px] border border-glass-border bg-glass px-5 font-sans text-sm font-light tracking-[0.02em] text-text shadow-app-sm outline-none backdrop-blur-sm transition-all placeholder:text-text-muted focus:w-[360px] focus:bg-[rgba(255,252,248,0.98)] focus:shadow-[var(--shadow-md),0_0_0_2px_var(--amber-soft)]"
      type="text"
      placeholder="输入食物、地域或风味…"
      autocomplete="off"
      @input="onInput"
      @blur="hideDropdown"
    />
    <Transition name="dropdown">
      <div v-if="results.length && showDropdown" class="absolute inset-x-0 top-[calc(100%+8px)] overflow-hidden rounded-sm border border-glass-border bg-glass shadow-app-md backdrop-blur-[24px]">
        <div
          v-for="item in results"
          :key="item.label"
          class="flex cursor-pointer items-center gap-2.5 px-4 py-2.5 text-xs text-text-mid transition-colors hover:bg-amber-soft"
          @mousedown.prevent="selectItem(item)"
        >
          <span class="h-1.5 w-1.5 shrink-0 rounded-full" :style="{ background: item.color }" />
          <span>
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
  if (route.name === 'map') return 'left-7 top-7'
  return 'left-1/2 top-7 -translate-x-1/2'
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
.dropdown-enter-active, .dropdown-leave-active { transition: opacity 150ms ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; }
</style>
