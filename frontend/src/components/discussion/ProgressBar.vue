<template>
  <div class="progress-bar">
    <div class="progress-header">
      <span class="progress-label">{{ label }}</span>
      <span class="progress-value">{{ progressText }}</span>
    </div>
    <div class="progress-track">
      <div
        class="progress-fill"
        :style="{ width: `${progress}%` }"
      >
        <div v-if="animated" class="progress-shimmer" />
      </div>
    </div>
    <div v-if="showDetails" class="progress-details">
      <span>{{ roundText }}</span>
      <span v-if="estimatedTime" class="estimated-time">
        <el-icon><Clock /></el-icon>
        {{ estimatedTime }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Clock } from '@element-plus/icons-vue'

interface Props {
  current: number
  max: number
  label?: string
  showDetails?: boolean
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Progress',
  showDetails: true,
  animated: true
})

const progress = computed(() => {
  if (props.max === 0) return 0
  return Math.min((props.current / props.max) * 100, 100)
})

const progressText = computed(() => {
  return `${props.current} / ${props.max}`
})

const roundText = computed(() => {
  return `Round ${props.current} of ${props.max}`
})

const estimatedTime = computed(() => {
  if (props.current >= props.max) return null

  const remaining = props.max - props.current
  const avgTimePerRound = 30 // seconds, estimate
  const totalSeconds = remaining * avgTimePerRound

  if (totalSeconds < 60) {
    return `~${totalSeconds}s remaining`
  } else {
    const minutes = Math.ceil(totalSeconds / 60)
    return `~${minutes}min remaining`
  }
})
</script>

<style scoped lang="scss">
.progress-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
}

.progress-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-color-primary);
}

.progress-track {
  position: relative;
  height: 8px;
  background-color: var(--el-fill-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  position: relative;
  height: 100%;
  background: linear-gradient(90deg, var(--el-color-primary), var(--el-color-success));
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-shimmer {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

.progress-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.estimated-time {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--el-color-success);

  .el-icon {
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .progress-label {
    font-size: 12px;
  }

  .progress-value {
    font-size: 13px;
  }
}
</style>
