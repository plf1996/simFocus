/**
 * UI Store
 * Manages global UI state (loading, notifications, theme, modals)
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { NotificationItem } from '@/types'

export const useUiStore = defineStore('ui', () => {
  // Loading State
  const globalLoading = ref(false)
  const loadingComponent = ref<Set<string>>(new Set())

  function setLoading(key: string, isLoading: boolean) {
    if (isLoading) {
      loadingComponent.value.add(key)
    } else {
      loadingComponent.value.delete(key)
    }
    globalLoading.value = loadingComponent.value.size > 0
  }

  // Notifications
  const notifications = ref<NotificationItem[]>([])

  function showNotification(notification: Omit<NotificationItem, 'id'>) {
    const id = Date.now().toString()
    notifications.value.push({ ...notification, id })
    setTimeout(() => {
      removeNotification(id)
    }, notification.duration ?? 5000)
  }

  function removeNotification(id: string) {
    notifications.value = notifications.value.filter((n) => n.id !== id)
  }

  // Modal State
  const activeModals = ref<Set<string>>(new Set())

  function openModal(key: string) {
    activeModals.value.add(key)
  }

  function closeModal(key: string) {
    activeModals.value.delete(key)
  }

  function isModalOpen(key: string) {
    return activeModals.value.has(key)
  }

  // Sidebar State (collapsed/expanded)
  const sidebarCollapsed = ref(false)

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  // Theme
  const theme = ref<'light' | 'dark'>('light')

  function setTheme(newTheme: 'light' | 'dark') {
    theme.value = newTheme
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
    localStorage.setItem('theme', newTheme)
  }

  function initializeTheme() {
    const stored = localStorage.getItem('theme') as 'light' | 'dark' | null
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setTheme(stored ?? (prefersDark ? 'dark' : 'light'))
  }

  return {
    // Loading
    globalLoading,
    loadingComponent,
    setLoading,
    // Notifications
    notifications,
    showNotification,
    removeNotification,
    // Modal
    activeModals,
    openModal,
    closeModal,
    isModalOpen,
    // Sidebar
    sidebarCollapsed,
    toggleSidebar,
    // Theme
    theme,
    setTheme,
    initializeTheme
  }
}, {
  persist: {
    key: 'ui-storage',
    storage: localStorage,
    paths: ['sidebarCollapsed', 'theme']
  }
})
