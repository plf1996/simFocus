<template>
  <div ref="listRef" class="message-list" @scroll="handleScroll">
    <!-- Phase Separator -->
    <div v-if="showPhaseSeparators && currentPhase" class="phase-separator">
      <el-divider>
        <PhaseIndicator :phase="currentPhase" :round="currentRound" />
      </el-divider>
    </div>

    <!-- Messages -->
    <div class="messages-container">
      <!-- Welcome message -->
      <div v-if="messages.length === 0" class="welcome-message">
        <el-empty description="Discussion will start soon...">
          <template #image>
            <el-icon :size="80" color="var(--el-color-primary)">
              <ChatDotRound />
            </el-icon>
          </template>
        </el-empty>
      </div>

      <!-- Message list -->
      <div v-else class="messages-wrapper">
        <MessageBubble
          v-for="message in messages"
          :key="message.id"
          :message="message"
          :is-streaming="isStreaming(message.id)"
          :streaming-content="getStreamingContent(message.id)"
          :show-actions="true"
          :show-token-count="showTokenCounts"
          @copy="handleCopyMessage"
          @quote="handleQuoteMessage"
        />

        <!-- Typing indicator -->
        <div v-if="typingCharacters.length > 0" class="typing-indicator">
          <div class="typing-avatar">
            <div class="avatar-placeholder typing">
              {{ typingCharacterName.charAt(0).toUpperCase() }}
            </div>
          </div>
          <div class="typing-content">
            <div class="typing-bubbles">
              <span class="bubble" />
              <span class="bubble" />
              <span class="bubble" />
            </div>
            <span class="typing-text">{{ typingCharacterName }} is typing...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Scroll to bottom button -->
    <Transition name="fade">
      <div v-if="showScrollButton" class="scroll-bottom">
        <AppButton circle @click="scrollToBottom">
          <el-icon><Bottom /></el-icon>
        </AppButton>
      </div>
    </Transition>

    <!-- Loading more indicator -->
    <div v-if="isLoadingMore" class="loading-more">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>Loading earlier messages...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { ChatDotRound, Bottom, Loading } from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'
import MessageBubble from './MessageBubble.vue'
import PhaseIndicator from './PhaseIndicator.vue'
import { useMessageStore } from '@/stores/message'
import type { DiscussionMessage } from '@/types'

interface Props {
  discussionId: string
  messages: DiscussionMessage[]
  currentPhase?: string
  currentRound?: number
  showPhaseSeparators?: boolean
  showTokenCounts?: boolean
  autoScroll?: boolean
}

interface Emits {
  loadMore: []
  scroll: [scrollTop: number]
}

const props = withDefaults(defineProps<Props>(), {
  showPhaseSeparators: true,
  showTokenCounts: false,
  autoScroll: true
})

const emit = defineEmits<Emits>()

const messageStore = useMessageStore()

// State
const listRef = ref<HTMLElement>()
const isAtBottom = ref(true)
const showScrollButton = ref(false)
const isLoadingMore = ref(false)

// Computed
const typingCharacters = computed(() => {
  // Get typing characters from store
  return Array.from(messageStore.typingCharacters)
})

const typingCharacterName = computed(() => {
  // Find the name of the typing character
  if (typingCharacters.value.length === 0) return ''
  const characterId = typingCharacters.value[0]
  const message = props.messages.find(m => m.participant_id === characterId)
  return message?.character_name || 'Someone'
})

// Methods
const isStreaming = (messageId: string) => {
  return messageStore.streamingContent.has(messageId)
}

const getStreamingContent = (messageId: string) => {
  return messageStore.getStreamingMessage.value(messageId)
}

const handleScroll = (e: Event) => {
  const target = e.target as HTMLElement
  const scrollTop = target.scrollTop
  const scrollHeight = target.scrollHeight
  const clientHeight = target.clientHeight

  // Check if at bottom
  isAtBottom.value = scrollTop + clientHeight >= scrollHeight - 100

  // Show/hide scroll button
  showScrollButton.value = !isAtBottom.value

  // Emit scroll event
  emit('scroll', scrollTop)

  // Load more when scrolling to top
  if (scrollTop === 0 && !isLoadingMore.value) {
    handleLoadMore()
  }
}

const handleLoadMore = () => {
  isLoadingMore.value = true
  emit('loadMore')
  setTimeout(() => {
    isLoadingMore.value = false
  }, 1000)
}

const scrollToBottom = (smooth = true) => {
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTo({
        top: listRef.value.scrollHeight,
        behavior: smooth ? 'smooth' : 'instant'
      })
    }
  })
}

const handleCopyMessage = (message: DiscussionMessage) => {
  console.log('Copy message:', message.id)
}

const handleQuoteMessage = (message: DiscussionMessage) => {
  console.log('Quote message:', message.id)
}

// Watch for new messages
watch(() => props.messages.length, () => {
  if (props.autoScroll && isAtBottom.value) {
    scrollToBottom()
  }
}, { flush: 'post' })

// Watch for streaming updates
watch(() => messageStore.streamingContent.size, () => {
  if (props.autoScroll) {
    scrollToBottom()
  }
})

// Initial scroll
onMounted(() => {
  scrollToBottom(false)
})

// Expose methods
defineExpose({
  scrollToBottom,
  getScrollTop: () => listRef.value?.scrollTop || 0
})
</script>

<style scoped lang="scss">
.message-list {
  position: relative;
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

.phase-separator {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: var(--el-bg-color);
  padding: 8px 0;

  :deep(.el-divider__text) {
    background-color: var(--el-bg-color);
  }
}

.messages-container {
  min-height: 100%;
}

.welcome-message {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
}

.typing-indicator {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

.typing-avatar {
  flex-shrink: 0;
}

.avatar-placeholder.typing {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--el-color-info), var(--el-color-primary));
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.typing-content {
  flex: 1;
  padding: 12px 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.typing-bubbles {
  display: flex;
  gap: 4px;
}

.bubble {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--el-text-color-placeholder);
  animation: typingBounce 1.4s infinite ease-in-out;

  &:nth-child(1) {
    animation-delay: 0s;
  }

  &:nth-child(2) {
    animation-delay: 0.2s;
  }

  &:nth-child(3) {
    animation-delay: 0.4s;
  }
}

@keyframes typingBounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
}

.typing-text {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.scroll-bottom {
  position: absolute;
  bottom: 24px;
  right: 24px;
  z-index: 10;
}

.loading-more {
  position: sticky;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background-color: var(--el-bg-color);
  color: var(--el-text-color-secondary);
  font-size: 13px;
  z-index: 5;

  .el-icon {
    font-size: 16px;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .message-list {
    padding: 12px;
  }

  .scroll-bottom {
    bottom: 16px;
    right: 16px;
  }
}
</style>
