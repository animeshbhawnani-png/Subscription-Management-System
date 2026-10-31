import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward /api/* to Django dev server — no CORS issues in development
      '/api': 'http://localhost:8000',
    },
  },
})

