/** 轻量级 fetch 封装：自动附加 Authorization header。 */
export async function api(path, options = {}) {
  const token = localStorage.getItem('auth_token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(path, { ...options, headers })
  const data = await res.json()
  return data
}
