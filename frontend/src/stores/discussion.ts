/**
 * Discussion Store
 * Manages active discussion state and operations
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Discussion, DiscussionCreate, DiscussionDetail, DiscussionStatus } from '@/types'
import { api } from '@/services/api'

export const useDiscussionStore = defineStore('discussion', () => {
  // State
  const activeDiscussion = ref<DiscussionDetail | null>(null)
  const discussions = ref<Discussion[]>([])
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  // Computed
  const activeDiscussionId = computed(() => activeDiscussion.value?.id ?? null)
  const isActive = computed(() => activeDiscussion.value?.status === 'running')
  const isPaused = computed(() => activeDiscussion.value?.status === 'paused')
  const isCompleted = computed(() => activeDiscussion.value?.status === 'completed')
  const progress = computed(() =>
    activeDiscussion.value
      ? (activeDiscussion.value.current_round / activeDiscussion.value.max_rounds) * 100
      : 0
  )

  const currentPhase = computed(() => activeDiscussion.value?.current_phase ?? null)
  const currentRound = computed(() => activeDiscussion.value?.current_round ?? 0)

  // Actions
  async function createDiscussion(data: DiscussionCreate) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/discussions', data)
      discussions.value.unshift(response.data)
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDiscussions() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/discussions')
      discussions.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDiscussion(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/discussions/${id}`)
      activeDiscussion.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function startDiscussion(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post(`/discussions/${id}/start`)
      if (activeDiscussion.value?.id === id) {
        activeDiscussion.value = response.data
      }
      updateDiscussionInList(response.data)
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function pauseDiscussion(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post(`/discussions/${id}/pause`)
      if (activeDiscussion.value?.id === id) {
        activeDiscussion.value = response.data
      }
      updateDiscussionInList(response.data)
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function resumeDiscussion(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post(`/discussions/${id}/resume`)
      if (activeDiscussion.value?.id === id) {
        activeDiscussion.value = response.data
      }
      updateDiscussionInList(response.data)
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function stopDiscussion(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post(`/discussions/${id}/stop`)
      if (activeDiscussion.value?.id === id) {
        activeDiscussion.value = response.data
      }
      updateDiscussionInList(response.data)
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function deleteDiscussion(id: string) {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/discussions/${id}`)
      discussions.value = discussions.value.filter((d) => d.id !== id)
      if (activeDiscussion.value?.id === id) {
        activeDiscussion.value = null
      }
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function injectQuestion(id: string, question: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post(`/discussions/${id}/inject`, { question })
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function adjustSpeed(id: string, speed: number) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.patch(`/discussions/${id}/speed`, { speed })
      if (activeDiscussion.value?.id === id) {
        activeDiscussion.value = { ...activeDiscussion.value, ...response.data }
      }
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function updateActiveDiscussion(data: Partial<DiscussionDetail>) {
    if (activeDiscussion.value) {
      activeDiscussion.value = { ...activeDiscussion.value, ...data }
    }
  }

  function updateDiscussionInList(discussion: Discussion) {
    const index = discussions.value.findIndex((d) => d.id === discussion.id)
    if (index !== -1) {
      discussions.value[index] = discussion
    }
  }

  function clearActiveDiscussion() {
    activeDiscussion.value = null
  }

  return {
    // State
    activeDiscussion,
    discussions,
    isLoading,
    error,
    // Computed
    activeDiscussionId,
    isActive,
    isPaused,
    isCompleted,
    progress,
    currentPhase,
    currentRound,
    // Actions
    createDiscussion,
    fetchDiscussions,
    fetchDiscussion,
    startDiscussion,
    pauseDiscussion,
    resumeDiscussion,
    stopDiscussion,
    deleteDiscussion,
    injectQuestion,
    adjustSpeed,
    updateActiveDiscussion,
    clearActiveDiscussion
  }
})
