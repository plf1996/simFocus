<template>
  <el-form-item
    :label="label"
    :prop="name"
    :required="required"
    :rules="rules"
    :error="error"
    :show-message="showMessage"
  >
    <el-input
      :model-value="modelValue"
      :type="inputType"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :clearable="clearable"
      :show-password="showPassword"
      :maxlength="maxlength"
      :show-word-limit="showWordLimit"
      :rows="rows"
      :autosize="autosize"
      @update:model-value="handleUpdate"
      @blur="handleBlur"
      @focus="handleFocus"
      @clear="handleClear"
      @change="handleChange"
    >
      <template v-if="$slots.prefix" #prefix>
        <slot name="prefix" />
      </template>
      <template v-if="$slots.suffix" #suffix>
        <slot name="suffix" />
      </template>
      <template v-if="$slots.prepend" #prepend>
        <slot name="prepend" />
      </template>
      <template v-if="$slots.append" #append>
        <slot name="append" />
      </template>
    </el-input>
    <template v-if="$slots.error" #error>
      <slot name="error" />
    </template>
  </el-form-item>
</template>

<script setup lang="ts">
interface Props {
  modelValue: string | number
  label?: string
  name?: string
  type?: 'text' | 'textarea' | 'password' | 'number' | 'email' | 'tel' | 'url'
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  clearable?: boolean
  showPassword?: boolean
  maxlength?: number
  showWordLimit?: boolean
  rows?: number
  autosize?: boolean | { minRows?: number; maxRows?: number }
  required?: boolean
  rules?: any[]
  error?: string
  showMessage?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  clearable: true,
  showMessage: true
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  clear: []
  change: [value: string | number]
}>()

const inputType = computed(() => {
  if (props.type === 'textarea') return 'textarea'
  if (props.type === 'number') return 'number'
  if (props.type === 'password' || props.showPassword) return 'password'
  if (props.type === 'email') return 'email'
  if (props.type === 'tel') return 'tel'
  if (props.type === 'url') return 'url'
  return 'text'
})

const handleUpdate = (value: string | number) => {
  emit('update:modelValue', value)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}

const handleClear = () => {
  emit('clear')
}

const handleChange = (value: string | number) => {
  emit('change', value)
}
</script>
