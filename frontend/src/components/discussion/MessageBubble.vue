<template>
  <div
    :class="[
      'message-bubble',
      `is-${position}`,
      { 'is-streaming': isStreaming, 'is-question': isInjectedQuestion }
    ]"
  >
    <!-- Avatar -->
    <div class="message-avatar">
      <img
        v-if="message.character_avatar"
        :src="message.character_avatar"
        :alt="message.character_name"
        class="avatar-img"
      />
      <div v-else class="avatar-placeholder">
        {{ message.character_name.charAt(0).toUpperCase() }}
      </div>
    </div>

    <!-- Content -->
    <div class="message-content-wrapper">
      <!-- Header -->
      <div class="message-header">
        <span class="character-name">{{ message.character_name }}</span>
        <div class="message-meta">
          <span class="round-info">Round {{ message.round }}</span>
          <el-tag :type="phaseType" size="small">{{ phaseText }}</el-tag>
          <span class="timestamp">{{ formatTime(message.created_at) }}</span>
        </div>
      </div>

      <!-- Body -->
      <div class="message-body">
        <!-- Injected question badge -->
        <div v-if="isInjectedQuestion" class="question-badge">
          <el-icon><QuestionFilled /></el-icon>
          <span>User Question</span>
        </div>

        <!-- Message text -->
        <div class="message-text">
          <template v-if="isStreaming && streamingContent">
            {{ streamingContent }}
            <span class="cursor">|</span>
          </template>
          <template v-else>
            {{ message.content }}
          </template>
        </div>

        <!-- Token count -->
        <div v-if="showTokenCount && message.token_count > 0" class="token-count">
          {{ message.token_count }} tokens
        </div>
      </div>

      <!-- Actions -->
      <div v-if="showActions" class="message-actions">
        <AppButton size="small" text @click="handleCopy">
          <el-icon><CopyDocument /></el-icon>
        </AppButton>
        <AppButton size="small" text @click="handleQuote">
          <el-icon><ChatLineRound /></el-icon>
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled, CopyDocument, ChatLineRound } from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'
import type { DiscussionMessage } from '@/types'

interface Props {
  message: DiscussionMessage
  position?: 'left' | 'right'
  isStreaming?: boolean
  streamingContent?: string
  showActions?: boolean
  showTokenCount?: boolean
}

interface Emits {
  copy: [message: DiscussionMessage]
  quote: [message: DiscussionMessage]
}

const props = withDefaults(defineProps<Props>(), {
  position: 'left',
  isStreaming: false,
  streamingContent: '',
  showActions: false,
  showTokenCount: false
})

const emit = defineEmits<Emits>()

// Computed
const isInjectedQuestion = computed(() => props.message.is_injected_question)

const phaseType = computed(() => {
  const typeMap: Record<string, any> = {
    opening: 'success',
    development: 'primary',
    debate: 'warning',
    closing: 'info'
  }
  return typeMap[props.message.phase] || ''
})

const phaseText = computed(() => {
  const textMap: Record<string, string> = {
    opening: 'Opening',
    development: 'Development',
    debate: 'Debate',
    closing: 'Closing'
  }
  return textMap[props.message.phase] || props.message.phase
})

// Methods
const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
  return date.toLocaleDateString()
}

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    ElMessage.success('Message copied to clipboard')
    emit('copy', props.message)
  } catch (error) {
    ElMessage.error('Failed to copy message')
  }
}

const handleQuote = () => {
  emit('quote', props.message)
}
</script>

<style scoped lang="scss">
.message-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  &.is-right {
    flex-direction: row-reverse;

    .message-content-wrapper {
      align-items: flex-end;
    }
  }

  &.is-streaming {
    .cursor {
      animation: blink 1s infinite;
    }

    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }
  }

  &.is-question {
    .message-content-wrapper {
      border-color: var(--el-color-warning);
      background-color: var(--el-color-warning-light-9);
    }
  }
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--el-border-color);
}

.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-success));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
}

.message-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 70%;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.character-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.round-info {
  font-weight: 500;
}

.message-body {
  padding: 12px 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter);
  position: relative;
}

.question-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background-color: var(--el-color-warning);
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;

  .el-icon {
    font-size: 14px;
  }
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.token-count {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  text-align: right;
}

.message-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;

  .message-bubble:hover & {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .message-content-wrapper {
    max-width: 85%;
  }
}
</style>
