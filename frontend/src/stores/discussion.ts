/**
 * Discussion Store
 * Manages active discussion state and operations
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Discussion, DiscussionCreate, DiscussionDetail, DiscussionStatus } from '@/types'

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
  const progress = computed(() =>
    activeDiscussion.value
      ? (activeDiscussion.value.current_round / activeDiscussion.value.max_rounds) * 100
      : 0
  )

  // Actions
  async function createDiscussion(data: DiscussionCreate) {
    isLoading.value = true
    error.value = null
    try {
      // TODO: Implement actual API call
      // const discussion = await discussionApi.create(data)
      // discussions.value.unshift(discussion)
      // return discussion
      return {} as Discussion
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
      // TODO: Implement actual API call
      // const discussion = await discussionApi.getById(id)
      // activeDiscussion.value = discussion
      // return discussion
      return {} as DiscussionDetail
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function startDiscussion(id: string) {
    // TODO: Implement actual API call
    // const discussion = await discussionApi.start(id)
    // if (activeDiscussion.value?.id === id) {
    //   activeDiscussion.value = discussion
    // }
    // updateDiscussionInList(discussion)
    // return discussion
    return {} as Discussion
  }

  async function pauseDiscussion(id: string) {
    // TODO: Implement actual API call
    // const discussion = await discussionApi.pause(id)
    // if (activeDiscussion.value?.id === id) {
    //   activeDiscussion.value = discussion
    // }
    // updateDiscussionInList(discussion)
    // return discussion
    return {} as Discussion
  }

  async function resumeDiscussion(id: string) {
    // TODO: Implement actual API call
    // const discussion = await discussionApi.resume(id)
    // if (activeDiscussion.value?.id === id) {
    //   activeDiscussion.value = discussion
    // }
    // updateDiscussionInList(discussion)
    // return discussion
    return {} as Discussion
  }

  async function stopDiscussion(id: string) {
    // TODO: Implement actual API call
    // const discussion = await discussionApi.stop(id)
    // if (activeDiscussion.value?.id === id) {
    //   activeDiscussion.value = discussion
    // }
    // updateDiscussionInList(discussion)
    // return discussion
    return {} as Discussion
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
    progress,
    // Actions
    createDiscussion,
    fetchDiscussion,
    startDiscussion,
    pauseDiscussion,
    resumeDiscussion,
    stopDiscussion,
    updateActiveDiscussion,
    clearActiveDiscussion
  }
})
