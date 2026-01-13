<template>
  <el-button
    :class="['app-button', buttonClass]"
    v-bind="$attrs"
    :loading="loading"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <template v-if="$slots.icon" #icon>
      <slot name="icon" />
    </template>
    <template v-if="$slots.default" #default>
      <slot />
    </template>
  </el-button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'text' | 'default'
  size?: 'large' | 'default' | 'small'
  loading?: boolean
  disabled?: boolean
  plain?: boolean
  round?: boolean
  circle?: boolean
  block?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  size: 'default',
  loading: false,
  disabled: false,
  plain: false,
  round: false,
  circle: false,
  block: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClass = computed(() => ({
  [`is-${props.type}`]: props.type !== 'default',
  [`is-${props.size}`]: props.size !== 'default',
  'is-block': props.block
}))

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
.app-button {
  &.is-block {
    width: 100%;
    display: flex;
  }
}
</style>
