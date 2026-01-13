<template>
  <AppCard
    :class="['topic-card', { 'is-clickable': clickable, 'is-active': isActive }]"
    :hoverable="clickable"
    @click="handleClick"
  >
    <!-- Header -->
    <template #header>
      <div class="topic-card-header">
        <div class="topic-title">
          <h4>{{ topic.title }}</h4>
          <el-tag v-if="showStatus" :type="statusType" size="small">
            {{ statusText }}
          </el-tag>
        </div>
        <el-dropdown v-if="showActions" trigger="click" @command="handleAction">
          <AppButton type="text" circle>
            <el-icon><MoreFilled /></el-icon>
          </AppButton>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="view">View Details</el-dropdown-item>
              <el-dropdown-item command="edit">Edit</el-dropdown-item>
              <el-dropdown-item command="duplicate">Duplicate</el-dropdown-item>
              <el-dropdown-item command="delete" divided>Delete</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </template>

    <!-- Body -->
    <div class="topic-card-body">
      <!-- Description -->
      <p v-if="topic.description" class="topic-description">
        {{ truncatedDescription }}
      </p>

      <!-- Context Preview -->
      <div v-if="topic.context" class="topic-context">
        <el-icon><InfoFilled /></el-icon>
        <span>{{ truncatedContext }}</span>
      </div>

      <!-- Attachments -->
      <div v-if="hasAttachments" class="topic-attachments">
        <el-icon><Paperclip /></el-icon>
        <span>{{ topic.attachments?.length }} attachment(s)</span>
      </div>

      <!-- Metadata -->
      <div class="topic-meta">
        <div class="meta-item">
          <el-icon><Calendar /></el-icon>
          <span>{{ formatDate(topic.created_at) }}</span>
        </div>
        <div v-if="discussionCount > 0" class="meta-item">
          <el-icon><ChatDotRound /></el-icon>
          <span>{{ discussionCount }} discussion(s)</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <template v-if="showFooter" #footer>
      <div class="topic-card-footer">
        <slot name="footer">
          <AppButton type="primary" size="small" @click.stop="handleStart">
            Start Discussion
          </AppButton>
        </slot>
      </div>
    </template>
  </AppCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MoreFilled, InfoFilled, Paperclip, Calendar, ChatDotRound } from '@element-plus/icons-vue'
import AppCard from '@/components/common/AppCard.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Topic, TopicStatus } from '@/types'

interface Props {
  topic: Topic
  clickable?: boolean
  showStatus?: boolean
  showActions?: boolean
  showFooter?: boolean
  discussionCount?: number
  isActive?: boolean
}

interface Emits {
  click: [topic: Topic]
  action: [action: string, topic: Topic]
  start: [topic: Topic]
}

const props = withDefaults(defineProps<Props>(), {
  clickable: true,
  showStatus: true,
  showActions: true,
  showFooter: false,
  discussionCount: 0,
  isActive: false
})

const emit = defineEmits<Emits>()

// Computed
const truncatedDescription = computed(() => {
  if (!props.topic.description) return ''
  return props.topic.description.length > 150
    ? props.topic.description.slice(0, 150) + '...'
    : props.topic.description
})

const truncatedContext = computed(() => {
  if (!props.topic.context) return ''
  return props.topic.context.length > 100
    ? props.topic.context.slice(0, 100) + '...'
    : props.topic.context
})

const hasAttachments = computed(() => {
  return props.topic.attachments && props.topic.attachments.length > 0
})

const statusType = computed(() => {
  const statusMap: Record<TopicStatus, any> = {
    draft: 'info',
    ready: 'success',
    in_discussion: 'warning',
    completed: ''
  }
  return statusMap[props.topic.status]
})

const statusText = computed(() => {
  const textMap: Record<TopicStatus, string> = {
    draft: 'Draft',
    ready: 'Ready',
    in_discussion: 'In Discussion',
    completed: 'Completed'
  }
  return textMap[props.topic.status]
})

// Methods
const handleClick = () => {
  if (props.clickable) {
    emit('click', props.topic)
  }
}

const handleAction = (command: string) => {
  emit('action', command, props.topic)
}

const handleStart = () => {
  emit('start', props.topic)
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return 'Today'
  } else if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7)
    return `${weeks} week${weeks > 1 ? 's' : ''} ago`
  } else {
    return date.toLocaleDateString()
  }
}
</script>

<style scoped lang="scss">
.topic-card {
  transition: all 0.3s ease;

  &.is-clickable {
    cursor: pointer;
  }

  &.is-active {
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
  }
}

.topic-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
}

.topic-title {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;

  h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    line-height: 1.4;
    flex: 1;
  }
}

.topic-card-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.topic-description {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  line-height: 1.6;
}

.topic-context {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  font-size: 13px;
  color: var(--el-text-color-regular);

  .el-icon {
    margin-top: 2px;
    color: var(--el-color-primary);
  }

  span {
    flex: 1;
    line-height: 1.5;
  }
}

.topic-attachments {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);

  .el-icon {
    font-size: 14px;
  }
}

.topic-card-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
