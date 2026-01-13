/**
 * Domain model types for frontend
 */

import type { CharacterConfig } from '../../../shared/types'
import type { DiscussionMode, DiscussionStatus, DiscussionPhase } from '../../../shared/types'

/**
 * User model
 */
export interface User {
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
 * Topic model
 */
export interface Topic {
  id: string
  user_id: string
  title: string
  description?: string
  context?: string
  attachments?: Attachment[]
  status: TopicStatus
  created_at: string
  updated_at: string
}

export interface Attachment {
  id: string
  name: string
  url: string
  type: string
  size: number
}

export type TopicStatus = 'draft' | 'ready' | 'in_discussion' | 'completed'

/**
 * Character model
 */
export interface Character {
  id: string
  user_id?: string
  name: string
  avatar_url?: string
  is_template: boolean
  is_public: boolean
  config: CharacterConfig
  usage_count: number
  rating_avg?: number
  rating_count: number
  created_at: string
}

/**
 * Discussion model
 */
export interface Discussion {
  id: string
  topic_id: string
  user_id: string
  discussion_mode: DiscussionMode
  max_rounds: number
  status: DiscussionStatus
  current_round: number
  current_phase: DiscussionPhase
  llm_provider: string
  llm_model: string
  total_tokens_used: number
  estimated_cost_usd?: number
  started_at?: string
  completed_at?: string
  created_at: string
}

/**
 * Discussion create request
 */
export interface DiscussionCreate {
  topic_id: string
  character_ids: string[]
  discussion_mode: DiscussionMode
  max_rounds: number
  llm_provider: string
  llm_model: string
}

/**
 * Discussion detail
 */
export interface DiscussionDetail extends Discussion {
  topic: Topic
  participants: Participant[]
  messages: DiscussionMessage[]
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
 * Inject question request
 */
export interface InjectQuestionRequest {
  question: string
}
