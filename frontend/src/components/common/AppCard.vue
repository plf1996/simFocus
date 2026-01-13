<template>
  <el-card
    :class="['app-card', cardClass]"
    :shadow="shadow"
    :body-style="bodyStyle"
  >
    <template v-if="$slots.header" #header>
      <div class="app-card-header">
        <slot name="header" />
      </div>
    </template>

    <div v-if="$slots.default" class="app-card-body">
      <slot />
    </div>

    <template v-if="$slots.footer" #footer>
      <div class="app-card-footer">
        <slot name="footer" />
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { computed, type CSSProperties } from 'vue'

interface Props {
  shadow?: 'always' | 'hover' | 'never'
  bordered?: boolean
  hoverable?: boolean
  bodyStyle?: CSSProperties
  bodyClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'hover',
  bordered: true,
  hoverable: false
})

const cardClass = computed(() => ({
  'is-bordered': props.bordered,
  'is-hoverable': props.hoverable,
  [props.bodyClass]: props.bodyClass
}))
</script>

<style scoped lang="scss">
.app-card {
  &.is-hoverable {
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--el-box-shadow-light);
    }
  }

  &.is-bordered {
    border: 1px solid var(--el-border-color);
  }

  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  :deep(.el-card__body) {
    padding: 20px;
  }

  :deep(.el-card__footer) {
    padding: 16px 20px;
    border-top: 1px solid var(--el-border-color-lighter);
  }
}

.app-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.app-card-body {
  flex: 1;
}

.app-card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}
</style>
