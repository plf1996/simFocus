<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">创建自定义角色</h1>

    <form @submit.prevent="handleSubmit" class="bg-white p-6 rounded-lg shadow-sm max-w-2xl">
      <div class="mb-6">
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
          角色名称 <span class="text-red-500">*</span>
        </label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="例如：产品经理、设计师、用户..."
        />
      </div>

      <div class="mb-6">
        <label for="avatar_url" class="block text-sm font-medium text-gray-700 mb-1">
          头像 URL（可选）
        </label>
        <input
          id="avatar_url"
          v-model="form.avatar_url"
          type="url"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="https://example.com/avatar.jpg"
        />
      </div>

      <div class="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label for="age" class="block text-sm font-medium text-gray-700 mb-1">
            年龄
          </label>
          <input
            id="age"
            v-model="form.age"
            type="number"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="35"
          />
        </div>
        <div>
          <label for="gender" class="block text-sm font-medium text-gray-700 mb-1">
            性别
          </label>
          <input
            id="gender"
            v-model="form.gender"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="男、女、其他..."
          />
        </div>
      </div>

      <div class="mb-6">
        <label for="profession" class="block text-sm font-medium text-gray-700 mb-1">
          职业 <span class="text-red-500">*</span>
        </label>
        <input
          id="profession"
          v-model="form.profession"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="例如：产品经理、工程师、教师..."
        />
      </div>

      <!-- Personality -->
      <div class="mb-6 p-4 bg-gray-50 rounded-md">
        <h3 class="font-medium text-gray-900 mb-4">性格特质（1-10）</h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">开放性</label>
            <input
              v-model="form.personality.openness"
              type="number"
              min="1"
              max="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">严谨性</label>
            <input
              v-model="form.personality.rigor"
              type="number"
              min="1"
              max="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">批判性思维</label>
            <input
              v-model="form.personality.critical_thinking"
              type="number"
              min="1"
              max="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">乐观程度</label>
            <input
              v-model="form.personality.optimism"
              type="number"
              min="1"
              max="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>
      </div>

      <!-- Knowledge -->
      <div class="mb-6 p-4 bg-gray-50 rounded-md">
        <h3 class="font-medium text-gray-900 mb-4">知识背景</h3>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">专业领域（用逗号分隔）</label>
          <input
            v-model="form.knowledgeFields"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md"
            placeholder="产品管理, UX设计, 市场分析"
          />
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">经验年限</label>
          <input
            v-model="form.knowledgeExperience"
            type="number"
            min="0"
            class="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">代表观点（用逗号分隔）</label>
          <input
            v-model="form.knowledgeViews"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md"
            placeholder="用户至上, 数据驱动, 快速迭代"
          />
        </div>
      </div>

      <!-- Discussion Style -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-1">立场</label>
        <select
          v-model="form.stance"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="support">支持</option>
          <option value="oppose">反对</option>
          <option value="neutral">中立</option>
          <option value="critical_exploration">批判性探索</option>
        </select>
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-1">表达风格</label>
        <select
          v-model="form.expression_style"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="formal">正式</option>
          <option value="casual">随意</option>
          <option value="technical">技术性</option>
          <option value="storytelling">叙事性</option>
        </select>
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-1">行为模式</label>
        <select
          v-model="form.behavior_pattern"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="active">主动</option>
          <option value="passive">被动</option>
          <option value="balanced">平衡</option>
        </select>
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
          <span v-else>创建角色</span>
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
  name: '',
  avatar_url: '',
  age: null,
  gender: '',
  profession: '',
  personality: {
    openness: 5,
    rigor: 5,
    critical_thinking: 5,
    optimism: 5
  },
  knowledgeFields: '',
  knowledgeExperience: 0,
  knowledgeViews: '',
  stance: 'critical_exploration',
  expression_style: 'formal',
  behavior_pattern: 'balanced'
})
const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    const characterData = {
      name: form.value.name,
      avatar_url: form.value.avatar_url || null,
      config: {
        age: form.value.age || null,
        gender: form.value.gender || null,
        profession: form.value.profession,
        personality: form.value.personality,
        knowledge: {
          fields: form.value.knowledgeFields.split(',').map(s => s.trim()).filter(s => s),
          experience_years: form.value.knowledgeExperience,
          representative_views: form.value.knowledgeViews.split(',').map(s => s.trim()).filter(s => s)
        },
        stance: form.value.stance,
        expression_style: form.value.expression_style,
        behavior_pattern: form.value.behavior_pattern
      }
    }

    const response = await endpoints.characters.create(characterData)
    router.push(`/characters/${response.data.id}`)
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
