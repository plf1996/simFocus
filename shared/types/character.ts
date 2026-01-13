/**
 * Shared type definitions for Character
 * Used by both frontend and backend
 */

/**
 * Character configuration
 */
export interface CharacterConfig {
  age: number
  gender: Gender
  profession: string
  personality: PersonalityTraits
  knowledge: KnowledgeBackground
  stance: DiscussionStance
  expression_style: ExpressionStyle
  behavior_pattern: BehaviorPattern
}

export type Gender = 'male' | 'female' | 'other' | 'prefer_not_to_say'

export interface PersonalityTraits {
  openness: number // 1-10
  rigor: number // 1-10
  critical_thinking: number // 1-10
  optimism: number // 1-10
}

export interface KnowledgeBackground {
  fields: string[]
  experience_years: number
  representative_views: string[]
}

export type DiscussionStance =
  | 'support'
  | 'oppose'
  | 'neutral'
  | 'critical_exploration'

export type ExpressionStyle = 'formal' | 'casual' | 'technical' | 'storytelling'

export type BehaviorPattern = 'active' | 'passive' | 'balanced'
