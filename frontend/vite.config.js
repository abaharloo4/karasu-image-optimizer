import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env variables
  const env = loadEnv(mode, process.cwd(), '')
  // Default to 127.0.0.1:5001 for host development, change to backend:5001 for docker compose
  let target = env.VITE_API_TARGET || 'http://127.0.0.1:5001'
  target = target.replace('localhost', '127.0.0.1')
  
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: target,
          changeOrigin: true,
        }
      }
    }
  }
})
