/**
 * Navigation Guards
 */

import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

export function setupRouterGuards(router: Router) {
  // Global before guard
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()
    const uiStore = useUiStore()

    // Set page title
    if (to.meta.title) {
      document.title =
        typeof to.meta.title === 'string' ? to.meta.title : `${to.meta.title(to)} | simFocus`
    }

    // Close mobile sidebar on navigation
    if (uiStore.sidebarCollapsed === false && window.innerWidth < 768) {
      uiStore.toggleSidebar()
    }

    // Check authentication
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      // Save intended destination
      localStorage.setItem('redirect', to.fullPath)
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }

    // Redirect authenticated users away from auth pages
    if (to.meta.requiresGuest && authStore.isAuthenticated) {
      return next({ name: 'dashboard' })
    }

    // Email verification check
    if (
      to.meta.requiresAuth &&
      !authStore.isEmailVerified &&
      to.name !== 'settings-profile'
    ) {
      uiStore.showNotification({
        type: 'warning',
        message: 'Please verify your email to access all features'
      })
    }

    next()
  })

  // Global after guard
  router.afterEach((to, from) => {
    // Track page view (analytics)
    if (typeof (window as any).gtag !== 'undefined') {
      ;(window as any).gtag('event', 'page_view', {
        page_path: to.path,
        page_title: to.meta.title
      })
    }
  })

  // Error handler
  router.onError((error) => {
    console.error('Router error:', error)
    const uiStore = useUiStore()
    uiStore.showNotification({
      type: 'error',
      message: 'Failed to load page. Please try again.'
    })
  })
}
