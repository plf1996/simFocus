/**
 * Authentication Store
 * Manages user authentication state and actions
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LoginRequest, RegisterRequest, User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isEmailVerified = computed(() => user.value?.email_verified ?? false)

  // Actions
  async function login(credentials: LoginRequest) {
    isLoading.value = true
    try {
      // TODO: Implement actual API call
      // const response = await authApi.login(credentials)
      // token.value = response.access_token
      // refreshToken.value = response.refresh_token
      // await fetchUser()
    } finally {
      isLoading.value = false
    }
  }

  async function register(data: RegisterRequest) {
    isLoading.value = true
    try {
      // TODO: Implement actual API call
      // const response = await authApi.register(data)
      // token.value = response.access_token
      // refreshToken.value = response.refresh_token
      // await fetchUser()
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    // TODO: Implement actual API call
    // const response = await authApi.getCurrentUser()
    // user.value = response
  }

  async function logout() {
    try {
      // TODO: Implement actual API call
      // await authApi.logout()
    } finally {
      user.value = null
      token.value = null
      refreshToken.value = null
      localStorage.removeItem('auth-storage')
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) throw new Error('No refresh token')
    // TODO: Implement actual API call
    // const response = await authApi.refreshToken({ refresh_token: refreshToken.value })
    // token.value = response.access_token
    // refreshToken.value = response.refresh_token
    // return response.access_token
    return ''
  }

  // Initialize from storage
  function initialize() {
    const stored = localStorage.getItem('auth-storage')
    if (stored) {
      const { token: storedToken, user: storedUser } = JSON.parse(stored)
      token.value = storedToken
      user.value = storedUser
    }
  }

  return {
    // State
    user,
    token,
    refreshToken,
    isLoading,
    // Computed
    isAuthenticated,
    isEmailVerified,
    // Actions
    login,
    register,
    fetchUser,
    logout,
    refreshAccessToken,
    initialize
  }
}, {
  persist: {
    key: 'auth-storage',
    storage: localStorage,
    paths: ['user', 'token', 'refreshToken']
  }
})
