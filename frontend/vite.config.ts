import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // This Proxy forwards any request starting with /api to your Docker backend
    proxy: {
      '/api': {
        // localhost for `npm run dev`; compose sets VITE_API_TARGET=http://api:8000
        target: process.env.VITE_API_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});