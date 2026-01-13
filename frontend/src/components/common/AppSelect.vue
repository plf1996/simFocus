<template>
  <el-form-item
    :label="label"
    :prop="name"
    :required="required"
    :rules="rules"
    :error="error"
  >
    <el-select
      :model-value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :clearable="clearable"
      :filterable="filterable"
      :allow-create="allowCreate"
      :multiple="multiple"
      :multiple-limit="multipleLimit"
      :remote="remote"
      :remote-method="remoteMethod"
      :loading="loading"
      :no-match-text="noMatchText"
      :no-data-text="noDataText"
      :popper-class="popperClass"
      :reserve-keyword="reserveKeyword"
      :default-first-option="defaultFirstOption"
      :teleported="teleported"
      :persistent="persistent"
      :automatic-dropdown="automaticDropdown"
      :fit-input-width="fitInputWidth"
      :size="size"
      @update:model-value="handleUpdate"
      @blur="handleBlur"
      @focus="handleFocus"
      @clear="handleClear"
      @visible-change="handleVisibleChange"
      @remove-tag="handleRemoveTag"
    >
      <template v-if="$slots.prefix" #prefix>
        <slot name="prefix" />
      </template>
      <template v-if="$slots.empty" #empty>
        <slot name="empty" />
      </template>
      <template v-if="$slots.default" #default>
        <slot />
      </template>
      <template v-if="$slots.tag" #tag>
        <slot name="tag" />
      </template>
      <template v-if="$slots.loading" #loading>
        <slot name="loading" />
      </template>
    </el-select>
  </el-form-item>
</template>

<script setup lang="ts">
interface Props {
  modelValue: string | number | boolean | Array<string | number | boolean>
  label?: string
  name?: string
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  filterable?: boolean
  allowCreate?: boolean
  multiple?: boolean
  multipleLimit?: number
  remote?: boolean
  loading?: boolean
  remoteMethod?: (query: string) => void
  noMatchText?: string
  noDataText?: string
  popperClass?: string
  reserveKeyword?: boolean
  defaultFirstOption?: boolean
  teleported?: boolean
  persistent?: boolean
  automaticDropdown?: boolean
  fitInputWidth?: boolean
  size?: 'large' | 'default' | 'small'
  required?: boolean
  rules?: any[]
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Please select',
  clearable: true,
  filterable: false,
  allowCreate: false,
  multiple: false,
  remote: false,
  loading: false,
  reserveKeyword: true,
  defaultFirstOption: false,
  teleported: true,
  persistent: true,
  automaticDropdown: false,
  fitInputWidth: false,
  size: 'default'
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | boolean | Array<string | number | boolean>]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  clear: []
  'visible-change': [visible: boolean]
  'remove-tag': [value: string | number | boolean]
}>()

const handleUpdate = (value: string | number | boolean | Array<string | number | boolean>) => {
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

const handleVisibleChange = (visible: boolean) => {
  emit('visible-change', visible)
}

const handleRemoveTag = (value: string | number | boolean) => {
  emit('remove-tag', value)
}
</script>
