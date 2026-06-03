import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/brand', name: 'brand', component: () => import('../views/BrandStoryView.vue') },
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
  if (to.meta.requiresAuth && !token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // 已登录用户访问登录/注册页 → 重定向到个人主页
  if (token && (to.name === 'login' || to.name === 'register')) {
    return { name: 'profile' }
  }

  return true
})

export default router
