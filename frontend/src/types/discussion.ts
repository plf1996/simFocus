/**
 * Discussion state types for frontend
 */

import type {
  DiscussionMode,
  DiscussionStatus,
  DiscussionPhase,
  DiscussionMessage,
  Participant
} from '../../../shared/types'

// Re-export shared types
export type {
  DiscussionMode,
  DiscussionStatus,
  DiscussionPhase,
  DiscussionMessage,
  Participant
}

/**
 * Discussion state for stores
 */
export interface DiscussionState {
  activeDiscussion: DiscussionDetail | null
  discussions: Discussion[]
  isLoading: boolean
  error: Error | null
}

/**
 * Discussion control commands
 */
export type DiscussionControl = 'pause' | 'resume' | 'speed' | 'inject'

/**
 * Discussion speed options
 */
export type DiscussionSpeed = 1.0 | 1.5 | 2.0 | 3.0
