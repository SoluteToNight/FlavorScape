import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/map', name: 'map', component: () => import('../views/MapView.vue') },
  { path: '/library', name: 'library', component: () => import('../views/LibraryView.vue') },
  { path: '/narrative', name: 'narrative', component: () => import('../views/NarrativeView.vue') },
  { path: '/about', name: 'about', component: () => import('../views/AboutView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
