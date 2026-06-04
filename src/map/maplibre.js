import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

export { maplibregl }

export function createMap(options) {
  return new maplibregl.Map(options)
}

export function addMapControls(map, controls = []) {
  if (!map) return

  controls.forEach(controlConfig => {
    if (!controlConfig) return

    const {
      type = 'navigation',
      position = 'bottom-right',
      options = {},
    } = controlConfig

    let control = controlConfig.control
    if (!control) {
      if (type === 'navigation') control = new maplibregl.NavigationControl(options)
      if (type === 'attribution') control = new maplibregl.AttributionControl(options)
    }

    if (control) map.addControl(control, position)
  })
}

export function removeMap(map) {
  if (!map) return
  map.remove()
}

export function fitBoundsFromCoordinates(map, coordinates, options = {}) {
  if (!map || !coordinates?.length) return null

  const bounds = coordinates.reduce(
    (acc, point) => acc.extend(point),
    new maplibregl.LngLatBounds(coordinates[0], coordinates[0]),
  )
  map.fitBounds(bounds, options)
  return bounds
}
