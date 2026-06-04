export function createHypRasterStyle({
  backgroundColor = '#C8DDE8',
  backgroundLayerId = 'bg',
  projection = null,
  rasterPaint = {},
  rasterSource = {},
  sky = null,
} = {}) {
  const style = {
    version: 8,
    sources: {
      'hyp-tiles': {
        type: 'raster',
        tiles: ['/tiles/raster/{z}/{x}/{y}.png'],
        tileSize: 256,
        minzoom: 0,
        maxzoom: 8,
        ...rasterSource,
      },
    },
    layers: [
      {
        id: backgroundLayerId,
        type: 'background',
        paint: { 'background-color': backgroundColor },
      },
      {
        id: 'hyp',
        type: 'raster',
        source: 'hyp-tiles',
        paint: rasterPaint,
      },
    ],
  }

  if (projection) style.projection = projection
  if (sky) style.sky = sky

  return style
}
