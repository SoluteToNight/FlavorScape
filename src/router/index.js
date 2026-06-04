import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/studio', name: 'studio', component: () => import('../views/StudioView.vue'), meta: { requiresAuth: true } },
  { path: '/brand', name: 'brand', component: () => import('../views/GeoAtlasView.vue') }, // 智慧大屏 / 地理志
  { path: '/marketing', name: 'marketing', component: () => import('../views/MarketingView.vue') }, // 🌟 【新增】商业营销海报生成器
  { path: '/archive', name: 'archive', component: () => import('../views/ArchiveView.vue') },
  { path: '/map', name: 'map', component: () => import('../views/MapView.vue') },
  { path: '/library', name: 'library', component: () => import('../views/LibraryView.vue') },
  { path: '/narrative', name: 'narrative', component: () => import('../views/NarrativeView.vue') },
  { path: '/spread', name: 'spread', component: () => import('../views/IngredientSpreadView.vue') },
  { path: '/about', name: 'about', component: () => import('../views/AboutView.vue') },
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  { path: '/register', name: 'register', component: () => import('../views/RegisterView.vue') },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../views/NotFoundView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局导航守卫
router.beforeEach((to, _from) => {
  const token = localStorage.getItem('auth_token')

  // 需要登录的页面 → 未登录则重定向到登录页
  const needsAuth = to.meta.requiresAuth || (to.name === 'brand' && typeof to.query.project === 'string' && to.query.project)

  if (needsAuth && !token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // 已登录用户访问登录/注册页 → 重定向到个人主页
  if (token && (to.name === 'login' || to.name === 'register')) {
    return { name: 'profile' }
  }

  return true
})

export default router
