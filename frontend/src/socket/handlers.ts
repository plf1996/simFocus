/**
 * Socket Event Handlers
 * Setup handlers for discussion WebSocket events
 */

import { socketClient } from './client'
import type { ServerToClientEvents, ClientToServerEvents } from '@/types'
import { useMessageStore } from '@/stores/message'
import { useDiscussionStore } from '@/stores/discussion'
import { useUiStore } from '@/stores/ui'

export function setupDiscussionHandlers(discussionId: string) {
  const socket = socketClient.connect(discussionId)
  const messageStore = useMessageStore()
  const discussionStore = useDiscussionStore()
  const uiStore = useUiStore()

  // Connection established
  socket.on('connected', (data: ServerToClientEvents['connected']) => {
    console.log('Connected to discussion:', data.discussion_id)
    discussionStore.updateActiveDiscussion({ status: data.status })
  })

  // New message (streaming)
  socket.on('message', (data: ServerToClientEvents['message']) => {
    if (data.is_streaming) {
      // Update streaming content
      messageStore.updateStreamingMessage(data.message_id, data.content)
    } else {
      // Add complete message
      messageStore.addMessage(discussionId, {
        id: data.message_id,
        discussion_id: discussionId,
        participant_id: data.character_id,
        character_name: data.character_name,
        round: data.round,
        phase: data.phase,
        content: data.content,
        token_count: 0, // Will be updated in message_complete
        is_injected_question: false,
        created_at: data.timestamp
      })
    }
  })

  // Message complete
  socket.on('message_complete', (data: ServerToClientEvents['message_complete']) => {
    messageStore.completeStreamingMessage(
      data.message_id,
      messageStore.getStreamingMessage(data.message_id)
    )
  })

  // Status update
  socket.on('status', (data: ServerToClientEvents['status']) => {
    discussionStore.updateActiveDiscussion({
      status: data.status,
      current_round: data.current_round,
      current_phase: data.current_phase
    })
  })

  // Character thinking indicator
  socket.on('character_thinking', (data: ServerToClientEvents['character_thinking']) => {
    messageStore.setTyping(data.character_id, true)
    // Clear typing indicator after 3 seconds
    setTimeout(() => {
      messageStore.setTyping(data.character_id, false)
    }, 3000)
  })

  // Error
  socket.on('error', (data: ServerToClientEvents['error']) => {
    uiStore.showNotification({
      type: 'error',
      message: data.message,
      duration: data.retryable ? 3000 : 0
    })
  })

  // Cleanup function
  return () => {
    socket.off('connected')
    socket.off('message')
    socket.off('message_complete')
    socket.off('status')
    socket.off('character_thinking')
    socket.off('error')
  }
}

export function sendControlCommand(
  command: 'pause' | 'resume' | 'speed' | 'inject',
  params?: { speed?: number; question?: string }
) {
  socketClient.emit('control', {
    control_type: command,
    ...params
  })
}

// Heartbeat for connection health
let heartbeatInterval: number | null = null

export function startHeartbeat() {
  heartbeatInterval = window.setInterval(() => {
    if (socketClient.isConnected()) {
      socketClient.emit('ping')
    }
  }, 30000) // Every 30 seconds
}

export function stopHeartbeat() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }
}
