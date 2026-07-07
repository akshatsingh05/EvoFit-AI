import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  build: {
    // Sourcemaps are useful in dev but shouldn't ship in the production
    // bundle (they expose original source and bloat the deploy artifact).
    sourcemap: false,
    // Split heavy, rarely-changing vendor code from app code so browsers
    // can cache it across deploys; keeps individual chunks smaller too.
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  },
})
