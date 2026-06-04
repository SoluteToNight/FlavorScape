<template>
  <nav class="navbar fixed top-0 inset-x-0 h-navbar z-[100] border-b transition-[background,border-color] duration-[400ms] ease" :class="{ 'is-home': isHome, 'is-map': isMap, 'is-product': isProduct }">
    <div class="navbar-shell h-full flex items-center">

      <!-- Logo -->
      <RouterLink to="/" class="navbar-logo no-underline flex items-baseline gap-0 shrink-0 h-9 px-3.5 rounded-full tracking-[0.04em]">
        <span class="logo-serif font-serif text-[17px] font-medium text-earth">寻味</span><span class="logo-sans font-sans text-sm font-light text-text-mid tracking-[0.1em]">地理</span>
      </RouterLink>

      <!-- Nav links -->
      <div class="nav-links flex items-center gap-1 flex-1 justify-center h-[38px] p-1 border border-[rgba(110,92,68,0.11)] rounded-full">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="item.path"
          class="nav-link no-underline text-sm font-medium text-text-mid tracking-[0.02em] px-[15px] py-1.5 rounded-full transition-all relative whitespace-nowrap"
          :class="{ active: route.name === item.name }"
        >
          {{ item.label }}
        </RouterLink>
      </div>

      <!-- Search -->
      <div class="search-wrap relative flex items-center gap-2 shrink-0" :class="{ expanded: searchOpen }">
        <input
          v-if="searchOpen"
          ref="searchEl"
          v-model="query"
          class="search-input w-[220px] h-[34px] bg-[rgba(255,252,248,0.85)] border border-glass-border rounded-[17px] px-4 font-sans text-xs font-light text-text tracking-[0.02em] outline-none transition-all"
          placeholder="搜索食物、地域或风味…"
          autocomplete="off"
          @input="onInput"
          @blur="onBlur"
          @keydown.escape="closeSearch"
        />
        <button class="search-btn w-[34px] h-[34px] rounded-full border border-glass-border bg-transparent cursor-pointer text-text-mid flex items-center justify-center transition-all shrink-0" :class="{ open: searchOpen }" @click="toggleSearch" aria-label="搜索">
          <svg v-if="!searchOpen" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
        <Transition name="dropdown">
          <div v-if="results.length && showDropdown" class="search-dropdown absolute top-[calc(100%+8px)] right-0 w-80 bg-[rgba(255,252,248,0.96)] border border-glass-border rounded-sm shadow-app-md overflow-hidden z-[110]">
            <div
              v-for="item in results"
              :key="item.label"
              class="flex items-center gap-2.5 px-4 py-2.5 cursor-pointer transition-colors"
              @mousedown.prevent="select(item)"
            >
              <span class="w-1.5 h-1.5 rounded-full shrink-0" :style="{ background: item.color }" />
              <span class="text-sm text-text">{{ item.label }}</span>
              <span class="text-xs text-text-muted ml-1">{{ item.sub }}</span>
              <span class="ml-auto text-2xs text-amber opacity-80">→ 地图</span>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Auth -->
      <div class="relative shrink-0">
        <!-- Logged out -->
        <RouterLink
          v-if="!authStore.isLoggedIn"
          to="/login"
          class="auth-btn h-[34px] rounded-full border border-[rgba(139,94,52,0.28)] bg-transparent cursor-pointer text-sm font-medium text-earth tracking-[0.03em] px-5 transition-all hover:bg-[rgba(139,94,52,0.1)] hover:border-earth active:scale-[0.97] no-underline inline-flex items-center"
        >
          登录
        </RouterLink>

        <!-- Logged in -->
        <div v-else class="relative">
          <button
            class="auth-btn h-[34px] rounded-full border border-[rgba(94,123,80,0.28)] bg-transparent cursor-pointer text-sm font-medium text-leaf tracking-[0.03em] px-4 transition-all hover:bg-[rgba(94,123,80,0.1)] active:scale-[0.97] flex items-center gap-1.5"
            @click="userMenuOpen = !userMenuOpen"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
            {{ authStore.user?.username }}
          </button>
          <Transition name="dropdown">
            <div
              v-if="userMenuOpen"
              class="absolute top-[calc(100%+8px)] right-0 w-36 bg-[rgba(255,252,248,0.96)] border border-glass-border rounded-[10px] shadow-app-md overflow-hidden z-[110]"
            >
              <RouterLink
                to="/profile"
                class="block w-full text-left px-4 py-2.5 text-sm text-text hover:bg-[rgba(110,92,68,0.06)] transition-colors no-underline"
                @click="userMenuOpen = false"
              >
                个人主页
              </RouterLink>
              <button
                class="w-full text-left px-4 py-2.5 text-sm text-text hover:bg-[rgba(110,92,68,0.06)] transition-colors"
                @click="userMenuOpen = false; authStore.logout()"
              >
                退出登录
              </button>
            </div>
          </Transition>
        </div>
      </div>

    </div>
  </nav>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/app.js'
import { useAuthStore } from '../stores/auth.js'
import { api } from '../utils/api.js'

const route  = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()

const isHome = computed(() => route.name === 'home')
const isMap  = computed(() => route.name === 'map')
const isProduct = computed(() => ['brand', 'spread', 'marketing', 'archive', 'studio', 'import'].includes(route.name))

const navItems = [
  { name: 'studio',    path: '/studio',    label: '创作工作台' },
  { name: 'home',      path: '/',          label: '产品入口' },
  { name: 'brand',     path: '/brand',     label: '智慧大屏' },
  { name: 'marketing', path: '/marketing', label: '营销海报' },
  { name: 'archive',   path: '/archive',   label: '实证白皮书' },
  { name: 'import',    path: '/import',    label: '资产导入' },
  { name: 'spread',    path: '/spread',    label: '传播图谱' },
  { name: 'map',       path: '/map',       label: '风味底图' },
]

const searchOpen    = ref(false)
const showDropdown  = ref(false)
const query         = ref('')
const results       = ref([])
const searchEl      = ref(null)
const userMenuOpen  = ref(false)
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
      const data = await api(`/api/search?q=${encodeURIComponent(query.value)}`)
      results.value = Array.isArray(data) ? data : []
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
/* KEPT: backdrop-filter vendor prefixes, page-conditional styles, gradients, composite shadows, animations, Vue transitions */

.navbar {
  background: rgba(250, 247, 241, 0.78);
  border-bottom-color: rgba(110, 92, 68, 0.12);
  backdrop-filter: blur(22px) saturate(1.08);
  -webkit-backdrop-filter: blur(22px) saturate(1.08);
}

.navbar.is-home {
  background: rgba(250, 247, 241, 0.24);
  border-bottom-color: rgba(110, 92, 68, 0.08);
}
.navbar.is-home .nav-link { color: rgba(90,83,78,0.75); }
.navbar.is-home .nav-link:hover { color: var(--text-mid); background: rgba(255,255,255,0.15); }
.navbar.is-home .nav-link.active { color: var(--earth); background: rgba(139, 94, 52, 0.08); box-shadow: inset 0 0 0 1px rgba(139, 94, 52, 0.12); }
.navbar.is-home .logo-sans { color: rgba(90,83,78,0.75); }

.navbar.is-map {
  background: rgba(248, 244, 239, 0.82);
}

.navbar.is-product {
  background: rgba(250, 247, 241, 0.86);
  border-bottom-color: rgba(116, 92, 62, 0.14);
}

.navbar-logo {
  background: rgba(255, 252, 247, 0.56);
  box-shadow: inset 0 0 0 1px rgba(110, 92, 68, 0.1);
}

.navbar-shell {
  width: min(var(--content-max), calc(100% - (var(--page-gutter) * 2)));
  margin-inline: auto;
  gap: clamp(12px, 1.5vw, 28px);
}

.nav-links {
  min-width: 0;
  background: rgba(255, 252, 247, 0.48);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.62);
}

.nav-link {
  flex: 0 1 auto;
}

.nav-link:hover {
  color: var(--text);
  background: rgba(94, 123, 80, 0.08);
}
.nav-link.active {
  color: var(--earth);
  background: rgba(139, 94, 52, 0.08);
  font-weight: 600;
  box-shadow: inset 0 0 0 1px rgba(139, 94, 52, 0.12);
}

.search-input {
  width: clamp(176px, 13vw, 220px);
  animation: fadeRight 200ms ease;
}
.search-input:focus {
  background: rgba(255,252,248,0.98);
  box-shadow: 0 0 0 2px var(--amber-soft);
  border-color: rgba(232,169,23,0.3);
  width: clamp(210px, 16vw, 260px);
}
.search-input::placeholder { color: var(--text-muted); }

@keyframes fadeRight {
  from { opacity: 0; width: 0; }
  to   { opacity: 1; width: 220px; }
}

.search-btn:hover, .search-btn.open {
  background: var(--amber-soft);
  border-color: rgba(232,169,23,0.3);
  color: var(--amber);
}

.search-dropdown {
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
}

.dropdown-enter-active, .dropdown-leave-active { transition: opacity 150ms ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; }

.auth-btn {
  white-space: nowrap;
}
.shadow-app-md {
  box-shadow: var(--shadow-md);
}

@media (max-width: 1439px), (max-height: 800px) {
  .navbar-shell {
    gap: 12px;
  }

  .navbar-logo {
    padding-inline: 12px;
  }

  .nav-links {
    gap: 0;
    padding: 3px;
  }

  .nav-link {
    padding-inline: 11px;
    font-size: 12px;
  }

  .search-wrap {
    gap: 8px;
  }

  .search-input {
    width: 176px;
  }
}
</style>
