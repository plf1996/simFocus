<template>
  <el-dialog
    v-model="visible"
    title="Choose a Topic Template"
    width="800px"
    @close="handleClose"
  >
    <div class="template-selector">
      <!-- Category Filter -->
      <div class="category-filter">
        <el-radio-group v-model="selectedCategory" size="small">
          <el-radio-button label="">All</el-radio-button>
          <el-radio-button
            v-for="category in categories"
            :key="category"
            :label="category"
          >
            {{ category }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- Search -->
      <div class="template-search">
        <el-input
          v-model="searchQuery"
          placeholder="Search templates..."
          :prefix-icon="Search"
          clearable
        />
      </div>

      <!-- Template Grid -->
      <div v-if="isLoading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="filteredTemplates.length === 0" class="empty-state">
        <el-empty description="No templates found" />
      </div>

      <div v-else class="template-grid">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          :class="['template-card', { 'is-selected': selectedTemplate?.id === template.id }]"
          @click="handleSelectTemplate(template)"
        >
          <div class="template-header">
            <h4>{{ template.name }}</h4>
            <el-tag size="small">{{ template.category }}</el-tag>
          </div>
          <p class="template-description">{{ template.description }}</p>
          <div class="template-preview">
            <div class="preview-field">
              <span class="field-label">Title:</span>
              <span class="field-value">{{ template.title }}</span>
            </div>
            <div v-if="template.description" class="preview-field">
              <span class="field-label">Description:</span>
              <span class="field-value">{{ truncate(template.description, 80) }}</span>
            </div>
            <div v-if="template.context" class="preview-field">
              <span class="field-label">Context:</span>
              <span class="field-value">{{ truncate(template.context, 80) }}</span>
            </div>
          </div>
          <div class="template-meta">
            <span class="usage-count">
              <el-icon><User /></el-icon>
              {{ template.usage_count }} uses
            </span>
            <el-rate
              v-model="template.rating"
              disabled
              show-score
              text-color="#ff9900"
            />
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <AppButton @click="handleClose">Cancel</AppButton>
        <AppButton
          type="primary"
          :disabled="!selectedTemplate"
          @click="handleConfirm"
        >
          Use Template
        </AppButton>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search, User } from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'

interface TopicTemplate {
  id: string
  name: string
  category: string
  description: string
  title: string
  description?: string
  context?: string
  usage_count: number
  rating: number
}

interface Props {
  modelValue: boolean
}

interface Emits {
  'update:modelValue': [value: boolean]
  select: [template: TopicTemplate]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// State
const selectedCategory = ref('')
const searchQuery = ref('')
const selectedTemplate = ref<TopicTemplate | null>(null)
const isLoading = ref(false)

// Mock templates data (in real app, this would come from API)
const templates = ref<TopicTemplate[]>([
  {
    id: '1',
    name: 'Product Feature Validation',
    category: 'Product',
    description: 'Validate new product features with diverse perspectives',
    title: 'Should we add [feature] to our product?',
    description: 'Discuss the potential impact, user value, and implementation challenges of adding this feature.',
    context: 'Target audience: [describe]\nCurrent product stage: [describe]\nKey metrics: [describe]',
    usage_count: 234,
    rating: 4.5
  },
  {
    id: '2',
    name: 'Marketing Strategy Review',
    category: 'Marketing',
    description: 'Evaluate marketing strategies and campaigns',
    title: 'How should we approach our next marketing campaign?',
    description: 'Explore different marketing channels, messaging strategies, and budget allocation options.',
    context: 'Product/service: [describe]\nTarget market: [describe]\nBudget range: [describe]\nTimeline: [describe]',
    usage_count: 189,
    rating: 4.3
  },
  {
    id: '3',
    name: 'Technical Architecture Decision',
    category: 'Technology',
    description: 'Make informed technical architecture choices',
    title: 'Which technology stack should we use for [project]?',
    description: 'Compare and evaluate different technical approaches, considering scalability, maintainability, and team expertise.',
    context: 'Project requirements: [describe]\nTeam size: [describe]\nTimeline constraints: [describe]\nPerformance requirements: [describe]',
    usage_count: 312,
    rating: 4.7
  },
  {
    id: '4',
    name: 'User Experience Improvement',
    category: 'Design',
    description: 'Identify UX improvements and design solutions',
    title: 'How can we improve the user experience of [feature]?',
    description: 'Brainstorm UX improvements, identify pain points, and propose design solutions.',
    context: 'Current issues: [describe]\nUser feedback: [describe]\nBusiness goals: [describe]\nTechnical constraints: [describe]',
    usage_count: 156,
    rating: 4.4
  },
  {
    id: '5',
    name: 'Business Model Exploration',
    category: 'Business',
    description: 'Explore and validate business model options',
    title: 'What business model should we adopt for [product/service]?',
    description: 'Evaluate different revenue models, pricing strategies, and market positioning approaches.',
    context: 'Product/service: [describe]\nTarget customers: [describe]\nMarket conditions: [describe]\nCompetitors: [describe]',
    usage_count: 201,
    rating: 4.6
  }
])

// Computed
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const categories = computed(() => {
  const cats = new Set(templates.value.map(t => t.category))
  return Array.from(cats).sort()
})

const filteredTemplates = computed(() => {
  let result = [...templates.value]

  // Filter by category
  if (selectedCategory.value) {
    result = result.filter(t => t.category === selectedCategory.value)
  }

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(t =>
      t.name.toLowerCase().includes(query) ||
      t.description.toLowerCase().includes(query) ||
      t.title.toLowerCase().includes(query)
    )
  }

  return result
})

// Methods
const handleSelectTemplate = (template: TopicTemplate) => {
  selectedTemplate.value = template
}

const handleConfirm = () => {
  if (selectedTemplate.value) {
    emit('select', selectedTemplate.value)
    handleClose()
  }
}

const handleClose = () => {
  selectedTemplate.value = null
  visible.value = false
}

const truncate = (text: string, maxLength: number) => {
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}

// Reset selection when dialog closes
watch(visible, (val) => {
  if (!val) {
    selectedCategory.value = ''
    searchQuery.value = ''
  }
})
</script>

<style scoped lang="scss">
.template-selector {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-search {
  width: 100%;
}

.loading-state {
  padding: 20px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
  max-height: 500px;
  overflow-y: auto;
  padding: 4px;
}

.template-card {
  padding: 16px;
  border: 2px solid var(--el-border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--el-color-primary);
    box-shadow: var(--el-box-shadow-light);
  }

  &.is-selected {
    border-color: var(--el-color-primary);
    background-color: var(--el-color-primary-light-9);
  }
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;

  h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }
}

.template-description {
  margin: 0 0 12px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.template-preview {
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  margin-bottom: 12px;
}

.preview-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;

  &:last-child {
    margin-bottom: 0;
  }

  .field-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--el-text-color-secondary);
  }

  .field-value {
    font-size: 13px;
    color: var(--el-text-color-primary);
    line-height: 1.4;
  }
}

.template-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.usage-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: 1fr;
  }
}
</style>
