<template>
  <el-input
    :model-value="modelValue"
    type="textarea"
    :placeholder="placeholder"
    :disabled="disabled"
    :readonly="readonly"
    :maxlength="maxlength"
    :show-word-limit="showWordLimit"
    :rows="rows"
    :autosize="autosize"
    @update:model-value="handleUpdate"
    @blur="handleBlur"
    @focus="handleFocus"
    @change="handleChange"
  />
</template>

<script setup lang="ts">
interface Props {
  modelValue: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  maxlength?: number
  showWordLimit?: boolean
  rows?: number
  autosize?: boolean | { minRows?: number; maxRows?: number }
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Please enter content',
  rows: 3,
  showWordLimit: false,
  autosize: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  change: [value: string]
}>()

const handleUpdate = (value: string) => {
  emit('update:modelValue', value)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}

const handleChange = (value: string) => {
  emit('change', value)
}
</script>
