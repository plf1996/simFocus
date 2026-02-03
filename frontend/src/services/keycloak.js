/**
 * Keycloak OIDC 认证服务
 *
 * 支持两种认证模式：
 * 1. 后端代理模式（推荐）: 通过后端进行认证流程
 * 2. 前端直接模式: 前端直接与 Keycloak 交互
 *
 * 前后端接口一致性：
 * - 后端回调: /api/auth/keycloak/callback
 * - 前端成功页面: /auth/success?token={access_token}
 * - 前端回调页面: /auth/callback
 */

import Keycloak from 'keycloak-js'
import keycloakConfig, { getBackendAuthUrl, isBackendProxyMode, getAuthMode } from '@/config/keycloak'

class KeycloakService {
  constructor() {
    this.keycloak = null
    this.authMode = 'backend-proxy'
    this.isAuthenticated = false
    this.token = null
    this.refreshToken = null
    this.userProfile = null
    this.tokenRefreshInterval = null
    this.initialized = false
  }

  /**
   * 初始化 Keycloak
   */
  async init() {
    if (this.initialized) {
      return true
    }

    this.authMode = getAuthMode()

    if (this.authMode === 'frontend-direct') {
      return await this._initFrontendDirect()
    } else {
      // 后端代理模式不需要初始化 Keycloak 实例
      this.initialized = true
      return true
    }
  }

  /**
   * 前端直接模式初始化
   */
  async _initFrontendDirect() {
    try {
      this.keycloak = Keycloak({
        url: keycloakConfig.url,
        realm: keycloakConfig.realm,
        clientId: keycloakConfig.clientId,
      })

      const authenticated = await this.keycloak.init({
        onLoad: keycloakConfig.onLoad,
        checkLoginIframe: keycloakConfig.checkLoginIframe,
        checkLoginIframeInterval: keycloakConfig.checkLoginIframeInterval,
        redirectUri: keycloakConfig.redirectUri,
        silentCheckSsoRedirectUri: keycloakConfig.silentCheckSsoRedirectUri,
        responseMode: keycloakConfig.responseMode,
        flow: keycloakConfig.flow,
        scope: keycloakConfig.scope,
      })

      this.isAuthenticated = authenticated

      if (authenticated) {
        this.token = this.keycloak.token
        this.refreshToken = this.keycloak.refreshToken
        this.userProfile = await this.loadUserProfile()

        // 启动 token 自动刷新
        this._startTokenRefresh()

        // 设置 token 到 localStorage（用于 API 请求）
        localStorage.setItem('token', this.token)
      }

      this.initialized = true
      return authenticated
    } catch (error) {
      console.error('Keycloak initialization failed:', error)
      this.initialized = true
      return false
    }
  }

  /**
   * 后端代理模式登录
   *
   * 流程：
   * 1. 前端访问后端的 /api/auth/keycloak/login
   * 2. 后端重定向到 Keycloak
   * 3. 用户在 Keycloak 登录
   * 4. Keycloak 回调到后端的 /api/auth/keycloak/callback
   * 5. 后端处理并重定向到前端的 /auth/success
   */
  loginBackendProxy() {
    // 重定向到后端的 Keycloak 登录端点
    const loginUrl = getBackendAuthUrl()
    window.location.href = loginUrl
  }

  /**
   * 前端直接模式登录
   */
  loginFrontendDirect() {
    if (!this.keycloak) {
      console.error('Keycloak not initialized')
      return
    }

    this.keycloak.login({
      redirectUri: keycloakConfig.redirectUri,
      scope: keycloakConfig.scope,
    })
  }

  /**
   * 登录（根据模式自动选择）
   */
  login() {
    if (this.authMode === 'frontend-direct') {
      this.loginFrontendDirect()
    } else {
      this.loginBackendProxy()
    }
  }

  /**
   * 退出登录
   */
  async logout() {
    // 停止 token 刷新
    this._stopTokenRefresh()

    if (this.authMode === 'frontend-direct' && this.keycloak) {
      // 前端直接模式：从 Keycloak 登出
      await this.keycloak.logout({
        redirectUri: window.location.origin + '/login',
      })
    } else {
      // 后端代理模式：从后端登出
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          await fetch(`${keycloakConfig.apiBaseUrl}/api/auth/keycloak/logout`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh_token: refreshToken }),
          })
        }
      } catch (error) {
        console.error('Backend logout error:', error)
      }

      // 清除本地状态
      this._clearLocalAuth()
    }
  }

  /**
   * 处理后端回调成功
   *
   * 当后端处理完 Keycloak 回调后，会重定向到这里
   * URL 格式: /auth/success?token={access_token}
   */
  handleBackendCallbackSuccess(token) {
    this.token = token
    this.isAuthenticated = true

    // 存储 token
    localStorage.setItem('token', token)

    // 获取用户信息
    this._fetchUserProfileWithToken(token)

    return this.token
  }

  /**
   * 使用 token 获取用户信息
   */
  async _fetchUserProfileWithToken(token) {
    try {
      const response = await fetch(`${keycloakConfig.apiBaseUrl}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        this.userProfile = await response.json()
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
    }
  }

  /**
   * 加载用户资料（前端直接模式）
   */
  async loadUserProfile() {
    if (!this.keycloak) {
      return null
    }

    try {
      const profile = await this.keycloak.loadUserProfile()
      this.userProfile = profile
      return profile
    } catch (error) {
      console.error('Failed to load user profile:', error)
      return null
    }
  }

  /**
   * 刷新 token
   */
  async updateToken(minValidity = 5) {
    if (this.authMode === 'frontend-direct' && this.keycloak) {
      try {
        const refreshed = await this.keycloak.updateToken(minValidity)
        if (refreshed) {
          this.token = this.keycloak.token
          this.refreshToken = this.keycloak.refreshToken
          localStorage.setItem('token', this.token)
        }
        return refreshed
      } catch (error) {
        console.error('Failed to refresh token:', error)
        this.isAuthenticated = false
        return false
      }
    } else if (this.authMode === 'backend-proxy') {
      // 后端代理模式：调用后端的刷新端点
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          return false
        }

        const response = await fetch(`${keycloakConfig.apiBaseUrl}/api/auth/keycloak/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })

        if (response.ok) {
          const data = await response.json()
          this.token = data.access_token
          if (data.refresh_token) {
            this.refreshToken = data.refresh_token
            localStorage.setItem('refresh_token', data.refresh_token)
          }
          localStorage.setItem('token', this.token)
          return true
        }

        return false
      } catch (error) {
        console.error('Backend token refresh error:', error)
        return false
      }
    }

    return false
  }

  /**
   * 启动 token 自动刷新
   */
  _startTokenRefresh() {
    this._stopTokenRefresh()

    this.tokenRefreshInterval = setInterval(async () => {
      if (this.isAuthenticated) {
        await this.updateToken(keycloakConfig.tokenRefreshInterval)
      }
    }, keycloakConfig.tokenRefreshInterval * 1000)
  }

  /**
   * 停止 token 自动刷新
   */
  _stopTokenRefresh() {
    if (this.tokenRefreshInterval) {
      clearInterval(this.tokenRefreshInterval)
      this.tokenRefreshInterval = null
    }
  }

  /**
   * 清除本地认证状态
   */
  _clearLocalAuth() {
    this.token = null
    this.refreshToken = null
    this.userProfile = null
    this.isAuthenticated = false

    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
  }

  /**
   * 获取当前 token
   */
  getToken() {
    return this.token
  }

  /**
   * 获取用户信息
   */
  getUserProfile() {
    return this.userProfile
  }

  /**
   * 检查是否已认证
   */
  isLoggedIn() {
    return this.isAuthenticated
  }

  /**
   * 检查是否使用前端直接模式
   */
  isFrontendDirectMode() {
    return this.authMode === 'frontend-direct'
  }

  /**
   * 检查是否使用后端代理模式
   */
  isBackendProxyMode() {
    return this.authMode === 'backend-proxy'
  }

  /**
   * 获取 Keycloak 实例（前端直接模式）
   */
  getKeycloakInstance() {
    return this.keycloak
  }
}

// 创建单例
const keycloakService = new KeycloakService()

export default keycloakService
