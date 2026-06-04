import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/studio', name: 'studio', component: () => import('../views/StudioView.vue'), meta: { requiresAuth: true } },
  { path: '/brand', name: 'brand', component: () => import('../views/GeoAtlasView.vue') },
  { path: '/marketing', name: 'marketing', component: () => import('../views/MarketingView.vue') },
  { path: '/archive', name: 'archive', component: () => import('../views/ArchiveView.vue') },
  { path: '/import', name: 'import', component: () => import('../views/DemoImportView.vue') },
  { path: '/map', name: 'map', component: () => import('../views/MapView.vue') },
  { path: '/library', name: 'library', component: () => import('../views/LibraryView.vue') },
  { path: '/narrative', name: 'narrative', component: () => import('../views/NarrativeView.vue') },
  { path: '/spread', name: 'spread', component: () => import('../views/IngredientSpreadView.vue') },
  { path: '/about', name: 'about', component: () => import('../views/AboutView.vue') },
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  { path: '/register', name: 'register', component: () => import('../views/RegisterView.vue') },
  { path: '/profile', name: 'profile', component: () => import('../views/ProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../views/NotFoundView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('auth_token')
  const projectBrandView = to.name === 'brand' && typeof to.query.project === 'string' && to.query.project
  const needsAuth = to.meta.requiresAuth || projectBrandView

  if (needsAuth && !token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (token && (to.name === 'login' || to.name === 'register')) {
    return { name: 'profile' }
  }

  return true
})

export default router
