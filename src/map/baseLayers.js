const PHYSICAL_VECTOR_LAYERS = [
  { id: 'coastline', url: '/tiles/vector/coastline', type: 'line' },
  { id: 'rivers', url: '/tiles/vector/rivers', type: 'line' },
]

export function addGeoJsonLayer(map, { id, url, type, paint, layout, beforeId }) {
  if (!map || !id) return false

  if (!map.getSource(id)) {
    map.addSource(id, { type: 'geojson', data: url })
  }

  if (map.getLayer(id)) return false

  const layerSpec = { id, type, source: id }
  if (paint) layerSpec.paint = paint
  if (layout) layerSpec.layout = layout

  if (beforeId && map.getLayer(beforeId)) {
    map.addLayer(layerSpec, beforeId)
  } else {
    map.addLayer(layerSpec)
  }

  return true
}

export function addPhysicalVectorLayers(map, {
  coastlinePaint = { 'line-color': '#8A7560', 'line-width': 0.6, 'line-opacity': 0.65 },
  riversPaint = { 'line-color': '#5BA0B8', 'line-width': 0.4, 'line-opacity': 0.6 },
} = {}) {
  const paints = { coastline: coastlinePaint, rivers: riversPaint }

  for (const layer of PHYSICAL_VECTOR_LAYERS) {
    addGeoJsonLayer(map, {
      ...layer,
      paint: paints[layer.id],
    })
  }
}

export function addEcoregionLayer(map, {
  id = 'ecoregions',
  url = '/tiles/vector/ecoregions',
  paint = {},
  layout = null,
  beforeId = null,
} = {}) {
  return addGeoJsonLayer(map, {
    id,
    url,
    type: 'line',
    paint,
    layout,
    beforeId,
  })
}

export function setLayerVisibility(map, id, visible) {
  if (!map?.getLayer(id)) return false
  map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none')
  return true
}
