<template>
  <div class="group/nav fixed bottom-8 left-8 z-[90] cursor-pointer" @mouseenter="isOpen = true" @mouseleave="isOpen = false">
    <div class="relative z-[2] h-2.5 w-2.5 rounded-full bg-amber transition-transform [animation:breathe_2.4s_ease-in-out_infinite] group-hover/nav:scale-[1.3]" />
    <Transition name="menu">
      <div v-show="isOpen" class="absolute bottom-5 -left-2">
        <div
          v-for="item in navItems"
          :key="item.name"
          class="group/spoke absolute flex cursor-pointer items-center gap-2.5 whitespace-nowrap"
          :style="{ bottom: item.bottom + 'px' }"
          @click="navigate(item.name)"
        >
          <span
            class="h-1.5 w-1.5 shrink-0 rounded-full bg-amber transition-[opacity,transform] group-hover/spoke:scale-[1.4] group-hover/spoke:opacity-100"
            :class="route.name === item.name ? 'scale-[1.4] opacity-100' : 'opacity-60'"
          />
          <span class="ml-1.5 text-xs font-light tracking-[0.06em] text-text-mid transition-colors group-hover/spoke:text-amber">{{ item.label }}</span>
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
.menu-enter-active, .menu-leave-active {
  transition: opacity 200ms ease;
}
.menu-enter-from, .menu-leave-to { opacity: 0; }
</style>
