<template>
  <div class="auth-success-container">
    <!-- 模态框背景 -->
    <div class="modal-overlay" :class="{ 'show': showModal }">
      <div class="modal-content" :class="{ 'show': showModal }">
        <!-- 加载状态 -->
        <div v-if="loading" class="modal-body">
          <div class="spinner-wrapper">
            <div class="spinner"></div>
            <p>正在完成登录...</p>
          </div>
        </div>

        <!-- 成功状态 -->
        <div v-else-if="!error" class="modal-body">
          <div class="success-icon-wrapper">
            <svg class="success-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="12" fill="#10B981"/>
              <path d="M8 12L11 15L16 9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>登录成功</h3>
          <p class="subtitle">正在跳转到主页...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else class="modal-body">
          <div class="error-icon-wrapper">
            <svg class="error-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="12" fill="#EF4444"/>
              <path d="M8 8L16 16M16 8L8 16" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <h3>登录失败</h3>
          <p class="subtitle">{{ error }}</p>
          <button @click="goToLogin" class="btn btn-primary">返回登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref(null)
const showModal = ref(false)

onMounted(async () => {
  try {
    // 显示模态框
    setTimeout(() => {
      showModal.value = true
    }, 100)

    // 从 URL 参数获取 token
    const token = route.query.token

    if (!token) {
      error.value = '未收到认证令牌'
      loading.value = false
      return
    }

    // 处理 Keycloak 回调
    await authStore.handleKeycloakCallback(token)

    loading.value = false

    // 延迟后跳转到目标页面
    setTimeout(() => {
      const redirectTo = localStorage.getItem('redirect_after_login') || '/topics'
      localStorage.removeItem('redirect_after_login')
      router.push(redirectTo)
    }, 1500)

  } catch (err) {
    console.error('Auth success error:', err)
    error.value = err.message || '认证处理失败'
    loading.value = false
  }
})

const goToLogin = () => {
  showModal.value = false
  setTimeout(() => {
    router.push('/login')
  }, 300)
}
</script>

<style scoped>
.auth-success-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.modal-overlay.show {
  opacity: 1;
}

.modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  min-width: 320px;
  max-width: 400px;
  transform: scale(0.9);
  transition: transform 0.3s ease;
}

.modal-content.show {
  transform: scale(1);
}

.modal-body {
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  text-align: center;
}

.spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.spinner {
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-radius: 50%;
  border-top: 4px solid #667eea;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.success-icon-wrapper,
.error-icon-wrapper {
  width: 64px;
  height: 64px;
}

.success-icon,
.error-icon {
  width: 100%;
  height: 100%;
}

h3 {
  margin: 0;
  color: #1f2937;
  font-size: 20px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}
</style>
