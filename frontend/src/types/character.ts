/**
 * Character configuration types for frontend
 */

import type { CharacterConfig } from '../../../shared/types'

// Re-export shared types
export type { CharacterConfig }

/**
 * Character form data
 */
export interface CharacterFormData {
  name: string
  avatar_url?: string
  config: CharacterConfig
  is_public?: boolean
}

/**
 * Character filter options
 */
export interface CharacterFilter {
  is_template?: boolean
  is_public?: boolean
  stance?: string
  profession?: string
  search?: string
}
