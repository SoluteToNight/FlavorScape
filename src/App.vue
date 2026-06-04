<template>
  <div class="app-root">
    <Navbar />
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="route.name" />
      </Transition>
    </RouterView>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import { useAuthStore } from './stores/auth.js'

const route = useRoute()
const authStore = useAuthStore()

onMounted(() => {
  authStore.init()
})
</script>

<style scoped>
.app-root {
  width: 100%;
  min-height: 100%;
  position: relative;
  overflow-x: hidden;
}
</style>
