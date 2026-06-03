import { ref } from 'vue'

export function useProductCases() {
  const cases = ref([])
  const loading = ref(false)
  const error = ref(null)

  function loadAll() {
    // Return cached data immediately on subsequent calls
    if (cases.value.length > 0) return cases.value

    loading.value = true
    error.value = null

    try {
      const modules = import.meta.glob('@/data/product_cases/*.json', { eager: true })
      const loaded = Object.entries(modules).map(([path, module]) => ({ ...module.default }))
      cases.value = loaded
      return loaded
    } catch (e) {
      error.value = e.message || 'Failed to load product cases'
      return []
    } finally {
      loading.value = false
    }
  }

  function getById(id) {
    return cases.value.find(c => c.id === id) || null
  }

  function getByCategory(cat) {
    return cases.value.filter(c => c.category === cat)
  }

  return { cases, loading, error, loadAll, getById, getByCategory }
}
