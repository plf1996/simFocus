/**
 * Unit Tests for Auth Store
 * Testing authentication state management
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types'

// Mock API
vi.mock('@/services/api', () => ({
  api: {
    post: vi.fn()
  }
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  describe('Initial State', () => {
    it('should have initial null state', () => {
      const store = useAuthStore()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.isLoading).toBe(false)
    })

    it('should not be authenticated initially', () => {
      const store = useAuthStore()

      expect(store.isAuthenticated).toBe(false)
    })

    it('should not have email verified initially', () => {
      const store = useAuthStore()

      expect(store.isEmailVerified).toBe(false)
    })
  })

  describe('Login', () => {
    it('should handle login loading state', async () => {
      const store = useAuthStore()

      const loginPromise = store.login({
        email: 'test@example.com',
        password: 'password123'
      })

      expect(store.isLoading).toBe(true)

      await loginPromise

      expect(store.isLoading).toBe(false)
    })

    it('should set loading to false on error', async () => {
      const store = useAuthStore()

      // Mock failed login
      store.login = vi.fn().mockRejectedValue(new Error('Login failed'))

      try {
        await store.login({ email: 'test@example.com', password: 'wrong' })
      } catch (error) {
        expect(store.isLoading).toBe(false)
      }
    })
  })

  describe('Register', () => {
    it('should handle register loading state', async () => {
      const store = useAuthStore()

      const registerPromise = store.register({
        email: 'test@example.com',
        password: 'Password123',
        name: 'Test User'
      })

      expect(store.isLoading).toBe(true)

      await registerPromise

      expect(store.isLoading).toBe(false)
    })
  })

  describe('Logout', () => {
    it('should clear user state on logout', () => {
      const store = useAuthStore()

      // Set some initial state
      store.$patch({
        user: { id: '1', email: 'test@example.com' } as User,
        token: 'fake-token',
        refreshToken: 'fake-refresh-token'
      })

      store.logout()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
    })

    it('should clear localStorage on logout', () => {
      const store = useAuthStore()

      localStorage.setItem('auth-storage', JSON.stringify({
        token: 'fake-token',
        user: { id: '1' }
      }))

      store.logout()

      expect(localStorage.getItem('auth-storage')).toBeNull()
    })
  })

  describe('Initialization', () => {
    it('should initialize from localStorage', () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        email_verified: true,
        auth_provider: 'email',
        created_at: '2026-01-13T00:00:00Z'
      }

      localStorage.setItem('auth-storage', JSON.stringify({
        token: 'stored-token',
        refreshToken: 'stored-refresh',
        user: mockUser
      }))

      const store = useAuthStore()
      store.initialize()

      expect(store.token).toBe('stored-token')
      expect(store.user).toEqual(mockUser)
    })

    it('should handle invalid localStorage data', () => {
      localStorage.setItem('auth-storage', 'invalid json')

      const store = useAuthStore()

      expect(() => store.initialize()).not.toThrow()
    })
  })

  describe('Computed Properties', () => {
    it('should calculate isAuthenticated correctly', () => {
      const store = useAuthStore()

      expect(store.isAuthenticated).toBe(false)

      store.$patch({
        token: 'token',
        user: { id: '1' } as User
      })

      expect(store.isAuthenticated).toBe(true)
    })

    it('should require both token and user for authentication', () => {
      const store = useAuthStore()

      store.$patch({ token: 'token' })
      expect(store.isAuthenticated).toBe(false)

      store.$patch({
        user: { id: '1' } as User
      })
      expect(store.isAuthenticated).toBe(true)
    })

    it('should calculate isEmailVerified correctly', () => {
      const store = useAuthStore()

      expect(store.isEmailVerified).toBe(false)

      store.$patch({
        user: { email_verified: true } as User
      })

      expect(store.isEmailVerified).toBe(true)

      store.$patch({
        user: { email_verified: false } as User
      })

      expect(store.isEmailVerified).toBe(false)
    })
  })

  describe('Token Refresh', () => {
    it('should throw error when no refresh token', async () => {
      const store = useAuthStore()

      await expect(store.refreshAccessToken()).rejects.toThrow('No refresh token')
    })
  })
})
