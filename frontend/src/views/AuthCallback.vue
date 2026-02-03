<template>
  <div class="auth-callback">
    <div class="loading-container">
      <div class="spinner"></div>
      <p>正在处理认证回调...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import keycloakService from '@/services/keycloak'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(async () => {
  try {
    // 检查是否使用前端直接模式
    if (keycloakService.isFrontendDirectMode()) {
      // 前端直接模式：keycloak-js 会自动处理回调
      // 我们只需要初始化并等待认证完成
      const authenticated = await keycloakService.init()

      if (authenticated) {
        const token = keycloakService.getToken()
        await authStore.handleKeycloakCallback(token)

        // 重定向到目标页面或首页
        const redirectTo = route.query.redirect || '/topics'
        router.push(redirectTo)
      } else {
        // 认证失败，重定向到登录页
        router.push('/login?error=auth_failed')
      }
    } else {
      // 后端代理模式：不应该到达这个页面
      // 如果到达这里，说明配置错误
      console.error('AuthCallback reached in backend-proxy mode')
      router.push('/login?error=invalid_mode')
    }
  } catch (error) {
    console.error('Auth callback error:', error)
    router.push('/login?error=callback_error')
  }
})
</script>

<style scoped>
.auth-callback {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.loading-container {
  text-align: center;
  color: white;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 4px solid white;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

p {
  font-size: 1.1rem;
  margin: 0;
}
</style>
