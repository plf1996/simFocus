<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-position="top"
    size="large"
    class="login-form"
  >
    <el-form-item label="Email" prop="email">
      <el-input
        v-model="formData.email"
        type="email"
        placeholder="your@email.com"
        :prefix-icon="Message"
        clearable
        @keyup.enter="handleSubmit"
      />
    </el-form-item>

    <el-form-item label="Password" prop="password">
      <el-input
        v-model="formData.password"
        type="password"
        placeholder="Enter your password"
        :prefix-icon="Lock"
        show-password
        clearable
        @keyup.enter="handleSubmit"
      />
    </el-form-item>

    <div class="form-actions">
      <el-checkbox v-model="formData.remember">
        Remember me
      </el-checkbox>
      <router-link to="/forgot-password" class="forgot-link">
        Forgot password?
      </router-link>
    </div>

    <el-form-item>
      <AppButton
        type="primary"
        :loading="isLoading"
        block
        size="large"
        @click="handleSubmit"
      >
        Sign In
      </AppButton>
    </el-form-item>

    <el-divider>
      <span class="divider-text">or continue with</span>
    </el-divider>

    <div class="social-login">
      <el-button :loading="socialLoading.google" @click="handleSocialLogin('google')">
        <template #icon>
          <svg class="social-icon" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="currentColor"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="currentColor"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="currentColor"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
        </template>
        Google
      </el-button>

      <el-button :loading="socialLoading.github" @click="handleSocialLogin('github')">
        <template #icon>
          <svg class="social-icon" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
            />
          </svg>
        </template>
        GitHub
      </el-button>
    </div>

    <div class="form-footer">
      <span class="footer-text">Don't have an account?</span>
      <router-link to="/register" class="register-link">
        Sign up
      </router-link>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Message, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import AppButton from '@/components/common/AppButton.vue'

const emit = defineEmits<{
  success: []
}>()

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const isLoading = ref(false)
const socialLoading = reactive({
  google: false,
  github: false
})

const formData = reactive({
  email: '',
  password: '',
  remember: false
})

const rules: FormRules = {
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: ['blur', 'change'] }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    isLoading.value = true

    await authStore.login({
      email: formData.email,
      password: formData.password
    })

    ElMessage.success('Login successful')

    // Redirect to intended page or dashboard
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)

    emit('success')
  } catch (error: any) {
    if (error?.message) {
      ElMessage.error(error.message)
    }
    // Validation error or API error - do nothing as Element Plus shows validation errors
  } finally {
    isLoading.value = false
  }
}

const handleSocialLogin = async (provider: 'google' | 'github') => {
  socialLoading[provider] = true

  try {
    // TODO: Implement OAuth flow
    // Redirect to backend OAuth endpoint
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    window.location.href = `${baseUrl}/auth/${provider}`
  } catch (error: any) {
    ElMessage.error(`Failed to login with ${provider}`)
  } finally {
    socialLoading[provider] = false
  }
}
</script>

<style scoped lang="scss">
.login-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 24px;

  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-form-item__label) {
    font-weight: 500;
  }
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .forgot-link {
    font-size: 14px;
    color: var(--el-color-primary);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

.divider-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.social-login {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;

  .social-icon {
    width: 18px;
    height: 18px;
  }
}

.form-footer {
  text-align: center;
  margin-top: 16px;

  .footer-text {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }

  .register-link {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-color-primary);
    text-decoration: none;
    margin-left: 4px;

    &:hover {
      text-decoration: underline;
    }
  }
}

@media (max-width: 480px) {
  .social-login {
    grid-template-columns: 1fr;
  }
}
</style>
