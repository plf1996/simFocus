<template>
  <aside
    :class="['app-sidebar', { 'is-collapsed': collapsed }]"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      :collapse-transition="true"
      :unique-opened="true"
      router
      class="sidebar-menu"
    >
      <template v-for="item in menuItems" :key="item.path">
        <el-sub-menu v-if="item.children && item.children.length > 0" :index="item.path">
          <template #title>
            <el-icon v-if="item.icon">
              <component :is="item.icon" />
            </el-icon>
            <span>{{ item.title }}</span>
          </template>
          <el-menu-item
            v-for="child in item.children"
            :key="child.path"
            :index="child.path"
          >
            <el-icon v-if="child.icon">
              <component :is="child.icon" />
            </el-icon>
            <template #title>
              <span>{{ child.title }}</span>
            </template>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item v-else :index="item.path">
          <el-icon v-if="item.icon">
            <component :is="item.icon" />
          </el-icon>
          <template #title>
            <span>{{ item.title }}</span>
          </template>
        </el-menu-item>
      </template>
    </el-menu>

    <div class="sidebar-footer">
      <el-tooltip :content="collapsed ? 'Expand' : 'Collapse'" placement="right">
        <el-button text @click="toggleCollapse">
          <el-icon :size="18">
            <DArrowLeft v-if="!collapsed" />
            <DArrowRight v-else />
          </el-icon>
        </el-button>
      </el-tooltip>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  House,
  ChatDotSquare,
  Document,
  User,
  Setting,
  DArrowLeft,
  DArrowRight
} from '@element-plus/icons-vue'

interface Props {
  collapsed?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'toggle-collapse': []
}>()

const route = useRoute()
const isMobile = ref(false)

const activeMenu = computed(() => {
  return route.path
})

const menuItems = computed(() => {
  return [
    {
      title: 'Dashboard',
      path: '/dashboard',
      icon: House
    },
    {
      title: 'Topics',
      path: '/topics',
      icon: Document
    },
    {
      title: 'Discussions',
      path: '/discussions',
      icon: ChatDotSquare
    },
    {
      title: 'Settings',
      path: '/settings',
      icon: Setting,
      children: [
        { title: 'Profile', path: '/settings/profile' },
        { title: 'API Keys', path: '/settings/api-keys' }
      ]
    }
  ]
})

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    emit('toggle-collapse')
  }
}

const handleMouseEnter = () => {
  if (!isMobile.value && props.collapsed) {
    // Optional: Expand on hover
    // emit('toggle-collapse')
  }
}

const handleMouseLeave = () => {
  if (!isMobile.value && !props.collapsed) {
    // Optional: Collapse on leave
    // emit('toggle-collapse')
  }
}

const toggleCollapse = () => {
  emit('toggle-collapse')
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped lang="scss">
.app-sidebar {
  position: fixed;
  top: var(--header-height, 60px);
  left: 0;
  bottom: 0;
  width: var(--sidebar-width, 240px);
  background-color: var(--el-bg-color-page);
  border-right: 1px solid var(--el-border-color-light);
  transition: width 0.3s ease;
  z-index: var(--z-sticky, 1020);
  display: flex;
  flex-direction: column;

  &.is-collapsed {
    width: var(--sidebar-collapsed-width, 64px);

    .sidebar-footer {
      padding: 12px;
    }

    :deep(.el-sub-menu__title),
    :deep(.el-menu-item) {
      span {
        opacity: 0;
        width: 0;
        overflow: hidden;
      }
    }
  }

  &:not(.is-collapsed) {
    :deep(.el-menu--collapse) {
      width: var(--sidebar-width, 240px);
    }
  }
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;

  &:not(.el-menu--collapse) {
    width: var(--sidebar-width, 240px);
  }

  &.el-menu--collapse {
    width: var(--sidebar-collapsed-width, 64px);
  }

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 48px;
    line-height: 48px;

    &.is-active {
      background-color: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
      border-right: 2px solid var(--el-color-primary);
    }

    span {
      opacity: 1;
      width: auto;
      transition: opacity 0.3s, width 0.3s;
    }
  }

  :deep(.el-sub-menu .el-menu-item) {
    background-color: var(--el-bg-color);
    min-width: var(--sidebar-width, 240px);

    &.is-active {
      background-color: var(--el-color-primary-light-9);
    }
  }
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: center;

  button {
    width: 100%;
  }
}

// Custom scrollbar
.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background-color: var(--el-border-color-darker);
  border-radius: 4px;

  &:hover {
    background-color: var(--el-border-color-dark);
  }
}

@media (max-width: 768px) {
  .app-sidebar {
    width: var(--sidebar-width, 240px);
    transform: translateX(-100%);

    &.is-collapsed {
      transform: translateX(0);
    }
  }
}
</style>
