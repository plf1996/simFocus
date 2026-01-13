/**
 * Unit Tests for Message Store
 * Testing message state management
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useMessageStore } from '@/stores/message'
import type { DiscussionMessage } from '@/types'

describe('Message Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Initial State', () => {
    it('should have empty initial state', () => {
      const store = useMessageStore()

      expect(store.messages.size).toBe(0)
      expect(store.typingCharacters.size).toBe(0)
      expect(store.streamingContent.size).toBe(0)
    })
  })

  describe('Set Messages', () => {
    it('should set messages for a discussion', () => {
      const store = useMessageStore()

      const messages: DiscussionMessage[] = [
        {
          id: 'msg-1',
          discussion_id: 'disc-1',
          participant_id: 'part-1',
          character_name: 'Alice',
          round: 1,
          phase: 'opening',
          content: 'Hello',
          token_count: 10,
          is_injected_question: false,
          created_at: '2026-01-13T00:00:00Z'
        },
        {
          id: 'msg-2',
          discussion_id: 'disc-1',
          participant_id: 'part-2',
          character_name: 'Bob',
          round: 1,
          phase: 'opening',
          content: 'Hi there',
          token_count: 15,
          is_injected_question: false,
          created_at: '2026-01-13T00:00:01Z'
        }
      ]

      store.setMessages('disc-1', messages)

      expect(store.getMessages('disc-1')).toHaveLength(2)
      expect(store.getMessages('disc-1')).toEqual(messages)
    })

    it('should replace existing messages', () => {
      const store = useMessageStore()

      store.setMessages('disc-1', [
        { id: 'msg-1', discussion_id: 'disc-1', participant_id: 'part-1', character_name: 'Alice', round: 1, phase: 'opening', content: 'Hello', token_count: 10, is_injected_question: false, created_at: '2026-01-13T00:00:00Z' }
      ] as DiscussionMessage[])

      store.setMessages('disc-1', [
        { id: 'msg-2', discussion_id: 'disc-1', participant_id: 'part-2', character_name: 'Bob', round: 1, phase: 'opening', content: 'Hi', token_count: 5, is_injected_question: false, created_at: '2026-01-13T00:00:00Z' }
      ] as DiscussionMessage[])

      expect(store.getMessages('disc-1')).toHaveLength(1)
      expect(store.getMessages('disc-1')[0].id).toBe('msg-2')
    })
  })

  describe('Add Message', () => {
    it('should add message to existing list', () => {
      const store = useMessageStore()

      const existing: DiscussionMessage = {
        id: 'msg-1',
        discussion_id: 'disc-1',
        participant_id: 'part-1',
        character_name: 'Alice',
        round: 1,
        phase: 'opening',
        content: 'Hello',
        token_count: 10,
        is_injected_question: false,
        created_at: '2026-01-13T00:00:00Z'
      }

      const newMessage: DiscussionMessage = {
        id: 'msg-2',
        discussion_id: 'disc-1',
        participant_id: 'part-2',
        character_name: 'Bog',
        round: 1,
        phase: 'opening',
        content: 'Hi there',
        token_count: 15,
        is_injected_question: false,
        created_at: '2026-01-13T00:00:01Z'
      }

      store.setMessages('disc-1', [existing])
      store.addMessage('disc-1', newMessage)

      const messages = store.getMessages('disc-1')
      expect(messages).toHaveLength(2)
      expect(messages[1]).toEqual(newMessage)
    })

    it('should create new list if none exists', () => {
      const store = useMessageStore()

      const message: DiscussionMessage = {
        id: 'msg-1',
        discussion_id: 'disc-1',
        participant_id: 'part-1',
        character_name: 'Alice',
        round: 1,
        phase: 'opening',
        content: 'Hello',
        token_count: 10,
        is_injected_question: false,
        created_at: '2026-01-13T00:00:00Z'
      }

      store.addMessage('disc-1', message)

      expect(store.getMessages('disc-1')).toHaveLength(1)
      expect(store.getMessages('disc-1')[0]).toEqual(message)
    })
  })

  describe('Streaming Messages', () => {
    it('should update streaming content', () => {
      const store = useMessageStore()

      store.updateStreamingMessage('msg-1', 'Partial content')

      expect(store.getStreamingMessage('msg-1')).toBe('Partial content')
    })

    it('should complete streaming and update message', () => {
      const store = useMessageStore()

      const message: DiscussionMessage = {
        id: 'msg-1',
        discussion_id: 'disc-1',
        participant_id: 'part-1',
        character_name: 'Alice',
        round: 1,
        phase: 'opening',
        content: 'Old content',
        token_count: 10,
        is_injected_question: false,
        created_at: '2026-01-13T00:00:00Z'
      }

      store.setMessages('disc-1', [message])
      store.updateStreamingMessage('msg-1', 'Streaming...')
      store.completeStreamingMessage('msg-1', 'New complete content')

      expect(store.getStreamingMessage('msg-1')).toBe('')
      expect(store.getMessages('disc-1')[0].content).toBe('New complete content')
    })

    it('should remove streaming content after completion', () => {
      const store = useMessageStore()

      store.updateStreamingMessage('msg-1', 'Streaming...')
      store.completeStreamingMessage('msg-1', 'Complete')

      expect(store.streamingContent.has('msg-1')).toBe(false)
    })
  })

  describe('Typing Indicators', () => {
    it('should set character as typing', () => {
      const store = useMessageStore()

      store.setTyping('char-1', true)

      expect(store.isTyping('char-1')).toBe(true)
    })

    it('should unset character as typing', () => {
      const store = useMessageStore()

      store.setTyping('char-1', true)
      store.setTyping('char-1', false)

      expect(store.isTyping('char-1')).toBe(false)
    })

    it('should handle multiple typing characters', () => {
      const store = useMessageStore()

      store.setTyping('char-1', true)
      store.setTyping('char-2', true)
      store.setTyping('char-3', true)

      expect(store.isTyping('char-1')).toBe(true)
      expect(store.isTyping('char-2')).toBe(true)
      expect(store.isTyping('char-3')).toBe(true)

      store.setTyping('char-2', false)

      expect(store.isTyping('char-1')).toBe(true)
      expect(store.isTyping('char-2')).toBe(false)
      expect(store.isTyping('char-3')).toBe(true)
    })
  })

  describe('Clear Messages', () => {
    it('should clear messages for specific discussion', () => {
      const store = useMessageStore()

      store.setMessages('disc-1', [
        { id: 'msg-1', discussion_id: 'disc-1', participant_id: 'part-1', character_name: 'Alice', round: 1, phase: 'opening', content: 'Hello', token_count: 10, is_injected_question: false, created_at: '2026-01-13T00:00:00Z' }
      ] as DiscussionMessage[])

      store.setMessages('disc-2', [
        { id: 'msg-2', discussion_id: 'disc-2', participant_id: 'part-2', character_name: 'Bob', round: 1, phase: 'opening', content: 'Hi', token_count: 5, is_injected_question: false, created_at: '2026-01-13T00:00:00Z' }
      ] as DiscussionMessage[])

      store.clearMessages('disc-1')

      expect(store.getMessages('disc-1')).toHaveLength(0)
      expect(store.getMessages('disc-2')).toHaveLength(1)
    })
  })

  describe('Clear All', () => {
    it('should clear all state', () => {
      const store = useMessageStore()

      store.setMessages('disc-1', [
        { id: 'msg-1', discussion_id: 'disc-1', participant_id: 'part-1', character_name: 'Alice', round: 1, phase: 'opening', content: 'Hello', token_count: 10, is_injected_question: false, created_at: '2026-01-13T00:00:00Z' }
      ] as DiscussionMessage[])

      store.setTyping('char-1', true)
      store.updateStreamingMessage('msg-1', 'Streaming...')

      store.clearAll()

      expect(store.messages.size).toBe(0)
      expect(store.typingCharacters.size).toBe(0)
      expect(store.streamingContent.size).toBe(0)
    })
  })
})
