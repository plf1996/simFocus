import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import keycloakService from '@/services/keycloak'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const authProvider = ref(localStorage.getItem('auth_provider') || 'local') // 'local' | 'keycloak'
  const isKeycloakEnabled = ref(import.meta.env.VITE_KEYCLOAK_ENABLED === 'true')

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 本地用户名密码登录
  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials)
      token.value = response.data.access_token
      user.value = response.data.user
      authProvider.value = 'local'
      localStorage.setItem('token', token.value)
      localStorage.setItem('auth_provider', 'local')
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      return response
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  // Keycloak SSO 登录
  const loginWithKeycloak = async () => {
    try {
      // 初始化 Keycloak 服务
      await keycloakService.init()

      // 调用 Keycloak 登录
      keycloakService.login()

      // 注意：实际认证流程是异步的
      // 用户会被重定向到 Keycloak，然后回调回来
      // 实际的 token 设置在 handleKeycloakCallback 中处理
    } catch (error) {
      console.error('Keycloak login error:', error)
      throw error
    }
  }

  // 处理 Keycloak 回调成功
  const handleKeycloakCallback = async (keycloakToken) => {
    try {
      token.value = keycloakToken
      authProvider.value = 'keycloak'
      localStorage.setItem('token', keycloakToken)
      localStorage.setItem('auth_provider', 'keycloak')
      api.defaults.headers.common['Authorization'] = `Bearer ${keycloakToken}`

      // 获取用户信息
      await fetchUser()

      return true
    } catch (error) {
      console.error('Keycloak callback error:', error)
      throw error
    }
  }

  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register', userData)
      // Auto-login after registration
      await login({ email: userData.email, password: userData.password })
      return response
    } catch (error) {
      console.error('Register error:', error)
      // Error is already formatted by api interceptor
      throw error
    }
  }

  const logout = async () => {
    // 如果是 Keycloak 认证，调用 Keycloak 登出
    if (authProvider.value === 'keycloak' && isKeycloakEnabled.value) {
      await keycloakService.logout()
    }

    user.value = null
    token.value = null
    authProvider.value = 'local'
    localStorage.removeItem('token')
    localStorage.removeItem('auth_provider')
    delete api.defaults.headers.common['Authorization']
  }

  const fetchUser = async () => {
    if (!token.value) return

    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (error) {
      console.error('Fetch user error:', error)
      logout()
    }
  }

  const updateUser = async (userData) => {
    try {
      const response = await api.patch('/users/me', userData)
      user.value = { ...user.value, ...response.data }
      return response
    } catch (error) {
      console.error('Update user error:', error)
      throw error
    }
  }

  // Initialize auth state
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    fetchUser()
  }

  return {
    user,
    token,
    authProvider,
    isKeycloakEnabled,
    isAuthenticated,
    login,
    loginWithKeycloak,
    handleKeycloakCallback,
    register,
    logout,
    fetchUser,
    updateUser
  }
})
