<template>
  <div class="character-panel">
    <!-- Header -->
    <div class="panel-header">
      <h4>Participants ({{ participants.length }})</h4>
      <el-button
        v-if="collapsible"
        size="small"
        text
        @click="isCollapsed = !isCollapsed"
      >
        <el-icon>
          <component :is="isCollapsed ? ArrowDown : ArrowUp" />
        </el-icon>
      </el-button>
    </div>

    <!-- Collapsible Content -->
    <Transition name="collapse">
      <div v-if="!isCollapsed" class="panel-content">
        <!-- Character List -->
        <div class="participant-list">
          <div
            v-for="participant in participants"
            :key="participant.id"
            :class="[
              'participant-item',
              { 'is-speaking': isSpeaking(participant.id) }
            ]"
          >
            <!-- Avatar -->
            <div class="participant-avatar">
              <img
                v-if="participant.character_avatar"
                :src="participant.character_avatar"
                :alt="participant.character_name"
                class="avatar-img"
              />
              <div v-else class="avatar-placeholder">
                {{ participant.character_name.charAt(0).toUpperCase() }}
              </div>

              <!-- Speaking indicator -->
              <div v-if="isSpeaking(participant.id)" class="speaking-indicator" />

              <!-- Stance badge -->
              <div v-if="participant.stance" class="stance-badge">
                <el-tag :type="getStanceType(participant.stance)" size="small">
                  {{ getStanceIcon(participant.stance) }}
                </el-tag>
              </div>
            </div>

            <!-- Info -->
            <div class="participant-info">
              <div class="participant-name">{{ participant.character_name }}</div>
              <div class="participant-stats">
                <span class="message-count">
                  <el-icon><ChatDotRound /></el-icon>
                  {{ participant.message_count }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="participant-actions">
              <el-dropdown trigger="click" @command="(cmd) => handleAction(cmd, participant)">
                <AppButton size="small" text>
                  <el-icon><MoreFilled /></el-icon>
                </AppButton>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="view">View Profile</el-dropdown-item>
                    <el-dropdown-item command="mute" v-if="!isMuted(participant.id)">
                      Mute
                    </el-dropdown-item>
                    <el-dropdown-item command="unmute" v-else>
                      Unmute
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>

        <!-- Statistics -->
        <div v-if="showStats" class="panel-stats">
          <div class="stat-row">
            <span class="stat-label">Total Messages</span>
            <span class="stat-value">{{ totalMessages }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Most Active</span>
            <span class="stat-value">{{ mostActiveParticipant }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Avg Messages/Person</span>
            <span class="stat-value">{{ averageMessages }}</span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowDown, ArrowUp, ChatDotRound, MoreFilled } from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Participant } from '@/types'

interface Props {
  participants: Participant[]
  speakingParticipantId?: string
  mutedParticipantIds?: string[]
  showStats?: boolean
  collapsible?: boolean
}

interface Emits {
  viewParticipant: [participant: Participant]
  muteParticipant: [participantId: string]
  unmuteParticipant: [participantId: string]
}

const props = withDefaults(defineProps<Props>(), {
  speakingParticipantId: '',
  mutedParticipantIds: () => [],
  showStats: true,
  collapsible: true
})

const emit = defineEmits<Emits>()

// State
const isCollapsed = ref(false)

// Computed
const totalMessages = computed(() => {
  return props.participants.reduce((sum, p) => sum + p.message_count, 0)
})

const mostActiveParticipant = computed(() => {
  if (props.participants.length === 0) return '-'
  const mostActive = [...props.participants].sort((a, b) => b.message_count - a.message_count)[0]
  return mostActive.character_name
})

const averageMessages = computed(() => {
  if (props.participants.length === 0) return 0
  return (totalMessages.value / props.participants.length).toFixed(1)
})

// Methods
const isSpeaking = (participantId: string) => {
  return props.speakingParticipantId === participantId
}

const isMuted = (participantId: string) => {
  return props.mutedParticipantIds?.includes(participantId)
}

const getStanceType = (stance?: string) => {
  const typeMap: Record<string, any> = {
    pro: 'success',
    con: 'danger',
    neutral: 'info'
  }
  return stance ? typeMap[stance] : ''
}

const getStanceIcon = (stance?: string) => {
  const iconMap: Record<string, string> = {
    pro: '👍',
    con: '👎',
    neutral: '🤝'
  }
  return stance ? iconMap[stance] : ''
}

const handleAction = (command: string, participant: Participant) => {
  switch (command) {
    case 'view':
      emit('viewParticipant', participant)
      break
    case 'mute':
      emit('muteParticipant', participant.id)
      break
    case 'unmute':
      emit('unmuteParticipant', participant.id)
      break
  }
}
</script>

<style scoped lang="scss">
.character-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.participant-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background-color: white;
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s ease;

  &.is-speaking {
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
  }
}

.participant-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
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

.speaking-indicator {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background-color: var(--el-color-success);
  border: 2px solid white;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

.stance-badge {
  position: absolute;
  bottom: -4px;
  left: -4px;
  transform: scale(0.8);
}

.participant-info {
  flex: 1;
  min-width: 0;
}

.participant-name {
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.participant-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.message-count {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  color: var(--el-text-color-secondary);

  .el-icon {
    font-size: 12px;
  }
}

.participant-actions {
  flex-shrink: 0;
}

.panel-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.stat-label {
  color: var(--el-text-color-secondary);
}

.stat-value {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  max-height: 500px;
  opacity: 1;
}

@media (max-width: 768px) {
  .character-panel {
    padding: 12px;
  }

  .participant-item {
    padding: 8px;
  }
}
</style>
