<template>
  <div :class="['app-loading', `is-${size}`, `is-${type}`]">
    <div v-if="type === 'spinner'" class="loading-spinner">
      <div class="spinner-circle" />
    </div>

    <el-icon v-else-if="type === 'dots'" class="is-loading">
      <Loading />
    </el-icon>

    <el-icon v-else class="is-loading">
      <Loading />
    </el-icon>

    <div v-if="text" class="loading-text">
      {{ text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

interface Props {
  text?: string
  size?: 'small' | 'default' | 'large'
  type?: 'default' | 'spinner' | 'dots'
  fullscreen?: boolean
  background?: string
}

withDefaults(defineProps<Props>(), {
  size: 'default',
  type: 'default',
  fullscreen: false
})
</script>

<style scoped lang="scss">
.app-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;

  &.is-small {
    .el-icon {
      font-size: 20px;
    }

    .loading-text {
      font-size: 12px;
    }
  }

  &.is-large {
    .el-icon {
      font-size: 40px;
    }

    .loading-text {
      font-size: 16px;
    }
  }

  &.is-spinner {
    .loading-spinner {
      width: 40px;
      height: 40px;

      .spinner-circle {
        width: 100%;
        height: 100%;
        border: 3px solid var(--el-border-color-lighter);
        border-top-color: var(--el-color-primary);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }
    }
  }

  &.is-dots {
    .el-icon {
      animation: pulse 1.5s ease-in-out infinite;
    }
  }
}

.loading-text {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  text-align: center;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
