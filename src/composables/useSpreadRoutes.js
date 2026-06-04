import { computed, reactive, ref } from 'vue'

const routes = ref([])
const details = reactive({})
const loading = ref(false)
const error = ref('')
let loaded = false

function sortTimeline(events = []) {
  return [...events]
    .filter(event => Array.isArray(event.coordinates))
    .sort((a, b) => Number(a.year || 0) - Number(b.year || 0))
}

export function routeEventKey(event, index = 0) {
  return String(event?.event_id || `${event?.year ?? 'origin'}-${event?.location || ''}-${index}`)
}

export function useSpreadRoutes() {
  async function loadRoutes() {
    if (loaded) return routes.value
    loading.value = true
    error.value = ''
    try {
      const res = await fetch('/api/ingredients/spread')
      if (!res.ok) throw new Error(`传播路径列表加载失败：${res.status}`)
      routes.value = await res.json()
      loaded = true
      return routes.value
    } catch (e) {
      error.value = e?.message || '传播路径列表加载失败'
      routes.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  async function loadRoute(id) {
    if (!id) return null
    if (details[id]) return details[id]
    loading.value = true
    error.value = ''
    try {
      const res = await fetch(`/api/ingredients/spread/${encodeURIComponent(id)}`)
      if (!res.ok) throw new Error(`传播路径加载失败：${res.status}`)
      const data = await res.json()
      details[id] = {
        ...data,
        timeline: sortTimeline(data.timeline),
      }
      return details[id]
    } catch (e) {
      error.value = e?.message || '传播路径加载失败'
      return null
    } finally {
      loading.value = false
    }
  }

  function getRoute(id) {
    return details[id] || null
  }

  const routeOptions = computed(() =>
    routes.value.map(item => ({
      id: item.ingredient_id,
      name: item.name,
      origin: item.origin,
      color: item.color || '#A96535',
      imageUrl: item.image_url,
      yearRange: item.year_range || [],
      eventCount: item.event_count || 0,
    }))
  )

  return {
    routes,
    routeOptions,
    loading,
    error,
    loadRoutes,
    loadRoute,
    getRoute,
  }
}
