<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">创建议题</h1>

    <form @submit.prevent="handleSubmit" class="bg-white p-6 rounded-lg shadow-sm max-w-2xl">
      <div class="mb-6">
        <label for="title" class="block text-sm font-medium text-gray-700 mb-1">
          议题标题 <span class="text-red-500">*</span>
        </label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          required
          minlength="10"
          maxlength="200"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="请输入议题标题（10-200字符）"
        />
        <p class="text-sm text-gray-500 mt-1">{{ form.title.length }}/200</p>
      </div>

      <div class="mb-6">
        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
          详细描述
        </label>
        <textarea
          id="description"
          v-model="form.description"
          rows="6"
          maxlength="2000"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="请详细描述议题背景、目标等信息（可选，最多2000字符）"
        ></textarea>
        <p class="text-sm text-gray-500 mt-1">{{ form.description.length }}/2000</p>
      </div>

      <div class="mb-6">
        <label for="context" class="block text-sm font-medium text-gray-700 mb-1">
          背景信息
        </label>
        <textarea
          id="context"
          v-model="form.context"
          rows="4"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="提供额外的背景信息、参考资料等（可选）"
        ></textarea>
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
          :disabled="loading"
          class="flex-1 bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading">保存中...</span>
          <span v-else>创建议题</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import endpoints from '@/services/endpoints'

const router = useRouter()

const form = ref({
  title: '',
  description: '',
  context: ''
})
const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    const response = await endpoints.topics.create(form.value)
    router.push(`/topics/${response.data.id}`)
  } catch (err) {
    error.value = err.message || '创建失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}
</script>
