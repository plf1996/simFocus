<template>
  <el-avatar
    :class="['app-avatar', avatarClass]"
    :size="avatarSize"
    :shape="shape"
    :src="src"
    :alt="alt"
    :icon="icon"
  >
    <template v-if="!src && !icon" #default>
      <span class="avatar-fallback">{{ fallbackText }}</span>
    </template>
  </el-avatar>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  src?: string
  alt?: string
  name?: string
  size?: number | 'large' | 'default' | 'small'
  shape?: 'circle' | 'square'
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  shape: 'circle',
  size: 'default'
})

const avatarClass = computed(() => ({
  'has-image': !!props.src
}))

const avatarSize = computed(() => {
  if (typeof props.size === 'number') {
    return props.size
  }
  const sizeMap = {
    large: 64,
    default: 40,
    small: 32
  }
  return sizeMap[props.size] || 40
})

const fallbackText = computed(() => {
  if (props.name) {
    // Get initials from name (first letter of each word, max 2)
    return props.name
      .split(' ')
      .slice(0, 2)
      .map(word => word.charAt(0).toUpperCase())
      .join('')
  }
  return '?'
})
</script>

<style scoped lang="scss">
.app-avatar {
  flex-shrink: 0;

  .avatar-fallback {
    font-weight: 500;
    user-select: none;
  }

  &.has-image {
    :deep(img) {
      object-fit: cover;
    }
  }
}
</style>
