<template>
  <div class="character-selector">
    <!-- Selection Summary -->
    <div class="selection-header">
      <div class="selection-info">
        <span class="label">Selected:</span>
        <span class="count">{{ selectedCharacters.length }} / {{ maxSelection }}</span>
      </div>
      <div class="selection-actions">
        <AppButton
          v-if="selectedCharacters.length > 0"
          size="small"
          text
          @click="handleClearAll"
        >
          Clear All
        </AppButton>
      </div>
    </div>

    <!-- Selected Characters Preview -->
    <div v-if="selectedCharacters.length > 0" class="selected-preview">
      <div
        v-for="character in selectedCharacters"
        :key="character.id"
        class="selected-item"
      >
        <img
          v-if="character.avatar_url"
          :src="character.avatar_url"
          :alt="character.name"
          class="selected-avatar"
        />
        <div v-else class="selected-avatar avatar-placeholder">
          {{ character.name.charAt(0).toUpperCase() }}
        </div>
        <span class="selected-name">{{ character.name }}</span>
        <AppButton
          type="danger"
          size="small"
          text
          @click="handleRemove(character)"
        >
          <el-icon><Close /></el-icon>
        </AppButton>
      </div>
    </div>

    <!-- Library Tab -->
    <el-tabs v-model="activeTab" class="selector-tabs">
      <!-- Character Library -->
      <el-tab-pane label="Library" name="library">
        <div class="library-content">
          <!-- Filters -->
          <div class="library-filters">
            <el-input
              v-model="searchQuery"
              placeholder="Search characters..."
              :prefix-icon="Search"
              clearable
              size="small"
              class="search-input"
            />

            <el-select
              v-model="filterStance"
              placeholder="Stance"
              clearable
              size="small"
              class="filter-select"
            >
              <el-option label="Supportive" value="support" />
              <el-option label="Opposing" value="oppose" />
              <el-option label="Neutral" value="neutral" />
              <el-option label="Critical" value="critical_exploration" />
            </el-select>

            <el-select
              v-model="filterProfession"
              placeholder="Profession"
              clearable
              size="small"
              class="filter-select"
            >
              <el-option
                v-for="profession in professions"
                :key="profession"
                :label="profession"
                :value="profession"
              />
            </el-select>
          </div>

          <!-- Character Grid -->
          <div v-if="isLoading" class="loading-state">
            <el-skeleton :rows="3" animated />
          </div>

          <div v-else-if="filteredCharacters.length === 0" class="empty-state">
            <el-empty description="No characters found" />
          </div>

          <div v-else class="character-grid">
            <div
              v-for="character in filteredCharacters"
              :key="character.id"
              :class="['character-item', { 'is-selected': isSelected(character.id) }]"
              @click="handleToggleCharacter(character)"
            >
              <div class="character-avatar-wrapper">
                <img
                  v-if="character.avatar_url"
                  :src="character.avatar_url"
                  :alt="character.name"
                  class="character-avatar"
                />
                <div v-else class="character-avatar avatar-placeholder">
                  {{ character.name.charAt(0).toUpperCase() }}
                </div>
                <el-checkbox
                  :model-value="isSelected(character.id)"
                  @click.stop
                />
              </div>
              <div class="character-details">
                <div class="character-name">{{ character.name }}</div>
                <div class="character-profession">{{ character.config.profession }}</div>
                <div class="character-tags">
                  <el-tag size="small" :type="getStanceType(character.config.stance)">
                    {{ getStanceText(character.config.stance) }}
                  </el-tag>
                  <el-tag size="small" type="info">
                    {{ character.config.expression_style }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Create Custom -->
      <el-tab-pane label="Create Custom" name="create">
        <div class="create-content">
          <CharacterEditor
            @save="handleCreateCharacter"
            @cancel="activeTab = 'library'"
          />
        </div>
      </el-tab-pane>

      <!-- AI Recommend -->
      <el-tab-pane label="AI Recommend" name="recommend">
        <div class="recommend-content">
          <div class="recommend-form">
            <el-form label-position="top">
              <el-form-item label="Topic Description">
                <AppInput
                  v-model="topicDescription"
                  type="textarea"
                  placeholder="Describe your topic to get AI character recommendations..."
                  :rows="4"
                />
              </el-form-item>
              <AppButton
                type="primary"
                :loading="isRecommending"
                @click="handleGetRecommendations"
              >
                Get Recommendations
              </AppButton>
            </el-form>
          </div>

          <div v-if="recommendations.length > 0" class="recommendations-list">
            <h5>Recommended Characters</h5>
            <div
              v-for="rec in recommendations"
              :key="rec.id"
              class="recommendation-item"
            >
              <div class="rec-info">
                <div class="rec-name">{{ rec.name }}</div>
                <div class="rec-reason">{{ rec.reason }}</div>
              </div>
              <AppButton
                size="small"
                :type="isSelected(rec.id) ? 'primary' : 'default'"
                @click="handleToggleCharacter(rec)"
              >
                {{ isSelected(rec.id) ? 'Selected' : 'Add' }}
              </AppButton>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search, Close } from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'
import AppInput from '@/components/common/AppInput.vue'
import CharacterEditor from './CharacterEditor.vue'
import type { Character, DiscussionStance } from '@/types'

interface Props {
  modelValue: Character[]
  maxSelection?: number
  characters?: Character[]
}

interface Emits {
  'update:modelValue': [characters: Character[]]
}

const props = withDefaults(defineProps<Props>(), {
  maxSelection: 7,
  characters: () => []
})

const emit = defineEmits<Emits>()

// State
const selectedCharacters = ref<Character[]>([...props.modelValue])
const activeTab = ref('library')
const searchQuery = ref('')
const filterStance = ref('')
const filterProfession = ref('')
const isLoading = ref(false)
const isRecommending = ref(false)
const topicDescription = ref('')
const recommendations = ref<Character[]>([])

// Computed
const professions = computed(() => {
  const profSet = new Set(props.characters.map(c => c.config.profession))
  return Array.from(profSet).sort()
})

const filteredCharacters = computed(() => {
  let result = [...props.characters]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(c =>
      c.name.toLowerCase().includes(query) ||
      c.config.profession.toLowerCase().includes(query)
    )
  }

  // Stance filter
  if (filterStance.value) {
    result = result.filter(c => c.config.stance === filterStance.value)
  }

  // Profession filter
  if (filterProfession.value) {
    result = result.filter(c => c.config.profession === filterProfession.value)
  }

  return result
})

// Methods
const isSelected = (characterId: string) => {
  return selectedCharacters.value.some(c => c.id === characterId)
}

const handleToggleCharacter = (character: Character) => {
  const index = selectedCharacters.value.findIndex(c => c.id === character.id)

  if (index !== -1) {
    // Remove
    selectedCharacters.value.splice(index, 1)
  } else {
    // Add
    if (selectedCharacters.value.length >= props.maxSelection) {
      ElMessage.warning(`Maximum ${props.maxSelection} characters allowed`)
      return
    }
    selectedCharacters.value.push(character)
  }

  emitValue()
}

const handleRemove = (character: Character) => {
  const index = selectedCharacters.value.findIndex(c => c.id === character.id)
  if (index !== -1) {
    selectedCharacters.value.splice(index, 1)
    emitValue()
  }
}

const handleClearAll = () => {
  selectedCharacters.value = []
  emitValue()
}

const handleCreateCharacter = (character: Character) => {
  selectedCharacters.value.push(character)
  emitValue()
  activeTab.value = 'library'
}

const handleGetRecommendations = async () => {
  if (!topicDescription.value.trim()) {
    ElMessage.warning('Please enter a topic description')
    return
  }

  isRecommending.value = true
  try {
    // TODO: Implement actual API call
    // const recs = await characterApi.getRecommendations(topicDescription.value)
    // recommendations.value = recs

    // Mock recommendations
    recommendations.value = props.characters.slice(0, 3)

    ElMessage.success('Recommendations generated')
  } catch (error) {
    ElMessage.error('Failed to get recommendations')
  } finally {
    isRecommending.value = false
  }
}

const emitValue = () => {
  emit('update:modelValue', selectedCharacters.value)
}

const getStanceType = (stance: DiscussionStance) => {
  const typeMap: Record<DiscussionStance, any> = {
    support: 'success',
    oppose: 'danger',
    neutral: 'info',
    critical_exploration: 'warning'
  }
  return typeMap[stance]
}

const getStanceText = (stance: DiscussionStance) => {
  const textMap: Record<DiscussionStance, string> = {
    support: 'Supportive',
    oppose: 'Opposing',
    neutral: 'Neutral',
    critical_exploration: 'Critical'
  }
  return textMap[stance]
}

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  selectedCharacters.value = [...newVal]
}, { deep: true })
</script>

<style scoped lang="scss">
.character-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;

  .selection-info {
    display: flex;
    align-items: center;
    gap: 8px;

    .label {
      font-size: 14px;
      color: var(--el-text-color-secondary);
    }

    .count {
      font-size: 16px;
      font-weight: 600;
      color: var(--el-color-primary);
    }
  }
}

.selected-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.selected-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 4px;
}

.selected-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;

  &.avatar-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-success));
    color: white;
    font-size: 14px;
    font-weight: 600;
  }
}

.selected-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.selector-tabs {
  :deep(.el-tabs__content) {
    padding-top: 16px;
  }
}

.library-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.library-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;

  .search-input {
    flex: 1;
    min-width: 200px;
  }

  .filter-select {
    width: 160px;
  }
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.character-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid var(--el-border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--el-color-primary);
  }

  &.is-selected {
    border-color: var(--el-color-primary);
    background-color: var(--el-color-primary-light-9);
  }
}

.character-avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.character-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;

  &.avatar-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-success));
    color: white;
    font-size: 20px;
    font-weight: 600;
  }
}

.character-details {
  flex: 1;
  min-width: 0;
}

.character-name {
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.character-profession {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.character-tags {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.create-content,
.recommend-content {
  padding: 16px 0;
}

.recommend-form {
  margin-bottom: 24px;
}

.recommendations-list {
  h5 {
    margin: 0 0 12px;
    font-size: 14px;
    font-weight: 600;
  }
}

.recommendation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  margin-bottom: 8px;
}

.rec-info {
  flex: 1;
}

.rec-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.rec-reason {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.loading-state,
.empty-state {
  padding: 40px 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .library-filters {
    flex-direction: column;

    .search-input,
    .filter-select {
      width: 100%;
    }
  }

  .character-grid {
    grid-template-columns: 1fr;
  }
}
</style>
