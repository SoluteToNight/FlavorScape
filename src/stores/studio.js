import { defineStore } from 'pinia'
import { reactive, computed } from 'vue'
import { useProductCases } from '../composables/useProductCases'

export const useStudioStore = defineStore('studio', () => {
  const { getById, loadAll } = useProductCases()

  // ── Project state (reactive for deep reactivity) ──
  const projects = reactive({})       // { [projectId]: ProjectState }
  let nextId = 1

  // ── Active project ID (use a ref wrapper inside reactive) ──
  const state = reactive({
    activeProjectId: null,
  })

  // ── Computed: active project ──
  const activeProject = computed(() => {
    if (!state.activeProjectId) return null
    return projects[state.activeProjectId] || null
  })

  // ── Computed: merged marketing data ──
  const mergedMarketingData = computed(() => {
    const p = activeProject.value
    if (!p) return null
    const product = getById(p.productId)
    if (!product) return null
    return {
      name: product.name,
      heroImage: p.marketing.customImage || product.heroImage,
      spatial: product.marketing.spatial,
      creative: {
        desc:       p.marketing.desc       ?? product.marketing.creative.desc.default,
        poeticLine: p.marketing.poeticLine ?? product.marketing.creative.poeticLine.default,
        narrative:  p.marketing.narrative  ?? product.marketing.creative.narrative.default,
        theme:      p.marketing.theme      ?? product.marketing.creative.theme.default,
        copy: {
          xiaohongshu: p.marketing.copy_xiaohongshu ?? product.marketing.creative.copy.xiaohongshu.default,
          ecommerce:   p.marketing.copy_ecommerce   ?? product.marketing.creative.copy.ecommerce.default,
        },
      },
    }
  })

  // ── Actions ──
  function createProject(productId, name) {
    const id = nextId++
    projects[id] = {
      id,
      name: name || '未命名项目',
      productId,
      activeOutput: 'poster',
      marketing: {
        desc: null, poeticLine: null, narrative: null, theme: 'nature',
        customImage: null, copy_xiaohongshu: null, copy_ecommerce: null,
      },
      archive: { flavorSummary: null, originDesc: null },
      display: { visibleNodeIds: null, cameraMode: 'tour', stageStories: {} },
      spread: { storySummary: null, brandStory: null },
      outputStatus: { poster: 'pending', archive: 'pending', display: 'pending', spread: 'skipped' },
    }
    state.activeProjectId = id
    return id
  }

  function updateCreative(module, field, value) {
    const p = activeProject.value
    if (!p) return
    p[module][field] = value
    // Auto-mark output as edited if status was pending
    if (module === 'marketing' && p.outputStatus.poster === 'pending') {
      p.outputStatus.poster = 'edited'
    }
  }

  function resetToDefault(module, field) {
    updateCreative(module, field, null)
  }

  function setActiveOutput(type) {
    if (activeProject.value) activeProject.value.activeOutput = type
  }

  function setOutputStatus(type, status) {
    if (activeProject.value) activeProject.value.outputStatus[type] = status
  }

  function switchProject(id) {
    state.activeProjectId = id
  }

  function hasAnyProject() {
    return Object.keys(projects).length > 0
  }

  // ── Ensure product cases are loaded when store initializes ──
  loadAll()

  return {
    state, projects, activeProject, mergedMarketingData,
    createProject, updateCreative, resetToDefault,
    setActiveOutput, setOutputStatus, switchProject, hasAnyProject,
  }
})
