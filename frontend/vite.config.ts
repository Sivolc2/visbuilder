import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    define: {
      __API_BASE_URL__: JSON.stringify(mode === 'production' ? '/api' : `${env.VITE_BACKEND_URL}/api`),
      __MAPBOX_TOKEN__: JSON.stringify(env.VITE_MAPBOX_ACCESS_TOKEN)
    },
    plugins: [react()],
    server: {
      port: 3000,
      open: true,
      proxy: mode === 'development' ? {
        '/api': {
          target: env.VITE_BACKEND_URL || 'http://localhost:5003',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      } : undefined
    }
  }
}) 