import { readFileSync } from 'fs'
import path from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const pkg = JSON.parse(readFileSync(path.resolve(__dirname, 'package.json'), 'utf-8')) as { version: string }

const viteBase = process.env.VITE_BASE || '/'
const normalizedBase = viteBase.startsWith('/') ? viteBase : `/${viteBase}`

export default defineConfig({
  base: normalizedBase.endsWith('/') ? normalizedBase : `${normalizedBase}/`,
  define: {
    'import.meta.env.VITE_APP_VERSION': JSON.stringify(pkg.version),
  },
  plugins: [react()],
  publicDir: 'static',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000/',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8000/',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
  },
})
