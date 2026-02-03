<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">API 密钥管理</h1>

    <div v-if="loading" class="text-center py-8">
      <div class="spinner mx-auto"></div>
    </div>

    <div v-else>
      <form @submit.prevent="handleCreateKey" class="bg-white p-6 rounded-lg shadow-sm mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">添加新的 API 密钥</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              提供商
            </label>
            <select
              v-model="form.provider"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="custom">自定义</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              名称
            </label>
            <input
              v-model="form.key_name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="OpenAI 主密钥"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              API 密钥
            </label>
            <input
              v-model="form.api_key"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="sk-..."
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              API Base URL（可选）
            </label>
            <input
              v-model="form.api_base_url"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="https://api.openai.com/v1"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              默认模型（可选）
            </label>
            <input
              v-model="form.default_model"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="gpt-4"
            />
          </div>
        </div>

        <button
          type="submit"
          :disabled="creating"
          class="mt-4 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50"
        >
          <span v-if="creating">添加中...</span>
          <span v-else>添加</span>
        </button>
      </form>

      <div v-if="apiKeys.length === 0" class="text-center py-8 text-gray-600">
        还没有配置 API 密钥，请添加一个以开始使用
      </div>

      <div v-else class="space-y-4">
        <h3 class="text-lg font-semibold text-gray-900">已配置的 API 密钥</h3>
        <div
          v-for="key in apiKeys"
          :key="key.id"
          class="bg-white p-6 rounded-lg shadow-sm"
        >
          <div class="flex justify-between items-start">
            <div>
              <h4 class="text-lg font-semibold text-gray-900">{{ key.key_name }}</h4>
              <p class="text-sm text-gray-600">
                提供商：{{ key.provider }} | 模型：{{ key.default_model || '未设置' }}
              </p>
              <p class="text-sm text-gray-500">
                上次使用：{{ key.last_used_at ? formatDate(key.last_used_at) : '从未使用' }}
              </p>
            </div>
            <button
              @click="deleteKey(key.id)"
              class="text-red-600 hover:text-red-700 px-3 py-1 border border-red-300 rounded text-sm"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import endpoints from '@/services/endpoints'

const apiKeys = ref([])
const loading = ref(true)
const creating = ref(false)
const form = ref({
  provider: 'openai',
  key_name: '',
  api_key: '',
  api_base_url: '',
  default_model: ''
})

const loadApiKeys = async () => {
  try {
    const response = await endpoints.apiKeys.getAll()
    apiKeys.value = response.data
  } catch (error) {
    console.error('Failed to load API keys:', error)
  } finally {
    loading.value = false
  }
}

const handleCreateKey = async () => {
  creating.value = true
  try {
    await endpoints.apiKeys.create(form.value)
    await loadApiKeys()
    // Reset form
    form.value = {
      provider: 'openai',
      key_name: '',
      api_key: '',
      api_base_url: '',
      default_model: ''
    }
  } catch (error) {
    console.error('Failed to create API key:', error)
    alert('添加失败：' + (error.message || '未知错误'))
  } finally {
    creating.value = false
  }
}

const deleteKey = async (id) => {
  if (!confirm('确定要删除这个 API 密钥吗？')) return

  try {
    await endpoints.apiKeys.delete(id)
    await loadApiKeys()
  } catch (error) {
    console.error('Failed to delete API key:', error)
    alert('删除失败')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadApiKeys()
})
</script>
