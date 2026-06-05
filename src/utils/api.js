/** 轻量级 fetch 封装：自动附加 Authorization header。 */
export async function api(path, options = {}) {
  const token = localStorage.getItem('auth_token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(path, { ...options, headers })
  const data = await res.json().catch(() => ({
    ok: res.ok,
    error: res.statusText || '请求失败',
  }))
  const payload = { ...data, status: res.status }

  if (res.status === 401 && shouldRedirectToLogin(path)) {
    localStorage.removeItem('auth_token')
    const redirect = `${window.location.pathname}${window.location.search}${window.location.hash}`
    window.location.assign(`/login?redirect=${encodeURIComponent(redirect)}`)
  }

  return payload
}

/** 上传 Studio 图片，返回服务端 URL。FormData 请求不预设 Content-Type。 */
export async function uploadStudioImage(file) {
  const token = localStorage.getItem('auth_token')
  const form = new FormData()
  form.append('file', file)

  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch('/api/studio/images', { method: 'POST', headers, body: form })
  const data = await res.json().catch(() => ({
    ok: false,
    error: res.statusText || '图片上传失败',
  }))
  if (!res.ok || !data.ok) throw new Error(data.error || '图片上传失败')
  return data.data.url
}

function shouldRedirectToLogin(path) {
  if (typeof window === 'undefined') return false
  if (window.location.pathname === '/login') return false
  const value = String(path || '')
  return !value.startsWith('/api/auth/login')
    && !value.startsWith('/api/auth/register')
    && !value.startsWith('/api/auth/me')
}
