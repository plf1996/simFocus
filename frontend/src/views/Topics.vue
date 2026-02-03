<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">议题</h1>
      <router-link
        to="/topics/new"
        class="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
      >
        创建议题
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-8">
      <div class="spinner mx-auto"></div>
    </div>

    <div v-else-if="topics.length === 0" class="text-center py-8 text-gray-600">
      还没有议题，<router-link to="/topics/new" class="text-primary-600">创建一个</router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="topic in topics"
        :key="topic.id"
        class="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        @click="goToTopic(topic.id)"
      >
        <div class="flex justify-between items-start mb-2">
          <h3 class="text-xl font-semibold text-gray-900">{{ topic.title }}</h3>
          <span
            class="px-2 py-1 text-xs font-medium rounded-full"
            :class="getStatusClass(topic.status)"
          >
            {{ getStatusText(topic.status) }}
          </span>
        </div>
        <p v-if="topic.description" class="text-gray-600 mb-4">
          {{ topic.description }}
        </p>
        <div class="text-sm text-gray-500">
          创建于 {{ formatDate(topic.created_at) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import endpoints from '@/services/endpoints'

const router = useRouter()
const topics = ref([])
const loading = ref(true)

const loadTopics = async () => {
  try {
    const response = await endpoints.topics.getAll()
    topics.value = response.data
  } catch (error) {
    console.error('Failed to load topics:', error)
  } finally {
    loading.value = false
  }
}

const goToTopic = (id) => {
  router.push(`/topics/${id}`)
}

const getStatusClass = (status) => {
  const classes = {
    draft: 'bg-gray-100 text-gray-700',
    ready: 'bg-blue-100 text-blue-700',
    in_discussion: 'bg-green-100 text-green-700',
    completed: 'bg-purple-100 text-purple-700'
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    ready: '准备中',
    in_discussion: '讨论中',
    completed: '已完成'
  }
  return texts[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadTopics()
})
</script>
