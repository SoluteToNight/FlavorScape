<template>
  <nav class="navbar" :class="{ 'is-home': isHome, 'is-map': isMap }">
    <div class="navbar-inner">

      <!-- Logo -->
      <RouterLink to="/" class="navbar-logo">
        <span class="logo-serif">寻味</span><span class="logo-sans">地理</span>
      </RouterLink>

      <!-- Nav links -->
      <div class="nav-links">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="item.path"
          class="nav-link"
          :class="{ active: route.name === item.name }"
        >
          {{ item.label }}
        </RouterLink>
      </div>

      <!-- Search -->
      <div class="navbar-search" :class="{ expanded: searchOpen }">
        <input
          v-if="searchOpen"
          ref="searchEl"
          v-model="query"
          class="search-input"
          placeholder="搜索食物、地域或风味…"
          autocomplete="off"
          @input="onInput"
          @blur="onBlur"
          @keydown.escape="closeSearch"
        />
        <button class="search-btn" :class="{ open: searchOpen }" @click="toggleSearch" aria-label="搜索">
          <svg v-if="!searchOpen" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
        <Transition name="dropdown">
          <div v-if="results.length && showDropdown" class="search-dropdown">
            <div
              v-for="item in results"
              :key="item.label"
              class="search-item"
              @mousedown.prevent="select(item)"
            >
              <span class="item-dot" :style="{ background: item.color }" />
              <span class="item-label">{{ item.label }}</span>
              <span class="item-sub">{{ item.sub }}</span>
              <span class="item-tag">→ 地图</span>
            </div>
          </div>
        </Transition>
      </div>

    </div>
  </nav>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/app.js'

const route  = useRoute()
const router = useRouter()
const appStore = useAppStore()

const isHome = computed(() => route.name === 'home')
const isMap  = computed(() => route.name === 'map')

const navItems = [
  { name: 'home',      path: '/',          label: '首　页'   },
  { name: 'map',       path: '/map',        label: '探索地图' },
  { name: 'library',   path: '/library',    label: '风味基因库'},
  { name: 'narrative', path: '/narrative',  label: '时空叙事馆'},
  { name: 'about',     path: '/about',      label: '关于方法论'},
]

const searchOpen    = ref(false)
const showDropdown  = ref(false)
const query         = ref('')
const results       = ref([])
const searchEl      = ref(null)
let debounceTimer   = null

async function toggleSearch() {
  searchOpen.value = !searchOpen.value
  if (searchOpen.value) {
    await nextTick()
    searchEl.value?.focus()
  } else {
    closeSearch()
  }
}

function closeSearch() {
  searchOpen.value = false
  showDropdown.value = false
  query.value = ''
  results.value = []
}

function onBlur() {
  setTimeout(() => { showDropdown.value = false }, 150)
}

async function onInput() {
  clearTimeout(debounceTimer)
  if (!query.value.trim()) { results.value = []; showDropdown.value = false; return }
  debounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query.value)}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      results.value = await res.json()
      showDropdown.value = results.value.length > 0
    } catch (err) {
      console.warn('[Navbar search]', err.message)
      results.value = []
      showDropdown.value = false
    }
  }, 200)
}

function select(item) {
  if (item.type === 'node')  appStore.selectNode(item.data)
  if (item.type === 'route') appStore.selectRoute(item.data)
  closeSearch()
  router.push('/map')
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: var(--navbar-h);
  z-index: 100;
  background: rgba(248, 244, 239, 0.9);
  border-bottom: 1px solid var(--glass-border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  transition: background 400ms ease, border-color 400ms ease;
}

/* On the home page: fully transparent so the particle canvas shows through */
.navbar.is-home {
  background: transparent;
  border-bottom-color: transparent;
}

/* On the map page: slightly more translucent so map shows */
.navbar.is-map {
  background: rgba(248, 244, 239, 0.82);
}

.navbar-inner {
  max-width: 1440px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 32px;
  gap: 40px;
}

/* Logo */
.navbar-logo {
  text-decoration: none;
  display: flex;
  align-items: baseline;
  gap: 0;
  flex-shrink: 0;
  letter-spacing: 0.06em;
}
.logo-serif {
  font-family: var(--font-serif);
  font-size: 17px; font-weight: 500;
  color: var(--amber);
}
.logo-sans {
  font-family: var(--font-sans);
  font-size: 14px; font-weight: 300;
  color: var(--text-mid);
  letter-spacing: 0.1em;
}

/* Nav links */
.nav-links {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  justify-content: center;
}

.nav-link {
  text-decoration: none;
  font-size: 13px;
  font-weight: 300;
  color: var(--text-mid);
  letter-spacing: 0.06em;
  padding: 6px 14px;
  border-radius: 20px;
  transition: all var(--transition);
  position: relative;
  white-space: nowrap;
}
.nav-link:hover {
  color: var(--text);
  background: rgba(200, 150, 15, 0.08);
}
.nav-link.active {
  color: var(--amber);
  background: var(--amber-soft);
  font-weight: 400;
}

/* On home page: white text for contrast against dark particle canvas */
.navbar.is-home .nav-link { color: rgba(90,83,78,0.75); }
.navbar.is-home .nav-link:hover { color: var(--text-mid); background: rgba(255,255,255,0.15); }
.navbar.is-home .nav-link.active { color: var(--amber); background: rgba(200,150,15,0.12); }
.navbar.is-home .logo-sans { color: rgba(90,83,78,0.75); }

/* Search */
.navbar-search {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.search-input {
  width: 220px;
  height: 34px;
  background: rgba(255,252,248,0.85);
  border: 1px solid var(--glass-border);
  border-radius: 17px;
  padding: 0 16px;
  font-family: var(--font-sans);
  font-size: 12px; font-weight: 300;
  color: var(--text); letter-spacing: 0.02em;
  outline: none;
  transition: all var(--transition);
  animation: fadeRight 200ms ease;
}
.search-input:focus {
  background: rgba(255,252,248,0.98);
  box-shadow: 0 0 0 2px var(--amber-soft);
  border-color: rgba(200,150,15,0.3);
  width: 260px;
}
.search-input::placeholder { color: var(--text-muted); }

@keyframes fadeRight {
  from { opacity: 0; width: 0; }
  to   { opacity: 1; width: 220px; }
}

.search-btn {
  width: 34px; height: 34px;
  border-radius: 50%;
  border: 1px solid var(--glass-border);
  background: transparent;
  cursor: pointer; color: var(--text-mid);
  display: flex; align-items: center; justify-content: center;
  transition: all var(--transition);
  flex-shrink: 0;
}
.search-btn:hover, .search-btn.open {
  background: var(--amber-soft);
  border-color: rgba(200,150,15,0.3);
  color: var(--amber);
}

.search-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  background: rgba(255,252,248,0.96);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-md);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  overflow: hidden;
  z-index: 110;
}
.search-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; cursor: pointer;
  transition: background var(--transition);
}
.search-item:hover { background: var(--amber-soft); }
.item-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.item-label { font-size: 13px; color: var(--text); }
.item-sub { font-size: 11px; color: var(--text-muted); margin-left: 4px; }
.item-tag { margin-left: auto; font-size: 10px; color: var(--amber); opacity: 0.8; }

.dropdown-enter-active, .dropdown-leave-active { transition: opacity 150ms ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; }
</style>
