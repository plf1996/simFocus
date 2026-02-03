import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://backend:8000',
        ws: true
      }
    }
  },
  build: {
    // 生产构建配置
    sourcemap: false,  // 禁用 source maps（生产环境）
    minify: 'terser',   // 使用 terser 压缩（更彻底的混淆）
    rollupOptions: {
      output: {
        // 文件名 hash（缓存控制）
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]'
      }
    },
    // 代码分割优化
    chunkSizeWarningLimit: 1000
  }
})
