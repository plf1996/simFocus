/**
 * Character Store
 * Manages discussion characters and character library
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Character, CharacterCreate, CharacterUpdate, CharacterTrait } from '@/types'
import { api } from '@/services/api'

export const useCharacterStore = defineStore('character', () => {
  // State
  const characters = ref<Character[]>([])
  const library = ref<Character[]>([])
  const currentCharacter = ref<Character | null>(null)
  const recommendations = ref<Character[]>([])
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  // Filters
  const filters = ref<{
    category?: string
    search?: string
    sortBy?: 'name' | 'rating' | 'most_used'
  }>({})

  // Computed
  const filteredLibrary = computed(() => {
    let result = [...library.value]

    // Apply category filter
    if (filters.value.category) {
      result = result.filter((c) => c.category === filters.value.category)
    }

    // Apply search filter
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      result = result.filter((c) =>
        c.name.toLowerCase().includes(searchLower) ||
        c.role.toLowerCase().includes(searchLower) ||
        c.traits.some((t: CharacterTrait) =>
          t.name.toLowerCase().includes(searchLower)
        )
      )
    }

    // Apply sorting
    switch (filters.value.sortBy) {
      case 'name':
        result.sort((a, b) => a.name.localeCompare(b.name))
        break
      case 'most_used':
        result.sort((a, b) => b.usage_count - a.usage_count)
        break
      case 'rating':
      default:
        result.sort((a, b) => b.rating - a.rating)
        break
    }

    return result
  })

  const categories = computed(() => {
    const uniqueCategories = new Set(library.value.map((c) => c.category))
    return Array.from(uniqueCategories).sort()
  })

  // Actions
  async function fetchCharacters() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/characters')
      characters.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCharacter(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/characters/${id}`)
      currentCharacter.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createCharacter(data: CharacterCreate) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/characters', data)
      characters.value.unshift(response.data)
      currentCharacter.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function updateCharacter(id: string, data: CharacterUpdate) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.patch(`/characters/${id}`, data)
      // Update in characters list
      const index = characters.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        characters.value[index] = response.data
      }
      // Update in library if present
      const libIndex = library.value.findIndex((c) => c.id === id)
      if (libIndex !== -1) {
        library.value[libIndex] = response.data
      }
      // Update current character if it's the same one
      if (currentCharacter.value?.id === id) {
        currentCharacter.value = response.data
      }
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function deleteCharacter(id: string) {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/characters/${id}`)
      // Remove from characters list
      characters.value = characters.value.filter((c) => c.id !== id)
      // Remove from library if present
      library.value = library.value.filter((c) => c.id !== id)
      // Clear current character if it's the deleted one
      if (currentCharacter.value?.id === id) {
        currentCharacter.value = null
      }
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchLibrary() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/characters/library')
      library.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function getRecommendations(topicId: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/characters/recommendations`, {
        params: { topic_id: topicId }
      })
      recommendations.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function rateCharacter(id: string, rating: number) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post(`/characters/${id}/rate`, { rating })
      // Update rating in lists
      const index = characters.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        characters.value[index].rating = rating
      }
      const libIndex = library.value.findIndex((c) => c.id === id)
      if (libIndex !== -1) {
        library.value[libIndex].rating = rating
      }
      if (currentCharacter.value?.id === id) {
        currentCharacter.value.rating = rating
      }
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

  function clearCurrentCharacter() {
    currentCharacter.value = null
  }

  function clearRecommendations() {
    recommendations.value = []
  }

  return {
    // State
    characters,
    library,
    currentCharacter,
    recommendations,
    isLoading,
    error,
    filters,
    // Computed
    filteredLibrary,
    categories,
    // Actions
    fetchCharacters,
    fetchCharacter,
    createCharacter,
    updateCharacter,
    deleteCharacter,
    fetchLibrary,
    getRecommendations,
    rateCharacter,
    setFilters,
    clearFilters,
    clearCurrentCharacter,
    clearRecommendations
  }
})
