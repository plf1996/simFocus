/**
 * Shared type definitions for API
 * Used by both frontend and backend
 */

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T
  message?: string
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page?: number
  size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

/**
 * API error response
 */
export interface ApiError {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
    request_id?: string
    timestamp?: string
  }
}
