<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <div class="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
      <h2 class="text-2xl font-bold text-center text-gray-900 mb-6">注册</h2>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
            姓名
          </label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="张三"
          />
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
            邮箱
          </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="your@email.com"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
            密码
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            minlength="8"
            maxlength="72"
            @input="validatePassword"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2"
            :class="passwordValidClass"
            placeholder="请输入密码"
          />
          <div class="mt-1 text-xs space-y-1">
            <div :class="passwordLengthValid ? 'text-green-600' : 'text-gray-500'">
              {{ passwordLengthValid ? '✓' : '○' }} 8-72个字符
            </div>
            <div v-if="passwordTooLong" class="text-red-600">
              ⚠ 密码过长（最多72个字符）
            </div>
          </div>
        </div>

        <div>
          <label for="bio" class="block text-sm font-medium text-gray-700 mb-1">
            简介（可选）
          </label>
          <textarea
            id="bio"
            v-model="form.bio"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="简单介绍一下自己..."
          ></textarea>
        </div>

        <div v-if="error" class="text-red-600 text-sm bg-red-50 p-3 rounded-md">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading || !isFormValid"
          class="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading">注册中...</span>
          <span v-else>注册</span>
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-600">
        已有账号？
        <router-link to="/login" class="text-primary-600 hover:text-primary-700">
          立即登录
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  name: '',
  email: '',
  password: '',
  bio: ''
})
const loading = ref(false)
const error = ref('')

// 密码验证
const passwordTooLong = ref(false)
const passwordLengthValid = ref(false)

const validatePassword = () => {
  const len = form.value.password.length
  passwordLengthValid.value = len >= 8 && len <= 72
  passwordTooLong.value = len > 72
}

const passwordValidClass = computed(() => {
  if (form.value.password.length === 0) return 'border-gray-300'
  if (passwordTooLong.value) return 'border-red-500 focus:ring-red-500'
  if (passwordLengthValid.value) return 'border-green-500 focus:ring-green-500'
  return 'border-gray-300'
})

const isFormValid = computed(() => {
  return form.value.email &&
         form.value.password.length >= 8 &&
         form.value.password.length <= 72 &&
         !passwordTooLong.value
})

const handleRegister = async () => {
  // 再次验证密码长度
  if (form.value.password.length > 72) {
    error.value = '密码不能超过72个字符'
    return
  }

  error.value = ''
  loading.value = true

  try {
    await authStore.register(form.value)
    router.push('/topics')
  } catch (err) {
    // 解析后端返回的错误信息
    const errorMsg = err.response?.data?.error?.message || err.message || '注册失败，请稍后重试'
    error.value = errorMsg
  } finally {
    loading.value = false
  }
}
</script>
