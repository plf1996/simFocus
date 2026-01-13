<template>
  <div class="main-layout">
    <AppHeader @toggle-sidebar="handleToggleSidebar" />

    <div class="main-layout-container">
      <AppSidebar :collapsed="uiStore.sidebarCollapsed" />

      <main :class="['main-content', { 'is-collapsed': uiStore.sidebarCollapsed }]">
        <div class="content-wrapper">
          <router-view v-slot="{ Component, route }">
            <transition :name="route.meta.transition || 'fade'" mode="out-in">
              <component :is="Component" :key="route.path" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppFooter from './AppFooter.vue'

const uiStore = useUiStore()

const handleToggleSidebar = () => {
  uiStore.toggleSidebar()
}
</script>

<style scoped lang="scss">
.main-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-layout-container {
  display: flex;
  flex: 1;
  margin-top: var(--header-height, 60px);
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width, 240px);
  transition: margin-left 0.3s ease;
  min-height: calc(100vh - var(--header-height, 60px) - var(--footer-height, 50px));

  &.is-collapsed {
    margin-left: var(--sidebar-collapsed-width, 64px);
  }
}

.content-wrapper {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

// Page transitions
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

// Responsive
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;

    &.is-collapsed {
      margin-left: 0;
    }
  }

  .content-wrapper {
    padding: 16px;
  }
}
</style>
