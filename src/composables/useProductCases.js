import { computed, ref } from 'vue'

const cases = ref([])
const loading = ref(false)
const error = ref(null)
let loaded = false

function normalizeCase(module) {
  return module?.default || module
}

export function useProductCases() {
  function loadAll() {
    if (loaded) return cases.value

    loading.value = true
    error.value = null

    try {
      const modules = import.meta.glob('@/data/product_cases/*.json', { eager: true })
      cases.value = Object.values(modules)
        .map(normalizeCase)
        .filter(Boolean)
        .sort((a, b) => String(a.name).localeCompare(String(b.name), 'zh-Hans-CN'))
      loaded = true
      return cases.value
    } catch (e) {
      error.value = e?.message || 'Failed to load product cases'
      cases.value = []
      loaded = false
      return []
    } finally {
      loading.value = false
    }
  }

  function getById(id) {
    if (!loaded) loadAll()
    return cases.value.find(c => c.id === id) || null
  }

  function getByCategory(category) {
    if (!loaded) loadAll()
    return cases.value.filter(c => c.category === category)
  }

  const categories = computed(() => {
    if (!loaded) loadAll()
    return [...new Set(cases.value.map(c => c.category).filter(Boolean))]
  })

  loadAll()

  return { cases, categories, loading, error, loadAll, getById, getByCategory }
}
