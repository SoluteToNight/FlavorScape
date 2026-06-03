<template>
  <div class="nav-dot fixed bottom-8 left-8 z-[90] cursor-pointer" :class="{ open: isOpen }" @mouseenter="isOpen = true" @mouseleave="isOpen = false">
    <div class="core w-2.5 h-2.5 rounded-full bg-amber relative z-[2]" />
    <Transition name="menu">
      <div v-show="isOpen" class="absolute bottom-5 -left-2">
        <div
          v-for="item in navItems"
          :key="item.name"
          class="absolute flex items-center gap-2.5 cursor-pointer whitespace-nowrap"
          :style="{ bottom: item.bottom + 'px' }"
          @click="navigate(item.name)"
        >
          <span class="spoke-dot w-1.5 h-1.5 rounded-full bg-amber opacity-60 shrink-0" :class="{ active: route.name === item.name }" />
          <span class="spoke-label text-xs font-light text-text-mid tracking-[0.06em] ml-1.5">{{ item.label }}</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isOpen = ref(false)

const navItems = [
  { name: 'home',      label: '首　页',     bottom: 60  },
  { name: 'map',       label: '探索地图',   bottom: 104 },
  { name: 'library',   label: '风味基因库', bottom: 148 },
  { name: 'narrative', label: '时空叙事馆', bottom: 192 },
  { name: 'about',     label: '关于·方法论', bottom: 236 },
]

function navigate(name) {
  router.push({ name })
  isOpen.value = false
}
</script>

<style scoped>
/* KEPT: animation, hover cascades, Vue transitions — Tailwind cannot express these */
.core {
  animation: breathe 2.4s ease-in-out infinite;
  transition: transform var(--transition);
}
.nav-dot:hover .core { transform: scale(1.3); }

.spoke-dot {
  transition: opacity var(--transition), transform var(--transition);
}
.spoke-dot.active,
.spoke:hover .spoke-dot {
  opacity: 1;
  transform: scale(1.4);
}

.spoke-label {
  transition: color var(--transition);
}
.spoke:hover .spoke-label { color: var(--amber); }

.menu-enter-active, .menu-leave-active {
  transition: opacity 200ms ease;
}
.menu-enter-from, .menu-leave-to { opacity: 0; }
</style>
