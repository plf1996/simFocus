<template>
  <div class="error-boundary">
    <slot v-if="!hasError" />
    <div v-else class="error-fallback">
      <el-result icon="error" title="Something went wrong" :sub-title="errorMessage">
        <template #extra>
          <el-space>
            <el-button type="primary" @click="reload">Reload Page</el-button>
            <el-button @click="goHome">Go to Home</el-button>
            <el-button v-if="showDetails" link @click="toggleDetails">
              {{ showErrorDetails ? 'Hide' : 'Show' }} Details
            </el-button>
          </el-space>
          <el-collapse-transition>
            <el-alert
              v-if="showErrorDetails && errorDetails"
              class="error-details"
              type="error"
              :closable="false"
            >
              <pre class="error-stack">{{ errorDetails }}</pre>
            </el-alert>
          </el-collapse-transition>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured, computed } from 'vue'
import { useRouter } from 'vue-router'

interface Props {
  showDetails?: boolean
  onError?: (error: Error, instance: any, info: string) => void
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: true
})

const router = useRouter()
const hasError = ref(false)
const error = ref<Error | null>(null)
const errorInfo = ref('')
const showErrorDetails = ref(false)

const errorMessage = computed(() => {
  if (!error.value) return 'An unexpected error occurred'

  // User-friendly error messages
  const message = error.value.message.toLowerCase()

  if (message.includes('network') || message.includes('fetch')) {
    return 'Network error. Please check your connection and try again.'
  }
  if (message.includes('timeout')) {
    return 'Request timed out. Please try again.'
  }
  if (message.includes('unauthorized') || message.includes('401')) {
    return 'You are not authorized. Please log in again.'
  }
  if (message.includes('forbidden') || message.includes('403')) {
    return 'You do not have permission to access this resource.'
  }
  if (message.includes('not found') || message.includes('404')) {
    return 'The requested resource was not found.'
  }

  return error.value.message
})

const errorDetails = computed(() => {
  if (!error.value) return ''
  return `
Error: ${error.value.message}
Stack: ${error.value.stack}
Component Info: ${errorInfo.value}
  `.trim()
})

function toggleDetails() {
  showErrorDetails.value = !showErrorDetails.value
}

function reload() {
  window.location.reload()
}

function goHome() {
  hasError.value = false
  error.value = null
  errorInfo.value = ''
  router.push('/')
}

// Capture errors from descendant components
onErrorCaptured((err: Error, instance: any, info: string) => {
  console.error('ErrorBoundary caught an error:', err)
  console.error('Component instance:', instance)
  console.error('Error info:', info)

  hasError.value = true
  error.value = err
  errorInfo.value = info

  // Call custom error handler if provided
  if (props.onError) {
    props.onError(err, instance, info)
  }

  // Prevent error from propagating further
  return false
})

// Expose reset method for programmatic error clearing
function reset() {
  hasError.value = false
  error.value = null
  errorInfo.value = ''
  showErrorDetails.value = false
}

defineExpose({
  reset
})
</script>

<script lang="ts">
export default {
  name: 'AppErrorBoundary'
}
</script>

<style scoped lang="scss">
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 20px;

  .el-result {
    max-width: 600px;
    margin: 0 auto;
  }
}

.error-details {
  margin-top: 20px;
  text-align: left;

  .error-stack {
    margin: 0;
    padding: 12px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.5;
    color: #f56c6c;
    background-color: #fef0f0;
    border-radius: 4px;
    white-space: pre-wrap;
    word-break: break-all;
  }
}
</style>
