<template>
  <div>
    <div v-if="loading" class="text-center py-8">
      <div class="spinner mx-auto"></div>
    </div>

    <div v-else-if="!topic" class="text-center py-8 text-gray-600">
      议题不存在
    </div>

    <div v-else>
      <div class="bg-white p-6 rounded-lg shadow-sm mb-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ topic.title }}</h1>
        <div class="flex gap-2 mb-4">
          <span
            class="px-3 py-1 text-sm font-medium rounded-full"
            :class="getStatusClass(topic.status)"
          >
            {{ getStatusText(topic.status) }}
          </span>
        </div>
        <p v-if="topic.description" class="text-gray-700 mb-4">
          {{ topic.description }}
        </p>
        <div v-if="topic.context" class="bg-gray-50 p-4 rounded-md">
          <h3 class="font-medium text-gray-900 mb-2">背景信息</h3>
          <p class="text-gray-700">{{ topic.context }}</p>
        </div>
      </div>

      <div class="flex gap-4">
        <router-link
          :to="`/discussions/new?topic=${topic.id}`"
          class="bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700"
        >
          创建讨论
        </router-link>
        <router-link
          to="/topics"
          class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          返回列表
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import endpoints from '@/services/endpoints'

const route = useRoute()
const topicId = route.params.id

const topic = ref(null)
const loading = ref(true)

const loadTopic = async () => {
  try {
    const response = await endpoints.topics.getById(topicId)
    topic.value = response.data
  } catch (error) {
    console.error('Failed to load topic:', error)
  } finally {
    loading.value = false
  }
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

onMounted(() => {
  loadTopic()
})
</script>
