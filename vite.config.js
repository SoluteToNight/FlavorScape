import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '127.0.0.1',
    port: 3002,
    proxy: {
      '/api':   { target: 'http://127.0.0.1:8001', changeOrigin: true },
      '/tiles': { target: 'http://127.0.0.1:8001', changeOrigin: true },
    },
  },
  optimizeDeps: {
    include: ['maplibre-gl', 'echarts'],
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue':      ['vue', 'vue-router', 'pinia'],
          'vendor-maplibre': ['maplibre-gl'],
          'vendor-deckgl':   ['@deck.gl/core', '@deck.gl/layers', '@deck.gl/geo-layers', '@deck.gl/mapbox'],
          'vendor-echarts':  ['echarts'],
        },
      },
    },
  },
})
