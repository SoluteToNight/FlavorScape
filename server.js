import express from 'express'
import cors from 'cors'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { createProxyMiddleware } from 'http-proxy-middleware'

const __dirname = dirname(fileURLToPath(import.meta.url))
const app = express()
const PORT = process.env.PORT || 3001

app.use(cors())
app.use(express.json())

// Proxy all /api/* and /tiles/* to FastAPI (port 8001)
const proxy = createProxyMiddleware({ target: 'http://localhost:8001', changeOrigin: true })
app.use('/api', proxy)
app.use('/tiles', proxy)

if (process.env.NODE_ENV === 'production') {
  app.use(express.static(join(__dirname, 'dist')))
  app.get('*', (req, res) => res.sendFile(join(__dirname, 'dist', 'index.html')))
}

app.listen(PORT, () => {
  console.log(`\x1b[32m✓\x1b[0m 寻味地理 → http://localhost:${PORT}`)
  console.log(`          /api/*  → FastAPI :8001`)
  console.log(`          /tiles/* → FastAPI :8001`)
})
