<template>
  <div id="app" :class="{ 'is-dark': uiStore.theme === 'dark' }">
    <!-- Global loading overlay -->
    <div v-if="uiStore.globalLoading" class="global-loading">
      <el-icon class="is-loading" :size="40">
        <Loading />
      </el-icon>
    </div>

    <!-- Router view -->
    <RouterView v-else />

    <!-- Global notification container -->
    <teleport to="body">
      <div class="notification-container">
        <!-- Element Plus handles notifications automatically -->
      </div>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onErrorCaptured } from 'vue'
import { useUiStore } from '@/stores/ui'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const uiStore = useUiStore()

// Capture component errors
onErrorCaptured((err: Error) => {
  console.error('Component error captured:', err)

  // Show error message to user
  ElMessage.error({
    message: err.message || 'An error occurred in this component',
    duration: 5000,
    showClose: true
  })

  // Return false to prevent error from propagating further
  return false
})

onMounted(() => {
  // Initialize theme on app mount
  uiStore.initializeTheme()
})
</script>

<style lang="scss">
#app {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  position: relative;
}

.is-dark {
  color-scheme: dark;
}

.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;

  .is-dark & {
    background-color: rgba(0, 0, 0, 0.9);
  }

  .el-icon {
    color: var(--el-color-primary);
  }
}

.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  pointer-events: none;
}

// Element Plus overrides
:deep(.el-message) {
  pointer-events: auto;
  box-shadow: var(--el-box-shadow-light);
}

:deep(.el-notification) {
  pointer-events: auto;
}
</style>
