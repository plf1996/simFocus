/**
 * Axios Instance & Configuration
 * Central HTTP client with interceptors for auth and error handling
 */

import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiError } from '@/types'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token from localStorage (auth store)
    const stored = localStorage.getItem('auth-storage')
    const token = stored ? JSON.parse(stored).token : null

    // Add auth token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Add request ID for tracing
    config.headers['X-Request-ID'] = generateRequestId()

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error: AxiosError<ApiError>) => {
    // Handle error
    if (error.response) {
      const { status, data } = error.response
      const errorMessage = data?.error?.message || 'An error occurred'

      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          localStorage.removeItem('auth-storage')
          window.location.href = '/login'
          break

        case 403:
          showErrorNotification('You do not have permission to perform this action')
          break

        case 404:
          showErrorNotification('Resource not found')
          break

        case 429:
          showErrorNotification('Too many requests. Please wait a moment.')
          break

        case 500:
        case 502:
        case 503:
        case 504:
          showErrorNotification('Server error. Please try again later.')
          break

        default:
          showErrorNotification(errorMessage)
      }
    } else if (error.request) {
      // Network error
      showErrorNotification('Network error. Please check your connection.')
    }

    return Promise.reject(error)
  }
)

// Utility: Generate request ID
function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// Utility: Show error notification
function showErrorNotification(message: string) {
  // Use Element Plus message directly to avoid circular dependency
  if (typeof (window as any).ElMessage !== 'undefined') {
    ;(window as any).ElMessage.error(message)
  } else {
    console.error(message)
  }
}

export { api }
export default api
