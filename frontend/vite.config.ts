import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import type { Plugin } from 'vite'

// Custom plugin to add health check endpoint
function healthCheckPlugin(): Plugin {
  return {
    name: 'health-check',
    configureServer(server) {
      server.middlewares.use('/health', (req, res) => {
        res.statusCode = 200
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify({
          status: 'healthy',
          service: 'visbuilder-frontend',
          timestamp: new Date().toISOString()
        }))
      })
    }
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    define: {
      __API_BASE_URL__: JSON.stringify(mode === 'production' ? '/api' : `${env.VITE_BACKEND_URL}/api`),
      __MAPBOX_TOKEN__: JSON.stringify(env.VITE_MAPBOX_ACCESS_TOKEN)
    },
    plugins: [react(), healthCheckPlugin()],
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