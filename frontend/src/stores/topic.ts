/**
 * Topic Store
 * Manages discussion topics and templates
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Topic, TopicCreate, TopicUpdate, TopicTemplate } from '@/types'
import { api } from '@/services/api'

export const useTopicStore = defineStore('topic', () => {
  // State
  const topics = ref<Topic[]>([])
  const templates = ref<TopicTemplate[]>([])
  const currentTopic = ref<Topic | null>(null)
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  // Filters
  const filters = ref<{
    status?: string
    search?: string
    sortBy?: 'newest' | 'oldest' | 'most_used'
  }>({})

  // Computed
  const filteredTopics = computed(() => {
    let result = [...topics.value]

    // Apply status filter
    if (filters.value.status) {
      result = result.filter((t) => t.status === filters.value.status)
    }

    // Apply search filter
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      result = result.filter((t) =>
        t.title.toLowerCase().includes(searchLower) ||
        t.description.toLowerCase().includes(searchLower)
      )
    }

    // Apply sorting
    switch (filters.value.sortBy) {
      case 'oldest':
        result.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
        break
      case 'most_used':
        result.sort((a, b) => b.usage_count - a.usage_count)
        break
      case 'newest':
      default:
        result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        break
    }

    return result
  })

  const topicStats = computed(() => ({
    total: topics.value.length,
    draft: topics.value.filter((t) => t.status === 'draft').length,
    ready: topics.value.filter((t) => t.status === 'ready').length,
    inDiscussion: topics.value.filter((t) => t.status === 'in_discussion').length,
    completed: topics.value.filter((t) => t.status === 'completed').length
  }))

  // Actions
  async function fetchTopics() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/topics')
      topics.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTopic(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/topics/${id}`)
      currentTopic.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createTopic(data: TopicCreate) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/topics', data)
      topics.value.unshift(response.data)
      currentTopic.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function updateTopic(id: string, data: TopicUpdate) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.patch(`/topics/${id}`, data)
      // Update in topics list
      const index = topics.value.findIndex((t) => t.id === id)
      if (index !== -1) {
        topics.value[index] = response.data
      }
      // Update current topic if it's the same one
      if (currentTopic.value?.id === id) {
        currentTopic.value = response.data
      }
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function deleteTopic(id: string) {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/topics/${id}`)
      // Remove from topics list
      topics.value = topics.value.filter((t) => t.id !== id)
      // Clear current topic if it's the deleted one
      if (currentTopic.value?.id === id) {
        currentTopic.value = null
      }
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTemplates() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/topics/templates')
      templates.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createFromTemplate(templateId: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post(`/topics/templates/${templateId}/use`)
      topics.value.unshift(response.data)
      currentTopic.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function setFilters(newFilters: typeof filters.value) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function clearFilters() {
    filters.value = {}
  }

  function clearCurrentTopic() {
    currentTopic.value = null
  }

  return {
    // State
    topics,
    templates,
    currentTopic,
    isLoading,
    error,
    filters,
    // Computed
    filteredTopics,
    topicStats,
    // Actions
    fetchTopics,
    fetchTopic,
    createTopic,
    updateTopic,
    deleteTopic,
    fetchTemplates,
    createFromTemplate,
    setFilters,
    clearFilters,
    clearCurrentTopic
  }
})
