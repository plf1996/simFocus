<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">创建讨论</h1>

    <div v-if="error && !topic" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
      {{ error }}
    </div>

    <div v-if="loading" class="text-center py-8">
      <div class="spinner mx-auto"></div>
    </div>

    <div v-else-if="!topic && !error">
      <div class="text-center py-8 text-gray-600">
        <p class="mb-4">未找到议题信息</p>
        <router-link to="/topics" class="text-primary-600 hover:text-primary-700">
          返回议题列表
        </router-link>
      </div>
    </div>

    <div v-else-if="topic">
      <!-- Topic Info -->
      <div class="bg-white p-6 rounded-lg shadow-sm mb-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-2">{{ topic?.title }}</h2>
        <p v-if="topic?.description" class="text-gray-600">{{ topic.description }}</p>
      </div>

      <form @submit.prevent="handleSubmit">
        <!-- Character Selection -->
        <div class="bg-white p-6 rounded-lg shadow-sm mb-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900">选择角色（3-7个）</h3>
            <div class="flex gap-3">
              <button
                type="button"
                @click="loadRecommendedCharacters"
                :disabled="recommending"
                class="text-primary-600 hover:text-primary-700 text-sm disabled:opacity-50 flex items-center gap-1"
              >
                <svg v-if="recommending" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>智能推荐</span>
              </button>
              <button
                type="button"
                @click="loadRandomCharacters"
                class="text-gray-600 hover:text-gray-700 text-sm"
              >
                随机推荐
              </button>
            </div>
          </div>

          <div v-if="recommendationLoaded" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p class="text-sm text-blue-700">
              <span class="font-medium">智能推荐</span> - 已根据议题内容推荐最匹配的角色
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="character in availableCharacters"
              :key="character.id"
              :class="['p-4 border rounded-lg cursor-pointer hover:shadow-md transition-all',
                selectedCharacters.includes(character.id) ? 'border-primary-500 bg-primary-50' : 'border-gray-200']"
              @click="toggleCharacter(character)"
            >
              <div class="flex items-center mb-2">
                <div v-if="character.avatar_url" class="w-10 h-10 rounded-full bg-gray-200 overflow-hidden mr-3">
                  <img :src="character.avatar_url" :alt="character.name" class="w-full h-full object-cover" />
                </div>
                <div v-else class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center mr-3">
                  <span class="text-primary-600 font-semibold">{{ character.name[0] }}</span>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <h4 class="font-medium text-gray-900">{{ character.name }}</h4>
                    <span v-if="character.similarity_score !== undefined && character.similarity_score !== null" class="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">
                      匹配度 {{ (character.similarity_score * 100).toFixed(0) }}%
                    </span>
                  </div>
                  <p class="text-sm text-gray-500">{{ character.config?.profession }}</p>
                </div>
                <div v-if="selectedCharacters.includes(character.id)" class="text-primary-600">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <p class="mt-4 text-sm text-gray-600">
            已选择 {{ selectedCharacters.length }}/7 个角色
          </p>
        </div>

        <!-- Discussion Settings -->
        <div class="bg-white p-6 rounded-lg shadow-sm mb-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">讨论设置</h3>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              讨论模式
            </label>
            <select
              v-model="form.discussion_mode"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="free">自由讨论模式</option>
              <option value="structured">结构化辩论模式</option>
              <option value="creative">创意发散模式</option>
              <option value="consensus">共识构建模式</option>
            </select>
            <p class="text-sm text-gray-500 mt-1">
              {{ getModeDescription(form.discussion_mode) }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              讨论轮次
            </label>
            <input
              v-model="form.max_rounds"
              type="number"
              min="1"
              max="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <p class="text-sm text-gray-500 mt-1">
              建议轮次：3-5 轮（每轮包含4个阶段：开场、发展、辩论、总结）
            </p>
          </div>
        </div>

        <div v-if="error" class="text-red-600 mb-4">
          {{ error }}
        </div>

        <div class="flex gap-4">
          <button
            type="button"
            @click="goBack"
            class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="loading || selectedCharacters.length < 3"
            class="flex-1 bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">创建中...</span>
            <span v-else>开始讨论</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import endpoints from '@/services/endpoints'

const route = useRoute()
const router = useRouter()

const topicId = route.query.topic
const topic = ref(null)
const availableCharacters = ref([])
const selectedCharacters = ref([])
const loading = ref(false)
const submitting = ref(false)
const recommending = ref(false)
const recommendationLoaded = ref(false)
const error = ref('')

const form = ref({
  discussion_mode: 'free',
  max_rounds: 3
})

const loadTopic = async () => {
  if (!topicId) {
    error.value = '缺少议题ID，请先选择议题'
    return
  }

  try {
    const response = await endpoints.topics.getById(topicId)
    topic.value = response.data
  } catch (err) {
    console.error('Failed to load topic:', err)
    error.value = '加载议题失败'
    setTimeout(() => router.push('/topics'), 2000)
  }
}

const loadCharacters = async () => {
  try {
    const response = await endpoints.characters.getTemplates()
    availableCharacters.value = response.data
  } catch (error) {
    console.error('Failed to load characters:', error)
  }
}

const loadRandomCharacters = async () => {
  try {
    const response = await endpoints.characters.getRandomTemplates(5)
    availableCharacters.value = response.data
    selectedCharacters.value = response.data.map(c => c.id)
    recommendationLoaded.value = false
  } catch (error) {
    console.error('Failed to load random characters:', error)
  }
}

const loadRecommendedCharacters = async () => {
  if (!topic.value) {
    error.value = '请先加载议题信息'
    return
  }

  recommending.value = true
  error.value = ''

  try {
    // Prepare topic data for recommendation
    const topicData = {
      title: topic.value.title,
      description: topic.value.description || ''
    }

    // Get recommended characters
    const response = await endpoints.characters.recommend(topicData, 5)
    availableCharacters.value = response.data

    // Auto-select top 5 characters
    selectedCharacters.value = response.data.slice(0, 5).map(c => c.id)
    recommendationLoaded.value = true
  } catch (err) {
    console.error('Failed to load recommended characters:', err)
    error.value = '智能推荐失败，请重试或使用随机推荐'
  } finally {
    recommending.value = false
  }
}

const toggleCharacter = (character) => {
  const index = selectedCharacters.value.indexOf(character.id)
  if (index > -1) {
    selectedCharacters.value.splice(index, 1)
  } else if (selectedCharacters.value.length < 7) {
    selectedCharacters.value.push(character.id)
  }
}

const getModeDescription = (mode) => {
  const descriptions = {
    free: '角色自由发言，系统保持对话平衡和逻辑连贯',
    structured: '分为正反方，每轮系统指定发言角色',
    creative: '基于"是的，而且"原则，角色在他人观点基础上延伸创新',
    consensus: '目标是寻找共同点，角色积极妥协和整合观点'
  }
  return descriptions[mode] || ''
}

const handleSubmit = async () => {
  if (selectedCharacters.value.length < 3) {
    error.value = '请至少选择 3 个角色'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    const response = await endpoints.discussions.create({
      topic_id: topicId,
      discussion_mode: form.value.discussion_mode,
      max_rounds: form.value.max_rounds,
      character_ids: selectedCharacters.value
    })
    router.push(`/discussions/${response.data.id}`)
  } catch (err) {
    error.value = err.message || '创建讨论失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(async () => {
  loading.value = true
  await loadTopic()
  await loadCharacters()
  loading.value = false
})
</script>
