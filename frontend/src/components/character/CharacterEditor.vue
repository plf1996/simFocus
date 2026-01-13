<template>
  <div class="character-editor">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-position="top"
    >
      <!-- Basic Info -->
      <div class="editor-section">
        <h4>Basic Information</h4>

        <el-form-item label="Name" prop="name">
          <AppInput
            v-model="formData.name"
            placeholder="Character name"
            :maxlength="50"
            required
          />
        </el-form-item>

        <el-form-item label="Avatar">
          <div class="avatar-upload">
            <img
              v-if="formData.avatar_url"
              :src="formData.avatar_url"
              alt="Avatar"
              class="avatar-preview"
            />
            <div v-else class="avatar-placeholder">
              <el-icon><User /></el-icon>
            </div>
            <el-upload
              :action="uploadUrl"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :on-success="handleAvatarSuccess"
              accept="image/*"
            >
              <AppButton size="small">
                <el-icon><Upload /></el-icon>
                Upload Avatar
              </AppButton>
            </el-upload>
          </div>
        </el-form-item>
      </div>

      <!-- Demographics -->
      <div class="editor-section">
        <h4>Demographics</h4>

        <el-form-item label="Age" prop="age">
          <el-input-number
            v-model="formData.config.age"
            :min="18"
            :max="100"
            :step="1"
          />
        </el-form-item>

        <el-form-item label="Gender" prop="gender">
          <el-select v-model="formData.config.gender" placeholder="Select gender">
            <el-option label="Male" value="male" />
            <el-option label="Female" value="female" />
            <el-option label="Other" value="other" />
            <el-option label="Prefer not to say" value="prefer_not_to_say" />
          </el-select>
        </el-form-item>

        <el-form-item label="Profession" prop="profession">
          <AppInput
            v-model="formData.config.profession"
            placeholder="e.g., Software Engineer, Marketing Manager"
            required
          />
        </el-form-item>
      </div>

      <!-- Personality Traits -->
      <div class="editor-section">
        <h4>Personality Traits (1-10)</h4>

        <div class="traits-grid">
          <el-form-item label="Openness">
            <el-slider
              v-model="formData.config.personality.openness"
              :min="1"
              :max="10"
              :marks="{ 1: 'Low', 5: 'Medium', 10: 'High' }"
              :show-tooltip="false"
            />
            <span class="trait-value">{{ formData.config.personality.openness }}</span>
          </el-form-item>

          <el-form-item label="Rigor">
            <el-slider
              v-model="formData.config.personality.rigor"
              :min="1"
              :max="10"
              :marks="{ 1: 'Low', 5: 'Medium', 10: 'High' }"
              :show-tooltip="false"
            />
            <span class="trait-value">{{ formData.config.personality.rigor }}</span>
          </el-form-item>

          <el-form-item label="Critical Thinking">
            <el-slider
              v-model="formData.config.personality.critical_thinking"
              :min="1"
              :max="10"
              :marks="{ 1: 'Low', 5: 'Medium', 10: 'High' }"
              :show-tooltip="false"
            />
            <span class="trait-value">{{ formData.config.personality.critical_thinking }}</span>
          </el-form-item>

          <el-form-item label="Optimism">
            <el-slider
              v-model="formData.config.personality.optimism"
              :min="1"
              :max="10"
              :marks="{ 1: 'Low', 5: 'Medium', 10: 'High' }"
              :show-tooltip="false"
            />
            <span class="trait-value">{{ formData.config.personality.optimism }}</span>
          </el-form-item>
        </div>
      </div>

      <!-- Knowledge Background -->
      <div class="editor-section">
        <h4>Knowledge Background</h4>

        <el-form-item label="Fields of Expertise" prop="fields">
          <el-select
            v-model="formData.config.knowledge.fields"
            multiple
            filterable
            allow-create
            placeholder="Add fields of expertise"
            style="width: 100%"
          >
            <el-option label="Technology" value="Technology" />
            <el-option label="Business" value="Business" />
            <el-option label="Marketing" value="Marketing" />
            <el-option label="Design" value="Design" />
            <el-option label="Psychology" value="Psychology" />
            <el-option label="Sociology" value="Sociology" />
            <el-option label="Economics" value="Economics" />
            <el-option label="Philosophy" value="Philosophy" />
          </el-select>
        </el-form-item>

        <el-form-item label="Years of Experience" prop="experience_years">
          <el-input-number
            v-model="formData.config.knowledge.experience_years"
            :min="0"
            :max="50"
          />
        </el-form-item>

        <el-form-item label="Representative Views" prop="representative_views">
          <AppInput
            v-model="viewsText"
            type="textarea"
            placeholder="Enter representative views (one per line)"
            :rows="4"
            @update:model-value="handleViewsChange"
          />
        </el-form-item>
      </div>

      <!-- Discussion Style -->
      <div class="editor-section">
        <h4>Discussion Style</h4>

        <el-form-item label="Stance" prop="stance">
          <el-radio-group v-model="formData.config.stance">
            <el-radio-button label="support">Supportive</el-radio-button>
            <el-radio-button label="oppose">Opposing</el-radio-button>
            <el-radio-button label="neutral">Neutral</el-radio-button>
            <el-radio-button label="critical_exploration">Critical Exploration</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="Expression Style" prop="expression_style">
          <el-radio-group v-model="formData.config.expression_style">
            <el-radio-button label="formal">Formal</el-radio-button>
            <el-radio-button label="casual">Casual</el-radio-button>
            <el-radio-button label="technical">Technical</el-radio-button>
            <el-radio-button label="storytelling">Storytelling</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="Behavior Pattern" prop="behavior_pattern">
          <el-radio-group v-model="formData.config.behavior_pattern">
            <el-radio-button label="active">Active</el-radio-button>
            <el-radio-button label="passive">Passive</el-radio-button>
            <el-radio-button label="balanced">Balanced</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </div>

      <!-- Public Toggle -->
      <div class="editor-section">
        <el-form-item>
          <el-checkbox v-model="formData.is_public">
            Make this character public (others can use it)
          </el-checkbox>
        </el-form-item>
      </div>

      <!-- Actions -->
      <div class="editor-actions">
        <AppButton @click="handleCancel">Cancel</AppButton>
        <AppButton type="primary" :loading="isSaving" @click="handleSave">
          Save Character
        </AppButton>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules, type UploadProps } from 'element-plus'
import { User, Upload } from '@element-plus/icons-vue'
import AppButton from '@/components/common/AppButton.vue'
import AppInput from '@/components/common/AppInput.vue'
import type { Character, CharacterFormData } from '@/types'
import type { CharacterConfig, Gender } from '@/shared/types'

interface Props {
  character?: Character
}

interface Emits {
  save: [character: Character]
  cancel: []
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// State
const formRef = ref<FormInstance>()
const isSaving = ref(false)
const viewsText = ref('')

// Form data
const formData = reactive<CharacterFormData>({
  name: props.character?.name || '',
  avatar_url: props.character?.avatar_url || '',
  config: {
    age: props.character?.config.age || 30,
    gender: props.character?.config.gender || 'prefer_not_to_say',
    profession: props.character?.config.profession || '',
    personality: {
      openness: props.character?.config.personality.openness || 5,
      rigor: props.character?.config.personality.rigor || 5,
      critical_thinking: props.character?.config.personality.critical_thinking || 5,
      optimism: props.character?.config.personality.optimism || 5
    },
    knowledge: {
      fields: props.character?.config.knowledge.fields || [],
      experience_years: props.character?.config.knowledge.experience_years || 5,
      representative_views: props.character?.config.knowledge.representative_views || []
    },
    stance: props.character?.config.stance || 'neutral',
    expression_style: props.character?.config.expression_style || 'formal',
    behavior_pattern: props.character?.config.behavior_pattern || 'balanced'
  },
  is_public: props.character?.is_public ?? false
})

// Initialize views text
if (props.character?.config.knowledge.representative_views) {
  viewsText.value = props.character.config.knowledge.representative_views.join('\n')
}

// Form validation rules
const formRules: FormRules = {
  name: [
    { required: true, message: 'Please enter a character name', trigger: 'blur' },
    { min: 2, max: 50, message: 'Name must be 2-50 characters', trigger: 'blur' }
  ],
  profession: [
    { required: true, message: 'Please enter a profession', trigger: 'blur' }
  ],
  fields: [
    { required: true, message: 'Please select at least one field', trigger: 'change' }
  ]
}

// Upload configuration
const uploadUrl = computed(() => {
  // TODO: Configure actual upload endpoint
  return '/api/v1/upload'
})

// Methods
const handleSave = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    isSaving.value = true

    // Create character object
    const character: Character = {
      id: props.character?.id || `char_${Date.now()}`,
      user_id: props.character?.user_id,
      name: formData.name,
      avatar_url: formData.avatar_url,
      is_template: false,
      is_public: formData.is_public ?? false,
      config: formData.config as CharacterConfig,
      usage_count: props.character?.usage_count || 0,
      rating_avg: props.character?.rating_avg,
      rating_count: props.character?.rating_count || 0,
      created_at: props.character?.created_at || new Date().toISOString()
    }

    emit('save', character)
    ElMessage.success('Character saved successfully')
  } catch (error) {
    console.error('Form validation failed:', error)
    ElMessage.error('Please fix the form errors')
  } finally {
    isSaving.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}

const handleViewsChange = (value: string) => {
  formData.config.knowledge.representative_views = value
    .split('\n')
    .map(v => v.trim())
    .filter(v => v.length > 0)
}

const beforeAvatarUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('Only image files are allowed')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('Image size must be less than 2MB')
    return false
  }
  return true
}

const handleAvatarSuccess = (response: any) => {
  formData.avatar_url = response.url
}

// Reset form
const resetForm = () => {
  formRef.value?.resetFields()
  viewsText.value = ''
}

defineExpose({
  resetForm
})
</script>

<style scoped lang="scss">
.character-editor {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.editor-section {
  padding: 20px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;

  h4 {
    margin: 0 0 16px;
    font-size: 16px;
    font-weight: 600;
  }
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--el-border-color);
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--el-fill-color);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--el-border-color);

  .el-icon {
    font-size: 32px;
    color: var(--el-text-color-placeholder);
  }
}

.traits-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;

  :deep(.el-form-item) {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0;

    .el-form-item__label {
      min-width: 120px;
    }

    .el-form-item__content {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 12px;
    }
  }
}

.trait-value {
  min-width: 24px;
  text-align: center;
  font-weight: 600;
  color: var(--el-color-primary);
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color);
}
</style>
