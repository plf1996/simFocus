<template>
  <div class="discussion-controls">
    <!-- Main Controls -->
    <div class="controls-main">
      <!-- Play/Pause -->
      <AppButton
        v-if="status === 'running' || status === 'paused'"
        :type="isActive ? 'warning' : 'success'"
        :icon="isActive ? VideoPause : VideoPlay"
        size="large"
        circle
        @click="handlePlayPause"
      />

      <!-- Stop -->
      <AppButton
        v-if="status === 'running' || status === 'paused'"
        type="danger"
        :icon="VideoStop"
        size="large"
        circle
        @click="handleStop"
      />

      <!-- Start -->
      <AppButton
        v-else
        type="primary"
        :icon="VideoPlay"
        size="large"
        circle
        :loading="isStarting"
        @click="handleStart"
      />
    </div>

    <!-- Secondary Controls -->
    <div class="controls-secondary">
      <!-- Speed Control -->
      <el-dropdown trigger="click" @command="handleSpeedChange">
        <AppButton size="small">
          <el-icon><Timer /></el-icon>
          {{ currentSpeed }}x
        </AppButton>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="speed in speeds"
              :key="speed"
              :command="speed"
              :disabled="speed === currentSpeed"
            >
              {{ speed }}x
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- Inject Question -->
      <AppButton size="small" @click="handleInjectQuestion">
        <el-icon><ChatLineRound /></el-icon>
        Inject Question
      </AppButton>

      <!-- More Options -->
      <el-dropdown trigger="click" @command="handleMoreAction">
        <AppButton size="small" :icon="MoreFilled" circle />
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="restart">
              <el-icon><RefreshRight /></el-icon>
              Restart Discussion
            </el-dropdown-item>
            <el-dropdown-item command="export">
              <el-icon><Download /></el-icon>
              Export Messages
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              Settings
            </el-dropdown-item>
            <el-dropdown-item command="report" divided>
              <el-icon><Document /></el-icon>
              Generate Report
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- Status Indicator -->
    <div v-if="showStatus" class="status-indicator">
      <el-tag :type="statusType" size="small">
        {{ statusText }}
      </el-tag>
    </div>

    <!-- Inject Question Dialog -->
    <el-dialog
      v-model="showInjectDialog"
      title="Inject Question into Discussion"
      width="500px"
    >
      <el-form label-position="top">
        <el-form-item label="Your Question">
          <AppInput
            v-model="injectQuestion"
            type="textarea"
            placeholder="Enter a question or comment to inject into the discussion..."
            :rows="4"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <AppButton @click="showInjectDialog = false">Cancel</AppButton>
        <AppButton
          type="primary"
          :disabled="!injectQuestion.trim()"
          @click="handleConfirmInject"
        >
          Inject
        </AppButton>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  VideoPlay,
  VideoPause,
  VideoStop,
  Timer,
  ChatLineRound,
  MoreFilled,
  RefreshRight,
  Download,
  Setting,
  Document
} from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'
import AppInput from '@/components/common/AppInput.vue'
import type { DiscussionStatus } from '@/types'

interface Props {
  status: DiscussionStatus
  isActive?: boolean
  showStatus?: boolean
}

interface Emits {
  start: []
  pause: []
  resume: []
  stop: []
  restart: []
  speedChange: [speed: number]
  injectQuestion: [question: string]
  export: []
  settings: []
  report: []
}

const props = withDefaults(defineProps<Props>(), {
  isActive: false,
  showStatus: true
})

const emit = defineEmits<Emits>()

// State
const currentSpeed = ref(1.0)
const speeds = [1.0, 1.5, 2.0, 3.0]
const showInjectDialog = ref(false)
const injectQuestion = ref('')
const isStarting = ref(false)

// Computed
const statusType = computed(() => {
  const typeMap: Record<DiscussionStatus, any> = {
    initialized: 'info',
    running: 'success',
    paused: 'warning',
    completed: '',
    failed: 'danger',
    cancelled: 'info'
  }
  return typeMap[props.status]
})

const statusText = computed(() => {
  const textMap: Record<DiscussionStatus, string> = {
    initialized: 'Ready to Start',
    running: 'In Progress',
    paused: 'Paused',
    completed: 'Completed',
    failed: 'Failed',
    cancelled: 'Cancelled'
  }
  return textMap[props.status]
})

// Methods
const handleStart = async () => {
  isStarting.value = true
  try {
    await ElMessageBox.confirm(
      'Start the discussion with the selected participants?',
      'Start Discussion',
      {
        type: 'info',
        confirmButtonText: 'Start'
      }
    )
    emit('start')
  } catch {
    // Cancelled
  } finally {
    isStarting.value = false
  }
}

const handlePlayPause = () => {
  if (props.isActive) {
    emit('pause')
  } else {
    emit('resume')
  }
}

const handleStop = async () => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to stop this discussion? This action cannot be undone.',
      'Stop Discussion',
      {
        type: 'warning',
        confirmButtonText: 'Stop',
        confirmButtonClass: 'el-button--danger'
      }
    )
    emit('stop')
  } catch {
    // Cancelled
  }
}

const handleSpeedChange = (speed: number) => {
  currentSpeed.value = speed
  emit('speedChange', speed)
  ElMessage.success(`Playback speed set to ${speed}x`)
}

const handleInjectQuestion = () => {
  injectQuestion.value = ''
  showInjectDialog.value = true
}

const handleConfirmInject = () => {
  if (injectQuestion.value.trim()) {
    emit('injectQuestion', injectQuestion.value.trim())
    showInjectDialog.value = false
    injectQuestion.value = ''
    ElMessage.success('Question injected into discussion')
  }
}

const handleMoreAction = async (command: string) => {
  switch (command) {
    case 'restart':
      try {
        await ElMessageBox.confirm(
          'Restart the discussion from the beginning?',
          'Restart Discussion',
          {
            type: 'warning',
            confirmButtonText: 'Restart'
          }
        )
        emit('restart')
      } catch {
        // Cancelled
      }
      break

    case 'export':
      emit('export')
      ElMessage.success('Messages exported')
      break

    case 'settings':
      emit('settings')
      break

    case 'report':
      emit('report')
      ElMessage.info('Generating discussion report...')
      break
  }
}
</script>

<style scoped lang="scss">
.discussion-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;
}

.controls-main {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.controls-secondary {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.status-indicator {
  display: flex;
  justify-content: center;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}

@media (max-width: 768px) {
  .discussion-controls {
    padding: 12px;
  }

  .controls-main {
    gap: 12px;
  }

  .controls-secondary {
    flex-direction: column;

    .app-button {
      width: 100%;
    }
  }
}
</style>
