/**
 * Message Store
 * Manages message cache for real-time updates
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DiscussionMessage } from '@/types'

export const useMessageStore = defineStore('message', () => {
  // State
  const messages = ref<Map<string, DiscussionMessage[]>>(new Map())
  const typingCharacters = ref<Set<string>>(new Set())
  const streamingContent = ref<Map<string, string>>(new Map())

  // Computed
  const getMessages = computed(() => (discussionId: string) =>
    messages.value.get(discussionId) ?? []
  )

  const isTyping = computed(() => (characterId: string) =>
    typingCharacters.value.has(characterId)
  )

  const getStreamingMessage = computed(() => (messageId: string) =>
    streamingContent.value.get(messageId) ?? ''
  )

  // Actions
  function setMessages(discussionId: string, messageList: DiscussionMessage[]) {
    messages.value.set(discussionId, messageList)
  }

  function addMessage(discussionId: string, message: DiscussionMessage) {
    const list = messages.value.get(discussionId) ?? []
    list.push(message)
    messages.value.set(discussionId, list)
  }

  function updateStreamingMessage(messageId: string, content: string) {
    streamingContent.value.set(messageId, content)
  }

  function completeStreamingMessage(messageId: string, finalContent: string) {
    streamingContent.value.delete(messageId)
    // Update the actual message in discussion
    for (const [discussionId, messageList] of messages.value) {
      const message = messageList.find((m) => m.id === messageId)
      if (message) {
        message.content = finalContent
        break
      }
    }
  }

  function setTyping(characterId: string, isTyping: boolean) {
    if (isTyping) {
      typingCharacters.value.add(characterId)
    } else {
      typingCharacters.value.delete(characterId)
    }
  }

  function clearMessages(discussionId: string) {
    messages.value.delete(discussionId)
  }

  function clearAll() {
    messages.value.clear()
    typingCharacters.value.clear()
    streamingContent.value.clear()
  }

  return {
    // State
    messages,
    typingCharacters,
    streamingContent,
    // Computed
    getMessages,
    isTyping,
    getStreamingMessage,
    // Actions
    setMessages,
    addMessage,
    updateStreamingMessage,
    completeStreamingMessage,
    setTyping,
    clearMessages,
    clearAll
  }
})
