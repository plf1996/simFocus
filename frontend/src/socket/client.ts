/**
 * Socket.IO Client
 * Manages WebSocket connection for real-time discussion updates
 */

import { io, Socket } from 'socket.io-client'
import type { SocketEvents } from '@/types'

class SocketClient {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect(discussionId: string): Socket {
    // Get token from localStorage (auth store)
    const stored = localStorage.getItem('auth-storage')
    const token = stored ? JSON.parse(stored).token : null

    // Prevent duplicate connections
    if (this.socket?.connected) {
      return this.socket
    }

    const wsUrl = import.meta.env.VITE_WS_BASE_URL || window.location.origin

    this.socket = io(`${wsUrl}/v1/ws/discussions/${discussionId}`, {
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts,
      timeout: 10000,
      transports: ['websocket', 'polling']
    })

    this.setupEventHandlers()
    return this.socket
  }

  private setupEventHandlers() {
    if (!this.socket) return

    // Connection events
    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, need manual reconnect
        this.socket?.connect()
      }
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.reconnectAttempts++
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        // Show error to user
        const uiStore = import('@/stores/ui').then((m) => m.useUiStore())
        uiStore.then((store) => {
          store.showNotification({
            type: 'error',
            message: 'Connection lost. Please refresh the page.'
          })
        })
      }
    })

    // Ping/pong for connection health
    this.socket.on('pong', () => {
      // Update last seen timestamp
    })
  }

  disconnect() {
    this.socket?.disconnect()
    this.socket = null
  }

  emit(event: string, data?: unknown) {
    this.socket?.emit(event, data)
  }

  on(event: string, handler: (...args: unknown[]) => void) {
    this.socket?.on(event, handler)
  }

  off(event: string, handler?: (...args: unknown[]) => void) {
    this.socket?.off(event, handler)
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false
  }
}

// Singleton instance
export const socketClient = new SocketClient()
