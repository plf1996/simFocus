<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-position="top"
    size="large"
    class="forgot-password-form"
  >
    <div class="form-header">
      <h2>Forgot Password?</h2>
      <p>Enter your email address and we'll send you a link to reset your password.</p>
    </div>

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

    <el-form-item>
      <AppButton
        type="primary"
        :loading="isLoading"
        block
        size="large"
        @click="handleSubmit"
      >
        Send Reset Link
      </AppButton>
    </el-form-item>

    <div class="form-footer">
      <router-link to="/login" class="back-link">
        <el-icon>
          <ArrowLeft />
        </el-icon>
        Back to Login
      </router-link>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Message, ArrowLeft } from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'

const emit = defineEmits<{
  success: []
}>()

const formRef = ref<FormInstance>()
const isLoading = ref(false)

const formData = reactive({
  email: ''
})

const rules: FormRules = {
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email', trigger: ['blur', 'change'] }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    isLoading.value = true

    // TODO: Call password reset API
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulated API call

    ElMessage.success('Password reset link has been sent to your email.')

    emit('success')

    // Reset form
    formData.email = ''
    formRef.value.resetFields()
  } catch (error: any) {
    if (error?.message) {
      ElMessage.error(error.message)
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.forgot-password-form {
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

.form-header {
  text-align: center;
  margin-bottom: 32px;

  h2 {
    font-size: 24px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin: 0 0 8px 0;
  }

  p {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    margin: 0;
    line-height: 1.5;
  }
}

.form-footer {
  text-align: center;
  margin-top: 24px;

  .back-link {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    font-weight: 500;
    color: var(--el-color-primary);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
