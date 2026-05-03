<template>
  <div class="nav-dot" :class="{ open: isOpen }" @mouseenter="isOpen = true" @mouseleave="isOpen = false">
    <div class="core" />
    <Transition name="menu">
      <div v-show="isOpen" class="menu">
        <div
          v-for="item in navItems"
          :key="item.name"
          class="spoke"
          :style="{ bottom: item.bottom + 'px' }"
          @click="navigate(item.name)"
        >
          <span class="spoke-dot" :class="{ active: route.name === item.name }" />
          <span class="spoke-label">{{ item.label }}</span>
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
.nav-dot {
  position: fixed;
  bottom: 32px;
  left: 32px;
  z-index: 90;
  cursor: pointer;
}

.core {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--amber);
  animation: breathe 2.4s ease-in-out infinite;
  position: relative;
  z-index: 2;
  transition: transform var(--transition);
}
.nav-dot:hover .core { transform: scale(1.3); }

.menu {
  position: absolute;
  bottom: 20px;
  left: -8px;
}

.spoke {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  white-space: nowrap;
}

.spoke-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--amber);
  opacity: 0.6;
  flex-shrink: 0;
  transition: opacity var(--transition), transform var(--transition);
}
.spoke-dot.active,
.spoke:hover .spoke-dot {
  opacity: 1;
  transform: scale(1.4);
}

.spoke-label {
  font-size: 11px;
  font-weight: 300;
  color: var(--text-mid);
  letter-spacing: 0.06em;
  transition: color var(--transition);
  margin-left: 6px;
}
.spoke:hover .spoke-label { color: var(--amber); }

.menu-enter-active, .menu-leave-active {
  transition: opacity 200ms ease;
}
.menu-enter-from, .menu-leave-to { opacity: 0; }
</style>
