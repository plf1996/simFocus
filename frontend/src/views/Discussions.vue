<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">讨论历史</h1>
    </div>

    <div v-if="loading" class="text-center py-8">
      <div class="spinner mx-auto"></div>
    </div>

    <div v-else-if="discussions.length === 0" class="text-center py-8 text-gray-600">
      还没有讨论记录，<router-link to="/topics" class="text-primary-600">去创建一个议题</router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="discussion in discussions"
        :key="discussion.id"
        class="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        @click="goToDiscussion(discussion.id)"
      >
        <div class="flex justify-between items-start mb-2">
          <h3 class="text-xl font-semibold text-gray-900">{{ discussion.topic_title }}</h3>
          <span
            class="px-2 py-1 text-xs font-medium rounded-full"
            :class="getStatusClass(discussion.status)"
          >
            {{ getStatusText(discussion.status) }}
          </span>
        </div>
        <p class="text-sm text-gray-600 mb-2">
          模式：{{ getModeText(discussion.discussion_mode) }} | 轮次：{{ discussion.current_round }}/{{ discussion.max_rounds }}
        </p>
        <div class="flex justify-between items-center text-sm text-gray-500">
          <span>创建于 {{ formatDate(discussion.created_at) }}</span>
          <router-link
            v-if="discussion.status === 'completed'"
            :to="`/discussions/${discussion.id}/report`"
            @click.stop
            class="text-primary-600 hover:text-primary-700"
          >
            查看报告
          </router-link>
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
const discussions = ref([])
const loading = ref(true)

const loadDiscussions = async () => {
  try {
    const response = await endpoints.discussions.getAll()
    discussions.value = response.data
  } catch (error) {
    console.error('Failed to load discussions:', error)
  } finally {
    loading.value = false
  }
}

const goToDiscussion = (id) => {
  router.push(`/discussions/${id}`)
}

const getStatusClass = (status) => {
  const classes = {
    initialized: 'bg-gray-100 text-gray-700',
    running: 'bg-green-100 text-green-700',
    paused: 'bg-yellow-100 text-yellow-700',
    completed: 'bg-blue-100 text-blue-700',
    failed: 'bg-red-100 text-red-700'
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

const getStatusText = (status) => {
  const texts = {
    initialized: '初始化',
    running: '进行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const getModeText = (mode) => {
  const texts = {
    free: '自由讨论',
    structured: '结构化辩论',
    creative: '创意发散',
    consensus: '共识构建'
  }
  return texts[mode] || mode
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
  loadDiscussions()
})
</script>
