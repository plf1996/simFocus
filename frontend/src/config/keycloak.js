/**
 * Keycloak OIDC 配置
 *
 * 前后端接口一致性说明：
 * - Frontend Client: simfocus-frontend (用于前端认证)
 * - Backend Client: simfocus-backend (用于后端服务)
 * - Callback URL: 匹配后端的 /api/auth/keycloak/callback
 * - Frontend Redirect: 后端会重定向到 /auth/success?token={access_token}
 */

export const keycloakConfig = {
  // Keycloak 服务器配置
  url: import.meta.env.VITE_KEYCLOAK_SERVER_URL || 'https://keycloak.plfai.cn/',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'simfocus',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'simfocus-frontend',

  // SSL 配置
  sslRequired: 'external',

  // 认证流程配置
  // 使用 standard flow (授权码模式)
  flow: 'standard',

  // 回调 URL 配置
  // 注意：这些 URL 必须在 Keycloak Admin Console 中配置为 Valid Redirect URIs
  redirectUri: window.location.origin + '/auth/callback',
  silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',

  // Token 配置
  // token: 在 Keycloak 会话期间保持有效
  // refreshToken: 用于获取新的 access token
  // idToken: 用于身份验证
  onLoad: 'login-required',

  // Session 配置
  checkLoginIframe: true,
  checkLoginIframeInterval: 10,

  // Silent SSO 配置
  silentSsoError: true,

  // Response mode
  responseMode: 'query',

  // Scope
  scope: 'openid profile email',

  // Token 刷新配置
  tokenRefreshInterval: 30, // 秒

  // 配置后端回调 URL（用于后端到前端的重定向）
  // 后端处理完 Keycloak 回调后，会重定向到这个 URL
  backendCallbackPath: '/auth/success',

  // API 配置
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
}

/**
 * 获取完整的 Keycloak 认证 URL（后端代理模式）
 *
 * 当使用后端代理模式时，前端通过后端进行认证：
 * 1. 前端访问后端的 /api/auth/keycloak/login
 * 2. 后端重定向到 Keycloak
 * 3. 用户在 Keycloak 登录
 * 4. Keycloak 回调到后端的 /api/auth/keycloak/callback
 * 5. 后端处理并重定向到前端的 /auth/success
 */
export const getBackendAuthUrl = () => {
  return `${keycloakConfig.apiBaseUrl}/api/auth/keycloak/login`
}

/**
 * 获取前端直接认证 URL（前端直接模式）
 *
 * 当使用前端直接模式时，前端直接与 Keycloak 交互：
 * 1. 前端通过 keycloak-js 登录
 * 2. Keycloak 回调到前端的 /auth/callback
 * 3. 前端将 token 发送到后端验证
 */
export const getFrontendAuthUrl = () => {
  // 使用 keycloak-js 时，这个 URL 由库自动生成
  return null
}

/**
 * 检查是否使用后端代理模式
 *
 * 后端代理模式的优点：
 * - 后端可以同步用户信息到数据库
 * - 统一的 token 管理
 * - 更好的安全性
 */
export const isBackendProxyMode = () => {
  return import.meta.env.VITE_AUTH_MODE === 'backend-proxy'
}

/**
 * 获取认证模式
 */
export const getAuthMode = () => {
  return import.meta.env.VITE_AUTH_MODE || 'backend-proxy' // 'backend-proxy' | 'frontend-direct'
}

export default keycloakConfig
