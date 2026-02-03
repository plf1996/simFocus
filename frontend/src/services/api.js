import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response

      if (status === 401 || status === 403) {
        // Unauthorized or Forbidden - clear token and redirect to login
        localStorage.removeItem('token')
        window.location.href = '/login'
      }

      // Return error response data
      return Promise.reject({
        status,
        message: data?.error?.message || data?.detail || '请求失败',
        code: data?.error?.code || 'UNKNOWN_ERROR'
      })
    } else if (error.request) {
      // Request made but no response received
      return Promise.reject({
        status: 0,
        message: '网络错误，请检查连接',
        code: 'NETWORK_ERROR'
      })
    } else {
      // Something happened in setting up the request
      return Promise.reject({
        status: 0,
        message: '请求配置错误',
        code: 'REQUEST_ERROR'
      })
    }
  }
)

export default api
