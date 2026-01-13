<template>
  <AppCard class="topic-form">
    <template #header>
      <h3>{{ isEdit ? 'Edit Topic' : 'Create New Topic' }}</h3>
    </template>

    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-position="top"
      @submit.prevent="handleSubmit"
    >
      <!-- Title -->
      <el-form-item label="Topic Title" prop="title">
        <AppInput
          v-model="formData.title"
          type="text"
          placeholder="Enter a clear, concise title for your topic"
          :maxlength="100"
          show-word-limit
          required
        />
      </el-form-item>

      <!-- Description -->
      <el-form-item label="Description" prop="description">
        <AppInput
          v-model="formData.description"
          type="textarea"
          placeholder="Provide a brief description of what you want to discuss"
          :rows="3"
          :maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <!-- Context -->
      <el-form-item label="Additional Context" prop="context">
        <AppInput
          v-model="formData.context"
          type="textarea"
          placeholder="Add any background information, constraints, or specific aspects to focus on"
          :rows="4"
          :maxlength="2000"
          show-word-limit
        />
      </el-form-item>

      <!-- Attachments -->
      <el-form-item label="Attachments">
        <el-upload
          v-model:file-list="attachmentList"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :on-success="handleUploadSuccess"
          :on-remove="handleRemoveAttachment"
          :before-upload="beforeUpload"
          :limit="5"
          drag
          multiple
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            Drop files here or <em>click to upload</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              Supported formats: PDF, DOC, TXT, MD (Max 10MB each)
            </div>
          </template>
        </el-upload>
      </el-form-item>

      <!-- Template Selection -->
      <el-form-item label="Use Template">
        <el-button @click="showTemplateSelector = true" text>
          <el-icon><Document /></el-icon>
          Browse Templates
        </el-button>
        <div v-if="selectedTemplate" class="template-tag">
          <el-tag closable @close="selectedTemplate = null">
            {{ selectedTemplate.name }}
          </el-tag>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="form-actions">
        <AppButton @click="handleCancel">Cancel</AppButton>
        <AppButton type="primary" :loading="isSubmitting" @click="handleSubmit">
          {{ isEdit ? 'Update Topic' : 'Create Topic' }}
        </AppButton>
      </div>
    </template>
  </AppCard>

  <!-- Template Selector Dialog -->
  <TopicTemplate
    v-model="showTemplateSelector"
    @select="handleTemplateSelect"
  />
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules, type UploadUserFile, type UploadProps } from 'element-plus'
import { UploadFilled, Document } from '@element-plus/icons-vue'
import AppCard from '@/components/common/AppCard.vue'
import AppInput from '@/components/common/AppInput.vue'
import AppButton from '@/components/common/AppButton.vue'
import TopicTemplate from './TopicTemplate.vue'
import type { Topic, Attachment } from '@/types'

interface Props {
  topic?: Topic
  isEdit?: boolean
}

interface Emits {
  submit: [data: {
    title: string
    description?: string
    context?: string
    attachments?: Attachment[]
  }]
  cancel: []
}

const props = withDefaults(defineProps<Props>(), {
  isEdit: false
})

const emit = defineEmits<Emits>()

// Form state
const formRef = ref<FormInstance>()
const isSubmitting = ref(false)
const showTemplateSelector = ref(false)
const selectedTemplate = ref<{ id: string; name: string } | null>(null)
const attachmentList = ref<UploadUserFile[]>([])

// Form data
const formData = reactive({
  title: props.topic?.title || '',
  description: props.topic?.description || '',
  context: props.topic?.context || ''
})

// Form validation rules
const formRules: FormRules = {
  title: [
    { required: true, message: 'Please enter a topic title', trigger: 'blur' },
    { min: 5, max: 100, message: 'Title must be 5-100 characters', trigger: 'blur' }
  ]
}

// Upload configuration
const uploadUrl = computed(() => {
  // TODO: Configure actual upload endpoint
  return '/api/v1/upload'
})

const uploadHeaders = computed(() => {
  // TODO: Add authentication headers
  return {}
})

// Methods
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    isSubmitting.value = true

    // Prepare attachments data
    const attachments: Attachment[] = attachmentList.value
      .filter(file => file.status === 'success')
      .map(file => ({
        id: file.response?.id || file.uid,
        name: file.name,
        url: file.response?.url || file.url,
        type: file.raw?.type || '',
        size: file.raw?.size || 0
      }))

    emit('submit', {
      title: formData.title,
      description: formData.description || undefined,
      context: formData.context || undefined,
      attachments: attachments.length > 0 ? attachments : undefined
    })

    ElMessage.success(props.isEdit ? 'Topic updated successfully' : 'Topic created successfully')
  } catch (error) {
    console.error('Form validation failed:', error)
    ElMessage.error('Please fix the form errors')
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}

const handleTemplateSelect = (template: any) => {
  selectedTemplate.value = template
  formData.title = template.title
  formData.description = template.description
  formData.context = template.context
  showTemplateSelector.value = false
}

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    ElMessage.error('File size cannot exceed 10MB')
    return false
  }

  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown'
  ]

  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('Only PDF, DOC, DOCX, TXT, and MD files are supported')
    return false
  }

  return true
}

const handleUploadSuccess = (response: any, file: UploadUserFile) => {
  console.log('Upload success:', response, file)
}

const handleRemoveAttachment = (file: UploadUserFile) => {
  console.log('Remove attachment:', file)
}

// Reset form
const resetForm = () => {
  formRef.value?.resetFields()
  attachmentList.value = []
  selectedTemplate.value = null
}

defineExpose({
  resetForm
})
</script>

<style scoped lang="scss">
.topic-form {
  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.template-tag {
  margin-top: 8px;
}

:deep(.el-upload-dragger) {
  width: 100%;
  padding: 20px;
}

:deep(.el-icon--upload) {
  font-size: 48px;
  color: var(--el-color-primary);
  margin-bottom: 16px;
}
</style>
