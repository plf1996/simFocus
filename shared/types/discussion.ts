/**
 * Shared type definitions for Discussion
 * Used by both frontend and backend
 */

export type DiscussionMode = 'free' | 'structured' | 'creative' | 'consensus'

export type DiscussionStatus =
  | 'initialized'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'cancelled'

export type DiscussionPhase = 'opening' | 'development' | 'debate' | 'closing'

/**
 * Discussion message
 */
export interface DiscussionMessage {
  id: string
  discussion_id: string
  participant_id: string
  character_name: string
  character_avatar?: string
  round: number
  phase: DiscussionPhase
  content: string
  token_count: number
  is_injected_question: boolean
  created_at: string
}

/**
 * Discussion participant
 */
export interface Participant {
  id: string
  character_id: string
  character_name: string
  character_avatar?: string
  position?: number
  stance?: 'pro' | 'con' | 'neutral'
  message_count: number
}
