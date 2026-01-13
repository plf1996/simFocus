<template>
  <header class="app-header">
    <div class="header-left">
      <el-button
        class="sidebar-toggle"
        text
        @click="$emit('toggle-sidebar')"
      >
        <el-icon :size="20">
          <Fold v-if="!uiStore.sidebarCollapsed" />
          <Expand v-else />
        </el-icon>
      </el-button>

      <router-link to="/" class="logo-link">
        <img src="/logo.svg" alt="simFocus" class="logo" />
        <span class="logo-text">simFocus</span>
      </router-link>
    </div>

    <div class="header-center">
      <el-input
        v-if="showSearch"
        v-model="searchQuery"
        placeholder="Search topics, discussions..."
        prefix-icon="Search"
        class="search-input"
        clearable
        @keyup.enter="handleSearch"
      />
    </div>

    <div class="header-right">
      <el-tooltip content="New Discussion" placement="bottom">
        <el-button text @click="handleNewDiscussion">
          <el-icon :size="20">
            <Plus />
          </el-icon>
        </el-button>
      </el-tooltip>

      <el-tooltip content="Notifications" placement="bottom">
        <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
          <el-button text @click="handleNotifications">
            <el-icon :size="20">
              <Bell />
            </el-icon>
          </el-button>
        </el-badge>
      </el-tooltip>

      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-dropdown">
          <AppAvatar :src="authStore.user?.avatar_url" :name="authStore.user?.name" :size="32" />
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>
              <div class="user-info">
                <div class="user-name">{{ authStore.user?.name || 'User' }}</div>
                <div class="user-email">{{ authStore.user?.email }}</div>
              </div>
            </el-dropdown-item>
            <el-dropdown-item divided command="profile">
              <el-icon><User /></el-icon>
              <span>Profile</span>
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              <span>Settings</span>
            </el-dropdown-item>
            <el-dropdown-item command="theme">
              <el-icon>
                <Sunny v-if="uiStore.theme === 'light'" />
                <Moon v-else />
              </el-icon>
              <span>{{ uiStore.theme === 'light' ? 'Dark Mode' : 'Light Mode' }}</span>
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              <span>Logout</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import AppAvatar from '@/components/common/AppAvatar.vue'
import {
  Fold,
  Expand,
  Plus,
  Bell,
  User,
  Setting,
  Sunny,
  Moon,
  SwitchButton
} from '@element-plus/icons-vue'

const emit = defineEmits<{
  'toggle-sidebar': []
}>()

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()

const searchQuery = ref('')
const showSearch = computed(() => authStore.isAuthenticated)
const unreadCount = ref(0) // TODO: Fetch from notification store

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ name: 'discussions', query: { search: searchQuery.value } })
  }
}

const handleNewDiscussion = () => {
  router.push({ name: 'topic-create' })
}

const handleNotifications = () => {
  // TODO: Open notification panel
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push({ name: 'settings-profile' })
      break
    case 'settings':
      router.push({ name: 'settings-api-keys' })
      break
    case 'theme':
      uiStore.setTheme(uiStore.theme === 'light' ? 'dark' : 'light')
      break
    case 'logout':
      authStore.logout()
      router.push({ name: 'login' })
      break
  }
}
</script>

<style scoped lang="scss">
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height, 60px);
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: var(--z-fixed, 1030);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;

  .sidebar-toggle {
    padding: 8px;

    @media (min-width: 769px) {
      display: none;
    }
  }
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--el-text-color-primary);

  .logo {
    width: 32px;
    height: 32px;
  }

  .logo-text {
    font-size: 20px;
    font-weight: 600;
    color: var(--el-color-primary);
  }
}

.header-center {
  flex: 1;
  max-width: 600px;
  margin: 0 24px;

  .search-input {
    width: 100%;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-dropdown {
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--el-fill-color-light);
  }
}

.user-info {
  .user-name {
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  .user-email {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}

.notification-badge {
  :deep(.el-badge__content) {
    transform: translateY(-50%) translateX(100%);
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 16px;
  }

  .header-center {
    display: none;
  }
}
</style>
