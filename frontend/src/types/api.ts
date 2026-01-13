/**
 * API request/response types for frontend
 */

import type {
  ApiResponse,
  PaginatedResponse,
  PaginationParams,
  ApiError
} from '../../../shared/types'

// Re-export shared types
export type { ApiResponse, PaginatedResponse, PaginationParams, ApiError }

/**
 * Login request
 */
export interface LoginRequest {
  email: string
  password: string
}

/**
 * Login response
 */
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

/**
 * Register request
 */
export interface RegisterRequest {
  email: string
  password: string
  name?: string
}

/**
 * Token refresh request
 */
export interface RefreshTokenRequest {
  refresh_token: string
}

/**
 * User response
 */
export interface UserResponse {
  id: string
  email: string
  name?: string
  avatar_url?: string
  bio?: string
  email_verified: boolean
  auth_provider: 'email' | 'google' | 'github'
  created_at: string
  last_login_at?: string
}

/**
 * API key configuration
 */
export interface ApiKeyConfig {
  id: string
  provider: 'openai' | 'anthropic' | 'custom'
  api_key: string
  model?: string
  base_url?: string
  is_default: boolean
  created_at: string
}

/**
 * API key create request
 */
export interface ApiKeyCreateRequest {
  provider: 'openai' | 'anthropic' | 'custom'
  api_key: string
  model?: string
  base_url?: string
  is_default?: boolean
}
