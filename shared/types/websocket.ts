/**
 * Shared type definitions for WebSocket events
 * Used by both frontend and backend
 */

import type { DiscussionStatus, DiscussionPhase } from './discussion'

/**
 * Server -> Client Events
 */
export interface ServerToClientEvents {
  // Connection confirmation
  connected: (data: {
    discussion_id: string
    status: DiscussionStatus
  }) => void

  // New character message (streaming)
  message: (data: {
    message_id: string
    character_id: string
    character_name: string
    content: string
    round: number
    phase: DiscussionPhase
    timestamp: string
    is_streaming: boolean
  }) => void

  // Message complete (final)
  message_complete: (data: {
    message_id: string
    token_count: number
  }) => void

  // Discussion status update
  status: (data: {
    status: DiscussionStatus
    current_round: number
    total_rounds: number
    current_phase: DiscussionPhase
    progress_percentage: number
  }) => void

  // Character thinking indicator
  character_thinking: (data: {
    character_id: string
    character_name: string
  }) => void

  // Error notification
  error: (data: {
    code: string
    message: string
    retryable: boolean
  }) => void

  // Pong response to heartbeat
  pong: () => void
}

/**
 * Client -> Server Events
 */
export interface ClientToServerEvents {
  // Subscribe to discussion updates
  subscribe: (data: { discussion_id: string }) => void

  // Control commands
  control: (data: {
    control_type: 'pause' | 'resume' | 'speed' | 'inject'
    speed?: 1.0 | 1.5 | 2.0 | 3.0
    question?: string
  }) => void

  // Heartbeat (client-side ping)
  ping: () => void
}

export type SocketEvents = ServerToClientEvents & ClientToServerEvents
