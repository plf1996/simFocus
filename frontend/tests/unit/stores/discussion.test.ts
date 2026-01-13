/**
 * Unit Tests for Discussion Store
 * Testing discussion state management
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useDiscussionStore } from '@/stores/discussion'
import type { Discussion, DiscussionDetail, DiscussionCreate } from '@/types'

describe('Discussion Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Initial State', () => {
    it('should have initial null state', () => {
      const store = useDiscussionStore()

      expect(store.activeDiscussion).toBeNull()
      expect(store.discussions).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should calculate activeDiscussionId correctly', () => {
      const store = useDiscussionStore()

      expect(store.activeDiscussionId).toBeNull()

      store.$patch({
        activeDiscussion: { id: 'disc-123' } as DiscussionDetail
      })

      expect(store.activeDiscussionId).toBe('disc-123')
    })
  })

  describe('Status Calculations', () => {
    it('should calculate isActive correctly', () => {
      const store = useDiscussionStore()

      expect(store.isActive).toBe(false)

      store.$patch({
        activeDiscussion: { status: 'running' } as DiscussionDetail
      })

      expect(store.isActive).toBe(true)

      store.$patch({
        activeDiscussion: { status: 'paused' } as DiscussionDetail
      })

      expect(store.isActive).toBe(false)
    })

    it('should calculate isPaused correctly', () => {
      const store = useDiscussionStore()

      expect(store.isPaused).toBe(false)

      store.$patch({
        activeDiscussion: { status: 'paused' } as DiscussionDetail
      })

      expect(store.isPaused).toBe(true)
    })
  })

  describe('Progress Calculation', () => {
    it('should calculate progress correctly', () => {
      const store = useDiscussionStore()

      expect(store.progress).toBe(0)

      store.$patch({
        activeDiscussion: {
          current_round: 5,
          max_rounds: 10
        } as DiscussionDetail
      })

      expect(store.progress).toBe(50)
    })

    it('should handle zero max rounds', () => {
      const store = useDiscussionStore()

      store.$patch({
        activeDiscussion: {
          current_round: 0,
          max_rounds: 0
        } as DiscussionDetail
      })

      expect(store.progress).toBe(NaN)
    })

    it('should handle no active discussion', () => {
      const store = useDiscussionStore()

      expect(store.progress).toBe(0)
    })
  })

  describe('Create Discussion', () => {
    it('should set loading state during creation', async () => {
      const store = useDiscussionStore()

      const createPromise = store.createDiscussion({
        topic_id: 'topic-1',
        character_ids: ['char-1', 'char-2'],
        discussion_mode: 'free',
        max_rounds: 10,
        llm_provider: 'openai',
        llm_model: 'gpt-4'
      } as DiscussionCreate)

      expect(store.isLoading).toBe(true)
      expect(store.error).toBeNull()

      await createPromise

      expect(store.isLoading).toBe(false)
    })

    it('should handle creation errors', async () => {
      const store = useDiscussionStore()

      const error = new Error('Creation failed')

      // Mock the action to throw error
      store.createDiscussion = vi.fn().mockRejectedValue(error)

      try {
        await store.createDiscussion({} as DiscussionCreate)
      } catch (e) {
        expect(store.error).toBe(error)
      }
    })
  })

  describe('Fetch Discussion', () => {
    it('should set loading state during fetch', async () => {
      const store = useDiscussionStore()

      const fetchPromise = store.fetchDiscussion('disc-123')

      expect(store.isLoading).toBe(true)

      await fetchPromise

      expect(store.isLoading).toBe(false)
    })

    it('should handle fetch errors', async () => {
      const store = useDiscussionStore()

      const error = new Error('Not found')

      store.fetchDiscussion = vi.fn().mockRejectedValue(error)

      try {
        await store.fetchDiscussion('invalid-id')
      } catch (e) {
        expect(store.error).toBe(error)
      }
    })
  })

  describe('Update Active Discussion', () => {
    it('should update active discussion properties', () => {
      const store = useDiscussionStore()

      store.$patch({
        activeDiscussion: {
          id: 'disc-1',
          status: 'initialized',
          current_round: 0
        } as DiscussionDetail
      })

      store.updateActiveDiscussion({
        status: 'running',
        current_round: 1
      })

      expect(store.activeDiscussion?.status).toBe('running')
      expect(store.activeDiscussion?.current_round).toBe(1)
      expect(store.activeDiscussion?.id).toBe('disc-1') // unchanged
    })

    it('should not update when no active discussion', () => {
      const store = useDiscussionStore()

      expect(() => {
        store.updateActiveDiscussion({ status: 'running' })
      }).not.toThrow()
    })
  })

  describe('Update Discussion in List', () => {
    it('should update discussion in list', () => {
      const store = useDiscussionStore()

      const discussion1: Discussion = {
        id: 'disc-1',
        topic_id: 'topic-1',
        user_id: 'user-1',
        discussion_mode: 'free',
        max_rounds: 10,
        status: 'initialized',
        current_round: 0,
        current_phase: 'opening',
        llm_provider: 'openai',
        llm_model: 'gpt-4',
        total_tokens_used: 0,
        created_at: '2026-01-13T00:00:00Z'
      }

      const discussion2: Discussion = {
        ...discussion1,
        id: 'disc-2'
      }

      store.$patch({
        discussions: [discussion1, discussion2]
      })

      const updated: Discussion = {
        ...discussion1,
        status: 'running',
        current_round: 1
      }

      store.updateDiscussionInList(updated)

      expect(store.discussions[0].status).toBe('running')
      expect(store.discussions[0].current_round).toBe(1)
      expect(store.discussions[1].status).toBe('initialized')
    })

    it('should not add discussion if not in list', () => {
      const store = useDiscussionStore()

      const discussion: Discussion = {
        id: 'disc-1',
        topic_id: 'topic-1',
        user_id: 'user-1',
        discussion_mode: 'free',
        max_rounds: 10,
        status: 'initialized',
        current_round: 0,
        current_phase: 'opening',
        llm_provider: 'openai',
        llm_model: 'gpt-4',
        total_tokens_used: 0,
        created_at: '2026-01-13T00:00:00Z'
      }

      store.updateDiscussionInList(discussion)

      expect(store.discussions).toHaveLength(0)
    })
  })

  describe('Clear Active Discussion', () => {
    it('should clear active discussion', () => {
      const store = useDiscussionStore()

      store.$patch({
        activeDiscussion: { id: 'disc-1' } as DiscussionDetail
      })

      store.clearActiveDiscussion()

      expect(store.activeDiscussion).toBeNull()
    })
  })
})
