<template>
  <div>
    <div v-if="loading" class="text-center py-8">
      <div class="spinner mx-auto"></div>
    </div>

    <div v-else-if="!discussion" class="text-center py-8 text-gray-600">
      讨论不存在
    </div>

    <div v-else class="flex flex-col lg:flex-row gap-6">
      <!-- Left Side: Discussion Info & Controls -->
      <div class="lg:w-1/3 space-y-6">
        <!-- Discussion Header -->
        <div class="bg-white p-6 rounded-lg shadow-sm">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="text-xl font-bold text-gray-900 mb-2">
                {{ topic?.title || '未命名讨论' }}
              </h1>
              <p class="text-sm text-gray-600 line-clamp-2">{{ topic?.description }}</p>
            </div>
            <span
              class="px-3 py-1 text-xs font-medium rounded-full flex-shrink-0"
              :class="getStatusClass(discussion.status)"
            >
              {{ getStatusText(discussion.status) }}
            </span>
          </div>

          <div class="grid grid-cols-2 gap-3 text-center mt-4">
            <div class="bg-gray-50 p-2 rounded">
              <div class="text-lg font-bold text-gray-900">{{ discussion.current_round }}</div>
              <div class="text-xs text-gray-500">当前轮次</div>
            </div>
            <div class="bg-gray-50 p-2 rounded">
              <div class="text-lg font-bold text-gray-900">{{ discussion.max_rounds }}</div>
              <div class="text-xs text-gray-500">总轮次</div>
            </div>
            <div class="bg-gray-50 p-2 rounded">
              <div class="text-lg font-bold text-gray-900">{{ getPhaseText(discussion.current_phase) }}</div>
              <div class="text-xs text-gray-500">当前阶段</div>
            </div>
            <div class="bg-gray-50 p-2 rounded">
              <div class="text-lg font-bold text-gray-900">{{ messages.length }}</div>
              <div class="text-xs text-gray-500">消息数</div>
            </div>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="bg-white p-4 rounded-lg shadow-sm">
          <div class="flex justify-between text-xs text-gray-600 mb-2">
            <span>第{{ discussion.current_round + 1 }}轮 - {{ getPhaseText(discussion.current_phase) }}</span>
            <span class="font-semibold">{{ Math.round(discussion.progress_percentage || 0) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-primary-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: (discussion.progress_percentage || 0) + '%' }"
            ></div>
          </div>
        </div>

        <!-- Control Buttons -->
        <div class="bg-white p-4 rounded-lg shadow-sm">
          <div class="flex flex-col gap-3">
            <!-- API Key Selection (only show when status is initialized) -->
            <div v-if="discussion.status === 'initialized'">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择 API Key
              </label>
              <select
                v-model="selectedApiKey"
                :disabled="apiKeys.length === 0 || starting"
                class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option v-if="apiKeys.length === 0" value="" disabled>
                  暂无可用的 API Key
                </option>
                <option v-for="key in apiKeys" :key="key.id" :value="key.key_name">
                  {{ key.key_name }} ({{ key.provider }}{{ key.default_model ? ' - ' + key.default_model : '' }})
                </option>
              </select>
              <p v-if="apiKeys.length === 0" class="mt-2 text-xs text-red-600">
                请先在设置中配置 API Key
              </p>
            </div>

            <div class="flex flex-col gap-2">
              <button
                v-if="discussion.status === 'initialized'"
                @click="startDiscussion"
                :disabled="starting || !selectedApiKey"
                class="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                {{ starting ? '启动中...' : '开始讨论' }}
              </button>
              <div v-if="['running', 'paused'].includes(discussion.status)" class="flex gap-2">
                <button
                  v-if="discussion.status === 'running'"
                  @click="pauseDiscussion"
                  class="flex-1 px-3 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 text-sm font-medium"
                >
                  暂停
                </button>
                <button
                  v-if="discussion.status === 'paused'"
                  @click="resumeDiscussion"
                  class="flex-1 px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm font-medium"
                >
                  继续
                </button>
                <button
                  @click="showInjectModal = true"
                  class="flex-1 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium"
                >
                  插入问题
                </button>
                <button
                  @click="stopDiscussion"
                  class="flex-1 px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm font-medium"
                >
                  结束讨论
                </button>
              </div>
              <router-link
                v-if="discussion.status === 'completed'"
                :to="`/discussions/${discussion.id}/report`"
                class="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm font-medium text-center block"
              >
                查看报告
              </router-link>
            </div>

            <!-- Token Usage -->
            <div v-if="discussion.total_tokens_used > 0" class="text-xs text-gray-500 text-center">
              Token 使用: {{ discussion.total_tokens_used }}
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side: Messages -->
      <div class="lg:w-2/3">
        <div class="bg-white rounded-lg shadow-sm h-full">
          <div
            ref="messagesContainer"
            class="p-6 space-y-4 overflow-y-auto"
            style="height: calc(100vh - 280px); min-height: 500px;"
          >
            <div
              v-for="message in messages"
              :key="message.id"
              :class="[
                'flex gap-3 p-4 rounded-lg transition-all',
                message.is_injected_question ? 'bg-blue-50 border-l-4 border-blue-500' : 'bg-gray-50 hover:bg-gray-100'
              ]"
            >
              <!-- Avatar -->
              <div class="flex-shrink-0">
                <div class="w-12 h-12 rounded-full overflow-hidden flex items-center justify-center relative"
                  :class="message.is_injected_question ? 'bg-blue-600' : 'bg-gradient-to-br from-primary-500 to-primary-700'"
                >
                  <span v-if="message.is_injected_question" class="text-white text-lg font-bold">?</span>
                  <span v-else class="text-white text-lg font-semibold">
                    {{ message.character_name?.[0] || '?' }}
                  </span>
                  <!-- Typing indicator for last message when running -->
                  <div v-if="isLastMessageStreaming(message)" class="absolute -bottom-1 -right-1">
                    <div class="flex gap-1">
                      <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                      <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                      <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Message Content -->
              <div class="flex-1 min-w-0">
                <!-- Header -->
                <div class="flex items-center gap-2 mb-2 flex-wrap">
                  <span class="font-semibold text-gray-900">
                    {{ message.is_injected_question ? '用户问题' : message.character_name }}
                  </span>
                  <span class="text-xs px-2 py-1 bg-white rounded-full text-gray-600 border">
                    第{{ message.round + 1 }}轮 · {{ getPhaseText(message.phase) }}
                  </span>
                  <span v-if="message.token_count > 0" class="text-xs text-gray-400">
                    {{ message.token_count }} tokens
                  </span>
                  <!-- Streaming indicator -->
                  <span v-if="isLastMessageStreaming(message)" class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full flex items-center gap-1">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path d="M10 5a2 2 0 11-4 0 2 2 0 014 0z" />
                      <path d="M10 19a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    正在输入...
                  </span>
                </div>

                <!-- Content with streaming effect -->
                <p class="text-gray-700 whitespace-pre-wrap leading-relaxed">{{ message.content }}</p>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="messages.length === 0" class="text-center py-16 text-gray-500">
              <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p class="text-lg font-medium mb-1">暂无消息</p>
              <p class="text-sm">{{ ['running', 'paused'].includes(discussion.status) ? '等待消息生成...' : '讨论尚未开始' }}</p>
            </div>

            <!-- Loading Indicator -->
            <div v-if="['running', 'paused'].includes(discussion.status) && messages.length === 0" class="text-center py-8">
              <div class="inline-flex items-center gap-3 px-6 py-3 bg-gray-50 rounded-full">
                <div class="spinner"></div>
                <p class="text-sm text-gray-600 font-medium">
                  {{ discussion.status === 'running' ? '讨论启动中...' : '讨论已暂停' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Inject Question Modal -->
    <Transition name="modal">
      <div
        v-if="showInjectModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="showInjectModal = false"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-lg w-full transform transition-all">
          <div class="p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">插入问题</h3>
            <textarea
              v-model="injectQuestion"
              rows="5"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              placeholder="输入你想插入到讨论中的问题..."
            ></textarea>
            <div class="flex justify-end gap-3 mt-4">
              <button
                @click="showInjectModal = false"
                class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 text-sm font-medium"
              >
                取消
              </button>
              <button
                @click="handleInjectQuestion"
                class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm font-medium"
              >
                插入
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .transform,
.modal-leave-active .transform {
  transition: transform 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .transform,
.modal-leave-to .transform {
  transform: scale(0.95);
}

.modal-enter-to .transform,
.modal-leave-from .transform {
  transform: scale(1);
}
</style>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import endpoints from '@/services/endpoints'
import { useModal } from '@/composables/useModal'

const route = useRoute()
const router = useRouter()
const discussionId = route.params.id

const { showAlert, showConfirm, showToast } = useModal()

const discussion = ref(null)
const topic = ref(null)
const messages = ref([])
const loading = ref(true)
const starting = ref(false)
const showInjectModal = ref(false)
const injectQuestion = ref('')
const messagesContainer = ref(null)
const apiKeys = ref([])
const selectedApiKey = ref(null)
let pollInterval = null

const loadDiscussion = async () => {
  try {
    const response = await endpoints.discussions.getById(discussionId)
    discussion.value = response.data
  } catch (error) {
    console.error('Failed to load discussion:', error)
  }
}

const loadMessages = async () => {
  try {
    const response = await endpoints.discussions.getMessages(discussionId)
    messages.value = response.data
    scrollToBottom()
  } catch (error) {
    console.error('Failed to load messages:', error)
  }
}

const loadTopic = async () => {
  if (!discussion.value?.topic_id) return
  try {
    const response = await endpoints.topics.getById(discussion.value.topic_id)
    topic.value = response.data
  } catch (error) {
    console.error('Failed to load topic:', error)
  }
}

const loadApiKeys = async () => {
  try {
    const response = await endpoints.apiKeys.getAll()
    // Only show active API keys
    apiKeys.value = response.data.filter(key => key.is_active)
    // Select first API key by default
    if (apiKeys.value.length > 0) {
      selectedApiKey.value = apiKeys.value[0].key_name
    }
  } catch (error) {
    console.error('Failed to load API keys:', error)
  }
}

const startDiscussion = async () => {
  if (!selectedApiKey.value) {
    await showAlert('请先配置并选择 API Key', { title: '提示' })
    return
  }

  starting.value = true
  try {
    // 使用用户选择的 API provider
    await endpoints.discussions.start(discussionId, selectedApiKey.value)
    await loadDiscussion()
    showToast('讨论已启动', 'success')
  } catch (error) {
    console.error('Failed to start discussion:', error)
    await showAlert(
      '启动讨论失败：' + (error.response?.data?.detail || error.message || '请确保已配置 API Key'),
      { title: '错误', confirmType: 'danger' }
    )
  } finally {
    starting.value = false
  }
}

const pauseDiscussion = async () => {
  try {
    await endpoints.discussions.pause(discussionId)
    await loadDiscussion()
    showToast('讨论已暂停', 'success')
  } catch (error) {
    console.error('Failed to pause discussion:', error)
    await showAlert('暂停失败，请稍后重试', { title: '错误', confirmType: 'danger' })
  }
}

const resumeDiscussion = async () => {
  try {
    await endpoints.discussions.resume(discussionId)
    await loadDiscussion()
    showToast('讨论已继续', 'success')
  } catch (error) {
    console.error('Failed to resume discussion:', error)
    await showAlert('继续失败，请稍后重试', { title: '错误', confirmType: 'danger' })
  }
}

const stopDiscussion = async () => {
  const confirmed = await showConfirm(
    '确定要结束讨论吗？结束后将自动生成报告。',
    { title: '确认结束', confirmType: 'danger', confirmText: '结束讨论' }
  )

  if (!confirmed) return

  try {
    await endpoints.discussions.stop(discussionId)
    await loadDiscussion()
    showToast('讨论已结束，正在生成报告...', 'success')
  } catch (error) {
    console.error('Failed to stop discussion:', error)
    await showAlert('结束失败，请稍后重试', { title: '错误', confirmType: 'danger' })
  }
}

const handleInjectQuestion = async () => {
  if (!injectQuestion.value.trim()) return

  try {
    await endpoints.discussions.injectQuestion(discussionId, injectQuestion.value)
    showInjectModal.value = false
    injectQuestion.value = ''
    await loadMessages()
    showToast('问题已插入讨论', 'success')
  } catch (error) {
    console.error('Failed to inject question:', error)
    await showAlert('插入失败，请稍后重试', { title: '错误', confirmType: 'danger' })
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const getStatusClass = (status) => {
  const classes = {
    initialized: 'bg-gray-100 text-gray-700',
    running: 'bg-green-100 text-green-700',
    paused: 'bg-yellow-100 text-yellow-700',
    completed: 'bg-blue-100 text-blue-700',
    failed: 'bg-red-100 text-red-700'
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

const getStatusText = (status) => {
  const texts = {
    initialized: '初始化',
    running: '进行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const getPhaseText = (phase) => {
  const texts = {
    opening: '开场',
    development: '发展',
    debate: '辩论',
    closing: '总结'
  }
  return texts[phase] || phase
}

// Check if a message is currently being generated (streaming)
const isLastMessageStreaming = (message) => {
  if (!discussion.value || discussion.value.status !== 'running') {
    return false
  }

  // Check if this is the last message
  const lastMessage = messages.value[messages.value.length - 1]
  if (!lastMessage || lastMessage.id !== message.id) {
    return false
  }

  // Check if the message is very recent (within last 10 seconds) and has content
  const now = new Date()
  const messageTime = new Date(message.created_at)
  const timeDiff = (now - messageTime) / 1000

  // Message is "streaming" if it was created recently and has content
  return timeDiff < 10 && message.content && message.content.length > 0
}

// Poll for updates when discussion is running
const startPolling = () => {
  pollInterval = setInterval(async () => {
    await loadMessages()
    await loadDiscussion()
  }, 500) // Poll every 500ms to show streaming effect
}

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

watch(() => discussion.value?.status, (newStatus) => {
  if (newStatus === 'running') {
    startPolling()
  } else {
    stopPolling()
  }
})

onMounted(async () => {
  await loadDiscussion()
  await loadMessages()
  await loadTopic()
  await loadApiKeys()
  loading.value = false

  if (discussion.value?.status === 'running') {
    startPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>
