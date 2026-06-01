import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    flavors: [],
    selectedNode: null,
    selectedRoute: null,
    selectedEcozone: null,
    currentChapter: 0,
    searchQuery: '',
    layerVisibility: {
      L0: true,  // base layer (raster/hypsometry)
      L1: true,  // ecoregions / geographic segmentation
      L2: false, // route lines + trips (context-driven)
      L3: true,  // nodes / scatter points
    },
    layerEnabled: {
      L0: true,
      L1: true,
      L2: true,
      L3: true,
    },
    l1Emphasis: false,
    activeIngredientId: null,
    spreadTimelineYear: null,
  }),
  actions: {
    setFlavors(list) {
      this.flavors = Array.isArray(list) ? list : []
    },
    selectNode(node) {
      this.selectedNode = node
      this.selectedRoute = null
      this.selectedEcozone = null
      this.layerVisibility.L2 = true
      this.l1Emphasis = false
    },
    selectRoute(route) {
      this.selectedRoute = route
      this.selectedNode = null
      this.selectedEcozone = null
      this.layerVisibility.L2 = true
      this.l1Emphasis = false
    },
    selectEcozone(props) {
      this.selectedEcozone = props
      this.selectedNode = null
      this.selectedRoute = null
      this.layerVisibility.L2 = false
      this.l1Emphasis = true
    },
    clearSelection() {
      this.selectedNode = null
      this.selectedRoute = null
      this.selectedEcozone = null
      this.layerVisibility.L2 = false
      this.l1Emphasis = false
    },
    setChapter(idx) {
      this.currentChapter = idx
    },
    setLayerVisibility(layer, visible) {
      if (layer in this.layerVisibility) {
        this.layerVisibility[layer] = !!visible
      }
    },
    setLayerEnabled(layer, enabled) {
      if (layer in this.layerEnabled) {
        this.layerEnabled[layer] = !!enabled
      }
    },
    resetLayerVisibility() {
      this.layerVisibility.L0 = true
      this.layerVisibility.L1 = true
      this.layerVisibility.L2 = false
      this.layerVisibility.L3 = true
      this.layerEnabled.L0 = true
      this.layerEnabled.L1 = true
      this.layerEnabled.L2 = true
      this.layerEnabled.L3 = true
      this.l1Emphasis = false
    },
    setL1Emphasis(on) {
      this.l1Emphasis = !!on
    },
    resetL1Emphasis() {
      this.l1Emphasis = false
    },
    setActiveIngredient(id) {
      this.activeIngredientId = id
    },
    setSpreadTimelineYear(year) {
      this.spreadTimelineYear = year
    },
  },
})
