/**
 * Socket.IO Client
 * Manages WebSocket connection for real-time discussion updates
 * Features: Exponential backoff, heartbeat, state restoration, reconnection
 */

import { io, Socket } from 'socket.io-client'
import type { SocketEvents } from '@/types'

interface ConnectionState {
  discussionId: string | null
  isAuthenticated: boolean
  lastMessageTime: number
  reconnectCount: number
}

class SocketClient {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private baseReconnectDelay = 1000 // 1 second
  private maxReconnectDelay = 30000 // 30 seconds
  private heartbeatInterval: ReturnType<typeof setInterval> | null = null
  private heartbeatIntervalTime = 30000 // 30 seconds
  private connectionState: ConnectionState = {
    discussionId: null,
    isAuthenticated: false,
    lastMessageTime: 0,
    reconnectCount: 0
  }
  private manualDisconnect = false
  private eventHandlers: Map<string, Array<(...args: unknown[]) => void>> = new Map()

  connect(discussionId: string): Socket {
    // Prevent duplicate connections for same discussion
    if (this.socket?.connected && this.connectionState.discussionId === discussionId) {
      return this.socket
    }

    // Disconnect existing socket if different discussion
    if (this.socket?.connected) {
      this.disconnect()
    }

    // Get token from localStorage (auth store)
    const stored = localStorage.getItem('auth-storage')
    const token = stored ? JSON.parse(stored).token : null

    const wsUrl = import.meta.env.VITE_WS_BASE_URL || window.location.origin

    // Reset connection state
    this.connectionState = {
      discussionId,
      isAuthenticated: !!token,
      lastMessageTime: Date.now(),
      reconnectCount: 0
    }

    this.manualDisconnect = false
    this.reconnectAttempts = 0

    this.socket = io(`${wsUrl}/v1/ws/discussions/${discussionId}`, {
      auth: { token },
      reconnection: true,
      reconnectionDelay: this.calculateReconnectDelay(),
      reconnectionDelayMax: this.maxReconnectDelay,
      reconnectionAttempts: this.maxReconnectAttempts,
      timeout: 10000,
      transports: ['websocket', 'polling'],
      forceNew: true // Force new connection for each discussion
    })

    this.setupEventHandlers()
    this.startHeartbeat()

    return this.socket
  }

  /**
   * Calculate exponential backoff delay for reconnection
   * Uses exponential backoff: delay = base * 2^attempt
   */
  private calculateReconnectDelay(): number {
    const delay = Math.min(
      this.baseReconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    )
    // Add some jitter to prevent thundering herd
    return delay + Math.random() * 1000
  }

  /**
   * Setup WebSocket event handlers
   */
  private setupEventHandlers() {
    if (!this.socket) return

    // Connection established
    this.socket.on('connect', () => {
      console.log('WebSocket connected', {
        discussionId: this.connectionState.discussionId,
        attempt: this.reconnectAttempts
      })

      this.reconnectAttempts = 0
      this.connectionState.lastMessageTime = Date.now()

      // Restore event handlers after reconnection
      this.restoreEventHandlers()

      // Notify app about reconnection
      this.emitSystemEvent('reconnected', {
        attempt: this.connectionState.reconnectCount
      })
    })

    // Disconnection handling
    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)

      this.stopHeartbeat()

      // Server initiated disconnect - don't auto reconnect
      if (reason === 'io server disconnect') {
        this.manualDisconnect = true
        this.emitSystemEvent('server-disconnect', { reason })
      }

      // Client-side disconnect (network issue, etc.)
      if (!this.manualDisconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        this.connectionState.reconnectCount = this.reconnectAttempts

        const nextDelay = this.calculateReconnectDelay()
        console.log(`Reconnecting in ${(nextDelay / 1000).toFixed(1)}s (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

        this.emitSystemEvent('reconnecting', {
          attempt: this.reconnectAttempts,
          maxAttempts: this.maxReconnectAttempts,
          delay: nextDelay
        })
      }

      // Max reconnection attempts reached
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached')
        this.emitSystemEvent('reconnect-failed', {
          attempts: this.reconnectAttempts
        })
      }
    })

    // Connection error
    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error.message)

      this.emitSystemEvent('connection-error', {
        error: error.message,
        attempt: this.reconnectAttempts
      })

      // Show user notification for critical errors
      if (this.reconnectAttempts >= 3) {
        this.emitSystemEvent('show-notification', {
          type: 'warning',
          message: `Connection unstable. Retrying... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
        })
      }
    })

    // Ping/Pong for connection health
    this.socket.on('pong', (latency) => {
      this.connectionState.lastMessageTime = Date.now()
      console.debug('Pong received, latency:', latency, 'ms')
    })

    // Error from server
    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error)
      this.emitSystemEvent('socket-error', { error })
    })
  }

  /**
   * Start heartbeat mechanism to detect stale connections
   */
  private startHeartbeat() {
    this.stopHeartbeat() // Clear existing interval

    this.heartbeatInterval = setInterval(() => {
      if (this.socket?.connected) {
        // Send ping
        this.socket.emit('ping', Date.now())

        // Check for stale connection (no message for 60 seconds)
        const timeSinceLastMessage = Date.now() - this.connectionState.lastMessageTime
        if (timeSinceLastMessage > 60000) {
          console.warn('Connection appears stale, disconnecting...')
          this.socket.disconnect()
        }
      }
    }, this.heartbeatIntervalTime)
  }

  /**
   * Stop heartbeat mechanism
   */
  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * Store event handlers to restore after reconnection
   */
  private storeEventHandler(event: string, handler: (...args: unknown[]) => void) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, [])
    }
    this.eventHandlers.get(event)?.push(handler)
  }

  /**
   * Restore all event handlers after reconnection
   */
  private restoreEventHandlers() {
    if (!this.socket) return

    for (const [event, handlers] of this.eventHandlers.entries()) {
      for (const handler of handlers) {
        this.socket.on(event, handler)
      }
    }
  }

  /**
   * Emit system event for app-wide handling
   */
  private emitSystemEvent(event: string, data?: unknown) {
    // Import dynamically to avoid circular dependency
    import('@/stores/ui').then(({ useUiStore }) => {
      const uiStore = useUiStore()

      switch (event) {
        case 'show-notification':
          if (data && typeof data === 'object' && 'type' in data && 'message' in data) {
            uiStore.showNotification({
              type: data.type as 'success' | 'warning' | 'error' | 'info',
              message: String(data.message)
            })
          }
          break

        case 'reconnect-failed':
          uiStore.showNotification({
            type: 'error',
            message: 'Connection lost. Please refresh the page.',
            duration: 0 // Don't auto-dismiss
          })
          break

        default:
          // Emit custom event for components to listen to
          window.dispatchEvent(
            new CustomEvent(`socket:${event}`, {
              detail: data
            })
          )
      }
    })
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    this.manualDisconnect = true
    this.stopHeartbeat()
    this.socket?.disconnect()
    this.socket = null
    this.eventHandlers.clear()
    this.connectionState = {
      discussionId: null,
      isAuthenticated: false,
      lastMessageTime: 0,
      reconnectCount: 0
    }
    this.reconnectAttempts = 0
  }

  /**
   * Emit event to server
   */
  emit(event: string, data?: unknown) {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
      this.connectionState.lastMessageTime = Date.now()
    } else {
      console.warn('Cannot emit event: socket not connected', event)
    }
  }

  /**
   * Listen to server event
   */
  on(event: string, handler: (...args: unknown[]) => void) {
    if (this.socket) {
      this.socket.on(event, handler)
      this.storeEventHandler(event, handler)
    }
  }

  /**
   * Remove event listener
   */
  off(event: string, handler?: (...args: unknown[]) => void) {
    if (this.socket) {
      this.socket.off(event, handler)

      // Remove from stored handlers
      if (handler && this.eventHandlers.has(event)) {
        const handlers = this.eventHandlers.get(event)?.filter((h) => h !== handler)
        if (handlers) {
          this.eventHandlers.set(event, handlers)
        }
      } else if (!handler) {
        // Remove all handlers for this event
        this.eventHandlers.delete(event)
      }
    }
  }

  /**
   * Check if socket is connected
   */
  isConnected(): boolean {
    return this.socket?.connected ?? false
  }

  /**
   * Get connection state info
   */
  getConnectionState(): ConnectionState {
    return { ...this.connectionState }
  }

  /**
   * Get socket ID
   */
  getSocketId(): string | undefined {
    return this.socket?.id
  }
}

// Singleton instance
export const socketClient = new SocketClient()

