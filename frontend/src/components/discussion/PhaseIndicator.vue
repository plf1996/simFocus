<template>
  <div class="phase-indicator">
    <div class="phase-icon">
      <component :is="phaseIcon" />
    </div>
    <div class="phase-content">
      <div class="phase-name">{{ phaseText }}</div>
      <div v-if="showRound" class="phase-round">Round {{ round }}</div>
    </div>
    <div v-if="showProgress" class="phase-progress">
      <div
        v-for="(p, index) in phases"
        :key="index"
        :class="['progress-step', { 'is-active': p === phase, 'is-completed': isCompleted(p) }]"
      >
        <div class="step-dot" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  ChatDotRound,
  TrendCharts,
  Lightbulb,
  CircleCheck
} from '@element-plus/icons-vue'
import type { DiscussionPhase } from '@/types'

interface Props {
  phase: DiscussionPhase
  round?: number
  showRound?: boolean
  showProgress?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showRound: true,
  showProgress: false
})

const phases: DiscussionPhase[] = ['opening', 'development', 'debate', 'closing']

const phaseIcon = computed(() => {
  const iconMap: Record<DiscussionPhase, any> = {
    opening: ChatDotRound,
    development: TrendCharts,
    debate: Lightbulb,
    closing: CircleCheck
  }
  return iconMap[props.phase]
})

const phaseText = computed(() => {
  const textMap: Record<DiscussionPhase, string> = {
    opening: 'Opening Phase',
    development: 'Development Phase',
    debate: 'Debate Phase',
    closing: 'Closing Phase'
  }
  return textMap[props.phase]
})

const isCompleted = (p: DiscussionPhase) => {
  const currentIndex = phases.indexOf(props.phase)
  const checkIndex = phases.indexOf(p)
  return checkIndex < currentIndex
}
</script>

<style scoped lang="scss">
.phase-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--el-color-primary-light-9), var(--el-fill-color-light));
  border-radius: 20px;
  border: 1px solid var(--el-color-primary-light-5);
}

.phase-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--el-color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  .el-icon {
    font-size: 18px;
  }
}

.phase-content {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.phase-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.phase-round {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.phase-progress {
  display: flex;
  gap: 6px;
}

.progress-step {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--el-border-color);
  transition: all 0.3s ease;

  &.is-completed {
    background-color: var(--el-color-success);
  }

  &.is-active {
    background-color: var(--el-color-primary);
    transform: scale(1.3);
  }

  .step-dot {
    width: 100%;
    height: 100%;
    border-radius: 50%;
  }
}

@media (max-width: 768px) {
  .phase-indicator {
    padding: 6px 12px;
  }

  .phase-icon {
    width: 28px;
    height: 28px;

    .el-icon {
      font-size: 16px;
    }
  }

  .phase-name {
    font-size: 13px;
  }
}
</style>
