<template>
  <div class="topic-list">
    <!-- Filters and Actions -->
    <div class="list-header">
      <div class="filters">
        <el-input
          v-model="searchQuery"
          placeholder="Search topics..."
          :prefix-icon="Search"
          clearable
          class="search-input"
        />

        <el-select
          v-model="statusFilter"
          placeholder="All Status"
          clearable
          class="filter-select"
        >
          <el-option label="All Status" value="" />
          <el-option label="Draft" value="draft" />
          <el-option label="Ready" value="ready" />
          <el-option label="In Discussion" value="in_discussion" />
          <el-option label="Completed" value="completed" />
        </el-select>

        <el-select
          v-model="sortBy"
          placeholder="Sort by"
          class="filter-select"
        >
          <el-option label="Latest First" value="created_desc" />
          <el-option label="Oldest First" value="created_asc" />
          <el-option label="Title A-Z" value="title_asc" />
          <el-option label="Title Z-A" value="title_desc" />
        </el-select>
      </div>

      <AppButton type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        New Topic
      </AppButton>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredTopics.length === 0" class="empty-state">
      <el-empty :description="emptyText">
        <AppButton type="primary" @click="handleCreate">
          Create Your First Topic
        </AppButton>
      </el-empty>
    </div>

    <!-- Topic Grid -->
    <div v-else class="topic-grid">
      <TopicCard
        v-for="topic in filteredTopics"
        :key="topic.id"
        :topic="topic"
        :clickable="true"
        :show-status="true"
        :show-actions="true"
        :show-footer="true"
        :discussion-count="getDiscussionCount(topic.id)"
        :is-active="topic.id === activeTopicId"
        @click="handleTopicClick"
        @action="handleTopicAction"
        @start="handleStartDiscussion"
      />
    </div>

    <!-- Load More -->
    <div v-if="hasMore" class="load-more">
      <AppButton
        :loading="isLoadingMore"
        @click="handleLoadMore"
      >
        Load More
      </AppButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'
import TopicCard from './TopicCard.vue'
import type { Topic } from '@/types'

interface Props {
  topics?: Topic[]
  isLoading?: boolean
  activeTopicId?: string
}

interface Emits {
  refresh: []
  create: []
  select: [topic: Topic]
  action: [action: string, topic: Topic]
  start: [topic: Topic]
  loadMore: []
}

const props = withDefaults(defineProps<Props>(), {
  topics: () => [],
  isLoading: false,
  activeTopicId: ''
})

const emit = defineEmits<Emits>()

// State
const searchQuery = ref('')
const statusFilter = ref<string>('')
const sortBy = ref('created_desc')
const isLoadingMore = ref(false)
const hasMore = ref(false)

// Discussion count cache (in real app, this would come from API)
const discussionCountMap = ref<Record<string, number>>({})

// Computed
const filteredTopics = computed(() => {
  let result = [...props.topics]

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(topic =>
      topic.title.toLowerCase().includes(query) ||
      topic.description?.toLowerCase().includes(query)
    )
  }

  // Filter by status
  if (statusFilter.value) {
    result = result.filter(topic => topic.status === statusFilter.value)
  }

  // Sort
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'created_desc':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'created_asc':
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      case 'title_asc':
        return a.title.localeCompare(b.title)
      case 'title_desc':
        return b.title.localeCompare(a.title)
      default:
        return 0
    }
  })

  return result
})

const emptyText = computed(() => {
  if (searchQuery.value || statusFilter.value) {
    return 'No topics match your filters'
  }
  return 'No topics yet'
})

// Methods
const handleCreate = () => {
  emit('create')
}

const handleTopicClick = (topic: Topic) => {
  emit('select', topic)
}

const handleTopicAction = (action: string, topic: Topic) => {
  emit('action', action, topic)
}

const handleStartDiscussion = (topic: Topic) => {
  emit('start', topic)
}

const handleLoadMore = () => {
  isLoadingMore.value = true
  emit('loadMore')
  // Reset loading after a delay (in real app, this would be handled by API response)
  setTimeout(() => {
    isLoadingMore.value = false
  }, 1000)
}

const getDiscussionCount = (topicId: string) => {
  return discussionCountMap.value[topicId] || 0
}

const fetchDiscussionCounts = async () => {
  // TODO: Implement actual API call to fetch discussion counts
  // const counts = await topicApi.getDiscussionCounts()
  // discussionCountMap.value = counts
}

// Lifecycle
onMounted(() => {
  fetchDiscussionCounts()
})

// Expose refresh method
const refresh = () => {
  emit('refresh')
  fetchDiscussionCounts()
}

defineExpose({
  refresh
})
</script>

<style scoped lang="scss">
.topic-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;

  .filters {
    display: flex;
    gap: 12px;
    flex: 1;
    flex-wrap: wrap;
  }

  .search-input {
    width: 280px;
  }

  .filter-select {
    width: 160px;
  }
}

.loading-state {
  padding: 20px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.load-more {
  display: flex;
  justify-content: center;
  padding: 20px;
}

@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    align-items: stretch;

    .filters {
      flex-direction: column;
    }

    .search-input,
    .filter-select {
      width: 100%;
    }
  }

  .topic-grid {
    grid-template-columns: 1fr;
  }
}
</style>
