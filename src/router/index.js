import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/brand', name: 'brand', component: () => import('../views/GeoAtlasView.vue') }, // 智慧大屏 / 地理志
  { path: '/marketing', name: 'marketing', component: () => import('../views/MarketingView.vue') }, // 🌟 【新增】商业营销海报生成器
  { path: '/archive', name: 'archive', component: () => import('../views/ArchiveView.vue') },
  { path: '/map', name: 'map', component: () => import('../views/MapView.vue') },
  { path: '/library', name: 'library', component: () => import('../views/LibraryView.vue') },
  { path: '/narrative', name: 'narrative', component: () => import('../views/NarrativeView.vue') },
  { path: '/spread', name: 'spread', component: () => import('../views/IngredientSpreadView.vue') },
  { path: '/about', name: 'about', component: () => import('../views/AboutView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
