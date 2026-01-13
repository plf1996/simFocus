<template>
  <AppCard
    :class="['character-card', { 'is-clickable': clickable, 'is-selected': selected }]"
    :hoverable="clickable"
    @click="handleClick"
  >
    <!-- Header -->
    <div class="character-header">
      <div class="avatar-wrapper">
        <img
          v-if="character.avatar_url"
          :src="character.avatar_url"
          :alt="character.name"
          class="character-avatar"
        />
        <div v-else class="character-avatar avatar-placeholder">
          {{ character.name.charAt(0).toUpperCase() }}
        </div>
        <div v-if="character.is_template" class="template-badge">
          <el-icon><Star /></el-icon>
        </div>
      </div>
      <div class="character-info">
        <h4 class="character-name">{{ character.name }}</h4>
        <p class="character-profession">{{ character.config.profession }}</p>
      </div>
      <el-checkbox v-if="showCheckbox" :model-value="selected" @change="handleSelect" />
    </div>

    <!-- Body -->
    <div class="character-body">
      <!-- Personality Traits -->
      <div class="traits-section">
        <div class="trait-label">Personality</div>
        <div class="traits-grid">
          <div v-for="(value, key) in displayTraits" :key="key" class="trait-item">
            <span class="trait-name">{{ formatTraitName(key) }}</span>
            <el-rate
              :model-value="value"
              disabled
              show-score
              text-color="#ff9900"
              :max="10"
              size="small"
            />
          </div>
        </div>
      </div>

      <!-- Knowledge & Stance -->
      <div class="meta-section">
        <div class="meta-item">
          <el-icon><Reading /></el-icon>
          <span>{{ character.config.knowledge.fields.join(', ') }}</span>
        </div>
        <div class="meta-item">
          <el-icon><ChatLineRound /></el-icon>
          <el-tag :type="stanceType" size="small">{{ stanceText }}</el-tag>
        </div>
        <div class="meta-item">
          <el-icon><MagicStick /></el-icon>
          <span>{{ formatExpressionStyle(character.config.expression_style) }}</span>
        </div>
      </div>

      <!-- Stats -->
      <div v-if="showStats" class="stats-section">
        <div class="stat-item">
          <el-icon><User /></el-icon>
          <span>{{ character.usage_count }} uses</span>
        </div>
        <div v-if="character.rating_avg" class="stat-item">
          <el-rate
            :model-value="character.rating_avg"
            disabled
            size="small"
          />
          <span class="rating-text">({{ character.rating_count }})</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div v-if="showActions" class="character-actions">
      <el-button-group>
        <AppButton size="small" @click.stop="handleEdit">
          <el-icon><Edit /></el-icon>
          Edit
        </AppButton>
        <AppButton size="small" @click.stop="handleDuplicate">
          <el-icon><CopyDocument /></el-icon>
          Duplicate
        </AppButton>
        <AppButton
          size="small"
          type="danger"
          @click.stop="handleDelete"
        >
          <el-icon><Delete /></el-icon>
        </AppButton>
      </el-button-group>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Star,
  Reading,
  ChatLineRound,
  MagicStick,
  User,
  Edit,
  CopyDocument,
  Delete
} from '@element-plus/icons-vue'
import AppCard from '@/components/common/AppCard.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Character, DiscussionStance } from '@/types'

interface Props {
  character: Character
  clickable?: boolean
  selected?: boolean
  showCheckbox?: boolean
  showStats?: boolean
  showActions?: boolean
}

interface Emits {
  click: [character: Character]
  select: [character: Character, selected: boolean]
  edit: [character: Character]
  duplicate: [character: Character]
  delete: [character: Character]
}

const props = withDefaults(defineProps<Props>(), {
  clickable: true,
  selected: false,
  showCheckbox: false,
  showStats: true,
  showActions: false
})

const emit = defineEmits<Emits>()

// Computed
const displayTraits = computed(() => {
  return {
    openness: props.character.config.personality.openness,
    rigor: props.character.config.personality.rigor,
    critical: props.character.config.personality.critical_thinking,
    optimism: props.character.config.personality.optimism
  }
})

const stanceType = computed(() => {
  const typeMap: Record<DiscussionStance, any> = {
    support: 'success',
    oppose: 'danger',
    neutral: 'info',
    critical_exploration: 'warning'
  }
  return typeMap[props.character.config.stance]
})

const stanceText = computed(() => {
  const textMap: Record<DiscussionStance, string> = {
    support: 'Supportive',
    oppose: 'Opposing',
    neutral: 'Neutral',
    critical_exploration: 'Critical'
  }
  return textMap[props.character.config.stance]
})

// Methods
const handleClick = () => {
  if (props.clickable) {
    emit('click', props.character)
  }
}

const handleSelect = (checked: boolean) => {
  emit('select', props.character, checked)
}

const handleEdit = () => {
  emit('edit', props.character)
}

const handleDuplicate = () => {
  emit('duplicate', props.character)
}

const handleDelete = () => {
  emit('delete', props.character)
}

const formatTraitName = (key: string) => {
  const nameMap: Record<string, string> = {
    openness: 'Openness',
    rigor: 'Rigor',
    critical: 'Critical Thinking',
    optimism: 'Optimism'
  }
  return nameMap[key] || key
}

const formatExpressionStyle = (style: string) => {
  const styleMap: Record<string, string> = {
    formal: 'Formal',
    casual: 'Casual',
    technical: 'Technical',
    storytelling: 'Storytelling'
  }
  return styleMap[style] || style
}
</script>

<style scoped lang="scss">
.character-card {
  transition: all 0.3s ease;

  &.is-clickable {
    cursor: pointer;
  }

  &.is-selected {
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
  }
}

.character-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.character-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--el-border-color);
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-success));
  color: white;
  font-size: 24px;
  font-weight: 600;
}

.template-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 20px;
  height: 20px;
  background-color: var(--el-color-warning);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;

  .el-icon {
    font-size: 12px;
    color: white;
  }
}

.character-info {
  flex: 1;
  min-width: 0;
}

.character-name {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.character-profession {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.character-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.traits-section {
  .trait-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--el-text-color-secondary);
    margin-bottom: 8px;
  }
}

.traits-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.trait-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;

  .trait-name {
    min-width: 80px;
    color: var(--el-text-color-regular);
  }

  :deep(.el-rate) {
    flex: 1;
  }
}

.meta-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--el-text-color-secondary);

  .el-icon {
    font-size: 14px;
  }

  span {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.stats-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);

  .rating-text {
    margin-left: 4px;
  }
}

.character-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>
