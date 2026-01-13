/**
 * Component prop types for frontend
 */

import type { Character, DiscussionMessage, Discussion, DiscussionStatus, DiscussionPhase } from './models'

/**
 * Character card props
 */
export interface CharacterCardProps {
  character: Character
  isSelected?: boolean
  showRating?: boolean
  size?: 'small' | 'medium' | 'large'
}

/**
 * Message bubble props
 */
export interface MessageBubbleProps {
  message: DiscussionMessage
  isStreaming?: boolean
  highlightKeywords?: string[]
}

/**
 * Discussion controls props
 */
export interface DiscussionControlsProps {
  discussionId: string
  status: DiscussionStatus
  currentPhase: DiscussionPhase
  canInject?: boolean
}

/**
 * Notification item
 */
export interface NotificationItem {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  message: string
  duration?: number
}

/**
 * Modal props
 */
export interface ModalProps {
  visible: boolean
  title?: string
  width?: string | number
  confirmText?: string
  cancelText?: string
  showCancel?: boolean
}

/**
 * Pagination props
 */
export interface PaginationProps {
  page: number
  pageSize: number
  total: number
  pageSizes?: number[]
}
