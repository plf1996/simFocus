<template>
  <div class="discussion-room">
    <!-- Error State -->
    <el-alert
      v-if="error"
      type="error"
      :title="error.message"
      :closable="false"
      show-icon
      class="room-error"
    />

    <!-- Loading State -->
    <div v-else-if="isLoading" class="room-loading">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- Main Content -->
    <div v-else-if="discussion" class="room-content">
      <!-- Header -->
      <div class="room-header">
        <div class="header-info">
          <h2 class="room-title">{{ discussion.topic.title }}</h2>
          <div class="room-meta">
            <el-tag :type="modeType" size="small">{{ modeText }}</el-tag>
            <span class="meta-divider">•</span>
            <span class="participant-count">
              {{ discussion.participants.length }} participants
            </span>
            <span class="meta-divider">•</span>
            <span class="created-time">
              {{ formatTime(discussion.started_at || discussion.created_at) }}
            </span>
          </div>
        </div>

        <!-- Header Actions -->
        <div class="header-actions">
          <AppButton size="small" @click="handleShowInfo">
            <el-icon><InfoFilled /></el-icon>
            Details
          </AppButton>
        </div>
      </div>

      <!-- Progress Bar -->
      <ProgressBar
        :current="discussion.current_round"
        :max="discussion.max_rounds"
        label="Discussion Progress"
      />

      <!-- Main Layout -->
      <div class="room-layout">
        <!-- Left Panel: Characters -->
        <div class="layout-left">
          <CharacterPanel
            :participants="discussion.participants"
            :speaking-participant-id="speakingParticipantId"
            :show-stats="true"
            :collapsible="true"
            @view-participant="handleViewParticipant"
          />
        </div>

        <!-- Center: Messages -->
        <div class="layout-center">
          <!-- Phase Indicator -->
          <div class="phase-banner">
            <PhaseIndicator
              :phase="discussion.current_phase"
              :round="discussion.current_round"
              :show-progress="false"
            />
          </div>

          <!-- Message List -->
          <MessageList
            ref="messageListRef"
            :discussion-id="discussion.id"
            :messages="discussion.messages"
            :current-phase="discussion.current_phase"
            :current-round="discussion.current_round"
            :show-phase-separators="true"
            :auto-scroll="autoScroll"
            @load-more="handleLoadMore"
          />

          <!-- Discussion Controls -->
          <DiscussionControls
            :status="discussion.status"
            :is-active="isActive"
            :show-status="true"
            @start="handleStart"
            @pause="handlePause"
            @resume="handleResume"
            @stop="handleStop"
            @restart="handleRestart"
            @speed-change="handleSpeedChange"
            @inject-question="handleInjectQuestion"
            @export="handleExport"
            @settings="handleSettings"
            @report="handleReport"
          />
        </div>

        <!-- Right Panel: Info (optional) -->
        <div class="layout-right">
          <AppCard class="info-card">
            <template #header>
              <h4>Discussion Info</h4>
            </template>

            <div class="info-section">
              <div class="info-label">Model</div>
              <div class="info-value">
                {{ discussion.llm_provider }} / {{ discussion.llm_model }}
              </div>
            </div>

            <div class="info-section">
              <div class="info-label">Tokens Used</div>
              <div class="info-value">{{ formatNumber(discussion.total_tokens_used) }}</div>
            </div>

            <div v-if="discussion.estimated_cost_usd" class="info-section">
              <div class="info-label">Estimated Cost</div>
              <div class="info-value">${{ discussion.estimated_cost_usd.toFixed(4) }}</div>
            </div>

            <div class="info-section">
              <div class="info-label">Status</div>
              <el-tag :type="statusType" size="small">
                {{ statusText }}
              </el-tag>
            </div>
          </AppCard>
        </div>
      </div>
    </div>

    <!-- Not Found -->
    <div v-else class="room-empty">
      <el-empty description="Discussion not found">
        <AppButton type="primary" @click="handleBack">
          Go Back
        </AppButton>
      </el-empty>
    </div>

    <!-- Character Detail Dialog -->
    <el-dialog
      v-model="showCharacterDialog"
      :title="selectedCharacter?.character_name"
      width="600px"
    >
      <CharacterPreview
        v-if="selectedCharacter"
        :character="mockCharacter"
        :show-stats="true"
        :show-behavior="true"
        :show-actions="false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useDiscussionStore } from '@/stores/discussion'
import { useMessageStore } from '@/stores/message'
import AppButton from '@/components/common/AppButton.vue'
import AppCard from '@/components/common/AppCard.vue'
import CharacterPanel from './CharacterPanel.vue'
import CharacterPreview from '../character/CharacterPreview.vue'
import MessageList from './MessageList.vue'
import DiscussionControls from './DiscussionControls.vue'
import ProgressBar from './ProgressBar.vue'
import PhaseIndicator from './PhaseIndicator.vue'
import type { DiscussionDetail, Participant, DiscussionStatus, DiscussionMode } from '@/types'

interface Props {
  discussionId?: string
}

interface Emits {
  back: []
  refresh: []
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const discussionStore = useDiscussionStore()
const messageStore = useMessageStore()

// State
const messageListRef = ref()
const speakingParticipantId = ref('')
const autoScroll = ref(true)
const showCharacterDialog = ref(false)
const selectedCharacter = ref<Participant | null>(null)

// Computed
const discussion = computed(() => discussionStore.activeDiscussion)
const isLoading = computed(() => discussionStore.isLoading)
const error = computed(() => discussionStore.error)
const isActive = computed(() => discussionStore.isActive)

// Mock character for preview (in real app, fetch from API)
const mockCharacter = computed(() => {
  if (!selectedCharacter.value) return null
  return {
    id: selectedCharacter.value.id,
    name: selectedCharacter.value.character_name,
    avatar_url: selectedCharacter.value.character_avatar,
    is_template: true,
    is_public: true,
    config: {
      age: 35,
      gender: 'prefer_not_to_say',
      profession: 'Expert',
      personality: {
        openness: 7,
        rigor: 6,
        critical_thinking: 8,
        optimism: 5
      },
      knowledge: {
        fields: ['General'],
        experience_years: 10,
        representative_views: []
      },
      stance: 'neutral',
      expression_style: 'formal',
      behavior_pattern: 'balanced'
    },
    usage_count: 0,
    rating_count: 0,
    created_at: new Date().toISOString()
  }
})

const modeType = computed(() => {
  const typeMap: Record<DiscussionMode, any> = {
    free: 'primary',
    structured: 'success',
    creative: 'warning',
    consensus: 'info'
  }
  return discussion.value ? typeMap[discussion.value.discussion_mode] : ''
})

const modeText = computed(() => {
  const textMap: Record<DiscussionMode, string> = {
    free: 'Free Discussion',
    structured: 'Structured Debate',
    creative: 'Creative Brainstorm',
    consensus: 'Consensus Building'
  }
  return discussion.value ? textMap[discussion.value.discussion_mode] : ''
})

const statusType = computed(() => {
  const typeMap: Record<DiscussionStatus, any> = {
    initialized: 'info',
    running: 'success',
    paused: 'warning',
    completed: '',
    failed: 'danger',
    cancelled: 'info'
  }
  return discussion.value ? typeMap[discussion.value.status] : ''
})

const statusText = computed(() => {
  const textMap: Record<DiscussionStatus, string> = {
    initialized: 'Ready',
    running: 'Running',
    paused: 'Paused',
    completed: 'Completed',
    failed: 'Failed',
    cancelled: 'Cancelled'
  }
  return discussion.value ? textMap[discussion.value.status] : ''
})

// Methods
const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just started'
  if (diffMins < 60) return `Started ${diffMins}m ago`
  const hours = Math.floor(diffMins / 60)
  if (hours < 24) return `Started ${hours}h ago`
  return date.toLocaleDateString()
}

const formatNumber = (num: number) => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

const handleShowInfo = () => {
  ElMessage.info('Discussion details')
}

const handleViewParticipant = (participant: Participant) => {
  selectedCharacter.value = participant
  showCharacterDialog.value = true
}

const handleStart = async () => {
  try {
    if (props.discussionId) {
      await discussionStore.startDiscussion(props.discussionId)
      ElMessage.success('Discussion started')
    }
  } catch (error) {
    ElMessage.error('Failed to start discussion')
  }
}

const handlePause = async () => {
  try {
    if (props.discussionId) {
      await discussionStore.pauseDiscussion(props.discussionId)
      ElMessage.info('Discussion paused')
    }
  } catch (error) {
    ElMessage.error('Failed to pause discussion')
  }
}

const handleResume = async () => {
  try {
    if (props.discussionId) {
      await discussionStore.resumeDiscussion(props.discussionId)
      ElMessage.success('Discussion resumed')
    }
  } catch (error) {
    ElMessage.error('Failed to resume discussion')
  }
}

const handleStop = async () => {
  try {
    if (props.discussionId) {
      await discussionStore.stopDiscussion(props.discussionId)
      ElMessage.warning('Discussion stopped')
    }
  } catch (error) {
    ElMessage.error('Failed to stop discussion')
  }
}

const handleRestart = () => {
  ElMessage.info('Restarting discussion...')
  emit('refresh')
}

const handleSpeedChange = (speed: number) => {
  ElMessage.success(`Playback speed: ${speed}x`)
}

const handleInjectQuestion = (question: string) => {
  ElMessage.success('Question injected')
  // TODO: Implement actual injection via WebSocket
}

const handleExport = () => {
  if (discussion.value) {
    const data = JSON.stringify(discussion.value.messages, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `discussion-${discussion.value.id}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('Messages exported')
  }
}

const handleSettings = () => {
  ElMessage.info('Settings')
}

const handleReport = () => {
  ElMessage.info('Generating report...')
}

const handleLoadMore = () => {
  ElMessage.info('Loading more messages...')
}

const handleBack = () => {
  emit('back')
}

// Lifecycle
onMounted(async () => {
  if (props.discussionId) {
    try {
      await discussionStore.fetchDiscussion(props.discussionId)
      // Initialize messages in store
      if (discussion.value) {
        messageStore.setMessages(props.discussionId, discussion.value.messages)
      }
    } catch (error) {
      ElMessage.error('Failed to load discussion')
    }
  }
})

onUnmounted(() => {
  // Cleanup
  discussionStore.clearActiveDiscussion()
})
</script>

<style scoped lang="scss">
.discussion-room {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20px;
}

.room-error,
.room-loading {
  padding: 40px;
}

.room-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, var(--el-color-primary-light-9), var(--el-fill-color-light));
  border-radius: 8px;
}

.header-info {
  flex: 1;
}

.room-title {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
  line-height: 1.3;
}

.room-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  flex-wrap: wrap;
}

.meta-divider {
  color: var(--el-border-color);
}

.participant-count,
.created-time {
  font-weight: 500;
}

.header-actions {
  flex-shrink: 0;
}

.room-layout {
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

.layout-left,
.layout-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.layout-center {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.phase-banner {
  padding: 8px 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;
}

.info-card {
  h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
  }
}

.info-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);

  &:last-child {
    border-bottom: none;
  }
}

.info-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.room-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

@media (max-width: 1200px) {
  .room-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }

  .layout-left,
  .layout-right {
    display: none;
  }
}

@media (max-width: 768px) {
  .room-header {
    flex-direction: column;
    padding: 16px;
  }

  .room-title {
    font-size: 20px;
  }

  .header-actions {
    width: 100%;

    .app-button {
      width: 100%;
    }
  }
}
</style>
