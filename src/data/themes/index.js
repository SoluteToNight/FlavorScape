const THEMES = {
  nature: {
    id: 'nature',
    name: '自然探索',
    canvas: {
      backgroundColor: '#ffffff',
      backgroundPattern: 'paper',
    },
    colors: {
      primary: '#2a4128',
      accent: '#708a68',
      bg: '#ffffff',
      paper: '#f4f5f2',
      text: '#333333',
      muted: 'rgba(51,51,51,0.68)',
      mapBaseFill: '#eef1eb',
      mapBaseStroke: 'rgba(0,0,0,0.08)',
      mapActiveFill: '#2a4128',
      mapActiveStroke: '#ffffff',
    },
    typography: {
      titleFont: '"Noto Sans SC", "PingFang SC", sans-serif',
      titleWeight: 700,
      titleSize: 36,
      bodyFont: '"Noto Sans SC", "PingFang SC", sans-serif',
      bodySize: 12,
      bodyLineHeight: 1.6,
      highlightColor: '#2a4128',
    },
  },
  heritage: {
    id: 'heritage',
    name: '古典传承',
    canvas: {
      backgroundColor: '#f6f3eb',
      backgroundPattern: 'grain',
    },
    colors: {
      primary: '#3c3127',
      accent: '#a1352a',
      bg: '#f6f3eb',
      paper: '#efe9dd',
      text: '#595045',
      muted: 'rgba(89,80,69,0.68)',
      mapBaseFill: '#eae3d5',
      mapBaseStroke: 'rgba(60,49,39,0.12)',
      mapActiveFill: '#3c3127',
      mapActiveStroke: '#a1352a',
    },
    typography: {
      titleFont: '"Noto Serif SC", "Songti SC", serif',
      titleWeight: 600,
      titleSize: 40,
      bodyFont: '"Noto Serif SC", "Songti SC", serif',
      bodySize: 12,
      bodyLineHeight: 1.7,
      highlightColor: '#a1352a',
    },
  },
  indigo: {
    id: 'indigo',
    name: '靛蓝拓印',
    canvas: {
      backgroundColor: '#10223d',
      backgroundPattern: 'cyanotype',
    },
    colors: {
      primary: '#ffffff',
      accent: '#a6c6d9',
      bg: '#10223d',
      paper: '#19335a',
      text: '#dbeafe',
      muted: 'rgba(219,234,254,0.66)',
      mapBaseFill: 'rgba(255,255,255,0.06)',
      mapBaseStroke: 'rgba(255,255,255,0.2)',
      mapActiveFill: '#ffffff',
      mapActiveStroke: '#10223d',
    },
    typography: {
      titleFont: '"Optima", "Noto Serif SC", serif',
      titleWeight: 700,
      titleSize: 38,
      bodyFont: '"Noto Sans SC", "PingFang SC", sans-serif',
      bodySize: 12,
      bodyLineHeight: 1.55,
      highlightColor: '#ffffff',
    },
  },
}

export const themeOptions = Object.values(THEMES).map(theme => ({
  id: theme.id,
  name: theme.name,
  swatch: `linear-gradient(135deg, ${theme.colors.bg} 0%, ${theme.colors.accent} 55%, ${theme.colors.primary} 100%)`,
}))

export function getTheme(id = 'nature', overrides = {}) {
  const base = THEMES[id] || THEMES.nature
  const theme = JSON.parse(JSON.stringify(base))
  Object.entries(overrides || {}).forEach(([path, value]) => {
    setToken(theme, path, value)
  })
  return theme
}

export function resolveToken(theme, ref, fallback = '') {
  if (!ref) return fallback
  return String(ref).split('.').reduce((acc, key) => acc?.[key], theme) ?? fallback
}

function setToken(target, path, value) {
  const keys = String(path).split('.')
  let cursor = target
  keys.slice(0, -1).forEach(key => {
    if (!cursor[key] || typeof cursor[key] !== 'object') cursor[key] = {}
    cursor = cursor[key]
  })
  cursor[keys[keys.length - 1]] = value
}

export default THEMES
