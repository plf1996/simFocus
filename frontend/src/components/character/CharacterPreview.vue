<template>
  <div class="character-preview">
    <!-- Character Profile -->
    <div class="profile-section">
      <div class="profile-header">
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
        </div>
        <div class="profile-info">
          <h3 class="character-name">{{ character.name }}</h3>
          <p class="character-profession">{{ character.config.profession }}</p>
          <div class="profile-tags">
            <el-tag :type="stanceType" size="small">
              {{ stanceText }}
            </el-tag>
            <el-tag type="info" size="small">
              {{ character.config.expression_style }}
            </el-tag>
            <el-tag type="info" size="small">
              {{ character.config.behavior_pattern }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div v-if="showStats" class="profile-stats">
        <div class="stat-item">
          <span class="stat-label">Usage</span>
          <span class="stat-value">{{ character.usage_count }}</span>
        </div>
        <div v-if="character.rating_avg" class="stat-item">
          <span class="stat-label">Rating</span>
          <div class="stat-rating">
            <el-rate
              :model-value="character.rating_avg"
              disabled
              size="small"
            />
            <span class="rating-count">({{ character.rating_count }})</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Personality Visualization -->
    <div class="personality-section">
      <h4>Personality Profile</h4>
      <div class="personality-chart">
        <div
          v-for="(value, key) in personalityTraits"
          :key="key"
          class="personality-bar"
        >
          <div class="bar-label">{{ formatTraitName(key) }}</div>
          <div class="bar-wrapper">
            <div
              class="bar-fill"
              :style="{ width: `${(value / 10) * 100}%` }"
            />
          </div>
          <div class="bar-value">{{ value }}/10</div>
        </div>
      </div>
    </div>

    <!-- Knowledge & Expertise -->
    <div class="knowledge-section">
      <h4>Knowledge & Expertise</h4>
      <div class="knowledge-grid">
        <div class="knowledge-item">
          <span class="item-label">Fields:</span>
          <div class="item-value">
            <el-tag
              v-for="field in character.config.knowledge.fields"
              :key="field"
              size="small"
              class="field-tag"
            >
              {{ field }}
            </el-tag>
          </div>
        </div>
        <div class="knowledge-item">
          <span class="item-label">Experience:</span>
          <span class="item-value">
            {{ character.config.knowledge.experience_years }} years
          </span>
        </div>
        <div v-if="hasRepresentativeViews" class="knowledge-item">
          <span class="item-label">Views:</span>
          <ul class="views-list">
            <li
              v-for="(view, index) in character.config.knowledge.representative_views"
              :key="index"
            >
              {{ view }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Discussion Behavior -->
    <div v-if="showBehavior" class="behavior-section">
      <h4>Discussion Behavior</h4>
      <div class="behavior-grid">
        <div class="behavior-item">
          <div class="behavior-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="behavior-content">
            <div class="behavior-label">Speaking Style</div>
            <div class="behavior-value">{{ formatExpressionStyle(character.config.expression_style) }}</div>
            <div class="behavior-desc">{{ getExpressionStyleDesc(character.config.expression_style) }}</div>
          </div>
        </div>
        <div class="behavior-item">
          <div class="behavior-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="behavior-content">
            <div class="behavior-label">Participation</div>
            <div class="behavior-value">{{ formatBehaviorPattern(character.config.behavior_pattern) }}</div>
            <div class="behavior-desc">{{ getBehaviorPatternDesc(character.config.behavior_pattern) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div v-if="showActions" class="actions-section">
      <AppButton type="primary" block @click="handleSelect">
        Select Character
      </AppButton>
      <AppButton block @click="handleEdit">
        Edit
      </AppButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ChatDotRound, TrendCharts } from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Character, DiscussionStance } from '@/types'

interface Props {
  character: Character
  showStats?: boolean
  showBehavior?: boolean
  showActions?: boolean
}

interface Emits {
  select: [character: Character]
  edit: [character: Character]
}

const props = withDefaults(defineProps<Props>(), {
  showStats: true,
  showBehavior: true,
  showActions: true
})

const emit = defineEmits<Emits>()

// Computed
const personalityTraits = computed(() => {
  return {
    openness: props.character.config.personality.openness,
    rigor: props.character.config.personality.rigor,
    critical_thinking: props.character.config.personality.critical_thinking,
    optimism: props.character.config.personality.optimism
  }
})

const hasRepresentativeViews = computed(() => {
  return props.character.config.knowledge.representative_views &&
    props.character.config.knowledge.representative_views.length > 0
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
    critical_exploration: 'Critical Explorer'
  }
  return textMap[props.character.config.stance]
})

// Methods
const formatTraitName = (key: string) => {
  const nameMap: Record<string, string> = {
    openness: 'Openness',
    rigor: 'Rigor',
    critical_thinking: 'Critical Thinking',
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

const getExpressionStyleDesc = (style: string) => {
  const descMap: Record<string, string> = {
    formal: 'Uses professional language, structured arguments',
    casual: 'Conversational tone, relatable examples',
    technical: 'Detailed explanations, domain-specific terminology',
    storytelling: 'Uses narratives and analogies to illustrate points'
  }
  return descMap[style] || ''
}

const formatBehaviorPattern = (pattern: string) => {
  const patternMap: Record<string, string> = {
    active: 'Active Speaker',
    passive: 'Passive Listener',
    balanced: 'Balanced'
  }
  return patternMap[pattern] || pattern
}

const getBehaviorPatternDesc = (pattern: string) => {
  const descMap: Record<string, string> = {
    active: 'Frequently initiates discussions and presents new ideas',
    passive: 'Responds when addressed, focuses on thoughtful answers',
    balanced: 'Mixes initiating and responding appropriately'
  }
  return descMap[pattern] || ''
}

const handleSelect = () => {
  emit('select', props.character)
}

const handleEdit = () => {
  emit('edit', props.character)
}
</script>

<style scoped lang="scss">
.character-preview {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-section {
  padding: 20px;
  background: linear-gradient(135deg, var(--el-color-primary-light-9), var(--el-fill-color-light));
  border-radius: 8px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.avatar-wrapper {
  flex-shrink: 0;
}

.character-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid white;
  box-shadow: var(--el-box-shadow-light);

  &.avatar-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-success));
    color: white;
    font-size: 32px;
    font-weight: 600;
  }
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.character-name {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.character-profession {
  margin: 0 0 8px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-color-primary);
}

.stat-rating {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rating-count {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.personality-section,
.knowledge-section,
.behavior-section {
  padding: 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;

  h4 {
    margin: 0 0 16px;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--el-text-color-secondary);
  }
}

.personality-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.personality-bar {
  display: grid;
  grid-template-columns: 120px 1fr 60px;
  align-items: center;
  gap: 12px;
}

.bar-label {
  font-size: 13px;
  font-weight: 500;
}

.bar-wrapper {
  height: 8px;
  background-color: var(--el-fill-color);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--el-color-primary), var(--el-color-success));
  transition: width 0.3s ease;
}

.bar-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-color-primary);
  text-align: right;
}

.knowledge-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.knowledge-item {
  display: flex;
  gap: 12px;
  font-size: 13px;

  .item-label {
    min-width: 80px;
    font-weight: 600;
    color: var(--el-text-color-secondary);
  }

  .item-value {
    flex: 1;
  }
}

.field-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.views-list {
  margin: 0;
  padding-left: 20px;

  li {
    margin-bottom: 4px;
    color: var(--el-text-color-regular);
  }
}

.behavior-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.behavior-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background-color: white;
  border-radius: 6px;
  border: 1px solid var(--el-border-color-light);
}

.behavior-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--el-color-primary-light-9);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  .el-icon {
    font-size: 18px;
    color: var(--el-color-primary);
  }
}

.behavior-content {
  flex: 1;
}

.behavior-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 2px;
}

.behavior-value {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.behavior-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.actions-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
