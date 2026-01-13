/**
 * Authentication Store
 * Manages user authentication state and actions
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LoginRequest, RegisterRequest, User } from '@/types'
import { api } from '@/services/api'
import { encryptApiKey, decryptApiKey, maskApiKey } from '@/utils/encryption'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const apiKeys = ref<Record<string, string>>({})
  const isLoading = ref(false)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isEmailVerified = computed(() => user.value?.email_verified ?? false)

  // Actions
  async function login(credentials: LoginRequest) {
    isLoading.value = true
    try {
      const response = await api.post('/auth/login', credentials)
      token.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      await fetchUser()
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function register(data: RegisterRequest) {
    isLoading.value = true
    try {
      const response = await api.post('/auth/register', data)
      token.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      await fetchUser()
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (error) {
      console.error('Fetch user failed:', error)
      throw error
    }
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      console.error('Logout API call failed:', error)
    } finally {
      user.value = null
      token.value = null
      refreshToken.value = null
      apiKeys.value = {}
      localStorage.removeItem('auth-storage')
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) throw new Error('No refresh token')
    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value
      })
      token.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      return response.data.access_token
    } catch (error) {
      console.error('Token refresh failed:', error)
      throw error
    }
  }

  /**
   * Store API key with encryption
   * @param provider - API provider name (e.g., 'openai', 'anthropic')
   * @param apiKey - Plain API key
   */
  function setApiKey(provider: string, apiKey: string) {
    const encryptedKey = encryptApiKey(apiKey)
    apiKeys.value = { ...apiKeys.value, [provider]: encryptedKey }
  }

  /**
   * Get decrypted API key
   * @param provider - API provider name
   * @returns Decrypted API key or null if not found
   */
  function getApiKey(provider: string): string | null {
    const encryptedKey = apiKeys.value[provider]
    if (!encryptedKey) return null
    try {
      return decryptApiKey(encryptedKey)
    } catch (error) {
      console.error(`Failed to decrypt API key for ${provider}:`, error)
      return null
    }
  }

  /**
   * Get masked API key for display
   * @param provider - API provider name
   * @returns Masked API key (e.g., 'sk-test••••••••')
   */
  function getMaskedApiKey(provider: string): string | null {
    const apiKey = getApiKey(provider)
    return apiKey ? maskApiKey(apiKey) : null
  }

  /**
   * Remove API key for a provider
   * @param provider - API provider name
   */
  function removeApiKey(provider: string) {
    const newKeys = { ...apiKeys.value }
    delete newKeys[provider]
    apiKeys.value = newKeys
  }

  /**
   * Check if API key exists for provider
   * @param provider - API provider name
   * @returns True if API key is stored
   */
  function hasApiKey(provider: string): boolean {
    return !!apiKeys.value[provider]
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
    apiKeys,
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
    setApiKey,
    getApiKey,
    getMaskedApiKey,
    removeApiKey,
    hasApiKey,
    initialize
  }
}, {
  persist: {
    key: 'auth-storage',
    storage: localStorage,
    paths: ['user', 'token', 'refreshToken', 'apiKeys']
  }
})
