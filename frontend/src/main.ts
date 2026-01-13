import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
// Element Plus styles are now imported via auto-import
// Only import global styles explicitly
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import App from './App.vue'
import router from './router'

// Import global styles
import '@/assets/styles/main.scss'

// Create app instance
const app = createApp(App)

// Create pinia instance with persist plugin
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

// Register plugins
app.use(pinia)
app.use(router)
// Element Plus is now auto-imported via unplugin-vue-components
// No need to manually register the full library

// Register Element Plus icons globally
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  // Log error to console in development
  if (import.meta.env.DEV) {
    console.error('Global error:', err)
    console.error('Component:', instance)
    console.error('Error info:', info)
  }

  // Show user-friendly error message
  const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'

  // Don't show notification for certain errors
  if (!errorMessage.includes('resize observer') && !errorMessage.includes('network')) {
    ElMessage.error({
      message: errorMessage,
      duration: 5000,
      showClose: true
    })
  }

  // TODO: Send error to error tracking service (e.g., Sentry)
  // if (import.meta.env.PROD) {
  //   Sentry.captureException(err)
  // }
}

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)

  if (import.meta.env.PROD) {
    ElMessage.error({
      message: 'An unexpected error occurred. Please try again.',
      duration: 5000,
      showClose: true
    })
  }
})

// Handle global errors
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error)

  if (import.meta.env.PROD && event.error) {
    ElMessage.error({
      message: 'An unexpected error occurred. Please refresh the page.',
      duration: 5000,
      showClose: true
    })
  }
})

// Mount app
app.mount('#app')
