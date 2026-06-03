import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../utils/api.js'

export const useAuthStore = defineStore('auth', () => {
  const user  = ref(null)
  const token = ref(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value)

  /** 页面加载时从 localStorage 恢复登录态，验证 token 有效性 */
  async function init() {
    const saved = localStorage.getItem('auth_token')
    if (!saved) return
    token.value = saved
    loading.value = true
    try {
      const res = await api('/api/auth/me')
      if (res.ok) {
        user.value = res.data.user
      } else {
        _clear()
      }
    } catch {
      _clear()
    } finally {
      loading.value = false
    }
  }

  async function login(username, password) {
    const res = await api('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    if (res.ok) {
      token.value = res.data.token
      user.value = res.data.user
      localStorage.setItem('auth_token', res.data.token)
    }
    return res
  }

  async function register(username, password) {
    const res = await api('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    if (res.ok) {
      token.value = res.data.token
      user.value = res.data.user
      localStorage.setItem('auth_token', res.data.token)
    }
    return res
  }

  function logout() {
    _clear()
  }

  function _clear() {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
  }

  return { user, token, loading, isLoggedIn, init, login, register, logout }
})
