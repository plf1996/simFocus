<template>
  <div class="character-library">
    <!-- Header -->
    <div class="library-header">
      <div class="header-info">
        <h3>Character Library</h3>
        <p class="subtitle">{{ characterCount }} characters available</p>
      </div>
      <div class="header-actions">
        <AppButton type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          Create Character
        </AppButton>
      </div>
    </div>

    <!-- Filters -->
    <div class="library-filters">
      <el-input
        v-model="searchQuery"
        placeholder="Search characters..."
        :prefix-icon="Search"
        clearable
        class="search-input"
      />

      <el-select
        v-model="filterSource"
        placeholder="Source"
        class="filter-select"
      >
        <el-option label="All Characters" value="" />
        <el-option label="My Characters" value="mine" />
        <el-option label="Templates" value="template" />
        <el-option label="Public" value="public" />
      </el-select>

      <el-select
        v-model="filterStance"
        placeholder="Stance"
        clearable
        class="filter-select"
      >
        <el-option label="Supportive" value="support" />
        <el-option label="Opposing" value="oppose" />
        <el-option label="Neutral" value="neutral" />
        <el-option label="Critical" value="critical_exploration" />
      </el-select>

      <el-select
        v-model="sortBy"
        placeholder="Sort by"
        class="filter-select"
      >
        <el-option label="Most Used" value="usage" />
        <el-option label="Highest Rated" value="rating" />
        <el-option label="Newest" value="newest" />
        <el-option label="Name A-Z" value="name" />
      </el-select>

      <el-button-group class="view-toggle">
        <AppButton
          :type="viewMode === 'grid' ? 'primary' : 'default'"
          size="small"
          @click="viewMode = 'grid'"
        >
          <el-icon><Grid /></el-icon>
        </AppButton>
        <AppButton
          :type="viewMode === 'list' ? 'primary' : 'default'"
          size="small"
          @click="viewMode = 'list'"
        >
          <el-icon><List /></el-icon>
        </AppButton>
      </el-button-group>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredCharacters.length === 0" class="empty-state">
      <el-empty :description="emptyText">
        <AppButton type="primary" @click="handleCreate">
          Create Your First Character
        </AppButton>
      </el-empty>
    </div>

    <!-- Character Grid/List -->
    <div v-else :class="['character-container', viewMode]">
      <CharacterCard
        v-for="character in paginatedCharacters"
        :key="character.id"
        :character="character"
        :clickable="true"
        :show-stats="true"
        :show-actions="true"
        @click="handleViewCharacter"
        @edit="handleEditCharacter"
        @duplicate="handleDuplicateCharacter"
        @delete="handleDeleteCharacter"
      />
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="library-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48]"
        :total="filteredCharacters.length"
        layout="total, sizes, prev, pager, next"
        @size-change="handlePageSizeChange"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showEditor"
      :title="editingCharacter ? 'Edit Character' : 'Create Character'"
      width="800px"
      @close="handleEditorClose"
    >
      <CharacterEditor
        v-if="showEditor"
        :character="editingCharacter"
        @save="handleSaveCharacter"
        @cancel="showEditor = false"
      />
    </el-dialog>

    <!-- Preview Dialog -->
    <el-dialog
      v-model="showPreview"
      title="Character Preview"
      width="600px"
    >
      <CharacterPreview
        v-if="previewCharacter"
        :character="previewCharacter"
        :show-stats="true"
        :show-behavior="true"
        :show-actions="false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Plus, Grid, List } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import AppButton from '@/components/common/AppButton.vue'
import CharacterCard from './CharacterCard.vue'
import CharacterEditor from './CharacterEditor.vue'
import CharacterPreview from './CharacterPreview.vue'
import type { Character } from '@/types'

interface Props {
  characters?: Character[]
  isLoading?: boolean
}

interface Emits {
  refresh: []
  create: []
  select: [character: Character]
  edit: [character: Character]
}

const props = withDefaults(defineProps<Props>(), {
  characters: () => [],
  isLoading: false
})

const emit = defineEmits<Emits>()

// State
const searchQuery = ref('')
const filterSource = ref('')
const filterStance = ref('')
const sortBy = ref('usage')
const viewMode = ref<'grid' | 'list'>('grid')
const currentPage = ref(1)
const pageSize = ref(12)
const showEditor = ref(false)
const showPreview = ref(false)
const editingCharacter = ref<Character | null>(null)
const previewCharacter = ref<Character | null>(null)

// Computed
const characterCount = computed(() => props.characters.length)

const filteredCharacters = computed(() => {
  let result = [...props.characters]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(c =>
      c.name.toLowerCase().includes(query) ||
      c.config.profession.toLowerCase().includes(query) ||
      c.config.knowledge.fields.some(f => f.toLowerCase().includes(query))
    )
  }

  // Source filter
  if (filterSource.value === 'mine') {
    result = result.filter(c => !c.is_template)
  } else if (filterSource.value === 'template') {
    result = result.filter(c => c.is_template)
  } else if (filterSource.value === 'public') {
    result = result.filter(c => c.is_public)
  }

  // Stance filter
  if (filterStance.value) {
    result = result.filter(c => c.config.stance === filterStance.value)
  }

  // Sort
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'usage':
        return b.usage_count - a.usage_count
      case 'rating':
        return (b.rating_avg || 0) - (a.rating_avg || 0)
      case 'newest':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'name':
        return a.name.localeCompare(b.name)
      default:
        return 0
    }
  })

  return result
})

const paginatedCharacters = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCharacters.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredCharacters.value.length / pageSize.value)
})

const emptyText = computed(() => {
  if (searchQuery.value || filterSource.value || filterStance.value) {
    return 'No characters match your filters'
  }
  return 'No characters yet'
})

// Methods
const handleCreate = () => {
  editingCharacter.value = null
  showEditor.value = true
}

const handleViewCharacter = (character: Character) => {
  previewCharacter.value = character
  showPreview.value = true
}

const handleEditCharacter = (character: Character) => {
  editingCharacter.value = character
  showEditor.value = true
}

const handleDuplicateCharacter = async (character: Character) => {
  try {
    await ElMessageBox.confirm(
      'Create a duplicate of this character?',
      'Duplicate Character',
      {
        type: 'info'
      }
    )

    const duplicate: Character = {
      ...character,
      id: `char_${Date.now()}`,
      name: `${character.name} (Copy)`,
      usage_count: 0,
      rating_avg: undefined,
      rating_count: 0,
      created_at: new Date().toISOString()
    }

    editingCharacter.value = duplicate
    showEditor.value = true

    ElMessage.success('Character duplicated. Edit and save to confirm.')
  } catch {
    // Cancelled
  }
}

const handleDeleteCharacter = async (character: Character) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${character.name}"? This action cannot be undone.`,
      'Delete Character',
      {
        type: 'warning',
        confirmButtonText: 'Delete',
        confirmButtonClass: 'el-button--danger'
      }
    )

    // TODO: Implement actual API call
    // await characterApi.delete(character.id)

    emit('refresh')
    ElMessage.success('Character deleted successfully')
  } catch {
    // Cancelled
  }
}

const handleSaveCharacter = (character: Character) => {
  showEditor.value = false
  emit('refresh')
  ElMessage.success(editingCharacter.value ? 'Character updated' : 'Character created')
}

const handleEditorClose = () => {
  editingCharacter.value = null
  showEditor.value = false
}

const handlePageSizeChange = () => {
  currentPage.value = 1
}

// Lifecycle
onMounted(() => {
  emit('refresh')
})

// Expose refresh method
const refresh = () => {
  emit('refresh')
}

defineExpose({
  refresh
})
</script>

<style scoped lang="scss">
.character-library {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.library-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-info {
    h3 {
      margin: 0 0 4px;
      font-size: 20px;
      font-weight: 600;
    }

    .subtitle {
      margin: 0;
      font-size: 14px;
      color: var(--el-text-color-secondary);
    }
  }
}

.library-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;

  .search-input {
    flex: 1;
    min-width: 200px;
    max-width: 400px;
  }

  .filter-select {
    width: 140px;
  }
}

.view-toggle {
  margin-left: auto;
}

.loading-state {
  padding: 40px 20px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.character-container {
  display: grid;
  gap: 20px;

  &.grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }

  &.list {
    grid-template-columns: 1fr;
  }
}

.library-pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

@media (max-width: 768px) {
  .library-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .library-filters {
    flex-direction: column;

    .search-input,
    .filter-select {
      width: 100%;
      max-width: none;
    }

    .view-toggle {
      margin-left: 0;
    }
  }

  .character-container.grid {
    grid-template-columns: 1fr;
  }
}
</style>
